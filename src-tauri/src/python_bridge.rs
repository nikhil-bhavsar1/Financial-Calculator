// Python Bridge - Direct Python invocation with streaming progress support
use std::io::{BufRead, BufReader, Write, Read};
use std::process::{Command, Stdio};
use std::path::PathBuf;
use std::env;
use std::time::{Duration, Instant};
use std::thread;
use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Emitter};

use rusqlite::{Connection, params};

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonRequest {
    pub command: String,
    pub file_path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub file_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub options: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PythonResponse {
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extracted_data: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metrics: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ProgressUpdate {
    pub status: String,
    pub current_page: i32,
    pub total_pages: i32,
    pub percentage: i32,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub partial_items: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub partial_text: Option<String>,
}

fn find_python() -> Option<String> {
    for cmd in &["python3", "python"] {
        if Command::new(cmd)
            .arg("--version")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok()
        {
            return Some(cmd.to_string());
        }
    }
    None
}

fn run_python_script_with_timeout(script: String, timeout_secs: u64) -> Result<String, String> {
    let python_cmd = find_python().ok_or("Python not found")?;
    
    let mut child = Command::new(&python_cmd)
        .arg("-c")
        .arg(&script)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;
        
    let start = Instant::now();
    let timeout = Duration::from_secs(timeout_secs);
    
    loop {
        match child.try_wait() {
            Ok(Some(status)) => {
                if !status.success() {
                    let mut stderr = String::new();
                    if let Some(mut err_pipe) = child.stderr.take() {
                         let _ = err_pipe.read_to_string(&mut stderr);
                    }
                    return Err(format!("Script failed: {}", stderr));
                }
                break;
            },
            Ok(None) => {
                if start.elapsed() > timeout {
                    let _ = child.kill();
                    return Err("Operation timed out".to_string());
                }
                thread::sleep(Duration::from_millis(50));
            },
            Err(e) => return Err(format!("Error waiting for process: {}", e)),
        }
    }
    
    let mut stdout_str = String::new();
    if let Some(mut out_pipe) = child.stdout.take() {
        out_pipe.read_to_string(&mut stdout_str)
            .map_err(|e| format!("Failed to read output: {}", e))?;
    }
    
    Ok(stdout_str)
}

fn find_api_script() -> Result<PathBuf, String> {
    // Try multiple possible locations
    let candidates = vec![
        PathBuf::from("python/api.py"),           // From project root (tauri dev)
        PathBuf::from("../python/api.py"),        // From src-tauri
        PathBuf::from("src-tauri/../python/api.py"), // Explicit
    ];
    
    for path in candidates {
        if path.exists() {
            return Ok(path);
        }
    }
    
    // Last resort: use current dir info for debugging
    let cwd = env::current_dir().unwrap_or_default();
    Err(format!(
        "Python API script not found. CWD: {:?}. Tried: python/api.py, ../python/api.py",
        cwd
    ))
}

#[tauri::command]
pub async fn run_python_analysis(
    app: AppHandle,
    file_path: String,
    content: Option<String>,
    file_name: Option<String>,
    options: Option<serde_json::Value>,
) -> Result<PythonResponse, String> {
    let python_cmd = find_python().ok_or("Python not found. Please install Python 3.x")?;
    let api_script = find_api_script()?;
    
    eprintln!("[PythonBridge] Using Python: {}", python_cmd);
    eprintln!("[PythonBridge] Script path: {:?}", api_script);
    eprintln!("[PythonBridge] File to analyze: {}", file_path);
    
    // Build request
    let request = PythonRequest {
        command: "parse".to_string(),
        file_path,
        content,
        file_name,
        options,
    };
    
    let request_json = serde_json::to_string(&request)
        .map_err(|e| format!("Failed to serialize request: {}", e))?;
    
    eprintln!("[PythonBridge] Request JSON length: {}", request_json.len());
    
    // Spawn Python process
    let mut child = Command::new(&python_cmd)
        .arg(&api_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {} (script: {:?})", e, api_script))?;
    
    // Send request - take stdin BEFORE sending
    {
        let stdin = child.stdin.as_mut()
            .ok_or("Failed to get Python stdin")?;
        
        stdin.write_all(request_json.as_bytes())
            .map_err(|e| format!("Failed to write to Python stdin: {}", e))?;
        stdin.write_all(b"\n")
            .map_err(|e| format!("Failed to write newline: {}", e))?;
        stdin.flush()
            .map_err(|e| format!("Failed to flush stdin: {}", e))?;
    }
    // stdin is dropped here, closing the pipe (signals EOF to Python)
    
    // Read stderr for debugging
    let stderr = child.stderr.take();
    
    // Read response from stdout with timeout
    let stdout = child.stdout.take()
        .ok_or("Failed to capture Python stdout")?;
    let reader = BufReader::new(stdout);
    
    let mut final_response: Option<PythonResponse> = None;
    let timeout_duration = Duration::from_secs(900); // 900 second timeout (15 mins) for very large PDFs
    let start_time = Instant::now();

    for line in reader.lines() {
        // Check timeout
        if start_time.elapsed() > timeout_duration {
            eprintln!("[PythonBridge] Timeout reached after 900 seconds, killing Python process");
            let _ = child.kill();
            return Err("PDF analysis timed out after 15 minutes. The document may be very large (>500 pages) or heavily formatted. Consider splitting the document or checking if it contains images that require OCR.".to_string());
        }
        
        if let Ok(line) = line {
            if !line.trim().starts_with('{') {
                continue; // Skip non-JSON lines
            }
            
            eprintln!("[PythonBridge] stdout: {}", &line[..line.len().min(200)]);
            
            // Try to parse as progress update first
            if let Ok(progress) = serde_json::from_str::<ProgressUpdate>(&line) {
                if progress.status == "progress" {
                    // Emit progress event to frontend
                    let _ = app.emit("pdf-progress", progress.clone());
                    eprintln!("[PythonBridge] Progress: {}% - Page {}/{}", 
                        progress.percentage, progress.current_page, progress.total_pages);
                    continue; // Continue reading for more updates
                }
            }
            
            // Try to parse as final response
            if let Ok(response) = serde_json::from_str::<PythonResponse>(&line) {
                final_response = Some(response);
                // Break after receiving final response to prevent hanging
                break;
            }
        }
    }
    
    // If we have a response, we can proceed even if process is still cleaning up
    if final_response.is_some() {
        eprintln!("[PythonBridge] Received final response, cleaning up process...");
    }
    
    // Capture stderr (with a shorter timeout to avoid blocking)
    if let Some(stderr) = stderr {
        let stderr_reader = BufReader::new(stderr);
        for line in stderr_reader.lines().take(10) {
            if let Ok(line) = line {
                eprintln!("[PythonBridge] stderr: {}", line);
            }
        }
    }
    
    // Wait for process to finish with a shorter timeout (5 seconds) since we already have the response
    let cleanup_timeout = Duration::from_secs(5);
    let cleanup_start = Instant::now();
    let mut status = None;
    
    while cleanup_start.elapsed() < cleanup_timeout {
        match child.try_wait() {
            Ok(Some(s)) => {
                status = Some(s);
                break;
            }
            Ok(None) => {
                // Still running, wait a bit
                thread::sleep(Duration::from_millis(50));
            }
            Err(e) => {
                eprintln!("[PythonBridge] Error checking process status: {}", e);
                break;
            }
        }
    }
    
    // Kill process if still running after cleanup timeout
    if status.is_none() {
        eprintln!("[PythonBridge] Process still running after response received, killing it");
        let _ = child.kill();
        // Try one more time to get exit status
        status = child.try_wait().ok().flatten();
    }
    
    eprintln!("[PythonBridge] Python exit status: {:?}", status);
    
    match final_response {
        Some(response) => {
            eprintln!("[PythonBridge] Returning successful response");
            Ok(response)
        }
        None => Err("No response from Python. Process may have timed out or crashed.".to_string()),
    }
}

#[tauri::command]
pub async fn update_terminology_mapping(
    mappings: serde_json::Value,
) -> Result<(), String> {
    let python_cmd = find_python().ok_or("Python not found")?;
    let api_script = find_api_script()?;
    
    let request = serde_json::json!({
        "command": "update_mapping",
        "mappings": mappings
    });
    
    let mut child = Command::new(&python_cmd)
        .arg(&api_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;
    
    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(request.to_string().as_bytes())
            .map_err(|e| format!("Failed to write: {}", e))?;
        stdin.write_all(b"\n").ok();
        stdin.flush().ok();
    }
    
    let _ = child.wait();
    Ok(())
}

#[tauri::command]
pub async fn calculate_metrics(
    _app: AppHandle,
    items_json: String,
) -> Result<PythonResponse, String> {
    let python_cmd = find_python().ok_or("Python not found")?;
    let api_script = find_api_script()?;
    
    let _request = serde_json::json!({
        "command": "calculate_metrics",
        "items_json": items_json
    });
    
    let mut child = Command::new(&python_cmd)
        .arg(&api_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;
    
    eprintln!("[PythonBridge] Calculating metrics from {} items", items_json.len());
    
    // Read response from stdout
    let stdout = child.stdout.take()
        .ok_or("Failed to capture Python stdout")?;
    let reader = BufReader::new(stdout);
    
    let mut final_response: Option<PythonResponse> = None;
    let _timeout_duration = Duration::from_secs(60); // 60 second timeout for metrics calc
    
    for line in reader.lines() {
        if let Ok(line) = line {
            if !line.trim().starts_with('{') {
                continue;
            }
            
            eprintln!("[PythonBridge] stdout: {}", &line[..line.len().min(200)]);
            
            // Try to parse as final response
            if let Ok(response) = serde_json::from_str::<PythonResponse>(&line) {
                final_response = Some(response);
                break;
            }
        }
    }
    
    // Wait for process to finish
    let _ = child.wait();
    eprintln!("[PythonBridge] Metrics calculation complete");
    
    match final_response {
        Some(response) => {
            eprintln!("[PythonBridge] Returning metrics response");
            Ok(response)
        }
        None => Err("No response from Python for metrics calculation".to_string()),
    }
}

// =============================================================================
// NSE/BSE SCRAPER COMMANDS
// =============================================================================

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CompanySearchResult {
    pub success: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub results: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub query: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub count: Option<i32>,
}



#[tauri::command]
pub async fn search_companies(
    query: String,
    exchange: Option<String>,
    limit: Option<i32>,
) -> Result<CompanySearchResult, String> {
    eprintln!("[PythonBridge] Searching companies: {}", query);
    
    let exchange_str = exchange.unwrap_or_else(|| "BOTH".to_string());
    let limit_val = limit.unwrap_or(10);
    
    let script = format!(
        "import sys; sys.path.extend(['python', '../python']); from scraper_bridge import search_companies_bridge; result = search_companies_bridge('{}', '{}', {}); print(result)",
        query.replace("'", "\\'"),
        exchange_str,
        limit_val
    );

    match run_python_script_with_timeout(script, 45) {
        Ok(stdout) => {
            let result: serde_json::Value = serde_json::from_str(&stdout)
                .map_err(|e| format!("Failed to parse search results: {}", e))?;
            
            let success = result.get("success").and_then(|v| v.as_bool()).unwrap_or(false);
            let count = result.get("count").and_then(|v| v.as_i64()).map(|v| v as i32);
            
            Ok(CompanySearchResult {
                success,
                results: Some(result.clone()),
                error: result.get("error").and_then(|v| v.as_str()).map(|s| s.to_string()),
                query: Some(query),
                count,
            })
        },
        Err(e) => {
            eprintln!("[PythonBridge] Search error: {}", e);
            Ok(CompanySearchResult {
                success: false,
                results: None,
                error: Some(e),
                query: Some(query),
                count: Some(0),
            })
        }
    }
}

#[tauri::command]
pub async fn get_company_details(
    symbol: String,
    exchange: String,
) -> Result<CompanySearchResult, String> {
    eprintln!("[PythonBridge] Getting company details: {} on {}", symbol, exchange);
    
    let script = format!(
        "import sys; sys.path.extend(['python', '../python']); from scraper_bridge import get_company_details_bridge; result = get_company_details_bridge('{}', '{}'); print(result)",
        symbol.replace("'", "\\'"),
        exchange
    );

    match run_python_script_with_timeout(script, 15) {
        Ok(stdout) => {
            let result: serde_json::Value = serde_json::from_str(&stdout)
                .map_err(|e| format!("Failed to parse company details: {}", e))?;
            
            let success = result.get("success").and_then(|v| v.as_bool()).unwrap_or(false);
            
            Ok(CompanySearchResult {
                success,
                results: Some(result.clone()),
                error: result.get("error").and_then(|v| v.as_str()).map(|s| s.to_string()),
                query: Some(symbol),
                count: if success { Some(1) } else { Some(0) },
            })
        },
        Err(e) => {
            eprintln!("[PythonBridge] Details error: {}", e);
            Ok(CompanySearchResult {
                success: false,
                results: None,
                error: Some(e),
                query: Some(symbol),
                count: Some(0),
            })
        }
    }
}

#[tauri::command]
pub async fn get_stock_quote(
    symbol: String,
    exchange: String,
) -> Result<CompanySearchResult, String> {
    eprintln!("[PythonBridge] Getting stock quote: {} on {}", symbol, exchange);
    
    let script = format!(
        "import sys; sys.path.extend(['python', '../python']); from scraper_bridge import get_stock_quote_bridge; result = get_stock_quote_bridge('{}', '{}'); print(result)",
        symbol.replace("'", "\\'"),
        exchange
    );

    match run_python_script_with_timeout(script, 15) {
        Ok(stdout) => {
            let result: serde_json::Value = serde_json::from_str(&stdout)
                .map_err(|e| format!("Failed to parse stock quote: {}", e))?;
            
            let success = result.get("success").and_then(|v| v.as_bool()).unwrap_or(false);
            
            Ok(CompanySearchResult {
                success,
                results: Some(result.clone()),
                error: result.get("error").and_then(|v| v.as_str()).map(|s| s.to_string()),
                query: Some(symbol),
                count: if success { Some(1) } else { Some(0) },
            })
        },
        Err(e) => {
            eprintln!("[PythonBridge] Quote error: {}", e);
            Ok(CompanySearchResult {
                success: false,
                results: None,
                error: Some(e),
                query: Some(symbol),
                count: Some(0),
            })
        }
    }
}

#[tauri::command]
pub async fn search_web(
    query: String,
) -> Result<CompanySearchResult, String> {
    eprintln!("[PythonBridge] Web search: {}", query);
    
    let script = format!(
        "import sys; sys.path.extend(['python', '../python']); from scraper_bridge import search_web_bridge; result = search_web_bridge('{}'); print(result)",
        query.replace("'", "\\'")
    );

    match run_python_script_with_timeout(script, 30) {
        Ok(stdout) => {
            let result: serde_json::Value = serde_json::from_str(&stdout)
                .map_err(|e| format!("Failed to parse web search results: {}", e))?;
            
            let success = result.get("success").and_then(|v| v.as_bool()).unwrap_or(false);
            let count = result.get("total_count").and_then(|v| v.as_i64()).map(|v| v as i32);
            
            Ok(CompanySearchResult {
                success,
                results: Some(result.clone()),
                error: result.get("error").and_then(|v| v.as_str()).map(|s| s.to_string()),
                query: Some(query),
                count,
            })
        },
        Err(e) => {
            eprintln!("[PythonBridge] Web search error: {}", e);
            Ok(CompanySearchResult {
                success: false,
                results: None,
                error: Some(e),
                query: Some(query),
                count: Some(0),
            })
        }
    }
}

#[tauri::command]
pub async fn get_scraper_status() -> Result<CompanySearchResult, String> {
    eprintln!("[PythonBridge] Getting scraper status");
    
    let python_cmd = find_python().ok_or("Python not found")?;
    
    let output = Command::new(&python_cmd)
        .arg("-c")
        .arg("import sys; sys.path.extend(['python', '../python']); from scraper_bridge import get_scraper_status_bridge; result = get_scraper_status_bridge(); print(result)")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("Failed to get scraper status: {}", e))?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Ok(CompanySearchResult {
            success: false,
            results: None,
            error: Some(stderr.to_string()),
            query: None,
            count: Some(0),
        });
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    let result: serde_json::Value = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse scraper status: {}", e))?;
    
    let success = result.get("success").and_then(|v| v.as_bool()).unwrap_or(false);
    
    Ok(CompanySearchResult {
        success,
        results: Some(result),
        error: None,
        query: None,
        count: None,
    })
}

#[tauri::command]
pub async fn get_db_data() -> Result<serde_json::Value, String> {
    eprintln!("[PythonBridge] Fetching DB data");

    let python_cmd = find_python().ok_or("Python not found")?;
    let api_script = find_api_script()?;

    let request = serde_json::json!({
        "command": "get_db_data"
    });

    let mut child = Command::new(&python_cmd)
        .arg(&api_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;

    // Send request
    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(request.to_string().as_bytes())
            .map_err(|e| format!("Failed to write: {}", e))?;
        stdin.write_all(b"\n").ok();
        stdin.flush().ok();
    }

    // Read response with extended timeout for DB queries
    let stdout = child.stdout.take()
        .ok_or("Failed to capture Python stdout")?;
    let reader = BufReader::new(stdout);

    let mut final_response: Option<PythonResponse> = None;
    let timeout_duration = Duration::from_secs(30); // 30 seconds for DB query
    let start_time = Instant::now();

    for line in reader.lines() {
        if start_time.elapsed() > timeout_duration {
            eprintln!("[PythonBridge] DB data fetch timeout");
            let _ = child.kill();
            return Err("Database query timed out after 30 seconds. The database may be locked or contain too much data.".to_string());
        }

        if let Ok(line) = line {
            if !line.trim().starts_with('{') {
                continue;
            }

            if let Ok(response) = serde_json::from_str::<PythonResponse>(&line) {
                final_response = Some(response);
                break;
            }
        }
    }

    // Wait for process to finish
    let _ = child.wait();

    match final_response {
        Some(response) => {
            // Return the full response including status and data
            let response_value = serde_json::to_value(&response)
                .map_err(|e| format!("Failed to serialize response: {}", e))?;
            Ok(response_value)
        }
        None => Err("No response from Python for DB data fetch".to_string()),
    }
}

// =============================================================================
// STREAMING DATABASE UPDATES - FOR RAW DB VIEW
// =============================================================================

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct DatabaseUpdate {
    pub action: String,
    pub table: String,
    pub row_id: Option<i64>,
    pub data: Option<serde_json::Value>,
}

#[tauri::command]
pub async fn start_db_streaming(
    app: AppHandle,
    _window: tauri::Window,
) -> Result<(), String> {
    eprintln!("[PythonBridge] Starting database streaming for Raw DB view");

    // This command initiates a background task that queries the database periodically
    // and sends updates to the frontend

    let app_handle = app.clone();

    // Spawn background task
    std::thread::spawn(move || {
        let mut counter = 0;

        loop {
            counter += 1;

            // Query database every 2 seconds
            std::thread::sleep(Duration::from_secs(2));

            // Get database path (Python uses extracted_data.db)
            let db_path = "extracted_data.db";
            if !std::path::Path::new(db_path).exists() {
                continue;
            }

            // Open database and query
            let items = match (|| -> Result<Vec<serde_json::Value>, String> {
                let conn = Connection::open(db_path).map_err(|e| e.to_string())?;
                
                // Query recent items (with LIMIT to prevent timeout)
                let mut items: Vec<serde_json::Value> = Vec::new();

                let mut stmt = conn.prepare("SELECT id, label, value_current, value_previous FROM financial_items ORDER BY row_index DESC LIMIT 50").map_err(|e| e.to_string())?;
                let mut rows = stmt.query(params![]).map_err(|e| e.to_string())?;

                while let Some(row) = rows.next().map_err(|e| e.to_string())? {
                    let item = serde_json::json!({
                        "id": row.get::<usize, String>(0).unwrap_or_default(),
                        "label": row.get::<usize, String>(1).unwrap_or_default(),
                        "currentYear": row.get::<usize, f64>(2).unwrap_or_default(),
                        "previousYear": row.get::<usize, f64>(3).unwrap_or_default()
                    });
                    items.push(item);
                }

                Ok(items)
            })() {
                Ok(items) => items,
                Err(e) => {
                    eprintln!("[PythonBridge] Database error: {}", e);
                    Vec::new()
                }
            };

            let update = DatabaseUpdate {
                action: if counter == 1 { "initial".to_string() } else { "incremental".to_string() },
                table: "financial_items".to_string(),
                row_id: None,
                data: Some(serde_json::json!(items)),
            };

            // Emit update to frontend
            if let Err(e) = app_handle.emit("db-update", update.clone()) {
                eprintln!("[PythonBridge] Failed to emit db-update event: {}", e);
            }

            // Stop after 100 iterations (200 seconds)
            if counter > 100 {
                break;
            }
        }
    });

    Ok(())
}

#[tauri::command]
pub async fn stop_db_streaming(
    app: AppHandle,
) -> Result<(), String> {
    eprintln!("[PythonBridge] Stopping database streaming");

    // Just emit a stop event
    if let Err(e) = app.emit("db-streaming-stopped", true) {
        Err(format!("Failed to emit stop event: {}", e))
    } else {
        Ok(())
    }
}

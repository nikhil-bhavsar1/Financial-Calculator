// Python Bridge - Direct Python invocation with streaming progress support
use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};
use std::path::PathBuf;
use std::env;
use std::time::{Duration, Instant};
use std::thread;
use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Emitter};

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
    let timeout_duration = Duration::from_secs(120); // 120 second timeout for large Annual Statements
    let start_time = Instant::now();
    
    for line in reader.lines() {
        // Check timeout
        if start_time.elapsed() > timeout_duration {
            eprintln!("[PythonBridge] Timeout reached after 120 seconds, killing Python process");
            let _ = child.kill();
            return Err("PDF analysis timed out after 120 seconds. The PDF may be corrupted or too complex to process.".to_string());
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

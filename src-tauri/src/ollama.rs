use tauri::{AppHandle, Emitter, Runtime};
use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::collections::HashMap;
use futures_util::StreamExt;

use crate::settings::SettingsStore;

fn get_base_url(state: &tauri::State<'_, std::sync::Mutex<SettingsStore>>) -> String {
    let store = state.lock().unwrap();
    let settings = store.get();
    let mut host = settings.llm.ollama_host.trim().to_string();
    
    // Default or empty host to 127.0.0.1
    // Also force localhost to 127.0.0.1 to avoid IPv6 issues (::1 vs 127.0.0.1)
    if host.is_empty() || host.to_lowercase() == "localhost" {
        host = "127.0.0.1".to_string();
    }
    
    format!("http://{}:{}", host, settings.llm.ollama_port)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
    pub images: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatRequest {
    pub messages: Vec<ChatMessage>,
    pub model: Option<String>,
    pub stream: bool,
    pub session_id: Option<String>,
    pub temperature: Option<f32>,
    pub num_ctx: Option<usize>,
    pub top_p: Option<f32>,
    pub top_k: Option<usize>,
    pub system: Option<String>,
    pub seed: Option<i32>,
    pub num_predict: Option<i32>,
    pub repeat_penalty: Option<f32>,
    pub format: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PullRequest {
    pub model: String,
    pub insecure: bool,
}

pub struct OllamaBridge {
    // Track if service is running? 
    // For now we just use HTTP checks
}

impl OllamaBridge {
    pub fn new() -> Self {
        Self {}
    }

    pub async fn start<R: Runtime>(&self, _app: &AppHandle<R>) -> Result<(), String> {
        // Direct Ollama connection doesn't strictly need a bridge start,
        // but we keep the method for main.rs compatibility.
        // If we want to auto-start Ollama itself, we'd add it here.
        Ok(())
    }
}

// --- Commands ---

#[tauri::command]
pub async fn start_ollama_bridge<R: Runtime>(_app: AppHandle<R>, state: tauri::State<'_, OllamaBridge>) -> Result<String, String> {
    state.start(&_app).await?;
    Ok("Bridge ready (Direct connection)".to_string())
}

#[tauri::command]
pub async fn stop_ollama_bridge() -> Result<(), String> {
    Ok(())
}

#[tauri::command]
pub async fn get_ollama_status(state: tauri::State<'_, std::sync::Mutex<SettingsStore>>) -> Result<serde_json::Value, String> {
    let client = Client::new();
    let bridge_url = get_base_url(&state);
    let res = client.get(&bridge_url)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    if res.status().is_success() {
        Ok(serde_json::json!({ "status": "connected" }))
    } else {
        Err("Ollama unreachable".to_string())
    }
}

#[tauri::command]
pub async fn generate_completion(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    prompt: String, 
    model: String, 
    context: Vec<i32>
) -> Result<String, String> {
    let client = Client::new();
    let bridge_url = get_base_url(&state);
    let res = client.post(format!("{}/api/generate", bridge_url))
        .json(&serde_json::json!({
            "model": model,
            "prompt": prompt,
            "stream": false,
            "context": if context.is_empty() { None } else { Some(context) }
        }))
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())?;

    res.get("response")
       .and_then(|v| v.as_str())
       .map(|s| s.to_string())
       .ok_or_else(|| "No response text in output".to_string())
}

#[tauri::command]
pub async fn list_ollama_models(state: tauri::State<'_, std::sync::Mutex<SettingsStore>>) -> Result<Vec<serde_json::Value>, String> {
    list_ollama_models_detailed(state).await
}

#[tauri::command]
pub async fn list_ollama_models_detailed(state: tauri::State<'_, std::sync::Mutex<SettingsStore>>) -> Result<Vec<serde_json::Value>, String> {
    let client = reqwest::Client::new();
    let bridge_url = get_base_url(&state);
    
    // 1. Get all available models
    let tags_res = client.get(format!("{}/api/tags", bridge_url))
        .send()
        .await
        .map_err(|e| format!("Ollama not running: {}", e))?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())?;

    // 2. Get currently loaded models (Ollama >= 0.1.34)
    let ps_res = client.get(format!("{}/api/ps", bridge_url))
        .send()
        .await
        .ok(); // Ignore errors if /api/ps fails (older Ollama)
    
    let loaded_models: HashMap<String, serde_json::Value> = if let Some(resp) = ps_res {
        if resp.status().is_success() {
            resp.json::<serde_json::Value>().await
                .ok()
                .and_then(|v| v.get("models").and_then(|m| m.as_array()).cloned())
                .unwrap_or_default()
                .into_iter()
                .filter_map(|m| {
                    let name = m.get("name")?.as_str()?.to_string();
                    Some((name, m))
                })
                .collect()
        } else {
            HashMap::new()
        }
    } else {
        HashMap::new()
    };

    // 3. Transform and Merge
    let mut result = Vec::new();
    if let Some(models) = tags_res.get("models").and_then(|m| m.as_array()) {
        for m in models {
            let mut model_obj = m.clone();
            
            // Flatten details if present (parameter_size, quantization_level)
            if let Some(details) = model_obj.get("details").and_then(|d| d.as_object()) {
                let details = details.clone();
                if let Some(obj) = model_obj.as_object_mut() {
                    for (k, v) in details {
                        obj.insert(k, v);
                    }
                }
            }
            
            let name = model_obj.get("name").and_then(|n| n.as_str()).unwrap_or("").to_string();
            
            // Check if loaded
            let is_loaded = loaded_models.contains_key(&name);
            if let Some(obj) = model_obj.as_object_mut() {
                obj.insert("loaded".to_string(), serde_json::json!(is_loaded));
                if is_loaded {
                    if let Some(loaded_info) = loaded_models.get(&name) {
                        // Merge VRAM usage info if available
                        if let Some(vram) = loaded_info.get("size_vram") {
                            obj.insert("vram_bytes".to_string(), vram.clone());
                            // Convert to readable string (roughly)
                            let bytes = vram.as_u64().unwrap_or(0);
                            let mb = bytes / (1024 * 1024);
                            obj.insert("vram_usage".to_string(), serde_json::json!(format!("{} MB", mb)));
                        }
                        if let Some(expires) = loaded_info.get("expires_at") {
                            obj.insert("expires_at".to_string(), expires.clone());
                        }
                    }
                }
            }
            
            result.push(model_obj);
        }
    }
    
    Ok(result)
}

#[tauri::command]
pub async fn pull_model(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    model: String, 
    insecure: bool
) -> Result<serde_json::Value, String> {
    let client = Client::new();
    let bridge_url = get_base_url(&state);
    let payload = PullRequest { model, insecure };
    let res = client.post(format!("{}/api/pull", bridge_url))
        .json(&payload)
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())?;
    Ok(res)
}

#[tauri::command]
pub async fn delete_model(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    model: String
) -> Result<serde_json::Value, String> {
    let client = Client::new();
    let bridge_url = get_base_url(&state);
    let res = client.post(format!("{}/api/delete", bridge_url))
        .json(&serde_json::json!({ "name": model }))
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())?;
    Ok(res)
}

#[tauri::command]
pub async fn unload_model(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    model: String
) -> Result<(), String> {
    let client = reqwest::Client::new();
    let bridge_url = get_base_url(&state);
    let _ = client.post(format!("{}/api/generate", bridge_url))
        .json(&serde_json::json!({
            "model": model,
            "prompt": "",
            "stream": false,
            "keep_alive": 0
        }))
        .send()
        .await;
    Ok(())
}

#[tauri::command]
pub async fn chat(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    request: ChatRequest
) -> Result<serde_json::Value, String> {
    let client = Client::new();
    let bridge_url = get_base_url(&state);
    let res = client.post(format!("{}/api/chat", bridge_url))
        .json(&request)
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())?;
    Ok(res)
}

#[tauri::command]
pub async fn chat_stream(
    app: AppHandle, 
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    request: ChatRequest
) -> Result<(), String> {
    let client = Client::new();
    let mut req = request.clone();
    req.stream = true;
    
    let bridge_url = get_base_url(&state);
    let res = client.post(format!("{}/api/chat", bridge_url))
        .json(&req)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    let mut stream = res.bytes_stream();
    
    while let Some(item) = stream.next().await {
        match item {
            Ok(chunk) => {
                let text = String::from_utf8_lossy(&chunk);
                for line in text.lines() {
                    if let Ok(val) = serde_json::from_str::<serde_json::Value>(line) {
                        let content = val.get("message")
                            .and_then(|m| m.get("content"))
                            .and_then(|c| c.as_str())
                            .map(|s| s.to_string());
                        
                        let done = val.get("done").and_then(|d| d.as_bool()).unwrap_or(false);
                        
                        let payload = serde_json::json!({
                            "content": content,
                            "done": done
                        });
                        
                        let _ = app.emit("chat-stream-event", &payload);
                    }
                }
            }
            Err(e) => {
                 let _ = app.emit("chat-stream-error", &(e.to_string()));
            }
        }
    }
    
    Ok(())
}

#[tauri::command]
pub async fn get_chat_history(_session_id: String) -> Result<Vec<serde_json::Value>, String> {
    Ok(vec![])
}

#[tauri::command]
pub async fn clear_chat_history(_session_id: String) -> Result<(), String> {
    Ok(())
}

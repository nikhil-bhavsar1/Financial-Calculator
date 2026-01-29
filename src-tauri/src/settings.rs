use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::{AppHandle, Manager};
use std::fs;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMSettings {
    pub ollama_host: String,
    pub ollama_port: u16,
    pub selected_model: String,
    pub context_window: usize,      // e.g., 4096, 8192, 32768
    pub temperature: f32,           // 0.0 to 2.0
    pub top_p: f32,                 // 0.0 to 1.0
    pub top_k: usize,               // 0 to 100
    pub system_prompt: String,
    pub keep_alive: String,         // "5m", "1h", etc.
    pub seed: Option<i32>,          // For reproducibility
    pub num_predict: Option<i32>,   // Max tokens to generate (-1 = unlimited)
    pub repeat_penalty: f32,
    pub format: Option<String>,     // "json" or null
}

impl Default for LLMSettings {
    fn default() -> Self {
        Self {
            ollama_host: "localhost".to_string(),
            ollama_port: 11434,
            selected_model: "llama3.2".to_string(),
            context_window: 4096,
            temperature: 0.7,
            top_p: 0.9,
            top_k: 40,
            system_prompt: "You are a helpful assistant.".to_string(),
            keep_alive: "5m".to_string(),
            seed: None,
            num_predict: None,
            repeat_penalty: 1.1,
            format: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppSettings {
    pub llm: LLMSettings,
    pub auto_start_ollama: bool,
    pub theme: String,
    pub language: String,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            llm: LLMSettings::default(),
            auto_start_ollama: true,
            theme: "system".to_string(),
            language: "en".to_string(),
        }
    }
}

pub struct SettingsStore {
    path: PathBuf,
    settings: AppSettings,
}

impl SettingsStore {
    pub fn new(app_handle: &AppHandle) -> Result<Self, String> {
        let app_dir = app_handle.path().app_data_dir()
            .map_err(|e| format!("Failed to get app data dir: {}", e))?;
        fs::create_dir_all(&app_dir).map_err(|e| e.to_string())?;
        
        let path = app_dir.join("settings.json");
        let settings = if path.exists() {
            let content = fs::read_to_string(&path).map_err(|e| e.to_string())?;
            serde_json::from_str(&content).unwrap_or_default()
        } else {
            AppSettings::default()
        };

        Ok(Self { path, settings })
    }

    pub fn get(&self) -> &AppSettings {
        &self.settings
    }

    pub fn save(&self) -> Result<(), String> {
        let json = serde_json::to_string_pretty(&self.settings).map_err(|e| e.to_string())?;
        fs::write(&self.path, json).map_err(|e| e.to_string())
    }
}

// Tauri Commands
#[tauri::command]
pub fn get_settings(state: tauri::State<'_, std::sync::Mutex<SettingsStore>>) -> Result<AppSettings, String> {
    let store = state.lock().map_err(|e| e.to_string())?;
    Ok(store.get().clone())
}

#[tauri::command]
pub fn update_llm_settings(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    settings: LLMSettings
) -> Result<(), String> {
    let mut store = state.lock().map_err(|e| e.to_string())?;
    store.settings.llm = settings;
    store.save()
}

#[tauri::command]
pub fn update_setting(
    state: tauri::State<'_, std::sync::Mutex<SettingsStore>>,
    key: String,
    value: serde_json::Value
) -> Result<(), String> {
    let mut store = state.lock().map_err(|e| e.to_string())?;
    
    match key.as_str() {
        "auto_start_ollama" => {
            store.settings.auto_start_ollama = value.as_bool().unwrap_or(true);
        }
        "theme" => {
            store.settings.theme = value.as_str().unwrap_or("system").to_string();
        }
        _ => return Err(format!("Unknown setting: {}", key)),
    }
    
    store.save()
}

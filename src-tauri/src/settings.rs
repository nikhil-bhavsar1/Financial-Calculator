use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::{AppHandle, Manager};
use std::fs;

// --- Sub-structs ---

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiKeys {
    pub gemini: String,
    pub groq: String,
    pub openai: String,
    pub openrouter: String,
    pub opencode: String,
}

impl Default for ApiKeys {
    fn default() -> Self {
        Self {
            gemini: String::new(),
            groq: String::new(),
            openai: String::new(),
            openrouter: String::new(),
            opencode: String::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupabaseConfig {
    pub url: String,
    pub key: String,
}

impl Default for SupabaseConfig {
    fn default() -> Self {
        Self {
            url: String::new(),
            key: String::new(),
        }
    }
}

// --- Main Structs ---

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
    #[serde(default = "default_num_gpu")]
    pub num_gpu: i32,
}

fn default_num_gpu() -> i32 { -1 }

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
            num_gpu: -1,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppSettings {
    pub llm: LLMSettings,
    
    #[serde(default)]
    pub auto_start_ollama: bool, 
    
    pub theme: String,
    pub language: String,

    #[serde(rename = "accentColor", default = "default_accent_color")]
    pub accent_color: String,
    
    #[serde(rename = "enableAI", default = "default_enable_ai")]
    pub enable_ai: bool,
    
    #[serde(rename = "aiProvider", default = "default_ai_provider")]
    pub ai_provider: String,
    
    #[serde(rename = "apiKeys", default)]
    pub api_keys: ApiKeys,
    
    #[serde(rename = "modelName", default)]
    pub model_name: String,
    
    #[serde(rename = "supabaseConfig", default)]
    pub supabase_config: SupabaseConfig,
}

fn default_accent_color() -> String { "violet".to_string() }
fn default_ai_provider() -> String { "gemini".to_string() }
fn default_enable_ai() -> bool { true }

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            llm: LLMSettings::default(),
            auto_start_ollama: true,
            theme: "system".to_string(),
            language: "en".to_string(),
            accent_color: default_accent_color(),
            enable_ai: default_enable_ai(),
            ai_provider: default_ai_provider(),
            api_keys: ApiKeys::default(),
            model_name: "".to_string(),
            supabase_config: SupabaseConfig::default(),
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
            serde_json::from_str(&content).unwrap_or_else(|_| AppSettings::default())
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
        "accentColor" => {
             store.settings.accent_color = value.as_str().unwrap_or("violet").to_string();
        }
        "enableAI" => {
            store.settings.enable_ai = value.as_bool().unwrap_or(true);
        }
        "aiProvider" => {
            store.settings.ai_provider = value.as_str().unwrap_or("gemini").to_string();
        }
        "modelName" => {
            store.settings.model_name = value.as_str().unwrap_or("").to_string();
        }
        "apiKeys" => {
            if let Ok(val) = serde_json::from_value(value) {
                store.settings.api_keys = val;
            }
        }
        "supabaseConfig" => {
            if let Ok(val) = serde_json::from_value(value) {
                store.settings.supabase_config = val;
            }
        }
        _ => return Err(format!("Unknown setting: {}", key)),
    }
    
    store.save()
}
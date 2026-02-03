// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod settings;
mod ollama;
mod python_bridge;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let app_handle = app.handle().clone();
            let settings_store = settings::SettingsStore::new(&app_handle)
                .expect("Failed to initialize settings store");

            app.manage(std::sync::Mutex::new(settings_store));

            // Start Ollama bridge on app start if configured
            let handle_for_async = app_handle.clone();
            tauri::async_runtime::spawn(async move {
                let state = handle_for_async.state::<std::sync::Mutex<settings::SettingsStore>>();
                let should_start = {
                    let store = state.lock().unwrap();
                    store.get().auto_start_ollama
                };

                if should_start {
                    let service = ollama::OllamaBridge::new();
                    if let Err(e) = service.start(&handle_for_async).await {
                        eprintln!("Failed to start Ollama bridge: {}", e);
                    }
                    // In Tauri v2, you usually manage state on the app/handle during setup
                    handle_for_async.manage(service);
                }
            });


            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Settings commands
            settings::get_settings,
            settings::update_llm_settings,
            settings::update_setting,
            // Ollama commands
            ollama::start_ollama_bridge,
            ollama::stop_ollama_bridge,
            ollama::get_ollama_status,
            ollama::list_ollama_models,
            ollama::list_ollama_models_detailed,
            ollama::pull_model,
            ollama::delete_model,
            ollama::unload_model,
            ollama::chat,
            ollama::chat_stream,
            ollama::generate_completion,
            ollama::get_chat_history,
            ollama::clear_chat_history,
            // Python bridge commands
            python_bridge::run_python_analysis,
            python_bridge::update_terminology_mapping,
            python_bridge::calculate_metrics,
            python_bridge::get_db_data,
            // Database streaming commands
            python_bridge::start_db_streaming,
            python_bridge::stop_db_streaming,
            // Company scraper commands
            python_bridge::search_companies,
            python_bridge::get_company_details,
            python_bridge::get_stock_quote,
            python_bridge::search_web,
            python_bridge::get_scraper_status,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

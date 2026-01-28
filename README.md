# Financial Calculator

A comprehensive financial analysis tool combining a React frontend with a powerful Python backend for document processing and metric calculation.

## 🚀 Quick Start

**The application requires both the compiled frontend and the Python backend to function.**

### Recommended Method
Run the full-stack launcher script:
```bash
./start.sh
```
This script handles:
1. Starting the Python API server (Port 8765)
2. Starting the Vite Development Server (Port 1420)
3. Launching the browser or desktop app

## 📂 Project Structure & File Responsibilities

### 🟢 Core Application
| File | Responsibility |
|------|----------------|
| **`App.tsx`** | Main entry point. Manages application state, active tabs (Dashboard, Document, Capture), and orchestrates data flow between components. |
| **`start.sh`** | **CRITICAL**. The master implementation script. Ensures all services (Frontend, Backend, Proxy) run in the correct environment. |
| **`vite.config.ts`** | Frontend build config. **Crucial**: Configures the proxy that forwards `/api` requests to the local Python server. |

### 🔌 Backend & Communication
| File | Responsibility |
|------|----------------|
| **`python/api.py`** | The brain of the operation. A Python REST API (default port 8765) that handles file parsing, OCR, and financial formula execution. |
| **`services/tauriBridge.ts`** | The "Hybrid Bridge". It detects the environment: <br>• **Desktop**: Uses Tauri Shell commands for direct process spawning.<br>• **Web**: Falls back to `fetch()` calls to the Python API proxy. |
| **`services/pythonBridge.ts`** | Legacy service layer, largely superseded by `tauriBridge` but may contain utility types. |

### 📊 Financial Logic
- **`py_lib/`**: Contains the reference implementations of individual financial formulas.
- **`python/calculator.py`**: The **Active Calculation Engine**. It consolidates the logic from `py_lib` into a robust, production-ready class structure used by the API.

> **Note:** The API uses `calculator.py` exclusively for runtime calculations. `py_lib` serves as the modular source of truth for the formulas.

### 💎 UI Components
| Component | Responsibility |
|-----------|----------------|
| **`DocumentViewer.tsx`** | Advanced document reader. Features pagination, search highlighting, zoom, and full-screen mode. |
| **`CapturedDataGrid.tsx`** | Displays raw financial items extracted from uploaded documents. |
| **`MetricsDashboard.tsx`** | The visual dashboard showing calculated ratios and health scores. |
| **`UploadModal.tsx`** | Handles file selection and initiates the upload process via the Bridge. |

## 🔄 Data Architecture

1. **Input**: User uploads a regular financial document (PDF/CSV/Text).
2. **Transportation**: 
   - `App.tsx` calls `runPythonAnalysis` in `tauriBridge.ts`.
   - The Bridge routes the request to `localhost:8765/api/parse`.
3. **Processing**:
   - `api.py` receives the file.
   - Delegates to `py_lib` modules for formula execution.
   - Returns a structured JSON object (`ExtractedItem[]`).
4. **Normalization**:
   - Frontend receives the JSON.
   - Transforms raw items into `FinancialItem` objects (standardized ID, label, value).
5. **Visualization**:
   - `CapturedDataGrid` lists the line items.
   - `MetricsDashboard` visualizes the computed health scores.

## 🛠 Prerequisites

### System Requirements
| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Node.js** | v18.0.0+ | Required for the React/Tauri frontend. |
| **Python** | v3.9+ | Required for the parsing and calculation API. |
| **Rust** | v1.70+ | (Optional) Only required if building the native desktop binary. |

### OCR Requirements (Crucial for Scanned PDFs)
The parser uses **Tesseract OCR** to handle scanned documents. You must install it at the system level:

**Fedora/RHEL:**
```bash
sudo dnf install tesseract tesseract-langpack-eng
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Python Libraries
The `start.sh` script will attempt to install these automatically, but you can install them manually:
```bash
pip3 install flask flask-cors pandas openpyxl pillow pytesseract opencv-python-headless pymupdf
```

**Optional:** If you want to use EasyOCR (slower but alternative to Tesseract):
```bash
pip3 install easyocr
```

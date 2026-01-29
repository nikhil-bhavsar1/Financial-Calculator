#!/bin/bash

# =============================================================================
# FINANCIAL CALCULATOR - FULL STACK LAUNCHER
# =============================================================================
# This script sets up the environment (Python venv, Node dependencies)
# and launches the backend API and frontend Desktop App.

set -u # Error on undefined variables

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Financial Calculator - Full Stack Launcher ===${NC}"
echo ""

# =============================================================================
# 0. CLEANUP & TRAP
# =============================================================================

cleanup() {
    echo ""
    echo -e "${BLUE}Shutting down Financial Calculator...${NC}"
    
    # Securely Wipe API Keys from settings.json
    echo -e "   🧹 Securely wiping API keys from storage..."
    python3 -c "
import json
import os
from pathlib import Path

# Identify config directory (Linux/standard XDG)
# Note: Adjust if running on Mac or Windows if needed, but this script is bash/Linux focused
config_dir = Path.home() / '.local/share/com.financial.calculator'
settings_file = config_dir / 'settings.json'

if settings_file.exists():
    try:
        with open(settings_file, 'r') as f:
            data = json.load(f)
        
        # Wipe sensitive fields
        if 'apiKeys' in data:
            data['apiKeys'] = {k: '' for k in data['apiKeys']}
        if 'supabaseConfig' in data:
             data['supabaseConfig'] = {'url': '', 'key': ''}
             
        with open(settings_file, 'w') as f:
            json.dump(data, f, indent=2)
        print('      ✓ API keys & secrets wiped from disk')
    except Exception as e:
        print(f'      ⚠️  Failed to wipe settings: {e}')
"

    # Kill Python API
    if [ ! -z "${PYTHON_PID:-}" ]; then
        kill $PYTHON_PID 2>/dev/null
        echo -e "   ${GREEN}✓ Python API stopped${NC}"
    fi
    
    # Kill any binary instance
    pkill -x "financial-calculator" 2>/dev/null
    
    # Kill Vite/Tauri processes
    # Find process listening on 1420
    VITE_PID=$(lsof -t -i:1420 2>/dev/null)
    if [ ! -z "$VITE_PID" ]; then
        kill -9 $VITE_PID 2>/dev/null
        echo -e "   ${GREEN}✓ Frontend services stopped${NC}"
    fi

    echo -e "   ${GREEN}✓ Cleanup complete. Have a nice day!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# 1. PYTHON ENVIRONMENT SETUP
# =============================================================================

echo -e "${BLUE}1. Setting up Python Environment...${NC}"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "   ${RED}❌ Python 3 is missing. Please install it.${NC}"
    exit 1
fi

# Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "   ${YELLOW}📦 Creating virtual environment (.venv)...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "   ${RED}❌ Failed to create virtual environment.${NC}"
        exit 1
    fi
fi

# Activate Virtual Environment
source .venv/bin/activate
echo -e "   ${GREEN}✅ Virtual environment activated ($(which python))${NC}"

# Install Python Dependencies
echo -e "   ${YELLOW}📦 Checking/Installing Python libraries...${NC}"
pip install --upgrade pip --quiet
# Install requirements if requirements.txt exists, otherwise install manually
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
else
    # Core libs
    REQUIRED_LIBS="flask flask-cors pytesseract pandas openpyxl pillow opencv-python-headless pymupdf"
    pip install $REQUIRED_LIBS --quiet
    
    # Check for RAG engine dependencies
    if [ -f "rag_engine.py" ]; then
        # Assuming rag_engine might need numpy or others
        pip install numpy --quiet
    fi
fi
echo -e "   ${GREEN}✅ Python dependencies installed${NC}"


# =============================================================================
# 2. NODE.JS ENVIRONMENT SETUP
# =============================================================================

echo ""
echo -e "${BLUE}2. Setting up Node.js Environment...${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "   ${RED}❌ npm is missing. Please install Node.js.${NC}"
    exit 1
fi

if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules)" ]; then
    echo -e "   ${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "   ${RED}❌ npm install failed.${NC}"
        exit 1
    fi
else
    echo -e "   ${GREEN}✅ node_modules found${NC}"
fi

# =============================================================================
# 3. EXTERNAL SERVICES CHECK (OCR & OLLAMA)
# =============================================================================

echo ""
echo -e "${BLUE}3. Checking External Services...${NC}"

# OCR
if command -v tesseract &> /dev/null; then
    echo -e "   ${GREEN}✅ Tesseract OCR found${NC}"
else
    echo -e "   ${YELLOW}⚠️  Tesseract OCR missing (Scanned PDFs will be unreadable)${NC}"
    echo "      Install via: sudo apt install tesseract-ocr (Linux) or brew install tesseract (Mac)"
fi

# EasyOCR check (Python)
if python -c "import easyocr" &> /dev/null; then
    echo -e "   ${GREEN}✅ EasyOCR found (Python)${NC}"
else
    echo -e "   ${YELLOW}ℹ️  EasyOCR not installed (Optional - Better accuracy)${NC}"
fi

# Ollama
if command -v ollama &> /dev/null; then
    echo -e "   ${GREEN}✅ Ollama found${NC}"
    # Check if running
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo -e "   ${GREEN}✅ Ollama service is running${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Ollama is installed but NOT running.${NC}"
        echo "      Please run 'ollama serve' in a separate terminal for AI features."
    fi
else
    echo -e "   ${YELLOW}⚠️  Ollama not found (AI Chat/RAG features will be disabled)${NC}"
    echo "      Install from https://ollama.com"
fi

# =============================================================================
# 4. STARTING SERVICES
# =============================================================================

echo ""
echo -e "${BLUE}4. Launching Application...${NC}"

# Kill existing ports
fuser -k 8765/tcp 2>/dev/null
fuser -k 1420/tcp 2>/dev/null

# Start Python API
echo -e "   🐍 Starting Python Backend (Port 8765)..."
python python/api.py --server 8765 > python-api.log 2>&1 &
PYTHON_PID=$!
sleep 2

# Check if Python API started
if ps -p $PYTHON_PID > /dev/null; then
    echo -e "   ${GREEN}✅ Python API running (PID: $PYTHON_PID)${NC}"
else
    echo -e "   ${RED}❌ Python API failed to start. Log output:${NC}"
    cat python-api.log
    exit 1
fi

# Configure Wayland for Linux
if [ "${XDG_SESSION_TYPE:-}" == "wayland" ]; then
    export GDK_BACKEND=wayland
    export WEBKIT_DISABLE_COMPOSITING_MODE=1
fi

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   🚀 Financial Calculator Started        ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo "   Backend: http://localhost:8765"
echo "   Frontend: http://localhost:1420 (starts with app)"
echo ""
echo -e "   ${YELLOW}ℹ️  Note: API Keys are saved for this session only."
echo -e "       They will be securely wiped from disk when you stop this script (Ctrl+C).${NC}"
echo ""

# Start Tauri
# Note: tauri.conf.json beforeDevCommand now runs 'npm run dev'
npm run tauri dev

# Wait for cleanup
wait
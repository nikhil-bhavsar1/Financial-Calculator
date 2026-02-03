#!/bin/bash

# =============================================================================
# FINANCIAL CALCULATOR - FULL STACK LAUNCHER
# =============================================================================
# This script sets up the environment (Python venv, Node dependencies)
# and launches the desktop application with the Rust-Python bridge.

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
    # Use venv python if it exists, otherwise system python
    PYTHON_BIN="python3"
    if [ -f ".venv/bin/python3" ]; then
        PYTHON_BIN=".venv/bin/python3"
    fi
    
    $PYTHON_BIN -c "
import json
import os
from pathlib import Path

# Identify config directory (using identifier from tauri.conf.json)
# Note: Linux path typically follows ~/.local/share/IDENTIFIER
config_dir = Path.home() / '.local/share/com.yourcompany.yourapp'
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

    # Kill any binary instance
    pkill -x "financial-calculator" 2>/dev/null
    
    # Kill Vite/Tauri/Cargo processes
    VITE_PID=$(lsof -t -i:1420 2>/dev/null)
    if [ ! -z "$VITE_PID" ]; then
        kill -9 $VITE_PID 2>/dev/null
    fi
    pkill -f "cargo run" 2>/dev/null

    echo -e "   ${GREEN}✓ Cleanup complete. Have a nice day!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# 1. RUST & SYSTEM CHECKS
# =============================================================================

echo -e "${BLUE}1. System Checks...${NC}"

if ! command -v cargo &> /dev/null; then
    echo -e "   ${RED}❌ Rust/Cargo is missing. Please install Rust (https://rustup.rs).${NC}"
    exit 1
else
    echo -e "   ${GREEN}✅ Rust/Cargo found$(cargo --version | awk '{print " ("$2")"}').${NC}"
fi

# =============================================================================
# 2. PYTHON ENVIRONMENT SETUP
# =============================================================================

echo ""
echo -e "${BLUE}2. Setting up Python Environment...${NC}"

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
echo -e "   ${YELLOW}📦 Installing Python libraries...${NC}"
pip install --upgrade pip --quiet

# CORE DEPENDENCIES (Required for basic functionality)
# -----------------------------------------------------------------------------
echo -e "   ${BLUE}   → Installing core dependencies...${NC}"
CORE_LIBS="pymupdf pdfplumber pandas lxml beautifulsoup4 flask flask-cors pillow requests"
pip install $CORE_LIBS --quiet
echo -e "   ${GREEN}   ✓ Core dependencies installed${NC}"

# -----------------------------------------------------------------------------
# OCR DEPENDENCIES (Required for scanned PDFs)
# -----------------------------------------------------------------------------
echo -e "   ${BLUE}   → Installing OCR dependencies...${NC}"
OCR_LIBS="pytesseract opencv-python-headless"
pip install $OCR_LIBS --quiet
echo -e "   ${GREEN}   ✓ OCR dependencies installed (pytesseract, opencv)${NC}"

# Check if tesseract is installed on system
if ! command -v tesseract &> /dev/null; then
    echo -e "   ${YELLOW}   ⚠️  Tesseract OCR binary not found on system.${NC}"
    echo -e "   ${YELLOW}      Install with: sudo apt install tesseract-ocr (Debian/Ubuntu)${NC}"
    echo -e "   ${YELLOW}      or: sudo dnf install tesseract (Fedora)${NC}"
fi

# -----------------------------------------------------------------------------
# PARSER DEPENDENCIES (Additional parsing support)
# -----------------------------------------------------------------------------
echo -e "   ${BLUE}   → Installing parser dependencies...${NC}"
PARSER_LIBS="openpyxl xlrd"
pip install $PARSER_LIBS --quiet
echo -e "   ${GREEN}   ✓ Parser dependencies installed${NC}"

# Check for requirements.txt
if [ -f "requirements.txt" ]; then
    echo -e "   ${BLUE}   → Installing from requirements.txt...${NC}"
    pip install -r requirements.txt --quiet
fi

echo -e "   ${GREEN}✅ Python dependencies installed${NC}"

# -----------------------------------------------------------------------------
# OPTIONAL: HEAVY ML DEPENDENCIES (EasyOCR, Torch)
# -----------------------------------------------------------------------------

# Check if EasyOCR is already installed
echo -e "   ${BLUE}   → Checking for EasyOCR...${NC}"
if python3 -c "import easyocr" 2>/dev/null; then
    echo -e "   ${GREEN}   ✓ EasyOCR already installed${NC}"
else
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW} OPTIONAL: Install ML-powered OCR (EasyOCR + PyTorch)?${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "   EasyOCR provides better accuracy for complex scanned documents"
    echo "   but requires PyTorch (~2GB download, may take several minutes)."
    echo ""
    read -p "   Install EasyOCR + PyTorch? (y/N): " INSTALL_EASYOCR
    INSTALL_EASYOCR=${INSTALL_EASYOCR:-N}

    if [[ "$INSTALL_EASYOCR" =~ ^[Yy]$ ]]; then
        echo -e "   ${BLUE}   → Installing EasyOCR and PyTorch (this may take a while)...${NC}"
        pip install torch torchvision --quiet
        pip install easyocr --quiet
        echo -e "   ${GREEN}   ✓ EasyOCR installed successfully${NC}"
    else
        echo -e "   ${BLUE}   → Skipping EasyOCR installation${NC}"
    fi
fi

echo ""


# =============================================================================
# 3. NODE.JS ENVIRONMENT SETUP
# =============================================================================

echo ""
echo -e "${BLUE}3. Setting up Node.js Environment...${NC}"

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
# 4. STARTING SERVICES
# =============================================================================

echo ""
echo -e "${BLUE}4. Launching Application...${NC}"

# Configure Wayland for Linux if needed
if [ "${XDG_SESSION_TYPE:-}" == "wayland" ]; then
    export GDK_BACKEND=wayland
    export WEBKIT_DISABLE_COMPOSITING_MODE=1
fi

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   🚀 Financial Calculator Started        ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo "   Backend: Rust Bridge + Python Parser (Direct Spawn)"
echo "   Frontend: http://localhost:1420"
echo ""
echo -e "   ${YELLOW}ℹ️  first-time build may take a few minutes.${NC}"
echo ""

# Start Tauri
npm run tauri dev

# Wait for cleanup
wait
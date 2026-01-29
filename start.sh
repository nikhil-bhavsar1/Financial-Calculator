#!/bin/bash

echo "=== Financial Calculator - Full Stack Launcher ==="
echo ""

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    echo "Shutting down Financial Calculator..."
    
    # Kill Python API
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null
        echo "   ✓ Python API stopped"
    fi
    
    # Kill any binary instance
    pkill -x "financial-calculator" 2>/dev/null
    
    # Kill Vite if it was started (some versions of npm run tauri dev daemonize it)
    lsof -t -i:1420 | xargs kill -9 2>/dev/null
    
    echo "   ✓ Services stopped. Have a nice day!"
    exit 0
}
trap cleanup SIGINT SIGTERM


# =============================================================================
# Dependency Checks
# =============================================================================

check_dependencies() {
    echo "1. Checking System Dependencies..."
    MISSING_DEPS=0
    
    # Check Python 3
    if command -v python3 &> /dev/null; then
        echo "   ✅ Found Python 3 ($(python3 --version))"
    else
        echo "   ❌ Python 3 is missing."
        MISSING_DEPS=1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        echo "   ✅ Found Node.js ($(node --version))"
    else
        echo "   ❌ Node.js is missing."
        MISSING_DEPS=1
    fi
    
    # Check Tesseract OCR
    if command -v tesseract &> /dev/null; then
        echo "   ✅ Found Tesseract OCR ($(tesseract --version | head -n1))"
        TESSERACT_AVAILABLE=1
    else
        echo "   ⚠️  Tesseract OCR is missing (Optional for scanned PDFs)."
        echo "      To install:"
        echo "      - Fedora: sudo dnf install tesseract tesseract-langpack-eng"
        echo "      - Ubuntu/Debian: sudo apt install tesseract-ocr"
        echo "      - macOS: brew install tesseract"
        TESSERACT_AVAILABLE=0
    fi
    
    if [ $MISSING_DEPS -eq 1 ]; then
        echo ""
        echo "❌ Critical dependencies are missing. Please install them and try again."
        exit 1
    fi
    
    echo ""
    echo "2. Checking Node.js Dependencies..."
    if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules)" ]; then
        echo "   📦 node_modules missing or empty. Running 'npm install'..."
        npm install
    else
        echo "   ✅ node_modules found."
    fi

    echo ""
    echo "3. Checking Python Libraries..."
    PIP_CMD="pip3"
    
    # Core required libraries
    REQUIRED_LIBS="flask flask-cors pytesseract pandas openpyxl pillow opencv-python-headless pymupdf"
    
    for lib in $REQUIRED_LIBS; do
        if $PIP_CMD show $lib &> /dev/null; then
            echo "   ✅ Found $lib"
        else
            echo "   📦 Installing missing library: $lib..."
            $PIP_CMD install $lib --quiet
        fi
    done
    
    # Check for EasyOCR (optional but recommended)
    echo ""
    echo "3. Checking OCR Engines..."
    
    EASYOCR_AVAILABLE=0
    if $PIP_CMD show easyocr &> /dev/null; then
        echo "   ✅ Found EasyOCR"
        EASYOCR_AVAILABLE=1
    else
        echo "   ⚠️  EasyOCR is not installed."
        echo ""
        echo "   EasyOCR provides better OCR accuracy for scanned documents,"
        echo "   especially for Indian financial statements with Hindi text."
        echo "   It requires PyTorch (~2GB download)."
        echo ""
        
        if [ "$TESSERACT_AVAILABLE" -eq 0 ]; then
            echo "   ⚠️  Neither Tesseract nor EasyOCR is available."
            echo "      OCR for scanned PDFs will NOT work without at least one."
        fi
        
        read -p "   Install EasyOCR and its dependencies? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   📦 Installing EasyOCR (this may take a few minutes)..."
            $PIP_CMD install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
            $PIP_CMD install easyocr --quiet
            
            if $PIP_CMD show easyocr &> /dev/null; then
                echo "   ✅ EasyOCR installed successfully"
                EASYOCR_AVAILABLE=1
            else
                echo "   ❌ EasyOCR installation failed. Continuing without it."
            fi
        else
            echo "   ℹ️  Skipping EasyOCR installation. OCR may be limited to Tesseract."
        fi
    fi
    
    # Summary
    echo ""
    echo "   OCR Status:"
    if [ "$TESSERACT_AVAILABLE" -eq 1 ] && [ "$EASYOCR_AVAILABLE" -eq 1 ]; then
        echo "   ✅ Both Tesseract and EasyOCR available (Best coverage)"
    elif [ "$TESSERACT_AVAILABLE" -eq 1 ]; then
        echo "   ✅ Tesseract available (Basic OCR)"
    elif [ "$EASYOCR_AVAILABLE" -eq 1 ]; then
        echo "   ✅ EasyOCR available (Deep Learning OCR)"
    else
        echo "   ⚠️  No OCR engine available - scanned PDFs will not be readable"
    fi
}

check_dependencies

# =============================================================================
# Process Cleanup (Prevent Multiple Instances)
# =============================================================================

echo "2. Cleaning up existing instances..."

# Kill any existing financial-calculator binaries
if pgrep -x "financial-calculator" > /dev/null; then
    echo "   🔄 Stopping existing Desktop App..."
    pkill -x "financial-calculator" 2>/dev/null
    sleep 1
fi

# Kill any existing Vite servers on our dev port
if lsof -Pi :1420 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔄 Stopping existing Vite server..."
    kill $(lsof -t -i:1420) 2>/dev/null
    sleep 1
fi

# Kill existing Python process on port 8765
if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔄 Stopping existing Python API..."
    kill $(lsof -t -i:8765) 2>/dev/null
    sleep 1
fi

# =============================================================================
# Main Execution
# =============================================================================

# Step 1: Start Python Backend API
echo ""
echo "3. Starting Python Backend API..."
# Kill existing process on port 8765 to ensure latest code is running
if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔄 Stopping existing Python API..."
    kill $(lsof -t -i:8765) 2>/dev/null
    sleep 1
fi

python3 python/api.py --server 8765 2>&1 | tee python-api.log &
PYTHON_PID=$!
sleep 2

if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Python API started on port 8765 (PID: $PYTHON_PID)"
else
    echo "   ⚠️  Python API may have failed to start. Check python-api.log"
    # Tail the log to show error
    tail -n 10 python-api.log
fi

# Step 2: Configure Graphics & Launch Desktop App
echo ""
echo "4. Launching Financial Calculator Desktop App..."

# Graphics backend configuration for Linux (Wayland focus)
export GDK_BACKEND=wayland
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export QT_QPA_PLATFORM=wayland
export MOZ_ENABLE_WAYLAND=1
export WEBKIT_DISABLE_COMPOSITING_MODE=1
export WEBKIT_DISABLE_DMABUF_RENDERER=1

# Fallback to X11 if Wayland is not available
if [ -z "$WAYLAND_DISPLAY" ] && [ -n "$DISPLAY" ]; then
    echo "   ⚠️  Wayland not detected, using X11"
    export GDK_BACKEND=x11
else
    echo "   ✓ Using Wayland graphics backend"
fi

echo ""
echo "=========================================="
echo "✅ Starting Full Stack Services..."
echo "   🐍 Python API: http://localhost:8765"
echo "   🖥️  Desktop App launching..."
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start Tauri in foreground (this will also start Vite via devUrl if configured in tauri.conf)
npm run tauri dev

# Keep script running is handled by foreground process
wait

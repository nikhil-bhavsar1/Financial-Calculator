#!/bin/bash

echo "=== Financial Calculator - Full Stack Launcher ==="
echo ""

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null
        echo "   ✓ Python API stopped"
    fi
    if [ ! -z "$VITE_PID" ]; then
        kill $VITE_PID 2>/dev/null
        echo "   ✓ Vite server stopped"
    fi
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
    else
        echo "   ⚠️  Tesseract OCR is missing (Required for scanned PDFs)."
        echo "      To install:"
        echo "      - Fedora: sudo dnf install tesseract tesseract-langpack-eng"
        echo "      - Ubuntu/Debian: sudo apt install tesseract-ocr"
        echo "      - macOS: brew install tesseract"
    fi
    
    if [ $MISSING_DEPS -eq 1 ]; then
        echo ""
        echo "❌ Critical dependencies are missing. Please install them and try again."
        exit 1
    fi
    
    echo ""
    echo "2. Checking Python Libraries..."
    PIP_CMD="pip3"
    REQUIRED_LIBS="flask flask-cors pytesseract pandas openpyxl pillow opencv-python-headless pymupdf"
    
    for lib in $REQUIRED_LIBS; do
        if $PIP_CMD show $lib &> /dev/null; then
            echo "   ✅ Found $lib"
        else
            echo "   📦 Installing missing library: $lib..."
            $PIP_CMD install $lib --quiet
        fi
    done
}

check_dependencies

# =============================================================================
# Main Execution
# =============================================================================

# Step 1: Start Python Backend API
echo ""
echo "3. Starting Python Backend API..."
if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Python API already running on port 8765"
else
    python3 python/api.py --server 8765 2>&1 | tee python-api.log &
    PYTHON_PID=$!
    sleep 2
    if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   ✅ Python API started on port 8765 (PID: $PYTHON_PID)"
    else
        echo "   ⚠️  Python API may still be starting. Check python-api.log"
    fi
fi

# Step 2: Start Vite Dev Server
echo ""
echo "2. Starting Vite Development Server..."
if lsof -Pi :1420 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Vite server already running on port 1420"
else
    npm run dev > vite.log 2>&1 &
    VITE_PID=$!
    echo "   ⏳ Waiting for Vite server to start..."
    for i in {1..20}; do
        if curl -s http://localhost:1420 > /dev/null 2>&1; then
            echo "   ✅ Vite server started on port 1420 (PID: $VITE_PID)"
            break
        fi
        sleep 1
    done
    if ! curl -s http://localhost:1420 > /dev/null 2>&1; then
        echo "   ❌ Vite server failed to start. Check vite.log"
        exit 1
    fi
fi

# Step 3: Open in browser
echo ""
echo "3. Opening application in browser..."
if command -v xdg-open > /dev/null 2>&1; then
    xdg-open http://localhost:1420 2>/dev/null &
    echo "   ✅ Browser launched"
else
    echo "   ℹ️  Please open http://localhost:1420 in your browser"
fi

# Step 4: Optional Desktop App
echo ""
echo "4. Desktop app options:"
echo "   The web version is now running at http://localhost:1420"
echo ""
read -p "Also launch Tauri desktop app? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Configuring graphics for Tauri..."
    
    # Graphics backend configuration
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
    
    echo "   Starting Tauri desktop app..."
    npm run tauri dev 2>&1 | tee tauri-output.log &
    TAURI_PID=$!
    echo "   ✅ Desktop app launched (PID: $TAURI_PID)"
fi

echo ""
echo "=========================================="
echo "✅ Financial Calculator is running!"
echo ""
echo "   📊 Web App:    http://localhost:1420"
echo "   🐍 Python API: http://localhost:8765"
echo ""
echo "   Logs:"
echo "   - Vite:   vite.log"
echo "   - Python: python-api.log"
echo "   - Tauri:  tauri-output.log (if enabled)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Keep script running
wait

#!/bin/bash

# Tauri Desktop App Launcher - Modern Wayland Graphics
echo "=== Financial Calculator Desktop Launcher ==="

# =============================================================================
# OCR Dependency Check
# =============================================================================

check_ocr_engines() {
    echo ""
    echo "Checking OCR engines..."
    
    TESSERACT_AVAILABLE=0
    EASYOCR_AVAILABLE=0
    PIP_CMD="pip3"
    
    # Check Tesseract
    if command -v tesseract &> /dev/null; then
        echo "   ✅ Tesseract OCR available"
        TESSERACT_AVAILABLE=1
    else
        echo "   ⚠️  Tesseract OCR not found"
    fi
    
    # Check EasyOCR
    if $PIP_CMD show easyocr &> /dev/null 2>&1; then
        echo "   ✅ EasyOCR available"
        EASYOCR_AVAILABLE=1
    else
        echo "   ⚠️  EasyOCR not installed"
    fi
    
    # If neither is available, offer to install EasyOCR
    if [ "$TESSERACT_AVAILABLE" -eq 0 ] && [ "$EASYOCR_AVAILABLE" -eq 0 ]; then
        echo ""
        echo "   ⚠️  No OCR engine available!"
        echo "   Scanned PDFs will NOT be readable without OCR."
        echo ""
        echo "   EasyOCR provides deep learning-based OCR with support for"
        echo "   English and Hindi text (common in Indian financial reports)."
        echo "   It requires PyTorch (~2GB download)."
        echo ""
        
        read -p "   Install EasyOCR now? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   📦 Installing EasyOCR (this may take a few minutes)..."
            $PIP_CMD install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
            $PIP_CMD install easyocr --quiet
            
            if $PIP_CMD show easyocr &> /dev/null 2>&1; then
                echo "   ✅ EasyOCR installed successfully"
            else
                echo "   ❌ Installation failed. Continuing anyway..."
            fi
        else
            echo "   ℹ️  Skipping. OCR features will be unavailable."
        fi
    fi
}

check_ocr_engines

# =============================================================================
# Graphics Configuration
# =============================================================================

echo ""
echo "Configuring graphics backend..."

# Use Wayland (modern GNU/Linux graphics standard)
export GDK_BACKEND=wayland
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export QT_QPA_PLATFORM=wayland
export MOZ_ENABLE_WAYLAND=1

# WebKit optimizations for Wayland
export WEBKIT_DISABLE_COMPOSITING_MODE=1
export WEBKIT_DISABLE_DMABUF_RENDERER=1

# Fallback to X11 if Wayland is not available
if [ -z "$WAYLAND_DISPLAY" ] && [ -n "$DISPLAY" ]; then
    echo "   ⚠️  Wayland not detected, falling back to X11"
    export GDK_BACKEND=x11
else
    echo "   ✓ Using Wayland graphics backend"
fi

# =============================================================================
# Server Checks
# =============================================================================

echo ""
echo "Checking required services..."

# Ensure Python API is running
if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ✅ Python API running on port 8765"
else
    echo "   ⚠️  Python API is not running."
    echo "      Starting Python API server..."
    python3 python/api.py --server 8765 > python-api.log 2>&1 &
    sleep 2
    if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "   ✅ Python API started on port 8765"
    else
        echo "   ❌ Failed to start Python API. Check python-api.log"
        exit 1
    fi
fi

# Ensure Vite is running
if lsof -Pi :1420 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   ✅ Vite server running on port 1420"
else
    echo "   ❌ Vite server is not running on port 1420"
    echo "      Please run 'npm run dev' in another terminal first"
    exit 1
fi

# =============================================================================
# Launch Desktop App
# =============================================================================

echo ""
echo "Starting Tauri desktop application..."
npm run tauri dev

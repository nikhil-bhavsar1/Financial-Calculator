#!/bin/bash

# =============================================================================
# OCR Setup Script for Financial Calculator
# =============================================================================
# This script checks and optionally installs OCR engines required for
# processing scanned PDF documents.
#
# Supported OCR Engines:
#   - Tesseract: Fast, system-level OCR (requires system package)
#   - EasyOCR: Deep learning based OCR with multi-language support
#
# Usage: ./scripts/setup-ocr.sh [--auto]
#        --auto: Automatically install EasyOCR without prompting
# =============================================================================

set -e

echo "=== Financial Calculator: OCR Setup ==="
echo ""

AUTO_INSTALL=0
if [ "$1" == "--auto" ]; then
    AUTO_INSTALL=1
fi

PIP_CMD="pip3"

# =============================================================================
# Check Tesseract
# =============================================================================

echo "Checking Tesseract OCR..."

TESSERACT_AVAILABLE=0
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "   ✅ Found: $TESSERACT_VERSION"
    TESSERACT_AVAILABLE=1
else
    echo "   ❌ Not installed"
    echo ""
    echo "   To install Tesseract:"
    echo "   • Fedora/RHEL: sudo dnf install tesseract tesseract-langpack-eng tesseract-langpack-hin"
    echo "   • Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin"
    echo "   • macOS: brew install tesseract tesseract-lang"
    echo "   • Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

echo ""

# =============================================================================
# Check EasyOCR
# =============================================================================

echo "Checking EasyOCR..."

EASYOCR_AVAILABLE=0
if $PIP_CMD show easyocr &> /dev/null 2>&1; then
    EASYOCR_VERSION=$($PIP_CMD show easyocr | grep Version | awk '{print $2}')
    echo "   ✅ Found: EasyOCR $EASYOCR_VERSION"
    EASYOCR_AVAILABLE=1
else
    echo "   ❌ Not installed"
fi

echo ""

# =============================================================================
# Check PyTorch (required by EasyOCR)
# =============================================================================

echo "Checking PyTorch..."

PYTORCH_AVAILABLE=0
if $PIP_CMD show torch &> /dev/null 2>&1; then
    PYTORCH_VERSION=$($PIP_CMD show torch | grep Version | awk '{print $2}')
    echo "   ✅ Found: PyTorch $PYTORCH_VERSION"
    PYTORCH_AVAILABLE=1
else
    echo "   ❌ Not installed (required by EasyOCR)"
fi

echo ""

# =============================================================================
# Summary and Installation Options
# =============================================================================

echo "==========================================="
echo "OCR Engine Status:"
echo "==========================================="

if [ "$TESSERACT_AVAILABLE" -eq 1 ] && [ "$EASYOCR_AVAILABLE" -eq 1 ]; then
    echo "✅ EXCELLENT: Both Tesseract and EasyOCR are available"
    echo "   You have the best OCR coverage for all document types."
    exit 0
elif [ "$TESSERACT_AVAILABLE" -eq 1 ]; then
    echo "✅ GOOD: Tesseract is available"
    echo "   Basic OCR will work. Consider adding EasyOCR for better accuracy."
elif [ "$EASYOCR_AVAILABLE" -eq 1 ]; then
    echo "✅ GOOD: EasyOCR is available"
    echo "   Deep learning OCR will work. Consider adding Tesseract for faster processing."
else
    echo "⚠️  WARNING: No OCR engine is available!"
    echo "   Scanned PDFs will NOT be readable."
fi

echo ""

# =============================================================================
# Install EasyOCR if needed
# =============================================================================

if [ "$EASYOCR_AVAILABLE" -eq 0 ]; then
    echo "==========================================="
    echo "EasyOCR Installation"
    echo "==========================================="
    echo ""
    echo "EasyOCR provides:"
    echo "   • Deep learning-based OCR with high accuracy"
    echo "   • Support for 80+ languages including Hindi"
    echo "   • Better handling of complex layouts and fonts"
    echo ""
    echo "Requirements:"
    echo "   • PyTorch (CPU version, ~2GB download)"
    echo "   • ~500MB additional for EasyOCR models"
    echo ""
    
    INSTALL_EASYOCR=0
    
    if [ "$AUTO_INSTALL" -eq 1 ]; then
        INSTALL_EASYOCR=1
    else
        read -p "Install EasyOCR now? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            INSTALL_EASYOCR=1
        fi
    fi
    
    if [ "$INSTALL_EASYOCR" -eq 1 ]; then
        echo ""
        echo "Installing PyTorch (CPU version)..."
        $PIP_CMD install torch torchvision --index-url https://download.pytorch.org/whl/cpu
        
        echo ""
        echo "Installing EasyOCR..."
        $PIP_CMD install easyocr
        
        echo ""
        # Verify installation
        if $PIP_CMD show easyocr &> /dev/null 2>&1; then
            echo "✅ EasyOCR installed successfully!"
            echo ""
            echo "Note: EasyOCR will download language models on first use (~100MB each)."
        else
            echo "❌ EasyOCR installation failed."
            echo "   Please check the error messages above and try again."
            exit 1
        fi
    else
        echo "Skipping EasyOCR installation."
    fi
fi

echo ""
echo "Setup complete!"

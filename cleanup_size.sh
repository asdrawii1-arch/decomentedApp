#!/bin/bash
# Project Size Cleanup Script
# This script helps reduce the project size by cleaning caches and optionally switching to CPU-only PyTorch

echo "=================================================="
echo "Project Size Cleanup Script"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment is not activated!"
    echo "Please run: source venv/bin/activate"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1️⃣  Cleaning pip cache..."
pip cache purge
echo "✓ Pip cache cleaned"
echo ""

echo "2️⃣  Removing Python bytecode files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "✓ Python bytecode cleaned"
echo ""

echo "3️⃣  Current PyTorch installation:"
pip show torch 2>/dev/null | grep -E "^(Name|Version|Location)" || echo "PyTorch not found"
echo ""

echo "=================================================="
echo "PyTorch Optimization Options:"
echo "=================================================="
echo ""
echo "Current PyTorch likely includes CUDA (3-4 GB)"
echo ""
echo "Choose an option:"
echo "  1) Switch to CPU-only PyTorch (saves 2-3 GB) - RECOMMENDED"
echo "  2) Remove OCR completely (saves 4-6 GB)"
echo "  3) Keep current installation (no change)"
echo "  4) Skip PyTorch optimization"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Switching to CPU-only PyTorch..."
        echo "This will:"
        echo "  - Uninstall current torch, torchvision, torchaudio"
        echo "  - Install CPU-only versions (~800 MB instead of 3+ GB)"
        echo ""
        read -p "Proceed? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip uninstall -y torch torchvision torchaudio 2>/dev/null
            pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
            echo "✓ Switched to CPU-only PyTorch"
        fi
        ;;
    2)
        echo ""
        echo "Removing OCR packages..."
        echo "This will remove:"
        echo "  - torch, torchvision, torchaudio"
        echo "  - easyocr"
        echo "  - pytesseract"
        echo ""
        echo "⚠️  OCR features will not work after this!"
        echo ""
        read -p "Are you sure? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip uninstall -y torch torchvision torchaudio easyocr pytesseract 2>/dev/null
            echo "✓ OCR packages removed"
            echo ""
            echo "You can use requirements-minimal.txt for future installations:"
            echo "  pip install -r requirements-minimal.txt"
        fi
        ;;
    3)
        echo ""
        echo "Keeping current PyTorch installation"
        ;;
    4)
        echo ""
        echo "Skipping PyTorch optimization"
        ;;
    *)
        echo ""
        echo "Invalid choice, skipping PyTorch optimization"
        ;;
esac

echo ""
echo "=================================================="
echo "Cleanup Complete!"
echo "=================================================="
echo ""
echo "To check project size, run:"
echo "  du -sh . 2>/dev/null"
echo ""
echo "For more information, see: SIZE_INVESTIGATION.md"

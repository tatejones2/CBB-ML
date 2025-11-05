#!/bin/bash

# Quick Start Script for CBB-ML Project
# This script sets up and runs an initial data collection

echo "=========================================="
echo "CBB-ML Quick Start"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate venv
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Check if packages are installed
echo "✓ Checking dependencies..."
python -c "import pandas, requests, sklearn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Some packages are missing!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Test ESPN API
echo "Step 1: Testing ESPN API access..."
python scripts/test_espn_api.py
if [ $? -ne 0 ]; then
    echo "❌ ESPN API test failed!"
    exit 1
fi

echo ""
echo "Step 2: Testing scraper..."
python scripts/test_scraper.py
if [ $? -ne 0 ]; then
    echo "❌ Scraper test failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All tests passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run 'python scripts/run_scraper.py' to collect data"
echo "2. Choose option 1 to scrape the current 2025 season"
echo "3. Run 'python scripts/inspect_data.py' to view the data"
echo ""
echo "For more information, see README.md and docs/cbb_ml_guide.md"
echo ""

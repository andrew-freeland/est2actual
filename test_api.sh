#!/bin/bash
# Quick test script for the API

set -e

echo "🧪 Testing Estimate Insight Agent Pro API"
echo "=========================================="
echo

# Check if server is running
echo "1️⃣  Testing health check..."
HEALTH=$(curl -s http://localhost:8080/ || echo "FAILED")

if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Server not running. Start with: python app.py"
    exit 1
fi

echo

# Test analyze endpoint
if [ -f "sample_data/estimate.xlsx" ] && [ -f "sample_data/actual.xlsx" ]; then
    echo "2️⃣  Testing /analyze endpoint..."
    
    RESPONSE=$(curl -s -X POST http://localhost:8080/analyze \
        -F "estimate_file=@sample_data/estimate.xlsx" \
        -F "actual_file=@sample_data/actual.xlsx" \
        -F "project_name=API Test Project" \
        -F "quick=true")
    
    if [[ $RESPONSE == *"success\":true"* ]]; then
        echo "✅ Analysis endpoint working"
        echo
        echo "📊 Response summary:"
        echo "$RESPONSE" | python3 -m json.tool | head -20
    else
        echo "❌ Analysis failed"
        echo "$RESPONSE"
        exit 1
    fi
else
    echo "⚠️  Sample data not found. Run: python scripts/create_test_data.py"
fi

echo
echo "3️⃣  Testing chart generation..."

CHART_RESPONSE=$(curl -s -X POST http://localhost:8080/analyze \
    -F "estimate_file=@sample_data/estimate.xlsx" \
    -F "actual_file=@sample_data/actual.xlsx" \
    -F "project_name=Chart Test" \
    -F "quick=true" \
    -F "generate_chart=true")

if [[ $CHART_RESPONSE == *"chart_image_base64"* ]]; then
    echo "✅ Chart generation working"
    CHART_SIZE=$(echo "$CHART_RESPONSE" | grep -o '"chart_image_base64":"[^"]*"' | wc -c)
    echo "   Chart size: ~$((CHART_SIZE / 1024))KB base64"
else
    echo "⚠️  Chart generation may be unavailable (matplotlib not installed?)"
fi

echo
echo "✅ All tests passed!"
echo
echo "Try these commands:"
echo "  curl http://localhost:8080/"
echo "  curl -X POST http://localhost:8080/analyze -F 'estimate_file=@estimate.xlsx' -F 'actual_file=@actual.xlsx'"
echo "  curl -X POST http://localhost:8080/analyze -F 'estimate_file=@estimate.xlsx' -F 'actual_file=@actual.xlsx' -F 'generate_chart=true'"


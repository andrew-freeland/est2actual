# API Quick Start - 5 Minutes to Running API

Get the API running in 5 minutes!

---

## Step 1: Install Dependencies (if not already done)

```bash
cd /Users/andrew-hci/est2actual
pip install -r requirements.txt
```

---

## Step 2: Generate Test Data

```bash
python scripts/create_test_data.py
```

This creates `sample_data/estimate.xlsx` and `sample_data/actual.xlsx`.

---

## Step 3: Start the API Server

### Option A: Development Mode (Flask)
```bash
python app.py
```

### Option B: Production Mode (Gunicorn)
```bash
gunicorn app:app --bind 0.0.0.0:8080
```

### Option C: Using Make
```bash
make api      # Development
make api-prod # Production
```

**The server will start on `http://localhost:8080`** ✅

---

## Step 4: Test the API

### Health Check:
```bash
curl http://localhost:8080/
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Estimate Insight Agent Pro",
  "version": "2.0.0"
}
```

### Analyze Files (Quick Mode - No AI):
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@sample_data/estimate.xlsx" \
  -F "actual_file=@sample_data/actual.xlsx" \
  -F "project_name=API Test" \
  -F "quick=true"
```

Expected response:
```json
{
  "success": true,
  "project_name": "API Test",
  "summary": {
    "total_estimated": 113000.0,
    "total_actual": 117000.0,
    "total_variance": 4000.0,
    "total_variance_pct": 3.5,
    ...
  },
  "narrative": "Project Budget Analysis\n========================\n...",
  "variance_data": [...]
}
```

### With AI (Requires GCP Setup):
```bash
# First: export GCP_PROJECT_ID=your-project-id

curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@sample_data/estimate.xlsx" \
  -F "actual_file=@sample_data/actual.xlsx" \
  -F "project_name=AI Test"
```

### With Memory (Requires GCP + Firestore):
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@sample_data/estimate.xlsx" \
  -F "actual_file=@sample_data/actual.xlsx" \
  -F "project_name=Memory Test" \
  -F "save_memory=true"
```

### Get Project History:
```bash
curl http://localhost:8080/history/Memory%20Test
```

---

## Step 5: Integrate with Your App

### Python:
```python
import requests

with open('estimate.xlsx', 'rb') as est, open('actual.xlsx', 'rb') as act:
    response = requests.post('http://localhost:8080/analyze', 
        files={'estimate_file': est, 'actual_file': act},
        data={'project_name': 'My Project', 'save_memory': 'true'}
    )
    
result = response.json()
print(result['narrative'])
```

### JavaScript:
```javascript
const formData = new FormData();
formData.append('estimate_file', estimateFile);
formData.append('actual_file', actualFile);
formData.append('project_name', 'My Project');

const response = await fetch('http://localhost:8080/analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.narrative);
```

### cURL Script:
```bash
#!/bin/bash
RESULT=$(curl -s -X POST http://localhost:8080/analyze \
  -F "estimate_file=@$1" \
  -F "actual_file=@$2" \
  -F "project_name=$3")

echo "$RESULT" | jq '.narrative'
```

Usage: `./analyze.sh estimate.xlsx actual.xlsx "Q4 Campaign"`

---

## 🐳 Docker Quick Start

### Build:
```bash
docker build -t est2actual .
```

### Run API:
```bash
docker run -p 8080:8080 est2actual
```

### Run CLI:
```bash
docker run \
  -v $(pwd)/sample_data:/data \
  est2actual \
  python main.py /data/estimate.xlsx /data/actual.xlsx --quick
```

---

## ☁️ Cloud Run Quick Deploy

### One Command:
```bash
./cloud/deploy.sh
```

### Manual:
```bash
gcloud builds submit --tag gcr.io/YOUR-PROJECT/est2actual
gcloud run deploy est2actual \
  --image gcr.io/YOUR-PROJECT/est2actual \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🧪 Automated Testing

```bash
# Starts server in background and tests all endpoints
make test-api
```

Or manually:
```bash
# Terminal 1: Start server
python app.py

# Terminal 2: Run tests
./test_api.sh
```

---

## 📊 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/analyze` | POST | Analyze Excel files |
| `/history/<name>` | GET | Get project history |

---

## 🔧 Troubleshooting

### "Address already in use"
Another process is using port 8080. Kill it or use a different port:
```bash
PORT=8081 python app.py
```

### "Missing GCP_PROJECT_ID"
Set environment variable:
```bash
export GCP_PROJECT_ID=your-project-id
python app.py
```

### "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### "Gemini failed"
Use quick mode to test without AI:
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "quick=true"
```

---

## 🎯 Next Steps

1. ✅ **API is running** - You can now accept HTTP requests
2. 📖 **Read full docs** - See [API_USAGE.md](API_USAGE.md)
3. 🔐 **Add auth** - Implement API keys or OAuth
4. 📊 **Monitor** - Add logging and metrics
5. 🚀 **Deploy** - Push to Cloud Run for production

---

## 🎉 You're Done!

The API is now running and ready to analyze budget variances via HTTP!

**CLI still works too:**
```bash
python main.py estimate.xlsx actual.xlsx
```

**Choose the interface that fits your workflow!** 🚀


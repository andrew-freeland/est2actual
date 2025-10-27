# API Usage Guide

The Estimate Insight Agent Pro can be used as both a **CLI tool** and a **REST API**.

---

## 🚀 Running Modes

### Mode 1: CLI (Command Line)

```bash
python main.py estimate.xlsx actual.xlsx --project-name "Q4 Campaign" --save-memory
```

Best for:
- Local analysis
- Batch processing
- Scripted workflows

### Mode 2: API (HTTP Server)

```bash
# Development
python app.py

# Production
gunicorn app:app --bind 0.0.0.0:8080
```

Best for:
- Web applications
- Microservices
- Cloud deployment

---

## 📡 API Endpoints

### `GET /`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Estimate Insight Agent Pro",
  "version": "2.0.0",
  "endpoints": {
    "POST /analyze": "Analyze estimate vs actual files",
    "GET /history/<project_name>": "Get project history",
    "GET /": "Health check"
  }
}
```

---

### `POST /analyze`

Analyze estimate vs actual Excel files.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Files**:
  - `estimate_file` (required): Excel file with estimated costs
  - `actual_file` (required): Excel file with actual costs
- **Form Data**:
  - `project_name` (optional): Name of the project (default: "Unnamed Project")
  - `save_memory` (optional): "true" to store in Firestore (default: "false")
  - `quick` (optional): "true" to skip Gemini and use quick summary (default: "false")
  - `generate_chart` (optional): "true" to generate variance bar chart (default: "false")

**Response (Success):**
```json
{
  "success": true,
  "project_name": "Q4 Campaign",
  "summary": {
    "total_estimated": 113000.0,
    "total_actual": 116500.0,
    "total_variance": 3500.0,
    "total_variance_pct": 3.1,
    "over_budget_categories": 3,
    "under_budget_categories": 2,
    "biggest_overrun": {
      "category": "Labor",
      "amount": 5000.0
    },
    "biggest_underrun": {
      "category": "Materials",
      "amount": -3000.0
    }
  },
  "narrative": "This project finished 3.1% over budget...",
  "variance_data": [
    {
      "Category": "Labor",
      "Estimated": 50000.0,
      "Actual": 55000.0,
      "Variance": 5000.0,
      "Variance_%": 10.0
    },
    ...
  ],
  "pattern_detection_enabled": true,
  "similar_projects_count": 2,
  "memory_id": "abc123xyz",
  "chart_image_base64": "iVBORw0KGgoAAAANSUhEUgAAB4AAAAQ4CAIAAABnsW5JAAA..."
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message here"
}
```

---

### `GET /history/<project_name>`

Retrieve all historical analyses for a specific project.

**Example:**
```
GET /history/Q4%20Campaign
```

**Response:**
```json
{
  "success": true,
  "project_name": "Q4 Campaign",
  "count": 3,
  "history": [
    {
      "id": "abc123",
      "project_name": "Q4 Campaign",
      "narrative": "...",
      "variance_summary": {...},
      "created_at": "2025-10-27T10:30:00",
      "metadata": {...}
    },
    ...
  ]
}
```

---

## 🧪 Testing the API

### Using cURL

**Health Check:**
```bash
curl http://localhost:8080/
```

**Analyze Files:**
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Q4 Campaign" \
  -F "save_memory=true"
```

**Get History:**
```bash
curl http://localhost:8080/history/Q4%20Campaign
```

**Analyze with Chart Generation:**
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Q4 Campaign" \
  -F "generate_chart=true"
```

### Using Python `requests`

```python
import requests

# Analyze files
with open('estimate.xlsx', 'rb') as est, open('actual.xlsx', 'rb') as act:
    files = {
        'estimate_file': est,
        'actual_file': act
    }
    data = {
        'project_name': 'Q4 Campaign',
        'save_memory': 'true'
    }
    
    response = requests.post('http://localhost:8080/analyze', 
                            files=files, 
                            data=data)
    result = response.json()
    
    if result['success']:
        print(f"Narrative: {result['narrative']}")
        print(f"Total Variance: ${result['summary']['total_variance']:,.2f}")
        
        # If chart was generated, save it
        if 'chart_image_base64' in result:
            import base64
            chart_data = base64.b64decode(result['chart_image_base64'])
            with open('variance_chart.png', 'wb') as f:
                f.write(chart_data)
            print("Chart saved to: variance_chart.png")
    else:
        print(f"Error: {result['error']}")

# Get history
response = requests.get('http://localhost:8080/history/Q4%20Campaign')
history = response.json()
print(f"Found {history['count']} past analyses")
```

### Using JavaScript (fetch)

```javascript
// Analyze files
const formData = new FormData();
formData.append('estimate_file', estimateFileInput.files[0]);
formData.append('actual_file', actualFileInput.files[0]);
formData.append('project_name', 'Q4 Campaign');
formData.append('save_memory', 'true');

// Optional: enable chart generation
formData.append('generate_chart', 'true');

const response = await fetch('http://localhost:8080/analyze', {
  method: 'POST',
  body: formData
});

const result = await response.json();

if (result.success) {
  console.log('Narrative:', result.narrative);
  console.log('Variance:', result.summary.total_variance);
  
  // If chart was generated, display it
  if (result.chart_image_base64) {
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${result.chart_image_base64}`;
    document.body.appendChild(img);
  }
}

// Get history
const historyResponse = await fetch('http://localhost:8080/history/Q4%20Campaign');
const history = await historyResponse.json();
console.log(`Found ${history.count} past analyses`);
```

---

## 🐳 Running with Docker

### Build the Image:
```bash
docker build -t est2actual .
```

### Run as API:
```bash
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GCP_REGION=us-central1 \
  est2actual
```

### Run as CLI:
```bash
docker run \
  -v $(pwd)/data:/data \
  -e GCP_PROJECT_ID=your-project-id \
  est2actual \
  python main.py /data/estimate.xlsx /data/actual.xlsx --quick
```

---

## ☁️ Deploying to Cloud Run

### Option 1: Using Deploy Script

```bash
./cloud/deploy.sh
```

### Option 2: Manual Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/est2actual

# Deploy to Cloud Run
gcloud run deploy est2actual \
  --image gcr.io/YOUR-PROJECT-ID/est2actual \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=YOUR-PROJECT-ID,GCP_REGION=us-central1" \
  --memory 1Gi \
  --timeout 300
```

### Test Cloud Run Deployment:

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe est2actual \
  --region us-central1 \
  --format="value(status.url)")

# Health check
curl $SERVICE_URL/

# Analyze files
curl -X POST $SERVICE_URL/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Production Test" \
  -F "save_memory=true"
```

---

## 🔐 Authentication (Optional)

For production, you may want to add authentication.

### Using Cloud Run IAM

Deploy without `--allow-unauthenticated`:

```bash
gcloud run deploy est2actual \
  --image gcr.io/YOUR-PROJECT-ID/est2actual \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated
```

Then call with authentication:

```bash
# Get ID token
TOKEN=$(gcloud auth print-identity-token)

# Make authenticated request
curl -X POST $SERVICE_URL/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx"
```

### Using API Keys (Custom)

Add to `routes/api.py`:

```python
@app.before_request
def check_api_key():
    if request.endpoint != 'health_check':
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('API_KEY')
        
        if not api_key or api_key != expected_key:
            return jsonify({'error': 'Unauthorized'}), 401
```

---

## 📊 Performance

### Local Development:
- Cold start: ~2-3 seconds
- Warm request: ~3-6 seconds (with Gemini)
- Quick mode: ~0.5-1 second

### Cloud Run (Production):
- Cold start: ~5-10 seconds (container startup)
- Warm request: ~3-6 seconds
- Auto-scaling: 0-1000 instances

### Optimization Tips:
- Use `quick=true` for faster responses without AI
- Set min instances to 1 to avoid cold starts:
  ```bash
  gcloud run services update est2actual --min-instances=1
  ```
- Increase memory for faster processing:
  ```bash
  gcloud run services update est2actual --memory=2Gi
  ```

---

## 🛠️ Troubleshooting

### "Connection refused" error
**Solution**: Make sure the server is running:
```bash
python app.py
```

### "Missing GCP_PROJECT_ID" error
**Solution**: Set environment variable:
```bash
export GCP_PROJECT_ID=your-project-id
python app.py
```

### "File too large" error
**Solution**: Files must be < 16MB. Increase limit in `routes/api.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Timeout on Cloud Run
**Solution**: Increase timeout:
```bash
gcloud run services update est2actual --timeout=600
```

---

## 🔄 Migrating from CLI to API

### Before (CLI):
```bash
python main.py estimate.xlsx actual.xlsx --project-name "Q4" --save-memory
```

### After (API):
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Q4" \
  -F "save_memory=true"
```

### Both modes use the same core logic - no data format changes!

---

## 📝 Summary

| Mode | Use Case | Command |
|------|----------|---------|
| CLI | Local/scripting | `python main.py ...` |
| API Dev | Testing | `python app.py` |
| API Prod | Production | `gunicorn app:app` |
| Docker | Containerized | `docker run ...` |
| Cloud Run | Serverless | `gcloud run deploy ...` |

**The API and CLI share the same analysis engine - choose based on your integration needs!** 🚀


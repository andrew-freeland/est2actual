# Estimate Insight Agent Pro

AI-powered cost variance analysis system using **Google Vertex AI Gemini 1.5 Pro**.

## 🎯 What It Does

1. **Accepts** two Excel files: estimated costs vs. actual costs
2. **Analyzes** variance across budget categories using pandas
3. **Generates** narrative insights explaining what happened using Gemini
4. **Stores** project memory in Firestore for pattern detection over time

## 🏗️ Architecture

```
est2actual/
├── parsers/              # Excel ingestion & dataframe comparison
├── report/               # Gemini-powered narrative generation
├── memory/               # Firestore storage with embeddings
├── routes/               # Flask API routes (for Cloud Run)
├── cloud/                # Cloud Run deployment utilities
└── main.py               # CLI runner
```

**Principles:**
- Modular, single-purpose components
- Google Cloud native (Vertex AI, Firestore)
- Easily extensible for charts, exports, dashboards

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Google Cloud Project** with:
   - Vertex AI API enabled
   - Firestore enabled
   - Authentication set up

### Setup

```bash
# 1. Clone and navigate
cd est2actual

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Authenticate with Google Cloud
gcloud auth application-default login

# 5. Set environment variables
cp .env.example .env
# Edit .env with your GCP_PROJECT_ID
```

### Running as CLI

```bash
# Basic usage (quick summary without AI)
python main.py estimate.xlsx actual.xlsx --quick

# With AI insight generation
python main.py estimate.xlsx actual.xlsx --project-name "Q4 Marketing Campaign"

# Save to Firestore memory
python main.py estimate.xlsx actual.xlsx --project-name "Q4 Campaign" --save-memory
```

### Running as API

```bash
# Development mode
python app.py

# Production mode
gunicorn app:app --bind 0.0.0.0:8080

# Test the API
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Q4 Campaign" \
  -F "save_memory=true"
```

**📖 Full API documentation**: See [API_USAGE.md](API_USAGE.md)

## 📊 Excel File Format

Your Excel files should have at minimum:
- **Category column**: Item names (e.g., "Labor", "Materials", "Marketing")
- **Amount column**: Numeric costs

Example:

| Category    | Amount  |
|-------------|---------|
| Labor       | 50000   |
| Materials   | 25000   |
| Marketing   | 15000   |

The parser automatically detects column names like: `Category`, `Name`, `Item`, `Amount`, `Cost`, `Value`, etc.

## 🧠 Memory System

When you use `--save-memory`, the system:
1. Saves the narrative and variance data to Firestore
2. Generates embeddings using Vertex AI text-embedding-gecko
3. Enables future pattern detection across similar projects

## 🌐 Deploying to Cloud Run

### Quick Deploy

```bash
# Automated deployment
./cloud/deploy.sh
```

### Manual Deployment

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/est2actual
gcloud run deploy est2actual \
  --image gcr.io/YOUR-PROJECT-ID/est2actual \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=YOUR-PROJECT-ID" \
  --memory 1Gi \
  --timeout 300
```

### Test Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe est2actual \
  --region us-central1 \
  --format="value(status.url)")

# Test health check
curl $SERVICE_URL/

# Test analysis
curl -X POST $SERVICE_URL/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Production Test"
```

**📖 Full deployment guide**: See [API_USAGE.md](API_USAGE.md)

## 🔐 Required GCP Permissions

Your service account needs:
- `aiplatform.endpoints.predict` (Vertex AI)
- `datastore.entities.create/get/list` (Firestore)

## 📝 Project Log

See [PROJECT_LOG.md](PROJECT_LOG.md) for architecture decisions and feature history.

## 🛠️ Usage Modes

### Mode 1: CLI (Command Line)
Best for local analysis, batch processing, scripted workflows
```bash
python main.py estimate.xlsx actual.xlsx --save-memory
```

### Mode 2: API (HTTP Server)
Best for web apps, microservices, cloud deployment
```bash
gunicorn app:app --bind 0.0.0.0:8080
```

### Mode 3: Docker
Best for containerized deployments
```bash
docker build -t est2actual .
docker run -p 8080:8080 est2actual
```

**📖 Complete usage guide**: See [API_USAGE.md](API_USAGE.md)

## 🎨 Extending

**Add charting:**
- Create `report/generate_charts.py`
- Use matplotlib or plotly
- Export to images or HTML

**Add authentication:**
- Add API key validation in `routes/api.py`
- Use Cloud Run IAM for access control

**Add pattern detection improvements:**
- Migrate to Vertex AI Matching Engine
- Implement vector similarity search
- Build trend analysis dashboards

## 📄 License

MIT


# Estimate Insight Agent Pro

AI-powered cost variance analysis system using **Google Vertex AI Gemini 1.5 Pro**.

## 🎯 What It Does

1. **Accepts** Excel files in two formats:
   - **Separate Files**: Upload estimate and actual cost files separately
   - **Combined File**: Upload a single file with both budget and actual columns (e.g., "Revised Budget Costs" and "Actual Costs")
2. **Analyzes** variance across budget categories using pandas
3. **Generates** narrative insights explaining what happened using Gemini
4. **Stores** project memory in Firestore for pattern detection over time

## 🏗️ Architecture

```
est2actual/
├── parsers/              # Excel ingestion & dataframe comparison
├── report/               # Gemini-powered narrative generation
├── memory/               # Firestore storage with embeddings
├── visuals/              # Chart generation (matplotlib/seaborn)
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

### Running the Web UI (Recommended)

The easiest way to use the system is through the beautiful web interface:

```bash
# Development mode
python web/app.py

# Production mode
gunicorn web.app:app --bind 0.0.0.0:8080

# Then visit http://localhost:8080 in your browser
```

**Features:**
- 🎨 Beautiful Tailwind CSS interface
- 📊 Flexible file upload options:
  - **Separate Files**: Upload estimate and actual files separately
  - **Combined File**: Upload a single file with both budget and actual columns
- 🤖 Real-time AI analysis with Gemini
- 📈 Interactive charts and visualizations
- 🧠 Pattern detection from memory
- 📋 Detailed variance breakdowns with category matching
- 📄 PDF export for comprehensive post-mortem reports

### Running as CLI

```bash
# Basic usage (quick summary without AI)
python main.py estimate.xlsx actual.xlsx --quick

# With AI insight generation
python main.py estimate.xlsx actual.xlsx --project-name "Smith ADU – Office Remodel"

# Save to Firestore memory
python main.py estimate.xlsx actual.xlsx --project-name "Smith ADU – Office Remodel" --save-memory

# Generate variance bar chart
python main.py estimate.xlsx actual.xlsx --project-name "Smith ADU – Office Remodel" --generate-chart

# All features combined
python main.py estimate.xlsx actual.xlsx \
  --project-name "Smith ADU – Office Remodel" \
  --save-memory \
  --generate-chart
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

# Test with chart generation
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "project_name=Q4 Campaign" \
  -F "generate_chart=true"
```

**📖 Full API documentation**: See [API_USAGE.md](API_USAGE.md)

## 📊 Excel File Format

The system supports **two file formats**:

### Format 1: Separate Files (Simple)
Two separate files: one for estimates, one for actuals.

**Minimum requirements:**
- **Category column**: Item names (e.g., "Labor", "Materials", "Marketing")
- **Amount column**: Numeric costs

Example:

| Category    | Amount  |
|-------------|---------|
| Labor       | 50000   |
| Materials   | 25000   |
| Marketing   | 15000   |

### Format 2: Combined File (Advanced)
One file with multiple cost columns. Upload the **same file twice**.

**Minimum requirements:**
- **Category column**: Item names
- **Budget column**: Contains "budget", "estimate", or "revised" in name
- **Actual column**: Contains "actual", "spent", or "final" in name

Example:

| Category    | Revised Budget | Actual Costs |
|-------------|----------------|--------------|
| Labor       | 50000          | 55000        |
| Materials   | 25000          | 22000        |
| Marketing   | 15000          | 18000        |

**📖 See [COMBINED_FORMAT_GUIDE.md](COMBINED_FORMAT_GUIDE.md) for detailed instructions**

The parser automatically detects column names and intelligently selects:
- Estimate columns: `Budget`, `Estimated`, `Revised Budget`, etc.
- Actual columns: `Actual Costs`, `Spent`, `Final Cost`, etc.
- Fallback: `Amount`, `Cost`, `Value`, `Price`, `Total`

## 🧠 Memory System

When you use `--save-memory`, the system:
1. Saves the narrative and variance data to Firestore
2. Generates embeddings using Vertex AI text-embedding-gecko
3. Enables future pattern detection across similar projects

## 💬 Feedback System

The web UI includes an intelligent feedback system to continuously improve insights:

**On Result Page (Detailed Feedback)**:
- Expandable feedback form with arrow toggle
- Thumbs up/down rating
- Optional detailed comments
- Helps identify which insights are most valuable

**On Patterns Page (Quick Feedback)**:
- Simple thumbs up/down buttons
- One-click feedback on historical insights
- Tracks satisfaction over time

All feedback is stored in Firestore for analysis and future AI improvements. The system gracefully handles errors - feedback never breaks the application.

**📖 See [FEEDBACK_QUICKSTART.md](FEEDBACK_QUICKSTART.md) for usage details**

## 🌐 Deploying to Cloud Run

The web UI deploys seamlessly to Cloud Run, giving you a production-ready hosted application.

### Quick Deploy

```bash
# Automated deployment (includes web UI + API)
./cloud/deploy.sh
```

This deploys the complete web interface with:
- Beautiful upload form at `/`
- Results viewer with charts
- Pattern exploration at `/patterns`
- REST API at `/analyze`

### Manual Deployment

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/est2actual
gcloud run deploy estimate-insight-agent \
  --image gcr.io/YOUR-PROJECT-ID/est2actual \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=YOUR-PROJECT-ID,FLASK_ENV=production" \
  --memory 1Gi \
  --cpu 2 \
  --timeout 300
```

### Test Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe estimate-insight-agent \
  --region us-central1 \
  --format="value(status.url)")

echo "Web UI: $SERVICE_URL"
echo "Patterns: $SERVICE_URL/patterns"

# Test via web browser (recommended)
open $SERVICE_URL

# Or test API endpoint
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

### Mode 1: Web UI (Recommended)
**Best for:** Interactive analysis, non-technical users, visual feedback
```bash
python web/app.py
# Visit http://localhost:8080
```

**Features:**
- Upload files through browser interface
- View AI insights in formatted layout
- Generate and view charts inline
- Explore pattern history
- Save results to memory with one click

### Mode 2: CLI (Command Line)
**Best for:** Local analysis, batch processing, scripted workflows
```bash
python main.py estimate.xlsx actual.xlsx --save-memory
```

### Mode 3: REST API (HTTP Server)
**Best for:** Integration with other apps, microservices, programmatic access
```bash
gunicorn app:app --bind 0.0.0.0:8080
```

### Mode 4: Docker
**Best for:** Containerized deployments, Cloud Run
```bash
docker build -t est2actual .
docker run -p 8080:8080 est2actual
```

**📖 Complete usage guide**: See [API_USAGE.md](API_USAGE.md)

## 📊 Chart Generation

The system can generate variance visualizations as PNG charts:

**CLI:**
```bash
python main.py estimate.xlsx actual.xlsx --generate-chart
```

**API:**
```bash
curl -X POST http://localhost:8080/analyze \
  -F "estimate_file=@estimate.xlsx" \
  -F "actual_file=@actual.xlsx" \
  -F "generate_chart=true"
```

The API returns the chart as a base64-encoded image in the response:
```json
{
  "success": true,
  "chart_image_base64": "iVBORw0KGgoAAAANSUhEUg...",
  ...
}
```

## 🖥️ Web UI Workflow

The web interface provides a complete end-to-end experience:

### 1. Upload
- Visit the homepage
- Enter project name
- Upload estimate and actual Excel files
- Choose options (save to memory, generate chart)

### 2. Analysis
- Files are processed automatically
- AI generates insights using Gemini
- Charts are created in real-time
- Similar past projects are retrieved from memory

### 3. Results
- View comprehensive analysis dashboard with:
  - Summary statistics (total variance, budget vs actual)
  - AI-generated narrative explaining what happened
  - Interactive variance chart (over/under budget by category)
  - Detailed breakdown table
  - Biggest over/under budget items
- Save results and view memory confirmation

### 4. Patterns
- Explore all past projects at `/patterns`
- See aggregate statistics
- Compare trends across projects
- Learn from historical patterns

## 🎨 Extending

**Add authentication:**
- Add API key validation in `routes/api.py`
- Use Cloud Run IAM for access control
- Implement user sessions in `web/app.py`

**Add pattern detection improvements:**
- Migrate to Vertex AI Matching Engine
- Implement vector similarity search
- Build trend analysis dashboards

**Enhance web UI:**
- Add user accounts and project workspaces
- Enable report exports (PDF, Excel)
- Add real-time collaboration features
- Implement custom dashboard layouts

## 📄 License

MIT


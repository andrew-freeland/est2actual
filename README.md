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

### Running Locally

```bash
# Basic usage (quick summary without AI)
python main.py estimate.xlsx actual.xlsx --quick

# With AI insight generation
python main.py estimate.xlsx actual.xlsx --project-name "Q4 Marketing Campaign"

# Save to Firestore memory
python main.py estimate.xlsx actual.xlsx --project-name "Q4 Campaign" --save-memory
```

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

_(Coming soon - see PROJECT_LOG.md for roadmap)_

## 🔐 Required GCP Permissions

Your service account needs:
- `aiplatform.endpoints.predict` (Vertex AI)
- `datastore.entities.create/get/list` (Firestore)

## 📝 Project Log

See [PROJECT_LOG.md](PROJECT_LOG.md) for architecture decisions and feature history.

## 🛠️ Extending

**Add charting:**
- Create `report/generate_charts.py`
- Use matplotlib or plotly
- Export to images or HTML

**Add API:**
- Create `routes/api.py` with Flask endpoints
- Deploy to Cloud Run

**Add pattern detection:**
- Enhance `memory/store_project_summary.py`
- Implement vector similarity search
- Build trend analysis

## 📄 License

MIT


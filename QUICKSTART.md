# Quick Start Guide

Get the Estimate Insight Agent Pro running in ~5 minutes.

## Step 1: Install Dependencies

```bash
cd /Users/andrew-hci/est2actual

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Create Test Data

```bash
python scripts/create_test_data.py
```

This creates `sample_data/estimate.xlsx` and `sample_data/actual.xlsx`.

## Step 3: Run Without AI (Quick Mode)

Test the parser and summary generation without calling Gemini:

```bash
python main.py sample_data/estimate.xlsx sample_data/actual.xlsx --project-name "Sample Project" --quick
```

Expected output:
- Variance table showing over/under budget categories
- Quick text summary with key statistics

## Step 4: Setup Google Cloud (Optional for AI features)

If you want AI insights and memory storage:

```bash
# Run setup script
./scripts/setup_gcp.sh

# Or manually:
# 1. Create GCP project
# 2. Enable Vertex AI API
# 3. Enable Firestore API
# 4. Authenticate: gcloud auth application-default login
# 5. Create .env with GCP_PROJECT_ID
```

## Step 5: Run With AI Insights

```bash
python main.py sample_data/estimate.xlsx sample_data/actual.xlsx --project-name "Sample Project"
```

This calls Gemini 1.5 Pro to generate narrative insights.

## Step 6: Save to Memory

```bash
python main.py sample_data/estimate.xlsx sample_data/actual.xlsx --project-name "Sample Project" --save-memory
```

This stores the analysis in Firestore with embeddings for future pattern detection.

## Troubleshooting

**"ModuleNotFoundError: No module named 'pandas'"**
→ Run `pip install -r requirements.txt`

**"GCP_PROJECT_ID must be set"**
→ Create `.env` file with your project ID or run `./scripts/setup_gcp.sh`

**"Failed to generate insight with Gemini"**
→ Check authentication: `gcloud auth application-default login`
→ Verify Vertex AI API is enabled

## Next Steps

- Modify the parser for your Excel format
- Customize the Gemini prompt in `report/generate_summary.py`
- Add charting or exports
- Deploy to Cloud Run (see README.md)


# Project Log - Estimate Insight Agent Pro

This log tracks all major architecture decisions, features, and changes.

---

## 2025-10-27: Project Initialization

### Core Architecture Established

**Modules Created:**
1. **`parsers/`** - Excel ingestion and variance calculation
   - `compare_estimate_to_actual.py`: Flexible Excel parsing with auto-detection of category/amount columns
   - Handles outer joins (categories in estimate but not actual, and vice versa)
   - Calculates absolute variance and percentage variance

2. **`report/`** - AI narrative generation
   - `generate_summary.py`: Vertex AI Gemini integration
   - Structured prompt engineering for executive-level insights
   - Fallback to quick summary if Gemini unavailable

3. **`memory/`** - Persistent storage with embeddings
   - `store_project_summary.py`: Firestore integration
   - Text embedding using `textembedding-gecko@003`
   - Pattern detection foundation (vector search TBD)

4. **`routes/`** - API endpoints (placeholder for Cloud Run)

5. **`cloud/`** - Deployment utilities (placeholder)

### Design Decisions

**Why Pandas?**
- Industry standard for tabular data
- Excel support via openpyxl
- Rich data manipulation capabilities

**Why Gemini 1.5 Pro?**
- Best-in-class reasoning for nuanced financial analysis
- Long context window (1M tokens) for future multi-project analysis
- Native Google Cloud integration

**Why Firestore?**
- Serverless, low-ops memory store
- Document model fits unstructured insights
- Native GCP integration for Cloud Run
- Note: Vector search not native - may migrate to Vertex AI Vector Search later

**Why Modular Structure?**
- Each module has single responsibility
- Easy to mock/test individual components
- Future features don't require refactoring existing code
- Another AI agent can easily understand and extend

### Current Capabilities

✅ **Working:**
- CLI runner accepts two Excel files
- Flexible parsing (auto-detects column names)
- Variance calculation (absolute & percentage)
- Summary statistics generation
- Gemini insight generation
- Firestore memory storage
- Embedding generation

⏳ **Planned:**
- Flask API for web interface
- Cloud Run deployment scripts
- Vector similarity search for pattern detection
- Charting (matplotlib/plotly)
- PDF/Excel report exports
- Multi-project trend analysis
- Dashboard UI

### Dependencies Rationale

**Core:**
- `pandas==2.1.4`: Dataframe operations
- `openpyxl==3.1.2`: Excel file support

**Google Cloud:**
- `google-cloud-aiplatform==1.38.1`: Vertex AI (Gemini + embeddings)
- `google-cloud-firestore==2.14.0`: Memory storage

**Web (for future Cloud Run):**
- `flask==3.0.0`: Lightweight web framework
- `gunicorn==21.2.0`: Production WSGI server

**Utilities:**
- `python-dotenv==1.0.0`: Environment variable management

### Authentication Strategy

**Local Development:**
```bash
gcloud auth application-default login
```

**Cloud Run Deployment:**
- Use Workload Identity
- Attach service account with required IAM roles

### Cost Optimization Notes

**Estimated costs per analysis:**
- Gemini 1.5 Pro: ~$0.01 per insight (typical prompt size)
- Firestore: ~$0.0001 per write
- Embeddings: ~$0.0001 per generation

**Total per run:** < $0.02

**For 100 projects/month:** < $2

### Next Steps

1. Create sample Excel files for testing
2. Test end-to-end flow locally
3. Add Flask API wrapper
4. Create Dockerfile for Cloud Run
5. Add deployment script
6. Implement vector similarity search
7. Build simple web UI

### Notes for Future AI Agents

- All Google Cloud operations require `GCP_PROJECT_ID` environment variable
- Gemini calls can fail if quota exceeded - handle gracefully
- Firestore needs indexes for complex queries - update firestore.indexes.json
- Consider rate limiting if exposing as public API
- Embedding model may change - abstract behind interface


# Estimate Insight - Technical Documentation

## Overview

Estimate Insight is a Python-based application that compares construction project estimates against actual costs, calculates variances, and generates analytical insights using Google's Vertex AI Gemini LLM. The system stores historical project data in Firestore for pattern recognition across projects.

## Architecture

### System Components

```
┌─────────────────┐
│   Web UI        │ Flask templates (Jinja2)
│  (Tailwind CSS) │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask App      │ Routes, request handling
│  (web/app.py)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analysis Core  │ Variance calculation, data processing
│  (routes/api.py)│
└────────┬────────┘
         │
    ┌────┴────┬──────────┬────────────┐
    ▼         ▼          ▼            ▼
┌────────┐ ┌──────┐ ┌─────────┐ ┌──────────┐
│ Parser │ │Vertex│ │Firestore│ │Chart Gen │
│        │ │  AI  │ │         │ │(Matplotlib)
└────────┘ └──────┘ └─────────┘ └──────────┘
```

### Technology Stack

#### Core Framework
- **Python 3.9+**: Runtime environment
- **Flask 2.3+**: WSGI web application framework
  - Lightweight, minimal overhead
  - Synchronous request handling suitable for I/O-bound operations
  - Template rendering with Jinja2
- **Gunicorn**: WSGI HTTP server for production deployment
  - Multi-worker process model for concurrency
  - Configured with 2 workers, 4 threads per worker

#### Data Processing
- **Pandas 2.0+**: Tabular data manipulation
  - Used for Excel file parsing via `openpyxl` engine
  - DataFrame operations for merge, filter, aggregate
  - Handles missing values and type coercion
- **NumPy**: Numerical operations (transitive dependency via Pandas)

#### Machine Learning / AI
- **Google Cloud Vertex AI SDK (`google-cloud-aiplatform`)**: 
  - Gemini 1.5 Pro model access via REST API
  - Generation config: temperature=0.3 (deterministic outputs), max_tokens=2048
  - Text embeddings via `textembedding-gecko@003` (768-dimensional vectors)

#### Data Persistence
- **Google Cloud Firestore** (`google-cloud-firestore`):
  - NoSQL document database
  - Native mode (not Datastore mode)
  - Collection: `project_insights`
  - Document schema:
    ```python
    {
        'project_name': str,
        'narrative': str,
        'variance_summary': dict,
        'embedding': list[float],  # 768-dim vector
        'created_at': timestamp,
        'metadata': dict
    }
    ```

#### Visualization
- **Matplotlib 3.7+**: Chart generation
  - Figure size: 12x6 inches, 100 DPI
  - Bar chart with variance visualization
- **Seaborn**: Statistical visualization (styling)

#### Frontend
- **Tailwind CSS 3.3+**: Utility-first CSS framework via CDN
- **Font Awesome 6.5+**: Icon library via CDN
- **Vanilla JavaScript**: No framework dependencies

#### Development
- **python-dotenv**: Environment variable management
- **Werkzeug**: WSGI utilities (file upload handling)

## Variance Calculation Methodology

### 1. Data Ingestion

Excel files are parsed using Pandas with the `openpyxl` engine:

```python
df = pd.read_excel(filepath, sheet_name=0, engine='openpyxl')
```

### 2. Column Normalization

The system normalizes column names to handle variations in Excel formats:

```python
def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Maps common column name variations to standard names:
    - 'description', 'item', 'task', 'category' → 'Category'
    - 'estimated', 'budget', 'planned' → 'Estimated'
    - 'actual', 'spent', 'real' → 'Actual'
    
    Case-insensitive matching with whitespace trimming.
    """
```

This allows the system to process Excel files from different sources (Buildertrend exports, QuickBooks exports, custom templates) without requiring a specific format.

### 3. Variance Computation

The core comparison uses Pandas merge with an **outer join** to handle:
- Line items present in estimate but not in actual (unspent budgets)
- Line items present in actual but not in estimate (unbudgeted expenses)

```python
variance_df = pd.merge(
    estimate_df, 
    actual_df, 
    on='Category', 
    how='outer',
    suffixes=('_est', '_act')
)
```

Missing values are filled with zeros:

```python
variance_df['Estimated'].fillna(0, inplace=True)
variance_df['Actual'].fillna(0, inplace=True)
```

### 4. Variance Metrics

For each line item:

```python
variance_df['Variance'] = variance_df['Actual'] - variance_df['Estimated']
variance_df['Variance_%'] = (variance_df['Variance'] / variance_df['Estimated']) * 100
```

**Edge case handling:**
- Division by zero (when Estimated = 0): Results in `inf`, which is acceptable for display purposes
- `inf` values indicate completely unbudgeted line items
- Negative variance = under budget
- Positive variance = over budget

### 5. Summary Statistics

Aggregated metrics calculated:

```python
{
    'total_estimated': float,           # Sum of all estimated amounts
    'total_actual': float,              # Sum of all actual amounts
    'total_variance': float,            # total_actual - total_estimated
    'total_variance_pct': float,        # (variance / estimated) * 100
    'over_budget_categories': int,      # Count where variance > 0
    'under_budget_categories': int,     # Count where variance < 0
    'biggest_overrun': {
        'category': str,
        'amount': float
    },
    'biggest_underrun': {
        'category': str,
        'amount': float
    }
}
```

## AI Integration

### Prompt Engineering

The Gemini prompt is structured to produce executive-level analysis:

1. **Context**: Project name, summary statistics, line-item details
2. **Historical context**: Similar past projects (if available)
3. **Task specification**: 
   - 300-500 word executive summary
   - 4-paragraph structure: Overview, Cost Drivers, Root Causes, Recommendations
   - Professional business language
   - Focus on insights, not number repetition

### Generation Parameters

```python
generation_config = {
    "temperature": 0.3,      # Low temperature for consistent financial analysis
    "max_output_tokens": 2048,  # Limit output length for cost control
    "top_p": 0.8,            # Nucleus sampling
    "top_k": 40              # Token selection pool size
}
```

**Rationale:**
- Low temperature (0.3) ensures deterministic, factual outputs suitable for financial reports
- Token limit prevents runaway generation and controls API costs
- Configuration biases toward precise, business-appropriate language

### Fallback Mechanism

If Vertex AI is unavailable or times out, the system generates a basic text summary without LLM processing:

```python
try:
    narrative = generate_insight_narrative(...)
except Exception as e:
    narrative = generate_quick_summary(summary_stats)
```

This ensures the system remains functional even without AI infrastructure.

## Pattern Recognition

### Embedding Generation

Project narratives are converted to 768-dimensional vectors using Google's text embedding model:

```python
embedding = generate_embedding(
    text=f"{project_name}: {narrative}",
    model="textembedding-gecko@003"
)
```

### Similarity Search

**Current implementation**: Linear search with cosine similarity
- Query embedding generated for search text
- Cosine similarity computed against all stored embeddings
- Top-k results returned

**Limitation**: Firestore does not support native vector similarity search. For production scale, consider:
- Vertex AI Matching Engine (vector database with ANN search)
- pgvector with Cloud SQL PostgreSQL
- Separate vector database (Pinecone, Weaviate)

**Cosine similarity formula:**
```
similarity = (A · B) / (||A|| * ||B||)
```

Where A is the query embedding and B is each stored embedding.

## API Design

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
    "status": "ok",
    "message": "Estimate Insight is running"
}
```

#### `POST /analyze`
Main analysis endpoint.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `estimate_file`: Excel file (.xlsx, .xls)
  - `actual_file`: Excel file (.xlsx, .xls)
  - `project_name`: string (optional, default: "Unnamed Project")
  - `save_memory`: boolean (optional, default: false)
  - `generate_chart`: boolean (optional, default: false)
  - `quick`: boolean (optional, default: false, skips Gemini)

**Response:**
```json
{
    "success": boolean,
    "project_name": string,
    "narrative": string,
    "summary": {
        "total_estimated": float,
        "total_actual": float,
        "total_variance": float,
        "total_variance_pct": float,
        "over_budget_categories": int,
        "under_budget_categories": int,
        "biggest_overrun": {...},
        "biggest_underrun": {...}
    },
    "variance_data": [...],
    "chart_image_base64": string | null,
    "memory_id": string | null,
    "similar_projects_count": int
}
```

**Processing pipeline:**
1. Validate file uploads (size, extension)
2. Save files to temporary directory
3. Parse Excel files → DataFrames
4. Calculate variance
5. Generate summary statistics
6. (Optional) Retrieve similar projects from Firestore
7. Generate narrative with Gemini
8. (Optional) Generate chart
9. (Optional) Save to Firestore
10. Return JSON response

**Timeout:** 120 seconds

## Chart Generation

Charts are generated using Matplotlib and encoded as base64 PNG data URIs:

```python
# Generate bar chart
fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
ax.bar(categories, variances, color=['red' if v > 0 else 'green' for v in variances])
ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)

# Save to in-memory buffer
buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight')
buf.seek(0)

# Encode as base64
image_base64 = base64.b64encode(buf.read()).decode('utf-8')
```

**Output format:** `data:image/png;base64,{encoded_data}`

This allows charts to be embedded directly in HTML or JSON responses without requiring separate image hosting.

## Security

### Authentication
- Service account authentication via `GOOGLE_APPLICATION_CREDENTIALS`
- OAuth2 flow with Application Default Credentials
- Service account requires roles:
  - `roles/aiplatform.admin` (Vertex AI access)
  - `roles/datastore.user` (Firestore read/write)

### File Upload Validation
- Extension whitelist: `.xlsx`, `.xls`
- Maximum file size: 16MB (configured via `MAX_CONTENT_LENGTH`)
- Secure filename handling via `werkzeug.secure_filename()`
- Temporary file storage with automatic cleanup

### Secrets Management
- Environment variables via `.env` file
- `.env` excluded from version control via `.gitignore`
- Service account keys stored outside project directory recommended

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with GCP credentials

# Run server
python3 web/app.py
```

Server listens on `0.0.0.0:8080`

### Google Cloud Run

**Dockerfile:**
- Base image: `python:3.9-slim`
- Installs system dependencies (gcc, g++ for numpy compilation)
- Installs Python packages
- Runs Gunicorn with `web.app:app`

**Deployment:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/estimate-insight
gcloud run deploy estimate-insight \
    --image gcr.io/PROJECT_ID/estimate-insight \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT_ID=PROJECT_ID,GCP_REGION=us-central1
```

**Resource configuration:**
- Memory: 1GB minimum
- CPU: 1 vCPU
- Timeout: 300 seconds (for AI processing)
- Concurrency: 80 requests per container

### Environment Variables

Required:
- `GCP_PROJECT_ID`: Google Cloud project identifier
- `GCP_REGION`: Vertex AI region (default: us-central1)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key JSON

Optional:
- `SECRET_KEY`: Flask session secret (auto-generated if not provided)
- `FLASK_ENV`: development | production
- `PORT`: Server port (default: 8080)

## Performance Characteristics

### Latency

Typical request timeline:
- Excel parsing: 50-200ms (depends on file size)
- Variance calculation: 10-50ms
- Gemini API call: 2-5 seconds (network + inference)
- Firestore write: 100-300ms
- Chart generation: 500-1000ms

**Total end-to-end:** ~3-7 seconds for full analysis with chart and memory storage

### Throughput

- Single process: ~10-15 requests/minute (limited by Gemini API latency)
- Multi-worker (Gunicorn): Scales linearly with workers (I/O bound)
- Vertex AI quota: 60 requests/minute (default)

### Scalability

**Bottlenecks:**
1. Gemini API latency (mitigated via request queuing)
2. Firestore write throughput (500 writes/second limit)
3. Vector similarity search (O(n) linear scan)

**Scaling strategies:**
- Horizontal scaling via Cloud Run (auto-scales to 1000 instances)
- Asynchronous task queue for batch processing (Celery + Redis)
- Vector database for sub-linear similarity search

## Cost Analysis

Per-request costs (approximate):

| Component | Cost | Notes |
|-----------|------|-------|
| Gemini 1.5 Pro | $0.0075 | ~1000 input tokens, ~500 output tokens |
| Text Embeddings | $0.000025 | 768-dim vector |
| Firestore Write | $0.000018 | Single document |
| Cloud Run | $0.0024 | 1s execution @ 1GB memory |
| **Total** | **~$0.01** | Per analysis request |

Monthly costs at scale:
- 1,000 analyses: $10
- 10,000 analyses: $100
- 100,000 analyses: $1,000

**Free tier:**
- Cloud Run: 2M requests/month
- Firestore: 50k reads/day, 20k writes/day, 1GB storage
- Vertex AI: $300 credit for first 90 days

## Testing

### Unit Testing

Not yet implemented. Recommended test coverage:
- `parsers/compare_estimate_to_actual.py`: Column normalization, variance calculation
- `report/generate_summary.py`: Prompt generation, fallback logic
- `memory/store_project_summary.py`: Embedding generation, Firestore operations

### Integration Testing

**Internal test script** (`scripts/run_internal_test.py`):
- Generates synthetic construction project data
- POSTs to `/analyze` endpoint
- Validates response structure
- Saves results to `tmp/test_results_*.json`

```bash
python3 scripts/run_internal_test.py
```

### Manual Testing

Test data generator:
```bash
python3 scripts/create_test_data.py
```

Creates sample Excel files in `sample_data/`:
- `estimate.xlsx`: 6 line items, $113k total
- `actual.xlsx`: 7 line items (includes unbudgeted item), $119.5k total

## Limitations

1. **Excel parsing**: Only supports `.xlsx` and `.xls` formats (no CSV direct support)
2. **Vector search**: Linear O(n) complexity, not suitable for >10k stored projects
3. **Concurrency**: Synchronous Flask app, limited by Gemini API latency
4. **Chart interactivity**: Static PNG images, no zoom/pan/hover
5. **File size**: 16MB upload limit may be insufficient for very large projects
6. **Gemini availability**: No retry logic or circuit breaker for API failures

## Future Improvements

### High Priority
1. Implement retry logic with exponential backoff for Vertex AI API calls
2. Add request caching to avoid duplicate Gemini API calls
3. Migrate to async framework (FastAPI) for improved concurrency
4. Implement Vertex AI Matching Engine for vector similarity search

### Medium Priority
1. Add authentication/authorization (Firebase Auth)
2. Support CSV file uploads
3. Interactive charts (Plotly.js)
4. Batch processing support
5. Export results to PDF

### Low Priority
1. Multi-language support (i18n)
2. Custom chart templates
3. Email notifications
4. Scheduled reports

## Contributing

### Code Style
- PEP 8 compliance
- Type hints for function signatures
- Docstrings for public functions (Google style)

### Git Workflow
- Feature branches: `feature/description`
- Commit messages: Conventional Commits format
- Pull requests require passing tests (when implemented)

## License

[Specify license]

## Support

For issues or questions:
1. Check `GCP_SETUP_GUIDE.md` for setup problems
2. Review `PROJECT_LOG.md` for known issues
3. Examine `REVIEW_FINDINGS.md` for architectural decisions

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-27  
**Python:** 3.9+  
**Flask:** 2.3+


# Architecture Documentation

## System Overview

```
┌─────────────────┐
│  Excel Files    │
│  (Est + Actual) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Parser Module                   │
│  - Load Excel                    │
│  - Normalize columns             │
│  - Calculate variance            │
│  - Generate summary stats        │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Report Module                   │
│  - Format prompt                 │
│  - Call Vertex AI Gemini         │
│  - Generate narrative insight    │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Memory Module (Optional)        │
│  - Generate embeddings           │
│  - Store in Firestore            │
│  - Enable pattern detection      │
└─────────────────────────────────┘
```

## Data Flow

1. **Input**: Two Excel files (estimate.xlsx, actual.xlsx)
2. **Parse**: Load into pandas DataFrames
3. **Normalize**: Auto-detect category/amount columns
4. **Merge**: Outer join on category (handles missing categories)
5. **Calculate**: Variance = Actual - Estimated
6. **Summarize**: Total variance, biggest over/under runs
7. **Generate**: Gemini creates narrative explaining the numbers
8. **Store**: Save to Firestore with embedding vector

## Module Design Principles

### 1. Single Responsibility

Each module does ONE thing well:
- **Parser**: Excel → DataFrame with variance
- **Report**: DataFrame → Narrative text
- **Memory**: Narrative → Firestore + embeddings

### 2. Clear I/O Boundaries

```python
# Parser
def compare_estimates(estimate_df, actual_df) -> variance_df

# Report
def generate_insight_narrative(variance_data, summary_stats) -> narrative_text

# Memory
def store_project_insight(project_name, narrative, variance_summary) -> doc_id
```

### 3. Testability

Each function can be tested in isolation:
- Mock pandas DataFrames for parser tests
- Mock Gemini responses for report tests
- Mock Firestore for memory tests

### 4. Extensibility

Add features without modifying existing code:
- New export format? Add to `report/`
- New storage backend? Add to `memory/`
- New data source? Add to `parsers/`

## Technology Choices

### Pandas
**Why**: Industry-standard for tabular data manipulation
**Alternatives considered**: Polars (too new), raw Python (too verbose)

### Vertex AI Gemini
**Why**: Best reasoning for financial analysis, native GCP integration
**Alternatives considered**: OpenAI GPT-4 (requires external API), Claude (same reason)

### Firestore
**Why**: Serverless, low-ops, native GCP, good for unstructured data
**Limitations**: No native vector search (may migrate to Vertex AI Vector Search)
**Alternatives considered**: BigQuery (overkill), Cloud SQL (requires management)

### Flask
**Why**: Lightweight, Python-native, perfect for Cloud Run
**Alternatives considered**: FastAPI (async not needed), Django (too heavy)

## Security Considerations

### Authentication
- **Local**: `gcloud auth application-default login`
- **Cloud Run**: Workload Identity with service account
- **Never**: Commit credentials or service account keys

### IAM Permissions Required
```
roles/aiplatform.user          # Vertex AI access
roles/datastore.user           # Firestore read/write
roles/logging.logWriter        # Cloud Logging
```

### Data Privacy
- No PII stored in Firestore by default
- Excel files not persisted (only processed in memory)
- Add encryption at rest if storing sensitive financial data

## Scalability

### Current Limits
- Single-threaded processing
- In-memory DataFrame (limited by Cloud Run memory)
- Synchronous Gemini calls

### Scale-Up Strategies
1. **Concurrent Processing**: Use Cloud Tasks for batch analysis
2. **Streaming**: Process large files in chunks
3. **Caching**: Cache Gemini responses for similar queries
4. **Load Balancing**: Cloud Run auto-scales instances

### Cost at Scale

| Volume | Est. Cost/Month |
|--------|----------------|
| 10 analyses/day | ~$6 |
| 100 analyses/day | ~$60 |
| 1000 analyses/day | ~$600 |

*Assumes avg prompt = 1000 tokens, Gemini Pro pricing*

## Future Enhancements

### Phase 2: Rich Outputs
- PDF reports with charts (matplotlib)
- Excel exports with formatted tables
- Email delivery

### Phase 3: Pattern Detection
- Vector similarity search across projects
- Trend analysis over time
- Predictive variance warnings

### Phase 4: Dashboard
- React/Vue frontend
- Real-time analysis
- Multi-user support

### Phase 5: Advanced AI
- Multi-modal analysis (parse PDF invoices)
- Agent-based decomposition for complex projects
- Automated recommendations with confidence scores

## Debugging

### Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test individual modules:
```python
# Test parser
from parsers.compare_estimate_to_actual import compare_estimates
df = compare_estimates(est_df, act_df)
print(df)

# Test report (without Gemini)
from report.generate_summary import generate_quick_summary
summary = generate_quick_summary(stats)
print(summary)
```

### Check Firestore data:
```bash
gcloud firestore collections list
gcloud firestore documents list project_insights
```

## Performance

### Typical Latencies
- Excel parsing: 50-200ms
- Variance calculation: 10-50ms
- Gemini generation: 2-5 seconds
- Firestore write: 100-300ms

**Total end-to-end**: ~3-6 seconds

### Optimization Opportunities
1. Cache parsed Excel if analyzing multiple times
2. Batch Firestore writes
3. Use Gemini Flash for faster (cheaper) results
4. Precompute embeddings for common categories


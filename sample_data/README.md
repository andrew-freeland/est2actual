# Sample Data

This directory contains example Excel files for testing the system.

## Creating Test Files

You can create test Excel files with this structure:

**estimate.xlsx:**
| Category    | Amount  |
|-------------|---------|
| Labor       | 50000   |
| Materials   | 25000   |
| Marketing   | 15000   |
| Equipment   | 10000   |
| Travel      | 5000    |

**actual.xlsx:**
| Category    | Amount  |
|-------------|---------|
| Labor       | 55000   |
| Materials   | 22000   |
| Marketing   | 18000   |
| Equipment   | 10000   |
| Travel      | 4000    |

The system will automatically detect:
- Over-budget: Labor (+$5k), Marketing (+$3k)
- Under-budget: Materials (-$3k), Travel (-$1k)
- On-budget: Equipment ($0)

## Python Script to Generate Test Files

```python
import pandas as pd

# Estimate data
estimate = pd.DataFrame({
    'Category': ['Labor', 'Materials', 'Marketing', 'Equipment', 'Travel'],
    'Amount': [50000, 25000, 15000, 10000, 5000]
})

# Actual data
actual = pd.DataFrame({
    'Category': ['Labor', 'Materials', 'Marketing', 'Equipment', 'Travel'],
    'Amount': [55000, 22000, 18000, 10000, 4000]
})

estimate.to_excel('estimate.xlsx', index=False)
actual.to_excel('actual.xlsx', index=False)
print("Test files created!")
```

Run this in the sample_data directory to create test files.


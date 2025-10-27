#!/usr/bin/env python3
"""
Create sample Excel files for testing the Estimate Insight Agent Pro.
"""

import pandas as pd
from pathlib import Path

# Create sample_data directory if it doesn't exist
output_dir = Path(__file__).parent.parent / 'sample_data'
output_dir.mkdir(exist_ok=True)

# Estimate data
estimate = pd.DataFrame({
    'Category': ['Labor', 'Materials', 'Marketing', 'Equipment', 'Travel', 'Consulting'],
    'Amount': [50000, 25000, 15000, 10000, 5000, 8000]
})

# Actual data - with realistic variances
actual = pd.DataFrame({
    'Category': ['Labor', 'Materials', 'Marketing', 'Equipment', 'Travel', 'Consulting', 'Contingency'],
    'Amount': [55000, 22000, 18000, 10000, 4000, 8500, 2000]
})

# Save to Excel
estimate_path = output_dir / 'estimate.xlsx'
actual_path = output_dir / 'actual.xlsx'

estimate.to_excel(estimate_path, index=False)
actual.to_excel(actual_path, index=False)

print("✅ Test files created successfully!")
print(f"   📄 {estimate_path}")
print(f"   📄 {actual_path}")
print()
print("Run the analysis:")
print(f"   python main.py {estimate_path} {actual_path} --project-name 'Sample Project' --quick")


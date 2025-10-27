"""
Parser: Compare Estimate to Actual
Accepts two Excel files and produces a variance dataframe.
"""

import pandas as pd
from typing import Dict, Any


def load_excel(filepath: str, sheet_name: str = 0) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame.
    
    Args:
        filepath: Path to the Excel file
        sheet_name: Sheet name or index (default: 0)
    
    Returns:
        DataFrame with the Excel data
    """
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        return df
    except Exception as e:
        raise ValueError(f"Failed to load Excel file {filepath}: {str(e)}")


def compare_estimates(estimate_df: pd.DataFrame, actual_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare estimate and actual dataframes to calculate variance.
    
    Expected columns: 'Category' (or similar), 'Amount' (or 'Cost', 'Value')
    
    Args:
        estimate_df: DataFrame with estimated costs
        actual_df: DataFrame with actual costs
    
    Returns:
        DataFrame with columns: Category, Estimated, Actual, Variance, Variance_Pct
    """
    # Normalize column names (flexible for different formats)
    estimate_df = _normalize_columns(estimate_df)
    actual_df = _normalize_columns(actual_df)
    
    # Merge on category
    merged = pd.merge(
        estimate_df[['category', 'amount']],
        actual_df[['category', 'amount']],
        on='category',
        how='outer',
        suffixes=('_estimate', '_actual')
    )
    
    # Fill NaN values with 0
    merged['amount_estimate'] = merged['amount_estimate'].fillna(0)
    merged['amount_actual'] = merged['amount_actual'].fillna(0)
    
    # Calculate variance
    merged['variance'] = merged['amount_actual'] - merged['amount_estimate']
    merged['variance_pct'] = (
        (merged['variance'] / merged['amount_estimate']) * 100
    ).replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # Rename for clarity
    merged.rename(columns={
        'category': 'Category',
        'amount_estimate': 'Estimated',
        'amount_actual': 'Actual',
        'variance': 'Variance',
        'variance_pct': 'Variance_%'
    }, inplace=True)
    
    return merged


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to lowercase and identify category/amount columns.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with normalized 'category' and 'amount' columns
    """
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()
    
    # Find category column
    category_candidates = ['category', 'name', 'item', 'description', 'line_item']
    category_col = None
    for candidate in category_candidates:
        if candidate in df.columns:
            category_col = candidate
            break
    
    if category_col is None:
        # Use first column as category
        category_col = df.columns[0]
    
    # Find amount column
    amount_candidates = ['amount', 'cost', 'value', 'price', 'total']
    amount_col = None
    for candidate in amount_candidates:
        if candidate in df.columns:
            amount_col = candidate
            break
    
    if amount_col is None:
        # Use first numeric column
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            amount_col = numeric_cols[0]
        else:
            raise ValueError("Could not find numeric amount column")
    
    # Create normalized dataframe
    normalized = pd.DataFrame({
        'category': df[category_col].astype(str),
        'amount': pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
    })
    
    return normalized


def generate_summary_stats(variance_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics from the variance dataframe.
    
    Args:
        variance_df: DataFrame with variance calculations
    
    Returns:
        Dictionary with summary statistics
    """
    total_estimated = variance_df['Estimated'].sum()
    total_actual = variance_df['Actual'].sum()
    total_variance = variance_df['Variance'].sum()
    
    over_budget = variance_df[variance_df['Variance'] > 0]
    under_budget = variance_df[variance_df['Variance'] < 0]
    
    return {
        'total_estimated': float(total_estimated),
        'total_actual': float(total_actual),
        'total_variance': float(total_variance),
        'total_variance_pct': float((total_variance / total_estimated * 100) if total_estimated > 0 else 0),
        'over_budget_categories': len(over_budget),
        'under_budget_categories': len(under_budget),
        'biggest_overrun': {
            'category': over_budget.loc[over_budget['Variance'].idxmax(), 'Category'] if len(over_budget) > 0 else None,
            'amount': float(over_budget['Variance'].max()) if len(over_budget) > 0 else 0
        },
        'biggest_underrun': {
            'category': under_budget.loc[under_budget['Variance'].idxmin(), 'Category'] if len(under_budget) > 0 else None,
            'amount': float(under_budget['Variance'].min()) if len(under_budget) > 0 else 0
        }
    }


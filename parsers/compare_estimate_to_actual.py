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


def compare_estimates(estimate_df: pd.DataFrame, actual_df: pd.DataFrame) -> tuple:
    """
    Compare estimate and actual dataframes to calculate variance.
    
    Expected columns: 'Category' (or similar), 'Amount' (or 'Cost', 'Value')
    
    Args:
        estimate_df: DataFrame with estimated costs
        actual_df: DataFrame with actual costs
    
    Returns:
        Tuple of (variance_df, category_mapping_dict)
        - variance_df: DataFrame with columns: Category, Estimated, Actual, Variance, Variance_Pct
        - category_mapping_dict: Details about how categories were matched/bundled
    """
    # Normalize column names (flexible for different formats)
    estimate_norm = _normalize_columns(estimate_df)
    actual_norm = _normalize_columns(actual_df)
    
    # Track categories before merge for mapping info
    estimate_categories = set(estimate_norm['category'].tolist())
    actual_categories = set(actual_norm['category'].tolist())
    
    # Merge on category
    merged = pd.merge(
        estimate_norm[['category', 'amount']],
        actual_norm[['category', 'amount']],
        on='category',
        how='outer',
        suffixes=('_estimate', '_actual')
    )
    
    # Build category mapping info before filling NaNs
    matched_categories = []
    estimate_only = []
    actual_only = []
    
    for _, row in merged.iterrows():
        category = row['category']
        has_estimate = pd.notna(row['amount_estimate']) and row['amount_estimate'] != 0
        has_actual = pd.notna(row['amount_actual']) and row['amount_actual'] != 0
        
        if has_estimate and has_actual:
            matched_categories.append({
                'category': category,
                'estimated': float(row['amount_estimate']),
                'actual': float(row['amount_actual'])
            })
        elif has_estimate and not has_actual:
            estimate_only.append({
                'category': category,
                'estimated': float(row['amount_estimate'])
            })
        elif has_actual and not has_estimate:
            actual_only.append({
                'category': category,
                'actual': float(row['amount_actual'])
            })
    
    category_mapping = {
        'matched_categories': matched_categories,
        'estimate_only_categories': estimate_only,
        'actual_only_categories': actual_only,
        'match_summary': {
            'total_matched': len(matched_categories),
            'total_estimate_only': len(estimate_only),
            'total_actual_only': len(actual_only),
            'match_rate_pct': (len(matched_categories) / max(len(estimate_categories), 1)) * 100
        }
    }
    
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
    
    return merged, category_mapping


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


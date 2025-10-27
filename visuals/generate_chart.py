"""
Chart Generation Module

Generates visualizations for variance analysis.
Currently supports: bar chart of variance by category.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional
import tempfile


def generate_variance_bar_chart(
    df: pd.DataFrame, 
    project_name: str,
    output_path: Optional[str] = None
) -> str:
    """
    Generate a bar chart showing variance by category.
    
    Args:
        df: DataFrame with columns: Category, Estimated, Actual, Variance, Variance_%
        project_name: Name of the project (used in chart title)
        output_path: Optional path to save PNG. If None, saves to temp file.
    
    Returns:
        Path to the saved PNG file
    
    Example:
        >>> variance_df = compare_estimates(est_df, act_df)
        >>> chart_path = generate_variance_bar_chart(variance_df, "Q4 Budget")
        >>> print(f"Chart saved to: {chart_path}")
    """
    # Validate required columns
    required_cols = ['Category', 'Variance']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"DataFrame missing required columns: {missing_cols}")
    
    # Set style
    sns.set_style("whitegrid")
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sort by variance for better visualization
    df_sorted = df.sort_values('Variance', ascending=True)
    
    # Define colors: red for over budget, green for under budget
    colors = ['#d32f2f' if x > 0 else '#388e3c' for x in df_sorted['Variance']]
    
    # Create horizontal bar chart
    bars = ax.barh(df_sorted['Category'], df_sorted['Variance'], color=colors, alpha=0.8)
    
    # Customize chart
    ax.set_xlabel('Variance ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Category', fontsize=12, fontweight='bold')
    ax.set_title(f'Budget Variance by Category\n{project_name}', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add a vertical line at x=0
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # Format x-axis with dollar signs and commas
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, df_sorted['Variance'])):
        label_x = value + (abs(df_sorted['Variance'].max()) * 0.02)
        ha = 'left' if value > 0 else 'right'
        if value < 0:
            label_x = value - (abs(df_sorted['Variance'].max()) * 0.02)
        
        ax.text(label_x, bar.get_y() + bar.get_height()/2, 
                f'${value:,.0f}',
                ha=ha, va='center', fontsize=9, fontweight='bold')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#d32f2f', alpha=0.8, label='Over Budget'),
        Patch(facecolor='#388e3c', alpha=0.8, label='Under Budget')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Determine output path
    if output_path is None:
        # Create temp file that won't be auto-deleted
        temp_dir = tempfile.gettempdir()
        output_path = str(Path(temp_dir) / f"variance_chart_{project_name.replace(' ', '_')}.png")
    
    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)  # Close to free memory
    
    return output_path


def chart_to_base64(chart_path: str) -> str:
    """
    Convert a PNG chart to base64 string for API responses.
    
    Args:
        chart_path: Path to the PNG file
    
    Returns:
        Base64 encoded string of the image
    """
    import base64
    
    with open(chart_path, 'rb') as img_file:
        img_data = img_file.read()
        base64_str = base64.b64encode(img_data).decode('utf-8')
    
    return base64_str


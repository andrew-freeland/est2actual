#!/usr/bin/env python3
"""
Estimate Insight Agent Pro - Main Runner

Usage:
    python main.py <estimate.xlsx> <actual.xlsx> [--project-name "Project Name"] [--save-memory]
"""

import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from parsers.compare_estimate_to_actual import (
    load_excel,
    compare_estimates,
    generate_summary_stats
)
from report.generate_summary import (
    initialize_vertex_ai,
    generate_insight_narrative,
    generate_quick_summary
)
from memory.store_project_summary import store_project_insight


def main():
    parser = argparse.ArgumentParser(
        description='Analyze estimate vs actual costs and generate AI insights'
    )
    parser.add_argument('estimate_file', help='Path to estimate Excel file')
    parser.add_argument('actual_file', help='Path to actual Excel file')
    parser.add_argument('--project-name', default='Unnamed Project', 
                       help='Name of the project being analyzed')
    parser.add_argument('--save-memory', action='store_true',
                       help='Save insight to Firestore memory')
    parser.add_argument('--quick', action='store_true',
                       help='Generate quick summary without calling Gemini')
    
    args = parser.parse_args()
    
    # Validate files exist
    if not os.path.exists(args.estimate_file):
        print(f"Error: Estimate file not found: {args.estimate_file}")
        sys.exit(1)
    
    if not os.path.exists(args.actual_file):
        print(f"Error: Actual file not found: {args.actual_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("ESTIMATE INSIGHT AGENT PRO")
    print("=" * 80)
    print()
    
    # Step 1: Load Excel files
    print(f"📊 Loading estimate file: {args.estimate_file}")
    estimate_df = load_excel(args.estimate_file)
    print(f"   ✓ Loaded {len(estimate_df)} rows")
    
    print(f"📊 Loading actual file: {args.actual_file}")
    actual_df = load_excel(args.actual_file)
    print(f"   ✓ Loaded {len(actual_df)} rows")
    print()
    
    # Step 2: Compare and calculate variance
    print("🔍 Comparing estimates to actuals...")
    variance_df = compare_estimates(estimate_df, actual_df)
    print(f"   ✓ Analyzed {len(variance_df)} categories")
    print()
    
    # Step 3: Generate summary statistics
    print("📈 Generating summary statistics...")
    summary_stats = generate_summary_stats(variance_df)
    print(f"   ✓ Total Variance: ${summary_stats['total_variance']:,.2f} "
          f"({summary_stats['total_variance_pct']:.1f}%)")
    print()
    
    # Display variance table
    print("VARIANCE ANALYSIS")
    print("-" * 80)
    print(variance_df.to_string(index=False))
    print()
    print("-" * 80)
    print()
    
    # Step 4: Generate narrative insight
    if args.quick:
        print("📝 Generating quick summary...")
        narrative = generate_quick_summary(summary_stats)
    else:
        print("🤖 Generating AI insight with Gemini 1.5 Pro...")
        try:
            initialize_vertex_ai()
            variance_data_str = variance_df.to_string(index=False)
            narrative = generate_insight_narrative(
                variance_data_str,
                summary_stats,
                args.project_name
            )
            print("   ✓ Insight generated")
        except Exception as e:
            print(f"   ⚠️  Failed to generate AI insight: {str(e)}")
            print("   Falling back to quick summary...")
            narrative = generate_quick_summary(summary_stats)
    
    print()
    print("AI INSIGHT")
    print("=" * 80)
    print(narrative)
    print("=" * 80)
    print()
    
    # Step 5: Save to memory (optional)
    if args.save_memory:
        print("💾 Saving to Firestore memory...")
        try:
            doc_id = store_project_insight(
                project_name=args.project_name,
                narrative=narrative,
                variance_summary=summary_stats,
                metadata={
                    'estimate_file': args.estimate_file,
                    'actual_file': args.actual_file
                }
            )
            print(f"   ✓ Saved with ID: {doc_id}")
        except Exception as e:
            print(f"   ⚠️  Failed to save to memory: {str(e)}")
    
    print()
    print("✅ Analysis complete!")


if __name__ == '__main__':
    main()


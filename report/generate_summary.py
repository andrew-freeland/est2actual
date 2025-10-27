"""
Report Generator: Generate narrative insights using Vertex AI Gemini.
"""

import os
from typing import Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel


def initialize_vertex_ai(project_id: str = None, location: str = "us-central1"):
    """
    Initialize Vertex AI with project credentials.
    
    Args:
        project_id: GCP project ID (defaults to env var GCP_PROJECT_ID)
        location: GCP region (defaults to us-central1)
    """
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID must be set in environment or passed as argument")
    
    vertexai.init(project=project_id, location=location)


def generate_insight_narrative(variance_data: str, summary_stats: Dict[str, Any], 
                               project_name: str = "Unnamed Project",
                               prior_summaries: list = None) -> str:
    """
    Generate a narrative insight using Gemini based on variance analysis.
    
    Args:
        variance_data: String representation of the variance dataframe
        summary_stats: Dictionary of summary statistics
        project_name: Name of the project being analyzed
        prior_summaries: List of similar past project summaries for pattern detection
    
    Returns:
        String containing the narrative insight
    """
    prompt = _build_prompt(variance_data, summary_stats, project_name, prior_summaries or [])
    
    try:
        model = GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,         # Lower for consistent financial analysis
                "max_output_tokens": 2048,  # Cost control
                "top_p": 0.8,
                "top_k": 40,
            }
        )
        return response.text
    except Exception as e:
        raise RuntimeError(f"Failed to generate insight with Gemini: {str(e)}")


def _build_prompt(variance_data: str, summary_stats: Dict[str, Any], 
                  project_name: str, prior_summaries: list = None) -> str:
    """
    Build the prompt for Gemini based on variance data and statistics.
    
    Args:
        variance_data: String representation of variance data
        summary_stats: Dictionary of summary statistics
        project_name: Name of the project
        prior_summaries: List of similar past project insights
    
    Returns:
        Formatted prompt string
    """
    # Build historical context if available
    historical_context = ""
    if prior_summaries and len(prior_summaries) > 0:
        historical_context = "\n**Historical Context - Similar Past Projects**:\n"
        for i, past_project in enumerate(prior_summaries[:3], 1):  # Limit to 3 for token efficiency
            proj_name = past_project.get('project_name', 'Unknown')
            variance_pct = past_project.get('variance_summary', {}).get('total_variance_pct', 0)
            historical_context += f"\n{i}. **{proj_name}**: {variance_pct:+.1f}% variance\n"
            
            # Include snippet of past narrative
            past_narrative = past_project.get('narrative', '')
            if past_narrative:
                snippet = past_narrative[:300] + "..." if len(past_narrative) > 300 else past_narrative
                historical_context += f"   Insight: {snippet}\n"
        
        historical_context += "\n**Pattern Detection**: Look for recurring themes across these projects.\n"
    
    prompt = f"""You are a financial analyst reviewing a project budget variance report.

**Project**: {project_name}

**Summary Statistics**:
- Total Estimated: ${summary_stats['total_estimated']:,.2f}
- Total Actual: ${summary_stats['total_actual']:,.2f}
- Total Variance: ${summary_stats['total_variance']:,.2f} ({summary_stats['total_variance_pct']:.1f}%)
- Categories Over Budget: {summary_stats['over_budget_categories']}
- Categories Under Budget: {summary_stats['under_budget_categories']}

**Biggest Overrun**: {summary_stats['biggest_overrun']['category']} (${summary_stats['biggest_overrun']['amount']:,.2f})
**Biggest Underrun**: {summary_stats['biggest_underrun']['category']} (${summary_stats['biggest_underrun']['amount']:,.2f})

**Detailed Variance Data**:
{variance_data}
{historical_context}
---

Please provide a professional, concise narrative insight (3-5 paragraphs) that:

1. **Summarizes** the overall budget performance (over/under budget and by how much)
2. **Identifies** the key cost drivers - which categories had the biggest impact?
3. **Explains** potential reasons for the variances (be specific to the category names)
4. **Detects Patterns** - if historical data is provided, identify any recurring issues or trends
5. **Recommends** 2-3 actionable steps for future projects based on this data and any patterns observed

Write in a clear, executive-friendly style. Focus on insights, not just restating numbers.
"""
    return prompt


def generate_quick_summary(summary_stats: Dict[str, Any]) -> str:
    """
    Generate a quick text summary without calling Gemini (for testing/fallback).
    
    Args:
        summary_stats: Dictionary of summary statistics
    
    Returns:
        Simple text summary
    """
    if summary_stats['total_variance'] > 0:
        status = "OVER BUDGET"
    elif summary_stats['total_variance'] < 0:
        status = "UNDER BUDGET"
    else:
        status = "ON BUDGET"
    
    summary = f"""
Project Budget Analysis
========================

Status: {status}

Total Estimated: ${summary_stats['total_estimated']:,.2f}
Total Actual: ${summary_stats['total_actual']:,.2f}
Variance: ${summary_stats['total_variance']:,.2f} ({summary_stats['total_variance_pct']:.1f}%)

Over Budget Categories: {summary_stats['over_budget_categories']}
Under Budget Categories: {summary_stats['under_budget_categories']}

Biggest Overrun: {summary_stats['biggest_overrun']['category']} (${summary_stats['biggest_overrun']['amount']:,.2f})
Biggest Underrun: {summary_stats['biggest_underrun']['category']} (${summary_stats['biggest_underrun']['amount']:,.2f})
"""
    return summary.strip()


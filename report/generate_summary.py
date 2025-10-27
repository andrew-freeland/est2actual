"""
Report Generator: Generate narrative insights using Vertex AI Gemini.
"""

import os
from typing import Dict, Any
import vertexai

# Try different import paths for different SDK versions
try:
    from vertexai.generative_models import GenerativeModel
except ImportError:
    try:
        from vertexai.preview.generative_models import GenerativeModel
    except ImportError:
        # Fallback for older versions
        GenerativeModel = None


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
    if GenerativeModel is None:
        raise RuntimeError(
            "Vertex AI Generative Models not available. "
            "This may be due to SDK version mismatch. "
            "Consider upgrading: pip install --upgrade google-cloud-aiplatform"
        )
    
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
    
    prompt = f"""You are writing a clear, easy-to-understand budget analysis report for a construction project. Your audience includes project managers and stakeholders who may not have deep financial expertise, so use plain English and avoid jargon.

**PROJECT**: {project_name}

**BUDGET SUMMARY**:
- Planned Budget: ${summary_stats['total_estimated']:,.2f}
- Actual Spending: ${summary_stats['total_actual']:,.2f}
- Difference: ${summary_stats['total_variance']:,.2f} ({summary_stats['total_variance_pct']:.1f}% {'over' if summary_stats['total_variance'] > 0 else 'under'} budget)
- Items Over Budget: {summary_stats['over_budget_categories']}
- Items Under Budget: {summary_stats['under_budget_categories']}

**BIGGEST CHANGES**:
- Largest Overrun: {summary_stats['biggest_overrun']['category']} (${summary_stats['biggest_overrun']['amount']:,.2f} more than planned)
- Largest Savings: {summary_stats['biggest_underrun']['category']} (${abs(summary_stats['biggest_underrun']['amount']):,.2f} less than planned)

**ALL LINE ITEMS**:
{variance_data}
{historical_context}
---

**YOUR TASK**: Write a clear 300-400 word summary that explains the budget results to non-financial readers. Use 4 paragraphs with plain English:

**Paragraph 1 - What Happened:**
Start with a simple, direct statement about whether the project was over or under budget and by how much. Explain what this means in practical terms - did the project cost more or less than expected?

**Paragraph 2 - Why It Happened:**
Explain the 2-3 biggest reasons for the budget difference. Use everyday language. Instead of "variance," say "went over" or "came in under." Instead of "cost drivers," say "the main reasons costs were higher/lower." Be specific about which items and how much.

**Paragraph 3 - What This Tells Us:**
{("Looking at past similar projects, what patterns do you notice? " if prior_summaries else "")}What can we learn from this? Are there specific types of costs that are consistently hard to estimate? Were there unexpected challenges? Use simple explanations like "The team may have underestimated how long X would take" or "Prices for Y were higher than expected."

**Paragraph 4 - What To Do Next Time:**
Give 3-4 specific, practical suggestions for future projects. Write these as clear actions, like "Allow an extra 10% buffer for Foundation Work" or "Get more detailed quotes from subcontractors before setting the budget." Make these recommendations feel actionable and realistic.

**WRITING STYLE**:
- Use conversational, professional language (as if explaining to a colleague)
- Write complete paragraphs, not bullet points
- Avoid financial jargon - say "went over budget" not "adverse variance"
- Use specific dollar amounts to make it concrete
- Keep sentences short and clear
- Avoid passive voice - say "costs increased" not "an increase was experienced"

Write your analysis now:
"""
    return prompt


def generate_quick_summary(summary_stats: Dict[str, Any], category_mapping: Dict[str, Any] = None) -> str:
    """
    Generate a clear, readable summary without calling Gemini (for testing/fallback).
    
    Args:
        summary_stats: Dictionary of summary statistics
    
    Returns:
        Formatted text summary in plain English
    """
    total_est = summary_stats['total_estimated']
    total_act = summary_stats['total_actual']
    variance = summary_stats['total_variance']
    variance_pct = summary_stats['total_variance_pct']
    
    # Determine status
    if variance > 0:
        status = "over budget"
        status_emoji = "⚠️"
    elif variance < 0:
        status = "under budget"
        status_emoji = "✅"
    else:
        status = "on budget"
        status_emoji = "✅"
    
    # Build category matching section
    category_matching_text = ""
    if category_mapping:
        match_summary = category_mapping.get('match_summary', {})
        matched = match_summary.get('total_matched', 0)
        estimate_only = match_summary.get('total_estimate_only', 0)
        actual_only = match_summary.get('total_actual_only', 0)
        match_rate = match_summary.get('match_rate_pct', 0)
        
        category_matching_text = f"""
Category Matching (Estimate Report vs Actual Report):
• {matched} categories found in BOTH reports (matched exactly)
• {estimate_only} categories only in Estimate report (no actual spending recorded)
• {actual_only} categories only in Actual report (unbudgeted/unexpected costs)
• Match Rate: {match_rate:.0f}%
"""
        
        # Add unmatched categories details if they exist
        if estimate_only > 0:
            estimate_only_cats = category_mapping.get('estimate_only_categories', [])
            if estimate_only_cats:
                category_matching_text += f"\nBudgeted but Not Spent: {', '.join([c['category'] for c in estimate_only_cats[:3]])}"
                if len(estimate_only_cats) > 3:
                    category_matching_text += f" (+{len(estimate_only_cats) - 3} more)"
        
        if actual_only > 0:
            actual_only_cats = category_mapping.get('actual_only_categories', [])
            if actual_only_cats:
                category_matching_text += f"\nUnbudgeted Spending: {', '.join([c['category'] for c in actual_only_cats[:3]])}"
                if len(actual_only_cats) > 3:
                    category_matching_text += f" (+{len(actual_only_cats) - 3} more)"
    
    # Build readable summary
    summary = f"""PROJECT BUDGET SUMMARY

Overall Performance: This project came in {status_emoji} {status} by ${abs(variance):,.2f} ({abs(variance_pct):.1f}%).

Budget Overview:
• Original Budget: ${total_est:,.2f}
• Actual Spending: ${total_act:,.2f}
• Difference: ${variance:+,.2f}
{category_matching_text}
Category Breakdown:
• {summary_stats['over_budget_categories']} categories exceeded their budgets
• {summary_stats['under_budget_categories']} categories came in under budget

Key Findings:
• Largest Cost Overrun: {summary_stats['biggest_overrun']['category']} was ${abs(summary_stats['biggest_overrun']['amount']):,.2f} over budget
• Largest Cost Savings: {summary_stats['biggest_underrun']['category']} saved ${abs(summary_stats['biggest_underrun']['amount']):,.2f}

{'This project exceeded the planned budget. Review the cost overruns to identify areas for better estimation in future projects.' if variance > 0 else 'This project came in under budget, which is positive. The cost savings may indicate effective management or conservative initial estimates.'}
"""
    return summary.strip()


#!/usr/bin/env python3
"""
PDF Export Module for Estimate Insight

Generates comprehensive multi-page PDF reports for project post-mortem analyses.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List


def generate_project_pdf(project_data: Dict[str, Any]) -> BytesIO:
    """
    Generate a comprehensive multi-page PDF report for project post-mortem analysis.
    
    Args:
        project_data: Dictionary containing project information
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontSize=11,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#e5e7eb'),
        leftIndent=4,
        rightIndent=4
    )
    
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4,
        leading=11
    )
    
    body_bold_style = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    # Extract data
    project_name = project_data.get('project_name', 'Unnamed Project')
    narrative = project_data.get('narrative', '')
    summary = project_data.get('summary') or project_data.get('variance_summary', {})
    created_at = project_data.get('created_at')
    category_mapping = project_data.get('category_mapping', {})
    metadata = project_data.get('metadata', {})
    
    # Date handling
    if created_at:
        if hasattr(created_at, 'strftime'):
            report_date = created_at.strftime('%B %d, %Y')
            reporting_period = created_at.strftime('%B %Y')
        else:
            report_date = str(created_at)
            reporting_period = str(created_at)
    else:
        report_date = datetime.now().strftime('%B %d, %Y')
        reporting_period = datetime.now().strftime('%B %Y')
    
    # ===== HEADER =====
    elements.append(Paragraph(
        "AI-GENERATED ESTIMATE INSIGHT REPORT: PROJECT POST-MORTEM",
        title_style
    ))
    elements.append(Spacer(1, 0.1*inch))
    
    # Project info table
    project_info = [
        ['Project Name:', project_name],
        ['Reporting Period:', reporting_period],
        ['Report Generated On:', report_date]
    ]
    
    info_table = Table(project_info, colWidths=[1.5*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # ===== 1. PROJECT BUDGET SUMMARY =====
    elements.append(Paragraph(
        "1. PROJECT BUDGET SUMMARY: OVERALL PERFORMANCE",
        section_heading_style
    ))
    
    if summary:
        total_estimated = summary.get('total_estimated', 0)
        total_actual = summary.get('total_actual', 0)
        total_variance = summary.get('total_variance', 0)
        variance_pct = summary.get('total_variance_pct', 0)
        
        status = "over budget" if total_variance > 0 else "under budget" if total_variance < 0 else "on budget"
        
        elements.append(Paragraph(
            f"<b>Overall Performance:</b> This project came in {status} by ${abs(total_variance):,.2f} ({abs(variance_pct):.1f}%)",
            body_style
        ))
        elements.append(Spacer(1, 0.05*inch))
        
        # Budget overview table
        budget_data = [
            ['<b>Budget Overview</b>', '<b>Amount</b>'],
            ['Original Budget', f'${total_estimated:,.2f}'],
            ['Actual Spending', f'${total_actual:,.2f}'],
            ['Difference', f'${total_variance:+,.2f}']
        ]
        
        budget_table = Table(budget_data, colWidths=[3*inch, 2*inch])
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1d5db')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9ca3af')),
        ]))
        
        elements.append(budget_table)
    
    elements.append(Spacer(1, 0.15*inch))
    
    # ===== 2. CATEGORY & METRIC BREAKDOWN =====
    elements.append(Paragraph(
        "2. CATEGORY & METRIC BREAKDOWN: VARIANCE ANALYSIS",
        section_heading_style
    ))
    
    # Category matching
    if category_mapping:
        match_summary = category_mapping.get('match_summary', {})
        matched = match_summary.get('total_matched', 0)
        estimate_only = match_summary.get('total_estimate_only', 0)
        actual_only = match_summary.get('total_actual_only', 0)
        match_rate = match_summary.get('match_rate_pct', 0)
        
        elements.append(Paragraph("<b>Category Matching (Estimate Report vs Actual Report):</b>", body_bold_style))
        elements.append(Paragraph(f"• {matched} categories found in BOTH reports (matched exactly)", body_style))
        elements.append(Paragraph(f"• {estimate_only} categories only in Estimate report (no actual spending recorded)", body_style))
        
        actual_only_cats = category_mapping.get('actual_only_categories', [])
        if actual_only_cats:
            cat_names = ', '.join([c['category'] for c in actual_only_cats[:3]])
            if len(actual_only_cats) > 3:
                cat_names += f' (+{len(actual_only_cats) - 3} more)'
            elements.append(Paragraph(f"• {actual_only} categories only in Actual report (unbudgeted/unexpected costs: {cat_names})", body_style))
        else:
            elements.append(Paragraph(f"• {actual_only} categories only in Actual report (unbudgeted/unexpected costs)", body_style))
        
        elements.append(Paragraph(f"• Match Rate: {match_rate:.0f}%", body_style))
        elements.append(Spacer(1, 0.05*inch))
    
    # Cost breakdown table (from summary stats)
    if summary:
        over_budget = summary.get('over_budget_categories', 0)
        under_budget = summary.get('under_budget_categories', 0)
        
        elements.append(Paragraph("<b>Category Breakdown:</b>", body_bold_style))
        elements.append(Paragraph(f"• {over_budget} categories exceeded their budgets", body_style))
        elements.append(Paragraph(f"• {under_budget} categories came in under budget", body_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # ===== 3. ROOT CAUSE ANALYSIS =====
    elements.append(Paragraph(
        "3. ROOT CAUSE ANALYSIS & IMPACT ON PROFITABILITY",
        section_heading_style
    ))
    
    if summary:
        biggest_overrun = summary.get('biggest_overrun', {})
        biggest_underrun = summary.get('biggest_underrun', {})
        
        elements.append(Paragraph("<b>Major Variance Drivers:</b>", body_bold_style))
        elements.append(Spacer(1, 0.05*inch))
        
        if biggest_overrun.get('amount', 0) != 0:
            overrun_cat = biggest_overrun.get('category', 'Unknown')
            overrun_amt = biggest_overrun.get('amount', 0)
            elements.append(Paragraph(
                f"<b>Largest Cost Overrun:</b> {overrun_cat} was ${abs(overrun_amt):,.2f} over budget",
                body_style
            ))
            elements.append(Paragraph(
                f"<b>Root Cause:</b> This category exceeded estimates, likely due to unforeseen complexities, "
                f"scope changes, or material/labor cost increases. Recommend detailed review of this category "
                f"for future project estimates.",
                body_style
            ))
            elements.append(Spacer(1, 0.05*inch))
        
        if biggest_underrun.get('amount', 0) != 0:
            underrun_cat = biggest_underrun.get('category', 'Unknown')
            underrun_amt = biggest_underrun.get('amount', 0)
            elements.append(Paragraph(
                f"<b>Largest Cost Savings:</b> {underrun_cat} saved ${abs(underrun_amt):,.2f}",
                body_style
            ))
            elements.append(Paragraph(
                f"<b>Reason:</b> This category came in under budget, possibly due to efficient resource management, "
                f"favorable market conditions, or conservative initial estimates. Consider replicating these practices.",
                body_style
            ))
            elements.append(Spacer(1, 0.05*inch))
        
        # Unbudgeted spending impacts
        if actual_only > 0:
            elements.append(Paragraph(
                f"<b>Unbudgeted Spending Impacts:</b> {actual_only} unexpected cost categories added "
                f"${abs(total_variance):,.2f} to the project. These unbudgeted items represent scope creep or "
                f"inadequate initial planning and should be addressed in the estimation process.",
                body_style
            ))
            elements.append(Spacer(1, 0.05*inch))
        
        # Overall profitability impact
        elements.append(Paragraph("<b>Overall Profitability Impact:</b>", body_bold_style))
        if total_variance > 0:
            elements.append(Paragraph(
                f"The total cost overrun of ${total_variance:,.2f} ({variance_pct:.1f}%) directly reduced the "
                f"net profit margin. The primary drivers were {overrun_cat if biggest_overrun.get('amount') else 'various categories'}. "
                f"Future projects should focus on tighter cost controls in high-variance categories.",
                body_style
            ))
        else:
            elements.append(Paragraph(
                f"The project came in ${abs(total_variance):,.2f} ({abs(variance_pct):.1f}%) under budget, "
                f"improving profitability. This was primarily driven by {underrun_cat if biggest_underrun.get('amount') else 'various categories'}. "
                f"These cost-saving practices should be documented and replicated in future projects.",
                body_style
            ))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # ===== 4. ACTIONABLE INSIGHTS & RECOMMENDATIONS =====
    elements.append(Paragraph(
        "4. ACTIONABLE INSIGHTS & RECOMMENDATIONS",
        section_heading_style
    ))
    
    elements.append(Paragraph("<b>Lessons Learned:</b>", body_bold_style))
    
    if summary:
        if total_variance > 0:
            elements.append(Paragraph(
                f"• Cost overruns in {over_budget} categories indicate estimation challenges or scope changes",
                body_style
            ))
            elements.append(Paragraph(
                "• Future projects should include contingency buffers for high-variance categories",
                body_style
            ))
        else:
            elements.append(Paragraph(
                "• Cost savings demonstrate effective project management and resource allocation",
                body_style
            ))
            elements.append(Paragraph(
                "• Document successful practices for replication in future projects",
                body_style
            ))
        
        if actual_only > 0:
            elements.append(Paragraph(
                f"• {actual_only} unbudgeted categories suggest gaps in initial scope definition",
                body_style
            ))
    
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph("<b>Recommended Actions:</b>", body_bold_style))
    
    elements.append(Paragraph(
        "1. <b>Refine Future Estimates:</b> Use actual costs from this project to create more accurate "
        "initial estimates. Focus on categories with significant variances and adjust assumptions accordingly.",
        body_style
    ))
    
    elements.append(Paragraph(
        "2. <b>Enhance Project Management:</b> Implement more rigorous cost tracking and earned value "
        "management (EVM) for real-time monitoring and course correction during project execution.",
        body_style
    ))
    
    elements.append(Paragraph(
        "3. <b>Strengthen Vendor Negotiation:</b> Replicate cost-saving strategies from categories that "
        "came in under budget. Standardize processes for negotiating bulk discounts with suppliers.",
        body_style
    ))
    
    elements.append(Paragraph(
        "4. <b>Review Scope Management:</b> Address unbudgeted items by improving initial scope definition "
        "and implementing formal change order processes to track and approve scope changes.",
        body_style
    ))
    
    elements.append(Spacer(1, 0.1*inch))
    
    # Conclusion
    elements.append(Paragraph("<b>Conclusion:</b>", body_bold_style))
    
    if summary:
        if abs(variance_pct) < 5:
            conclusion_text = (
                f"This project performed {status} by {abs(variance_pct):.1f}%, demonstrating strong cost control "
                "and accurate estimation. The variance analysis provides clear insights for maintaining this "
                "performance level in future projects. By addressing minor variances and replicating successful "
                "practices, management can continue to deliver projects on budget."
            )
        elif total_variance > 0:
            conclusion_text = (
                f"While the project exceeded the budget by {variance_pct:.1f}%, this variance analysis "
                "provides clear, actionable insights. By addressing the root causes of the unfavorable "
                "variances and implementing the recommended actions, management can make informed adjustments "
                "to improve the financial performance of future initiatives."
            )
        else:
            conclusion_text = (
                f"The project came in {abs(variance_pct):.1f}% under budget, demonstrating effective cost "
                "management. This variance analysis highlights successful practices that should be documented "
                "and replicated. Continue these approaches while remaining vigilant about scope definition "
                "and estimation accuracy."
            )
        
        elements.append(Paragraph(conclusion_text, body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(
        "Powered by Estimate Insight - AI-Powered Cost Variance Analysis",
        footer_style
    ))
    elements.append(Paragraph(
        f"© {datetime.now().year} Builder's Business Partner LLC",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


def generate_pdf_filename(project_name: str) -> str:
    """
    Generate a clean filename for the PDF export.
    
    Args:
        project_name: Name of the project
    
    Returns:
        Sanitized filename
    """
    # Remove special characters and replace spaces with underscores
    clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in project_name)
    clean_name = clean_name.replace(' ', '_')
    
    # Truncate if too long
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    
    # Add timestamp and extension
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"{clean_name}_{timestamp}.pdf"

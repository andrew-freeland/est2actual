#!/usr/bin/env python3
"""
PDF Export Module for Estimate Insight

Generates professional one-page PDF reports for project analyses.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from typing import Dict, Any


def generate_project_pdf(project_data: Dict[str, Any]) -> BytesIO:
    """
    Generate a one-page PDF report for a project analysis.
    
    Args:
        project_data: Dictionary containing project information with keys:
            - project_name: Name of the project
            - narrative: AI-generated insight text
            - summary: Dictionary of summary statistics
            - created_at: Analysis timestamp
            - doc_id: Optional Firestore document ID
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    
    # Create PDF with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        leading=12
    )
    
    # Extract data
    project_name = project_data.get('project_name', 'Unnamed Project')
    narrative = project_data.get('narrative', '')
    summary = project_data.get('summary', {})
    created_at = project_data.get('created_at')
    
    # Header
    elements.append(Paragraph("ESTIMATE INSIGHT REPORT", title_style))
    
    # Subtitle with date
    if created_at:
        date_str = created_at.strftime('%B %d, %Y') if hasattr(created_at, 'strftime') else str(created_at)
    else:
        date_str = datetime.now().strftime('%B %d, %Y')
    elements.append(Paragraph(f"Generated on {date_str}", subtitle_style))
    
    elements.append(Spacer(1, 0.1*inch))
    
    # Project Title
    elements.append(Paragraph(project_name, heading_style))
    
    elements.append(Spacer(1, 0.1*inch))
    
    # Summary Statistics Table
    if summary:
        total_estimated = summary.get('total_estimated', 0)
        total_actual = summary.get('total_actual', 0)
        total_variance = summary.get('total_variance', 0)
        variance_pct = summary.get('total_variance_pct', 0)
        
        # Determine status color
        if total_variance > 0:
            status = "OVER BUDGET"
            status_color = colors.HexColor('#dc2626')
        elif total_variance < 0:
            status = "UNDER BUDGET"
            status_color = colors.HexColor('#16a34a')
        else:
            status = "ON BUDGET"
            status_color = colors.HexColor('#2563eb')
        
        # Summary table data
        summary_data = [
            ['Total Estimated', f'${total_estimated:,.2f}'],
            ['Total Actual', f'${total_actual:,.2f}'],
            ['Variance', f'${total_variance:,.2f}'],
            ['Variance %', f'{variance_pct:.1f}%'],
            ['Status', status]
        ]
        
        # Create table
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, -1), (-1, -1), status_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # AI Insight Section
    elements.append(Paragraph("AI-Generated Insight", heading_style))
    
    # Format narrative for PDF
    if narrative:
        # Split narrative into paragraphs and format
        paragraphs = narrative.split('\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                # Convert bullet points
                if para.startswith('•'):
                    para = '&nbsp;&nbsp;&nbsp;&nbsp;' + para
                elements.append(Paragraph(para, body_style))
    else:
        elements.append(Paragraph("No insight available.", body_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER
    )
    
    elements.append(Spacer(1, 0.1*inch))
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
    
    # Get PDF from buffer
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


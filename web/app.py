#!/usr/bin/env python3
"""
Web UI Flask Application - User-friendly upload interface

This serves the HTML templates and communicates with the backend API.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
import tempfile
from werkzeug.utils import secure_filename

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from routes.api import analyze_files


def create_web_app():
    """Create and configure Flask web application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    return app


app = create_web_app()


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Estimate Insight is running'}, 200


@app.route('/', methods=['GET'])
def index():
    """Display the upload form."""
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    """
    Handle form submission and process files.
    
    Receives files from the form, saves them temporarily,
    runs analysis, and redirects to results page.
    """
    # Validate files
    if 'estimate_file' not in request.files:
        flash('Please upload an estimate file', 'error')
        return redirect(url_for('index'))
    
    if 'actual_file' not in request.files:
        flash('Please upload an actual file', 'error')
        return redirect(url_for('index'))
    
    estimate_file = request.files['estimate_file']
    actual_file = request.files['actual_file']
    
    if estimate_file.filename == '' or actual_file.filename == '':
        flash('Please select both files', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(estimate_file.filename) or not allowed_file(actual_file.filename):
        flash('Only .xlsx and .xls files are allowed', 'error')
        return redirect(url_for('index'))
    
    # Get form parameters
    project_name = request.form.get('project_name', 'Unnamed Project').strip()
    if not project_name:
        project_name = 'Unnamed Project'
    
    save_memory = 'save_memory' in request.form
    generate_chart = 'generate_chart' in request.form
    
    # Save files temporarily and run analysis
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            estimate_path = os.path.join(temp_dir, secure_filename(estimate_file.filename))
            actual_path = os.path.join(temp_dir, secure_filename(actual_file.filename))
            
            estimate_file.save(estimate_path)
            actual_file.save(actual_path)
            
            # Run analysis using the same backend logic as the API
            result = analyze_files(
                estimate_path,
                actual_path,
                project_name=project_name,
                save_memory=save_memory,
                quick_mode=False,  # Always use Gemini for web UI
                generate_chart=generate_chart
            )
        
        if not result.get('success'):
            flash(f"Analysis failed: {result.get('error', 'Unknown error')}", 'error')
            return redirect(url_for('index'))
        
        # Pass results to template
        return render_template('result.html', **result)
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/patterns', methods=['GET'])
def patterns():
    """
    Display learned insights from memory.
    
    Shows all projects with variance patterns and trends.
    """
    try:
        from memory.store_project_summary import get_all_projects
        
        try:
            projects = get_all_projects(limit=50)
        except:
            # Function might not exist yet, return empty
            projects = []
        
        # Calculate aggregate statistics
        if projects:
            total_projects = len(projects)
            avg_variance = sum(p.get('summary', {}).get('total_variance', 0) for p in projects) / total_projects if total_projects > 0 else 0
            over_budget_count = sum(1 for p in projects if p.get('summary', {}).get('total_variance', 0) > 0)
        else:
            total_projects = 0
            avg_variance = 0
            over_budget_count = 0
        
        stats = {
            'total_projects': total_projects,
            'avg_variance': avg_variance,
            'over_budget_count': over_budget_count,
            'under_budget_count': total_projects - over_budget_count
        }
        
        return render_template('patterns.html', projects=projects, stats=stats)
    
    except Exception as e:
        flash(f'Could not retrieve patterns: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/export_pdf/<doc_id>', methods=['GET'])
def export_pdf(doc_id):
    """
    Export a project analysis as a PDF.
    
    Args:
        doc_id: Firestore document ID of the project
    
    Returns:
        PDF file download
    """
    try:
        from google.cloud import firestore
        from report.export_pdf import generate_project_pdf, generate_pdf_filename
        from flask import send_file
        
        # Initialize Firestore
        db = firestore.Client(project=os.getenv('GCP_PROJECT_ID'))
        
        # Retrieve project data
        doc_ref = db.collection('project_insights').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            flash('Project not found', 'error')
            return redirect(url_for('patterns'))
        
        project_data = doc.to_dict()
        
        # Generate PDF
        pdf_buffer = generate_project_pdf(project_data)
        
        # Generate filename
        project_name = project_data.get('project_name', 'Project')
        filename = generate_pdf_filename(project_name)
        
        # Send PDF
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'Failed to generate PDF: {str(e)}', 'error')
        return redirect(url_for('patterns'))


@app.route('/analyze', methods=['POST'])
def analyze_api():
    """
    API endpoint for programmatic analysis (same as routes/api.py).
    
    Expected request:
    - Content-Type: multipart/form-data
    - Files: estimate_file, actual_file
    - Form data: project_name, save_memory, quick, generate_chart
    
    Returns JSON with variance analysis, AI insight, and optional chart.
    """
    from flask import jsonify
    
    # Validate request
    if 'estimate_file' not in request.files:
        return jsonify({'success': False, 'error': 'Missing estimate_file'}), 400
    
    if 'actual_file' not in request.files:
        return jsonify({'success': False, 'error': 'Missing actual_file'}), 400
    
    estimate_file = request.files['estimate_file']
    actual_file = request.files['actual_file']
    
    # Check if files are valid
    if estimate_file.filename == '' or actual_file.filename == '':
        return jsonify({'success': False, 'error': 'Empty filename'}), 400
    
    if not allowed_file(estimate_file.filename) or not allowed_file(actual_file.filename):
        return jsonify({'success': False, 'error': 'Files must be .xlsx or .xls'}), 400
    
    # Get parameters
    project_name = request.form.get('project_name', 'Unnamed Project')
    save_memory = request.form.get('save_memory', '').lower() in ['true', '1', 'yes']
    quick_mode = request.form.get('quick', '').lower() in ['true', '1', 'yes']
    generate_chart = request.form.get('generate_chart', '').lower() in ['true', '1', 'yes']
    
    # Process files
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            estimate_path = os.path.join(temp_dir, secure_filename(estimate_file.filename))
            actual_path = os.path.join(temp_dir, secure_filename(actual_file.filename))
            
            estimate_file.save(estimate_path)
            actual_file.save(actual_path)
            
            # Run analysis
            result = analyze_files(
                estimate_path,
                actual_path,
                project_name=project_name,
                save_memory=save_memory,
                quick_mode=quick_mode,
                generate_chart=generate_chart
            )
        
        return jsonify(result), 200 if result.get('success') else 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@app.errorhandler(413)
def file_too_large(e):
    """Handle file too large errors."""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)


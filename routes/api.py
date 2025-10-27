"""
Flask API Routes - RESTful interface for estimate analysis

Exposes the core analysis engine via HTTP endpoints.
"""

from flask import Flask, request, jsonify
import tempfile
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
from werkzeug.utils import secure_filename

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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
from memory.store_project_summary import (
    store_project_insight,
    retrieve_similar_projects,
    get_project_history
)
from visuals.generate_chart import generate_variance_bar_chart, chart_to_base64


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    return app


app = create_app()


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}


def analyze_files(estimate_path: str, actual_path: str, 
                  project_name: str = "Unnamed Project",
                  save_memory: bool = False,
                  quick_mode: bool = False,
                  generate_chart: bool = False) -> Dict[str, Any]:
    """
    Core analysis logic - reusable by both CLI and API.
    
    Args:
        estimate_path: Path to estimate Excel file
        actual_path: Path to actual Excel file
        project_name: Name of the project
        save_memory: Whether to save to Firestore
        quick_mode: Skip Gemini and use quick summary
        generate_chart: Whether to generate and return chart visualization
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Step 1: Load Excel files
        estimate_df = load_excel(estimate_path)
        actual_df = load_excel(actual_path)
        
        # Step 2: Calculate variance
        variance_df = compare_estimates(estimate_df, actual_df)
        
        # Step 3: Generate summary statistics
        summary_stats = generate_summary_stats(variance_df)
        
        # Step 4: Retrieve similar past projects (if memory enabled)
        prior_summaries = []
        if save_memory:
            try:
                search_query = f"{project_name} budget variance analysis"
                prior_summaries = retrieve_similar_projects(search_query, limit=3)
            except Exception as e:
                print(f"Warning: Could not retrieve memory: {str(e)}")
        
        # Step 5: Generate narrative insight
        if quick_mode:
            narrative = generate_quick_summary(summary_stats)
        else:
            try:
                initialize_vertex_ai()
                variance_data_str = variance_df.to_string(index=False)
                narrative = generate_insight_narrative(
                    variance_data_str,
                    summary_stats,
                    project_name,
                    prior_summaries=prior_summaries
                )
            except Exception as e:
                print(f"Warning: Gemini failed, using quick summary: {str(e)}")
                narrative = generate_quick_summary(summary_stats)
        
        # Step 6: Save to memory (optional)
        doc_id = None
        if save_memory:
            try:
                doc_id = store_project_insight(
                    project_name=project_name,
                    narrative=narrative,
                    variance_summary=summary_stats,
                    metadata={
                        'similar_projects_count': len(prior_summaries)
                    }
                )
            except Exception as e:
                print(f"Warning: Could not save to memory: {str(e)}")
        
        # Step 7: Generate chart (optional)
        chart_base64 = None
        if generate_chart:
            try:
                chart_path = generate_variance_bar_chart(variance_df, project_name)
                chart_base64 = chart_to_base64(chart_path)
                # Clean up temp file
                import os
                try:
                    os.remove(chart_path)
                except:
                    pass
            except Exception as e:
                print(f"Warning: Could not generate chart: {str(e)}")
        
        # Prepare response
        result = {
            'success': True,
            'project_name': project_name,
            'summary': summary_stats,
            'narrative': narrative,
            'variance_data': variance_df.to_dict('records'),
            'pattern_detection_enabled': len(prior_summaries) > 0,
            'similar_projects_count': len(prior_summaries),
            'memory_id': doc_id
        }
        
        # Add chart if generated
        if chart_base64:
            result['chart_image_base64'] = chart_base64
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({
        'status': 'healthy',
        'service': 'Estimate Insight Agent Pro',
        'version': '2.0.0',
        'endpoints': {
            'POST /analyze': 'Analyze estimate vs actual files',
            'GET /history/<project_name>': 'Get project history',
            'GET /': 'Health check'
        }
    })


@app.route('/analyze', methods=['POST'])
def analyze_estimates():
    """
    Analyze estimate vs actual files.
    
    Expected request:
    - Content-Type: multipart/form-data
    - Files: estimate_file, actual_file
    - Form data: project_name (optional), save_memory (optional), quick (optional), generate_chart (optional)
    
    Returns JSON with variance analysis, AI insight, and optional chart image (base64).
    """
    # Validate request
    if 'estimate_file' not in request.files:
        return jsonify({'success': False, 'error': 'Missing estimate_file'}), 400
    
    if 'actual_file' not in request.files:
        return jsonify({'success': False, 'error': 'Missing actual_file'}), 400
    
    estimate_file = request.files['estimate_file']
    actual_file = request.files['actual_file']
    
    # Check if files are valid
    if estimate_file.filename == '':
        return jsonify({'success': False, 'error': 'Empty estimate filename'}), 400
    
    if actual_file.filename == '':
        return jsonify({'success': False, 'error': 'Empty actual filename'}), 400
    
    if not allowed_file(estimate_file.filename):
        return jsonify({'success': False, 'error': 'Estimate file must be .xlsx or .xls'}), 400
    
    if not allowed_file(actual_file.filename):
        return jsonify({'success': False, 'error': 'Actual file must be .xlsx or .xls'}), 400
    
    # Get optional parameters
    project_name = request.form.get('project_name', 'Unnamed Project')
    save_memory = request.form.get('save_memory', 'false').lower() == 'true'
    quick_mode = request.form.get('quick', 'false').lower() == 'true'
    generate_chart = request.form.get('generate_chart', 'false').lower() == 'true'
    
    # Save uploaded files to temporary location
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
    
    # Return appropriate status code
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/history/<project_name>', methods=['GET'])
def get_history(project_name: str):
    """
    Retrieve historical insights for a project.
    
    Returns list of past analyses from Firestore.
    """
    try:
        history = get_project_history(project_name)
        
        # Convert datetime objects to strings for JSON serialization
        for entry in history:
            if 'created_at' in entry:
                entry['created_at'] = entry['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'project_name': project_name,
            'count': len(history),
            'history': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


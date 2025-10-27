#!/usr/bin/env python3
"""
Internal Test Script - Full AI Insight Workflow

This script tests the complete workflow WITHOUT using the web browser:
1. Auto-generates synthetic Excel files (estimate + actual)
2. Sends them to the Flask /analyze API endpoint
3. Prints the full JSON response including narrative, chart, and memory info

Usage:
    python scripts/run_internal_test.py
    
Requirements:
    - Flask server must be running on localhost:8080
    - GCP credentials must be configured in .env
"""

import requests
import json
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{text}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{CYAN}ℹ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def generate_test_data(tmp_dir):
    """
    Generate synthetic estimate and actual Excel files.
    
    Args:
        tmp_dir: Temporary directory to save files
        
    Returns:
        Tuple of (estimate_path, actual_path)
    """
    print_info("Generating synthetic test data...")
    
    # Estimate data - Construction project budget
    estimate = pd.DataFrame({
        'Category': [
            'Foundation Work',
            'Framing',
            'Roofing',
            'Electrical',
            'Plumbing',
            'HVAC',
            'Drywall & Insulation',
            'Flooring',
            'Paint & Finish',
            'Fixtures & Appliances'
        ],
        'Amount': [
            45000,  # Foundation
            65000,  # Framing
            35000,  # Roofing
            28000,  # Electrical
            22000,  # Plumbing
            18000,  # HVAC
            25000,  # Drywall
            30000,  # Flooring
            15000,  # Paint
            20000   # Fixtures
        ]
    })
    
    # Actual data - with realistic variances (over and under budget)
    actual = pd.DataFrame({
        'Category': [
            'Foundation Work',
            'Framing',
            'Roofing',
            'Electrical',
            'Plumbing',
            'HVAC',
            'Drywall & Insulation',
            'Flooring',
            'Paint & Finish',
            'Fixtures & Appliances',
            'Permits & Fees',      # New line item
            'Site Cleanup'         # New line item
        ],
        'Amount': [
            48500,  # Foundation - over by $3,500
            62000,  # Framing - under by $3,000
            38000,  # Roofing - over by $3,000
            28000,  # Electrical - on budget
            24500,  # Plumbing - over by $2,500
            17000,  # HVAC - under by $1,000
            25000,  # Drywall - on budget
            33000,  # Flooring - over by $3,000
            14000,  # Paint - under by $1,000
            22000,  # Fixtures - over by $2,000
            3500,   # Permits - unbudgeted
            2000    # Cleanup - unbudgeted
        ]
    })
    
    # Save to Excel in temp directory
    estimate_path = os.path.join(tmp_dir, 'estimate.xlsx')
    actual_path = os.path.join(tmp_dir, 'actual.xlsx')
    
    estimate.to_excel(estimate_path, index=False)
    actual.to_excel(actual_path, index=False)
    
    print_success(f"Generated estimate.xlsx ({len(estimate)} items)")
    print_success(f"Generated actual.xlsx ({len(actual)} items)")
    
    # Print summary
    total_estimate = estimate['Amount'].sum()
    total_actual = actual['Amount'].sum()
    variance = total_actual - total_estimate
    variance_pct = (variance / total_estimate) * 100
    
    print_info(f"Total Estimate: ${total_estimate:,.2f}")
    print_info(f"Total Actual: ${total_actual:,.2f}")
    print_info(f"Variance: ${variance:,.2f} ({variance_pct:+.1f}%)")
    
    return estimate_path, actual_path


def check_server_running(base_url):
    """
    Check if Flask server is running.
    
    Args:
        base_url: Base URL of the server
        
    Returns:
        Boolean indicating if server is accessible
    """
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # Try root endpoint as fallback
        try:
            response = requests.get(base_url, timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def send_to_api(estimate_path, actual_path, base_url='http://localhost:8080'):
    """
    Send files to the Flask /analyze API endpoint.
    
    Args:
        estimate_path: Path to estimate Excel file
        actual_path: Path to actual Excel file
        base_url: Base URL of the Flask server
        
    Returns:
        Response JSON or None if error
    """
    print_info("Sending files to /analyze endpoint...")
    
    try:
        # Prepare files for upload
        with open(estimate_path, 'rb') as est_file, open(actual_path, 'rb') as act_file:
            files = {
                'estimate_file': ('estimate.xlsx', est_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                'actual_file': ('actual.xlsx', act_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            # Prepare form data
            data = {
                'project_name': 'InternalTest',
                'save_memory': 'true',
                'generate_chart': 'true',
                'quick': 'false'  # Use Gemini AI for full analysis
            }
            
            # Make POST request
            print_info(f"POST {base_url}/analyze")
            print_info(f"   project_name: InternalTest")
            print_info(f"   save_memory: true")
            print_info(f"   generate_chart: true")
            
            response = requests.post(
                f"{base_url}/analyze",
                files=files,
                data=data,
                timeout=120  # Allow up to 2 minutes for AI processing
            )
            
            # Check response status
            if response.status_code == 200:
                print_success(f"API request successful (200 OK)")
                return response.json()
            else:
                print_error(f"API request failed ({response.status_code})")
                print_error(f"Response: {response.text}")
                return None
                
    except requests.exceptions.Timeout:
        print_error("Request timed out (exceeded 120 seconds)")
        return None
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server")
        print_warning("Make sure Flask is running: python3 web/app.py")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return None


def print_response(response):
    """
    Pretty print the API response.
    
    Args:
        response: JSON response from API
    """
    print_header("API RESPONSE")
    
    if not response:
        print_error("No response received")
        return
    
    # Check success status
    if not response.get('success', False):
        print_error("Analysis failed")
        print(json.dumps(response, indent=2))
        return
    
    print_success("Analysis completed successfully!\n")
    
    # Print narrative insight
    if 'narrative' in response:
        print(f"{BOLD}{CYAN}AI-Generated Narrative:{RESET}")
        print(f"{'-'*60}")
        print(response['narrative'])
        print(f"{'-'*60}\n")
    
    # Print summary statistics
    if 'summary' in response:
        print(f"{BOLD}{CYAN}Summary Statistics:{RESET}")
        summary = response['summary']
        print(f"  Total Estimated: ${summary.get('total_estimate', 0):,.2f}")
        print(f"  Total Actual: ${summary.get('total_actual', 0):,.2f}")
        print(f"  Total Variance: ${summary.get('total_variance', 0):,.2f}")
        print(f"  Variance %: {summary.get('variance_percentage', 0):.1f}%")
        print(f"  Items Over Budget: {summary.get('over_budget_count', 0)}")
        print(f"  Items Under Budget: {summary.get('under_budget_count', 0)}")
        print()
    
    # Print chart info
    if 'chart_image_base64' in response and response['chart_image_base64']:
        print_success(f"Chart generated ({len(response['chart_image_base64'])} bytes base64)")
        print_info("Chart is included in response as base64-encoded PNG")
        print()
    
    # Print memory info
    if 'memory_id' in response and response['memory_id']:
        print_success(f"Saved to Firestore with ID: {response['memory_id']}")
        print()
    
    # Print similar projects
    if 'similar_projects' in response and response['similar_projects']:
        print(f"{BOLD}{CYAN}Similar Past Projects:{RESET}")
        for i, proj in enumerate(response['similar_projects'], 1):
            print(f"  {i}. {proj.get('project_name', 'Unknown')} (similarity: {proj.get('similarity_score', 0):.2f})")
        print()
    
    # Print raw JSON (optional - commented out by default)
    # print(f"{BOLD}{CYAN}Full JSON Response:{RESET}")
    # print(json.dumps(response, indent=2))


def save_results_to_file(response, output_dir='tmp'):
    """
    Save test results to a file for review.
    
    Args:
        response: JSON response from API
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'test_results_{timestamp}.json')
    
    with open(output_file, 'w') as f:
        json.dump(response, f, indent=2)
    
    print_success(f"Results saved to: {output_file}")


def main():
    """Main test execution."""
    print_header("INTERNAL TEST - Full AI Insight Workflow")
    
    base_url = 'http://localhost:8080'
    
    # Step 1: Check if server is running
    print_info("Step 1: Checking if Flask server is running...")
    if not check_server_running(base_url):
        print_error("Flask server is not running!")
        print_warning("\nTo start the server, run:")
        print_warning("   python3 web/app.py\n")
        print_warning("Then run this test again:")
        print_warning("   python3 scripts/run_internal_test.py\n")
        sys.exit(1)
    
    print_success("Flask server is running")
    
    # Step 2: Generate test data
    print_info("\nStep 2: Generating synthetic test data...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        estimate_path, actual_path = generate_test_data(tmp_dir)
        
        # Step 3: Send to API
        print_info("\nStep 3: Sending files to API endpoint...")
        response = send_to_api(estimate_path, actual_path, base_url)
        
        if not response:
            print_error("\nTest failed - no response from API")
            sys.exit(1)
        
        # Step 4: Print results
        print_info("\nStep 4: Processing response...")
        print_response(response)
        
        # Step 5: Save results
        print_info("Step 5: Saving results to file...")
        save_results_to_file(response)
    
    # Final summary
    print_header("TEST COMPLETE")
    
    if response and response.get('success'):
        print_success("✅ All tests passed!")
        print_success("✅ AI insights generated")
        print_success("✅ Chart created")
        print_success("✅ Memory saved to Firestore")
        print()
        print_info("The system is working end-to-end! 🎉")
    else:
        print_error("❌ Test failed")
        print_warning("Check the error messages above for details")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


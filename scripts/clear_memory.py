#!/usr/bin/env python3
"""
Clear all project insights from Firestore memory.

This will delete ALL stored project analyses.
Use with caution!
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
ENDC = "\033[0m"


def clear_all_projects():
    """Delete all projects from Firestore."""
    try:
        from google.cloud import firestore
        
        print(f"\n{BOLD}{RED}⚠️  WARNING: This will DELETE ALL project history!{ENDC}")
        print(f"{YELLOW}This action cannot be undone.{ENDC}\n")
        
        # Confirmation
        confirm = input(f"Type 'DELETE ALL' to confirm: ")
        
        if confirm != "DELETE ALL":
            print(f"\n{YELLOW}Cancelled. No data was deleted.{ENDC}")
            return
        
        print(f"\n{BOLD}Connecting to Firestore...{ENDC}")
        
        # Initialize Firestore
        project_id = os.getenv('GCP_PROJECT_ID')
        if not project_id:
            print(f"{RED}Error: GCP_PROJECT_ID not set in .env{ENDC}")
            sys.exit(1)
        
        db = firestore.Client(project=project_id)
        
        # Get all documents
        print(f"{BOLD}Fetching all projects...{ENDC}")
        collection_ref = db.collection('project_insights')
        docs = collection_ref.stream()
        
        # Count and delete
        deleted_count = 0
        for doc in docs:
            print(f"  Deleting: {doc.id}")
            doc.reference.delete()
            deleted_count += 1
        
        print(f"\n{GREEN}{BOLD}✓ Successfully deleted {deleted_count} project(s)!{ENDC}")
        print(f"{GREEN}Memory cleared. You can start fresh.{ENDC}\n")
        
    except Exception as e:
        print(f"\n{RED}Error: {str(e)}{ENDC}\n")
        sys.exit(1)


if __name__ == "__main__":
    clear_all_projects()


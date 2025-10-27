"""
Feedback Storage: Store user feedback on AI insights for continuous improvement.

This module stores feedback on:
- Individual insight details (detailed feedback with text)
- Pattern summaries (simple thumbs up/down)
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.cloud import firestore


def initialize_firestore(project_id: str = None) -> firestore.Client:
    """
    Initialize Firestore client.
    
    Args:
        project_id: GCP project ID (defaults to env var GCP_PROJECT_ID)
    
    Returns:
        Firestore client instance
    """
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID must be set in environment or passed as argument")
    
    return firestore.Client(project=project_id)


def store_insight_feedback(
    insight_id: str,
    feedback_type: str,
    rating: str,
    feedback_text: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    collection_name: str = "insight_feedback"
) -> str:
    """
    Store user feedback on an AI-generated insight.
    
    Args:
        insight_id: ID of the project/insight being rated
        feedback_type: Type of feedback ('detailed' or 'summary')
        rating: User rating ('thumbs_up' or 'thumbs_down')
        feedback_text: Optional detailed feedback text
        metadata: Additional context (e.g., category, variance amount)
        collection_name: Firestore collection name
    
    Returns:
        Document ID of the stored feedback
    """
    db = initialize_firestore()
    
    # Prepare feedback document
    document = {
        'insight_id': insight_id,
        'feedback_type': feedback_type,
        'rating': rating,
        'feedback_text': feedback_text or '',
        'metadata': metadata or {},
        'created_at': datetime.utcnow(),
        'version': '1.0'
    }
    
    # Store in Firestore
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(document)
    
    return doc_ref.id


def get_feedback_for_insight(
    insight_id: str,
    collection_name: str = "insight_feedback"
) -> List[Dict[str, Any]]:
    """
    Retrieve all feedback for a specific insight.
    
    Args:
        insight_id: ID of the insight
        collection_name: Firestore collection name
    
    Returns:
        List of feedback documents
    """
    db = initialize_firestore()
    
    docs = db.collection(collection_name).where(
        'insight_id', '==', insight_id
    ).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        data['feedback_id'] = doc.id
        results.append(data)
    
    return results


def get_feedback_statistics(
    insight_id: Optional[str] = None,
    collection_name: str = "insight_feedback"
) -> Dict[str, Any]:
    """
    Get aggregate statistics on feedback.
    
    Args:
        insight_id: Optional - get stats for specific insight, or all if None
        collection_name: Firestore collection name
    
    Returns:
        Dictionary with feedback statistics
    """
    db = initialize_firestore()
    
    # Build query
    query = db.collection(collection_name)
    if insight_id:
        query = query.where('insight_id', '==', insight_id)
    
    docs = query.stream()
    
    # Calculate statistics
    total_feedback = 0
    thumbs_up = 0
    thumbs_down = 0
    detailed_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        total_feedback += 1
        
        if data.get('rating') == 'thumbs_up':
            thumbs_up += 1
        elif data.get('rating') == 'thumbs_down':
            thumbs_down += 1
        
        if data.get('feedback_text'):
            detailed_count += 1
    
    return {
        'total_feedback': total_feedback,
        'thumbs_up': thumbs_up,
        'thumbs_down': thumbs_down,
        'detailed_feedback_count': detailed_count,
        'satisfaction_rate': (thumbs_up / total_feedback * 100) if total_feedback > 0 else 0
    }


def get_recent_feedback(
    limit: int = 50,
    collection_name: str = "insight_feedback"
) -> List[Dict[str, Any]]:
    """
    Retrieve recent feedback across all insights.
    
    Args:
        limit: Maximum number of feedback items to return
        collection_name: Firestore collection name
    
    Returns:
        List of recent feedback documents
    """
    db = initialize_firestore()
    
    docs = db.collection(collection_name).order_by(
        'created_at', direction=firestore.Query.DESCENDING
    ).limit(limit).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        data['feedback_id'] = doc.id
        results.append(data)
    
    return results


def get_negative_feedback_for_review(
    limit: int = 20,
    collection_name: str = "insight_feedback"
) -> List[Dict[str, Any]]:
    """
    Retrieve negative feedback that may need attention.
    
    Args:
        limit: Maximum number of items to return
        collection_name: Firestore collection name
    
    Returns:
        List of negative feedback items with detailed text
    """
    db = initialize_firestore()
    
    docs = db.collection(collection_name).where(
        'rating', '==', 'thumbs_down'
    ).order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        # Only include items with detailed feedback text
        if data.get('feedback_text'):
            data['feedback_id'] = doc.id
            results.append(data)
    
    return results


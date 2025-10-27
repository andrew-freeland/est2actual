"""
Memory Store: Save project summaries to Firestore with embeddings for pattern detection.
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.cloud import firestore
import vertexai
from vertexai.language_models import TextEmbeddingModel


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


def generate_embedding(text: str, project_id: str = None) -> List[float]:
    """
    Generate embedding vector for text using Vertex AI.
    
    Args:
        text: Text to embed
        project_id: GCP project ID
    
    Returns:
        List of floats representing the embedding vector
    """
    if project_id is None:
        project_id = os.getenv("GCP_PROJECT_ID")
    
    # Initialize Vertex AI if not already done
    try:
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
        embeddings = model.get_embeddings([text])
        return embeddings[0].values
    except Exception as e:
        print(f"Warning: Failed to generate embedding: {str(e)}")
        return []


def store_project_insight(
    project_name: str,
    narrative: str,
    variance_summary: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    collection_name: str = "project_insights"
) -> str:
    """
    Store a project insight in Firestore with embedding for future recall.
    
    Args:
        project_name: Name of the project
        narrative: Generated narrative insight
        variance_summary: Summary statistics dictionary
        metadata: Additional metadata (e.g., file paths, user info)
        collection_name: Firestore collection name
    
    Returns:
        Document ID of the stored insight
    """
    db = initialize_firestore()
    
    # Generate embedding for semantic search
    embedding_text = f"{project_name}\n{narrative}"
    embedding = generate_embedding(embedding_text)
    
    # Prepare document
    document = {
        'project_name': project_name,
        'narrative': narrative,
        'variance_summary': variance_summary,
        'embedding': embedding,
        'metadata': metadata or {},
        'created_at': datetime.utcnow(),
        'version': '1.0'
    }
    
    # Store in Firestore
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(document)
    
    return doc_ref.id


def retrieve_similar_projects(
    query_text: str,
    limit: int = 5,
    collection_name: str = "project_insights"
) -> List[Dict[str, Any]]:
    """
    Retrieve similar past projects based on semantic similarity.
    
    Args:
        query_text: Text to search for (e.g., current project narrative)
        limit: Maximum number of results to return
        collection_name: Firestore collection name
    
    Returns:
        List of similar project documents
    """
    db = initialize_firestore()
    
    # Generate embedding for query
    query_embedding = generate_embedding(query_text)
    
    if not query_embedding:
        print("Warning: Could not generate query embedding, returning empty results")
        return []
    
    # Note: Firestore doesn't have native vector similarity search
    # For production, consider using Vertex AI Vector Search or pgvector
    # For now, we'll return recent projects as a placeholder
    
    docs = db.collection(collection_name).order_by(
        'created_at', direction=firestore.Query.DESCENDING
    ).limit(limit).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        results.append(data)
    
    return results


def get_project_history(
    project_name: str,
    collection_name: str = "project_insights"
) -> List[Dict[str, Any]]:
    """
    Retrieve all insights for a specific project.
    
    Args:
        project_name: Name of the project
        collection_name: Firestore collection name
    
    Returns:
        List of project insight documents
    """
    db = initialize_firestore()
    
    docs = db.collection(collection_name).where(
        'project_name', '==', project_name
    ).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        results.append(data)
    
    return results


def get_all_projects(
    limit: int = 50,
    collection_name: str = "project_insights"
) -> List[Dict[str, Any]]:
    """
    Retrieve all project insights from Firestore.
    
    Args:
        limit: Maximum number of projects to return
        collection_name: Firestore collection name
    
    Returns:
        List of all project insight documents
    """
    db = initialize_firestore()
    
    docs = db.collection(collection_name).order_by(
        'created_at', direction=firestore.Query.DESCENDING
    ).limit(limit).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        # Ensure summary key exists for compatibility
        if 'variance_summary' in data:
            data['summary'] = data['variance_summary']
        results.append(data)
    
    return results


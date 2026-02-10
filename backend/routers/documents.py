from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
import os
from datetime import datetime
import uuid

from database import get_db
from models import Document, Case, User
from schemas import DocumentCreate, DocumentResponse
from routers.auth import get_current_user

router = APIRouter()

# Document storage configuration
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()

def generate_digital_signature(file_hash: str, user_id: int) -> str:
    """
    Generate digital signature for document
    AI/ML PLACEHOLDER: This will be enhanced with proper PKI implementation
    """
    # Basic signature for now - will be replaced with proper cryptographic signature
    signature_data = f"{file_hash}:{user_id}:{datetime.now().isoformat()}"
    return hashlib.sha256(signature_data.encode()).hexdigest()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    case_id: int,
    title: str,
    document_type: str,
    is_public: bool = False,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for a case"""
    
    # Verify case exists and user has access
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check permissions
    if (current_user.role not in ["chief_justice", "court_administrator"] and 
        case.court_id != current_user.court_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read file content
    file_content = await file.read()
    file_hash = calculate_file_hash(file_content)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Generate digital signature
    digital_signature = generate_digital_signature(file_hash, current_user.id)
    
    # Check if this is a new version of existing document
    existing_doc = db.query(Document).filter(
        Document.case_id == case_id,
        Document.title == title,
        Document.document_type == document_type
    ).order_by(Document.version.desc()).first()
    
    version = (existing_doc.version + 1) if existing_doc else 1
    
    # Create document record
    db_document = Document(
        case_id=case_id,
        title=title,
        document_type=document_type,
        file_path=file_path,
        file_hash=file_hash,
        digital_signature=digital_signature,
        version=version,
        uploaded_by=current_user.id,
        is_public=is_public
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/case/{case_id}", response_model=List[DocumentResponse])
async def get_case_documents(
    case_id: int,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents for a case"""
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check permissions
    if (current_user.role not in ["chief_justice", "court_administrator"] and 
        case.court_id != current_user.court_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(Document).filter(Document.case_id == case_id)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    documents = query.order_by(Document.upload_date.desc()).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document details"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    case = document.case
    if (not document.is_public and 
        current_user.role not in ["chief_justice", "court_administrator"] and 
        case.court_id != current_user.court_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return document

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download document file"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    case = document.case
    if (not document.is_public and 
        current_user.role not in ["chief_justice", "court_administrator"] and 
        case.court_id != current_user.court_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=document.file_path,
        filename=f"{document.title}_{document.version}.pdf",
        media_type='application/octet-stream'
    )

@router.post("/{document_id}/verify")
async def verify_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify document integrity and signature"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if file exists
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Read file and calculate current hash
    with open(document.file_path, "rb") as f:
        current_content = f.read()
    
    current_hash = calculate_file_hash(current_content)
    
    # Verify hash matches stored hash
    hash_valid = current_hash == document.file_hash
    
    # Verify digital signature
    expected_signature = generate_digital_signature(document.file_hash, document.uploaded_by)
    signature_valid = expected_signature == document.digital_signature
    
    return {
        "document_id": document_id,
        "hash_valid": hash_valid,
        "signature_valid": signature_valid,
        "is_authentic": hash_valid and signature_valid,
        "stored_hash": document.file_hash,
        "current_hash": current_hash,
        "upload_date": document.upload_date,
        "uploaded_by": document.uploader.full_name if document.uploader else "Unknown"
    }

@router.get("/search/semantic")
async def semantic_document_search(
    query: str,
    case_id: Optional[int] = None,
    document_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Semantic search across legal documents
    AI/ML PLACEHOLDER: This will use TensorFlow.js and NLP models
    """
    
    # Basic text search for now - will be enhanced with semantic search
    query_filter = db.query(Document)
    
    if case_id:
        query_filter = query_filter.filter(Document.case_id == case_id)
    
    if document_type:
        query_filter = query_filter.filter(Document.document_type == document_type)
    
    # Filter by user's court access
    if current_user.role not in ["chief_justice", "court_administrator"]:
        query_filter = query_filter.join(Case).filter(Case.court_id == current_user.court_id)
    
    # Basic title search for now
    documents = query_filter.filter(
        Document.title.ilike(f"%{query}%")
    ).limit(limit).all()
    
    # AI/ML PLACEHOLDER: Replace with semantic search results
    search_results = []
    for doc in documents:
        search_results.append({
            "document_id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "case_number": doc.case.case_number,
            "relevance_score": 0.8,  # Placeholder score
            "snippet": f"Document: {doc.title}...",  # Placeholder snippet
            "upload_date": doc.upload_date
        })
    
    return {
        "query": query,
        "total_results": len(search_results),
        "results": search_results,
        "ai_ml_note": "Semantic search with TensorFlow.js and NLP models to be implemented"
    }

@router.get("/legal-entities/extract")
async def extract_legal_entities(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract legal entities from document
    AI/ML PLACEHOLDER: This will use Named Entity Recognition
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    case = document.case
    if (not document.is_public and 
        current_user.role not in ["chief_justice", "court_administrator"] and 
        case.court_id != current_user.court_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # AI/ML PLACEHOLDER: Implement NER for legal entities
    extracted_entities = {
        "acts": ["Indian Penal Code", "Code of Criminal Procedure"],  # Placeholder
        "sections": ["Section 302", "Section 420"],  # Placeholder
        "precedents": ["Kesavananda Bharati v. State of Kerala"],  # Placeholder
        "parties": ["Plaintiff", "Defendant"],  # Placeholder
        "dates": ["2024-01-15"],  # Placeholder
        "amounts": ["Rs. 1,00,000"]  # Placeholder
    }
    
    return {
        "document_id": document_id,
        "document_title": document.title,
        "extracted_entities": extracted_entities,
        "ai_ml_note": "Named Entity Recognition for legal documents to be implemented with TensorFlow.js"
    }

@router.get("/citation-network/{document_id}")
async def get_citation_network(
    document_id: int,
    depth: int = 2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get citation network for a document
    AI/ML PLACEHOLDER: This will build citation graphs
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # AI/ML PLACEHOLDER: Build actual citation network
    citation_network = {
        "nodes": [
            {"id": document_id, "title": document.title, "type": "source"},
            {"id": "cite_1", "title": "Related Case 1", "type": "citation"},
            {"id": "cite_2", "title": "Related Case 2", "type": "citation"}
        ],
        "edges": [
            {"source": document_id, "target": "cite_1", "type": "cites"},
            {"source": document_id, "target": "cite_2", "type": "cites"}
        ]
    }
    
    return {
        "document_id": document_id,
        "citation_network": citation_network,
        "depth": depth,
        "ai_ml_note": "Citation network analysis to be implemented with graph algorithms"
    }
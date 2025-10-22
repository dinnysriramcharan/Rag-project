import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Ensure project root is on sys.path when running with uvicorn --reload
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from backend/.env if present
load_dotenv(PROJECT_ROOT / "backend" / ".env", override=False)

from backend.rag.chain import RAGChain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for validation
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    history: Optional[List[dict]] = Field(default=None, description="Chat history")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    namespace: Optional[str] = Field(default="default", max_length=100, description="Document namespace")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"
    uptime: str

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024  # 10MB default
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}

def _get_allowed_origins() -> List[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    if not raw:
        # Default origins for development and production
        return [
            "http://localhost:5173", 
            "http://localhost:5174", 
            "http://localhost:3000",
            "https://ragproject.vercel.app",
            "*"
        ]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

# Rate limiting (simple in-memory)
request_counts = {}
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit(client_ip: str) -> bool:
    now = datetime.now()
    minute_key = f"{client_ip}:{now.minute}"
    
    if minute_key not in request_counts:
        request_counts[minute_key] = 0
    
    if request_counts[minute_key] >= RATE_LIMIT_REQUESTS:
        return False
    
    request_counts[minute_key] += 1
    return True

app = FastAPI(
    title="AI Document Search (RAG Chatbot)",
    description="Production-ready RAG chatbot with document upload and semantic search",
    version="1.0.0"
)

@app.on_event("startup")
async def _check_required_env() -> None:
    missing: List[str] = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("PINECONE_API_KEY"):
        missing.append("PINECONE_API_KEY")
    if not os.getenv("PINECONE_ENV"):
        missing.append("PINECONE_ENV")
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Create backend/.env (copy backend/env.example) and set real values."
        )
    logger.info("Application startup completed successfully")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Please try again later."}
        )
    
    response = await call_next(request)
    return response

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        uptime="running"
    )

# Detailed health check
@app.get("/health/detailed")
@app.get("/api/health/detailed")
async def detailed_health():
    try:
        # Test RAG chain initialization
        chain = _get_chain()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "rag_chain": "healthy",
                "openai": "connected",
                "pinecone": "connected"
            },
            "configuration": {
                "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
                "allowed_extensions": list(ALLOWED_EXTENSIONS),
                "rate_limit_requests_per_minute": RATE_LIMIT_REQUESTS
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

_rag_chain: Optional[RAGChain] = None

def _get_chain() -> RAGChain:
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain

@app.options("/chat")
@app.options("/api/chat")
async def chat_options():
    from fastapi.responses import Response
    return Response(
        content="OK",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/chat")
@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict:
    """Chat with the AI using document context"""
    try:
        logger.info(f"Chat request received: {len(request.message)} chars, top_k={request.top_k}")
        
        chain = _get_chain()
        result = chain.invoke(
            message=request.message,
            history=request.history,
            top_k=request.top_k,
            namespace=request.namespace
        )
        
        logger.info(f"Chat response generated with {len(result.get('citations', []))} citations")
        return result
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")

@app.options("/upload")
@app.options("/api/upload")
async def upload_options():
    from fastapi.responses import Response
    return Response(
        content="OK",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/upload")
@app.post("/api/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    namespace: str = Form(default="default")
) -> dict:
    """Upload and process a document with validation"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )
    
    # Validate namespace
    if not namespace or len(namespace.strip()) == 0:
        namespace = "default"
    namespace = namespace.strip()
    
    logger.info(f"Processing upload: {file.filename} ({len(content)} bytes) to namespace '{namespace}'")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process the file using the ingestion logic
        from scripts.ingest import file_to_text, chunk_text, build_items, upsert_items
        
        # Extract text
        text = file_to_text(Path(tmp_file_path))
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in file")
        
        # Chunk text
        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="No content chunks created")
        
        # Build items for upsert
        items = build_items(Path(file.filename), chunks)
        
        # Upsert to Pinecone
        upsert_items(
            index_name=os.getenv("PINECONE_INDEX", "documents"),
            namespace=namespace,
            items=items
        )
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        logger.info(f"Successfully processed {file.filename}: {len(chunks)} chunks created")
        
        return {
            "success": True,
            "message": f"Successfully processed {file.filename}",
            "chunks_created": len(chunks),
            "namespace": namespace,
            "file_size_bytes": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error for {file.filename}: {e}")
        # Clean up temp file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} from {request.client.host}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} from {request.client.host}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
import os
import shutil
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Your existing modules
from chat_with_notes.data_extraction import process_pdf
from chat_with_notes.rag_query import ask as rag_ask

import requests

# ================= CONFIG =================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

# ================= FASTAPI APP =================
app = FastAPI(title="PDF Chat Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= MODELS =================
class ChatRequest(BaseModel):
    message: str
    use_pdf: bool = False

# ================= HELPERS =================
def call_general_llm(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    res = requests.post(OLLAMA_URL, json=payload)
    res.raise_for_status()
    return res.json()["response"]

# ================= ROUTES =================
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF and build FAISS index
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    try:
        pdf_path = os.path.join(UPLOAD_DIR, file.filename)
        
        logger.info(f"Uploading PDF: {file.filename}")
        
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"PDF saved, starting processing...")
        
        # Process PDF → embeddings → FAISS
        # This can take time for large PDFs
        process_pdf(pdf_path)
        
        logger.info(f"PDF processing complete: {file.filename}")
        
        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
        }
    except Exception as e:
        logger.error(f"Error processing PDF {file.filename}: {e}", exc_info=True)
        return {
            "error": f"Failed to process PDF: {str(e)}",
            "filename": file.filename,
        }

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Chat endpoint:
    - If use_pdf = True → RAG over PDF
    - If use_pdf = False → general LLM
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if request.use_pdf:
        try:
            logger.info(f"Using RAG for question: {request.message[:100]}...")
            answer = rag_ask(request.message)
            logger.info("RAG answer generated successfully")
            return {
                "answer": answer,
                "source": "pdf",
            }
        except FileNotFoundError as e:
            logger.error(f"FAISS index not found: {e}")
            return {
                "error": "PDF has not been uploaded and processed yet. Please upload a PDF first.",
                "details": "The FAISS index file is missing. Upload a PDF to build the index.",
            }
        except Exception as e:
            logger.error(f"RAG error: {e}", exc_info=True)
            return {
                "error": "Error processing PDF-based question",
                "details": str(e),
            }

    # General chat
    logger.info(f"Using general LLM for question: {request.message[:100]}...")
    try:
        answer = call_general_llm(request.message)
        return {
            "answer": answer,
            "source": "general",
        }
    except Exception as e:
        logger.error(f"General LLM error: {e}", exc_info=True)
        return {
            "error": "Error generating response",
            "details": str(e),
        }

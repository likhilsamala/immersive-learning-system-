import json
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# ================= CONFIG =================
FAISS_INDEX_PATH = "data/extracted_data/faiss.index"
METADATA_PATH = "data/extracted_data/metadata.json"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

TOP_K = 5


# ================= LOAD =================
def load_faiss():
    index = faiss.read_index(FAISS_INDEX_PATH)
    return index


def load_metadata():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ================= EMBEDDING =================
def embed_query(query: str, model):
    emb = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return emb.astype("float32")


# ================= RETRIEVAL =================
def retrieve_chunks(query, index, metadata, model):
    query_emb = embed_query(query, model)
    distances, indices = index.search(query_emb, TOP_K)

    retrieved = []
    for idx in indices[0]:
        retrieved.append(metadata[idx])

    return retrieved


# ================= PROMPT =================
def build_prompt(context_chunks, question):
    if not context_chunks:
        return f"""
You are a helpful assistant. Answer the following question based on your knowledge.

Question: {question}

Answer:
"""
    
    context_text = "\n\n".join(
        f"[Chunk {i+1}]\n{chunk['text']}" for i, chunk in enumerate(context_chunks)
    )

    prompt = f"""You are a helpful assistant that answers questions based EXCLUSIVELY on the provided context from uploaded documents.

CRITICAL INSTRUCTIONS:
1. You MUST answer the question using ONLY the information provided in the context below
2. The context comes from PDF documents that the user has uploaded
3. If the answer can be found in the context, provide it directly from the context
4. Do NOT say the context is unrelated or not relevant - analyze it carefully
5. If the answer is truly not in the context, say "Based on the provided context, I cannot find a direct answer to this question. However, from the context I can see: [summarize what IS in the context]"
6. Do NOT make up information that isn't in the context
7. Quote or paraphrase specific parts of the context when answering

Context from uploaded documents:
{context_text}

Question: {question}

Answer (based ONLY on the context above):
"""
    return prompt.strip()


# ================= OLLAMA CALL =================
def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"]


# ================= MAIN =================
def ask(question: str):
    import logging
    import os
    logger = logging.getLogger(__name__)
    
    # Check if index exists
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}. Please upload a PDF first.")
    
    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}. Please upload a PDF first.")
    
    logger.info(f"Loading FAISS index and metadata for question: {question[:100]}...")
    index = load_faiss()
    metadata = load_metadata()
    
    logger.info(f"FAISS index loaded: {index.ntotal} vectors")
    logger.info(f"Metadata loaded: {len(metadata)} chunks")
    
    embedder = SentenceTransformer(EMBED_MODEL)
    logger.info("Embedding model loaded")

    logger.info("Retrieving relevant chunks...")
    chunks = retrieve_chunks(question, index, metadata, embedder)
    logger.info(f"Retrieved {len(chunks)} chunks")
    
    # Log retrieved chunks for debugging
    for i, chunk in enumerate(chunks):
        logger.debug(f"Chunk {i+1}: {chunk['text'][:100]}...")
    
    prompt = build_prompt(chunks, question)
    logger.info("Prompt built, calling Ollama...")
    
    answer = call_ollama(prompt)
    logger.info("Answer generated successfully")

    return answer


if __name__ == "__main__":
    while True:
        q = input("\nAsk a question (or 'exit'): ")
        if q.lower() == "exit":
            break
        answer = ask(q)
        print("\n🧠 Answer:\n")
        print(answer)

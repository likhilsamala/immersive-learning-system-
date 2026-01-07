import os
import re
import json
import uuid
import faiss
import torch
import numpy as np
from typing import List, Dict, Any

from docling.document_converter import DocumentConverter, FormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

from sentence_transformers import SentenceTransformer


# ================= CONFIG =================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

OUTPUT_DIR = "data/extracted_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FAISS_INDEX_PATH = f"{OUTPUT_DIR}/faiss.index"
METADATA_PATH = f"{OUTPUT_DIR}/metadata.json"
CHUNKS_TEXT_PATH = f"{OUTPUT_DIR}/chunks.txt"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ================= HELPERS =================
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()


def chunk_text(text: str) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ================= JSON TEXT EXTRACTION =================
def extract_text_from_json(obj: Any, collected: List[str]):
    """
    Recursively traverse Docling JSON and extract text
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in {"text", "value", "content"} and isinstance(v, str):
                if v.strip():
                    collected.append(v)
            else:
                extract_text_from_json(v, collected)

    elif isinstance(obj, list):
        for item in obj:
            extract_text_from_json(item, collected)


# ================= EXTRACTION =================
def extract_document(pdf_path: str) -> List[Dict]:
    pipeline_options = StandardPdfPipeline.get_default_options()
    pipeline_options.do_ocr = True
    pipeline_options.ocr_options.lang = ["eng"]
    pipeline_options.ocr_options.force_full_page_ocr = True

    format_options = {
        InputFormat.PDF: FormatOption(
            backend=PyPdfiumDocumentBackend,
            pipeline_cls=StandardPdfPipeline,
            pipeline_options=pipeline_options,
        )
    }

    converter = DocumentConverter(format_options=format_options)
    result = converter.convert(pdf_path)

    # 🔥 THIS IS THE KEY
    doc_json = result.document.model_dump()

    collected_text = []
    extract_text_from_json(doc_json, collected_text)

    full_text = "\n".join(collected_text)

    print(f"DEBUG: extracted raw text length = {len(full_text)}")
    print(f"DEBUG: sample = {full_text[:300]!r}")

    if not full_text.strip():
        return []

    return [{
        "type": "text",
        "content": full_text,
        "page": "all"
    }]


# ================= EMBEDDINGS =================
def embed_chunks(chunks: List[str]) -> np.ndarray:
    model = SentenceTransformer(EMBED_MODEL, device=DEVICE)
    embeddings = model.encode(
        chunks,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.astype("float32")


# ================= FAISS =================
def store_faiss(embeddings: np.ndarray):
    if embeddings.size == 0:
        print("⚠️ No embeddings to store")
        return

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)

    # 🚨 Windows-safe: DO NOT attempt GPU FAISS unless explicitly available
    use_gpu_faiss = False

    if use_gpu_faiss:
        try:
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index)
            print("🚀 FAISS GPU enabled")
        except Exception:
            print("⚠️ FAISS GPU unavailable, using CPU")

    index.add(embeddings)

    # ✅ Always write CPU index (portable)
    faiss.write_index(index, FAISS_INDEX_PATH)



# ================= MAIN =================
def process_pdf(pdf_path: str):
    extracted = extract_document(pdf_path)

    print(f"🔍 Extracted items: {len(extracted)}")
    if not extracted:
        print("❌ No data extracted")
        return

    all_chunks, metadata = [], []

    for item in extracted:
        cleaned = clean_text(item["content"])
        chunks = chunk_text(cleaned)

        for chunk in chunks:
            cid = str(uuid.uuid4())
            all_chunks.append(chunk)
            metadata.append({
                "chunk_id": cid,
                "source_file": os.path.basename(pdf_path),
                "page": item["page"],
                "content_type": item["type"],
                "text": chunk,
            })

    embeddings = embed_chunks(all_chunks)
    store_faiss(embeddings)

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(CHUNKS_TEXT_PATH, "w", encoding="utf-8") as f:
        for m in metadata:
            f.write(f"[{m['chunk_id']} | page {m['page']}]\n{m['text']}\n\n")

    print("\n✅ EXTRACTION COMPLETE")
    print("• OCR ✔")
    print("• Layout text ✔")
    print("• Embeddings ✔")
    print("• FAISS ✔")


# ================= ENTRY =================
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python data_extraction.py <pdf_path>")
        exit(1)
    process_pdf(sys.argv[1])

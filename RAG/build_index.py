import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    kb_path = "data/kb.jsonl"
    index_dir = "faiss_index"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150,
        separators=["\n\n", "\n", " - ", ". ", " "]
    )

    docs = []
    for item in load_jsonl(kb_path):
        text = f"Question: {item['question']}\n\nRéponse:\n{item['answer']}"
        chunks = splitter.split_text(text)
        for i, ch in enumerate(chunks):
            docs.append(Document(
                page_content=ch,
                metadata={
                    "id": item.get("id", ""),
                    "section": item.get("section", ""),
                    "source_url": item.get("source_url", ""),
                    "chunk_id": i
                }
            ))

    # 🚀 Use GPU if available for faster embedding computation
    device = 'cpu'
    try:
        import torch
        if torch.cuda.is_available():
            device = 'cuda'
            print(f"🚀 GPU detected! Using CUDA device: {torch.cuda.get_device_name()}")
        else:
            print("💻 No GPU available, using CPU")
    except ImportError:
        print("💻 PyTorch not available, using CPU")

    # Use local HuggingFace embeddings (multilingual model for French support)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': device},  # Use GPU if available
        encode_kwargs={'normalize_embeddings': True}
    )
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(index_dir)

    print(f"OK: indexed {len(docs)} chunks -> {index_dir}/")

if __name__ == "__main__":
    main()

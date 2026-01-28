# RAG System - Essential Files Only

## 📁 Project Structure
```
julie-rag/
├── extract_docx_to_jsonl.py   # Convert DOCX to JSONL
├── build_index.py              # Build FAISS index
├── rag_api.py                  # YOUR MAIN API (use this)
├── requirement.txt             # Dependencies
├── data/
│   └── kb.jsonl               # Knowledge base (47 Q&A)
└── faiss_index/               # Vector database
```

## 🚀 Quick Start

### 1. If you need to rebuild from new DOCX:
```bash
python extract_docx_to_jsonl.py
python build_index.py
```

### 2. To use the RAG API:
```python
from rag_api import RAGKnowledgeBase

# Initialize
rag = RAGKnowledgeBase()

# Search
result = rag.search("comment accéder à mon espace client", k=3)

# Output: {"documents": ["...", "...", "..."]}
```

## 📥 Input Format
```json
{"query": "user question"}
```

## 📤 Output Format
```json
{
  "documents": [
    "Question: ... Réponse: ...",
    "Question: ... Réponse: ...",
    "Question: ... Réponse: ..."
  ]
}
```

## ✅ Ready to Integrate
Your RAG module is ready. Other developers can import and use `rag_api.py`

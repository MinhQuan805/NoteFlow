# Backend - NoteFlow API

FastAPI server cung cấp API cho hệ thống RAG và quản lý dữ liệu.

## 📁 Cấu trúc

```
backend/
├── ai/                 # RAG pipeline & AI modules
│   ├── rag_system.py   # Main RAG orchestrator
│   ├── rag_modules.py  # LLM client, embeddings
│   ├── parser.py       # LlamaParse integration
│   ├── pipeline.py     # Ingestion pipeline
│   └── intent_classifer.py
├── routers/            # API endpoints
│   ├── conversations.py
│   ├── files.py
│   ├── notebooks.py
│   └── notes.py
├── schemas/            # Pydantic models
├── config/             # Configuration files
├── main.py             # FastAPI app entry
└── requirements.txt
```

## 🚀 Chạy server

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 8000
```

## 🔑 Environment Variables

Tạo file `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key
LLAMA_PARSE_API_KEY=your_llamaparse_key
MONGO_URI=mongodb://localhost:27017
```

## 📡 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/notebooks/` | Danh sách notebooks |
| POST | `/notebooks/create` | Tạo notebook mới |
| POST | `/files/upload_files/{id}` | Upload và ingest file |
| POST | `/query/{notebookId}/{conversationId}` | Chat với RAG |
| POST | `/generate_slides/...` | Tạo slide tự động |

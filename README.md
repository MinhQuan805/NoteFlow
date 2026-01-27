# NoteFlow 📚

**Personal Document Knowledge Management and Retrieval System**

NoteFlow is a RAG (Retrieval-Augmented Generation) application that enables users to chat with personal documents, organize knowledge by notebooks, and automatically generate presentations.

## ✨ Key Features

- 📁 **Document Management** - Upload PDF, DOCX, TXT, or scrape content from URLs
- 💬 **Intelligent Chat** - Q&A with documents, with source citations
- 🔍 **Hybrid Search** - Combines BM25 (keyword) and Vector Search (semantic)
- 🎯 **Intent Classification** - Automatically categorizes general chat vs RAG-required queries
- 📝 **Note-taking** - Integrated rich text editor (BlockNote)
- 🎨 **Auto Slide Generation** - Creates presentations from documents with KaTeX support

<img width="1919" height="909" alt="2" src="https://github.com/user-attachments/assets/92cb28ff-05ec-47c9-a54f-c1491408dc21" />

## 🏗️ Architecture

<div align="center">
  <img width="500" height="600"  alt="software architecture" src="https://github.com/user-attachments/assets/2dbf964d-78b4-4245-9888-140a2a4caa01" />
</div>

## 📁 Project Structure

```
NoteFlow/
├── backend/                        # FastAPI Server + RAG Pipeline
│   ├── ai/                         # RAG Core Components
│   │   ├── rag_system.py           # Main RAG orchestrator & slide generation
│   │   ├── rag_modules.py          # LLM, embeddings, vector DB wrapper
│   │   ├── rag_manager.py          # Per-notebook RAG instances
│   │   ├── parser.py               # Document parsing (LlamaParse)
│   │   ├── intent_classifier.py    # Query intent classification
│   │   └── config.yaml             # RAG configuration
│   │
│   ├── routers/                    # API Endpoints
│   │   ├── conversationsRouter.py  # Chat & queries
│   │   ├── filesRouter.py          # File upload/ingestion
│   │   ├── notebookRouter.py       # Notebook CRUD
│   │   └── slidesRouter.py         # Slide generation
│   │
│   ├── schemas/                    # Pydantic Models
│   ├── config/database.py          # MongoDB connection
│   ├── data/{notebook_id}/         # Isolated FAISS indexes per notebook
│   ├── main.py                     # FastAPI entry point
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # Next.js 15 Web Application
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   └── (client)/           # Client routes
│   │   │       ├── home/           # Notebook list
│   │   │       └── notebook/[notebookId]/  # Notebook workspace
│   │   │
│   │   ├── components/             # React Components
│   │   │   ├── client/notebook/    # Notebook UI
│   │   │   │   ├── chat/           # Chat interface
│   │   │   │   ├── source/         # File management
│   │   │   │   ├── note/           # Note editor (BlockNote)
│   │   │   │   └── slide/          # Slide viewer
│   │   │   └── ui/                 # Reusable UI components
│   │   │
│   │   ├── hooks/                  # Custom React Hooks
│   │   ├── lib/api/                # API client functions
│   │   ├── schemas/                # TypeScript interfaces
│   │   └── utils/                  # Helper functions
│   │
│   ├── package.json
│   └── .env.local                  # Frontend config
│
└── benchmark/                      # Evaluation & Testing
    ├── dataset/                    # CS224N Q&A markdown files
    ├── result/                     # Benchmark outputs & charts
    ├── run_benchmark.py            # Main evaluation script
    └── benchmark_dataset.csv       # 88 test questions
```

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

### 1. Clone repository
```bash
git clone https://github.com/your-username/NoteFlow.git
cd NoteFlow
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Environment Variables
Create `.env` file in `backend/`:
```env
# LLM
GOOGLE_API_KEY=your_gemini_api_key

# Document Parsing
LLAMA_PARSE_API_KEY=your_llamaparse_api_key

# Database
MONGO_URI=mongodb://localhost:27017
# or MongoDB Atlas connection string

# File Storage (optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run build
npm run start
```

Open your browser at: http://localhost:3000

## 📊 Benchmark

Evaluated on 88 questions from Stanford CS224N:

| Metric | Score |
|--------|-------|
| F1 Score | 33.08% |
| ROUGE-L | 27.68% |
| Contains | 58.13% |
| **Cosine Similarity** | **64.07%** |

> High Cosine Similarity demonstrates the system retrieves correct information, even when the LLM paraphrases using different wording.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 15, TailwindCSS, Radix UI |
| Backend | FastAPI, Python 3.10 |
| Database | MongoDB, FAISS |
| LLM | Gemini or OpenAI models |
| Parsing | LlamaParse |
| Embeddings | all-MiniLM-L6-v2 |

## 📸 User Interface
<div align="center">
  <img width="49%" src="https://github.com/user-attachments/assets/100aaf22-5df5-4aaf-a07d-6bbf9f17ea4d" alt="Notebook List" />
  <img width="49%" src="https://github.com/user-attachments/assets/b2904214-baa1-4cae-a0e5-5d3e700b0dd7" alt="Chat Interface" />
</div>

<div align="center">
  <img width="49%" src="https://github.com/user-attachments/assets/cfaabf54-07fc-4687-ba48-adcdb0640d5d" alt="Document Sources" />
  <img width="49%" src="https://github.com/user-attachments/assets/4a5cd67c-4efc-4dd5-9665-4255d2603fcf" alt="Note Editor" />
</div>

<div align="center">
  <img width="49%" src="https://github.com/user-attachments/assets/497b921d-b04b-4362-a8c3-428543225865" alt="Slide Generation" />
  <img width="49%" src="https://github.com/user-attachments/assets/6efd4d01-f929-4930-944f-dcd7f5a7dded" alt="Slide Viewer" />
</div>


## 👥 Development Team

| Name | Student ID |
|------|------------|
| Nguyễn Quốc Khánh | 24520793 |
| Võ Minh Quân | 24521459 |

**Institution:** University of Information Technology - VNU-HCM

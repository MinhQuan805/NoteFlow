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

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│  Frontend   │────▶│   Backend   │────▶│    AI Services      │
│  Next.js 15 │     │   FastAPI   │     │  Gemini + LlamaParse│
└─────────────┘     └──────┬──────┘     └─────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Database   │
                    │ MongoDB+FAISS│
                    └─────────────┘
```

## 📁 Project Structure

```
NoteFlow/
├── backend/          # FastAPI server + RAG pipeline
├── frontend/         # Next.js 15 web app
├── benchmark/        # Evaluation scripts & dataset
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

## 👥 Development Team

| Name | Student ID |
|------|------------|
| Nguyễn Quốc Khánh | 24520793 |
| Võ Minh Quân | 24521459 |

**Course:** CS311 - Artificial Intelligence Programming Techniques  
**Institution:** University of Information Technology - VNU-HCM
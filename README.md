# NoteFlow 📚

**Hệ thống quản lý và truy xuất tri thức từ tài liệu cá nhân**

NoteFlow là một ứng dụng RAG (Retrieval-Augmented Generation) cho phép người dùng chat với tài liệu cá nhân, tổ chức kiến thức theo Notebook, và tự động tạo bài thuyết trình.

## ✨ Tính năng chính

- 📁 **Quản lý tài liệu** - Upload PDF, DOCX, TXT hoặc cào nội dung từ URL
- 💬 **Chat thông minh** - Hỏi đáp với tài liệu, có trích dẫn nguồn
- 🔍 **Hybrid Search** - Kết hợp BM25 (keyword) và Vector Search (semantic)
- 🎯 **Intent Classification** - Tự động phân loại chat thường vs câu hỏi cần RAG
- 📝 **Ghi chú** - Rich text editor tích hợp (BlockNote)
- 🎨 **Tạo Slide tự động** - Sinh bài thuyết trình từ tài liệu với KaTeX support

## 🏗️ Kiến trúc

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

## 📁 Cấu trúc thư mục

```
NoteFlow/
├── backend/          # FastAPI server + RAG pipeline
├── frontend/         # Next.js 15 web app
├── benchmark/        # Evaluation scripts & dataset
└── report-latex/     # Academic report (Vietnamese)
```

## 🚀 Cài đặt

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local hoặc Atlas)

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
pip install -r requirements.txt
```

### 3. Environment Variables
Tạo file `.env` trong `backend/`:
```env
# LLM
GOOGLE_API_KEY=your_gemini_api_key

# Document Parsing
LLAMA_PARSE_API_KEY=your_llamaparse_api_key

# Database
MONGO_URI=mongodb://localhost:27017
# hoặc MongoDB Atlas connection string

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

Tạo file `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Chạy ứng dụng

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Mở trình duyệt tại: http://localhost:3000

## 📊 Benchmark

Đánh giá trên 88 câu hỏi từ Stanford CS224N:

| Metric | Score |
|--------|-------|
| F1 Score | 33.08% |
| ROUGE-L | 27.68% |
| Contains | 58.13% |
| **Cosine Similarity** | **64.07%** |

> Cosine Similarity cao chứng tỏ hệ thống truy xuất đúng thông tin, dù LLM diễn đạt lại bằng từ ngữ khác.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 15, TailwindCSS, Radix UI |
| Backend | FastAPI, Python 3.10 |
| Database | MongoDB, FAISS |
| LLM | Gemini 2.5 Flash |
| Parsing | LlamaParse |
| Embeddings | all-MiniLM-L6-v2 |

## 👥 Nhóm phát triển

| Họ tên | MSSV |
|--------|------|
| Nguyễn Quốc Khánh | 24520793 |
| Võ Minh Quân | 24521459 |

**Môn học:** CS311 - Kĩ thuật lập trình Trí tuệ nhân tạo  
**Trường:** Đại học Công nghệ Thông tin - ĐHQG TP.HCM

## 📄 License

MIT License - Xem [LICENSE](LICENSE) để biết thêm chi tiết.

# Frontend - NoteFlow Web App

Giao diện người dùng xây dựng với Next.js 15 (App Router).

## 📁 Cấu trúc

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx            # Home - Notebook list
│   └── notebook/[id]/      # Notebook workspace
├── components/             # React components
│   ├── chat/               # Chat interface
│   ├── sources/            # File management
│   └── notes/              # Note editor
├── lib/                    # Utilities
├── store/                  # Redux Toolkit
└── public/                 # Static assets
```

## 🚀 Chạy development server

```bash
# Install dependencies
npm install

# Run dev server
npm run dev
```

Mở http://localhost:3000

## 🔑 Environment Variables

Tạo file `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛠️ Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Styling:** TailwindCSS
- **UI Components:** Radix UI, Shadcn/ui
- **State Management:** Redux Toolkit
- **Rich Text:** BlockNote
- **Math Rendering:** KaTeX

## 📦 Build production

```bash
npm run build
npm start
```

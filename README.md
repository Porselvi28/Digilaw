# ⚖️ DigiLaw

> **Retrieval-Augmented Legal Intelligence for Smart Legal Assistance**

DigiLaw is an AI-powered legal intelligence platform that helps individuals organize, understand, and act on their legal matters. It combines a modern React frontend with a FastAPI backend, using RAG (Retrieval-Augmented Generation) over a curated legal knowledge base to surface relevant laws, analyze evidence, find similar cases, and generate actionable legal guidance.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5+-646CFF?style=flat&logo=vite&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=flat)
![Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=flat&logo=google&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📁 **Case Management** | Create and manage legal cases with full metadata |
| 📄 **Document Upload** | Upload PDF, DOCX, JPG, PNG, TXT — up to 10 MB |
| 🔍 **Smart Text Extraction** | PyMuPDF for PDFs + automatic OCR fallback for scanned pages |
| 🧠 **AI Evidence Analysis** | Gemini AI identifies and classifies key evidence from documents |
| ⚖️ **Legal Relevance Scoring** | RAG-powered relevance scoring against a legal knowledge base |
| 🔗 **Similar Case Matching** | ChromaDB vector search finds comparable case patterns |
| 📋 **Action Plan Generator** | AI-generated, prioritized next-step checklist per case |
| 💬 **Ask DigiLaw** | Conversational AI chat grounded in your case documents |
| 🔐 **Auth & Security** | JWT-based authentication, UUID filenames, MIME validation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend (Vite)                 │
│   Dashboard · Cases · Documents · Evidence · Analysis   │
│         Similar Cases · Action Plan · Ask AI            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────┐
│               FastAPI Backend (Python)                  │
│                                                         │
│  /auth   /cases   /documents   /ask                     │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  PostgreSQL  │  │   ChromaDB   │  │  Google Gemini│  │
│  │  (Cases,     │  │  (Vector     │  │  (RAG / LLM)  │  │
│  │   Docs, Users│  │   Embeddings)│  │               │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  PyMuPDF ──► OCR (Tesseract) ──► Text Chunks            │
│  ──► Embeddings ──► ChromaDB ──► Gemini ──► Response    │
└─────────────────────────────────────────────────────────┘
```

### Document Processing Pipeline

```
Upload (PDF / DOCX / Image / TXT)
        ↓
Validate (extension, MIME type, size ≤ 10 MB)
        ↓
Save to disk (UUID filename)  →  Create DB record
        ↓
Text Extraction
  ├── DOCX / TXT → direct read
  ├── Image      → Tesseract OCR
  └── PDF        → PyMuPDF
                    └── sparse page? → OCR fallback (2× resolution)
        ↓
Evidence Analysis (Gemini AI)
        ↓
Embed text chunks → store in ChromaDB
        ↓
Legal Relevance Score · Similar Cases · Action Plan
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — REST API framework
- **SQLAlchemy + PostgreSQL** — relational database
- **PyMuPDF (fitz)** — PDF text extraction
- **Tesseract / pytesseract** — OCR for scanned documents
- **ChromaDB** — vector store for semantic search
- **Google Gemini** — LLM for analysis, RAG, and chat
- **JWT (python-jose)** — authentication
- **Pydantic v2** — data validation

### Frontend
- **React 18** — UI framework
- **Vite** — build tool & dev server
- **Framer Motion** — animations
- **Lucide React** — icons
- **React Router** — client-side routing

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Tesseract OCR installed on your system
- Google Gemini API key

---

### 1. Clone the Repository

```bash
git clone https://github.com/Porselvi28/Digilaw.git
cd Digilaw
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/digilaw
GEMINI_API_KEY=your_google_gemini_api_key
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run database migrations and start the server:

```bash
# Apply DB schema
python migrate_auth.py
python migrate_documents.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (opens in browser automatically)
npm run dev -- --open
```

App available at: **http://localhost:5173**

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and get JWT token |
| `GET` | `/api/cases` | List all cases for current user |
| `POST` | `/api/cases` | Create a new case |
| `GET` | `/api/cases/{id}` | Get case details |
| `POST` | `/api/documents/upload` | Upload a document to a case |
| `POST` | `/api/documents/{id}/extract` | Extract text from document |
| `POST` | `/api/documents/{id}/analyze-evidence` | AI evidence analysis |
| `POST` | `/api/cases/{id}/legal-relevance` | Score legal relevance |
| `POST` | `/api/cases/{id}/similar-cases` | Find similar cases via vector search |
| `POST` | `/api/cases/{id}/action-plan` | Generate AI action plan |
| `POST` | `/api/ask` | Ask a legal question (RAG chat) |

---

## 📁 Project Structure

```
Digilaw/
├── backend/
│   ├── app/
│   │   ├── database/        # DB connection
│   │   ├── dependencies/    # Auth middleware
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic & AI pipeline
│   │   └── main.py          # FastAPI app entry point
│   ├── uploads/             # Uploaded files (gitignored)
│   ├── chroma_db/           # Vector store (gitignored)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/      # Reusable UI components
    │   ├── context/         # React context (auth, demo)
    │   ├── data/            # Mock data
    │   ├── pages/           # App pages & marketing pages
    │   ├── services/        # API client
    │   └── utils/
    ├── public/
    ├── index.html
    └── package.json
```

---

## ⚠️ Disclaimer

DigiLaw is a **legal intelligence and organization tool** — not a substitute for professional legal advice. All AI-generated content (analysis, references, action plans) should be verified by a qualified legal professional before relying on it for important decisions.

---

## 👥 Team

Built with ❤️ for the purpose of making legal information more accessible.

---

## 📄 License

This project is for educational and demonstration purposes.

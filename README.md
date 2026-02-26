# InsightX

**AI-powered natural language analytics for Indian UPI transaction data.**

InsightX lets you ask questions in plain English — or by voice or image — and get instant database insights, powered by Vanna AI (Text-to-SQL), Groq LLM, and a local SQLite database of UPI transactions.

---

## ✨ Features

- 🖥️ **React Dashboard**: Modern chat UI built with React, Vite, shadcn/ui, and Tailwind CSS.
- 👁️ **OCR / Image Analysis**: Upload a chart or screenshot — EasyOCR extracts the text and queries the database.
- 🎤 **Voice-to-SQL**: Speak your question, get data. Powered by local OpenAI Whisper.
- 💡 **Smart Analytics**: AI-powered executive summaries and follow-up suggestions via Groq LLM.
- 📊 **Real-time Execution**: Natural language → SQL → live SQLite results, displayed as tables or charts.
- 🎯 **Fully Local**: Whisper, ChromaDB, and EasyOCR all run on your machine — no data leaves your system.
- 🔄 **Dual-AI Pipeline**: Vanna (Text-to-SQL) + Groq LLaMA 3.3 (Synthesis) in one pipeline.

---

## Project Structure

```
Insightx-/
├── backend/
│   ├── app/
│   │   └── main.py                    # FastAPI (Vanna AI + Groq + Whisper + EasyOCR)
│   ├── scripts/
│   │   ├── train_vanna.py             # Train Vanna on DB schema & examples
│   │   ├── demo_vanna.py              # CLI demo for testing Vanna queries
│   │   ├── evaluate_vanna.py          # Evaluation script
│   │   ├── speech_to_text.py          # Voice-to-text using Whisper (local)
│   │   └── ocr_easyocr.py             # OCR using EasyOCR (local)
│   ├── data/                          # SQLite DB + CSV datasets (git-ignored)
│   ├── vector_store/                  # ChromaDB vector embeddings (git-ignored)
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── lib/api.ts                 # Typed API client (ask / voice-ask / ocr-ask)
│   │   ├── pages/
│   │   │   ├── Index.tsx              # Landing page
│   │   │   └── Dashboard.tsx          # Main chat interface (live API)
│   │   └── components/
│   │       ├── ChatMessage.tsx        # Message renderer with follow-ups & SQL disclosure
│   │       └── DataVisualizer.tsx     # Table / Chart / KPI renderer
│   ├── vite.config.ts                 # Dev server with /api proxy → localhost:8000
│   └── package.json
├── .gitignore
├── LICENSE
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Groq API Key — get free at [console.groq.com](https://console.groq.com)
- UPI transaction SQLite database in `backend/data/`

### 1. Backend Setup
```bash
cd backend

# Create .env
echo GROQ_API_KEY=your_key_here > .env
echo GROQ_MODEL=llama-3.3-70b-versatile >> .env

# Install dependencies
pip install -r requirements.txt

# Train Vanna (first time only)
python scripts/train_vanna.py

# Start backend API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend: **http://localhost:8000** | Swagger docs: **http://localhost:8000/docs**

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```
Frontend: **http://localhost:8080**

> The Vite dev server automatically proxies all `/api/*` requests to `http://localhost:8000`, so no CORS configuration is needed.

---

## API Endpoints

### `GET /`
Health check. Returns `{"status": "ok"}`.

### `POST /api/ask`
Text query through the full Dual-AI pipeline.

**Request:**
```json
{ "question": "What is the total UPI transaction volume by bank?" }
```

**Response:**
```json
{
  "question": "...",
  "sql": "SELECT bank, SUM(amount) FROM upi_transactions GROUP BY bank",
  "data": [{"bank": "SBI", "amount": 1500000}],
  "answer": "SBI led with ₹15 lakh in UPI transactions...",
  "follow_up_questions": ["Show trends by month", "Which bank had the most transactions?"]
}
```

### `POST /api/voice-ask`
Upload audio → Whisper transcription → full pipeline.

**Request:** `multipart/form-data` with `audio` file (`.webm`, `.wav`, `.mp3`).

**Response:** Same as `/api/ask` + `"transcription": "..."`.

### `POST /api/ocr-ask`
Upload image → EasyOCR text extraction → Groq interpretation → full pipeline.

**Request:** `multipart/form-data` with:
- `image` — image file (`.jpg`, `.png`, `.webp`)
- `text` *(optional)* — additional context or constraint (e.g. "focus on Q3")

**Response:** Same as `/api/ask` + `"ocr_text": "..."`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI, Python 3.10+ |
| Text-to-SQL | Vanna AI + local ChromaDB vector store |
| LLM | Groq LLaMA 3.3 70B (SQL generation + executive summaries) |
| Speech | OpenAI Whisper (local, no API key) |
| OCR | EasyOCR (local, CPU-based) |
| Database | SQLite (UPI transactions) |
| Animations | Framer Motion |

---

## Environment Variables

Create `.env` in `backend/`:

```env
# Required
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Optional
WHISPER_MODEL=base           # tiny / base / small / medium / large
DB_PATH=data/upi_transactions.db
VECTOR_STORE_PATH=vector_store/
```

Get your free Groq API key: https://console.groq.com

---

## Architecture

```
User Input (Text / Voice / Image)
         │
         ├── Text  ──────────────────────────────────────────────────────────┐
         │                                                                   │
         ├── Voice ── Whisper (local) ── Transcription ─────────────────────┤
         │                                                                   │
         └── Image ── EasyOCR (local) ── Raw Text ── Groq (interpret) ──────┤
                                                                             │
                                                            ┌────────────────▼───────────────┐
                                                            │   Vanna AI  (Text → SQL)       │
                                                            │   ChromaDB  (vector lookup)    │
                                                            └────────────────┬───────────────┘
                                                                             │
                                                            ┌────────────────▼───────────────┐
                                                            │   SQLite Execution             │
                                                            └────────────────┬───────────────┘
                                                                             │
                                                            ┌────────────────▼───────────────┐
                                                            │   Groq LLaMA 3.3               │
                                                            │   Executive Summary + Follow-ups│
                                                            └────────────────┬───────────────┘
                                                                             │
                                                            ┌────────────────▼───────────────┐
                                                            │   React Dashboard              │
                                                            │   Table / Chart / Answer       │
                                                            └────────────────────────────────┘
```

---

## License

MIT

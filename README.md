# InsightX

**AI-powered natural language analytics for Indian UPI transaction data.**

InsightX lets you ask questions in plain English and get instant insights — powered by Vanna AI (Text-to-SQL), Groq LLM, and a local SQLite database of UPI transactions. Includes **Speech-to-Text** support for hands-free queries!

---

## ✨ Features

- 👁️ **OCR / Image Analysis**: Extract text from images (charts, reports) and query data based on it.
- 🎤 **Voice-to-SQL**: Full voice interaction pipeline (Speak → Text → SQL → Answer).
- 💡 **Smart Analytics**: AI-powered insights and follow-up suggestions via Groq LLM.
- 📊 **Real-time Execution**: Execute queries against local SQLite database instantly.
- 🎯 **No External Dependencies**: All ML models run locally (Whisper, ChromaDB, Groq)
- 🔄 **Dual-AI Pipeline**: Combines Text-to-SQL + LLM synthesis for comprehensive answers

---

## Project Structure

```
Insightx-/
├── backend/
│   ├── app/
│   │   └── main.py                    # FastAPI backend (Vanna AI + Groq LLM)
│   ├── scripts/
│   │   ├── train_vanna.py             # Train Vanna on DB schema & examples
│   │   ├── demo_vanna.py              # CLI demo for testing Vanna queries
│   │   ├── evaluate_vanna.py          # Evaluation script
│   │   ├── speech_to_text.py          # Voice-to-text using Whisper (local)
│   │   └── ocr_easyocr.py             # OCR using EasyOCR (local)
│   ├── data/                          # SQLite DB + CSV datasets (git-ignored)
│   ├── vector_store/                  # ChromaDB vector embeddings (git-ignored)
│   ├── notebooks/
│   │   └── feature_engineering.ipynb  # Data exploration & analysis
│   ├── eval_report.json               # Evaluation metrics
│   └── requirements.txt               # Python dependencies
├── frontend/                          # (Empty - ready for UI framework)
├── .gitignore
├── LICENSE
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key (get free at [console.groq.com](https://console.groq.com))
- UPI transaction SQLite database

### 1. Navigate to Backend
```bash
cd backend
```

### 2. Create Environment File
Create `.env` in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train Vanna (First Time Only)
Trains the AI on your database schema and SQL examples:
```bash
python scripts/train_vanna.py
```

### 5. Start the API Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: **http://localhost:8000**

### 6. Start the Frontend (UI)
```bash
cd frontend
chainlit run app.py -w --port 8002
```
The UI will be available at: **http://localhost:8002**

### 7. Test the API
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total transaction volume?"}'
```

Or use the interactive docs at: **http://localhost:8000/docs**

## API Endpoints

### Health Check
**`GET /`**
- Returns API status
- Response: `{"status": "ok"}`

### Ask a Question (Main Endpoint)
**`POST /api/ask`**
- Converts natural language to SQL using Vanna AI
- Executes SQL and generates an executive summary using Groq LLM
- Returns SQL query, results, answer, and follow-up suggestions

**Request:**
```json
{
  "question": "What is the total UPI transaction volume by bank?"
}
```

**Response:**
```json
{
  "sql": "SELECT bank, SUM(amount) FROM transactions GROUP BY bank",
  "data": [
    {"bank": "SBI", "amount": 1500000},
    {"bank": "ICICI", "amount": 2300000}
  ],
  "answer": "SBI processed $1.5M and ICICI processed $2.3M in UPI transactions.",
  "follow_up_questions": [
    "What is the transaction count by bank?",
    "Show me trends over time"
  ]
}
```

### Voice Query
**`POST /api/voice-ask`**
- Accepts audio file upload (`.wav`, `.webm`, `.mp3`).
- Transcribes audio locally using Whisper.
- Executes the full analysis pipeline.
- **Request**: `multipart/form-data` with `audio` file.

### OCR / Image Query
**`POST /api/ocr-ask`**
- Accepts image file upload (`.jpg`, `.png`).
- Optional `text` field for specific user instructions.
- Extracts text → Interprets with Groq → Generates SQL.
- **Request**: `multipart/form-data` with `image` file and optional `text` string.

## Tech Stack

- **FastAPI** — High-performance async API framework
- **Vanna AI** — Text-to-SQL with local ChromaDB vector store
- **Groq LLaMA 3.3 70B** — Open-source LLM for SQL generation & summaries
- **ChromaDB** — Vector database for semantic search
- **SQLite** — Embedded database for UPI transactions
- **EasyOCR** — Optical Character Recognition for images
- **OpenAI Whisper** — Local speech recognition (no API key required)
- **SoundDevice** — Microphone audio capture
- **Pandas** — Data processing and transformation

## Scripts

### `train_vanna.py`
Trains Vanna AI on your database schema:
```bash
python scripts/train_vanna.py
```
- Creates ChromaDB embeddings of your database schema
- Trains on SQL examples and business rules
- Must run before the API is functional

### `demo_vanna.py`
Quick command-line demo for testing Vanna:
```bash
python scripts/demo_vanna.py
```

### `evaluate_vanna.py`
Evaluates Vanna's SQL generation accuracy:
```bash
python scripts/evaluate_vanna.py
```

### `speech_to_text.py` (NEW)
Convert voice queries to text using local Whisper model:
```bash
python scripts/speech_to_text.py
```
**Features:**
- Real-time microphone recording
- Supports multiple Whisper model sizes (tiny, base, small, medium, large)
- No API key required — runs entirely locally
- Configurable recording duration
- Returns transcribed text ready for SQL generation

### `ocr_easyocr.py` (NEW)
Extract text from images using EasyOCR:
```bash
python scripts/ocr_easyocr.py path/to/image.png --detailed
```
**Features:**
- Runs locally (CPU/GPU)
- Preprocessing for rotation and contrast
- Outputs raw text or JSON with confidence scores

## Architecture

### Dual Pipeline Support

**Option 1: Voice Query (Speech-to-Text)**
```
Microphone Audio
    ↓
OpenAI Whisper (Local)
    ↓
Transcribed Text
    ↓
[Proceed with Option 2 below]
```

**Option 2: Text Query**
```
User Question (Text)
    ↓
Vanna AI (Text-to-SQL via ChromaDB + Groq)
    ↓
Generated SQL Query
    ↓
SQLite Execution
    ↓
Query Results (Data)
    ↓
Groq LLM (Executive Summary + Follow-ups)
    ↓
Unified JSON Response
    ↓
Frontend/Client
```

**Combined Pipeline:**
```
Voice Input (Optional)
    ├─→ Whisper (Speech-to-Text)
    ↓
Text Question
    ↓
Vanna (Text-to-SQL) + Groq (LLM)
    ↓
SQL Generation & Execution
    ↓
Data Processing & Synthesis
    ↓
Final Response (SQL + Data + Answer + Follow-ups)
```

## Environment Variables

Create `.env` file in `backend/`:

```env
# Groq LLM Configuration
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Optional: Custom DB path (defaults to data/upi_transactions.db)
# DB_PATH=/path/to/custom.db
```

Get your free Groq API key: https://console.groq.com

## Speech-to-Text Setup (Optional)

For voice query support, install additional dependencies:

```bash
pip install sounddevice numpy openai-whisper
```

**Whisper Model Sizes:**
| Model | Size | Speed | Accuracy | VRAM |
|-------|------|-------|----------|------|
| tiny | 39M | ⚡⚡⚡ Fast | ◯ Fair | ~1GB |
| base | 140M | ⚡⚡ Good | ◐ Good | ~1GB |
| small | 244M | ⚡ Slower | ◉ Better | ~2GB |
| medium | 769M | — | ◉◉ Excellent | ~5GB |
| large | 2.9GB | Slow | ◉◉◉ Best | ~10GB |

**Quick Voice Query:**
```python
from scripts.speech_to_text import SpeechToText

stt = SpeechToText(model_name="base")
audio_text = stt.record_and_transcribe(duration=5)
print(f"You said: {audio_text}")

# Then feed to API
# requests.post("http://localhost:8000/api/ask", json={"question": audio_text})
```

## License

MIT

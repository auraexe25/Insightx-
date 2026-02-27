<p align="center">
  <img src="https://img.shields.io/badge/InsightX-Agentic_AI_Analytics-7c3aed?style=for-the-badge" alt="InsightX" />
</p>

<h1 align="center">InsightX</h1>

<p align="center">
  <b>AI-powered natural language analytics platform for Indian UPI transaction data.</b><br/>
  Ask questions in plain English — or by voice, or image — and get instant database insights.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/node-18+-green?logo=nodedotjs" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/React-18-61dafb?logo=react" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 💬 **Natural Language Queries** | Ask questions in plain English — Vanna AI converts them to SQL automatically |
| 🎤 **Voice Input** | Speak your question — local Whisper STT transcribes and queries the database |
| 📸 **Image / OCR Input** | Upload a chart or screenshot — EasyOCR extracts text and formulates a query |
| 🤖 **Dual-AI Pipeline** | Vanna AI (Text-to-SQL) + Groq LLaMA 3.3 70B (executive summaries & follow-ups) |
| 📊 **Live Data Visualization** | Results displayed as interactive tables, charts, and KPI cards |
| 🧠 **Chat Memory** | Full conversation history persisted in SQLite — survives page reloads and browser restarts |
| 💡 **Smart Follow-ups** | AI-generated follow-up questions grounded strictly in the database schema — no hallucinated columns |
| 🎯 **Intent Guardrail** | Groq-powered intent classification prevents Vanna from generating SQL for greetings or off-topic input |
| 🔒 **Fully Local Processing** | Whisper, ChromaDB, EasyOCR, and SQLite all run on your machine — no data leaves your system |
| 🗂️ **Session Management** | Create, switch, and delete chat sessions — full sidebar with real-time history |

---

## 📸 Screenshots

> *Add screenshots of your running app here.*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                   │
│                  Text  /  Voice  /  Image                           │
└──────────┬──────────────────┬──────────────────┬────────────────────┘
           │                  │                  │
           │            ┌─────▼─────┐      ┌─────▼──────┐
           │            │  Whisper   │      │  EasyOCR   │
           │            │  (local)   │      │  (local)   │
           │            └─────┬─────┘      └─────┬──────┘
           │                  │                   │
           │            Transcription        Raw Text
           │                  │                   │
           │                  │             ┌─────▼──────┐
           │                  │             │ Groq LLM   │
           │                  │             │ (interpret) │
           │                  │             └─────┬──────┘
           │                  │                   │
           ▼                  ▼                   ▼
     ┌─────────────────────────────────────────────────┐
     │           Intent Guardrail (Groq)               │
     │  Classifies: Data question? YES → Vanna         │
     │                              NO  → Conversational│
     └──────────────────────┬──────────────────────────┘
                            │
               ┌────────────▼────────────┐
               │   Vanna AI              │
               │   ChromaDB (vectors)    │
               │   → SQL Generation      │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   SQLite Execution      │
               │   upi_transactions.db   │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   Groq LLaMA 3.3 70B   │
               │   • Executive Summary   │
               │   • Schema-grounded     │
               │     Follow-up Questions │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   Chat History DB       │
               │   chat_history.db       │
               │   (auto-save session)   │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   React Dashboard       │
               │   Table / Chart / KPI   │
               │   Follow-up Buttons     │
               └─────────────────────────┘
```

---

## 📂 Project Structure

```
Insightx-/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI server (10 endpoints, dual-AI pipeline)
│   │   └── chat_db.py                   # SQLite chat history (sessions + messages CRUD)
│   ├── scripts/
│   │   ├── train_vanna.py               # Train Vanna on DB schema + example queries (439 lines)
│   │   ├── demo_vanna.py                # CLI demo for testing Vanna text-to-SQL
│   │   ├── evaluate_vanna.py            # Accuracy evaluation harness for Vanna
│   │   ├── speech_to_text.py            # Standalone Whisper STT utility
│   │   ├── ocr_easyocr.py              # EasyOCR extraction module
│   │   ├── generate_test_image.py       # Generates test images for OCR testing
│   │   ├── test_ocr_endpoint.py         # Test script for /api/ocr-ask
│   │   └── test_ocr_with_text.py        # Test script for OCR + text context
│   ├── data/
│   │   ├── upi_transactions.db          # SQLite database (250,000 transactions)
│   │   └── chat_history.db              # Chat session history (auto-created)
│   ├── vector_store/                    # ChromaDB vector embeddings (auto-created by train_vanna.py)
│   ├── notebooks/                       # Jupyter notebooks for exploration
│   ├── .env                             # Environment variables (git-ignored)
│   ├── .env.example                     # Template for environment variables
│   ├── requirements.txt                 # Python dependencies (19 packages)
│   └── eval_report.json                 # Vanna evaluation results
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                      # Root component with React Router
│   │   ├── main.tsx                     # Vite entry point
│   │   ├── index.css                    # Global styles (glassmorphism, animations, dark theme)
│   │   ├── lib/
│   │   │   └── api.ts                   # Typed API client (askQuestion, voiceAsk, ocrAsk, sessions)
│   │   ├── pages/
│   │   │   ├── Index.tsx                # Landing page
│   │   │   ├── Dashboard.tsx            # Main chat interface (session-aware, ~340 lines)
│   │   │   └── NotFound.tsx             # 404 page
│   │   ├── components/
│   │   │   ├── DashboardSidebar.tsx     # Session sidebar (live API, delete, navigate)
│   │   │   ├── ChatMessage.tsx          # Message renderer (follow-ups, SQL disclosure, export)
│   │   │   ├── DataVisualizer.tsx       # Table / Line / Bar / Pie chart / KPI renderer
│   │   │   ├── NavLink.tsx              # Navigation link component
│   │   │   └── ui/                      # 49 shadcn/ui components (button, dialog, toast, etc.)
│   │   ├── hooks/                       # Custom React hooks
│   │   └── test/                        # Vitest test files
│   ├── vite.config.ts                   # Dev server (port 8080, /api proxy → 8000)
│   ├── package.json                     # Node dependencies
│   ├── tailwind.config.ts               # Tailwind CSS configuration
│   ├── tsconfig.json                    # TypeScript configuration
│   └── postcss.config.js               # PostCSS configuration
│
├── .gitignore                           # Git ignore rules
├── LICENSE                              # MIT License (Copyright 2026 Atul)
└── README.md                            # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Groq API Key** — free at [console.groq.com](https://console.groq.com)
- **Google Gemini API Key** — free at [aistudio.google.com](https://aistudio.google.com) *(only needed for training Vanna)*
- **FFmpeg** — required by Whisper for audio processing ([ffmpeg.org](https://ffmpeg.org))

### 1. Clone the Repository

```bash
git clone https://github.com/atulbhaskar1034/Insightx-.git
cd Insightx-
```

### 2. Backend Setup

```bash
cd backend

# Create environment file
cp .env.example .env
# Edit .env and add your API keys:
#   GROQ_API_KEY=your_groq_key
#   GEMINI_API_KEY=your_gemini_key    (for training only)

# Install Python dependencies
pip install -r requirements.txt

# Train Vanna AI (first time only — takes ~2 minutes)
python scripts/train_vanna.py

# Start the backend API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend starts at **http://localhost:8000**. Swagger API docs are available at **http://localhost:8000/docs**.

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm run dev
```

The frontend starts at **http://localhost:8080**. It automatically proxies all `/api/*` requests to the backend at `localhost:8000`.

### 4. Open in Browser

Navigate to **http://localhost:8080** → Click **"Try InsightX"** → Start asking questions!

---

## 🔌 API Endpoints

### Core Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ask` | Text query → Vanna SQL → Groq summary → JSON response |
| `POST` | `/api/voice-ask` | Audio upload → Whisper transcription → full pipeline |
| `POST` | `/api/ocr-ask` | Image upload → EasyOCR → Groq interpretation → full pipeline |
| `POST` | `/api/transcribe` | Audio → text only (no query execution) |

### Chat Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/sessions` | List all chat sessions (newest first) |
| `POST` | `/api/sessions` | Create a new empty session |
| `GET` | `/api/sessions/{id}/messages` | Get all messages for a session |
| `DELETE` | `/api/sessions/{id}` | Delete a session and all its messages |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check → `{"status": "ok"}` |

---

### Request / Response Examples

#### `POST /api/ask`

**Request:**
```json
{
  "question": "Which bank has the highest transaction volume?",
  "chat_history": [
    {"role": "user", "content": "Show total transactions"},
    {"role": "assistant", "content": "There are 250,000 total transactions."}
  ],
  "session_id": "a1b2c3d4e5f6"
}
```

**Response:**
```json
{
  "question": "Which bank has the highest transaction volume?",
  "sql": "SELECT sender_bank, COUNT(*) as txn_count FROM transactions GROUP BY sender_bank ORDER BY txn_count DESC LIMIT 1",
  "data": [{"sender_bank": "SBI", "txn_count": 35412}],
  "answer": "SBI leads with 35,412 transactions, accounting for 14.2% of all UPI activity.",
  "follow_up_questions": [
    "What is the average amount_inr for SBI transactions?",
    "How does SBI's transaction volume compare on weekends vs weekdays?",
    "What is the fraud_flag rate for sender_bank = 'SBI'?"
  ]
}
```

#### `POST /api/voice-ask`

**Request:** `multipart/form-data` with `audio` field (.webm, .wav, .mp3, .ogg, .m4a)

**Response:** Same as `/api/ask` + `"transcription": "which bank has the most transactions"`

#### `POST /api/ocr-ask`

**Request:** `multipart/form-data` with:
- `image` — `.jpg`, `.png`, `.webp`, `.bmp`
- `text` *(optional)* — additional context (e.g. "focus on failed transactions")

**Response:** Same as `/api/ask` + `"ocr_text": "...", "original_question": "..."`

---

## 🗄️ Database Schema

### `upi_transactions.db` — Transaction Data (250,000 rows)

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `transaction_id` | TEXT | Unique transaction ID | `TXN0000000001` |
| `timestamp` | TEXT | Transaction datetime | `2024-10-08 15:17:28` |
| `transaction_type` | TEXT | Type of transaction | `P2P`, `P2M`, `Bill Payment`, `Recharge` |
| `merchant_category` | TEXT | Merchant category (NULL for P2P) | `Food`, `Grocery`, `Shopping`, `Fuel`, `Utilities`, `Entertainment`, `Healthcare`, `Transport`, `Education`, `Other` |
| `amount_inr` | INTEGER | Amount in Indian Rupees | `100` – `50000` |
| `transaction_status` | TEXT | Transaction outcome | `SUCCESS`, `FAILED` |
| `sender_age_group` | TEXT | Sender's age bracket | `18-25`, `26-35`, `36-45`, `46-55`, `56+` |
| `receiver_age_group` | TEXT | Receiver's age bracket (NULL for non-P2P) | Same as sender |
| `sender_state` | TEXT | Sender's Indian state | `Delhi`, `Maharashtra`, `Karnataka`, ... |
| `sender_bank` | TEXT | Sender's bank | `SBI`, `HDFC`, `ICICI`, `Axis`, `Kotak`, `PNB`, `Yes Bank`, `IndusInd` |
| `receiver_bank` | TEXT | Receiver's bank | Same as sender_bank |
| `device_type` | TEXT | Device used | `Android`, `iOS`, `Web` |
| `network_type` | TEXT | Network connection | `3G`, `4G`, `5G`, `WiFi` |
| `fraud_flag` | INTEGER | Fraud indicator | `0` (not fraud), `1` (fraud) |
| `hour_of_day` | INTEGER | Hour (24h format) | `0` – `23` |
| `day_of_week` | TEXT | Day name | `Monday` – `Sunday` |
| `is_weekend` | INTEGER | Weekend flag | `0` (weekday), `1` (weekend) |
| `day_part` | TEXT | Part of day | `Morning`, `Afternoon`, `Evening`, `Night` |
| `amount_tier` | TEXT | Amount classification | `Small (<₹500)`, `Medium (₹500-5000)`, `Large (₹5000-50000)` |
| `sender_age_label` | TEXT | Age classification | `Young (18-25)`, `Adult (26-55)`, `Old (56+)` |
| `receiver_age_label` | TEXT | Receiver age label (NULL for non-P2P) | Same as sender |

### `chat_history.db` — Chat Sessions (auto-created)

**`sessions` table:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT (PK) | 12-character hex session ID |
| `title` | TEXT | Auto-generated from first question |
| `created_at` | TEXT | ISO 8601 timestamp |
| `updated_at` | TEXT | Last activity timestamp |

**`messages` table:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment message ID |
| `session_id` | TEXT (FK) | References sessions.id (CASCADE delete) |
| `role` | TEXT | `user` or `assistant` |
| `content` | TEXT | Message text |
| `sql_text` | TEXT | Generated SQL (assistant only) |
| `data_json` | TEXT | Full response JSON (assistant only) |
| `created_at` | TEXT | ISO 8601 timestamp |

---

## 🛠️ Tech Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | **FastAPI** 0.110+ | Async API server with auto-generated Swagger docs |
| Text-to-SQL | **Vanna AI** 0.7+ | Converts natural language to SQL using vector similarity |
| Vector Store | **ChromaDB** 0.4+ | Local vector database for Vanna's training data |
| LLM (Runtime) | **Groq** — LLaMA 3.3 70B | SQL generation, executive summaries, follow-ups, intent classification |
| LLM (Training) | **Google Gemini** 2.0 Flash | Used only during `train_vanna.py` |
| Speech-to-Text | **OpenAI Whisper** (local) | Audio transcription — no API key needed |
| OCR | **EasyOCR** 1.7+ | Image text extraction — CPU-based, no GPU required |
| Database | **SQLite** | Transaction data + chat history |
| Data Processing | **Pandas** 2.0+, **NumPy** 1.24+ | DataFrame operations and data formatting |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | **React 18** + **TypeScript** | Component-based UI with full type safety |
| Build Tool | **Vite 5** | Fast HMR dev server with API proxy |
| UI Library | **shadcn/ui** (49 components) | Radix UI primitives with Tailwind styling |
| Styling | **Tailwind CSS 3.4** | Utility-first CSS with custom dark theme |
| Charts | **Recharts** 2.15 | Line, bar, and pie chart visualizations |
| Animations | **Framer Motion** 12 | Page transitions, message animations, loading states |
| Icons | **Lucide React** | 1000+ SVG icons |
| Routing | **React Router 6** | Client-side routing with session URL params |
| State | **TanStack React Query** | Server state management |
| Notifications | **Sonner** | Toast notifications |

---

## ⚙️ Environment Variables

Create a `.env` file in `backend/` (use `.env.example` as template):

```env
# ─── Required ────────────────────────────────────────────────

# Groq API Key (used by the runtime API server)
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini API Key (used ONLY by scripts/train_vanna.py)
GEMINI_API_KEY=your_gemini_api_key_here

# ─── Optional ────────────────────────────────────────────────

# LLM model names
GROQ_MODEL=llama-3.3-70b-versatile        # Default Groq model
GEMINI_MODEL=gemini-2.0-flash             # Default Gemini model (training only)

# Whisper model size: tiny / base / small / medium / large
WHISPER_MODEL=base                         # Larger = more accurate but slower
```

### Where to Get API Keys

| Key | URL | Free Tier |
|-----|-----|-----------|
| Groq API Key | [console.groq.com](https://console.groq.com) | ✅ Free (rate-limited) |
| Gemini API Key | [aistudio.google.com](https://aistudio.google.com) | ✅ Free |

---

## 🧪 Scripts Reference

All scripts are in `backend/scripts/` and should be run from the `backend/` directory.

| Script | Command | Description |
|--------|---------|-------------|
| `train_vanna.py` | `python scripts/train_vanna.py` | Trains Vanna AI on the DB schema, column descriptions, and 100+ example question-SQL pairs. **Run once after setup.** |
| `demo_vanna.py` | `python scripts/demo_vanna.py` | Interactive CLI to test Vanna text-to-SQL without the web UI |
| `evaluate_vanna.py` | `python scripts/evaluate_vanna.py` | Runs an evaluation suite against Vanna and generates `eval_report.json` |
| `speech_to_text.py` | `python scripts/speech_to_text.py` | Standalone Whisper transcription utility |
| `ocr_easyocr.py` | *(imported by main.py)* | EasyOCR text extraction module |

---

## 🖥️ Frontend Components

| Component | File | Description |
|-----------|------|-------------|
| **Dashboard** | `pages/Dashboard.tsx` | Main chat interface — session-aware, loads messages from DB, auto-creates sessions, sends `session_id` with every query |
| **DashboardSidebar** | `components/DashboardSidebar.tsx` | Left sidebar — fetches real sessions from API, click to switch, hover to delete, shows relative timestamps |
| **ChatMessage** | `components/ChatMessage.tsx` | Renders user/AI messages — includes follow-up buttons, SQL disclosure (collapsible), and JSON export |
| **DataVisualizer** | `components/DataVisualizer.tsx` | Renders data as tables (with ₹ formatting), line/bar/pie charts (Recharts), or KPI cards |
| **Landing Page** | `pages/Index.tsx` | Hero page with feature highlights and CTA to Dashboard |

---

## 🧠 How It Works

### 1. User Sends a Query
The user types a question, records voice, or uploads an image via the React dashboard.

### 2. Input Processing
- **Text** → sent directly to the pipeline
- **Voice** → Whisper (local) transcribes to text → sent to pipeline
- **Image** → EasyOCR extracts text → Groq interprets and formulates a database question → sent to pipeline

### 3. Intent Classification
Groq classifies whether the input is a data question (`YES`) or conversational (`NO`).
- **YES** → proceeds to Vanna AI for SQL generation
- **NO** → returns a friendly conversational reply with chat history context

### 4. SQL Generation & Execution
Vanna AI uses ChromaDB vector similarity to find relevant training examples, then generates SQL. The SQL is executed against the local SQLite database.

### 5. Synthesis
The query results are sent to Groq LLaMA 3.3 70B with:
- The full database schema
- The user's chat history (last 3 turns)
- Strict rules for follow-up question generation

Groq returns a JSON with an executive summary and 3 schema-grounded follow-up questions.

### 6. Persistence
If a `session_id` is provided, both the user question and AI response are saved to `chat_history.db`. The session title is auto-set from the first question.

### 7. Display
The React dashboard renders the response as a table/chart with the executive summary, follow-up buttons, and collapsible SQL disclosure.

---

## 📋 Example Queries

Here are some questions you can ask InsightX:

```
Show total UPI transaction volume
Which bank has the most transactions?
Top 5 transactions by amount
What is the fraud rate by transaction type?
Show spending trends by day of week
Which age group uses P2P transfers most?
Average transaction amount for each merchant category
How many failed transactions happened on weekends?
What is the distribution of transactions by network type?
Compare SBI vs HDFC transaction volumes
Which state has the highest average transaction amount?
Show hourly transaction pattern for Sundays
```

---

## 🔧 Development

### Running Tests

```bash
# Frontend unit tests
cd frontend
npm test

# Frontend test watch mode
npm run test:watch

# Backend evaluation
cd backend
python scripts/evaluate_vanna.py
```

### Building for Production

```bash
# Frontend production build
cd frontend
npm run build

# Output → frontend/dist/
```

### Linting

```bash
cd frontend
npm run lint
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Create `backend/.env` with your API key (see `.env.example`) |
| `ModuleNotFoundError: whisper` | Install with `pip install openai-whisper` and ensure FFmpeg is in PATH |
| `database is locked` | Ensure only one instance of the backend is running |
| `Vanna generates wrong SQL` | Re-run `python scripts/train_vanna.py` to retrain with more examples |
| Frontend shows `502 Bad Gateway` | Ensure the backend is running on port 8000 |
| `EasyOCR init failed` | Install with `pip install easyocr` — first run downloads ~100MB model |
| CORS errors in browser | The Vite proxy handles this automatically — ensure you're accessing `localhost:8080`, not `8000` |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Atul

---

## 🙏 Acknowledgments

- [Vanna AI](https://vanna.ai) — Text-to-SQL framework
- [Groq](https://groq.com) — Ultra-fast LLM inference
- [OpenAI Whisper](https://github.com/openai/whisper) — Speech recognition
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — Optical character recognition
- [ChromaDB](https://www.trychroma.com) — Vector database
- [shadcn/ui](https://ui.shadcn.com) — React component library
- [Recharts](https://recharts.org) — Chart library

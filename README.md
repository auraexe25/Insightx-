<div align="center">
  <img src="https://img.shields.io/badge/InsightX-Agentic_AI_Analytics-7c3aed?style=for-the-badge&logoColor=white" alt="InsightX" />

  <h1>InsightX</h1>

  <p>
    <b>The Elite AI-Powered Analytics & Executive Reporting Platform for UPI Data</b><br/>
    Ask questions in plain English, by voice, or by image upload — get instant executed SQL, dynamic visualizations, and 1-click corporate PDF reports.
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Node.js-18+-green?logo=nodedotjs&logoColor=white" alt="Node" />
    <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=black" alt="React" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white" alt="Tailwind" />
  </p>
</div>

---

## 📸 Demo Showcase
<img width="1901" height="970" alt="Image" src="https://github.com/user-attachments/assets/c0093ecb-19c0-4fb4-8c41-f52f31caa575" />

<img width="1919" height="975" alt="Image" src="https://github.com/user-attachments/assets/dcb43cf5-920f-4bc1-81c6-8ea906d3e785" />

<img width="1339" height="983" alt="Image" src="https://github.com/user-attachments/assets/7e604951-6cbf-4dd6-b389-8b2dfef7f9d2" />

<img width="1395" height="975" alt="Image" src="https://github.com/user-attachments/assets/4a6e4964-6069-4682-904a-7188f3a14825" />

<img width="1538" height="976" alt="Image" src="https://github.com/user-attachments/assets/177eb71a-ecb8-481f-b6a8-2dd16d5740a3" />





---

## ✨ Elite Features

| Feature | Description |
|---------|-------------|
| 💬 **Natural Language Queries** | Ask questions in plain English — Vanna AI converts them to SQL automatically. |
| 📄 **1-Click Board Reports** | Click one button to export your active chat session into a clean, light-themed, professional executive **PDF document** (powered by `html2pdf.js`). |
| 🎤 **Voice Input** | Speak your question — local Whisper STT transcribes and queries the database via microphone. |
| 📸 **Image / OCR Input** | Upload a chart or screenshot — EasyOCR extracts text and Groq formulates a database query. |
| 🤖 **Dual-AI Pipeline** | Vanna AI (Text-to-SQL) + Groq LLaMA 3.3 70B (executive summaries & follow-ups). |
| 📊 **Dynamic Visualization** | The AI automatically decides the best way to visualize data: **Bar, Line, Pie, KPI, or Table**, rendered beautifully via Recharts. |
| 🧠 **Chat Memory** | Full conversation history is persisted in SQLite — survives page reloads and browser restarts. |
| 💡 **Smart Follow-ups** | AI-generated follow-up questions grounded strictly in the database schema — no hallucinated columns. |
| 🎯 **Intent Guardrail** | Groq-powered intent classification prevents Vanna from generating SQL for greetings or off-topic input. |
| 🔒 **Fully Local Processing** | Whisper, ChromaDB, EasyOCR, and SQLite all run on your machine — no data leaves your system. |
| 🗂️ **Session Management** | Create, switch, and delete chat sessions — premium glass-morphism sidebar with real-time history. |

---

## 🏗️ Architecture
![Image](https://github.com/user-attachments/assets/3804dfea-e7f9-4f21-8018-cd16d88a86e2)
              
---

## User Flow Diagram
![Image](https://github.com/user-attachments/assets/fc931330-242e-4012-8986-67bb210785a8)

---



## 📂 Project Structure

```text
Insightx-/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI server (10 endpoints, dual-AI pipeline)
│   │   └── chat_db.py                   # SQLite chat history (sessions + messages CRUD)
│   ├── scripts/
│   │   ├── train_vanna.py               # Train Vanna on DB schema + example queries
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
│   ├── vector_store/                    # ChromaDB vector embeddings (auto-created)
│   ├── notebooks/                       # Jupyter notebooks for exploration
│   ├── .env                             # Environment variables (git-ignored)
│   ├── .env.example                     # Template for environment variables
│   └── requirements.txt                 # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                      # Root component with React Router
│   │   ├── main.tsx                     # Vite entry point
│   │   ├── index.css                    # Global styles (glassmorphism, animations, dark theme)
│   │   ├── lib/
│   │   │   └── api.ts                   # Typed API client
│   │   ├── pages/
│   │   │   ├── Index.tsx                # Landing page
│   │   │   ├── Dashboard.tsx            # Main chat interface (+ dynamic PDF Export logic)
│   │   │   └── NotFound.tsx             # 404 page
│   │   ├── components/
│   │   │   ├── DashboardSidebar.tsx     # Branded session sidebar
│   │   │   ├── ChatMessage.tsx          # Message renderer (follow-ups, SQL disclosure)
│   │   │   ├── DataVisualizer.tsx       # Table / Line / Bar / Pie chart / KPI renderer
│   │   │   ├── ReportTemplate.tsx       # Hidden light-themed corporate template for PDF export
│   │   │   ├── NavLink.tsx              # Navigation link component
│   │   │   └── ui/                      # 49 shadcn/ui components
│   │   ├── hooks/                       # Custom React hooks
│   │   └── test/                        # Vitest test files
│   ├── vite.config.ts                   # Dev server (port 8080, /api proxy → 8000)
│   ├── package.json                     # Node dependencies (including html2pdf.js, recharts)
│   ├── tailwind.config.ts               # Tailwind CSS configuration
│   └── tsconfig.json                    # TypeScript configuration
└── README.md                            # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **FFmpeg** — required by Whisper for audio processing ([ffmpeg.org](https://ffmpeg.org))
- **Groq API Key** — free at [console.groq.com](https://console.groq.com)
- **Google Gemini API Key** — free at [aistudio.google.com](https://aistudio.google.com) *(only needed for training Vanna)*

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

The frontend starts at **http://localhost:8080**. It automatically proxies all `/api/*` requests to the backend.

### 4. Open in Browser

Navigate to **http://localhost:8080** → Click **"Try InsightX"** → Start asking questions!

---

## 🔌 API Endpoints

### Core Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ask` | Text query → Vanna SQL → Groq summary → JSON response |
| `POST` | `/api/voice-ask` | Audio upload (.webm) → Whisper transcription → full pipeline |
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
| Speech-to-Text | **OpenAI Whisper** (local) | Audio transcription (coupled with **FFmpeg**) |
| OCR | **EasyOCR** 1.7+ | Image text extraction — CPU-based |
| Database | **SQLite** | Transaction data + chat history |
| Data Processing | **Pandas** 2.0+, **NumPy** 1.24+ | DataFrame operations and formatting |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | **React 18** + **TypeScript** | Component-based UI with full type safety |
| Build Tool | **Vite 5** | Fast HMR dev server |
| UI Library | **shadcn/ui** | Radix UI primitives with Tailwind styling |
| Styling | **Tailwind CSS 3.4** | Utility-first CSS with custom dark theme |
| Charts | **Recharts** 2.15 | Responsive Line, Bar, and Pie chart visualizations |
| Reports | **html2pdf.js** | 1-Click Executive Corporate PDF Generation |
| Animations | **Framer Motion** 12 | Fluid transitions, message animations, waveforms |
| Icons | **Lucide React** | Beautiful SVG icons |
| Routing | **React Router 6** | Client-side routing with session capability |

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

---

## 📋 Example Queries to Try

Once the app is running, try asking:

1. *"What is the distribution of transactions by network type?"* (Will automatically render a **Pie Chart**)
2. *"Show me the total transaction count over the last 7 days."* (Will automatically render a **Line Chart**)
3. *"Which top 5 states have the highest transaction volume?"* (Will automatically render a **Bar Chart**)
4. *"What is the overall total transaction amount?"* (Will automatically render a **KPI Card**)

*(After asking, click the **Export Board Report** button in the header to download the entire session as a polished Corporate PDF document!)*

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Create `backend/.env` with your API key (see `.env.example`) |
| `ModuleNotFoundError: whisper` | Install with `pip install openai-whisper` and ensure **FFmpeg** is in PATH |
| `[WinError 2] The system cannot find the file specified` | **FFmpeg is missing**. Whisper requires it to decode WebM audio from browsers. Install via `winget install Gyan.FFmpeg` or conda. |
| `database is locked` | Ensure only one instance of the backend is running. |
| `Vanna generates wrong SQL` | Re-run `python scripts/train_vanna.py` to retrain with more examples. |
| Frontend shows `502 Bad Gateway` | Ensure the backend is running on port 8000. |
| `EasyOCR init failed` | Install with `pip install easyocr` — first run downloads a ~100MB model. |

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
- [html2pdf.js](https://ekoopmans.github.io/html2pdf.js/) — Client-side PDF generation

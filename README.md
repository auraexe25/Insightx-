# InsightX

**AI-powered natural language analytics for Indian UPI transaction data.**

InsightX lets you ask questions in plain English and get instant insights — powered by Vanna AI (Text-to-SQL), Groq LLM, and a local SQLite database of UPI transactions.

---

## Project Structure (Monorepo)

```
Insightx-/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI backend (headless API)
│   ├── scripts/
│   │   ├── train_vanna.py        # Train Vanna on schema, rules & examples
│   │   └── demo_vanna.py         # Quick CLI demo for Vanna queries
│   ├── data/                     # SQLite DB + CSV datasets (git-ignored)
│   ├── vector_store/             # ChromaDB embeddings (git-ignored)
│   ├── notebooks/
│   │   └── feature_engineering.ipynb
│   └── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Quick Start

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Train Vanna (first time only)

```bash
python scripts/train_vanna.py
```

### 4. Run the API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Ask a Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total transaction volume for SBI?"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | Health check |
| `POST` | `/ask`   | Ask a natural language question → get SQL, data, answer & follow-ups |

## Tech Stack

- **FastAPI** — High-performance async API
- **Vanna AI** — Text-to-SQL with ChromaDB vector store
- **Groq (LLaMA 3.3 70B)** — LLM for answer generation
- **SQLite** — Local UPI transaction database

## License

MIT

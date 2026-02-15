# CVS Store Assistant (SLM + RAG)

A store operations assistant for retail pharmacy: answers policy/SOP questions using RAG over your documents and inventory/analytics questions using a local SQLite DB, powered by a small language model (Ollama) and safety guardrails.

## Features

- **Policy / RAG**: Questions about procedures, SOPs, returns, etc. are answered from ingested PDF/DOCX documents using FAISS + sentence embeddings.
- **Data / Analytics**: Stockout risk, days of supply, and inventory metrics from a SQLite database.
- **Safety**: Redirects medical/medication advice requests to consult a pharmacist.
- **API**: FastAPI backend with a `/chat` endpoint.
- **UI**: Streamlit app that talks to the API.

## Prerequisites

- **Python 3.10+**
- **Ollama** running locally with a model (e.g. `phi3:mini`). Install from [ollama.ai](https://ollama.ai) and run:
  ```bash
  ollama pull phi3:mini
  ```

## Push to GitHub

From the project root (e.g. `AI Project` or `cvs_slm_assistant`, depending on where you want the repo root):

```bash
git init
git add .
git commit -m "Initial commit: CVS Store Assistant (SLM + RAG)"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Create the repository on GitHub first (empty, no README), then use its URL in `git remote add origin`.

## Setup

1. **Clone the repo** (or use this folder):
   ```bash
   git clone <your-repo-url>
   cd "AI Project"
   cd cvs_slm_assistant
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database** (optional; for analytics):
   ```bash
   python app/db.py
   ```

5. **Ingest documents for RAG** (optional; for policy answers):
   - Place PDF/DOCX files in `kb/docs/`.
   - Run:
     ```bash
     python app/ingest.py
     ```
   If you skip this, policy questions will fail until the index exists.

## Run

1. **Start the API** (from `cvs_slm_assistant`):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Streamlit UI** (in another terminal):
   ```bash
   streamlit run ui/streamlit_app.py
   ```

3. Open the URL Streamlit shows (e.g. `http://localhost:8501`) and use the chat interface. Ensure Ollama is running at `http://localhost:11434`.

## Project layout

```
cvs_slm_assistant/
├── app/
│   ├── main.py      # FastAPI app, /chat
│   ├── router.py    # policy vs data routing
│   ├── rag.py       # FAISS retrieval + context
│   ├── llm.py       # Ollama client
│   ├── safety.py    # Medical-advice guard
│   ├── analytics.py # Stockout risk, etc.
│   ├── db.py        # SQLite init
│   └── ingest.py    # Build kb from docs
├── ui/
│   └── streamlit_app.py
├── kb/              # RAG knowledge base (docs + index)
├── data/            # SQLite DB (inventory)
├── requirements.txt
└── README.md
```

## License

Use as you like; no warranty.

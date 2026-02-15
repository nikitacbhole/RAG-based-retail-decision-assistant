from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.router import route_query
from app.safety import is_medical_advice_request, SAFE_REDIRECT
from app.rag import retrieve, build_context
from app.analytics import get_stockout_risk
from app.llm import ollama_generate

app = FastAPI(title="CVS Store Assistant (SLM + RAG)")

class ChatRequest(BaseModel):
    query: str
    store_id: Optional[str] = "001"

class ChatResponse(BaseModel):
    route: str
    answer: str
    citations: List[Dict] = []

SYSTEM_POLICY = (
    "You are a store operations assistant for a retail pharmacy store.\n"
    "Rules:\n"
    "1) No medical advice/diagnosis/medication guidance.\n"
    "2) If using context sources, answer ONLY from the provided sources.\n"
    "3) If the answer is not in sources, say: 'Not found in the provided documents.'\n"
    "4) Format: Summary, Steps/Actions, Sources (if any).\n"
)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    q = (req.query or "").strip()
    if not q:
        return ChatResponse(route="none", answer="Please enter a question.", citations=[])

    if is_medical_advice_request(q):
        return ChatResponse(route="safety", answer=SAFE_REDIRECT, citations=[])

    route = route_query(q)

    # ---------------- POLICY / RAG ----------------
    if route == "policy":
        retrieved = retrieve(q, top_k=6)
        context, kept = build_context(retrieved)

        prompt = (
            f"CONTEXT:\n{context}\n\n"
            f"USER QUESTION:\n{q}\n\n"
            "Answer with:\n"
            "- Summary (1–2 lines)\n"
            "- Steps/Actions (bullets)\n"
            "- Sources (list the SOURCE lines you used)\n"
        )

        ans = ollama_generate(prompt=prompt, system=SYSTEM_POLICY, temperature=0.2)
        citations = [{"source": c["source"], "chunk_id": c["chunk_id"]} for c in kept]
        return ChatResponse(route="policy", answer=ans, citations=citations)

    # ---------------- DATA / ANALYTICS ----------------
    df = get_stockout_risk(store_id=req.store_id or "001", days_threshold=7.0)
    risky = df[df["stockout_risk"] == True].head(10)

    table_text = risky.to_string(index=False) if not risky.empty else df.head(10).to_string(index=False)

    prompt = (
        "You are given computed inventory metrics (truth). Do not invent numbers.\n\n"
        f"QUESTION:\n{q}\n\n"
        f"COMPUTED DATA:\n{table_text}\n\n"
        "Respond with:\n"
        "- Summary\n"
        "- Key drivers\n"
        "- Actions for store associate (bullets)\n"
        "- Callouts (assumptions/risks)\n"
    )

    ans = ollama_generate(prompt=prompt, system=SYSTEM_POLICY, temperature=0.2)
    return ChatResponse(route="data", answer=ans, citations=[])

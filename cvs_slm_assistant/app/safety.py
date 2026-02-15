import re

MEDICAL_PATTERNS = [
    r"\bdiagnos(e|is)\b",
    r"\bshould i take\b",
    r"\bwhat medicine\b",
    r"\bside effects\b",
    r"\bpregnan(t|cy)\b",
    r"\bsymptom(s)?\b",
    r"\bdosage\b",
]

def is_medical_advice_request(q: str) -> bool:
    ql = q.lower()
    return any(re.search(p, ql) for p in MEDICAL_PATTERNS)

SAFE_REDIRECT = (
    "I can help with **store/pharmacy operations, policies, and workflow guidance**. "
    "I can’t provide medical advice, diagnosis, or medication guidance. "
    "For medical questions, please consult a licensed pharmacist or healthcare provider."
)

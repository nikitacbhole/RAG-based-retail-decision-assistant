def route_query(q: str) -> str:
    ql = q.lower()

    data_keywords = [
        "stockout", "out of stock", "oos", "trend", "kpi", "sales",
        "forecast", "inventory", "days of supply", "reorder", "top sku",
        "why did", "increase", "decrease", "shrink", "returns rate"
    ]
    policy_keywords = [
        "policy", "sop", "procedure", "how do i", "process", "return", "refund",
        "coupon", "checklist", "workflow", "steps"
    ]

    data_score = sum(1 for k in data_keywords if k in ql)
    policy_score = sum(1 for k in policy_keywords if k in ql)

    # Safer default: policy/RAG
    return "data" if data_score > policy_score else "policy"

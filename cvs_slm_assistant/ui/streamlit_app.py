import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="CVS Store Assistant (SLM + RAG)", layout="wide")
st.title("CVS Store Assistant — SLM + RAG")

store_id = st.text_input("Store ID", value="001")
query = st.text_area("Ask a question (policy or inventory/analytics):", height=120)

if st.button("Ask"):
    if not query.strip():
        st.warning("Please type a question.")
    else:
        with st.spinner("Thinking..."):
            r = requests.post(API_URL, json={"query": query, "store_id": store_id}, timeout=180)
            r.raise_for_status()
            data = r.json()

        st.subheader(f"Route: {data['route']}")
        st.write(data["answer"])

        if data.get("citations"):
            st.subheader("Citations")
            st.json(data["citations"])

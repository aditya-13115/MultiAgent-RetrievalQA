import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(page_title="Healthcare AI RAG", layout="wide")

st.title("🧠 Healthcare AI RAG Assistant")

# Input
query = st.text_input("Ask a question:")

if st.button("Run") and query:
    with st.spinner("Processing..."):
        response = requests.post(API_URL, json={"query": query})

    if response.status_code != 200:
        st.error("API Error")
    else:
        data = response.json()

        # =========================
        # ✅ FINAL ANSWER (CLEAN)
        # =========================
        st.markdown("## ✅ Final Answer")
        st.success(data["answer"])

        trace = data["trace"]

        # =========================
        # 🔽 COLLAPSIBLE DEBUG PANEL
        # =========================
        with st.expander("🔍 View Reasoning & Retrieval Details", expanded=False):

            st.markdown("### 🔀 Router Decision")
            st.write(trace["route"])

            st.markdown("### ✏️ Rewritten Query")
            st.write(trace["rewritten_query"])

            st.markdown("### 🧩 Sub-Queries")
            st.write(trace["sub_queries"])

            st.markdown("### 📚 Retrieved Documents")
            st.write(trace["retrieved_docs"])

            st.markdown("### 🧠 Reasoning (Chain-of-Thought)")
            st.text(trace["reasoning"])

            if trace["critic"]:
                st.markdown("### 🧪 Critic")
                st.text(trace["critic"])
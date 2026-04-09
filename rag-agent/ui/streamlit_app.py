import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"
RESET_URL = "http://127.0.0.1:8000/reset"

st.set_page_config(page_title="Healthcare AI RAG", layout="wide", page_icon="🧠")

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.title(" Controls")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        requests.post(RESET_URL)
        st.rerun()

    st.markdown("---")
    st.caption("Multi-Agent RAG System")

# -------------------------
# TITLE
# -------------------------
st.title("Healthcare AI RAG Assistant")
st.caption("Ask anything about AI in Healthcare")

# -------------------------
# SESSION STATE
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# DISPLAY CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# INPUT
# -------------------------
query = st.chat_input("Ask your question...")

if query:
    # USER MESSAGE
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    # ASSISTANT RESPONSE
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(API_URL, json={"query": query})

        if response.status_code != 200:
            st.error("API Error")
        else:
            data = response.json()
            answer = data.get("answer", "")
            trace = data.get("trace", {})

            # FINAL ANSWER
            st.markdown(answer)

            # STORE RESPONSE
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # -------------------------
            # COLLAPSIBLE TRACE
            # -------------------------
            with st.expander("View reasoning pipeline", expanded=False):

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Router")
                    st.code(trace.get("route", ""))

                with col2:
                    st.markdown("### Rewritten Query")
                    st.code(trace.get("rewritten_query", ""))

                st.markdown("### Sub-Queries")
                st.write(trace.get("sub_queries", []))

                st.markdown("### Retrieved Docs")
                docs = trace.get("retrieved_docs", [])
                if docs:
                    st.write(docs)
                else:
                    st.info("No citations extracted")

                st.markdown("### Reasoning")
                st.text(trace.get("reasoning", ""))

                if trace.get("critic"):
                    st.markdown("### Critic")
                    st.text(trace.get("critic"))

"""Public demo: no user uploads, no arbitrary SQL, session-local conversation."""
from dataclasses import asdict
import logging
import time

import streamlit as st

from crestline.assistant import Assistant
from crestline.database import Database

st.set_page_config(page_title="Crestline · Internal Assistant", page_icon="◈", layout="wide")


@st.cache_resource
def resources():
    database = Database()
    database.bootstrap()
    return Assistant(database)


def show_result(result):
    st.markdown(result["answer"])
    st.caption(f"{result['domain'].upper()} · {result['mode']} · {result['elapsed_ms']:,} ms")
    if result.get("notice"):
        st.caption(result["notice"])
    if result.get("rows"):
        with st.expander("View verified data"):
            st.dataframe(result["rows"], use_container_width=True, hide_index=True)
    if result.get("evidence"):
        with st.expander("Sources and evidence"):
            for source in result["evidence"]:
                st.markdown(f"**[{source['id']}] {source['source']}**")
                st.text(source["text"])
    if result.get("sql"):
        with st.expander("Inspect the read-only query"):
            st.code(result["sql"], language="sql")
            st.write("Parameters:", result["parameters"])


st.title("◈ Crestline")
st.subheader("Answers connected to the evidence.")
st.write("Explore company policies, campaign briefs, product documentation and business metrics in one conversation.")
st.caption("Portfolio demo · Fictional company · Business records cover 2024 · No real employee or customer data")

try:
    assistant = resources()
except Exception:
    logging.getLogger(__name__).error("Assistant initialization failed; check server startup logs")
    st.error("The assistant is still initializing or its database is unavailable. Please try again shortly.")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history=[]
with st.sidebar:
    st.markdown("### Your workspace")
    st.write("HR · Marketing · Product · Business analytics")
    st.success("PostgreSQL + pgvector connected")
    if assistant.llm.enabled:
        st.caption("Gemini configured · Sources shown with every answer")
    else:
        st.info("Evidence mode: direct data and document excerpts. Gemini synthesis is not configured.")
    if st.button("New conversation", use_container_width=True):
        st.session_state.history=[]
        st.rerun()
    st.markdown("[View project on GitHub](https://github.com/gusbakers/enterprise-internal-assistant)")
    st.caption("This is a public demo, not a production HR system. Please do not enter personal or confidential information.")

examples = ["How many Crestline X phones were sold in total?", "What is the PTO carryover policy?",
            "What is the target audience for the Crestline Watch campaign?", "What are the Crestline Cloud API rate limits?"]
selected=None
if not st.session_state.history:
    cols=st.columns(2)
    for i, example in enumerate(examples):
        if cols[i%2].button(example, use_container_width=True): selected=example
for turn in st.session_state.history:
    with st.chat_message("user"): st.markdown(turn["question"])
    with st.chat_message("assistant"): show_result(turn["result"])
question=st.chat_input("Ask about Crestline…", max_chars=1500) or selected
if question:
    if time.time()-st.session_state.get("last_request",0)<2:
        st.info("Please wait a moment before sending the next question.")
        st.stop()
    st.session_state.last_request=time.time()
    with st.chat_message("user"): st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Checking the sources…"):
                result=assistant.ask(question,st.session_state.history[-3:])
            rendered=asdict(result)
            show_result(rendered)
            st.session_state.history.append({"question":question,"resolved_question":result.resolved_question,"result":rendered})
            st.session_state.history=st.session_state.history[-20:]
        except Exception:
            logging.getLogger(__name__).error("Request failed; no user content recorded")
            st.error("I couldn't complete that request. Please try again shortly.")

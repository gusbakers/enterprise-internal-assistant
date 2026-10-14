"""Crestline's public, evidence-grounded workspace."""
from dataclasses import asdict
import logging
import time

import streamlit as st

from crestline.assistant import Assistant
from crestline.database import Database

st.set_page_config(page_title="Crestline · Knowledge workspace", page_icon="🔷", layout="wide")
st.markdown('''<style>
.stApp {background:#f5f8ff;color:#13254b;}
[data-testid="stSidebar"] {background:#0c2450;}
[data-testid="stSidebar"] * {color:#e5efff;}
[data-testid="stSidebar"] .stButton>button {background:#16386d!important;border:1px solid #537ab2!important;color:#ffffff!important;}
[data-testid="stSidebar"] .stButton>button:hover {background:#2457a0!important;}
[data-testid="stSidebar"] a {color:#a9d4ff!important;}
.block-container {max-width:1120px;padding-top:2.2rem;padding-bottom:2rem;}
.hero {background:linear-gradient(120deg,#0b285a,#175fbe 65%,#418cde);border-radius:24px;padding:36px 40px;color:white;margin-bottom:22px;box-shadow:0 14px 38px #164a8a18;}
.hero .eyebrow {font-size:12px;letter-spacing:2px;font-weight:700;color:#b9d6ff;}
.hero h1 {color:white;font-size:40px;letter-spacing:-1.5px;margin:8px 0;}
.hero p {color:#dfedff;font-size:16px;max-width:600px;margin:8px 0;}
.hero .tag {display:inline-block;border:1px solid #82b6f066;border-radius:30px;padding:5px 12px;margin:12px 8px 0 0;font-size:12px;color:#e5efff;}
[data-testid="stChatMessage"] {border:1px solid #dce7f7;border-radius:18px;background:white;padding:20px;margin:14px 0;box-shadow:0 5px 18px #0b285a05;}
[data-testid="stChatInput"] {border-radius:16px;border:1px solid #a6c3ef;}
.stButton>button {border-radius:13px;border:1px solid #ccddf5;background:white;color:#16457b;min-height:46px;transition:all .15s;}
.stButton>button:hover {border-color:#2874d0;background:#edf5ff;color:#16457b;transform:translateY(-1px);}
[data-testid="stMetric"] {background:white;border:1px solid #dce7f7;padding:16px 20px;border-radius:16px;}
[data-testid="stMetricValue"] {color:#185fba;font-size:26px;}
[data-testid="stExpander"] {border:1px solid #e1e9f5;border-radius:12px;}
h2,h3 {color:#153968;}
@media(max-width:640px){.hero{padding:24px}.hero h1{font-size:30px}.block-container{padding-top:1rem}}
</style>''', unsafe_allow_html=True)


@st.cache_resource
def resources():
    database=Database()
    database.bootstrap()
    return Assistant(database)


EXAMPLES = {
    "Explore": [("Sales snapshot", "How many Crestline X phones were sold in total?"), ("Time off", "What is the maximum PTO carryover?"), ("Campaign audience", "Who is the target audience for the Crestline Watch campaign?"), ("API limits", "What are the Cloud API rate limits?")],
    "People": [("Remote schedule", "How many remote days can Engineering work?"), ("PTO carryover", "What is the maximum PTO carryover?"), ("Team size", "How many employees work in Engineering?"), ("Onboarding", "What happens in the first week of onboarding?")],
    "Campaigns": [("Watch audience", "Who is the target audience for the Crestline Watch campaign?"), ("Launch strategy", "What is the Crestline X launch strategy?"), ("Pro campaign", "Who is the target audience for the Crestline Pro campaign?")],
    "Products": [("API rate limits", "What are the Cloud API rate limits?"), ("System requirements", "What are the system requirements for Crestline OS?"), ("API authentication", "How does Cloud API authentication work?")],
    "Analytics": [("Total units", "How many Crestline X phones were sold in total?"), ("Best month", "Which month had the highest Crestline X sales in 2024?"), ("Monthly trend", "Crestline X sales by month in 2024"), ("First quarter", "Crestline X sales in Q1 2024")],
}


def show_result(result, index):
    st.markdown(result["answer"])
    mode="Gemini · grounded answer" if result["mode"].startswith("Gemini") else "Source-based answer"
    if not result.get("evidence"):
        mode="Clarification" if result["mode"]=="needs clarification" else "No supported answer"
    st.caption(f"{mode} · {len(result.get('evidence',[]))} sources · {result['elapsed_ms']/1000:.1f}s")
    if result.get("notice") and "not configured" not in result["notice"]:
        st.caption(result["notice"])
    if result.get("evidence"):
        with st.expander("Sources · verify this answer"):
            for source in result["evidence"]:
                st.markdown(f"**[{source['id']}] {source['source']}**")
                st.text(source["text"])
    if result.get("rows"):
        with st.expander("Data · explore the results"):
            rows=result["rows"]
            if len(rows)>1 and all("month" in r and "units_sold" in r for r in rows):
                st.caption("Units sold by month · 2024 demo records")
                st.bar_chart(rows, x="month", y="units_sold", color="#2874d0")
            st.dataframe(rows,use_container_width=True,hide_index=True)
            with st.expander("Query details"):
                st.code(result["sql"],language="sql")
                st.write("Parameters:",result["parameters"])
    st.feedback("thumbs",key=f"feedback_{st.session_state.conversation_id}_{index}")


try:
    assistant=resources()
except Exception:
    logging.getLogger(__name__).error("Assistant initialization failed")
    st.error("The workspace is warming up. Please refresh in a moment.")
    st.stop()

st.session_state.setdefault("history",[])
st.session_state.setdefault("conversation_id",0)
with st.sidebar:
    st.markdown("## 🔷 Crestline")
    st.caption("KNOWLEDGE WORKSPACE")
    st.divider()
    topic=st.radio("Explore a topic",list(EXAMPLES))
    st.divider()
    if st.button("＋ New conversation",use_container_width=True):
        st.session_state.history=[]
        st.session_state.conversation_id+=1
        st.session_state.pop("pending_question",None)
        st.rerun()
    st.markdown("**Connected to company sources**")
    st.caption("Gemini is enabled. Answers are checked against sources." if assistant.llm.enabled else "Source-based mode · Gemini is not configured. Selected facts retain the source language.")
    st.caption("Demo company · 2024 business records. Do not enter confidential information.")
    st.markdown("[Project & architecture ↗](https://github.com/gusbakers/enterprise-internal-assistant)")

st.markdown('''<div class="hero"><div class="eyebrow">CRESTLINE / INTERNAL INTELLIGENCE</div><h1>Less searching.<br>More clarity.</h1><p>Your company knowledge, one question away.<br>Direct answers. Essential details. Sources you can inspect.</p><span class="tag">People & policies</span><span class="tag">Products & campaigns</span><span class="tag">Business insights</span></div>''',unsafe_allow_html=True)
if not st.session_state.history:
    a,b,c=st.columns(3)
    a.metric("Knowledge sources","9 documents")
    b.metric("Connected domains","4 teams")
    c.metric("Business data","2024")
st.markdown("### What would you like to know?")
selected=None
cols=st.columns(2)
for i,(label,prompt) in enumerate(EXAMPLES[topic]):
    if cols[i%2].button(label,key=f"example_{topic}_{i}",help=prompt,use_container_width=True):
        selected=prompt
for index,turn in enumerate(st.session_state.history):
    with st.chat_message("user"): st.markdown(turn["question"])
    with st.chat_message("assistant",avatar="🔷"): show_result(turn["result"],index)
question=st.chat_input("Ask a question — English or Spanish",max_chars=1500) or selected
if question:
    if time.time()-st.session_state.get("last_request",0)<2:
        st.info("Please wait a moment before your next question.")
        st.stop()
    st.session_state.last_request=time.time()
    try:
        with st.spinner("Finding the essential facts…"):
            result=assistant.ask(question,st.session_state.history[-3:])
        st.session_state.history.append({"question":question,"resolved_question":result.resolved_question,"result":asdict(result)})
        st.session_state.history=st.session_state.history[-20:]
        st.rerun()
    except Exception:
        logging.getLogger(__name__).error("Request failed; no user content recorded")
        st.error("I couldn't complete that request. Please try again.")

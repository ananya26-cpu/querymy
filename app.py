import streamlit as st
import pandas as pd
import yfinance as yf
from gemini_helper import ask_gemini
from data_handler import load_file, get_data_summary, detect_anomalies
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="QueryMy", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif !important; }
.stApp { background-color: #020408 !important; background-image: linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px); background-size: 48px 48px; }
section[data-testid="stSidebar"] { background-color: #070d14 !important; border-right: 1px solid #0f2035 !important; }
section[data-testid="stSidebar"] * { color: #e8f4ff !important; }
.stChatMessage { background-color: #0b1520 !important; border: 1px solid #0f2035 !important; border-radius: 12px !important; margin-bottom: 8px !important; }
.stButton > button { background: linear-gradient(135deg, #0066ff, #00d4ff) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(0,102,255,0.4) !important; }
.stFileUploader { background-color: #0b1520 !important; border: 1px dashed #0f2035 !important; border-radius: 12px !important; }
.stExpander { background-color: #0b1520 !important; border: 1px solid #0f2035 !important; border-radius: 12px !important; }
.stDataFrame { background-color: #0b1520 !important; border-radius: 8px !important; }
.stSuccess { background-color: #052e16 !important; border: 1px solid #166534 !important; border-radius: 8px !important; }
h1, h2, h3, p, label { color: #e8f4ff !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #0f2035; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div style="padding:8px 0 24px;">
<div style="font-family:monospace;font-size:0.75rem;color:#00d4ff;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:12px;">// AI-Powered Data Intelligence</div>
<div style="font-size:2.8rem;font-weight:800;letter-spacing:-0.04em;line-height:1;background:linear-gradient(135deg,#00d4ff,#0066ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;">⚡ QueryMy</div>
<div style="font-size:0.9rem;color:#3a5a78;font-family:monospace;">Ask anything about your data — built by Ananya Gautam</div>
</div>
''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📂 Data Source")
    data_source = st.radio("", ["Upload CSV/Excel", "Live Stock Data"])
    if data_source == "Upload CSV/Excel":
        uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"])
        if uploaded_file:
            df = load_file(uploaded_file)
            if df is not None:
                st.success(f"✅ {uploaded_file.name}")
                st.write(f"**{df.shape[0]} rows × {df.shape[1]} cols**")
                st.dataframe(df.head(5), use_container_width=True)
                st.session_state["df"] = df
                st.session_state["data_summary"] = get_data_summary(df)
    elif data_source == "Live Stock Data":
        ticker = st.text_input("Stock symbol", value="RELIANCE.NS")
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])
        if st.button("⚡ Fetch Live Data"):
            with st.spinner("Fetching..."):
                df = yf.download(ticker, period=period)
                df.reset_index(inplace=True)
                st.success(f"✅ {ticker} loaded")
                st.dataframe(df.tail(5), use_container_width=True)
                st.session_state["df"] = df
                st.session_state["data_summary"] = get_data_summary(df)

if "df" in st.session_state:
    with st.expander("🔍 Anomaly Detection"):
        anomalies = detect_anomalies(st.session_state["df"])
        st.write(anomalies)
        if st.button("🧠 Explain Anomalies with AI"):
            explanation = ask_gemini("Explain these anomalies in simple business terms", anomalies)
            st.write(explanation)

if "df" in st.session_state:
    if st.button("📄 Download PDF Report"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "QueryMy — Data Analysis Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Rows: {st.session_state['df'].shape[0]} | Columns: {st.session_state['df'].shape[1]}")
        summary_lines = st.session_state["data_summary"].split("\n")
        y = 690
        for line in summary_lines[:15]:
            c.drawString(50, y, line[:90])
            y -= 18
        c.save()
        buffer.seek(0)
        st.download_button("📥 Click to Download", buffer, file_name="querymy_report.pdf")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask anything about your data..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            data_context = st.session_state.get("data_summary", "No data loaded yet.")
            response = ask_gemini(prompt, data_context)
            st.write(response)
    st.session_state["messages"].append({"role": "assistant", "content": response})

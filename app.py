import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from gemini_helper import ask_gemini, generate_sql, auto_insight
from data_handler import load_file, get_data_summary, detect_anomalies
from sql_handler import load_csv_to_db, run_sql, get_schema
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import json

st.set_page_config(page_title="QueryMy Pro", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
* { font-family: 'Syne', sans-serif !important; }
.stApp { background-color: #020408 !important; background-image: linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px); background-size: 48px 48px; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #070d14 0%, #050a10 100%) !important; border-right: 1px solid #0f2035 !important; }
section[data-testid="stSidebar"] * { color: #a8c8e8 !important; }
.stChatMessage { background: linear-gradient(135deg, #0b1520, #070d14) !important; border: 1px solid #0f2035 !important; border-radius: 12px !important; margin-bottom: 10px !important; }
.stChatMessage:hover { border-color: rgba(0,212,255,0.25) !important; }
.stButton > button { background: linear-gradient(135deg, #0066ff, #00d4ff) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; box-shadow: 0 4px 15px rgba(0,102,255,0.3) !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(0,102,255,0.5) !important; }
.stFileUploader { background: linear-gradient(135deg, #0b1520, #070d14) !important; border: 1px dashed rgba(0,212,255,0.2) !important; border-radius: 12px !important; }
.stExpander { background: linear-gradient(135deg, #0b1520, #070d14) !important; border: 1px solid #0f2035 !important; border-radius: 12px !important; }
.stDataFrame { background-color: #0b1520 !important; border-radius: 8px !important; border: 1px solid #0f2035 !important; }
.stSuccess { background: linear-gradient(135deg, #052e16, #063a1c) !important; border: 1px solid rgba(0,255,136,0.3) !important; border-radius: 8px !important; }
h1, h2, h3 { color: #e8f4ff !important; }
p, label { color: #a8c8e8 !important; }
.metric-card { background: linear-gradient(135deg, #0b1520, #070d14); border: 1px solid #0f2035; border-radius: 12px; padding: 16px 20px; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #00d4ff, #0066ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-label { font-size: 0.7rem; color: #3a5a78; font-family: monospace; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #0f2035; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding:8px 0 24px;border-bottom:1px solid #0f2035;margin-bottom:24px;">
<div style="font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:10px;">// AI-Powered Data Intelligence</div>
<div style="font-size:2.8rem;font-weight:800;letter-spacing:-0.04em;line-height:1;background:linear-gradient(135deg,#00d4ff,#0066ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;">⚡ QueryMy Pro</div>
<div style="font-size:0.8rem;color:#3a5a78;font-family:monospace;">Ask anything about your data — built by Ananya Gautam</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #0f2035;'>// Data Source</div>", unsafe_allow_html=True)
    data_source = st.radio("", ["Upload CSV/Excel", "Live Stock Data"])
    if data_source == "Upload CSV/Excel":
        uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"])
        if uploaded_file:
            df = load_file(uploaded_file)
            if df is not None:
                st.success(f"✅ {uploaded_file.name}")
                st.markdown(f"<div style='font-family:monospace;font-size:0.75rem;color:#3a5a78;margin:8px 0;'>{df.shape[0]} rows · {df.shape[1]} cols</div>", unsafe_allow_html=True)
                st.dataframe(df.head(5), use_container_width=True)
                st.session_state["df"] = df
                st.session_state["data_summary"] = get_data_summary(df)
                load_csv_to_db(df)
                st.session_state["db_loaded"] = True
                st.session_state.pop("auto_insight", None)
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
                load_csv_to_db(df)
                st.session_state["db_loaded"] = True
                st.session_state.pop("auto_insight", None)

if "df" in st.session_state:
    df = st.session_state["df"]
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;'>// Dataset Overview</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df.shape[0]:,}</div><div class='metric-label'>Total Rows</div></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df.shape[1]}</div><div class='metric-label'>Columns</div></div>", unsafe_allow_html=True)
    with cols[2]:
        if numeric_cols:
            val = f"{df[numeric_cols[0]].sum():,.0f}"
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{val}</div><div class='metric-label'>Total {numeric_cols[0]}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{df.shape[1]}</div><div class='metric-label'>Features</div></div>", unsafe_allow_html=True)
    with cols[3]:
        missing = df.isnull().sum().sum()
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{missing}</div><div class='metric-label'>Missing Values</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

if "df" in st.session_state and "auto_insight" not in st.session_state:
    with st.spinner("🤖 AI is analyzing your dataset..."):
        insight = auto_insight(st.session_state["data_summary"])
        st.session_state["auto_insight"] = insight

if "auto_insight" in st.session_state:
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;'>// AI Executive Summary</div>", unsafe_allow_html=True)
    insight_html = st.session_state["auto_insight"].replace("\n", "<br>")
    st.markdown(f"<div style='background:linear-gradient(135deg,#0b1520,#070d14);border:1px solid #0f2035;border-left:3px solid #00d4ff;border-radius:12px;padding:20px;margin-bottom:24px;font-size:0.9rem;color:#a8c8e8;line-height:2;'>{insight_html}</div>", unsafe_allow_html=True)

if "df" in st.session_state:
    with st.expander("🔍 Anomaly Detection"):
        anomalies = detect_anomalies(st.session_state["df"])
        st.write(anomalies)
        if st.button("🧠 Explain Anomalies with AI"):
            explanation = ask_gemini("Explain these anomalies in simple business terms", anomalies)
            st.write(explanation)

if "df" in st.session_state:
    with st.expander("🗄️ Text to SQL — Ask in Plain English"):
        sql_question = st.text_input("Ask a SQL question:", placeholder="e.g. Show top 5 categories by total sales")
        if st.button("⚡ Run SQL Query"):
            with st.spinner("Generating SQL..."):
                schema = get_schema()
                sql = generate_sql(sql_question, schema)
                st.markdown(f"```sql\n{sql}\n```")
                result, error = run_sql(sql)
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.dataframe(result, use_container_width=True)

if "df" in st.session_state:
    if st.button("📄 Generate PDF Report"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "QueryMy Pro — Data Analysis Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Rows: {st.session_state['df'].shape[0]} | Columns: {st.session_state['df'].shape[1]}")
        summary_lines = st.session_state["data_summary"].split("\n")
        y = 690
        for line in summary_lines[:15]:
            c.drawString(50, y, line[:90])
            y -= 18
        c.save()
        buffer.seek(0)
        st.download_button("📥 Download Report", buffer, file_name="querymy_report.pdf")

if "df" in st.session_state:
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;margin-top:16px;'>// Quick Questions</div>", unsafe_allow_html=True)
    if st.button("🎲 Surprise Me — Generate 3 Questions"):
        with st.spinner("Generating questions..."):
            data_context = st.session_state.get("data_summary", "")
            suggestion_prompt = f"""Based on this dataset, generate exactly 3 interesting business questions a manager would ask.
Dataset: {data_context}
Return ONLY 3 questions, numbered 1. 2. 3. Nothing else."""
            suggestions = ask_gemini(suggestion_prompt, data_context)
            st.session_state["suggestions"] = suggestions
    if "suggestions" in st.session_state:
        st.markdown(f"<div style='background:#0b1520;border:1px solid #0f2035;border-radius:12px;padding:16px;margin-bottom:16px;font-size:0.9rem;color:#a8c8e8;line-height:1.8;'>{st.session_state['suggestions']}</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg.get("chart") is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)
        else:
            st.write(msg["content"])

if prompt := st.chat_input("Ask anything... try 'show me a bar chart of Sales by Category'"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            data_context = st.session_state.get("data_summary", "No data loaded yet.")
            chart_keywords = ["chart", "plot", "graph", "visualize", "show me", "bar", "line", "pie"]
            wants_chart = any(k in prompt.lower() for k in chart_keywords)

            if wants_chart and "df" in st.session_state:
                chart_prompt = f"""You are a data analyst. Based on this dataset and question, return ONLY a JSON object.
Dataset info: {data_context}
Question: {prompt}
Return ONLY this JSON, nothing else:
{{"chart_type": "bar" or "line" or "pie", "title": "chart title", "x_col": "exact column name", "y_col": "exact column name"}}"""
                raw = ask_gemini(chart_prompt, data_context)
                try:
                    start = raw.find('{')
                    end = raw.rfind('}') + 1
                    config = json.loads(raw[start:end])
                    df = st.session_state["df"]
                    ct = config.get("chart_type", "bar")
                    x = config.get("x_col")
                    y = config.get("y_col")
                    title = config.get("title", "Chart")
                    if ct == "bar":
                        fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    elif ct == "line":
                        fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    elif ct == "pie":
                        fig = px.pie(df, names=x, values=y, title=title)
                    fig.update_layout(paper_bgcolor="#0b1520", plot_bgcolor="#070d14", font_color="#e8f4ff", title_font_color="#00d4ff", xaxis=dict(gridcolor="#0f2035"), yaxis=dict(gridcolor="#0f2035"))
                    st.plotly_chart(fig, use_container_width=True)
                    st.session_state["messages"].append({"role": "assistant", "content": "", "chart": fig})
                except Exception as e:
                    response = ask_gemini(prompt, data_context)
                    st.write(response)
                    st.session_state["messages"].append({"role": "assistant", "content": response})
            else:
                response = ask_gemini(prompt, data_context)
                st.write(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})

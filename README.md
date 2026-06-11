# ⚡ QueryMy Pro — AI Data Analyst

> Ask anything about your data in plain English. AI writes the SQL for you.

🔗 **Live Demo:** [bit.ly/querymypro](https://bit.ly/querymypro)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-deployed-red?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-Llama_3.1-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)

---

## 🚀 What It Does

Upload any CSV or Excel file and QueryMy Pro instantly:

| Feature | Description |
|---|---|
| 🤖 AI Executive Summary | McKinsey-style insights auto-generated on upload |
| 📊 Interactive Charts | "Show me a bar chart of Sales by Category" |
| 🗄️ Text to SQL | Type a question → AI writes + runs the SQL |
| 🔍 Anomaly Detection | Flags unusual values with AI explanation |
| 📄 PDF Export | One-click report download |
| ⚡ Live Stock Data | Pull NSE/BSE data in real time |
| 🎲 Surprise Me | AI generates 3 business questions from your data |

---

## 🛠️ Tech Stack

`Python` `Streamlit` `Groq AI (Llama 3.1)` `Pandas` `Plotly` `SQLite` `yFinance` `ReportLab`

---

## 💻 Run Locally

```bash
git clone https://github.com/ananya26-cpu/querymy
cd querymy
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
streamlit run app.py
```

---

## ⚡ Performance Benchmarks

| Question | Type | Time |
|---|---|---|
| Top 5 categories by sales? | SQL | ~1.2s |
| Any anomalies in sales column? | Analysis | ~1.8s |
| Show monthly trend chart | Chart | ~0.9s |
| What is total revenue? | SQL | ~1.1s |
| Which region performs best? | Analysis | ~1.4s |
| Plot sales by category | Chart | ~0.8s |
| Average order value? | SQL | ~1.0s |
| Explain anomalies in plain english | Analysis | ~2.1s |
| Top 3 products by profit | SQL | ~1.3s |
| Predict next month trend | Analysis | ~1.9s |

*Powered by Groq AI (Llama 3.1) — fastest inference engine available*

## 👩‍💻 Built by

**Ananya Gautam** — building in public 🚀  
Follow on X: [@annannyaaa555](https://x.com/annannyaaa555)

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_gemini(question, data_context=""):
    prompt = f"""You are QueryMy — an expert data analyst assistant built by Ananya Gautam.

Dataset information:
{data_context}

User question: {question}

Answer clearly and concisely like a senior business analyst would.
If numbers are involved, be specific. Keep it under 5 lines."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_sql(question, schema):
    prompt = f"""You are a SQL expert. Generate a SQL query for this question.

Schema:
{schema}

Question: {question}

Rules:
- Table name is always: data
- Return ONLY the SQL query, nothing else
- No markdown, no explanation, just the query"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def auto_insight(data_summary):
    prompt = f"""You are a senior business analyst. A new dataset was just uploaded.

Dataset info:
{data_summary}

Give an executive summary in exactly this format:
📊 OVERVIEW: [1 line about what this dataset is]
🔑 KEY FINDING 1: [most important insight]
🔑 KEY FINDING 2: [second important insight]
🔑 KEY FINDING 3: [third important insight]
⚠️ WATCH OUT: [one risk or anomaly to investigate]
💡 RECOMMENDATION: [one actionable business recommendation]

Be specific with numbers. Sound like a McKinsey analyst."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

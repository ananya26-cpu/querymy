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

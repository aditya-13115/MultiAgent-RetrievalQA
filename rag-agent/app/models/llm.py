import os
import time
from groq import Groq
from dotenv import load_dotenv


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt):
    for _ in range(5):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Retry {_+1} failed:", e)
            time.sleep(1.5 * (2 ** _))
    return "Error: LLM failed"


def call_judge_llm(prompt):
    for _ in range(5):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Retry {_+1} failed:", e)
            time.sleep(1.5 * (2 ** _))
    return "Error: LLM failed"
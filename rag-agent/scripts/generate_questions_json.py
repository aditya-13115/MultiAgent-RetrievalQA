import fitz  # PyMuPDF
import json
import os
import sys
import re

# adjust path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.llm import call_llm


# -------------------------
# STEP 1: LOAD PDF TEXT
# -------------------------
def load_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    doc.close()
    return text


# -------------------------
# STEP 2: CALL LLM TO EXTRACT (STRICT)
# -------------------------
def extract_questions_with_llm(text):
    prompt = f"""
You are a STRICT data extraction system.

Your task is to extract questions EXACTLY as they appear in the PDF.

CRITICAL RULES (DO NOT VIOLATE):
- DO NOT paraphrase
- DO NOT summarize
- DO NOT reword
- DO NOT add anything
- DO NOT infer missing text
- COPY text EXACTLY from input
- Preserve numbers, symbols, formatting (%, →, /, ·, etc.)
- Extract ONLY what is explicitly present

OUTPUT FORMAT (STRICT JSON ONLY):
[
  {{
    "id": "Q01",
    "question": "...",
    "answer": "..."
  }}
]

EXTRA RULES:
- Extract ALL 11 questions (Q01–Q11)
- Question = text between difficulty label and answer
- Answer = EXACT short answer line (e.g., "22% vs 9%")
- DO NOT include explanations, paragraphs, or sources
- DO NOT output anything except JSON
- If unsure, SKIP — do NOT guess

TEXT:
{text[:12000]}
"""

    response = call_llm(prompt)
    return response


# -------------------------
# STEP 3: CLEAN + SAVE JSON (ROBUST)
# -------------------------
def save_json(response):
    try:
        # -------------------------
        # 1. REMOVE <think> BLOCK
        # -------------------------
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

        # -------------------------
        # 2. EXTRACT JSON
        # -------------------------
        json_match = re.search(r"\[.*\]", response, re.DOTALL)

        if not json_match:
            raise ValueError("No valid JSON found")

        json_str = json_match.group()

        # -------------------------
        # 3. LOAD JSON
        # -------------------------
        data = json.loads(json_str)

        # -------------------------
        # 4. SAVE WITH UTF-8 (FIXES ERROR)
        # -------------------------
        os.makedirs("eval", exist_ok=True)

        with open("eval/questions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(data)} questions to eval/questions.json")

    except Exception as e:
        print("Failed to parse LLM output")
        print("\n--- CLEANED OUTPUT ---\n")
        print(response)
        print("\n--- ERROR ---\n", e)


# -------------------------
# MAIN
# -------------------------
def main():
    pdf_path = "data/raw/healthcare_ai_evalset_v2.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    print("📄 Reading PDF...")
    text = load_pdf_text(pdf_path)

    print("🤖 Extracting questions using LLM...")
    response = extract_questions_with_llm(text)

    print("💾 Saving JSON...")
    save_json(response)


if __name__ == "__main__":
    main()

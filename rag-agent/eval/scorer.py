from app.models.llm import call_judge_llm
import json
import re


# =========================
# NORMALIZATION (USED INTERNALLY)
# =========================
def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = text.replace("→", " ")
    text = text.replace("–", " ")
    text = text.replace("/", " ")
    text = text.replace("·", " ")
    text = re.sub(r'[^a-z0-9% ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# =========================
# LLM SCORE (PRIMARY SCORER)
# =========================
def llm_score(pred, truth):
    prompt = f"""
You are an expert evaluator.

Score the model answer from 0 to 10 based on correctness.

Ground truth:
{truth}

Model answer:
{pred}

Evaluation rules:
- DO NOT penalize wording differences or paraphrasing
- Focus ONLY on factual correctness
- If key numbers/entities match → high score (8–10)
- If partially correct → medium score (4–7)
- If incorrect or missing → low score (0–3)
- If answer explicitly says "not found" or avoids answering → low score

Return ONLY a number between 0 and 10.
"""

    response = call_judge_llm(prompt)

    try:
        num = re.findall(r"\d+\.?\d*", response)
        return float(num[0]) if num else 0.0
    except:
        return 0.0


# =========================
# FINAL SCORE (NO HARDCODING)
# =========================
def final_score(pred, truth):
    # Just rely on LLM judge (clean + correct)
    return llm_score(pred, truth)


# =========================
# RUBRIC SCORING
# =========================
def llm_judge_full(pred, truth):
    prompt = f"""
Evaluate the answer using this rubric:

1. Factual Accuracy (0–3)
2. Citation Quality (0–3)
3. Reasoning Quality (0–2)
4. Completeness (0–2)

Ground truth:
{truth}

Model answer:
{pred}

IMPORTANT:
- DO NOT penalize wording differences
- Focus on correctness and grounding
- Reward correct numbers and entities

Return STRICT JSON ONLY:
{{
  "factual": <0-3>,
  "citation": <0-3>,
  "reasoning": <0-2>,
  "completeness": <0-2>,
  "total": <0-10>
}}
"""

    response = call_judge_llm(prompt)

    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")

        return json.loads(match.group())

    except:
        return {
            "factual": 0,
            "citation": 0,
            "reasoning": 0,
            "completeness": 0,
            "total": 0
        }
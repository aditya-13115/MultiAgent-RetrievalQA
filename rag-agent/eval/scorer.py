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
You are a STRICT but FAIR evaluator.

Ground truth:
{truth}

Model answer:
{pred}

SCORING RULES (IMPORTANT):

- If key numbers/entities match → 9–10
- If partially correct → 6–8
- If mostly correct but missing minor detail → 7–9
- If vague but directionally correct → 5–7
- If incorrect → 0–4

CRITICAL:
- DO NOT penalize formatting differences
- DO NOT penalize missing words if meaning is same
- If numbers match → HIGH SCORE
- Short answers are fine

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

IIMPORTANT:
- DO NOT penalize wording differences
- REWARD correct numbers heavily
- If answer contains correct key facts → high factual score
- If citations exist → give at least 2
- Be lenient but accurate

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
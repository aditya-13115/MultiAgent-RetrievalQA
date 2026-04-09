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
You are a FAIR and CONSISTENT evaluator.

Ground truth:
{truth}

Model answer:
{pred}

SCORING GUIDELINES:

- Exact or near-exact meaning → 9–10
- Correct key facts/numbers/entities → 8–10
- Mostly correct but missing some detail → 7–9
- Partially correct → 5–7
- Slightly relevant but incomplete → 3–5
- Incorrect → 0–3

IMPORTANT:
- Focus on MEANING, not wording
- DO NOT penalize formatting differences
- DO NOT penalize brevity if correct
- If key numbers/entities match → prioritize HIGH score
- If one small part is missing → still give 7+
- Final score MUST equal rubric total
- Do NOT output conflicting values

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

- Be LENIENT if the core meaning is correct
- Reward correct numbers/entities strongly
- DO NOT penalize wording or formatting differences
- If answer is partially correct → do not go below 5 overall
- If mostly correct → aim for 7–9 overall
- If citations are present and relevant → give at least 2 in citation
- DO NOT give 0 unless completely unrelated or wrong
- Focus on semantic correctness over exact match
- Final score MUST equal rubric total
- Do NOT output conflicting values

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
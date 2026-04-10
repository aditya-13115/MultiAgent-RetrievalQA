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
    text = re.sub(r"[^a-z0-9% ]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# SINGLE LLM JUDGE (FIXED)
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

--------------------------------
CORE PRINCIPLE:
--------------------------------
- Judge based on MEANING, not wording
- Be FAIR: not overly harsh, not overly lenient
- Verify correctness strictly against ground truth

--------------------------------
SCORING SCALE:
--------------------------------
- Fully correct → 9–10
- Mostly correct → 7–8.5
- Partially correct → 5–6.5
- Weak but relevant → 3–4.5
- Incorrect → 0–2.5

--------------------------------
RULES:
--------------------------------
- Missing minor detail → reduce completeness ONLY
- Wrong core fact → factual ≤ 1
- If answer says "no info" but answer exists → factual = 0
- Do NOT reward citation if answer is wrong

--------------------------------
DECIMAL SCORING:
--------------------------------
- You MAY use decimals (e.g., 1.5, 2.5)

--------------------------------
CITATION INTERPRETATION FIX:
--------------------------------

- If at least ONE citation is present AND answer is factually correct:
  → assign citation score between 2–3

- Do NOT require multiple citations for full marks

- Treat USED_DOCS as valid supporting evidence

- Do NOT give citation = 0 if a citation exists and answer is correct

--------------------------------
COMPLETENESS CALIBRATION:
--------------------------------

- If answer captures the MAIN fact but misses a secondary detail:
  → completeness = 1.5–2

- Do NOT heavily penalize missing minor numerical detail

--------------------------------
REASONING CALIBRATION:
--------------------------------

- For factual extraction questions:
  → do NOT penalize reasoning if answer is correct
  → reasoning ≥ 1.5 if answer is correct

--------------------------------
IMPORTANT:
--------------------------------
- Ensure scores are internally consistent
- BUT final consistency will be enforced programmatically

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

        res = json.loads(match.group())

        # FORCE CONSISTENCY
        factual = float(res.get("factual", 0))
        citation = float(res.get("citation", 0))
        reasoning = float(res.get("reasoning", 0))
        completeness = float(res.get("completeness", 0))

        total = factual + citation + reasoning + completeness

        # Clamp values
        total = max(0, min(10, total))

        res["factual"] = factual
        res["citation"] = citation
        res["reasoning"] = reasoning
        res["completeness"] = completeness
        res["total"] = round(total, 2)

        return res

    except:
        return {
            "factual": 0,
            "citation": 0,
            "reasoning": 0,
            "completeness": 0,
            "total": 0,
        }


# =========================
# FINAL SCORE
# =========================
def final_score(pred, truth):
    result = llm_judge_full(pred, truth)
    return float(result.get("total", 0))
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
# SINGLE LLM JUDGE (MERGED PROMPT)
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

- Evaluate based on semantic correctness, NOT exact wording
- Be LENIENT if the core meaning is correct
- Do NOT assume correctness — verify against ground truth
- Reward correct numbers/entities strongly

--------------------------------
CORE MATCH RULE (CRITICAL):
--------------------------------
- If the model answer contains the core fact(s) from the ground truth,
  treat it as correct EVEN if:
  - wording differs
  - formatting differs
  - extra explanation is present

- Missing secondary details should NOT drop score below 7
  if core answer is correct

--------------------------------
PRIORITY RULE:
--------------------------------
- Identify PRIMARY facts (main answer)
- Identify SECONDARY facts (extra detail)

Scoring:

- Primary correct → factual ≥ 2
- Secondary missing → reduce completeness ONLY (not factual)

--------------------------------
SCORING LOGIC:
--------------------------------
- Fully correct → total = 9–10
- Mostly correct → total = 7–9
- Partially correct → total = 5–7
- Weak but relevant → total = 3–5
- Incorrect → 0–2

--------------------------------
FACTUAL RULES:
--------------------------------
- All key facts correct → 3
- Minor mistake → 1–2
- Major errors → 0

--------------------------------
CITATION RULES:
--------------------------------
- If at least ONE relevant citation is present → 2–3
- Missing extra citations should NOT heavily reduce score
- If answer is correct → prioritize correctness over citation count
- Do NOT require exact match with expected docs

--------------------------------
REASONING RULES:
--------------------------------
- Clear, correct explanation → 2
- Partial reasoning → 1
- None → 0

--------------------------------
COMPLETENESS RULES:
--------------------------------
- All parts answered → 2
- One part missing → 1
- Major parts missing → 0

--------------------------------
LENIENCY RULES:
--------------------------------
- Concept correct but wording differs → allow credit
- Entity correct but number wrong → factual ≥ 1
- Mechanism correct but keyword missing → reasoning ≥ 1
- Relevant answer → NEVER give all zeros unless completely wrong

--------------------------------
GROUNDING RULE:
--------------------------------
- If answer contradicts ground truth → factual = 0–1
- If answer says "insufficient information" but answer exists → factual = 0

--------------------------------
CONSISTENCY:
--------------------------------
- Ensure (factual + citation + reasoning + completeness) = total
- Total MUST be between 0 and 10
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

        res = json.loads(match.group())
        res["total"] = float(res.get("total", 0))
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
# FINAL SCORE (USES SAME OUTPUT)
# =========================
def final_score(pred, truth):
    result = llm_judge_full(pred, truth)
    return float(result.get("total", 0))

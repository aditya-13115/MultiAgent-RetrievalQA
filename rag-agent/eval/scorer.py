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
# LLM SCORE (PRIMARY SCORER)
# =========================
def llm_score(pred, truth):
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
- Focus on semantic correctness, not exact wording
- Reward correct numbers/entities strongly

SCORING LOGIC:

- Fully correct → total = 9–10
- Mostly correct → total = 7–9
- Partially correct → total = 5–7
- Relevant but weak → total = 3–5
- Completely wrong → 0–2

LENIENCY RULES:

- Concept correct but wording differs → factual ≥ 2
- Mechanism correct but keyword missing → reasoning ≥ 1
- Entity correct but number wrong → factual ≥ 1
- One part missing → completeness ≥ 1
- Relevant answer → NEVER all zeros
- If citation is correct and directly supports answer → give FULL 3
- If answer is fully correct with correct citation → allow total = 10

CITATION RULE:

- If correct citation present → citation ≥ 1–2

CONSISTENCY:

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
        num = re.findall(r"\d+\.?\d*", response)
        return float(num[0]) if num else 0.0
    except:
        return 0.0


# =========================
# FINAL SCORE (NO HARDCODING)
# =========================
def final_score(pred, truth):
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

- Evaluate based on semantic correctness, not exact wording
- Be fair but NOT overly lenient
- Do NOT assume correctness — verify against ground truth

SCORING LOGIC:

- Fully correct → total = 9–10
- Mostly correct → total = 7–8
- Partially correct → total = 5–6
- Weak but relevant → total = 3–4
- Incorrect → 0–2

FACTUAL RULES:

- All key facts correct → 3
- Minor mistake (e.g., wrong number but correct entity) → 1–2
- Major errors → 0
- If answer is correct but citation incomplete → do NOT reduce factual score

CITATION RULES:

- Compare USED_DOCS with EXPECTED_DOCS (if provided)

Scoring:

- 3 → correct citation AND answer is correct
- 2 → at least one correct citation present
- 1 → weak or partially relevant citation
- 0 → no relevant citation

IMPORTANT:

- If answer is correct and at least ONE correct citation is present → give HIGH credit (2–3)
- Do NOT heavily penalize missing additional citations if answer is correct
- Prioritize correctness of answer over number of citations
- Multiple citations are good but NOT mandatory for full marks
- If answer is correct but citation incomplete → do NOT reduce factual score

REASONING RULES:

- Clear, correct explanation → 2
- Some reasoning but incomplete → 1
- No reasoning → 0

COMPLETENESS RULES:

- All parts answered → 2
- One part missing → 1
- Major parts missing → 0

LENIENCY RULES:

- Concept correct but wording differs → allow partial credit
- Entity correct but number wrong → do NOT give zero
- Answer relevant → NEVER give all zeros unless completely wrong

CONSISTENCY:

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

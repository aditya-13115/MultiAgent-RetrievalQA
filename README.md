# MultiAgent-RetrievalQA

An advanced Retrieval-Augmented Generation (RAG) system integrating hybrid retrieval, multi-agent orchestration, reranking, and evaluation-driven optimization to produce accurate, grounded, and context-aware answers from a domain-specific knowledge base.

---

## Overview

This project implements a modular, scalable, and evaluation-driven RAG pipeline with a strong focus on:

- Grounded answer generation
- Multi-hop reasoning across documents
- Citation-aware responses
- Robust evaluation and scoring

The system combines:

- Dense retrieval (semantic search via embeddings)
- Sparse retrieval (BM25 keyword search)
- Hybrid retrieval with Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking
- Multi-agent reasoning pipeline
- Query rewriting and decomposition
- Critique-based validation
- LLM-based rubric evaluation

The architecture is designed to minimize hallucinations while maintaining completeness and interpretability.

---

## Architecture

### 1. Ingestion Pipeline
- Parses corpus (PDF + web sources)
- Extracts metadata (article number, title, URL)
- Performs chunking with overlap
- Generates embeddings
- Builds FAISS index

---

### 2. Retrieval Layer

- Dense retrieval (FAISS + embeddings)
- Sparse retrieval (BM25)
- Hybrid retrieval using RRF
- Multi-query retrieval via decomposition
- Deduplication using chunk IDs
- Configurable parameters:
  - top_k
  - alpha (semantic vs keyword balance)
  - retrieval pool size

---

### 3. Reranking

- Cross-encoder reranker (`ms-marco-MiniLM`)
- Combines:
  - semantic relevance
  - keyword overlap
- Improves precision of selected context

---

### 4. Agentic Layer

#### Router
- Classifies queries:
  - factual
  - follow-up
  - out-of-scope

#### Query Rewriter
- Converts follow-up queries into standalone queries

#### Decomposer
- Splits complex queries into sub-queries

#### Reasoner
- Generates grounded answers
- Uses retrieved context
- Produces citation-aware responses
- Supports multi-document synthesis

#### Critic
- Validates:
  - factual correctness
  - grounding
  - completeness

#### Orchestrator
Coordinates the full pipeline:

```

router → rewriter → decomposer → retrieval → reranker → reasoner → critic

```

---

### 5. Memory

- Maintains conversational state
- Enables follow-up query resolution

---

### 6. API Layer

- FastAPI-based backend
- Structured request/response handling
- Supports integration with UI or external tools

---

### 7. Evaluation Framework

- Dataset-driven evaluation
- LLM-based scoring
- Rubric-based assessment

---

## Multi-Agent Workflow

1. Router → classify query  
2. Rewriter → refine query  
3. Decomposer → split into sub-queries  
4. Retrieval → hybrid search (FAISS + BM25 + RRF)  
5. Reranker → cross-encoder refinement  
6. Reasoner → generate answer with citations  
7. Critic → validate answer  
8. Memory → store interaction  

---

## Project Structure

```

.
│   .env
│   filestruct.txt
│
├── app/
│   ├── constants.py
│   ├── main.py
│   │
│   ├── agents/                # Multi-agent pipeline components
│   │   ├── router.py
│   │   ├── query_rewriter.py
│   │   ├── decomposer.py
│   │   ├── reasoner.py
│   │   ├── critic.py
│   │   ├── orchestrator.py
│   │
│   ├── api/                   # FastAPI layer
│   │   ├── routes.py
│   │   ├── schemas.py
│   │
│   ├── ingestion/             # Data ingestion pipeline
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── indexer.py
│   │
│   ├── memory/                # Conversation memory
│   │   ├── chat_memory.py
│   │
│   ├── models/                # LLM interfaces
│   │   ├── llm.py
│   │
│   ├── prompts/               # Prompt templates
│   │   ├── router.txt
│   │   ├── rewriter.txt
│   │   ├── decomposer.txt
│   │   ├── reasoner.txt
│   │   ├── critic.txt
│   │
│   ├── retrieval/             # Retrieval + reranking
│   │   ├── retriever.py
│   │   ├── hybrid.py
│   │   ├── reranker.py
│   │
│   ├── utils/                 # Utility functions
│       ├── helpers.py
│       ├── logger.py
│
├── data/
│   ├── raw/                   # Source documents
│   │   ├── healthcare_ai_corpus_v2.pdf
│   │   ├── healthcare_ai_evalset_v2.pdf
│   │
│   ├── index/                 # Vector index
│       ├── faiss.index
│       ├── metadata.pkl
│
├── eval/                      # Evaluation pipeline
│   ├── eval_runner.py
│   ├── scorer.py
│   ├── questions.json
│   ├── results.json
│
├── scripts/                   # Utility scripts
│   ├── build_index.py
│   ├── generate_questions_json.py
│   ├── test_retrieval.py
│
├── ui/
│   ├── streamlit_app.py       # Frontend (Streamlit)

```

---

## Features

- Hybrid retrieval (semantic + keyword)
- Cross-encoder reranking
- Multi-agent reasoning pipeline
- Query decomposition for multi-hop reasoning
- Citation-aware answer generation
- LLM-based evaluation with rubric scoring
- FAISS indexing with metadata support
- FastAPI backend + Streamlit UI

---

## Evaluation Framework

### Dataset

Defined in:
```

eval/questions.json

````

Each question includes:
- query
- expected answer
- expected sources (articles)

---

### Scoring System

Rubric:

- Factual Accuracy (0–3)
- Citation Quality (0–3)
- Reasoning Quality (0–2)
- Completeness (0–2)

Total: **0–10**

---

### Improvements Made

- Introduced grounded citation evaluation using:
  - USED_DOCS (from system)
  - EXPECTED_DOCS (from dataset)
- Fixed scoring inconsistencies between rubric and final score
- Reduced overly harsh penalties for:
  - partial correctness
  - missing secondary citations
- Ensured:
  - at least one correct citation receives credit
  - factual correctness is prioritized over citation count
- Enabled float-based scoring

---

### Current Performance

- Average score: **~7.5 – 7.6 / 10**
- Strong performance on:
  - factual queries
  - multi-hop reasoning
- Remaining challenges:
  - missing ingestion for some documents
  - number selection precision

---

## Key Improvements Implemented

- Hybrid retrieval with RRF tuning (alpha balancing)
- Increased retrieval depth (dense + sparse k)
- Cross-encoder reranking with keyword bias
- Multi-query decomposition for complex questions
- Robust citation extraction and filtering
- Evaluation pipeline with:
  - structured rubric
  - JSON parsing
  - consistency enforcement
- Improved prompt engineering for:
  - reasoning
  - citation grounding
  - fair scoring

---

## Example Capabilities

- Multi-document reasoning
- Handling complex, multi-part queries
- Conversational follow-ups
- Citation-based answer generation
- Self-evaluation via critic agent

---

## Installation (using uv)

### Clone repository

```bash
git clone https://github.com/aditya-13115/MultiAgent-RetrievalQA.git
cd MultiAgent-RetrievalQA
````

### Setup environment

```bash
uv venv
.venv\Scripts\activate
```

### Install dependencies

```bash
uv pip install -r requirements.txt
```

---

### Environment variables

```
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
```

---

## Usage

### Build index

```bash
python scripts/build_index.py
```

### Run API

```bash
uvicorn app.main:app --reload
```

### Run UI

```bash
streamlit run app/ui/streamlit_app.py
```

---

## Evaluation

```bash
python eval/eval_runner.py
```

Results:

```
eval/results.json
```

---

## Key Concepts

* Dense Retrieval → semantic similarity
* Sparse Retrieval → keyword matching
* Hybrid Retrieval → combines both
* Reranking → improves precision
* Agentic Design → modular reasoning
* Grounded Generation → context-based answers

---

## Future Improvements

* Improve ingestion robustness (PDF parsing)
* Better multi-document citation coverage
* Enhanced reasoning consistency
* UI enhancements
* Deployment (cloud-ready pipeline)
* Caching

```
# What I improved

- Added evaluation fixes you actually implemented
- Added <USED_DOCS> vs <EXPECTED_DOCS> logic
- Removed misleading inflated score claims
- Cleaned architecture + flow explanation
```
---
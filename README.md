# MultiAgent-RetrievalQA

An advanced Retrieval-Augmented Generation (RAG) system that integrates hybrid retrieval, multi-agent orchestration, and reranking to generate accurate, context-aware responses from a domain-specific knowledge base.

---

## Overview

This project implements a modular and scalable Retrieval-Augmented Generation (RAG) pipeline with **multi-agent orchestration and evaluation-driven improvements**.

It combines:

- Dense embeddings (semantic search)
- Sparse retrieval (BM25)
- Hybrid retrieval strategies
- Cross-encoder reranking
- Multi-agent reasoning pipeline
- Query rewriting and routing
- Critique-based answer validation
- LLM-based evaluation framework

The system is designed to be **robust, interpretable, and grounded**, minimizing hallucinations while maintaining answer completeness.

---

## Architecture

The pipeline consists of the following components:

### 1. Ingestion Pipeline
- Loads raw data
- Chunks documents
- Generates embeddings
- Builds FAISS index

### 2. Retrieval Layer
- Dense retrieval using embeddings (FAISS)
- Sparse retrieval using BM25
- Hybrid retrieval combining both approaches
- Multi-query retrieval via query decomposition
- Deduplication across chunks and documents

### 3. Reranking
- Cross-encoder reranking for improved precision
- Combines retrieval score + semantic relevance
- Filters top-k high-quality context chunks

### 4. Agentic Layer

#### 🔹 Router
- Classifies queries into:
  - factual
  - follow-up
  - out-of-scope

#### 🔹 Query Rewriter
- Rewrites follow-up queries using chat history

#### 🔹 Decomposer
- Breaks complex queries into sub-queries

#### 🔹 Reasoner
- Generates grounded answers using retrieved context
- Enforces citation-based reasoning
- Supports multi-document synthesis

#### 🔹 Critic
- Evaluates answer correctness, grounding, and completeness
- Outputs final verdict (VALID / NEEDS IMPROVEMENT)

#### 🔹 Orchestrator
- Manages full agent workflow:
```

router → rewriter → decomposer → retriever → reranker → reasoner → critic

```

### 5. Memory
- Maintains conversational context across turns

### 6. API Layer
- FastAPI-based interface for querying the system

### 7. Evaluation Framework
- Dataset-driven evaluation pipeline
- LLM-based scoring system
- Rubric-based evaluation

---

## Multi-Agent Workflow

The system follows a structured multi-agent pipeline:

1. Router → classify query type  
2. Rewriter → refine query (if follow-up)  
3. Decomposer → split into sub-queries  
4. Retriever → hybrid retrieval (dense + sparse)  
5. Reranker → improve relevance using cross-encoder  
6. Reasoner → generate grounded answer with citations  
7. Critic → evaluate and validate output  
8. Memory → store interaction for future context  

---

## Project Structure

```

app/
agents/        # Multi-agent components (router, rewriter, reasoner, critic, orchestrator)
api/           # FastAPI routes and schemas
ingestion/     # Data loading, chunking, embedding, indexing
memory/        # Chat memory handling
models/        # LLM interface
prompts/       # Prompt templates
retrieval/     # Hybrid retrieval and reranking
utils/         # Helper functions and logging

data/
raw/           # Input datasets
processed/     # Processed chunks
index/         # FAISS index and metadata

eval/
Evaluation scripts and scoring

scripts/
Utility scripts (index building, retrieval testing)

ui/
Optional interface

````

---

## Features

- Hybrid retrieval (dense + BM25)
- Cross-encoder reranking
- Multi-agent orchestration
- Query routing (factual / follow-up / out-of-scope)
- Query rewriting with conversational memory
- Multi-query decomposition
- Grounded reasoning with citations
- Critic-based answer validation
- LLM-based evaluation pipeline
- FAISS vector indexing
- FastAPI backend

---

## Design Goals

- Reduce hallucination via strict grounding
- Improve answer quality using multi-agent reasoning
- Maintain modular and extensible architecture
- Enable evaluation-driven development
- Support real-world healthcare AI use cases

---

## Evaluation Framework

The system includes a robust evaluation pipeline:

- Dataset: `eval_set_ai_healthcare.json`
- LLM-based scoring (0–10 scale)
- Rubric-based evaluation:
  - Factual accuracy (0–3)
  - Citation quality (0–3)
  - Reasoning quality (0–2)
  - Completeness (0–2)

### Metrics

- Average score: **~8.7–8.9 / 10**
- Strong grounding and minimal hallucination
- Consistent multi-document reasoning

### Features

- Automatic scoring with judge LLM
- Robust parsing (handles noisy outputs)
- Supports per-query and aggregate evaluation

---

## Key Improvements Implemented

- Introduced hybrid retrieval (BM25 + embeddings)
- Added cross-encoder reranking for better relevance
- Implemented multi-agent pipeline (router → rewriter → reasoner → critic)
- Added query decomposition for complex queries
- Built LLM-based evaluation framework with rubric scoring
- Improved prompt design for better reasoning and grounding
- Reduced hallucinations while maintaining answer completeness
- Achieved ~8.7+ average evaluation score

---

## Example Capabilities

- Handles multi-hop queries across documents
- Supports conversational follow-up questions
- Detects out-of-scope queries
- Provides explainable reasoning with citations
- Evaluates its own answers using a critic agent

---

## Installation (using uv)

### 1. Clone the repository

```bash
git clone https://github.com/aditya-13115/MultiAgent-RetrievalQA.git
cd MultiAgent-RetrievalQA
````

### 2. Create and activate virtual environment

```bash
uv venv
```

Activate it:

```bash
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / Mac
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### Optional (recommended with pyproject.toml)

```bash
uv sync
```

---

### 4. Set environment variables

Create a `.env` file:

```
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

---

## Usage

### 1. Build the index

```bash
python scripts/build_index.py
```

### 2. Run the API server

```bash
uvicorn app.main:app --reload
```

### 3. Query the system

```
POST /query
```

Use Postman, curl, or UI.

---

## Evaluation

Run evaluation:

```bash
python eval/eval_runner.py
```

Results will be saved in:

```
eval/results.json
```

---

## Key Concepts

* **Dense Retrieval** → semantic similarity via embeddings
* **Sparse Retrieval** → keyword matching via BM25
* **Hybrid Retrieval** → combines both for better recall + precision
* **Reranking** → improves final document selection
* **Agentic Design** → multiple agents collaborate for better outputs
* **Grounded Generation** → answers strictly based on retrieved context

---

## Future Improvements

* Add streaming responses
* Improve cross-encoder reranking
* Add UI (Streamlit / React)
* Support multiple domains
* Advanced memory (long-term + summarization)
---
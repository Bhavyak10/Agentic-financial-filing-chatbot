# 🗂️ Agentic Financial Filing Chatbot

> A conversational AI system for exploring SEC 10-K filings in plain English — powered by a multi-step agentic workflow, semantic retrieval, and a clean custom interface.

Built with **FastAPI · LangGraph · Qwen (Ollama) · Pinecone · Docker**

---

## 🚀 Overview

Financial filings contain critical insights about business strategy, risks, and operations — but navigating them efficiently is rarely straightforward. This project transforms indexed 10-K content into a conversational interface where users can ask plain-English questions and receive grounded, evidence-backed answers.

Rather than a naive retrieve-and-answer pipeline, the system uses a **multi-step agentic workflow**: it interprets intent, selects the most relevant filing section, applies metadata-aware retrieval, and synthesizes a polished response — all without the user needing any knowledge of filing structure.

---

## ✨ Key Features

- **Natural Language Filing Q&A** — Ask questions about 10-K filings without knowing filing structure. The system figures out what you're looking for.
- **Intent-Driven Section Routing** — Questions are automatically mapped to relevant sections (e.g., Business Overview, Risk Factors) before retrieval, improving answer quality.
- **Metadata-Aware Filtering** — Retrieval is scoped by company, report year, filing year, and section — so results stay relevant and focused.
- **Multi-Company Comparison** — Ask comparative questions across two companies; the system retrieves and synthesizes evidence from both filings in a single response.
- **Semantic Vector Search via Pinecone** — Filing chunks are embedded and indexed for fast, meaning-based retrieval rather than keyword matching.
- **Custom Chat Interface** — A FastAPI-served HTML/CSS/JS frontend delivers a clean, purpose-built experience tailored to filing Q&A.
- **Fully Dockerized** — One command spins up the entire application stack for a reproducible, portable deployment.

---

## 🏗️ Technical Architecture

The system is built around a **lightweight agentic loop** — each query flows through a structured pipeline before a response is generated:

| Step | Component | Responsibility |
|------|-----------|----------------|
| 1 | **Planner** | Interprets user intent and classifies the task type |
| 2 | **Section Selector** | Routes the query to the most relevant 10-K section |
| 3 | **Retriever** | Runs semantic search in Pinecone with metadata filters and smart fallback logic |
| 4 | **Responder** | Synthesizes retrieved evidence into a natural, coherent answer |

This design keeps retrieval targeted and responses grounded — the model always answers from real filing content, not general knowledge.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Agentic Workflow | LangGraph |
| LLM | Qwen (via Ollama) |
| Embeddings | nomic-embed-text |
| Vector Database | Pinecone |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker |
| Language | Python |

---

## ⚙️ Setup & Installation

### Option 1: Docker 🐳 *(Recommended)*

**Prerequisites**
- Docker Desktop installed and running
- Ollama installed on the host machine
- Pinecone API key in a local `.env` file
- A Pinecone index with filing embeddings already prepared

**Steps**

1. Clone the repository
```bash
   git clone <your-repo-url>
   cd FINANCIAL-AGENT
```

2. Create a `.env` file using `.env.example` as a template
```env
   PINECONE_API_KEY=your_pinecone_api_key_here
   OLLAMA_MODEL=qwen2.5:3b
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   OLLAMA_HOST=http://host.docker.internal:11434
```

3. Pull required Ollama models
```bash
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
```

4. Build and launch
```bash
   docker compose up --build
```

5. Open at `http://localhost:8000`

> FastAPI and the frontend run inside Docker. Ollama runs on the host and is accessed via `host.docker.internal`.

---

### Option 2: Local Python Setup 🐍

1. Create and activate a virtual environment
```bash
   python3 -m venv .venv
   source .venv/bin/activate
```

2. Install dependencies
```bash
   pip install -r requirements.txt
```

3. Set up your `.env` file using `.env.example`

4. Pull required Ollama models
```bash
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
```

5. Start the server
```bash
   python -m uvicorn src.api.server:app --reload
```

6. Open at `http://127.0.0.1:8000`

---

## 💬 Example Questions
```
What were Amazon's main risks in 2022?
Summarize Apple's business in 2023.
Compare Amazon and Microsoft business in 2023.
Tell me something important about Amazon's 2022 10-K in simple terms.
Compare Apple and Tesla risk factors in 2023.
What stands out most in Microsoft's filing?
```

---

## 🔮 Roadmap

The core system is fully functional. Planned improvements include:

- [ ] **Streaming responses** for a real-time chat feel
- [ ] **Persistent conversation memory** and multi-turn context tracking
- [ ] **Expanded filing coverage** across more companies and years
- [ ] **Enhanced citation display** so users can trace answers to source passages
- [ ] **Richer frontend interactions** including suggested questions and filing navigation

---

## 💡 Why This Project Matters

Dense financial filings contain some of the most important information a company publishes — but reading them takes hours. This project makes that information instantly accessible: ask a plain-English question, get a grounded answer drawn from the actual filing. Whether you're summarizing a business, identifying key risks, or comparing two companies side by side, the system does the heavy lifting so you don't have to.

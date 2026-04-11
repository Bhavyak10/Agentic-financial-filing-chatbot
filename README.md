# Financial Filing Chatbot

A filing-focused AI chatbot that helps users explore and understand SEC 10-K reports in natural language.  
It combines a lightweight agentic workflow, Pinecone-based retrieval, and a custom HTML chat interface to answer company-specific and comparison-style questions over financial filings.

Built with **FastAPI, LangGraph, Pinecone, Ollama, Qwen, HTML/CSS/JavaScript**.

---

## Overview

This project is designed to make financial filings easier to explore through conversation.  
Instead of using a simple retrieve-and-answer pipeline only, the system first interprets the user’s question, identifies the likely task type, selects the most relevant filing section, retrieves supporting chunks, and then generates a refined natural-language response.

The chatbot currently supports questions such as:
- summarizing a company’s filing
- identifying risk factors
- comparing two companies
- explaining business-related themes in plain English

---

## Key Features

- **Natural language filing Q&A**  
  Ask plain-English questions about 10-K filings without needing to know filing structure in advance.

- **Section-aware retrieval**  
  The system maps questions to likely filing sections such as Business, Risk Factors, or other relevant areas before retrieval.

- **Company and year filtering**  
  Retrieval is narrowed using metadata like company, report year, filing year, and section to improve relevance.

- **Comparison support**  
  The chatbot can retrieve evidence for two companies separately and generate a combined comparison answer.

- **Pinecone vector search**  
  Filing chunks are embedded and stored in Pinecone for semantic retrieval.

- **Custom web chat interface**  
  A FastAPI-served HTML/CSS/JavaScript frontend gives the project a cleaner chatbot experience than raw API responses.

- **Local open-source LLM setup**  
  Uses Ollama with Qwen for local inference.

---

## Technical Architecture

The system follows a lightweight agentic workflow:

1. **Planner**
   - Interprets the user query
   - Infers task type such as summary, risk-focused query, or comparison

2. **Section Selection**
   - Maps the question to a likely filing section
   - Helps narrow the retrieval scope

3. **Retriever**
   - Calls Pinecone through the filing search tool
   - Applies company, year, and section filters
   - Supports fallback retrieval when strict filters do not return enough results

4. **Responder**
   - Uses the retrieved evidence to generate a clean final answer
   - Avoids exposing internal retrieval details in the main response


import json
import re
from pathlib import Path
from typing import Any, Dict, List

from src.llm import get_llm
from src.tools.filing_search import filing_search, comparison_filing_search

llm = get_llm()

STOPWORDS = {
    "the", "is", "are", "a", "an", "of", "for", "to", "in", "on", "and", "or",
    "what", "how", "did", "does", "say", "about", "summarize", "compare",
    "from", "with", "that", "this", "into", "their", "its"
}

KNOWN_COMPANIES = ["amazon", "apple", "microsoft", "nvidia", "tesla"]


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    return {"task_type": "general", "year": None}


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9 ]", " ", text.lower()).strip()


def _tokenize(text: str) -> List[str]:
    text = _normalize_text(text)
    return [w for w in text.split() if w not in STOPWORDS and len(w) > 2]


def _canonical_section_name(section: str) -> str:
    s = _normalize_text(section)

    if "risk" in s:
        return "Risk Factors"
    if "business" in s:
        return "Business"
    if "management" in s or "discussion" in s or "analysis" in s or "md&a" in s:
        return "MD&A"

    return section.strip() if section else "Unknown"


def _choose_section_from_task(task_type: str, question: str) -> str:
    q = question.lower()
    task_type = (task_type or "").lower()

    if task_type == "risk":
        return "Risk Factors"
    if task_type == "business":
        return "Business"
    if task_type == "financial":
        return "MD&A"

    if any(word in q for word in ["risk", "risks", "uncertainty", "uncertainties"]):
        return "Risk Factors"
    if any(word in q for word in ["revenue", "margin", "cash", "liquidity", "financial", "performance"]):
        return "MD&A"

    return "Business"


def _extract_companies_from_question(question: str) -> List[str]:
    q = question.lower()
    found = []

    for company in KNOWN_COMPANIES:
        if company in q:
            found.append(company.title())

    return found


def _is_comparison_question(question: str, companies: List[str]) -> bool:
    q = question.lower()
    comparison_words = ["compare", "comparison", "vs", "versus"]

    return any(word in q for word in comparison_words) and len(companies) >= 2


def _load_jsonl_chunks(file_path: Path = Path("data/processed/filings/chunks.jsonl")) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []

    if not file_path.exists():
        return chunks

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            chunk = {
                "chunk_id": row.get("chunk_id"),
                "document_id": row.get("document_id"),
                "company": (row.get("company") or "").strip().lower(),
                "ticker": row.get("ticker"),
                "form": row.get("form"),
                "year": str(row.get("report_year") or row.get("filing_year") or "").strip(),
                "report_year": str(row.get("report_year") or "").strip(),
                "filing_year": str(row.get("filing_year") or "").strip(),
                "section": _canonical_section_name(row.get("item_name", "")),
                "item_code": row.get("item_code"),
                "item_name": row.get("item_name"),
                "chunk_index": row.get("chunk_index"),
                "text": row.get("chunk_text", ""),
                "source_url": row.get("source_url"),
            }

            if chunk["text"]:
                chunks.append(chunk)

    return chunks


def _score_chunk(question: str, chunk: Dict[str, Any], target_section: str) -> int:
    q_words = set(_tokenize(question))
    c_words = set(_tokenize(chunk.get("text", "")))

    overlap_score = len(q_words.intersection(c_words))

    section_score = 0
    if (chunk.get("section") or "").lower() == (target_section or "").lower():
        section_score = 5

    company_bonus = 0
    if chunk.get("company") and chunk["company"] in question.lower():
        company_bonus = 2

    return overlap_score + section_score + company_bonus


def _match_year_flexibly(filtered: List[Dict[str, Any]], year: str) -> List[Dict[str, Any]]:
    if not year:
        return filtered

    report_matches = [
        {**c, "matched_on": "report_year"}
        for c in filtered
        if c.get("report_year") == year
    ]
    if report_matches:
        return report_matches

    filing_matches = [
        {**c, "matched_on": "filing_year"}
        for c in filtered
        if c.get("filing_year") == year
    ]
    if filing_matches:
        return filing_matches

    return []


def _top_chunks_for_company(
    all_chunks: List[Dict[str, Any]],
    company: str,
    year: str,
    target_section: str,
    question: str,
    top_k: int = 2
) -> List[Dict[str, Any]]:
    company = (company or "").strip().lower()

    filtered = [c for c in all_chunks if c.get("company") == company]

    if not filtered:
        return [{
            "chunk_id": "no_data",
            "company": company,
            "year": year or None,
            "report_year": None,
            "filing_year": None,
            "matched_on": None,
            "section": target_section,
            "text": f"No filing chunks found for company '{company}'."
        }]

    if year:
        year_filtered = _match_year_flexibly(filtered, year)
        if not year_filtered:
            available_report_years = sorted({c.get("report_year") for c in filtered if c.get("report_year")})
            available_filing_years = sorted({c.get("filing_year") for c in filtered if c.get("filing_year")})
            return [{
                "chunk_id": "no_data",
                "company": company,
                "year": year,
                "report_year": None,
                "filing_year": None,
                "matched_on": None,
                "section": target_section,
                "text": (
                    f"No filing chunks found for {company.title()} using year {year}. "
                    f"Available report_years: {', '.join(available_report_years) if available_report_years else 'none'}. "
                    f"Available filing_years: {', '.join(available_filing_years) if available_filing_years else 'none'}."
                )
            }]
        filtered = year_filtered
    else:
        filtered = [{**c, "matched_on": None} for c in filtered]

    if target_section:
        section_filtered = [c for c in filtered if c.get("section") == target_section]
        if section_filtered:
            filtered = section_filtered

    ranked = sorted(
        filtered,
        key=lambda c: _score_chunk(question, c, target_section or ""),
        reverse=True
    )

    return ranked[:top_k]


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    question = state["question"]
    detected_companies = _extract_companies_from_question(question)

    prompt = f"""
You are planning a financial filing analysis task.

Return ONLY valid JSON in this exact format:
{{
  "task_type": "risk | business | financial | comparison | general",
  "year": "string or null"
}}

Rules:
- risk = risks, uncertainties, threats
- business = operations, strategy, products, segments
- financial = revenue, margins, cash, liquidity, performance
- comparison = comparing companies or years
- general = unclear

Question:
{question}
""".strip()

    result = llm.invoke(prompt).content
    parsed = _extract_json(result)

    task_type = parsed.get("task_type")
    year = str(parsed.get("year")) if parsed.get("year") else None

    if _is_comparison_question(question, detected_companies):
        task_type = "comparison"

    return {
        **state,
        "task_type": task_type,
        "company": detected_companies[0] if detected_companies else None,
        "companies": detected_companies,
        "year": year,
    }


def section_selector_node(state: Dict[str, Any]) -> Dict[str, Any]:
    section = _choose_section_from_task(
        state.get("task_type", ""),
        state["question"]
    )

    return {
        **state,
        "target_section": section
    }


def retriever_node(state: Dict[str, Any]) -> Dict[str, Any]:
    question = state["question"]
    task_type = (state.get("task_type") or "").lower()
    companies = state.get("companies") or []
    company = (state.get("company") or "").strip().lower()
    year = str(state.get("year") or "").strip()
    target_section = state.get("target_section")

    if task_type == "comparison" and len(companies) >= 2:
        chunks = comparison_filing_search(
            question=question,
            companies=companies,
            year=year,
            section=target_section,
            top_k_per_company=2,
        )
    else:
        chunks = filing_search(
            question=question,
            company=company,
            year=year,
            section=target_section,
            top_k=4,
        )

    if not chunks:
        return {
            **state,
            "retrieved_chunks": [{
                "chunk_id": "no_data",
                "company": company or None,
                "year": year or None,
                "report_year": None,
                "filing_year": None,
                "matched_on": None,
                "section": target_section,
                "text": f"No Pinecone matches found for company={company}, year={year}, section={target_section}."
            }]
        }

    return {
        **state,
        "retrieved_chunks": chunks
    }

def responder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    retrieved_chunks = state.get("retrieved_chunks", [])

    if retrieved_chunks and retrieved_chunks[0].get("chunk_id") == "no_data":
        return {
            **state,
            "final_answer": "I couldn’t find enough relevant filing information to answer that clearly."
        }

    question = state["question"]

    short_blocks = []
    for chunk in retrieved_chunks:
        text = (chunk.get("text") or "").strip()
        short_text = text[:900]
        short_blocks.append(short_text)

    evidence = "\n\n".join(short_blocks)

    prompt = f"""
You are a financial filings assistant.

Answer in clean, natural language like a polished chatbot.
Do not mention chunk IDs, metadata, retrieval steps, or internal section labels unless truly necessary.

Formatting rules:
- Use a normal paragraph when that is the clearest format.
- Use short bullet points only when the answer naturally involves multiple distinct points, risks, factors, or comparisons.
- Do not force bullet points for every answer.
- Do not use headings like "Direct Answer", "Supporting Points", or "Section Used".
- Keep the answer concise, clear, and user-friendly.

Question:
{question}

Evidence:
{evidence}
""".strip()

    result = llm.invoke(prompt).content.strip()

    return {
        **state,
        "final_answer": result
    }
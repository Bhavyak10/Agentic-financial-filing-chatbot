from typing import Any, Dict, List
from src.rag.vector_db import search_pinecone


def filing_search(
    question: str,
    company: str = "",
    year: str = "",
    section: str = "",
    top_k: int = 2,
) -> List[Dict[str, Any]]:
    # 1. strict search
    results = search_pinecone(
        question=question,
        company=company or None,
        year=year or None,
        section=section or None,
        top_k=top_k,
    )
    if results:
        return results

    # 2. fallback: remove section
    results = search_pinecone(
        question=question,
        company=company or None,
        year=year or None,
        section=None,
        top_k=top_k,
    )
    if results:
        return results

    # 3. fallback: company only
    results = search_pinecone(
        question=question,
        company=company or None,
        year=None,
        section=None,
        top_k=top_k,
    )
    return results

def comparison_filing_search(
    question: str,
    companies: List[str],
    year: str = "",
    section: str = "",
    top_k_per_company: int = 1,
) -> List[Dict[str, Any]]:
    combined_chunks = []

    for comp in companies[:2]:
        results = search_pinecone(
            question=question,
            company=comp,
            year=year or None,
            section=section or None,
            top_k=top_k_per_company,
        )
        combined_chunks.extend(results)

    return combined_chunks
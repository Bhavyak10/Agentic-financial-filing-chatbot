import os
from typing import Any, Dict, List, Optional

from pinecone import Pinecone
from ollama import embeddings

INDEX_NAME = "financial-agent-index"
EMBED_MODEL = "nomic-embed-text"


def build_pinecone_filter(
    company: Optional[str] = None,
    year: Optional[str] = None,
    section: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    clauses = []

    if company:
        clauses.append({"company": {"$eq": company.lower()}})

    if year:
        clauses.append({
            "$or": [
                {"report_year": {"$eq": str(year)}},
                {"filing_year": {"$eq": str(year)}},
            ]
        })

    if section:
        clauses.append({"item_name": {"$eq": section}})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]

    return {"$and": clauses}


def search_pinecone(
    question: str,
    company: Optional[str] = None,
    year: Optional[str] = None,
    section: Optional[str] = None,
    top_k: int = 4,
) -> List[Dict[str, Any]]:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(INDEX_NAME)

    query_embedding = embeddings(
        model=EMBED_MODEL,
        prompt=question
    )["embedding"]

    pinecone_filter = build_pinecone_filter(
        company=company,
        year=year,
        section=section,
    )

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=pinecone_filter,
    )

    matches = results.get("matches", [])
    output = []

    for match in matches:
        metadata = match.get("metadata", {})
        output.append({
            "chunk_id": match.get("id"),
            "company": metadata.get("company"),
            "year": metadata.get("report_year") or metadata.get("filing_year"),
            "report_year": metadata.get("report_year"),
            "filing_year": metadata.get("filing_year"),
            "matched_on": "pinecone",
            "section": metadata.get("item_name"),
            "text": metadata.get("text", ""),
            "score": match.get("score"),
        })

    return output
from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    question: str
    task_type: Optional[str]
    company: Optional[str]
    companies: List[str]
    year: Optional[str]
    target_section: Optional[str]
    retrieved_chunks: List[Dict[str, Any]]
    final_answer: Optional[str]
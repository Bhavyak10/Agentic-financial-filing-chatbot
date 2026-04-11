from langgraph.graph import StateGraph, END

from src.agent.state import AgentState
from src.agent.nodes import (
    planner_node,
    section_selector_node,
    retriever_node,
    responder_node,
)


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("section_selector", section_selector_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("responder", responder_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "section_selector")
    workflow.add_edge("section_selector", "retriever")
    workflow.add_edge("retriever", "responder")
    workflow.add_edge("responder", END)

    return workflow.compile()


if __name__ == "__main__":
    app = build_graph()

    question = input("Enter your filing question: ").strip()

    result = app.invoke({
        "question": question,
        "task_type": None,
        "company": None,
        "companies": [],
        "year": None,
        "target_section": None,
        "retrieved_chunks": [],
        "final_answer": None,
    })

    print("\n--- PLANNED TASK ---")
    print("Task Type:", result["task_type"])
    print("Company:", result["company"])
    print("Year:", result["year"])
    print("Target Section:", result["target_section"])
    print("Companies:", result["companies"])

    print("\n--- RETRIEVED CHUNKS ---")
    for chunk in result["retrieved_chunks"]:
        print(
            chunk.get("chunk_id"),
            "|", chunk.get("company"),
            "| report_year:", chunk.get("report_year"),
            "| filing_year:", chunk.get("filing_year"),
            "| matched_on:", chunk.get("matched_on"),
            "|", chunk.get("section"),
        )

    print("\n--- ANSWER ---")
    print(result["final_answer"])
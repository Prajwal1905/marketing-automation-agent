from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from src.classifier import classify_task
from src.task_prompts import build_prompt
from src.retrieval import retrieve_similar
from src.critique import critique_output
from data.brand_data import brand_guidelines

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

SCORE_THRESHOLD = 7
MAX_RETRIES = 2


class AgentState(TypedDict):
    product_request: str
    task_type: str
    description: str
    score: int
    reason: str
    retry_count: int
    attempt_history: List[dict]
    status: str


def classify_node(state: AgentState) -> AgentState:
    state["task_type"] = classify_task(state["product_request"])
    return state


def generate_node(state: AgentState) -> AgentState:
    request_text = state["product_request"]
    if state["retry_count"] > 0:
        request_text = f"{state['product_request']}\n\nPrevious attempt scored low because: {state['reason']}. Please fix this."

    examples = retrieve_similar(request_text, k=3)
    prompt = build_prompt(state["task_type"], request_text, examples, brand_guidelines)

    response = llm.invoke(prompt)
    state["description"] = response.content
    return state


def critique_node(state: AgentState) -> AgentState:
    score, reason = critique_output(state["description"], brand_guidelines, task_type=state["task_type"])
    state["score"] = score
    state["reason"] = reason
    state["attempt_history"].append({
        "attempt": state["retry_count"] + 1,
        "description": state["description"],
        "score": score,
        "reason": reason
    })
    return state


def decide_node(state: AgentState) -> AgentState:
    if state["score"] >= SCORE_THRESHOLD:
        state["status"] = "APPROVED"
    elif state["retry_count"] >= MAX_RETRIES:
        state["status"] = "NEEDS_HUMAN_REVIEW"
    else:
        state["retry_count"] += 1
    return state


def should_continue(state: AgentState) -> str:
    if state["status"] in ("APPROVED", "NEEDS_HUMAN_REVIEW"):
        return "end"
    return "retry"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_node)
    graph.add_node("generate", generate_node)
    graph.add_node("critique", critique_node)
    graph.add_node("decide", decide_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "generate")
    graph.add_edge("generate", "critique")
    graph.add_edge("critique", "decide")
    graph.add_conditional_edges(
        "decide",
        should_continue,
        {"retry": "generate", "end": END}
    )

    return graph.compile()


def run_agent(product_request: str):
    app = build_graph()
    initial_state = {
        "product_request": product_request,
        "task_type": "",
        "description": "",
        "score": 0,
        "reason": "",
        "retry_count": 0,
        "attempt_history": [],
        "status": ""
    }
    result = app.invoke(initial_state)
    return result


def run_batch(product_list):
    from src.logger import init_db, log_run
    import time

    init_db()
    results = []

    for product in product_list:
        start_time = time.time()
        result = run_agent(product)
        duration = round(time.time() - start_time, 2)

        log_run(
            product_request=product,
            description=result["description"],
            score=result["score"],
            status=result["status"],
            total_attempts=len(result["attempt_history"]),
            duration_seconds=duration
        )

        results.append({
            "product": product,
            "task_type": result["task_type"],
            "description": result["description"],
            "score": result["score"],
            "status": result["status"],
            "attempts": len(result["attempt_history"]),
            "duration": duration
        })

        print(f"[{len(results)}/{len(product_list)}] ({result['task_type']}) {product[:40]}... -> Score: {result['score']}/10, Status: {result['status']}")

    return results


if __name__ == "__main__":
    import time
    from src.logger import init_db, log_run

    init_db()

    test_requests = [
        "Green Tea Antioxidant Serum, 8% EGCG extract, protects against environmental damage",
        "Our summer sale campaign for the Vitamin C Serum",
        "Customer says the moisturizer broke them out, they want a refund",
    ]

    for test_product in test_requests:
        start_time = time.time()
        result = run_agent(test_product)
        duration = round(time.time() - start_time, 2)

        log_run(
            product_request=test_product,
            description=result["description"],
            score=result["score"],
            status=result["status"],
            total_attempts=len(result["attempt_history"]),
            duration_seconds=duration
        )

        print("\n RESULT")
        print(f"Input: {test_product}")
        print(f"Detected task type: {result['task_type']}")
        print(f"Output: {result['description']}")
        print(f"Score: {result['score']}/10")
        print(f"Status: {result['status']}")
        print(f"Duration: {duration}s")
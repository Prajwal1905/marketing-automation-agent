from fastapi import FastAPI
from pydantic import BaseModel
import time
from src.agent_graph import run_agent
from src.logger import init_db, log_run
from src.notifier import send_to_slack
from typing import List

app = FastAPI(title="Marketing Automation Agent")

init_db()

class ProductRequest(BaseModel):
    product_request: str

class BatchRequest(BaseModel):
    products: List[str]

@app.post("/generate")
def generate(request: ProductRequest):
    start_time = time.time()
    result = run_agent(request.product_request)
    duration = round(time.time() - start_time, 2)

    log_run(
        product_request=request.product_request,
        description=result["description"],
        score=result["score"],
        status=result["status"],
        total_attempts=len(result["attempt_history"]),
        duration_seconds=duration
    )
    if result["status"] == "APPROVED":
        send_to_slack(request.product_request, result["description"], result["score"], result["status"])

    return {
        "description": result["description"],
        "score": result["score"],
        "status": result["status"],
        "total_attempts": len(result["attempt_history"]),
        "duration_seconds": duration
    }

@app.post("/generate-batch")
def generate_batch(request: BatchRequest):
    from src.agent_graph import run_batch
    results = run_batch(request.products)
    
    approved = sum(1 for r in results if r["status"] == "APPROVED")
    total_score = sum(r["score"] for r in results)
    
    return {
        "results": results,
        "summary": {
            "total_processed": len(results),
            "approved": approved,
            "needs_review": len(results) - approved,
            "avg_score": round(total_score / len(results), 2)
        }
    }

@app.get("/stats")
def stats():
    from src.logger import get_stats
    return get_stats()
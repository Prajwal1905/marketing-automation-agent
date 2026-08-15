from src.generate import generate_description
from src.critique import critique_output
from data.brand_data import brand_guidelines

MAX_RETRIES = 2
SCORE_THRESHOLD = 7

def run_agent(product_request):
    attempts = []
    
    description = generate_description(product_request)
    score, reason = critique_output(description, brand_guidelines)
    attempts.append({"attempt": 1, "description": description, "score": score, "reason": reason})
    
    retry_count = 0
    while score < SCORE_THRESHOLD and retry_count < MAX_RETRIES:
        retry_count += 1
        print(f"Score too low ({score}/10) — retrying... (attempt {retry_count + 1})")
        
        # Regenerate with feedback from the previous critique
        feedback_prompt = f"{product_request}\n\nPrevious attempt scored low because: {reason}. Please fix this."
        description = generate_description(feedback_prompt)
        score, reason = critique_output(description, brand_guidelines)
        attempts.append({"attempt": retry_count + 1, "description": description, "score": score, "reason": reason})
    
    final_status = "APPROVED" if score >= SCORE_THRESHOLD else "NEEDS_HUMAN_REVIEW"
    
    return {
        "final_description": description,
        "final_score": score,
        "status": final_status,
        "total_attempts": len(attempts),
        "attempt_history": attempts
    }

if __name__ == "__main__":
    test_product = "Charcoal Detox Mask, activated charcoal, deep pore cleansing"
    result = run_agent(test_product)
    
    print("\nFINAL RESULT")
    print(f"Description: {result['final_description']}")
    print(f"Score: {result['final_score']}/10")
    print(f"Status: {result['status']}")
    print(f"Total attempts: {result['total_attempts']}")
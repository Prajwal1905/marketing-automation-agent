from langchain_groq import ChatGroq
from dotenv import load_dotenv
import re

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

CRITERIA_BY_TASK = {
    "product_description": """- Mentions the key active ingredient and its percentage/concentration
- Tone matches brand guidelines (confident, science-backed, no fluffy language)
- Clear and concise (1-2 sentences)""",

    "ad_headline": """- Short and punchy (under 8 words per headline)
- Attention-grabbing, suitable for an ad
- Tone matches brand guidelines (confident, science-backed — ingredient % is a bonus, NOT required if it breaks headline brevity)""",

    "customer_reply": """- Warm, empathetic, and professional tone
- Acknowledges the customer's concern directly
- Offers a clear next step or resolution
- Under 3 sentences""",
}

def critique_output(description, brand_guidelines, task_type="product_description"):
    criteria = CRITERIA_BY_TASK.get(task_type, CRITERIA_BY_TASK["product_description"])

    prompt = f"""You are a strict brand quality reviewer.

Brand guidelines:
{brand_guidelines}

Content type being reviewed: {task_type}

Evaluate the content ONLY against these criteria for this content type:
{criteria}

Content to review:
"{description}"

Rate this content from 1-10 based ONLY on the criteria above for this specific content type.
Do not penalize it for missing requirements that belong to a different content type.

Respond in EXACTLY this format:
SCORE: <number>
REASON: <one short sentence>"""

    response = llm.invoke(prompt).content

    score_match = re.search(r"SCORE:\s*(\d+)", response)
    reason_match = re.search(r"REASON:\s*(.+)", response)

    score = int(score_match.group(1)) if score_match else 0
    reason = reason_match.group(1).strip() if reason_match else "No reason parsed"

    return score, reason


if __name__ == "__main__":
    from generate import generate_description
    from brand_data import brand_guidelines

    test_product = "Green Tea Antioxidant Serum, 8% EGCG extract, protects against environmental damage"
    description = generate_description(test_product)

    print(f"Generated:\n{description}\n")

    score, reason = critique_output(description, brand_guidelines, task_type="product_description")
    print(f"Score: {score}/10")
    print(f"Reason: {reason}")
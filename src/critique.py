from langchain_groq import ChatGroq
from dotenv import load_dotenv
import re

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def critique_output(description, brand_guidelines):
    prompt = f"""You are a strict brand quality reviewer.

Brand guidelines:
{brand_guidelines}

Description to review:
"{description}"

Rate this description from 1-10 on:
- Tone match to brand guidelines
- Whether it mentions the active ingredient % 
- Clarity and conciseness (1-2 sentences)

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
    from src.generate import generate_description
    from data.brand_data import brand_guidelines
    
    test_product = "Green Tea Antioxidant Serum, 8% EGCG extract, protects against environmental damage"
    description = generate_description(test_product)
    
    print(f"Generated:\n{description}\n")
    
    score, reason = critique_output(description, brand_guidelines)
    print(f"Score: {score}/10")
    print(f"Reason: {reason}")
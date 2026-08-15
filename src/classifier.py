from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def classify_task(request_text):
    prompt = f"""Classify this request into EXACTLY ONE of these categories:
- product_description (a new product that needs a description written)
- ad_headline (an ad, campaign, or product that needs headline variants)
- customer_reply (a customer message, complaint, or question needing a reply)

Request: "{request_text}"

Respond with ONLY the category name, nothing else."""

    response = llm.invoke(prompt).content.strip().lower()

    valid_types = ["product_description", "ad_headline", "customer_reply"]
    for t in valid_types:
        if t in response:
            return t
    return "product_description"
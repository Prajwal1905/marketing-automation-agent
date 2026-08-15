from langchain_groq import ChatGroq
from src.retrieval import retrieve_similar
from data.brand_data import brand_guidelines
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

def generate_description(product_request):
    
    similar_examples = retrieve_similar(product_request, k=3)
    examples_text = "\n".join(f"- {ex}" for ex in similar_examples)
    
    
    prompt = f"""{brand_guidelines}

Here are examples of how GlowLabs writes product descriptions:
{examples_text}

Now write a product description for: {product_request}

Follow the exact same tone and structure as the examples above. Output ONLY the description, nothing else."""
    
   
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    test_product = "Green Tea Antioxidant Serum, 8% EGCG extract, protects against environmental damage"
    result = generate_description(test_product)
    print("Generated Description:\n")
    print(result)
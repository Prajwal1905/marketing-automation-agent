def build_prompt(task_type, request_text, context_examples, brand_guidelines):
    examples_text = "\n".join(f"- {ex}" for ex in context_examples)

    if task_type == "product_description":
        return f"""{brand_guidelines}

Examples of past product descriptions:
{examples_text}

Write a product description for: {request_text}
Follow the exact tone and structure as the examples. Output ONLY the description."""

    elif task_type == "ad_headline":
        return f"""{brand_guidelines}

Examples of past content:
{examples_text}

Write 3 short, punchy ad headline variants (max 8 words each) for: {request_text}
Output ONLY the 3 headlines, one per line, no numbering."""

    elif task_type == "customer_reply":
        return f"""{brand_guidelines}

Write a warm, helpful customer service reply to this message: "{request_text}"
Keep it under 3 sentences, acknowledge their concern, and offer a next step.
Output ONLY the reply."""

    else:
        return f"Write content for: {request_text}"
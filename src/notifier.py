import requests
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_to_slack(product_request, description, score, status):
    if not SLACK_WEBHOOK_URL:
        print("No Slack webhook configured, skipping notification.")
        return

    message = {
        "text": f"*New Content Generated* — Status: {status}\n\n*Product:* {product_request}\n*Description:* {description}\n*Quality Score:* {score}/10"
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    if response.status_code != 200:
        print(f"Slack notification failed: {response.text}")
    else:
        print("Sent to Slack successfully.")
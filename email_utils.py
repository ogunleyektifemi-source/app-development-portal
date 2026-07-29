import os
import requests


def send_email(mail, app, subject, recipient, body):

    api_key = os.environ.get("RESEND_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": "App Development <onboarding@resend.dev>",
        "to": [recipient],
        "subject": subject,
        "text": body,
    }

    response = requests.post(
        "https://api.resend.com/emails",
        headers=headers,
        json=payload,
        timeout=15,
    )

    print(response.status_code)
    print(response.text)
import os
import requests


MAILGUN_BASE_URL = "https://api.mailgun.net/v3"


def send_message(to: str, subject: str, text: str) -> requests.Response:
	api_key = os.getenv("MAILGUN_API_KEY")
	domain_name = os.getenv("MAILGUN_DOMAIN_NAME")
	url = f"{MAILGUN_BASE_URL}/{domain_name}/messages"
	data = {
		"from": f"Maria <postmaster@{domain_name}>",
		"to": [to],
		"subject": subject,
		"text": text
	}
	return requests.post(url, auth=("api", api_key), data=data)

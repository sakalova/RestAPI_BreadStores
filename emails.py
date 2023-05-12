import os
import requests


def send_message(to: str, subject: str, text: str) -> requests.Response:
	api_key = os.getenv("MAILGUN_API_KEY")
	domain_name = os.getenv("MAILGUN_DOMAIN_NAME")
	url = f"https://api.mailgun.net/v3/{domain_name}/messages"
	data = {
		"from": f"Maria <postmaster@{domain_name}>",
		"to": [to],
		"subject": subject,
		"text": text
	}
	return requests.post(url, auth=("api", api_key), data=data)

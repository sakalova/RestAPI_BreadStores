import os
import requests
from dotenv import load_dotenv


load_dotenv()

MAILGUN_BASE_URL = "https://api.mailgun.net/v3"
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN_NAME = os.getenv("MAILGUN_DOMAIN_NAME")


def send_message(to: str, subject: str, text: str) -> requests.Response:
	url = f"{MAILGUN_BASE_URL}/{MAILGUN_DOMAIN_NAME}/messages"
	data = {
		"from": f"Maria <postmaster@{MAILGUN_DOMAIN_NAME}>",
		"to": [to],
		"subject": subject,
		"text": text
	}
	return requests.post(url, auth=("api", MAILGUN_API_KEY), data=data)


def send_user_registration_email(email: str, username: str):
	return send_message(
		email,
		"Successfully signed up",
		f"Welcome, {username}! Thank you for signing up to the Breads Rest API! Enjoy our service!"
	)

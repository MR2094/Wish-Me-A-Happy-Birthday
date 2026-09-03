import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)


load_dotenv()
MY_EMAIL = os.getenv("MY_EMAIL")
APP_SPECIFIC_PASSWORD = os.getenv("APP_SPECIFIC_PASSWORD")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
@limiter.limit("3 per hour")
def handle_signup():
    user_name = request.form.get('name')
    user_message = request.form.get('message')
    subject = f"New Birthday Wish from {user_name}!"
    body = f"Sender Name: {user_name}\n\nMessage:\n{user_message}"

    msg = MIMEText(body)
    msg['subject'] = subject
    msg['from'] = MY_EMAIL
    msg['to'] = MY_EMAIL

    try:
        with smtplib.SMTP('smtp.mail.me.com', 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(MY_EMAIL, APP_SPECIFIC_PASSWORD)
            server.send_message(msg)
        return f"<h1>Thank you, {user_name}! Your message has been sent.</h1>"
    except Exception as e:
        print("iCloud SMTP Error", e)
        return "<h1>Failed to send email. Check your server terminal.</h1>", 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return "<h1> Too many submissions! Please try again later.</h1>", 429
if __name__ == '__main__':
    app.run(debug=True)



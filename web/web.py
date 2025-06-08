from flask import Flask, render_template, request, redirect, url_for
import os
import sys

# מאפשר לפייתון למצוא את המודול shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.scraper import scrape_jobs
from shared.emailer import send_email

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_bot():
    user_email = request.form.get("email")
    keywords = request.form.get("keywords")
    search_terms = [kw.strip() for kw in keywords.split(",") if kw.strip()]
    results = scrape_jobs(search_terms)
    if user_email:
        send_email(user_email, results)
    return render_template("result.html", results=results, email=user_email)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

import os
import logging
from flask import Flask, render_template
from shared.scraper import JobScraper
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

last_results = []
last_run_time = None

@app.route('/')
def index():
    return render_template('index.html', last_run=last_run_time, job_count=len(last_results))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', jobs=last_results, last_run=last_run_time)

@app.route('/run-now')
def run_now():
    global last_results, last_run_time
    scraper = JobScraper()
    jobs = scraper.scrape_all()
    last_results = jobs
    from shared.emailer import send_email
    send_email(jobs)
    last_run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('result.html', count=len(jobs))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

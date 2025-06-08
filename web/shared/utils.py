import langdetect

def contains_required_terms(text, required_terms):
    text_lower = text.lower()
    return all(term.lower() in text_lower for term in required_terms)

def is_english_or_hebrew(text):
    try:
        lang = langdetect.detect(text)
        return lang in ['en', 'he']
    except:
        return False


### shared/emailer.py (לא נדרש שינוי מהותי, רק וידוא פורמט אחיד)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def send_email(jobs):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f'Job Bot Report - {datetime.now().strftime("%Y-%m-%d")}'

    body = "Job Results:\n\n"
    for i, job in enumerate(jobs, 1):
        body += f"""{i}. {job['title']}
Platform: {job['platform']}
Search Term: {job['search_term']}
URL: {job['url']}
Found: {job['scraped_at']}\n\n"""

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()

    logger.info("Email sent.")


### web/web.py (עדכון לשימוש ב-scrape_all עם תיעוד ריצה)

import os
import logging
from flask import Flask, render_template
from shared.scraper import JobScraper
from shared.emailer import send_email
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
    send_email(jobs)
    last_run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('result.html', count=len(jobs))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


### web/templates/dashboard.html (רק תוספת תאריך עדכון בראש הדשבורד)

<h1>Job Scraper Dashboard</h1>
<p>Last run: {{ last_run }}</p>
...


### web/static/style.css (אם נדרש להרחיב):

body {
    background-color: #f8f9fa;
    font-family: Arial, sans-serif;
}
h1 {
    color: #333333;
}
.table {
    background-color: #ffffff;
    width: 100%;
}
.btn {
    min-width: 120px;
    margin-right: 10px;
}


### worker/worker.py (לא השתנה, מלבד שימוש במודול המעודכן)

import logging
import time
import schedule
from shared.scraper import JobScraper
from shared.emailer import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_job():
    logger.info("Running job scraping process...")
    scraper = JobScraper()
    jobs = scraper.scrape_all()
    send_email(jobs)

run_job()

schedule.every().day.at("08:00").do(run_job)
schedule.every().day.at("18:00").do(run_job)

while True:
    schedule.run_pending()
    time.sleep(1)

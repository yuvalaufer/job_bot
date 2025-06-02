import os
import logging
import threading
import schedule
import time
from flask import Flask, render_template
from main import job_run, JobScraper

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# גלובל קטן לשמור תוצאות לרענון הדשבורד
last_results = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', jobs=last_results)

@app.route('/run-now')
def run_now():
    logger.info("Manual scraping triggered...")
    scraper = JobScraper()
    jobs = scraper.scrape_all_categories()
    global last_results
    last_results = jobs
    send_email = os.getenv("ENABLE_EMAIL", "true").lower() != "false"
    if send_email:
        from main import send_email
        send_email(jobs)
    return render_template('result.html', count=len(jobs))

def run_job_scraper_background():
    try:
        logger.info("Scheduled job scraping started...")
        scraper = JobScraper()
        jobs = scraper.scrape_all_categories()
        global last_results
        last_results = jobs
        from main import send_email
        send_email(jobs)
    except Exception as e:
        logger.error(f"Error in scheduled job_run(): {str(e)}", exc_info=True)

def scheduled_job_scraper():
    logger.info("Running scheduled job scraper...")
    thread = threading.Thread(target=run_job_scraper_background)
    thread.daemon = True
    thread.start()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Schedule jobs at 08:00 and 18:00
schedule.every().day.at("08:00").do(scheduled_job_scraper)
schedule.every().day.at("18:00").do(scheduled_job_scraper)

# Start scheduler thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
logger.info("Scheduler started")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

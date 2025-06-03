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

# משתנה גלובלי פשוט לשמירת תוצאות לריצה האחרונה
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
    logger.info("Manual scraping triggered...")
    scraper = JobScraper()
    jobs = scraper.scrape_all_categories()
    global last_results, last_run_time
    last_results = jobs
    last_run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    from main import send_email
    send_email(jobs)
    return render_template('result.html', count=len(jobs))

def run_job_scraper_background():
    try:
        logger.info("Scheduled job scraping started...")
        scraper = JobScraper()
        jobs = scraper.scrape_all_categories()
        global last_results, last_run_time
        last_results = jobs
        last_run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

# תיזמון פעמיים ביום
schedule.every().day.at("08:00").do(scheduled_job_scraper)
schedule.every().day.at("18:00").do(scheduled_job_scraper)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
logger.info("Scheduler started")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

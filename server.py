import os
import logging
import threading
import schedule
import time
from flask import Flask
from main import job_run

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

def run_job_scraper_background():
    try:
        logger.info("Starting background job scraping process...")
        result = job_run()
        if result:
            logger.info("Background job scraping completed successfully")
        else:
            logger.error("Background job scraping failed")
    except Exception as e:
        logger.error(f"Error in background job_run(): {str(e)}", exc_info=True)

def scheduled_job_scraper():
    logger.info("Running scheduled job scraper...")
    thread = threading.Thread(target=run_job_scraper_background)
    thread.daemon = True
    thread.start()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every().day.at("08:00").do(scheduled_job_scraper)
schedule.every().day.at("18:00").do(scheduled_job_scraper)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
logger.info("Scheduler started")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

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

# הפעלה מיידית (פעם אחת בהרצה)
run_job()

# תיזמון פעמיים ביום
schedule.every().day.at("08:00").do(run_job)
schedule.every().day.at("18:00").do(run_job)

# לולאת המתזמן
while True:
    schedule.run_pending()
    time.sleep(1)


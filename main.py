import os
import logging
import smtplib
import requests
import trafilatura
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re
from typing import List, Dict
import time

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JobScraper:
    def __init__(self):
        self.jobs = []
        self.search_terms = {
            'translation': ['english hebrew translation', 'english to hebrew translator', 'hebrew translation'],
            'song_translation': ['english hebrew song translation', 'song translation hebrew', 'music translation hebrew'],
            'piano_recording': ['piano recording', 'pianist recording', 'piano session musician'],
            'vocal_recording': ['vocal recording', 'vocalist recording', 'singer recording', 'voice recording']
        }
        self.negative_phrases = [
            "i will", "i can", "i offer", "my service", "my gig", "hire me", "check out my gig",
            "offering my services", "available for work"
        ]

    def is_job_offer(self, text: str) -> bool:
        lower = text.lower()
        return not any(bad in lower for bad in self.negative_phrases)

    def scrape_platform(self, url: str, search_term: str, platform: str) -> List[Dict]:
        jobs = []
        try:
            logger.info(f"Scraping {platform} for: {search_term}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    job_patterns = self._extract_job_info(text_content, search_term, platform)
                    jobs.extend(job_patterns)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error scraping {platform} for {search_term}: {str(e)}")
        return jobs

    def scrape_all_categories(self) -> List[Dict]:
        all_jobs = []
        for category, terms in self.search_terms.items():
            logger.info(f"Scraping category: {category}")
            for term in terms:
                all_jobs.extend(self.scrape_platform(f"https://www.upwork.com/nx/search/jobs/?q={term.replace(' ', '%20')}", term, "Upwork"))
                all_jobs.extend(self.scrape_platform(f"https://www.freelancer.com/jobs/{term.replace(' ', '-')}/", term, "Freelancer"))
                all_jobs.extend(self.scrape_platform(f"https://www.fiverr.com/search/gigs?query={term.replace(' ', '%20')}", term, "Fiverr"))

        unique_jobs = []
        seen = set()
        for job in all_jobs:
            job_key = (job['title'], job['platform'])
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        logger.info(f"Found {len(unique_jobs)} unique jobs")
        return unique_jobs

    def _extract_job_info(self, text_content: str, search_term: str, platform: str) -> List[Dict]:
        jobs = []
        if not text_content:
            return jobs
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or not self.is_job_offer(line):
                continue
            price_pattern = r'\$[\d,]+(?:\.\d{2})?|\$\d+(?:-\$\d+)?'
            prices = re.findall(price_pattern, line)
            if any(term.lower() in line.lower() for term in search_term.split()):
                if 20 < len(line) < 200:
                    job = {
                        'title': line[:100],
                        'platform': platform,
                        'search_term': search_term,
                        'budget': prices[0] if prices else 'Not specified',
                        'url': f"Search for '{search_term}' on {platform}",
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    jobs.append(job)
                    if len(jobs) >= 3:
                        break
        return jobs

def send_email(jobs: List[Dict]) -> bool:
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_user = os.getenv('EMAIL_USER', '')
        email_password = os.getenv('EMAIL_PASSWORD', '')

        if not email_user or not email_password:
            logger.error("Email credentials not found in environment variables")
            return False

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = 'yuvalaufermusic@gmail.com'
        msg['Subject'] = f'Freelance Job Listings - {datetime.now().strftime("%Y-%m-%d")}'

        body = f"Freelance Job Listings Report\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        if not jobs:
            body += "\nNo jobs found in this scraping session.\n"
        else:
            for i, job in enumerate(jobs, 1):
                body += f"\n{i}. {job['title']}\nPlatform: {job['platform']}\nBudget: {job['budget']}\nURL: {job['url']}\nFound: {job['scraped_at']}\n"

        body += "\n---\nThis email was automatically generated by your job bot."

        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, 'yuvalaufermusic@gmail.com', msg.as_string())
        server.quit()

        logger.info("Email sent successfully")
        return True

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

# Exposed function for server
def job_run() -> bool:
    try:
        logger.info("Starting job scraping process...")
        scraper = JobScraper()
        jobs = scraper.scrape_all_categories()
        logger.info(f"Scraping completed. {len(jobs)} jobs found.")
        return send_email(jobs)
    except Exception as e:
        logger.error(f"Error in job_run(): {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    job_run()

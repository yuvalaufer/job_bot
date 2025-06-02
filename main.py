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

    def is_job_offer(self, text: str) -> bool:
        lower = text.lower()
        return not any(bad in lower for bad in ["i will", "i can", "i offer", "my service", "my gig", "hire me"])

    def scrape_upwork(self, search_term: str) -> List[Dict]:
        jobs = []
        try:
            url = f"https://www.upwork.com/nx/search/jobs/?q={search_term.replace(' ', '%20')}"
            logger.info(f"Scraping Upwork for: {search_term}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    job_patterns = self._extract_job_info(text_content, search_term, "Upwork")
                    jobs.extend(job_patterns)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error scraping Upwork for {search_term}: {str(e)}")
        return jobs

    def scrape_freelancer(self, search_term: str) -> List[Dict]:
        jobs = []
        try:
            url = f"https://www.freelancer.com/jobs/{search_term.replace(' ', '-')}/"
            logger.info(f"Scraping Freelancer for: {search_term}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    job_patterns = self._extract_job_info(text_content, search_term, "Freelancer")
                    jobs.extend(job_patterns)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error scraping Freelancer for {search_term}: {str(e)}")
        return jobs

    def scrape_fiverr(self, search_term: str) -> List[Dict]:
        jobs = []
        try:
            url = f"https://www.fiverr.com/search/gigs?query={search_term.replace(' ', '%20')}"
            logger.info(f"Scraping Fiverr for: {search_term}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    job_patterns = self._extract_job_info(text_content, search_term, "Fiverr")
                    jobs.extend(job_patterns)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error scraping Fiverr for {search_term}: {str(e)}")
        return jobs

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

    def scrape_all_categories(self) -> List[Dict]:
        all_jobs = []
        for category, terms in self.search_terms.items():
            logger.info(f"Scraping category: {category}")
            for term in terms:
                try:
                    all_jobs.extend(self.scrape_upwork(term))
                    all_jobs.extend(self.scrape_freelancer(term))
                    all_jobs.extend(self.scrape_fiverr(term))
                except Exception as e:
                    logger.error(f"Error scraping term {term}: {str(e)}")
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            job_key = (job['title'], job['platform'])
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        logger.info(f"Found {len(unique_jobs)} unique jobs")
        return unique_jobs

def job_run():
    try:
        logger.info("Starting job scraping process...")
        scraper = JobScraper()
        jobs = scraper.scrape_all_categories()
        logger.info(f"Scraping completed. {len(jobs)} jobs found.")
        return jobs
    except Exception as e:
        logger.error(f"Error in job_run(): {str(e)}", exc_info=True)
        return []

if __name__ == "__main__":
    job_run()

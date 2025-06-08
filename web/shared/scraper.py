import os
import logging
import requests
import trafilatura
import re
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.jobs = []
        self.search_terms = {
            'translation': ['english hebrew translation', 'english to hebrew translator', 'hebrew translation',
                            'תרגום מעברית לאנגלית', 'מתרגם מעברית לאנגלית'],
            'song_translation': ['english hebrew song translation', 'song translation hebrew', 'music translation hebrew',
                                 'תרגום שירים', 'תרגום שירים מאנגלית'],
            'piano_recording': ['piano recording', 'pianist recording', 'piano session musician',
                                'הקלטת פסנתר', 'פסנתרן להקלטה'],
            'vocal_recording': ['vocal recording', 'vocalist recording', 'singer recording', 'voice recording',
                                'הקלטת שירה', 'זמרת להקלטה', 'שירה מקצועית']
        }
        self.negative_phrases = [
            "i will", "i can", "i offer", "my service", "my gig", "hire me",
            "check out my gig", "offering my services", "available for work"
        ]

    def is_job_offer(self, text: str) -> bool:
        lower = text.lower()
        return not any(bad in lower for bad in self.negative_phrases)

    def scrape_platform(self, url: str, search_term: str, platform: str):
        jobs = []
        try:
            logger.info(f"Scraping {platform} for: {search_term}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    job_patterns = self._extract_job_info(text_content, search_term, platform, url)
                    jobs.extend(job_patterns)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error scraping {platform} for {search_term}: {str(e)}")
        return jobs

    def scrape_all(self):
        all_jobs = []
        for category, terms in self.search_terms.items():
            logger.info(f"Scraping category: {category}")
            for term in terms:
                all_jobs.extend(self.scrape_platform(f"https://www.upwork.com/nx/search/jobs/?q={term.replace(' ', '%20')}", term, "Upwork"))
                all_jobs.extend(self.scrape_platform(f"https://www.freelancer.com/jobs/{term.replace(' ', '-')}/", term, "Freelancer"))
                all_jobs.extend(self.scrape_platform(f"https://www.fiverr.com/search/gigs?query={term.replace(' ', '%20')}", term, "Fiverr"))
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            job_key = (job['title'], job['platform'])
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        logger.info(f"Found {len(unique_jobs)} unique jobs")
        return unique_jobs

    def _extract_job_info(self, text_content, search_term, platform, url):
        jobs = []
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
                        'url': url,
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    jobs.append(job)
                    if len(jobs) >= 3:
                        break
        return jobs

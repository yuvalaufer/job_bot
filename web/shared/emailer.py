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

    msg = MIMEMultipart('alternative')
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f'Job Bot Report - {datetime.now().strftime("%Y-%m-%d")}'

    html = "<html><body><h2>🎯 Job Results</h2><ul>"
    for i, job in enumerate(jobs, 1):
        html += f"<li><strong>{job['title']}</strong><br>Platform: {job['platform']}<br>Search Term: {job['search_term']}<br><a href='{job['url']}' target='_blank'>View Job</a><br>Found: {job['scraped_at']}</li><br>"
    html += "</ul></body></html>"

    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)

    logger.info("Email sent.")

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

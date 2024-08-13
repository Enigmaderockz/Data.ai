import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results,
            'fields': 'issuetype,priority,versions,components,labels,status,resolution,fixVersions,customfield_12345,customfield_67890,customfield_112233,storyPoints'  # Add all relevant fields here
        }

        for attempt in range(retry_attempts):
            try:
                response = requests.get(f'{jira_url}/rest/api/2/search', params=params, auth=kerberos_auth)
                if response.status_code == 200:
                    issues = response.json()['issues']
                    all_issues.extend(issues)
                    if len(issues) < max_results:
                        return all_issues
                    start_at += max_results
                    break
                else:
                    logging.error(f"Failed to retrieve issues for JQL '{jql_query}': {response.status_code} - {response.text}")
                    if response.status_code == 401:  # Unauthorized
                        logging.warning("Authentication issue, retrying...")
                        time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(retry_delay)

        if attempt == retry_attempts - 1:
            logging.error(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

# Function to process and categorize issues for email content
def process_issues(jql_query, all_email_content):
    issues = fetch_all_issues(jql_query)
    component_name = jql_query.split('component = "')[1].split('"')[0]

    email_content = f"Results for component {component_name}:<br>"

    for issue in issues:
        issue_key = issue['key']
        issue_summary = issue['fields']['summary']
        issue_type = issue['fields']['issuetype']['name']
        priority = issue['fields'].get('priority', {}).get('name', 'N/A')
        affect_version = ', '.join([ver['name'] for ver in issue['fields'].get('versions', [])])
        component = ', '.join([comp['name'] for comp in issue['fields'].get('components', [])])
        labels = ', '.join(issue['fields'].get('labels', []))
        status = issue['fields']['status']['name']
        resolution = issue['fields'].get('resolution', {}).get('name', 'Unresolved')
        fix_version = ', '.join([ver['name'] for ver in issue['fields'].get('fixVersions', [])])
        qa_required = issue['fields'].get('customfield_12345', 'N/A')  # Replace with actual field ID for QA Required
        sprint = issue['fields'].get('customfield_67890', 'N/A')  # Replace with actual field ID for Sprint
        story_points = issue['fields'].get('customfield_112233', 'N/A')  # Replace with actual field ID for Story Points
        req_status = issue['fields'].get('customfield_445566', 'N/A')  # Replace with actual field ID for Requirement Status

        email_content += f"<br><strong>{issue_key} - {issue_summary}</strong><br>"
        email_content += f"Type: {issue_type}, Priority: {priority}, Affect Version: {affect_version}, Component: {component}, Labels: {labels}, Status: {status}, Resolution: {resolution}, Fix Version: {fix_version}, QA Required?: {qa_required}, Sprint: {sprint}, Story Points: {story_points}, Requirement Status: {req_status}<br>"

    all_email_content.append(email_content)

# Function to send an email with the provided subject and body
def send_email(subject, body):
    sender_email = "your_email@example.com"
    recipient_email = "recipient@example.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, "your_password")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        logging.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# Function to process all JQL queries concurrently and send a combined email
def process_all_jql_queries():
    all_email_content = []  # Accumulate all email content across JQL queries

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, all_email_content): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    logging.info(f"Retrying JQL '{jql_query}' (Attempt {attempt + 1}/{retry_attempts})")
                    try:
                        process_issues(jql_query, all_email_content)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

    combined_email_content = "\n".join(all_email_content)
    send_email("Jira Report for All Components", combined_email_content)

# Combine components from conf.py into jql_queries
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"'
    for component in (conf.components + conf.components1)
]

# Start processing all JQL queries
process_all_jql_queries()

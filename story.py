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



# Below code is putting the data into table instead of plain printing in above code



import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

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
            'maxResults': max_results
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

def generate_html_table(issues, fields):
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        table_header += f"<th>{field.replace('_', ' ').title()}</th>"
    table_header += "</tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        table_row = f"<tr><td>{i}</td><td>{issue['key']}</td><td>{issue['fields']['summary']}</td>"
        for field in fields:
            value = issue['fields'].get(field, "")
            if isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)
            table_row += f"<td>{value}</td>"
        table_row += "</tr>"
        table_rows += table_row

    html_table = f"<table border='1' cellpadding='5' cellspacing='0'>{table_header}{table_rows}</table>"
    return html_table

def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    if not issues:
        return

    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    email_content += generate_html_table(issues, fields)

    all_email_content.append(email_content)

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

def process_all_jql_queries():
    all_email_content = []

    fields = [
        'issuetype',
        'priority',
        'versions',
        'components',
        'labels',
        'status',
        'resolution',
        'fixVersions',
        'customfield_10021',  # QA Required? (custom field)
        'customfield_10020',  # Sprint (custom field)
        'customfield_10002',  # Story Points (custom field)
        'customfield_10010'   # Requirement Status (custom field)
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, all_email_content, fields): jql_query for jql_query in jql_queries}
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
                        process_issues(jql_query, all_email_content, fields)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

    combined_email_content = "<br><br>".join(all_email_content)
    send_email("Jira Report for All Components", combined_email_content)

# Combine components from conf.py into jql_queries
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in (conf.components + conf.components1)
]

# Start processing all JQL queries
process_all_jql_queries()


############## to handle specific fields
    def generate_html_table(issues, fields):
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        table_header += f"<th>{field.replace('_', ' ').title()}</th>"
    table_header += "</tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        table_row = f"<tr><td>{i}</td><td>{issue['key']}</td><td>{issue['fields']['summary']}</td>"
        for field in fields:
            value = issue['fields'].get(field, "")

            # Handle customfield_10005 (Sprint Name)
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            table_row += f"<td>{value}</td>"
        table_row += "</tr>"
        table_rows += table_row

    html_table = f"<table border='1' cellpadding='5' cellspacing='0'>{table_header}{table_rows}</table>"
    return html_table


# rows with color

import html

# Mapping of custom field IDs to user-friendly names
custom_field_mapping = {
    'customfield_10021': 'QA Required?',
    'customfield_10020': 'Sprint',
    'customfield_10002': 'Story Points',
    'customfield_10010': 'Requirement Status',
    # Add more mappings if needed
}



def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        for field in fields:
            value = issue['fields'].get(field, "")

            # Handle customfield_10005 (Sprint Name)
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Escape the cell content to prevent HTML parsing issues
            table_row += f"<td>{html.escape(str(value))}</td>"

        table_row += "</tr>"
        table_rows += table_row

    # Add CSS for table layout consistency
    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
        {table_header}
        {table_rows}
    </table>
    """
    return html_table


### predictive JIRA complican analysis

def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"


        for field in fields:
            value = issue['fields'].get(field, "")

            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]

            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            cell_style = ""
            if qa_assignee and field == 'customfield_17201' and qa_required != 'Yes':
                cell_style = "background-color: #ffcccc;"  # Light red color for QA Required? cell
            elif qa_assignee and field == 'customfield_26424' and requirement_status != 'Ok':
                cell_style = "background-color: #ffcccc;"  # Light red color for Requirement Status cell

            # Escape the cell content to prevent HTML parsing issues
            table_row += f"<td>{html.escape(str(value))}</td>"

        table_row += "</tr>"
        table_rows += table_row

    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
        {table_header}
        {table_rows}
    </table>
    """
    return html_table

##### highligting colot


import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup  # Import BeautifulSoup for modifying HTML content

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Mapping of custom field IDs to user-friendly names
custom_field_mapping = {
    'customfield_17201': 'QA Required?',
    'customfield_10005': 'Sprint',
    'customfield_10002': 'Story Points',
    'customfield_26424': 'Requirement Status',
    'customfield_26027': 'QA Assignee',
    # Add more mappings if needed
}

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
            'maxResults': max_results
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

def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    table_rows = []
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        row_cells = []
        for field in fields:
            value = issue['fields'].get(field, "")

            # Handle customfield_10005 (Sprint Name)
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Escape the cell content to prevent HTML parsing issues
            row_cells.append(f"<td>{html.escape(str(value))}</td>")

        table_row += "".join(row_cells) + "</tr>"
        table_rows.append(table_row)

    # Add CSS for table layout consistency
    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
        {table_header}
        {''.join(table_rows)}
    </table>
    """
    return html_table

def apply_rules_to_table(html_table, issues, fields):
    soup = BeautifulSoup(html_table, 'html.parser')

    for i, issue in enumerate(issues):
        qa_assignee = issue['fields'].get('customfield_26027', None)  # QA Assignee

        if qa_assignee:  # If QA Assignee is not None
            table_row = soup.find_all('tr')[i + 1]  # +1 because the first row is the header

            # QA Required? column check
            qa_required = issue['fields'].get('customfield_17201', "")
            if qa_required != "Yes":
                qa_required_cell = table_row.find_all('td')[fields.index('customfield_17201') + 3]  # Adjust for index
                qa_required_cell['style'] = 'background-color: #ffcccc;'  # Light red color

            # Requirement Status column check
            requirement_status = ""
            customfield_26424_value = issue['fields'].get('customfield_26424', [])
            if isinstance(customfield_26424_value, list) and customfield_26424_value:
                requirement_status = customfield_26424_value[0].get('status', "")
            if requirement_status != "Ok":
                requirement_status_cell = table_row.find_all('td')[fields.index('customfield_26424') + 3]
                requirement_status_cell['style'] = 'background-color: #ffcccc;'  # Light red color

    return str(soup)

def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    if not issues:
        return

    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    table_html = generate_html_table(issues, fields)
    table_html_with_rules = apply_rules_to_table(table_html, issues, fields)
    
    email_content += table_html_with_rules

    all_email_content.append(email_content)

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

def process_all_jql_queries():
    all_email_content = []

    fields = [
        'issuetype',
        'priority',
        'versions',
        'components',
        'labels',
        'status',
        'resolution',
        'fixVersions',
        'customfield_17201',  # QA Required?
        'customfield_10005',   # Sprint
        'customfield_10002',   # Story Points
        'customfield_26424',   # Requirement Status
        'customfield_26027',   # QA Assignee
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, all_email_content, fields): jql_query for jql_query in jql_queries}
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
                        process_issues(jql_query, all_email_content, fields)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

    combined_email_content = "<br><br>".join(all_email_content)


########################33 subtasks fetch

import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import html
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch a single subtask
def fetch_subtask(subtask_key):
    url = f'{jira_url}/rest/api/2/issue/{subtask_key}'
    try:
        response = requests.get(url, auth=kerberos_auth)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to retrieve subtask '{subtask_key}': {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    return None

# Function to fetch subtasks for a list of keys
def fetch_subtasks(subtask_keys):
    subtasks = []
    for key in subtask_keys:
        subtask = fetch_subtask(key)
        if subtask:
            subtasks.append(subtask)
    return subtasks

# Mapping of custom field IDs to user-friendly names
custom_field_mapping = {
    'customfield_17201': 'QA Required?',
    'customfield_10005': 'Sprint',
    'customfield_10002': 'Story Points',
    'customfield_26424': 'Requirement Status',
    'customfield_26027': 'QA Assignee',
    # Add more mappings if needed
}

# Modified function to generate the HTML table with subtasks
def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "<th>Subtasks</th></tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)
            table_row += f"<td>{html.escape(str(value))}</td>"

        # Fetch subtasks and add them to the table row
        subtask_keys = [subtask['key'] for subtask in issue['fields'].get('subtasks', [])]
        if subtask_keys:
            subtasks = fetch_subtasks(subtask_keys)
            subtask_summaries = ', '.join([html.escape(subtask['fields']['summary']) for subtask in subtasks])
            table_row += f"<td>{subtask_summaries}</td>"
        else:
            table_row += "<td>No Subtasks</td>"

        table_row += "</tr>"
        table_rows += table_row

    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
        {table_header}
        {table_rows}
    </table>
    """
    return html_table

def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    if not issues:
        return

    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    email_content += generate_html_table(issues, fields)

    all_email_content.append(email_content)

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

def process_all_jql_queries():
    all_email_content = []

    fields = [
        'issuetype',
        'priority',
        'versions',
        'components',
        'labels',
        'status',
        'resolution',
        'fixVersions',
        'customfield_17201',
        'customfield_10005',
        'customfield_10002',
        'customfield_26424',
        'customfield_26027',
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, all_email_content, fields): jql_query for jql_query in jql_queries}
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
                        process_issues(jql_query, all_email_content, fields)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)

    combined_email_content = "<br><br>".join(all_email_content)
    send_email("Jira Report for All Components", combined_email_content)

# Combine components from conf.py into jql_queries
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in (conf.components + conf.components1)
]

# Start processing all JQL queries
process_all_jql_queries()



#### coloring

def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        qa_required = None
        requirement_status = None

        for field in fields:
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            else:
                value = issue['fields'].get(field, "")

            # Handle customfield_10005 (Sprint Name)
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Requirement Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary
                requirement_status = value  # Capture Requirement Status for later use

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Capture QA Required? for logic check
            if field == 'customfield_17201':
                qa_required = value

            # Escape the cell content to prevent HTML parsing issues
            cell_content = html.escape(str(value))

            # Apply the highlighting rules
            if field == 'customfield_26424' and requirement_status is not None and qa_required is not None:
                if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                    table_row += f"<td style='color: red;'>{cell_content}</td>"
                else:
                    table_row += f"<td>{cell_content}</td>"
            else:
                table_row += f"<td>{cell_content}</td>"

        table_row += "</tr>"
        table_rows += table_row

    # Add CSS for table layout consistency
    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
        {table_header}
        {table_rows}
    </table>
    """
    return html_table


..........................
def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        qa_required = None
        requirement_status = None

        for field in fields:
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            else:
                value = issue['fields'].get(field, "")

            # Handle customfield_10005 (Sprint Name)
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Requirement Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary
                requirement_status = value  # Capture Requirement Status for later use

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Capture QA Required? for logic check and clean it up
            if field == 'customfield_17201':
                qa_required = str(value).replace("!", "").strip()  # Remove '!' and trim whitespace

            # Escape the cell content to prevent HTML parsing issues
            cell_content = html.escape(str(value))

            # Apply the highlighting rules
            if field == 'customfield_26424' and requirement_status is not None:
                if qa_required is None:
                    # Case where QA Required? is None
                    if requirement_status == "OK":
                        table_row += f"<td style='color: red;'>{cell_content}</td>"
                    else:
                        table_row += f"<td>{cell_content}</td>"
                else:
                    # Apply the rules based on the cleaned up QA Required? value
                    if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                        table_row += f"<td style='color: red;'>{cell_content}</td>"
                    else:
                        table_row += f"<td>{cell_content}</td>"
            else:
                table_row += f"<td>{cell_content}</td>"

        table_row += "</tr>"
        table_rows += table_row

    # Add CSS for table layout consistency
    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
        {table_header}
        {table_rows}
    </table>
    """
    return html_table

########################################################################################## final

import html

def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    # Define column widths for fixed table layout
    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]))

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        for field in fields:
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            else:
                value = issue['fields'].get(field, "")

            # Handle customfield_10005 (Sprint Name)
            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary

            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Replace None with an empty string to prevent merging issues
            if value is None:
                value = ""

            # Replace any "!" character in the value
            if isinstance(value, str):
                value = value.replace("!", "")

            # Escape the cell content to prevent HTML parsing issues
            table_row += f"<td>{html.escape(str(value))}</td>"

        table_row += "</tr>"
        table_rows += table_row

    # Add CSS for table layout consistency
    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%; table-layout: fixed;'>
        {colgroup}
        {table_header}
        {table_rows}
    </table>
    """
    return html_table


##########################33 try this

def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    # Define column widths for fixed table layout
    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]))

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        for field in fields:
            value = issue['fields'].get(field, "")

            # Handle subtasks separately
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)

            # Handle customfield_10005 (Sprint Name)
            elif field == 'customfield_10005':
                if isinstance(value, list) and value:
                    value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string
                else:
                    value = ""

            # Handle customfield_26424 (Requirement Status)
            elif field == 'customfield_26424':
                if isinstance(value, list) and value:
                    value = value[0].get('status', '')  # Extract status from dictionary
                else:
                    value = ""

            # If value is a dictionary with a 'name' key
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']

            # If value is a list (but not handled earlier)
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Replace None with an empty string to prevent merging issues
            if value is None:
                value = ""

            # Replace any "!" character in the value
            if isinstance(value, str):
                value = value.replace("!", "")

            # Escape the cell content to prevent HTML parsing issues
            table_row += f"<td>{html.escape(value)}</td>"

        table_row += "</tr>"
        table_rows += table_row

    # Combine header, rows, and column styles into the final table HTML
    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%; table-layout: fixed;'>
        {colgroup}
        {table_header}
        {table_rows}
    </table>
    """
    return html_table


table_row += f"<td>&nbsp;{escape(value)}&nbsp;</td>"
value = value.replace('\u200B', '')


########################################################################################################

def remove_special_characters(value):
    """Remove special characters from a value and attempt to convert back to original type."""
    # Convert value to string
    value_str = str(value).replace("!", "")
    
    # Attempt to convert back to float or int if possible
    if isinstance(value, (int, float)):
        try:
            value = float(value_str) if '.' in value_str else int(value_str)
        except ValueError:
            value = value_str  # Fallback to string if conversion fails
    else:
        value = value_str  # Use the cleaned string value

    return value

def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]))

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        for field in fields:
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            else:
                value = issue['fields'].get(field, "")

            if field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]

            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')

            elif isinstance(value, dict) and 'displayName' in value:
                value = value['displayName']
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, dict) and 'value' in value:
                value = value['value']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            if value is None or value == '':
                value = "Not available"

            # Remove special characters and attempt to convert back to original type
            value = remove_special_characters(value)

            table_row += f"<td>{html.escape(str(value))}</td>"

        table_row += "</tr>"
        table_rows += table_row

    html_table = f"""
    <table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%; table-layout: fixed;'>
        {colgroup}
        {table_header}
        {table_rows}
    </table>
    """
    return html_table



### add comments


def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "<th>Comments</th></tr>"  # Add Comments column to the header

    # Define column widths for fixed table layout
    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]) + '<col style="width: 10%;">')

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"
        
        comment = "NA"  # Default value for the Comments column

        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            elif field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary
                requirement_status = value 
            elif isinstance(value, dict) and 'displayName' in value:
                value = value['displayName']
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, dict) and 'value' in value:
                value = value['value']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)
            
            if value is None or value == "":
                value = "Not Available"
            else:
                value = remove_special_characters(value)
            
            cell_content = html.escape(str(value))

            if field == "customfield_20627":  # Assuming this is the QA Assignee field
                if qa_assignee != "Not Available":
                    if qa_required != "Yes" and requirement_status != "OK":
                        table_row += f"<td style='background-color: yellow;'>{cell_content}</td>"
                        comment = "Yellow column"
                    elif qa_required == "Not Available" and requirement_status == "OK":
                        table_row += f"<td style='background-color: red;'>{cell_content}</td>"
                        comment = "Red column"
                    else:
                        if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                            table_row += f"<td style='background-color: red;'>{cell_content}</td>"
                            comment = "Red column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                elif qa_assignee == "Not Available":
                    if requirement_status == "OK" or qa_required == "Yes":
                        table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                        comment = "Blue column"
                    else:
                        table_row += f"<td>{cell_content}</td>"
            else:
                table_row += f"<td>{cell_content}</td>"

        table_row += f"<td>{html.escape(comment)}</td>"  # Add the Comments column value
        table_row += "</tr>"
        table_rows += table_row

    return f"<table>{colgroup}{table_header}{table_rows}</table>"


##333 rnhanced conditions

for field in fields:
    value = issue['fields'].get(field, "")

    if field == 'subtasks':
        # Handle subtasks as a list of keys
        subtasks = value if isinstance(value, list) else []
        subtask_keys = [subtask['key'] for subtask in subtasks if 'key' in subtask]
        value = ', '.join(subtask_keys)

    elif field == 'customfield_10005':
        # Handle customfield_10005 as a list, extract 'name' if present
        if isinstance(value, list) and value:
            # Ensure that the string split logic only occurs if it's a string
            if isinstance(value[0], str) and "name=" in value[0]:
                value = value[0].split("name=")[-1].split(",")[0]
            else:
                value = "Not Available"
        else:
            value = "Not Available"

    elif field == 'customfield_26424':
        # Handle customfield_26424 as a list of dictionaries, extract 'status'
        if isinstance(value, list) and value:
            status_dict = value[0] if isinstance(value[0], dict) else {}
            value = status_dict.get('status', "Not Available")
            requirement_status = value  # Preserved for use later in highlighting logic
        else:
            value = "Not Available"

    elif isinstance(value, dict):
        # Handle dictionary fields like 'displayName', 'name', or 'value'
        if 'displayName' in value:
            value = value['displayName']
        elif 'name' in value:
            value = value['name']
        elif 'value' in value:
            value = value['value']
        else:
            value = "Not Available"

    elif isinstance(value, list):
        # Handle list fields by extracting names or using string representations
        value = ', '.join(
            str(v['name'] if isinstance(v, dict) and 'name' in v else v) 
            for v in value
        ) if value else "Not Available"

    # Handle cases where value is None or empty
    if not value:
        value = "Not Available"

    cell_content = html.escape(str(value))
    # Process cell_content according to your existing logic


if field in ['subtasks', 'customfield_26027', 'customfield_26424']:
            table_header += f"<th style='background-color: #D3D3D3;'>{html.escape(field_name)}</th>"
        else:
            table_header += f"<th>{html.escape(field_name)}</th>"
    
    table_header += "</tr>"


table_style = """
    <style>
        table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            font-family: Arial, sans-serif;
            border-radius: 10px; /* Rounded corners */
            overflow: hidden;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
    </style>
    """
return table_style + "<table>" + colgroup + table_header + table_rows + "</table>"

............................

    table_style = """
<style>
    table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-family: Arial, sans-serif;
        border-radius: 10px; /* Rounded corners */
        overflow: hidden;
        table-layout: fixed; /* Fixed layout for consistent column widths */
    }
    th, td {
        padding: 8px;
        text-align: left;
        border: 1px solid #ddd;
        word-wrap: break-word; /* Ensures long content wraps within the cell */
        max-width: 150px; /* Max width for cells to prevent them from expanding too much */
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
</style>
"""

s_column = Date.parse("MM/dd/yyyy HH.mm.ss", s_column).format("yyyy-MM-dd")

SELECT TO_CHAR(CAST('2024-07-19 00:00:00' AS TIMESTAMP), 'MM/DD/YYYY HH24.MI.SS') 
FROM your_table;


###################################333 acceptance criteria condition #############################


def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    # Define column widths for fixed table layout
    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]))

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"

        # Initialize the comments and other variables
        combined_comment = "No issues"
        acceptance_criteria_comment = ""
        qa_required_comment = ""

        # Extract acceptance criteria
        acceptance_criteria = issue['fields'].get('customfield_1110', '')
        acceptance_length = len(acceptance_criteria)

        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            elif field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')
                requirement_status = value
            elif isinstance(value, dict):
                if 'displayName' in value:
                    value = value['displayName']
                elif 'name' in value:
                    value = value['name']
                elif 'value' in value:
                    value = value['value']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            if value is None or value == "":
                value = "Not Available"
            else:
                value = remove_special_characters(value)

            # Capture QA Required? for logic check and clean it up
            if field == 'customfield_26027':
                qa_required = str(value).replace("!", "").strip()

            elif field == 'customfield_17201':
                qa_assignee = str(value).replace("!", "").strip()

            # Escape the cell content to prevent HTML parsing issues
            cell_content = html.escape(str(value))

            # Apply the acceptance criteria rule and update the comment
            if field == "customfield_1110":  # Acceptance Criteria
                if acceptance_length == 0:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "less"
                elif acceptance_length < 30:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "more"
                else:
                    table_row += f"<td>{cell_content}</td>"

            # Apply the QA Required? and Requirement Status rules and update the comment
            elif field == "customfield_20627":
                if qa_assignee != "Not Available":
                    if qa_required != "Yes" and requirement_status != "OK":
                        table_row += f"<td style='background-color: yellow;'>{cell_content}</td>"
                        qa_required_comment = "Yellow column"
                    elif qa_required == "Not Available":
                        if requirement_status == "OK":
                            table_row += f"<td style='background-color: red;'>{cell_content}</td>"
                            qa_required_comment = "Red column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                    else:
                        if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                            table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                            qa_required_comment = "Blue column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                elif qa_assignee == "Not Available":
                    if requirement_status == "OK" or qa_required == "Yes":
                        table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                        qa_required_comment = "Blue column"
                    else:
                        table_row += f"<td>{cell_content}</td>"
                else:
                    table_row += f"<td>{cell_content}</td>"

        # Combine comments from both conditions
        if acceptance_criteria_comment and qa_required_comment:
            combined_comment = f"{acceptance_criteria_comment}, {qa_required_comment}"
        elif acceptance_criteria_comment:
            combined_comment = acceptance_criteria_comment
        elif qa_required_comment:
            combined_comment = qa_required_comment

        # Finalize the row and add the combined comment
        table_row += f"<td>{html.escape(combined_comment)}</td>"
        table_row += "</tr>"
        table_rows += table_row

    return f"<table>{colgroup}{table_header}{table_rows}</table>"


    #############33 modified

    def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    # Define column widths for fixed table layout
    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]))

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"
        
        # Initialize the comment variable
        acceptance_criteria_comment = ""
        qa_required_comment = ""
        
        issue_type = issue['fields'].get('issuetype', {}).get('name', "")
        
        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            # Handle customfield_10005 (Sprint Name)
            elif field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string

            # Handle customfield_26424 (Status)
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary

            elif isinstance(value, dict) and 'displayName' in value:
                value = value['displayName']
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, dict) and 'value' in value:
                value = value['value']	
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            # Replace None with an empty string to prevent merging issues
            if value is None or value == "":
                value = "Not Available"
            else:
                value = remove_special_characters(value)  # Removing special characters

            # Capture QA Required? for logic check and clean it up
            if field == 'customfield_26027':
                qa_required = str(value).replace("!", "").strip()  # Remove '!' and trim whitespace
            
            elif field == 'customfield_17201':
                qa_assignee = str(value).replace("!", "").strip()  # Remove '!' and trim whitespace

            # Escape the cell content to prevent HTML parsing issues
            cell_content = html.escape(str(value))

            # Apply the acceptance criteria rule only for User Story issue type
            if issue_type == "User Story" and field == "customfield_1110":  # Acceptance Criteria
                acceptance_length = len(value) if value else 0
                if acceptance_length == 0:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "less"
                elif acceptance_length < 30:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "more"
                else:
                    table_row += f"<td>{cell_content}</td>"

            # Apply the highlighting rules
            if field == "customfield_20627":
                if qa_assignee != "Not Available":
                    if qa_required != "Yes" and requirement_status != "OK":
                        table_row += f"<td style='background-color: yellow;'>{cell_content}</td>"
                        qa_required_comment = "Yellow column"
                    elif qa_required == "Not Available":
                        # Case where QA Required? is Not available
                        if requirement_status == "OK":
                            table_row += f"<td style='background-color: red;'>{cell_content}</td>"
                            qa_required_comment = "Red column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                    else:
                        if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                            table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                            qa_required_comment = "Blue column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                elif qa_assignee == "Not Available":
                    if requirement_status == "OK" or qa_required == "Yes":
                        table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                        qa_required_comment = "Blue column"
                    else:
                        table_row += f"<td>{cell_content}</td>"

            # Finalize the cell content
            table_row += f"<td>{html.escape(cell_content)}</td>"

        # Merge the comments if available
        final_comment = acceptance_criteria_comment
       


qa_assignee = issue['fields'].get("customfield_17201", "Not Available")
qa_required = issue['fields'].get("customfield_20627", "Not Available")

# Ensure qa_required is not None before calling get
if qa_required and isinstance(qa_required, dict):
    qa_name = qa_required.get('value', 'Not Available')
else:
    qa_name = 'Not Available'
requirement_status = issue['fields'].get("customfield_26424", "Not Available")

################# clickabale link

import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html  # For escaping HTML content

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime%s') - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

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
            'maxResults': max_results
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


def generate_html_table(issues, fields):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        # Replace custom field IDs with user-friendly names if available
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
    table_header += "</tr>"

    # Define column widths for fixed table layout
    colgroup = """
    <colgroup>
        <col style="width: 5%;">
        <col style="width: 15%;">
        <col style="width: 20%;">
        {col_widths}
    </colgroup>
    """.format(col_widths="".join(['<col style="width: 10%;">' for _ in fields]))

    table_rows = ""
    for i, issue in enumerate(issues, start=1):
        # Alternate row color: light gray for odd rows, white for even rows
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        
        # Create the link for the issue key
        issue_key_link = f'<a href="{jira_url}/browse/{issue["key"]}" target="_blank">{html.escape(issue["key"])}</a>'

        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{issue_key_link}</td><td>{html.escape(issue['fields']['summary'])}</td>"
        
        # Initialize comment variables
        acceptance_criteria_comment = ""
        qa_required_comment = ""
        requirement_status = ""
        qa_required = ""
        qa_assignee = ""

        # Iterate over each field to populate the table row
        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            elif field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]  # Extract name from string
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')  # Extract status from dictionary
                requirement_status = value
            elif isinstance(value, dict) and 'displayName' in value:
                value = value['displayName']
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, dict) and 'value' in value:
                value = value['value']
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            if value is None or value == "":
                value = "Not Available"
            else:
                value = remove_special_characters(value)  # Removing special characters
            
            if field == 'customfield_26027':
                qa_required = str(value).replace("!", "").strip()  # Remove '!' and trim whitespace
            elif field == 'customfield_17201':
                qa_assignee = str(value).replace("!", "").strip()  # Remove '!' and trim whitespace

            cell_content = html.escape(str(value))

            # Apply the highlighting rules
            if issue_type == "User Story" and field == "customfield_1110":  # Acceptance Criteria
                acceptance_length = len(value) if value else 0
                if acceptance_length == 0:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "less"
                elif acceptance_length < 30:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "more"
                else:
                    table_row += f"<td>{cell_content}</td>"

            elif field == "customfield_20627":
                if qa_assignee != "Not Available":
                    if qa_required != "Yes" and requirement_status != "OK":
                        table_row += f"<td style='background-color: yellow;'>{cell_content}</td>"
                        qa_required_comment = "Yellow column"
                    elif qa_required == "Not Available":
                        if requirement_status == "OK":
                            table_row += f"<td style='background-color: red;'>{cell_content}</td>"
                            qa_required_comment = "Red column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                    else:
                        if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                            table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                            qa_required_comment = "Blue column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                elif qa_assignee == "Not Available":
                    if requirement_status == "OK" or qa_required == "Yes":
                        table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                        qa_required_comment = "Blue column"
                    else:
                        table_row += f"<td>{cell_content}</td>"
                else:
                    table_row += f"<td>{cell_content}</td>"

        if acceptance_criteria_comment and qa_required_comment:
            combined_comment = f"{acceptance_criteria_comment}, {qa_required_comment}"
        elif acceptance_criteria_comment:
            combined_comment = acceptance_criteria_comment
        elif qa_required_comment:
            combined_comment = qa_required_comment

        table_row += f"<td>{html.escape(combined_comment)}</td>"
        table_row += "</tr>"
        table_rows += table_row

    # Combine table header, colgroup, and table rows to complete the HTML table
    html_table = f"<table border='1' style='border-collapse: collapse;'>{colgroup}{table_header}{table_rows}</table>"
    return html_table


def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    if not issues:
        return

    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    email_content += generate_html_table(issues, fields)

    all_email_content.append(email_content)

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
    except Exception as

  # Add the JQL query itself to the email content
    # Add the JQL query with blue color styling
    email_content += f"<p><strong>JQL:</strong> <span style='color:blue;'>{html.escape(jql_query)}</span></p><br>"


def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    if issues:
        email_content += generate_html_table(issues, fields)
    else:
        email_content += "<p style='color:red;'>No data available for this JQL.</p>"

    all_email_content.append(email_content)



############################# Excel reporting


import pandas as pd
from openpyxl import Workbook
from email.mime.base import MIMEBase
from email import encoders
import os

def generate_excel_file(issues, fields, component_name):
    # Create a Pandas DataFrame from the issues
    data = []
    for i, issue in enumerate(issues, start=1):
        row = {
            'Serial No': i,
            'Story': issue['key'],
            'Summary': issue['fields']['summary']
        }
        for field in fields:
            value = issue['fields'].get(field, "")
            if isinstance(value, dict):
                value = value.get('name', value.get('displayName', ''))
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) else v) for v in value)
            row[custom_field_mapping.get(field, field.replace('_', ' ').title())] = value

        data.append(row)

    df = pd.DataFrame(data)

    # Create a new Excel file
    excel_filename = f"{component_name}_issues.xlsx"
    excel_filepath = os.path.join('/tmp', excel_filename)  # Save in a temporary location
    df.to_excel(excel_filepath, index=False)

    return excel_filepath

def send_email(subject, body, attachment_path=None):
    sender_email = "your_email@example.com"
    recipient_email = "recipient@example.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    # Attach the Excel file
    if attachment_path:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}',
            )
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, "your_password")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        logging.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    if not issues:
        return

    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    excel_filepath = generate_excel_file(issues, fields, component_name)
    
    email_content += f"<p>You can download the detailed report <a href='cid:{os.path.basename(excel_filepath)}'>here</a>.</p>"

    all_email_content.append((email_content, excel_filepath))

def process_all_jql_queries():
    all_email_content = []

    fields = [
        'issuetype',
        'priority',
        'versions',
        'components',
        'labels',
        'status',
        'resolution',
        'fixVersions',
        'customfield_10021',  # QA Required? (custom field)
        'customfield_10020',  # Sprint (custom field)
        'customfield_10002',  # Story Points (custom field)
        'customfield_10010'   # Requirement Status (custom field)
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, all_email_content, fields): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")

    combined_email_content = ""
    attachments = []
    for content, attachment_path in all_email_content:
        combined_email_content += content + "<br><br>"
        attachments.append(attachment_path)

    send_email("Jira Report for All Components", combined_email_content, attachment_path=attachments[0])

# Start processing all JQL queries
process_all_jql_queries()

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

import html

def generate_html_table(issues, fields):
    table = "<table border='1'>"
    table += "<tr>"
    for field in fields:
        table += f"<th>{html.escape(field)}</th>"
    table += "</tr>"

    for issue in issues:
        table_row = "<tr>"
        for field in fields:
            value = issue['fields'].get(field, "")

            # Handle None explicitly
            if value is None:
                value = ""

            # Specific handling for known custom fields
            if field == 'customfield_10005':
                value = handle_customfield_10005(value)
            elif field == 'customfield_26424':
                value = handle_customfield_26424(value)
            else:
                # Handle other potential dictionary or list values
                value = handle_generic_field(value)

            # Escape value for HTML
            value = html.escape(value)

            # Add the processed value to the table row
            table_row += f"<td>{value}</td>"

        table_row += "</tr>"
        table += table_row

    table += "</table>"
    return table

def handle_customfield_10005(value):
    if isinstance(value, list) and value:
        # Extract the name from the list of dictionaries
        return ', '.join(v.split("name=")[-1].split(",")[0] for v in value if "name=" in v)
    return str(value)

def handle_customfield_26424(value):
    if isinstance(value, list) and value:
        # Extract the status from the list of dictionaries
        return ', '.join(v.get('status', '') for v in value)
    return str(value)

def handle_generic_field(value):
    if isinstance(value, dict):
        return value.get('displayName') or value.get('name') or value.get('value') or ""
    elif isinstance(value, list):
        return ', '.join(
            str(v['name']) if isinstance(v, dict) and 'name' in v else str(v)
            for v in value
        )
    return str(value)

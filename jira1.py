import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Generate the JQL queries dynamically based on components in conf.py
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components
] + [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components1
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query with retries
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        for attempt in range(retry_attempts):
            try:
                # Make the request
                response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

                # Check if the request was successful
                if response.status_code == 200:
                    issues = response.json()['issues']
                    all_issues.extend(issues)
                    if len(issues) < max_results:
                        return all_issues
                    start_at += max_results
                    break
                else:
                    print(f"Failed to retrieve issues for JQL '{jql_query}': {response.status_code} - {response.text}")
                    if response.status_code == 401:  # Unauthorized
                        print("Authentication issue, retrying...")
                        time.sleep(retry_delay)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if attempt == retry_attempts - 1:
            print(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

def process_issues(jql_query):
    # Fetch all issues for the current JQL query
    issues = fetch_all_issues(jql_query)

    # Initialize lists to categorize issues
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully automated': [],
        'Partially automated': [],
        'Can\'t be automated': []
    }

    # Process each issue
    for issue in issues:
        cust_field = issue['fields'].get('cust_field')
        if not cust_field or not cust_field.get('value'):
            no_automation_reason.append(issue)
        else:
            reason = cust_field['value']
            if reason in automation_reason_with_values:
                automation_reason_with_values[reason].append(issue)
            else:
                automation_reason_with_values[reason] = [issue]

    # Determine the component for the current JQL query
    component = jql_query.split('component = ')[1].strip('"')

    # Print the results for the current JQL query
    print(f"\nResults for {component}:\n")
    print(f"Issues with blank automation reason: {len(no_automation_reason)}")
    for issue in no_automation_reason:
        print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues with automation reason:")
    for reason, issue_list in automation_reason_with_values.items():
        print(f"{reason}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")

# Function to process all JQL queries with retries
def process_all_jql_queries():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing JQL '{jql_query}': {e}")
                # Retry the same JQL query if it fails
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    print(f"Retrying JQL '{jql_query}' (Attempt {attempt + 1}/{retry_attempts})")
                    try:
                        process_issues(jql_query)
                        break
                    except Exception as e:
                        print(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

# Start processing all JQL queries
process_all_jql_queries()


2 ..............................................................................



import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Generate the JQL queries dynamically based on components in conf.py
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components
] + [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components1
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query with retries
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        for attempt in range(retry_attempts):
            try:
                # Make the request
                response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

                # Check if the request was successful
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
                        time.sleep(retry_delay)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if attempt == retry_attempts - 1:
            logging.error(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

def process_issues(jql_query):
    # Fetch all issues for the current JQL query
    issues = fetch_all_issues(jql_query)

    # Initialize lists to categorize issues
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully automated': [],
        'Partially automated': [],
        'Can\'t be automated': []
    }
    labels_with_values = {
        'None': [],
        'Has values': []
    }

    resolution_with_values = {
        'None': [],
        'Has values': []
    }


    # Process each issue
    for issue in issues:
        # Categorize by automation reason
        cust_field = issue['fields'].get('cust_field')
        if not cust_field or not cust_field.get('value'):
            no_automation_reason.append(issue)
        else:
            reason = cust_field['value']
            if reason in automation_reason_with_values:
                automation_reason_with_values[reason].append(issue)
            else:
                automation_reason_with_values[reason] = [issue]

        # Categorize by labels
        labels = issue['fields'].get('labels', [])
        if not labels:
            labels_with_values['None'].append(issue)
        else:
            labels_with_values['Has values'].append(issue)


    # Categorize by resolution
        resolution = issue['fields'].get('resolution')
        if not resolution:
            resolution_with_values['None'].append(issue)
        else:
            resolution_with_values['Has values'].append(issue)

    # Determine the component for the current JQL query
    component = jql_query.split('component = ')[1].strip('"')

    # Print the results for the current JQL query
    print(f"\nResults for {component}:\n")
    
    print(f"Issues with blank automation reason: {len(no_automation_reason)}")
    for issue in no_automation_reason:
        print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues with automation reason:")
    for reason, issue_list in automation_reason_with_values.items():
        print(f"{reason}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues categorized by labels:")
    for label_status, issue_list in labels_with_values.items():
        print(f"Labels {label_status}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")


    print("\nIssues categorized by resolution:")
    for resolution_status, issue_list in resolution_with_values.items():
        print(f"Resolution {resolution_status}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")

# Function to process all JQL queries with retries
def process_all_jql_queries():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")
                # Retry the same JQL query if it fails
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    logging.info(f"Retrying JQL '{jql_query}' (Attempt {attempt + 1}/{retry_attempts})")
                    try:
                        process_issues(jql_query)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

# Start processing all JQL queries
process_all_jql_queries()


3 ......................................................................................................

import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Generate the JQL queries dynamically based on components in conf.py
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components
] + [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components1
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query with retries
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        for attempt in range(retry_attempts):
            try:
                # Make the request
                response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

                # Check if the request was successful
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
                        time.sleep(retry_delay)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if attempt == retry_attempts - 1:
            logging.error(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

# Function to categorize issues based on a given field
def categorize_issues(issues, field_name):
    categorized_issues = {
        'None': [],
        'Has values': []
    }
    for issue in issues:
        field_value = issue['fields'].get(field_name)
        if not field_value:
            categorized_issues['None'].append(issue)
        else:
            categorized_issues['Has values'].append(issue)
    return categorized_issues

# Function to process issues for a given JQL query
def process_issues(jql_query):
    # Fetch all issues for the current JQL query
    issues = fetch_all_issues(jql_query)

    # Initialize lists to categorize issues
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully automated': [],
        'Partially automated': [],
        'Can\'t be automated': []
    }

    # Process each issue for automation reason
    for issue in issues:
        cust_field = issue['fields'].get('cust_field')
        if not cust_field or not cust_field.get('value'):
            no_automation_reason.append(issue)
        else:
            reason = cust_field['value']
            if reason in automation_reason_with_values:
                automation_reason_with_values[reason].append(issue)
            else:
                automation_reason_with_values[reason] = [issue]

    # Categorize issues based on labels and resolution fields
    labels_with_values = categorize_issues(issues, 'labels')
    resolution_with_values = categorize_issues(issues, 'resolution')

    # Determine the component for the current JQL query
    component = jql_query.split('component = ')[1].strip('"')

    # Print the results for the current JQL query
    print(f"\nResults for {component}:\n")
    
    print(f"Issues with blank automation reason: {len(no_automation_reason)}")
    for issue in no_automation_reason:
        print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues with automation reason:")
    for reason, issue_list in automation_reason_with_values.items():
        print(f"{reason}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues categorized by labels:")
    for label_status, issue_list in labels_with_values.items():
        print(f"Labels {label_status}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues categorized by resolution:")
    for resolution_status, issue_list in resolution_with_values.items():
        print(f"Resolution {resolution_status}: {len(issue_list)}")
        for issue in issue_list:
            resolution = issue['fields'].get('resolution')
            resolution_name = resolution['name'] if resolution else 'UNRESOLVED'
            print(f"{issue['key']}|{issue['fields']['summary']}|{resolution_name}")

# Function to process all JQL queries with retries
def process_all_jql_queries():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")
                # Retry the same JQL query if it fails
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    logging.info(f"Retrying JQL '{jql_query}' (Attempt {attempt + 1}/{retry_attempts})")
                    try:
                        process_issues(jql_query)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

# Start processing all JQL queries
process_all_jql_queries()


4.............................................


import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Generate the JQL queries dynamically based on components in conf.py
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components
] + [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components1
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query with retries
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        for attempt in range(retry_attempts):
            try:
                # Make the request
                response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

                # Check if the request was successful
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
                        time.sleep(retry_delay)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if attempt == retry_attempts - 1:
            logging.error(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

# Function to categorize issues based on a given field
def categorize_issues(issues, field_name):
    categorized_issues = {
        'None': [],
        'Has values': []
    }
    for issue in issues:
        field_value = issue['fields'].get(field_name)
        if not field_value:
            categorized_issues['None'].append(issue)
        else:
            categorized_issues['Has values'].append(issue)
    return categorized_issues

# Generic function to print categorized issues
def print_categorized_issues(categorized_issues, field_name, default_value):
    print(f"\nIssues categorized by {field_name}:")
    for status, issue_list in categorized_issues.items():
        print(f"{field_name} {status}: {len(issue_list)}")
        for issue in issue_list:
            value = issue['fields'].get(field_name)
            if field_name == 'resolution' and value:
                value = value['name']
            print(f"{issue['key']}|{issue['fields']['summary']}|{value if value else default_value}")

# Function to process issues for a given JQL query
def process_issues(jql_query):
    # Fetch all issues for the current JQL query
    issues = fetch_all_issues(jql_query)

    # Initialize lists to categorize issues
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully automated': [],
        'Partially automated': [],
        'Can\'t be automated': []
    }

    # Process each issue for automation reason
    for issue in issues:
        cust_field = issue['fields'].get('cust_field')
        if not cust_field or not cust_field.get('value'):
            no_automation_reason.append(issue)
        else:
            reason = cust_field['value']
            if reason in automation_reason_with_values:
                automation_reason_with_values[reason].append(issue)
            else:
                automation_reason_with_values[reason] = [issue]

    # Categorize issues based on labels and resolution fields
    labels_with_values = categorize_issues(issues, 'labels')
    resolution_with_values = categorize_issues(issues, 'resolution')

    # Determine the component for the current JQL query
    component = jql_query.split('component = ')[1].strip('"')

    # Print the results for the current JQL query
    print(f"\nResults for {component}:\n")
    
    print(f"Issues with blank automation reason: {len(no_automation_reason)}")
    for issue in no_automation_reason:
        print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nIssues with automation reason:")
    for reason, issue_list in automation_reason_with_values.items():
        print(f"{reason}: {len(issue_list)}")
        for issue in issue_list:
            print(f"{issue['key']}|{issue['fields']['summary']}")

    # Print categorized issues for labels and resolution
    print_categorized_issues(labels_with_values, 'labels', 'NO LABEL')
    print_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED')

# Function to process all JQL queries with retries
def process_all_jql_queries():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")
                # Retry the same JQL query if it fails
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    logging.info(f"Retrying JQL '{jql_query}' (Attempt {attempt + 1}/{retry_attempts})")
                    try:
                        process_issues(jql_query)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

# Start processing all JQL queries
process_all_jql_queries()


5....................................................

import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import csv
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Generate the JQL queries dynamically based on components in conf.py
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components
] + [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components1
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query with retries
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        for attempt in range(retry_attempts):
            try:
                # Make the request
                response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

                # Check if the request was successful
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
                        time.sleep(retry_delay)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if attempt == retry_attempts - 1:
            logging.error(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

# Function to save issues to a CSV file
def save_issues_to_csv(issues, filename):
    fieldnames = ['Key', 'Summary', 'Field Value']
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow({
                'Key': issue['key'],
                'Summary': issue['fields']['summary'],
                'Field Value': issue.get('field_value', 'N/A')
            })

# Function to categorize issues based on a given field
def categorize_issues(issues, field_name):
    categorized_issues = {
        'None': [],
        'Has values': []
    }
    for issue in issues:
        field_value = issue['fields'].get(field_name)
        if not field_value:
            categorized_issues['None'].append(issue)
        else:
            categorized_issues['Has values'].append(issue)
    return categorized_issues

# Generic function to print and save categorized issues
def print_and_save_categorized_issues(categorized_issues, field_name, default_value):
    print(f"\nIssues categorized by {field_name}:")
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        print(f"{field_name} {status}: {count}")
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            for issue in issue_list:
                value = issue['fields'].get(field_name)
                if field_name == 'resolution' and value:
                    value = value['name']
                issue['field_value'] = value if value else default_value
            save_issues_to_csv(issue_list, filename)
            print(f"Details: {filename}")

# Function to process issues for a given JQL query
def process_issues(jql_query):
    # Fetch all issues for the current JQL query
    issues = fetch_all_issues(jql_query)

    # Initialize lists to categorize issues
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully automated': [],
        'Partially automated': [],
        'Can\'t be automated': []
    }

    # Process each issue for automation reason
    for issue in issues:
        cust_field = issue['fields'].get('cust_field')
        if not cust_field or not cust_field.get('value'):
            no_automation_reason.append(issue)
        else:
            reason = cust_field['value']
            if reason in automation_reason_with_values:
                automation_reason_with_values[reason].append(issue)
            else:
                automation_reason_with_values[reason] = [issue]

    # Categorize issues based on labels and resolution fields
    labels_with_values = categorize_issues(issues, 'labels')
    resolution_with_values = categorize_issues(issues, 'resolution')

    # Determine the component for the current JQL query
    component = jql_query.split('component = ')[1].strip('"')

    # Print the results for the current JQL query
    print(f"\nResults for {component}:\n")
    
    print(f"Issues with blank automation reason: {len(no_automation_reason)}")
    if len(no_automation_reason) > 0:
        filename = f"Issues_with_blank_automation_reason_{len(no_automation_reason)}.csv"
        save_issues_to_csv(no_automation_reason, filename)
        print(f"Details: {filename}")

    print("\nIssues with automation reason:")
    for reason, issue_list in automation_reason_with_values.items():
        print(f"{reason}: {len(issue_list)}")
        if len(issue_list) > 0:
            filename = f"Issues_with_{reason.replace(' ', '_')}_{len(issue_list)}.csv"
            save_issues_to_csv(issue_list, filename)
            print(f"Details: {filename}")

    # Print and save categorized issues for labels and resolution
    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL')
    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED')

# Function to process all JQL queries with retries
def process_all_jql_queries():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")
                # Retry the same JQL query if it fails
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    logging.info(f"Retrying JQL '{jql_query}' (Attempt {attempt + 1}/{retry_attempts})")
                    try:
                        process_issues(jql_query)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

# Start processing all JQL queries
process_all_jql_queries()


6..............................................................................................



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import csv
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Generate the JQL queries dynamically based on components in conf.py
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components
] + [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in conf.components1
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query with retries
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []
    retry_attempts = 3
    retry_delay = 5

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        for attempt in range(retry_attempts):
            try:
                # Make the request
                response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

                # Check if the request was successful
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
                        time.sleep(retry_delay)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(retry_delay)  # Wait before retrying

        if attempt == retry_attempts - 1:
            logging.error(f"Failed to retrieve issues for JQL '{jql_query}' after {retry_attempts} attempts.")
            break

    return all_issues

# Function to save issues to a CSV file
def save_issues_to_csv(issues, filename):
    fieldnames = ['Key', 'Summary', 'Field Value']
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow({
                'Key': issue['key'],
                'Summary': issue['fields']['summary'],
                'Field Value': issue.get('field_value', 'N/A')
            })

# Function to categorize issues based on a given field
def categorize_issues(issues, field_name):
    categorized_issues = {
        'None': [],
        'Has values': []
    }
    for issue in issues:
        field_value = issue['fields'].get(field_name)
        if not field_value:
            categorized_issues['None'].append(issue)
        else:
            categorized_issues['Has values'].append(issue)
    return categorized_issues

# Generic function to print and save categorized issues
def print_and_save_categorized_issues(categorized_issues, field_name, default_value, email_content, base_url):
    email_body = ""
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            file_url = f"{base_url}/{filename}"
            save_issues_to_csv(issue_list, filename)
            # Append to the email body with a link
            email_body += f"{field_name} {status}: <a href='{file_url}'>{count}</a><br>"
        else:
            # Append the count without a link
            email_body += f"{field_name} {status}: {count}<br>"
    
    email_content.append(email_body)

# Function to process issues for a given JQL query
def process_issues(jql_query, email_content, base_url):
    issues = fetch_all_issues(jql_query)

    # Processing as before...
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully automated': [],
        'Partially automated': [],
        'Can\'t be automated': []
    }
    
    for issue in issues:
        cust_field = issue['fields'].get('cust_field')
        if not cust_field or not cust_field.get('value'):
            no_automation_reason.append(issue)
        else:
            reason = cust_field['value']
            if reason in automation_reason_with_values:
                automation_reason_with_values[reason].append(issue)
            else:
                automation_reason_with_values[reason] = [issue]

    labels_with_values = categorize_issues(issues, 'labels')
    resolution_with_values = categorize_issues(issues, 'resolution')

    component = jql_query.split('component = ')[1].strip('"')

    # Start building the email content
    email_body = f"<h2>Results for {component}:</h2><br>"
    email_body += f"Issues with blank automation reason: {len(no_automation_reason)}<br>"
    if len(no_automation_reason) > 0:
        filename = f"Issues_with_blank_automation_reason_{len(no_automation_reason)}.csv"
        file_url = f"{base_url}/{filename}"
        save_issues_to_csv(no_automation_reason, filename)
        email_body += f"<a href='{file_url}'>Details</a><br>"

    email_body += "<h3>Issues with automation reason:</h3><br>"
    for reason, issue_list in automation_reason_with_values.items():
        count = len(issue_list)
        if count > 0:
            filename = f"Issues_with_{reason.replace(' ', '_')}_{count}.csv"
            file_url = f"{base_url}/{filename}"
            save_issues_to_csv(issue_list, filename)
            email_body += f"{reason}: <a href='{file_url}'>{count}</a><br>"
        else:
            email_body += f"{reason}: {count}<br>"

    # Categorized issues with links
    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url)
    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url)
    
    email_content.append(email_body)

# Function to send the email
def send_email(subject, to, content):
    # Set up the email server and login credentials
    smtp_server = "smtp.example.com"  # Replace with your SMTP server
    smtp_port = 587  # Replace with your SMTP port (usually 587 for TLS)
    smtp_user = "your-email@example.com"  # Replace with your email
    smtp_password = "your-password"  # Replace with your password
    
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = subject
    
    # Combine all email parts into a single body
    email_body = ''.join(content)
    msg.attach(MIMEText(email_body, 'html'))

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to, msg.as_string())
        server.quit()
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to process all JQL queries with retries
def process_all_jql_queries():
    base_url = "http://your-server.com/csv-files"
    email_content = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, email_content, base_url): jql_query for jql_query in jql_queries}
        for future in concurrent.futures.as_completed(futures):
            jql_query = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing JQL '{jql_query}': {e}")
    
    send_email("JIRA Report", "team@example.com", email_content)

# Start processing all JQL queries
process_all_jql_queries()




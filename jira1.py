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
    email_body = f"\nIssues categorized by {field_name}:<br>"
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        email_body += f"{field_name} {status}: {count}<br>"
        
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            for issue in issue_list:
                value = issue['fields'].get(field_name)
                if field_name == 'resolution' and value:
                    value = value['name']
                issue['field_value'] = value if value else default_value
            
            save_issues_to_csv(issue_list, filename)
            file_url = f"{base_url}/{filename}"
            email_body += f"<a href='{file_url}'>Details</a><br>"
    
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


7..............................................................................


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

# Function to fetch all issues for a given JQL query with retries
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

# Function to save issues to a CSV file
def save_issues_to_csv(issue_list, filename):
    keys = ['key', 'summary', 'field_value']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for issue in issue_list:
            writer.writerow({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'field_value': issue['field_value']
            })

# Updated function to print and save categorized issues and build email content with embedded links
def print_and_save_categorized_issues(categorized_issues, field_name, default_value, email_content, base_url):
    email_body = f"\nIssues categorized by {field_name}:<br>"
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            for issue in issue_list:
                value = issue['fields'].get(field_name)
                if field_name == 'resolution' and value:
                    value = value['name']
                issue['field_value'] = value if value else default_value
            
            save_issues_to_csv(issue_list, filename)
            file_url = f"{base_url}/{filename}"
            email_body += f"{field_name} {status}: <a href='{file_url}'>{count}</a><br>"
        else:
            email_body += f"{field_name} {status}: {count}<br>"
    
    email_content.append(email_body)

# Function to process issues for a given JQL query
# Function to process issues for a given JQL query
def process_issues(jql_query):
    issues = fetch_all_issues(jql_query)

    # Categorize issues based on automation reason, labels, and resolution
    no_automation_reason = []
    automation_reason_with_values = {
        'Fully Automated': [],
        'Partially Automated': [],
        'Automated and Not Usable': [],
        'Pending Automation Analysis': [],
        'Not Feasible-Not Automated': [],
        'Feasible-Not Automated': [],
        'Feasible-Automation In Progress': []
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

    # Determine the component for the current JQL query
    component = jql_query.split('component = ')[1].strip('"')

    # Print results and prepare email content
    print(f"\nResults for {component}:\n")

    email_content = []

    if len(no_automation_reason) > 0:
        filename = f"{component}_No_Automation_Reason_{len(no_automation_reason)}.csv"
        save_issues_to_csv(no_automation_reason, filename)
        email_content.append(f"Issues with blank automation reason: <a href='http://your-server.com/files/{filename}'>{len(no_automation_reason)}</a><br>")
    else:
        email_content.append(f"Issues with blank automation reason: 0<br>")

    print("\nIssues with automation reason:")
    for reason, issue_list in automation_reason_with_values.items():
        count = len(issue_list)
        print(f"{reason}: {count}")
        if count > 0:
            filename = f"{component}_{reason.replace(' ', '_')}_{count}.csv"
            save_issues_to_csv(issue_list, filename)
            email_content.append(f"{reason}: <a href='http://your-server.com/files/{filename}'>{count}</a><br>")
        else:
            email_content.append(f"{reason}: 0<br>")

    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url="http://your-server.com/files")
    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url="http://your-server.com/files")

    # Now, send the email with the content
    send_email("Jira Report for " + component, "".join(email_content))

# Function to send an email
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

# Combine components from conf.py into jql_queries
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{component}"' 
    for component in (conf.components + conf.components1)
]

# Start processing all JQL queries
process_all_jql_queries()





7..................

def save_issues_to_csv(issue_list, filename, jql_query):
    keys = ['key', 'summary', 'field_value']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        
        # Write the JQL query as the first row
        csvfile.write(f"JQL,{jql_query}\n")
        
        writer.writeheader()
        for issue in issue_list:
            writer.writerow({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'field_value': issue['field_value']
            })


def process_issues(jql_query, all_email_content):
    issues = fetch_all_issues(jql_query)

    no_automation_reason = []
    automation_reason_with_values = {
        'Fully Automated': [],
        'Partially Automated': [],
        'Automated and Not Usable': [],
        'Pending Automation Analysis': [],
        'Not Feasible-Not Automated': [],
        'Feasible-Not Automated': [],
        'Feasible-Automation In Progress': []
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

    email_content = []

    if len(no_automation_reason) > 0:
        filename = f"{component}_No_Automation_Reason_{len(no_automation_reason)}.csv"
        save_issues_to_csv(no_automation_reason, filename, jql_query)
        email_content.append(f"Issues with blank automation reason: <a href='http://your-server.com/files/{filename}'>{len(no_automation_reason)}</a><br>")

    for reason, issue_list in automation_reason_with_values.items():
        count = len(issue_list)
        if count > 0:
            filename = f"{component}_{reason.replace(' ', '_')}_{count}.csv"
            save_issues_to_csv(issue_list, filename, jql_query)
            email_content.append(f"{reason}: <a href='http://your-server.com/files/{filename}'>{count}</a><br>")
    
    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url="http://your-server.com/files")
    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url="http://your-server.com/files")

    all_email_content.append("\n".join(email_content))




8...............................


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

def save_issues_to_csv(issue_list, filename):
    keys = ['key', 'summary', 'field_value']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for issue in issue_list:
            writer.writerow({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'field_value': issue['field_value']
            })

def print_and_save_categorized_issues(categorized_issues, field_name, default_value, email_content, base_url):
    email_body = f"\nIssues categorized by {field_name}:<br>"
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            for issue in issue_list:
                value = issue['fields'].get(field_name)
                if field_name == 'resolution' and value:
                    value = value['name']
                issue['field_value'] = value if value else default_value
            
            save_issues_to_csv(issue_list, filename)
            file_url = f"{base_url}/{filename}"
            email_body += f"{field_name} {status}: <a href='{file_url}'>{count}</a><br>"
        else:
            email_body += f"{field_name} {status}: {count}<br>"
    
    email_content.append(email_body)

def process_issues(jql_query, all_email_content):
    issues = fetch_all_issues(jql_query)

    no_automation_reason = []
    automation_reason_with_values = {
        'Fully Automated': [],
        'Partially Automated': [],
        'Automated and Not Usable': [],
        'Pending Automation Analysis': [],
        'Not Feasible-Not Automated': [],
        'Feasible-Not Automated': [],
        'Feasible-Automation In Progress': []
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

    email_content = []

    if len(no_automation_reason) > 0:
        filename = f"{component}_No_Automation_Reason_{len(no_automation_reason)}.csv"
        save_issues_to_csv(no_automation_reason, filename)
        email_content.append(f"Issues with blank automation reason: <a href='http://your-server.com/files/{filename}'>{len(no_automation_reason)}</a><br>")

    for reason, issue_list in automation_reason_with_values.items():
        count = len(issue_list)
        if count > 0:
            filename = f"{component}_{reason.replace(' ', '_')}_{count}.csv"
            save_issues_to_csv(issue_list, filename)
            email_content.append(f"{reason}: <a href='http://your-server.com/files/{filename}'>{count}</a><br>")
    
    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url="http://your-server.com/files")
    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url="http://your-server.com/files")

    all_email_content.append("\n".join(email_content))

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


beautify..................................


def print_and_save_categorized_issues(categorized_issues, field_name, default_value, email_content, base_url):
    email_body = f"<h3 style='color:blue;'>Issues categorized by {field_name}:</h3>"
    email_body += "<ul style='font-family: Arial, sans-serif;'>"
    
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            for issue in issue_list:
                value = issue['fields'].get(field_name)
                if field_name == 'resolution' and value:
                    value = value['name']
                issue['field_value'] = value if value else default_value
            
            save_issues_to_csv(issue_list, filename)
            file_url = f"{base_url}/{filename}"
            email_body += f"<li><strong>{field_name} {status}</strong>: <a href='{file_url}'>{count}</a></li>"
        else:
            email_body += f"<li><strong>{field_name} {status}</strong>: {count}</li>"
    
    email_body += "</ul>"
    email_content.append(email_body)

def send_email(subject, body):
    sender_email = "your_email@example.com"
    recipient_email = "recipient@example.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Wrap the body with a div that applies the Arial font to all text
    full_body = f"<div style='font-family: Arial, sans-serif;'>{body}</div>"
    msg.attach(MIMEText(full_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, "your_password")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        logging.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# The rest of your code remains the same

// Summary

def process_issues(jql_query, all_email_content, summary_counts):
    issues = fetch_all_issues(jql_query)

    no_automation_reason = []
    automation_reason_with_values = {
        'Fully Automated': [],
        'Partially Automated': [],
        'Automated and Not Usable': [],
        'Pending Automation Analysis': [],
        'Not Feasible-Not Automated': [],
        'Feasible-Not Automated': [],
        'Feasible-Automation In Progress': []
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

    email_content = []

    if len(no_automation_reason) > 0:
        filename = f"{component}_No_Automation_Reason_{len(no_automation_reason)}.csv"
        save_issues_to_csv(no_automation_reason, filename)
        email_content.append(f"Issues with blank automation reason: <a href='http://your-server.com/files/{filename}'>{len(no_automation_reason)}</a><br>")
        summary_counts['no_automation_reason'] += len(no_automation_reason)

    for reason, issue_list in automation_reason_with_values.items():
        count = len(issue_list)
        if count > 0:
            filename = f"{component}_{reason.replace(' ', '_')}_{count}.csv"
            save_issues_to_csv(issue_list, filename)
            email_content.append(f"{reason}: <a href='http://your-server.com/files/{filename}'>{count}</a><br>")
            summary_counts[reason.lower().replace(' ', '_')] += count
    
    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url="http://your-server.com/files")
    summary_counts['labels_none'] += len(labels_with_values['None'])
    summary_counts['labels_with_values'] += len(labels_with_values['Has values'])

    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url="http://your-server.com/files")
    summary_counts['resolution_none'] += len(resolution_with_values['None'])
    summary_counts['resolution_with_values'] += len(resolution_with_values['Has values'])

    all_email_content.append("\n".join(email_content))

def process_all_jql_queries():
    all_email_content = []  # Accumulate all email content across JQL queries
    summary_counts = {
        'no_automation_reason': 0,
        'fully_automated': 0,
        'partially_automated': 0,
        'automated_and_not_usable': 0,
        'pending_automation_analysis': 0,
        'not_feasible_not_automated': 0,
        'feasible_not_automated': 0,
        'feasible_automation_in_progress': 0,
        'labels_none': 0,
        'labels_with_values': 0,
        'resolution_none': 0,
        'resolution_with_values': 0
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_issues, jql_query, all_email_content, summary_counts): jql_query for jql_query in jql_queries}
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
                        process_issues(jql_query, all_email_content, summary_counts)
                        break
                    except Exception as e:
                        logging.error(f"Retry {attempt + 1} failed for JQL '{jql_query}': {e}")
                        time.sleep(5)  # Wait before retrying

    combined_email_content = "\n".join(all_email_content)

    # Add summary to the email content
    summary = f"""
    <br><br><strong>Summary:</strong><br>
    Total issues with no automation reason: {summary_counts['no_automation_reason']}<br>
    Total fully automated issues: {summary_counts['fully_automated']}<br>
    Total partially automated issues: {summary_counts['partially_automated']}<br>
    Total automated and not usable issues: {summary_counts['automated_and_not_usable']}<br>
    Total pending automation analysis issues: {summary_counts['pending_automation_analysis']}<br>
    Total not feasible - not automated issues: {summary_counts['not_feasible_not_automated']}<br>
    Total feasible - not automated issues: {summary_counts['feasible_not_automated']}<br>
    Total feasible - automation in progress issues: {summary_counts['feasible_automation_in_progress']}<br>
    Total issues categorized by label (None): {summary_counts['labels_none']}<br>
    Total issues categorized by label (Has values): {summary_counts['labels_with_values']}<br>
    Total issues categorized by resolution (None): {summary_counts['resolution_none']}<br>
    Total issues categorized by resolution (Has values): {summary_counts['resolution_with_values']}<br>
    """
    combined_email_content += summary

    send_email("Jira Report for All Components", combined_email_content)

# Start processing all JQL queries
process_all_jql_queries()

...................................................

def update_summary_counts(summary_counts, category, categorized_issues):
    summary_counts[f'{category}_none'] += len(categorized_issues['None'])
    summary_counts[f'{category}_with_values'] += len(categorized_issues['Has values'])


def process_issues(jql_query, all_email_content, summary_counts):
    issues = fetch_all_issues(jql_query)

    # Existing logic for categorizing issues
    labels_with_values = categorize_issues(issues, 'labels')
    resolution_with_values = categorize_issues(issues, 'resolution')

    # Use the helper function to update summary counts
    update_summary_counts(summary_counts, 'labels', labels_with_values)
    update_summary_counts(summary_counts, 'resolution', resolution_with_values)

    # The rest of your existing code
########################################33 generic #############################################################################3



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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

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

def save_issues_to_csv(issue_list, filename):
    keys = ['key', 'summary', 'field_value']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for issue in issue_list:
            writer.writerow({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'field_value': issue['field_value']
            })

def print_and_save_categorized_issues(categorized_issues, field_name, default_value, email_content, base_url):
    email_body = f"\nIssues categorized by {field_name}:<br>"
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            for issue in issue_list:
                value = issue['fields'].get(field_name)
                if field_name == 'resolution' and value:
                    value = value['name']
                issue['field_value'] = value if value else default_value
            
            save_issues_to_csv(issue_list, filename)
            file_url = f"{base_url}/{filename}"
            email_body += f"{field_name} {status}: <a href='{file_url}'>{count}</a><br>"
        else:
            email_body += f"{field_name} {status}: {count}<br>"
    
    email_content.append(email_body)

def process_issues(jql_query, all_email_content):
    issues = fetch_all_issues(jql_query)

    no_automation_reason = []
    automation_reason_with_values = {
        'Fully Automated': [],
        'Partially Automated': [],
        'Automated and Not Usable': [],
        'Pending Automation Analysis': [],
        'Not Feasible-Not Automated': [],
        'Feasible-Not Automated': [],
        'Feasible-Automation In Progress': []
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

    field_name = jql_query.split(' AND ')[-1].split(' = ')[0]

    email_content = []

    if len(no_automation_reason) > 0:
        filename = f"{field_name}_No_Automation_Reason_{len(no_automation_reason)}.csv"
        save_issues_to_csv(no_automation_reason, filename)
        email_content.append(f"Issues with blank automation reason: <a href='http://your-server.com/files/{filename}'>{len(no_automation_reason)}</a><br>")
        summary_counts['no_automation_reason'] += len(no_automation_reason)


    for reason, issue_list in automation_reason_with_values.items():
        count = len(issue_list)
        if count > 0:
            filename = f"{field_name}_{reason.replace(' ', '_')}_{count}.csv"
            save_issues_to_csv(issue_list, filename)
            email_content.append(f"{reason}: <a href='http://your-server.com/files/{filename}'>{count}</a><br>")
            summary_counts[reason.lower().replace(' ', '_')] += count
    
    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url="http://your-server.com/files")
    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url="http://your-server.com/files")

    print_and_save_categorized_issues(labels_with_values, 'labels', 'NO LABEL', email_content, base_url="http://your-server.com/files")
    summary_counts['labels_none'] += len(labels_with_values['None'])
    summary_counts['labels_with_values'] += len(labels_with_values['Has values'])

    print_and_save_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED', email_content, base_url="http://your-server.com/files")
    summary_counts['resolution_none'] += len(resolution_with_values['None'])
    summary_counts['resolution_with_values'] += len(resolution_with_values['Has values'])

    all_email_content.append("\n".join(email_content))

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
    all_email_content = []  # Accumulate all email content across JQL queries

    summary_counts = {
        'no_automation_reason': 0,
        'fully_automated': 0,
        'partially_automated': 0,
        'automated_and_not_usable': 0,
        'pending_automation_analysis': 0,
        'not_feasible_not_automated': 0,
        'feasible_not_automated': 0,
        'feasible_automation_in_progress': 0,
        'labels_none': 0,
        'labels_with_values': 0,
        'resolution_none': 0,
        'resolution_with_values': 0
    }

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
                        time.sleep(5)  # Delay between retries

    summary_email_body = "\n".join(all_email_content)
    send_email("Jira Issue Report", summary_email_body)

def generate_jql_queries(start_date, end_date, fields_and_values):
    jql_queries = []

    for field, values in fields_and_values.items():
        if values:  # Check if the list is not empty
            joined_values = ', '.join(f'"{value}"' for value in values)
            jql_queries.append(f'created >= "{start_date}" AND created < "{end_date}" AND {field} IN ({joined_values})')

    return jql_queries

if __name__ == "__main__":
    # Define the date range
    start_date = "2024-07-31"
    end_date = "2024-08-01"

    # Define the fields and their corresponding values
    fields_and_values = {
        'component': conf.components + conf.components1,
        'assignee': conf.assignees + conf.assignees1
        # Add more fields and values as needed
    }

    # Generate JQL queries based on the specified fields and values
    jql_queries = generate_jql_queries(start_date, end_date, fields_and_values)

    # Process all generated JQL queries
    process_all_jql_queries()



############### 

# Ensure the key normalization is consistent across the code
normalized_keys = {
    'Not Feasible-Not Automated': 'not_feasible_not_automated',
    'Feasible-Not Automated': 'feasible_not_automated',
    'Fully Automated': 'fully_automated',
    'Partially Automated': 'partially_automated',
    'Automated and Not Usable': 'automated_and_not_usable',
    'Pending Automation Analysis': 'pending_automation_analysis',
    'Feasible-Automation In Progress': 'feasible_automation_in_progress'
}

for reason, issue_list in automation_reason_with_values.items():
    count = len(issue_list)
    if count > 0:
        reason_key = normalized_keys.get(reason, reason.lower().replace(' ', '_'))
        filename = f"{assignee}_{reason_key}_{count}.csv"
        save_issues_to_csv(issue_list, filename)
        email_content.append(f"{reason}: <a href='http://your-server.com/files/{filename}'>{count}</a><br>")
        summary_counts[reason_key] = summary_counts.get(reason_key, 0) + count

# Update the summary with the normalized keys
summary = f"""
<br><br><strong>Summary:</strong><br>
Total issues with no automation reason: {summary_counts['no_automation_reason']}<br>
Total fully automated issues: {summary_counts['fully_automated']}<br>
Total partially automated issues: {summary_counts['partially_automated']}<br>
Total automated and not usable issues: {summary_counts['automated_and_not_usable']}<br>
Total pending automation analysis issues: {summary_counts['pending_automation_analysis']}<br>
Total not feasible - not automated issues: {summary_counts['not_feasible_not_automated']}<br>
Total feasible - not automated issues: {summary_counts['feasible_not_automated']}<br>
Total feasible - automation in progress issues: {summary_counts['feasible_automation_in_progress']}<br>
Total issues categorized by label (None): {summary_counts['labels_none']}<br>
Total issues categorized by label (Has values): {summary_counts['labels_with_values']}<br>
Total issues categorized by resolution (None): {summary_counts['resolution_none']}<br>
Total issues categorized by resolution (Has values): {summary_counts['resolution_with_values']}<br>
"""

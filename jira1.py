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


5.................................................................................


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

# Function to categorize issues based on test execution status
def categorize_by_execution_status(issues):
    execution_status = {
        'Not associated': [],
        'TODO': [],
        'PASS': [],
        'FAIL': []
    }
    for issue in issues:
        executions = issue['fields'].get('executions')
        if not executions:
            execution_status['Not associated'].append(issue)
        else:
            for execution in executions:
                status = execution['status']
                if status in execution_status:
                    execution_status[status].append(issue)
                else:
                    execution_status[status] = [issue]
    return execution_status

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

# Function to print execution status issues
def print_execution_status_issues(execution_status):
    print(f"\nTest cases not associated with test execution: {len(execution_status['Not associated'])}")
    for issue in execution_status['Not associated']:
        print(f"{issue['key']}|{issue['fields']['summary']}")

    print("\nTest cases associated with test execution:")
    for status, issue_list in execution_status.items():
        if status != 'Not associated':
            print(f"{status}: {len(issue_list)}")
            for issue in issue_list:
                print(f"{issue['key']}|{issue['fields']['summary']}")

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
    execution_status = categorize_by_execution_status(issues)

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

    # Print categorized issues for labels, resolution, and execution status
    print_categorized_issues(labels_with_values, 'labels', 'NO LABEL')
    print_categorized_issues(resolution_with_values, 'resolution', 'UNRESOLVED')
    print_execution_status_issues(execution_status)

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


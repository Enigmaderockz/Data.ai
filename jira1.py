import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures

# Jira server URL
jira_url = 'https://your-company-jira.com'

# List of JQL queries
jql_queries = [
    'created >= "2024-07-31" AND created < "2024-08-01" AND component = "DRM"',
    'created >= "2024-07-31" AND created < "2024-08-01" AND component = "AIDT"'
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        # Make the request
        response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

        # Check if the request was successful
        if response.status_code == 200:
            issues = response.json()['issues']
            all_issues.extend(issues)
            if len(issues) < max_results:
                break
            start_at += max_results
        else:
            print(f"Failed to retrieve issues for JQL '{jql_query}': {response.status_code} - {response.text}")
            break

    return all_issues

for jql_query in jql_queries:
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
........................

import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures

# Jira server URL
jira_url = 'https://your-company-jira.com'

# List of JQL queries
jql_queries = [
    'created >= "2024-07-31" AND created < "2024-08-01" AND component = "DRM"',
    'created >= "2024-07-31" AND created < "2024-08-01" AND component = "AIDT"'
]

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Function to fetch all issues for a given JQL query
def fetch_all_issues(jql_query):
    start_at = 0
    max_results = 1000
    all_issues = []

    while True:
        # Request parameters
        params = {
            'jql': jql_query,
            'startAt': start_at,
            'maxResults': max_results
        }

        # Make the request
        response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

        # Check if the request was successful
        if response.status_code == 200:
            issues = response.json()['issues']
            all_issues.extend(issues)
            if len(issues) < max_results:
                break
            start_at += max_results
        else:
            print(f"Failed to retrieve issues for JQL '{jql_query}': {response.status_code} - {response.text}")
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

# Use ThreadPoolExecutor to fetch issues concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_issues, jql_query) for jql_query in jql_queries]
    for future in concurrent.futures.as_completed(futures):
        future.result()


import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED

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

for jql_query in jql_queries:
    # Request parameters
    params = {
        'jql': jql_query,
        'maxResults': 1000  # adjust the limit as needed
    }

    # Make the request
    response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

    # Check if the request was successful
    if response.status_code == 200:
        issues = response.json()['issues']

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
    else:
        print(f"Failed to retrieve issues for JQL '{jql_query}': {response.status_code} - {response.text}")

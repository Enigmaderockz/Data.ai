import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED

# Jira server URL
jira_url = 'https://your-company-jira.com'

# JQL query
jql_query = 'your JQL query here'

# Jira search API endpoint
search_url = f'{jira_url}/rest/api/2/search'

# HTTP headers
headers = {
    'Content-Type': 'application/json'
}

# Request parameters
params = {
    'jql': jql_query,
    'maxResults': 1000  # adjust the limit as needed
}

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

# Make the request
response = requests.get(search_url, headers=headers, params=params, auth=kerberos_auth)

# Check if the request was successful
if response.status_code == 200:
    issues = response.json()['issues']
    for issue in issues:
        print(issue['key'], issue['fields']['summary'])
else:
    print(f"Failed to retrieve issues: {response.status_code} - {response.text}")

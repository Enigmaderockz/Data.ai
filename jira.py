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



## import os
from datetime import datetime

# ... [rest of your imports]

def create_output_folder():
    # Create a folder with date and timestamp combination
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"output_{timestamp}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def save_issues_to_csv(issue_list, folder_name, filename):
    keys = ['key', 'summary', 'field_value']
    file_path = os.path.join(folder_name, filename)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for issue in issue_list:
            writer.writerow({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'field_value': issue['field_value']
            })
    return file_path

def print_and_save_categorized_issues(categorized_issues, field_name, default_value, email_content, base_url, folder_name):
    email_body = f"\nIssues categorized by {field_name}:<br>"
    for status, issue_list in categorized_issues.items():
        count = len(issue_list)
        
        if count > 0:
            filename = f"{field_name.replace(' ', '_')}_{status.replace(' ', '_')}_{count}.csv"
            file_path = save_issues_to_csv(issue_list, folder_name, filename)
            file_url = f"{base_url}/{filename}"
            email_body += f"{field_name} {status}: <a href='{file_url}'>{count}</a><br>"
        else:
            email_body += f"{field_name} {status}: {count}<br>"
    
    email_content.append(email_body)

def process_all_jql_queries():
    folder_name = create_output_folder()  # Create output folder at the start
    base_url = f"http://your-server.com/files/{folder_name}"  
    all_email_content = []
    summary_counts = {
        # Your summary_counts dictionary...
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
                        time.sleep(5)  # Wait before retrying
                        
    combined_email_content = "\n".join(all_email_content)
    
    # Add summary to the email content
    summary = f"""
    <br><br><strong>Summary:</strong><br>
    Total issues with no automation reason: {summary_counts['no_automation_reason']}<br>
    # Rest of your summary...
    """
    combined_email_content += summary
    
    # Add folder details to the summary
    combined_email_content += f"<br><br>Please check this folder for more details: {folder_name}<br>"

    send_email("Jira Report for All Components", combined_email_content)

# Combine components from conf.py into jql_queries
jql_queries = [
    f'created >= "2024-07-31" AND created < "2024-08-01" AND component = "{assignee}"' 
    for component in (conf.components + conf.components1)
]

# Start processing all JQL queries
process_all_jql_queries()


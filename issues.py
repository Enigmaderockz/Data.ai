######################## GROK

import requests
import json
import ijson
from tenacity import retry, stop_after_attempt, wait_exponential
import concurrent.futures
import csv
from datetime import datetime
from tqdm import tqdm

# Session for reducing network overhead
session = requests.Session()
session.headers.update({'Accept': 'application/json'})

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_issues(url, get_total=False):
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        parser = ijson.parse(r.raw)
        issues = []
        for prefix, event, value in parser:
            if prefix == 'body.issues' and event == 'start_array':
                issues = []
            elif prefix.startswith('body.issues.item.'):
                if event == 'end_map':
                    issues.append(current_item)
                    current_item = {}
                elif event == 'string' or event == 'number':
                    current_item[prefix.split('.')[-1]] = value
            elif prefix == 'body.total' and event == 'number' and get_total:
                total = value
        if get_total:
            return issues, total
        return issues

def fetch_issues_parallel(urls):
    total_urls = len(urls)
    max_workers = min(30, total_urls)  # Dynamically set max_workers based on the number of URLs
    print(f"Assigned max workers: {max_workers}")
    
    with tqdm(total=total_urls, desc="Fetching URLs", unit="url", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]", 
              ncols=100, ascii=" ▻") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(fetch_issues, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    result = future.result()
                    yield from result  # Yield issues one by one to save memory
                except Exception as exc:
                    print(f"URL {future_to_url[future]} generated an exception: {exc}")
                pbar.update(1)

def fetch_jira_issues(jql, parallel=True):
    initial_url = "http://testmanagerservice.ms.com:8000/cloud/tm/jqldump/"
    base_url = "http://testmanagerservice.ms.com:8000/cloud/tm/jqldump/"
    params = {
        'Jira Server': 'morganstanley-wm.atlassian.net',
        'Jql': jql,
        'maxResults': 100
    }
    
    url = f"{initial_url}?Jira%20Server={params['Jira Server']}&Jql={params['Jql']}&maxResults={params['maxResults']}"
    issues, total = fetch_issues(url, get_total=True)
    
    yield from issues  # Yield initial batch of issues

    if total > 100:
        if parallel:
            urls = [
                f"{base_url}?Jira%20Server={params['Jira Server']}&Jql={params['Jql']}&startAt={i}&maxResults={params['maxResults']}"
                for i in range(100, total, 100)
            ]
            yield from fetch_issues_parallel(urls)
        else:
            with tqdm(total=(total // 100), desc="Fetching Issues", unit="batch", 
                      bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]", 
                      ncols=100, ascii=" ▻") as pbar:
                for i in range(100, total, 100):
                    url = f"{base_url}?Jira%20Server={params['Jira Server']}&Jql={params['Jql']}&startAt={i}&maxResults={params['maxResults']}"
                    batch = fetch_issues(url)
                    yield from batch  # Yield issues one by one
                    pbar.update(1)

def generate_csv_with_raw_json_data(issues_iterator, csv_filename):
    headers = [
        "Issue Type", "Summary", "Assignee", "Reporter", "Priority", "Status", "Resolution",
        "Created", "Updated", "Components", "Custom field (Automation Status/Reason/Solution)",
        "Custom field (Reason for Closure)", "Project", "Key", "Project key"
    ]

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for issue in issues_iterator:
            fields = issue['fields']
            row = {
                "Issue Type": fields['issuetype']['name'],
                "Summary": fields['summary'].replace(',', ' '),
                "Assignee": fields['assignee']['displayName'] if fields['assignee'] else '',
                "Reporter": fields['reporter']['displayName'] if fields['reporter'] else '',
                "Priority": fields['priority']['name'],
                "Status": fields['status']['name'],
                "Resolution": fields['resolution']['name'] if fields['resolution'] else '',
                "Created": datetime.strptime(fields['created'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "Updated": datetime.strptime(fields['updated'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "Components": ';'.join([component['name'] for component in fields['components']]) if fields['components'] else '',
                "Custom field (Automation Status/Reason/Solution)": (
                    f"{fields['customfield_10356']['value']} - {fields['customfield_10356']['child']['value']}"
                    if fields['customfield_10356'] and 'child' in fields['customfield_10356']
                    else fields['customfield_10356']['value'] if fields['customfield_10356'] else ''
                ),
                "Custom field (Reason for Closure)": (
                    fields['customfield_10340']['value'].replace('Test : ', '') if fields['customfield_10340'] else ''
                ),
                "Project": fields['project']['name'],
                "Key": issue['key'],
                "Project key": issue['key'].split('-')[0]
            }
            writer.writerow(row)

# Usage
jql = 'project in ("GBT DRM Fleet", "LEAD Fleet", "Client Onboarding") and type = "Xray Test" and createdDate > 2024-09-01'
issues = fetch_jira_issues(jql)
generate_csv_with_raw_json_data(issues, 'output.csv')


#################################################### CHATGPT

import requests
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import concurrent.futures
import csv
from datetime import datetime
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.console import Console

# Use a session for requests to reuse connections
session = requests.Session()

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_issues(url, get_total=False):
    response = session.get(url)
    response.raise_for_status()  # Raise an error for HTTP issues
    if response.headers['Content-Type'] == 'application/json':
        data = response.json()
        data = json.loads(data['body'])
        if get_total:
            return data['issues'], data.get('total', 0)
        return data['issues']
    else:
        raise ValueError(f"Unexpected content type: {response.headers['Content-Type']}, content: {response.text}")

def fetch_issues_parallel(urls):
    results = []
    total_urls = len(urls)
    max_workers = min(30, total_urls)
    console = Console()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Fetching issues...", total=total_urls)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(fetch_issues, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    console.log(f"URL {future_to_url[future]} generated an exception: {exc}")
                progress.update(task, advance=1)
    return results

def fetch_jira_issues(jql, parallel=True):
    initial_url = "http://testmanagerservice.ms.com:8000/cloud/tm/jqldump/"
    base_url = "http://testmanagerservice.ms.com:8000/cloud/tm/jqldump/"
    params = {
        'jira Server': 'morganstanley-wm.atlassian.net',
        'Jql': jql,
        'maxResults': 100
    }
    total = 0
    all_issues = []
    url = f"{initial_url}?Jira%20Server={params['jira Server']}&Jql={params['Jql']}&maxResults={params['maxResults']}"
    issues, total = fetch_issues(url, get_total=True)
    all_issues.extend(issues)

    if total > 100:
        if parallel:
            urls = [
                f"{base_url}?Jira%20Server={params['jira Server']}&Jql={params['Jql']}&startAt={i}&maxResults={params['maxResults']}"
                for i in range(100, total, 100)
            ]
            results = fetch_issues_parallel(urls)
            for result in results:
                all_issues.extend(result)
        else:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                TimeRemainingColumn(),
                transient=True
            ) as progress:
                task = progress.add_task("Fetching batches...", total=len(range(100, total, 100)))
                for i in range(100, total, 100):
                    url = f"{base_url}?Jira%20Server={params['jira Server']}&Jql={params['Jql']}&startAt={i}&maxResults={params['maxResults']}"
                    result = fetch_issues(url)
                    all_issues.extend(result)
                    progress.update(task, advance=1)

    print(f"Total issues fetched: {len(all_issues)}")
    return all_issues

def generate_csv_with_raw_json_data(issues, csv_filename):
    headers = [
        "Issue Type", "Summary", "Assignee", "Reporter", "Priority", "Status", "Resolution",
        "Created", "Updated", "Components", "Custom field (Automation Status/Reason/Solution)",
        "Custom field (Reason for Closure)", "Project", "Key", "Project key"
    ]

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for issue in issues:
            fields = issue['fields']
            row = {
                "Issue Type": fields['issuetype']['name'],
                "Summary": fields['summary'].replace(',', ' '),
                "Assignee": fields['assignee']['displayName'] if fields['assignee'] else '',
                "Reporter": fields['reporter']['displayName'] if fields['reporter'] else '',
                "Priority": fields['priority']['name'],
                "Status": fields['status']['name'],
                "Resolution": fields['resolution']['name'] if fields['resolution'] else '',
                "Created": datetime.strptime(fields['created'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "Updated": datetime.strptime(fields['updated'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "Components": ';'.join([component['name'] for component in fields['components']]) if fields['components'] else '',
                "Custom field (Automation Status/Reason/Solution)": (
                    f"{fields['customfield_10356']['value']} - {fields['customfield_10356']['child']['value']}"
                    if fields['customfield_10356'] and 'child' in fields['customfield_10356']
                    else fields['customfield_10356']['value'] if fields['customfield_10356'] else ''
                ),
                "Custom field (Reason for Closure)": (
                    fields['customfield_10340']['value'].replace('Test : ', '') if fields['customfield_10340'] else ''
                ),
                "Project": fields['project']['name'],
                "Key": issue['key'],
                "Project key": issue['key'].split('-')[0]
            }
            writer.writerow(row)

jql = 'project in ("GBT DRM Fleet", "LEAD Fleet", "Client Onboarding") and type = "Xray Test" and createdDate > 2024-09-01'
issues = fetch_jira_issues(jql)
generate_csv_with_raw_json_data(issues, 'output.csv')

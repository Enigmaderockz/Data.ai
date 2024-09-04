import os
import requests
from requests_kerberos import HTTPKerberosAuth, REQUIRED
import concurrent.futures
import time
import conf  # Import the configuration file
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Jira server URL
jira_url = 'https://your-company-jira.com'

# Kerberos authentication
kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED)

def fetch_all_issues(jql_query):
    # [Existing code for fetching issues...]

def generate_html_table(issues, fields):
    # [Existing code for generating the HTML table...]

def save_html_report(component_name, table_html):
    """Save the HTML report to a file and return the file path."""
    file_name = f"report_{component_name}.html"
    file_path = os.path.join(os.getcwd(), file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(table_html)

    return file_path

def process_issues(jql_query, all_email_content, fields):
    issues = fetch_all_issues(jql_query)
    if not issues:
        return

    component_name = jql_query.split('component = ')[1].split()[0].replace('"', '')
    email_content = f"<h2>Results for component: {component_name}</h2><br>"

    table_html = generate_html_table(issues, fields)
    email_content += table_html

    # Save the HTML report and add the download link to the email content
    html_file_path = save_html_report(component_name, table_html)
    download_link = f"<a href='file://{html_file_path}'>Download HTML Report</a><br>"
    email_content += download_link

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



import os

def save_html_report(component_name, table_html, directory=None):
    """Save the HTML report to a specified directory and return the file path."""
    if directory is None:
        directory = os.getcwd()  # Use the current working directory if no directory is provided

    file_name = f"report_{component_name}.html"
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(table_html)

    return file_path

custom_directory = r"\\v\\global\sdfd"
table_html = "<html><body><h1>Report for ComponentA</h1><table><tr><td>Issue 1</td></tr></table></body></html>"

file_path = save_html_report("ComponentA", table_html, custom_directory)
print(f"Report saved at: {file_path}")


def generate_download_link(component_name, table_html):
    """Generate a download link for the saved HTML report."""
    # Save the HTML report and get the Unix file path
    unix_file_path = save_html_report(component_name, table_html)

    # Convert the Unix path to a Windows-style path
    windows_file_path = unix_file_path.replace("/", "\\")

    # Generate the download link with the desired format
    download_link = f"You can download the HTML file for summary: <a href='file://{windows_file_path}'>HTML report for {component_name}</a><br>"

    return download_link





###############333 CSS

def save_html_report(component_name, table_html, directory=None):
    """Save the HTML report to a specified directory and return the file path."""
    if directory is None:
        directory = os.getcwd()  # Use the current working directory if no directory is provided

    file_name = f"report_{component_name}.html"
    file_path = os.path.join(directory, file_name)

    # Define CSS directly within the <style> tag
    css_styles = """
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 14px;
            color: #333;
        }
        h2 {
            color: #1a73e8;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
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
        colgroup col {
            width: 15%;
        }
    </style>
    """

    # Combine the CSS and HTML content into a full HTML structure
    full_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        {css_styles}
    </head>
    <body>
        <h2>Report for {component_name}</h2>
        {table_html}
    </body>
    </html>
    """

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(full_html)

    return file_path



def generate_html_table(issues, fields):
    # Table header with filters
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th><input type='text' id='filter-{field}' onkeyup='filterTable(\"filter-{field}\", {fields.index(field) + 3})' placeholder='Search {html.escape(field_name)}'></th>"
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
            # Handle different field types and special cases...
            # [Your existing field handling logic]

            # Escape the cell content to prevent HTML parsing issues
            cell_content = html.escape(str(value))

            # Apply the highlighting rules
            # [Your existing highlighting logic]

            table_row += f"<td>{cell_content}</td>"

        table_row += "</tr>"
        table_rows += table_row

    # JavaScript function for filtering the table
    filter_script = """
    <script>
        function filterTable(inputId, colIndex) {
            var input, filter, table, tr, td, i, txtValue;
            input = document.getElementById(inputId);
            filter = input.value.toUpperCase();
            table = input.closest("table");
            tr = table.getElementsByTagName("tr");
            for (i = 1; i < tr.length; i++) {
                td = tr[i].getElementsByTagName("td")[colIndex];
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }       
            }
        }
    </script>
    """

    # Combine everything to form the final table HTML
    table_html = f"<table>{colgroup}{table_header}{table_rows}</table>{filter_script}"
    
    return table_html

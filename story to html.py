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





import os
import html

def generate_and_save_html_report(issues, fields, component_name, directory=None):
    """Generate an enhanced HTML report with CSS styling, filtering, and save it to a specified directory."""
    # Generate the HTML content with CSS styling and filtering
    table_html = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                text-align: left;
                padding: 12px; /* Adjust padding for wider columns */
                border: 1px solid #dddddd;
                word-break: break-word; /* Ensure text wraps in cells */
            }
            th {
                background-color: #f2f2f2;
                cursor: pointer;
            }
            th.filter-header {
                position: sticky;
                top: 0;
                background-color: #fff;
                z-index: 1;
            }
            input[type="text"] {
                width: 100%;
                box-sizing: border-box;
            }
        </style>
        <script>
            // Function to filter table based on user input
            function filterTable(input, columnIndex) {
                var filter = input.value.toUpperCase();
                var table = document.getElementById("issuesTable");
                var tr = table.getElementsByTagName("tr");

                for (var i = 1; i < tr.length; i++) {
                    var td = tr[i].getElementsByTagName("td")[columnIndex];
                    if (td) {
                        var txtValue = td.textContent || td.innerText;
                        tr[i].style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
                    }
                }
            }
        </script>
    </head>
    <body>
        <h2>Jira Issues Report</h2>
        <table id="issuesTable">
            <thead>
                <tr>
    """
    # Adding headers with filter input boxes
    for field in fields:
        table_html += f"<th class='filter-header'>{field}<br><input type='text' onkeyup='filterTable(this, {fields.index(field)})' placeholder='Filter {field}'></th>"

    table_html += "</tr></thead><tbody>"

    # Adding the table rows
    for issue in issues:
        table_html += "<tr>"
        for field in fields:
            value = issue.get(field, "Not available")
            table_html += f"<td>{html.escape(str(value))}</td>"
        table_html += "</tr>"

    table_html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Save the HTML report to the specified directory
    if directory is None:
        directory = os.getcwd()  # Use the current working directory if no directory is provided

    file_name = f"report_{component_name}.html"
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(table_html)

    return file_path

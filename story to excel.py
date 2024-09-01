Step 1: Modify generate_html_table Function
First, let's modify your generate_html_table function to add an "Export to Excel" button at the top of the table:

python
Copy code
def generate_html_table(issues, fields, excel_filename):
    # Table header
    table_header = "<tr><th>Serial No</th><th>Story</th><th>Summary</th>"
    for field in fields:
        field_name = custom_field_mapping.get(field, field.replace('_', ' ').title())
        table_header += f"<th>{html.escape(field_name)}</th>"
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
        row_color = "#f2f2f2" if i % 2 != 0 else "#ffffff"
        table_row = f"<tr style='background-color:{row_color};'><td>{i}</td><td>{html.escape(issue['key'])}</td><td>{html.escape(issue['fields']['summary'])}</td>"
        comment = "No issues" 
        acceptance_criteria = issue['fields'].get('customfield_1110', '')
        issue_type = issue['fields'].get('issuetype', {}).get('name', "")

        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            elif field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')
                requirement_status = value 
            elif isinstance(value, dict) and 'displayName' in value:
                value = value['displayName']
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, dict) and 'value' in value:
                value = value['value']	
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)

            if value is None or value == "":
                value = "Not Available"
            else:
                value = remove_special_characters(value)

            cell_content = html.escape(str(value))

            if issue_type == "User Story" and field == "customfield_1110":
                acceptance_length = len(value) if value else 0
                if acceptance_length == 0:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "less"
                elif acceptance_length < 30:
                    table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                    acceptance_criteria_comment = "more"
                else:
                    table_row += f"<td>{cell_content}</td>"
            elif field == "customfield_20627":
                if qa_assignee != "Not Available":
                    if qa_required != "Yes" and requirement_status != "OK":
                        table_row += f"<td style='background-color: yellow;'>{cell_content}</td>"
                        qa_required_comment = "Yellow column"
                    elif qa_required == "Not Available":
                        if requirement_status == "OK":
                            table_row += f"<td style='background-color: red;'>{cell_content}</td>"
                            qa_required_comment = "Red column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                    else:
                        if (qa_required == "Yes" and requirement_status != "OK") or (qa_required == "No" and requirement_status == "OK"):
                            table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                            qa_required_comment = "Blue column"
                        else:
                            table_row += f"<td>{cell_content}</td>"
                elif qa_assignee == "Not Available":
                    if requirement_status == "OK" or qa_required == "Yes":
                        table_row += f"<td style='background-color: blue;'>{cell_content}</td>"
                        qa_required_comment = "Blue column"
                    else:
                        table_row += f"<td>{cell_content}</td>"
                else:
                    table_row += f"<td>{cell_content}</td>"

        if acceptance_criteria_comment and qa_required_comment:
            combined_comment = f"{acceptance_criteria_comment}, {qa_required_comment}"
        elif acceptance_criteria_comment:
            combined_comment = acceptance_criteria_comment
        elif qa_required_comment:
            combined_comment = qa_required_comment

        table_row += f"<td>{html.escape(combined_comment)}</td>"
        table_row += "</tr>"
        table_rows += table_row

    # Add an "Export to Excel" button/link at the top
    export_button = f"""
    <p><a href="cid:{excel_filename}" download="{excel_filename}">
    <button style="padding:10px 20px; font-size:16px; background-color:#4CAF50; color:white; border:none; border-radius:5px;">Export to Excel</button>
    </a></p>
    """

    table_html = f"<table>{colgroup}<thead>{table_header}</thead><tbody>{table_rows}</tbody></table>"
    
    return export_button + table_html
Step 2: Create the Excel File
Now, let's create a function to generate the Excel file from the issues data:

python
Copy code
import pandas as pd

def export_to_excel(issues, fields, excel_filename):
    data = []
    for issue in issues:
        row = {
            'Serial No': issues.index(issue) + 1,
            'Story': issue['key'],
            'Summary': issue['fields']['summary']
        }
        for field in fields:
            value = issue['fields'].get(field, "")
            if field == 'subtasks':
                subtasks = issue['fields'].get('subtasks', [])
                subtask_keys = [subtask['key'] for subtask in subtasks]
                value = ', '.join(subtask_keys)
            elif field == 'customfield_10005' and isinstance(value, list) and value:
                value = value[0].split("name=")[-1].split(",")[0]
            elif field == 'customfield_26424' and isinstance(value, list) and value:
                value = value[0].get('status', '')
            elif isinstance(value, dict) and 'displayName' in value:
                value = value['displayName']
            elif isinstance(value, dict) and 'name' in value:
                value = value['name']
            elif isinstance(value, dict) and 'value' in value:
                value = value['value']	
            elif isinstance(value, list):
                value = ', '.join(str(v['name'] if isinstance(v, dict) and 'name' in v else v) for v in value)
            row[field] = value if value else "Not Available"
        data.append(row)

    df = pd.DataFrame(data)
    df.to_excel(excel_filename, index=False)
Step 3: Attach the Excel File to the Email
Now, you'll need to attach the generated Excel file to the email when you send it:

python
Copy code
import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_excel(html_content, excel_filename, recipients):
    msg = MIMEMultipart()
    msg['Subject'] = 'JIRA Issues Report'
    msg['From'] = 'your-email@example.com'
    msg['To'] = ', '.join(recipients)

    # Attach the HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Attach the Excel file
    with open(excel_filename, 'rb') as file:
        excel_attachment = MIMEApplication(file.read(), _subtype='xlsx')
        excel_attachment.add_header('Content-Disposition', 'attachment', filename=excel_filename)
        msg.attach(excel_attachment)

    # Send the email
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('your-email@example.com', 'your-password')
        server.send_message(msg)
Step 4: Putting It All Together
Finally, put everything together in your main function:

python
Copy code
def main():
    issues = get_issues()  # Your function to fetch issues
    fields = ['customfield_10005', 'customfield_26424', 'subtasks', 'summary', ...]  # Add the fields you want
    excel_filename = 'JIRA_Issues_Report.xlsx'

    # Generate HTML content
    html_content = generate_html_table(issues, fields, excel_filename)

    # Generate Excel file
    export_to_excel(issues, fields, excel_filename)

    # Send email with the Excel file attached
    send_email_with_excel(html_content, excel_filename, ['recipient@example.com'])

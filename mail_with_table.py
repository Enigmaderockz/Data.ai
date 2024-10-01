import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# Function to generate HTML table from CSV file
def create_html_table(csv_file):
    # Read the CSV file
    data = pd.read_csv(csv_file)

    # Initialize HTML table structure
    html = """
    <html>
    <head>
        <style>
            table {
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 11px;
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <p><strong>Test Summary:</strong></p>
        <table>
            <tr>
                <th>Serial#</th>
                <th>Test Case Name</th>
                <th>Scenario</th>
                <th>Status</th>
            </tr>
    """
    
    # Process the CSV data to extract required fields
    for idx, row in data.iterrows():
        # Extract the "name" column for test case name
        test_case_name = row['name']
        
        # Extract the part after 'feature:' in the 'doc' column for Scenario
        scenario = row['doc'].split('feature: ')[1]
        
        # Convert the status to uppercase and set color formatting
        status = row['status'].upper()
        status_color = "green" if status == "PASSED" else "red"
        
        # Create HTML rows
        html += f"""
            <tr>
                <td>{idx + 1}</td>
                <td>{test_case_name}</td>
                <td>{scenario}</td>
                <td style="color: {status_color}; font-weight: bold;">{status}</td>
            </tr>
        """
    
    # Close the HTML table and body tags
    html += """
        </table>
    </body>
    </html>
    """
    
    return html

# Function to send an email with HTML content
def send_email(sender_email, receiver_email, subject, html_content, smtp_server, smtp_port, smtp_user, smtp_password):
    # Create a multipart message
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)  # Login with your credentials
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
if __name__ == '__main__':
    # Generate the HTML content from the CSV file
    csv_file = 'your_csv_file.csv'  # Path to your CSV file
    html_content = create_html_table(csv_file)

    # Email details
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    subject = "Test Summary Report"
    
    # SMTP server configuration (Example: Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your_email@example.com"  # SMTP username (your email)
    smtp_password = "your_password"  # SMTP password (your email password)

    # Send the email
    send_email(sender_email, receiver_email, subject, html_content, smtp_server, smtp_port, smtp_user, smtp_password)



import pandas as pd

# Load both CSV files
df1 = pd.read_csv('run1.csv')
df2 = pd.read_csv('run2.csv')

# Combine the two DataFrames
combined_df = pd.concat([df1, df2], ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('combined_run.csv', index=False)

print("CSV files combined successfully into 'combined_run.csv'")





import pandas as pd
import glob

# Find all CSV files that start with 'run' and end with '.csv'
csv_files = glob.glob('run*.csv')

# Create an empty list to store DataFrames
df_list = []

# Loop through all found CSV files and load them into DataFrames
for file in csv_files:
    df = pd.read_csv(file)
    df_list.append(df)

# Combine all DataFrames into one
combined_df = pd.concat(df_list, ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('combined_run.csv', index=False)

print(f"Combined {len(csv_files)} CSV files successfully into 'combined_run.csv'")

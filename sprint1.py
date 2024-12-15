import pandas as pd
import os
from datetime import datetime

def generate_html_table_with_style(data_rows, caption, additional_links=""):
    """
    Generates a styled HTML table using provided data rows and additional links.
    
    Args:
        data_rows (list): List of HTML strings for rows.
        caption (str): Table caption text.
        additional_links (str): Additional HTML links to display above the table.

    Returns:
        str: HTML content for the table.
    """
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Calibri', sans-serif;
                margin: 20px;
                color: #333;
                text-align: left;
                font-size: 16px;
            }}
            h1 {{
                color: #4a64a1;
                text-align: center;
                font-size: 24px;
                margin-bottom: 15px;
            }}
            h2 {{
                color: #f76b98;
                font-size: 20px;
                margin-bottom: 10px;
            }}
            table {{
                width: 60%;
                border-collapse: collapse;
                margin: 20px auto;
                font-size: 12px;
                text-align: left;
                background-color: #f7f7f7;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                padding: 8px 15px;
                border: 1px solid #4a64a1;
                text-align: left;
            }}
            th {{
                background-color: #62a4d0;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
            }}
            tr:nth-child(even) {{
                background-color: #f1f1f1;
            }}
            tr:hover {{
                background-color: #e0e0e0;
            }}
            caption {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 12px;
                color: #2a4d6d;
            }}
            .expandable-section {{
                margin: 20px auto;
                width: 80%;
                text-align: left;
            }}
            details {{
                border: 1px solid #ccc;
                padding: 8px;
                margin-bottom: 10px;
                background-color: #fafafa;
            }}
            summary {{
                font-weight: bold;
                cursor: pointer;
                color: #0ca38b;
            }}
        </style>
    </head>
    <body>
        <h1>Test Case Data Summary</h1>

        <h2>Monthly Level Data</h2>
        <table>
            <caption>{caption}</caption>
            <thead>
                <tr>
                    <th>Month</th>
                    <th>Created</th>
                    <th>Automated</th>
                    <th>Manual</th>
                    <th>Backlog</th>
                    <th>Total</th>
                    <th>% Automated</th>
                </tr>
            </thead>
            <tbody>
                {''.join(data_rows)}
            </tbody>
        </table>

        <h2 id="monthly-fleet-data">Fleet & Squad Level Data</h2>
        {additional_links}
    </body>
    </html>
    """

def process_test_case_data_with_fleet(excel_file_path, output_html_path):
    # Create a folder with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder = f"sprint_auto_details_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)

    # Read CSV file
    df = pd.read_csv(excel_file_path)

    # Ensure 'Created' column is in datetime format
    df['Created'] = pd.to_datetime(df['Created'], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=['Created'])

    # Add 'Month' column to dataframe
    df['Month'] = df['Created'].dt.strftime('%B-%Y')

    # Categorize data into Automated, Manual, and Backlog
    def categorize(status):
        if pd.isna(status):
            return 'Backlog'
        elif 'Fully Automated' in status or 'Automated and Not Usable' in status:
            return 'Automated'
        elif 'Not Feasible-Not Automated' in status:
            return 'Manual'
        else:
            return 'Backlog'

    df['Category'] = df['Custom field (Automation Status/Reason/Solution)'].apply(categorize)

    # Initialize result variables
    result = []
    month_details = ""

    for month, month_group in df.groupby('Month'):
        min_date = month_group['Created'].min().strftime('%d-%m-%Y')
        max_date = month_group['Created'].max().strftime('%d-%m-%Y')
        date_range = f"{min_date} to {max_date}"

        # Create CSV for monthly data by category
        for category in ['Automated', 'Manual', 'Backlog']:
            category_group = month_group[month_group['Category'] == category]
            if not category_group.empty:
                category_csv_path = os.path.join(output_folder, f"{month.replace('-', '')}_{category}.csv")
                category_group.to_csv(category_csv_path, index=False)

        automated = (month_group['Category'] == 'Automated').sum()
        manual = (month_group['Category'] == 'Manual').sum()
        backlog = (month_group['Category'] == 'Backlog').sum()
        total = automated + manual + backlog
        percent_automated = round((automated / total) * 100, 2) if total > 0 else 0

        result.append(f"""
        <tr>
            <td>{month}</td>
            <td>{date_range}</td>
            <td>{automated}</td>
            <td>{manual}</td>
            <td>{backlog}</td>
            <td>{total}</td>
            <td>{percent_automated}%</td>
        </tr>
        """)

        fleet_details = ""
        fleet_squad_details = ""

        for fleet, fleet_group in month_group.groupby('Project key'):
            for squad, squad_group in fleet_group.groupby(fleet_group['Components'].fillna("No Component")):
                automated = (squad_group['Category'] == 'Automated').sum()
                manual = (squad_group['Category'] == 'Manual').sum()
                backlog = (squad_group['Category'] == 'Backlog').sum()
                total = automated + manual + backlog
                percent_automated = round((automated / total) * 100, 2) if total > 0 else 0

                squad_details = f"""
                <tr>
                    <td>{squad}</td>
                    <td>{automated}</td>
                    <td>{manual}</td>
                    <td>{backlog}</td>
                    <td>{total}</td>
                    <td>{percent_automated}%</td>
                </tr>
                """
                fleet_squad_details += squad_details

            fleet_details += f"<table>{fleet_squad_details}</table>"

        month_details += f"<details>{fleet_details}</details>"

    # Generate the final HTML
    html_content = generate_html_table_with_style(result, "", month_details)
    with open(output_html_path, 'w') as file:
        file.write(html_content)
    print(f"HTML file saved at: {output_html_path}")
    print(f"CSV files saved in: {output_folder}")


# Example usage:
file_path = 'jira.csv'
output_html_file = 'sprint.html'
process_test_case_data_with_fleet(file_path, output_html_file)

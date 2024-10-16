import pandas as pd
import sys

# Load data from Excel based on date and sheet name
def load_excel_data(file_path, workbook_name):
    df = pd.read_excel(file_path, sheet_name=workbook_name)
    return df

# Load and prepare tables from both Excel files for HTML report
def load_and_prepare_tables(old_file, new_file, workbook_name):
    # Load data from each file
    df1 = load_excel_data(old_file, workbook_name)
    df2 = load_excel_data(new_file, workbook_name)
    
    # Generate HTML tables with custom styling
    table1_html = df1.to_html(index=False, border=0, justify='center', 
                              classes='dataframe', table_id='table1')
    table2_html = df2.to_html(index=False, border=0, justify='center', 
                              classes='dataframe', table_id='table2')
    
    # Return tables as HTML
    return table1_html, table2_html

# Calculate percentage change for absolute increment and decrement
def calculate_percentage_change(old, new, total_old, total_new, metric):
    if total_old == 0 and total_new == 0:
        return f"{metric} remained constant with no change"
    elif total_old == 0:
        percentage_old = 0
    else:
        percentage_old = (old / total_old) * 100

    percentage_new = (new / total_new) * 100
    change = percentage_new - percentage_old
    
    return f"{metric} {'increased' if change > 0 else 'decreased' if change < 0 else 'remained constant'} by {abs(change):.2f}%"

# Find entities with specific minimum or maximum value in a column, based on `group_by`
def get_users_with_value(df, column, value, group_by):
    return df[df[column] == value][group_by].tolist()

# Compare data and return the summary
def compare_data(old_file, new_file, workbook_name, group_by):
    old_df = load_excel_data(old_file, workbook_name)
    new_df = load_excel_data(new_file, workbook_name)

    if 'Total' not in new_df.columns:
        new_df['Total'] = new_df['Automated'] + new_df['Manual'] + new_df['Backlog']
    
    merged_df = pd.merge(old_df, new_df, on=group_by, suffixes=('_old', '_new'), how='outer')
    output = {}

    # Generating summary for each section
    comparison_summary = f"Comparison Summary based on the latest data from {new_file} using {group_by}:<br><br>"
    max_automation_increase = {'user': None, 'change': -float('inf')}
    min_automation_increase = {'user': None, 'change': float('inf')}
    constant_automation_users = []

    for _, row in merged_df.iterrows():
        entity = row[group_by]
        if pd.isna(row['Automated_new']):
            comparison_summary += f"<strong>{entity}</strong><br>"
            comparison_summary += f"Data for {entity} doesn’t exist in the latest date file {new_file}.<br><br>"
            continue

        if pd.isna(row['Automated_old']):
            comparison_summary += f"<strong>{entity}</strong><br>"
            comparison_summary += f"{entity} seems to be a new entry as there is no data in old file {old_file}.<br>"
            comparison_summary += f"  • Automated test cases are {int(row['Automated_new'])}<br>"
            comparison_summary += f"  • Backlog test cases are {int(row['Backlog_new'])}<br>"
            comparison_summary += f"  • Manual test cases are {int(row['Manual_new'])}<br><br>"
            continue

        # Use a safe method to handle NaN values
        automated_old = int(row.get('Automated_old', 0) if not pd.isna(row.get('Automated_old')) else 0)
        automated_new = int(row.get('Automated_new', 0) if not pd.isna(row.get('Automated_new')) else 0)
        backlog_old = int(row.get('Backlog_old', 0) if not pd.isna(row.get('Backlog_old')) else 0)
        backlog_new = int(row.get('Backlog_new', 0) if not pd.isna(row.get('Backlog_new')) else 0)
        manual_old = int(row.get('Manual_old', 0) if not pd.isna(row.get('Manual_old')) else 0)
        manual_new = int(row.get('Manual_new', 0) if not pd.isna(row.get('Manual_new')) else 0)
        total_old = int(row.get('Total_old', 1) if not pd.isna(row.get('Total_old')) else 1)
        total_new = int(row.get('Total_new', 1) if not pd.isna(row.get('Total_new')) else 1)

        auto_change = calculate_percentage_change(automated_old, automated_new, total_old, total_new, "Automated")
        back_change = calculate_percentage_change(backlog_old, backlog_new, total_old, total_new, "Backlog")
        man_change = calculate_percentage_change(manual_old, manual_new, total_old, total_new, "Manual")

        # Track users with automation increase
        auto_percentage_change = ((automated_new - automated_old) / (automated_old if automated_old != 0 else 1)) * 100
        if auto_percentage_change > max_automation_increase['change']:
            max_automation_increase = {'user': entity, 'change': auto_percentage_change}
        if 0 < auto_percentage_change < min_automation_increase['change']:
            min_automation_increase = {'user': entity, 'change': auto_percentage_change}
        if auto_percentage_change == 0:
            constant_automation_users.append(entity)

        comparison_summary += f"<strong>{entity}</strong><br>"
        comparison_summary += f"Automated test cases are {automated_new} and have {auto_change}.<br>"
        comparison_summary += f"Backlog test cases are {backlog_new} and have {back_change}.<br>"
        comparison_summary += f"Manual test cases are {manual_new} and have {man_change}.<br><br>"

    output['Comparison Summary'] = comparison_summary

    # Section for MAX and MIN of numbers
    max_automation_val = new_df['Automated'].max()
    max_manual_val = new_df['Manual'].max()
    max_backlog_val = new_df['Backlog'].max()
    min_automation_val = new_df['Automated'].min()
    min_manual_val = new_df['Manual'].min()
    min_backlog_val = new_df['Backlog'].min()
    
    max_automation_users = get_users_with_value(new_df, 'Automated', max_automation_val, group_by)
    max_manual_users = get_users_with_value(new_df, 'Manual', max_manual_val, group_by)
    max_backlog_users = get_users_with_value(new_df, 'Backlog', max_backlog_val, group_by)
    min_automation_users = get_users_with_value(new_df, 'Automated', min_automation_val, group_by)
    min_manual_users = get_users_with_value(new_df, 'Manual', min_manual_val, group_by)
    min_backlog_users = get_users_with_value(new_df, 'Backlog', min_backlog_val, group_by)

    max_summary = f"Most automation: {', '.join(max_automation_users)} with {max_automation_val} automated tests.<br>"
    max_summary += f"Most manual effort: {', '.join(max_manual_users)} with {max_manual_val} manual tests.<br>"
    max_summary += f"Most backlog: {', '.join(max_backlog_users)} with {max_backlog_val} backlog tests.<br>"
    output['By MAX of numbers'] = max_summary

    min_summary = f"Least automation: {', '.join(min_automation_users)} with {min_automation_val} automated tests.<br>"
    min_summary += f"Least manual effort: {', '.join(min_manual_users)} with {min_manual_val} manual tests.<br>"
    min_summary += f"Least backlog: {', '.join(min_backlog_users)} with {min_backlog_val} backlog tests.<br>"
    output['By MINIMUM of numbers'] = min_summary

    focus_points = f" "
    # Section for Points to be focused
    if min_automation_increase['user'] and min_automation_increase['change'] < 100:
        focus_points += f"User with least automation increase: {min_automation_increase['user']} ({min_automation_increase['change']:.2f}%).<br>"
    filtered_constant_users = [user for user in constant_automation_users if user not in max_automation_users]
    if filtered_constant_users:
        focus_points += f"Entities with no increment in automation: {', '.join(constant_automation_users)}<br>"
    output['Points to be focused'] = focus_points

    # Section for Entities sorted by total test cases and their automation percentages
    sorted_by_total = new_df.sort_values(by='Total', ascending=False)
    total_summary = ""
    for _, row in sorted_by_total.iterrows():
        total_summary += f"{row[group_by]}: {int(row['Total'])} total test cases, {(row['Automated'] / row['Total']) * 100:.2f}% automated.<br>"
    output['Entities sorted by total test cases and their automation percentages'] = total_summary

    # Section for Entities sorted by automation percentage
    sorted_by_auto_percent = new_df.copy()
    sorted_by_auto_percent['Automation_Percentage'] = (sorted_by_auto_percent['Automated'] / sorted_by_auto_percent['Total']) * 100
    sorted_by_auto_percent = sorted_by_auto_percent.sort_values(by='Automation_Percentage', ascending=False)
    auto_percent_summary = ""
    for _, row in sorted_by_auto_percent.iterrows():
        auto_percent_summary += f"{row[group_by]}: Automation coverage is {row['Automation_Percentage']:.2f}% based on {int(row['Total'])} total test cases<br>"
    output['Entities sorted by automation percentage based on total test cases'] = auto_percent_summary

    return output

def generate_html_report(data, table1_html, table2_html, file1_name, file2_name, table_border_color="#4a90e2", table_font_family="Arial"):
    html_content = f"""
    <html>
    <head>
        <title>Comparison Report</title>
        <style>
            body {{ 
                font-family: 'Aptos Display', sans-serif;
                background-color: #f4f4f9;  
                color: #333;  
                padding: 20px;
                line-height: 1.6;
                transition: background-color 0.3s, color 0.3s;
            }}
            h1 {{
                text-align: center;
                font-size: 36px;
                margin-bottom: 20px;
                background: -webkit-linear-gradient(left, #ff7e5f, #feb47b);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            h2 {{ 
                font-size: 24px;
                cursor: pointer;
                margin: 10px 0;
                background: -webkit-linear-gradient(left, #6a11cb, #2575fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex; /* Use flexbox to align icon and text */
                align-items: center; /* Center vertically */
            }}
            .toggle-icon {{
                margin-right: 10px; /* Space between icon and text */
            }}
            .section-content {{ 
                display: none; 
                padding-left: 20px; 
            }}
            ul {{
                list-style-type: disc;
                padding-left: 40px;
            }}
            li {{
                margin-bottom: 8px;
                color: #333;  
                transition: color 0.3s;
            }}
            table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                font-family: {table_font_family};
            }}
            th, td {{
                border: 1px solid {table_border_color};
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: {table_border_color};
                color: white;
            }}
            td {{
                background-color: #f9f9f9;  
                color: #333;  
            }}
        </style>
        <script>
            function toggleSection(id, icon) {{
                var section = document.getElementById(id);
                
                if (section.style.display === 'none') {{
                    section.style.display = 'block';
                    icon.innerHTML = '&#9660;'; // Downward arrow
                }} else {{
                    section.style.display = 'none';
                    icon.innerHTML = '&#9654;'; // Rightward arrow
                }}
            }}

        </script>
    </head>
    <body>

        <h1>Comparison Report</h1>

        <h2 onclick="toggleSection('table1', this.querySelector('.toggle-icon'))">
            <span class="toggle-icon">&#9660;</span> Data from {file1_name}
        </h2>
        <div id="table1" class="section-content" style="display: block;">
            {table1_html}
        </div>

        <h2 onclick="toggleSection('table2', this.querySelector('.toggle-icon'))">
            <span class="toggle-icon">&#9660;</span> Data from {file2_name}
        </h2>
        <div id="table2" class="section-content" style="display: block;">
            {table2_html}
        </div>
    """

    # Section ids and titles
    section_ids = ['comparison_summary', 'max_numbers', 'min_numbers', 'focus_points', 'total_test_cases', 'automation_percentage']
    section_titles = [
        'Comparison Summary', 
        'By MAX of numbers', 
        'By MINIMUM of numbers', 
        'Points to be focused', 
        'Entities sorted by total test cases and their automation percentages', 
        'Entities sorted by automation percentage based on total test cases'
    ]

    for i, title in enumerate(section_titles):
        default_display = 'block' if i == 0 else 'none'
        icon_direction = '&#9660;' if i == 0 else '&#9654;' 
        html_content += f"<h2 onclick=\"toggleSection('{section_ids[i]}', this.querySelector('.toggle-icon'))\"><span class='toggle-icon'>{icon_direction}</span> {title}</h2>"
        
        html_content += f"<div id='{section_ids[i]}' class='section-content' style='display: {default_display};'>"
        html_content += "<ul>"
        
        for line in data[title].split('<br>'):
            if line.strip():
                html_content += f"<li>{line.strip()}</li>"
        
        html_content += "</ul>"
        html_content += "</div>"

    html_content += """
    </body>
    </html>
    """

    # Save the HTML to a file
    with open('comparison_report.html', 'w') as file:
        file.write(html_content)

    print("HTML report with expandable sections and toggle icons on the left has been generated.")

# Usage example
old_file = sys.argv[1]
new_file = sys.argv[2]
workbook_name = sys.argv[3]
result_by_column = sys.argv[4]

# Call compare_data and pass the output to the HTML generator

def generate_comaprison_report(old_file, new_file, workbook_name, result_by_column):
    table1_html, table2_html = load_and_prepare_tables(old_file, new_file, workbook_name)
    data = compare_data(old_file, new_file, workbook_name, result_by_column)
    # Generate HTML report
    generate_html_report(data, table1_html, table2_html,old_file, new_file, table_border_color="#FF6347", table_font_family="Verdana")

generate_comaprison_report(old_file, new_file, workbook_name, result_by_column)

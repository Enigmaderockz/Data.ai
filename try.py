import pandas as pd
import sys

# Load data from Excel based on file path and sheet name
def load_excel_data(file_path, workbook_name):
    return pd.read_excel(file_path, sheet_name=workbook_name)

# Load and prepare tables from both Excel files for HTML report
def load_and_prepare_tables(old_file, new_file, workbook_name):
    df1 = load_excel_data(old_file, workbook_name)
    df2 = load_excel_data(new_file, workbook_name)

    table1_html = df1.to_html(index=False, border=0, justify='center',
                              classes='dataframe', table_id='table1')
    table2_html = df2.to_html(index=False, border=0, justify='center',
                              classes='dataframe', table_id='table2')

    return table1_html, table2_html

# Calculate percentage change for absolute increment and decrement
def calculate_percentage_change(old, new, total_old, total_new, metric):
    if total_old == 0 and total_new == 0:
        return f"{metric} remained constant with no change"
    
    percentage_old = (old / total_old) * 100 if total_old != 0 else 0
    percentage_new = (new / total_new) * 100
    change = percentage_new - percentage_old

    return f"{metric} {'increased' if change > 0 else 'decreased' if change < 0 else 'remains constant'} {'by' if change != 0 else 'at'} {abs(change):.2f}%"

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

    comparison_summary = []
    max_automation_increase = {'user': None, 'change': -float('inf')}
    min_automation_increase = {'user': None, 'change': float('inf')}
    constant_automation_users = []

    for _, row in merged_df.iterrows():
        entity = row[group_by]
        if pd.isna(row['Automated_new']):
            comparison_summary.append(f"<strong>{entity}:</strong><br>Data for {entity} doesn't exist in the {new_file}.xlsx.<br><br>")
            continue

        if pd.isna(row['Automated_old']):
            comparison_summary.append(f"<strong>{entity}:</strong><br>{entity} seems to be a new entry as there is no data in {old_file}. However, I can fetch the details for you from {new_file}.xlsx<br>")
            comparison_summary.append(f" - Automated test case count is {int(row['Automated_new'])}<br>")
            comparison_summary.append(f" - Backlog test case count is {int(row['Backlog_new'])}<br>")
            comparison_summary.append(f" - Manual test case count is {int(row['Manual_new'])}<br><br>")
            continue

        automated_old = int(row.get('Automated_old', 0) if not pd.isna(row.get('Automated_old')) else 0)
        automated_new = int(row.get('Automated_new', 0) if not pd.isna(row.get('Automated_new')) else 0)
        backlog_old = int(row.get('Backlog_old', 0) if not pd.isna(row.get('Backlog_old')) else 0)
        backlog_new = int(row.get('Backlog_new', 0) if not pd.isna(row.get('Backlog_new')) else 0)
        manual_old = int(row.get('Manual_old', 0) if not pd.isna(row.get('Manual_old')) else 0)
        manual_new = int(row.get('Manual_new', 0) if not pd.isna(row.get('Manual_new')) else 0)
        total_old = int(row.get('Total_old', 1) if not pd.isna(row.get('Total_old')) else 1)
        total_new = int(row.get('Total_new', 1) if not pd.isna(row.get('Total_new')) else 1)

        auto_change = calculate_percentage_change(automated_old, automated_new, total_old, total_new, "Automation")
        back_change = calculate_percentage_change(backlog_old, backlog_new, total_old, total_new, "Backlog")
        man_change = calculate_percentage_change(manual_old, manual_new, total_old, total_new, "Manual")

        auto_percentage_change = ((automated_new - automated_old) / (automated_old if automated_old != 0 else 1)) * 100
        if auto_percentage_change > max_automation_increase['change']:
            max_automation_increase = {'user': entity, 'change': auto_percentage_change}
        if 0 < auto_percentage_change < min_automation_increase['change']:
            min_automation_increase = {'user': entity, 'change': auto_percentage_change}
        if auto_percentage_change == 0:
            constant_automation_users.append(entity)

        comparison_summary.append(f"<strong>{entity}:-</strong><br>Automated test case count is {automated_new} resulted in {auto_change}.<br>")
        comparison_summary.append(f"Backlog test case count is {backlog_new} resulted in {back_change}.<br>")
        comparison_summary.append(f"Manual test case count is {manual_new} resulted in {man_change}.<br><br>")

    output["Comparison Summary"] = ''.join(comparison_summary)
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

    output['By MAX of numbers'] = (
        f"Maximum automation potential: {', '.join(max_automation_users)} with {max_automation_val} automated TCs.<br>"
        f"Maximum manual effort: {', '.join(max_manual_users)} with {max_manual_val} manual TCs.<br>"
        f"Maximum backlog: {', '.join(max_backlog_users)} with {max_backlog_val} backlog TCs.<br>"
    )

    output["By MINIMUM of numbers"] = (
        f"Minimum automation potential: {', '.join(min_automation_users)} with {min_automation_val} automated TCs.<br>"
        f"Minimum manual effort: {', '.join(min_manual_users)} with {min_manual_val} manual TCs.<br>"
        f"Minimum backlog: {', '.join(min_backlog_users)} with {min_backlog_val} backlog TCs.<br>"
    )

    focus_points = []
    focus_points.append(f"{', '.join(max_manual_users)} has the highest number of manual test case count: {max_manual_val}.<br>")
    focus_points.append(f"{', '.join(max_backlog_users)} has the highest number of backlog test case count: {max_backlog_val}.<br>")
    if min_automation_increase['user'] and min_automation_increase['change'] < 100:
        focus_points.append(f"{min_automation_increase['user']} has the least increment in automation: {min_automation_increase['change']:.2f}%.<br>")
    filtered_constant_users = [user for user in constant_automation_users if user not in max_automation_users]
    if filtered_constant_users:
        focus_points.append(f"{group_by} with no increment in automation: {', '.join(filtered_constant_users)}<br>")
    output['Points to be focused'] = ''.join(focus_points)

    sorted_by_total = new_df.sort_values(by='Total', ascending=False)
    total_summary = ''.join([f"{row[group_by]}: {int(row['Total'])} total TCs with {(row['Automated'] / row['Total']) * 100:.2f}% automation coverage.<br>" for _, row in sorted_by_total.iterrows()])
    output["Entities sorted by total TCs and their automation percentages"] = total_summary

    sorted_by_auto_percent = new_df.copy()
    sorted_by_auto_percent["Automation_Percentage"] = (sorted_by_auto_percent['Automated'] / sorted_by_auto_percent['Total']) * 100
    sorted_by_auto_percent = sorted_by_auto_percent.sort_values(by='Automation_Percentage', ascending=False)
    auto_percent_summary = ''.join([f"{row[group_by]}: Automation coverage is {row['Automation_Percentage']:.2f}% based on automated {int(row['Automated'])} out of {int(row['Total'])} total TCs<br>" for _, row in sorted_by_auto_percent.iterrows()])
    output["Entities sorted by automation percentage based on total TCs"] = auto_percent_summary

    return output

# Generate HTML with expandable sections
def generate_html_report(data, table1_html, table2_html, old_file, new_file, table_border_color="#FF1E00", table_font_family="Segoe UI"):
    html_content = [
        "<html><head><title>Comparison Report</title><style>",
        "body { font-family: 'Segoe UI', sans-serif; background-color: #f4f4f9; color: #333; padding: 20px; line-height: 1.6; transition: background-color 0.3s, color 0.3s; }",
        "h1 { font-size: 36px; margin-bottom: 20px; background: linear-gradient(to right, #3AB0FF, #FF1E00); -webkit-background-clip: text; color: transparent; text-align: center; }",
        "h2 { color: #FF1E00; font-size: 24px; cursor: pointer; margin: 10px 0; position: relative; }",
        "h2:after { content: ''; display: inline-block; height: 2px; background-color: #FF1E00; width: 0; transition: width 0.3s ease; position: absolute; bottom: 0px; left: 0; }",
        "h2:hover::after { width: 40%; }",
        ".section-content { display: none; padding-left: 20px; }",
        "ul { list-style-type: disc; padding-left: 40px; }",
        "li { margin-bottom: 8px; color: #333; transition: color 0.3s; }",
        "table { width: 50%; font-size: small; border-collapse: separate; border-spacing: 2px; font-family: ", table_font_family, "; transition: background-color 0.3s, color 0.3s; }",
        "th, td { border: 1px solid ", table_border_color, "; padding: 4px; text-align: center; tansition: background-color 0.3s, color 0.3s; }",
        "th { background-color: ", table_border_color, "; color: white; }",
        "td { background-color: #f9f9f9; color: #333; }",

        ".toggle-switch { position: fixed; top: 10px; right: 10px; display: flex; align-items: center; }",
        ".toggle-switch input[type='checkbox'] { display: none; }",
        ".toggle-switch-label { width: 50px; height: 26px; background-color: #4CAF50; border-radius: 13px; cursor: pointer; position: relative; transition: background-color 0.3s; }",
        ".toggle-switch-label::after { content: ''; width: 20px; height: 20px; background-color: white; border-radius: 50%; position: absolute; top: 3px; left: 4px; transition: transform 0.3s; }",
        ".toggle-switch input[type='checkbox']:checked + .toggle-switch-label { background-color: #ccc; }", 
        ".toggle-switch input[type='checkbox']:checked + .toggle-switch-label::after { transform: translateX(24px); }",
        "</style><script>",

        "function toggleSection(id) { var section = document.getElementById(id); section.style.display = section.style.display == 'none' ? 'block' : 'none'; }",
        "function toggleTheme() { var body = document.body; var listItems = document.querySelectorAll('li'); var tableCells = document.querySelectorAll('td'); var tableHeaders = document.querySelectorAll('th');",
        "if (body.style.backgroundColor == 'rgb(51, 51, 51)') { body.style.backgroundColor = '#f4f4f9'; body.style.color = '#333'; listItems.forEach(function(item) { item.style.color = '#333'; }); tableCells.forEach(function(cell) { cell.style.backgroundColor = '#f9f9f9'; cell.style.color = '#333'; }); }",
        "else { body.style.backgroundColor = '#333'; body.style.color = '#eee'; listItems.forEach(function(item) { item.style.color = '#eee'; }); tableCells.forEach(function(cell) { cell.style.backgroundColor = '#444'; cell.style.color = '#eee'; }); }",
        "</script></head><body><div class='toggle-switch'><input type='checkbox' id='themeToggle' onclick='toggleTheme()'><label for='themeToggle' class='toggle-switch-label'></label></div>",
        "<h1>Comparison Analysis Report</h1>",
        "<h2 onclick=\"toggleSection('table1')\">Data from", old_file, "</h2><div id='table1' class='section-content' style='display: block;'>", table1_html, "</div>",
        "<h2 onclick=\"toggleSection('table2')\">Data from", new_file, "</h2><div id='table2' class='section-content' style='display: block;'>", table2_html, "</div>"
    ]

    section_ids = ['comparison_summary', 'max_numbers', 'min_numbers', 'focus_points', 'total_test_cases', 'automation_percentage']
    section_titles = [
        'Points to be focused',
        'Comparison Summary',
        'By MAX of numbers',
        'By MINIMUM of numbers',
        'Entities sorted by total TCs and their automation percentages',
        'Entities sorted by automation percentage based on total TCs']
    
    for i, title in enumerate(section_titles):
        default_display = 'block' if i == 0 else 'none'
        html_content.append(f"<h2 onclick=\"toggleSection('{section_ids[i]}')\">{title}</h2>")
        html_content.append(f"<div id='{section_ids[i]}' class='section-content' style='display: {default_display};'><ul>")
        for line in data[title].split("<br>"):
            if "Comparison summary" in line or "seems to be a new entry as there is no data" in line:
                html_content.append(f"<p style='margin-left: 0px;'>{line.strip()}<br></p>")
            elif ":-" in line:
                html_content.append(f"<p style='margin-left: 0px; color:#3ABOFF;'>{line.strip()}<br></p>")
            elif "increased by" in line:
                parts = line.split("increased by")
                html_content.append(f"<li style='margin-left: 40px;'>{parts[0]}<span style='color:#4CAF50;'><strong>increased by {parts[1]}</strong></span></li>")
            elif "decreased by" in line:
                parts = line.split("decreased by")
                html_content.append(f"<li style='margin-left: 40px;'>{parts[0]}<span style='color:red;'><strong>decreased by {parts[1]}</strong></span></li>")
            elif "remains constant" in line:
                parts = line.split("remains constant")
                html_content.append(f"<li style='margin-left: 40px;'>{parts[0]}<span style='color:#e67e22;'><strong>remains constant {parts[1]}</strong></span></li>")
            elif line.strip():
                html_content.append(f"<li style='margin-left: 40px;'>{line.strip()}</li>")
        html_content.append("</ul></div>")

    html_content.append("</body></html>")

    with open('comparison_report.html', 'w') as file:
        file.write(''.join(html_content))

    print("comparison_report.html report has been generated.")

# Usage example
old_file = sys.argv[1]
new_file = sys.argv[2]
workbook_name = sys.argv[3]
result_by_column = sys.argv[4]

def generate_comparison_report(old_file, new_file, workbook_name, result_by_column):
    table1_html, table2_html = load_and_prepare_tables(old_file, new_file, workbook_name)
    data = compare_data(old_file, new_file, workbook_name, result_by_column)
    generate_html_report(data, table1_html, table2_html, old_file, new_file, table_border_color="#3ABOFF", table_font_family="Segoe UI")

generate_comparison_report(old_file, new_file, workbook_name, result_by_column)

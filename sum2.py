import pandas as pd
from colorama import Fore, Style
import sys

# Load data from Excel based on date and sheet name
def load_excel_data(file_date, workbook_name):
    file_path = f'jan_aug_2024_{file_date}.xlsx'
    df = pd.read_excel(file_path, sheet_name=workbook_name)
    return df

# Calculate percentage change for absolute increment and decrement
def calculate_percentage_change(old, new, total_old, total_new, metric):
    if total_old == 0 and total_new == 0:
        return f"{metric} remained constant with no change", Fore.YELLOW
    elif total_old == 0:
        percentage_old = 0
    else:
        percentage_old = (old / total_old) * 100

    percentage_new = (new / total_new) * 100
    change = percentage_new - percentage_old
    
    if metric == "Automated":
        color = Fore.GREEN if change > 20 else Fore.RED if change < 0 else Fore.YELLOW
    elif metric == "Backlog":
        color = Fore.RED if change > 0 else Fore.GREEN if change <= -20 else Fore.YELLOW
    elif metric == "Manual":
        color = Fore.RED if change > 0 else Fore.GREEN if change < 0 else Fore.YELLOW
    
    return f"{metric} {'increased' if change > 0 else 'decreased' if change < 0 else 'remained constant'} by {abs(change):.2f}%", color

# Find entities with specific minimum or maximum value in a column, based on `group_by`
def get_users_with_value(df, column, value, group_by):
    return df[df[column] == value][group_by].tolist()

# Compare data and create a business-friendly summary
def compare_data(old_date, new_date, workbook_name, group_by):
    old_df = load_excel_data(old_date, workbook_name)
    new_df = load_excel_data(new_date, workbook_name)

    # Add a total column to calculate automation percentage if not present
    if 'Total' not in new_df.columns:
        new_df['Total'] = new_df['Automated'] + new_df['Manual'] + new_df['Backlog']
    
    merged_df = pd.merge(old_df, new_df, on=group_by, suffixes=('_old', '_new'), how='outer')

    output_message = f"\nComparison Summary as per the data fetched on the latest date {new_date} based on {group_by}:\n\n"
    
    max_automation_increase = {'user': None, 'change': -float('inf')}
    min_automation_increase = {'user': None, 'change': float('inf')}
    constant_automation_users = []

    for _, row in merged_df.iterrows():
        entity = row[group_by]

        if pd.isna(row['Automated_new']):
            output_message += f"{entity}\n"
            output_message += f"{Fore.YELLOW}• Data for {entity} doesn’t exist in the jan_aug_2024_{new_date}.xlsx{Style.RESET_ALL}\n\n"
            continue

        if pd.isna(row['Automated_old']):
            output_message += f"{entity}\n"
            output_message += f"{Fore.YELLOW}• {entity} seems to be a new entry as there is no data in jan_aug_2024_{old_date}.xlsx.{Style.RESET_ALL}\n"
            output_message += f"  • Automated test cases are {int(row['Automated_new'])}\n"
            output_message += f"  • Backlog test cases are {int(row['Backlog_new'])}\n"
            output_message += f"  • Manual test cases are {int(row['Manual_new'])}\n\n"
            continue

        automated_old = int(row.get('Automated_old', 0))
        automated_new = int(row.get('Automated_new', 0))
        backlog_old = int(row.get('Backlog_old', 0))
        backlog_new = int(row.get('Backlog_new', 0))
        manual_old = int(row.get('Manual_old', 0))
        manual_new = int(row.get('Manual_new', 0))
        total_old = int(row.get('Total_old', 1))
        total_new = int(row.get('Total_new', 1))

        auto_change, auto_color = calculate_percentage_change(automated_old, automated_new, total_old, total_new, "Automated")
        back_change, back_color = calculate_percentage_change(backlog_old, backlog_new, total_old, total_new, "Backlog")
        man_change, man_color = calculate_percentage_change(manual_old, manual_new, total_old, total_new, "Manual")

        auto_percentage_change = ((automated_new - automated_old) / (automated_old if automated_old != 0 else 1)) * 100
        if auto_percentage_change > max_automation_increase['change']:
            max_automation_increase = {'user': entity, 'change': auto_percentage_change}
        if 0 < auto_percentage_change < min_automation_increase['change']:
            min_automation_increase = {'user': entity, 'change': auto_percentage_change}
        if auto_percentage_change == 0:
            constant_automation_users.append(entity)

        output_message += f"{entity}\n"
        output_message += f"{Fore.GREEN}• Automated test cases are {automated_new} and have {auto_color}{auto_change}{Style.RESET_ALL}.\n"
        output_message += f"{Fore.GREEN}• Backlog test cases are {backlog_new} and have {back_color}{back_change}{Style.RESET_ALL}.\n"
        output_message += f"{Fore.GREEN}• Manual test cases are {manual_new} and have {man_color}{man_change}{Style.RESET_ALL}.\n\n"

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

    output_message += f"\n{Fore.BLUE}By MAX of numbers{Style.RESET_ALL}\n"
    output_message += f" • Most automation: {', '.join(max_automation_users)} with {max_automation_val} automated tests.\n"
    output_message += f" • Most manual effort: {', '.join(max_manual_users)} with {max_manual_val} manual tests.\n"
    output_message += f" • Most backlog: {', '.join(max_backlog_users)} with {max_backlog_val} backlog tests.\n"
    output_message += f"\n{Fore.BLUE}By MINIMUM of numbers{Style.RESET_ALL}\n"
    output_message += f" • Least automation: {', '.join(min_automation_users)} with {min_automation_val} automated tests.\n"
    output_message += f" • Least manual effort: {', '.join(min_manual_users)} with {min_manual_val} manual tests.\n"
    output_message += f" • Least backlog: {', '.join(min_backlog_users)} with {min_backlog_val} backlog tests.\n"
    output_message += f"\n{Fore.BLUE}Points to be focused{Style.RESET_ALL}\n"

    # Exclude users with 100% automation increase from "Points to be focused"
    if min_automation_increase['user'] and min_automation_increase['change'] < 100:
        output_message += f"{Fore.RED} • User with least automation % increase: {min_automation_increase['user']} with an increase of {min_automation_increase['change']:.2f}%{Style.RESET_ALL}\n"

    # Add users with constant automation who are not at 100% automation
    filtered_constant_users = [user for user in constant_automation_users if user not in max_automation_users]
    if filtered_constant_users:
        output_message += f" • Users with no increment in automation %: {', '.join(filtered_constant_users)}\n"

    
    # Sorting entities by the total number of test cases in descending order
    sorted_df = new_df.copy()
    sorted_df['Automation_Percentage'] = (sorted_df['Automated'] / sorted_df['Total']) * 100
    sorted_df = sorted_df.sort_values(by='Total', ascending=False)
    output_message += f"\n{Fore.MAGENTA}Entities sorted by total test cases and their automation percentages:{Style.RESET_ALL}\n"
    for _, row in sorted_df.iterrows():
        output_message += f" • {row[group_by]}: {int(row['Total'])} total test cases, {row['Automation_Percentage']:.2f}% automated.\n"
    
    # Sorting entities by automation percentage in descending order
    sorted_df['Automation_Percentage'] = (sorted_df['Automated'] / sorted_df['Total']) * 100
    sorted_df = sorted_df.sort_values(by='Automation_Percentage', ascending=False)
    output_message += f"\n{Fore.MAGENTA}Entities sorted by automation percentage based on total test cases:{Style.RESET_ALL}\n"
    for _, row in sorted_df.iterrows():
        output_message += f" • {row[group_by]}: Automation coverage is {row['Automation_Percentage']:.2f}% based on {int(row['Total'])} total test cases\n"


    return output_message

# Usage
old_date = sys.argv[1]
new_date = sys.argv[2]
workbook_name = sys.argv[3]
group_by_column = sys.argv[4]

# Call compare_data and store the output

# Call compare_data and store the output in a variable
comparison_summary = compare_data(old_date, new_date, workbook_name, group_by_column)

# Print the output
print(comparison_summary)
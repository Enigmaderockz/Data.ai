import pandas as pd
from openpyxl import load_workbook
import argparse

def generate_summary(file_path, grouping_columns, sheet_name):
    # Load the Excel file
    excel_data = pd.read_excel(file_path, sheet_name=0)

    # Define the statuses that map to each category
    automated_status = ['Automated']
    backlog_status = ['Partial automated', 'Not automated', 'Automatable but not automated']
    manual_status = ['Not feasible not automated']

    # Create a summary DataFrame grouped by the specified columns
    summary_df = (
        excel_data
        .groupby(grouping_columns + ['Overall Automation Status'])
        .size()
        .reset_index(name='Count')
        .pivot_table(
            index=grouping_columns,
            columns='Overall Automation Status',
            values='Count',
            fill_value=0
        )
        .reset_index()
    )

    # Reindex to add missing columns with a default value of 0
    all_statuses = automated_status + backlog_status + manual_status
    summary_df = summary_df.reindex(columns=grouping_columns + all_statuses, fill_value=0)

    # Calculate totals and assign to respective columns
    summary_df['Automated'] = summary_df[automated_status].sum(axis=1)
    summary_df['Backlog'] = summary_df[backlog_status].sum(axis=1)
    summary_df['Manual'] = summary_df[manual_status].sum(axis=1)
    summary_df['Total'] = summary_df[['Automated', 'Backlog', 'Manual']].sum(axis=1)

    # Calculate the % Automated column
    summary_df['% Automated'] = (summary_df['Automated'] / summary_df['Total']) * 100

    # Select the required columns for the final summary
    final_summary_columns = grouping_columns + ['Automated', 'Backlog', 'Manual', 'Total', '% Automated']
    final_summary_df = summary_df[final_summary_columns]

    # Append the new sheet to the workbook
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        final_summary_df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Data has been successfully written to the sheet '{sheet_name}' in the workbook.")

    # Return the filename
    return file_path

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate summary report for Excel data.')
    parser.add_argument('file_path', help='Path to the Excel file')
    parser.add_argument('grouping_columns', nargs='+', help='Columns to group by (e.g., "Name Squad")')
    parser.add_argument('sheet_name', help='Name of the worksheet to create or replace')

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with parsed arguments
    generate_summary(args.file_path, args.grouping_columns, args.sheet_name)

#Usage:
#python generate_summary.py jan_aug_2024_2024-10-11.xlsx "Name" "Squad" "By Name"
#python generate_summary.py jan_aug_2024_2024-10-11.xlsx "Squad" "By Squad"
#python group.py jan_aug_2024_2024-10-11.xlsx "Name" "Squad" "Qa Required" "By QA"

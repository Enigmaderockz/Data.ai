def process_test_case_data_with_fleet(excel_file_path, output_html_path):
    # Create a folder with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder = f"sprint_auto_details_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)

    # Read Excel file
    df = pd.read_excel(excel_file_path)

    # Debug: Check unique values in the column
    print("Unique values in 'Custom field (Automation Status/Reason/Solution)':")
    print(df['Custom field (Automation Status/Reason/Solution)'].unique())

    # Ensure consistent formatting by stripping whitespace
    df['Custom field (Automation Status/Reason/Solution)'] = df['Custom field (Automation Status/Reason/Solution)'].astype(str).str.strip()

    # Function to extract month name and year from Created column
    def extract_month_year(date_str):
        return pd.to_datetime(date_str).strftime('%B-%Y')

    # Add 'Month' column to dataframe
    df['Month'] = df['Created'].apply(extract_month_year)

    # Categorize data into Automated, Manual, and Backlog
    def categorize(status):
        # Debugging: Print the value being processed
        print(f"Processing status: {status}")
        
        if pd.isna(status) or status.strip() == '' or status.lower() == 'nan':
            return 'Backlog'
        status = status.strip()
        if 'Fully Automated' in status or 'Automated and Not Usable' in status:
            return 'Automated'
        elif 'Not Feasible-Not Automated' in status:
            return 'Manual'
        else:
            return 'Backlog'
    df['Category'] = df['Custom field (Automation Status/Reason/Solution)'].apply(categorize)

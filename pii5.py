def process_pii(csv_file, **kwargs):
    # Extracting the parameters from kwargs
    phone_column = kwargs.get('phone_column', None)
    first_name_column = kwargs.get('first_name_column', None)
    last_name_column = kwargs.get('last_name_column', None)
    email_column = kwargs.get('email_column', None)

    # Call the previously defined PII detection function
    pii_status, pii_details = pii_detection_from_csv(csv_file, phone_column, first_name_column, last_name_column, email_column)

    if pii_status is True:
        print("No PII detected")
    elif pii_status is False:
        print("PII detected in the following columns:")
        for column, values in pii_details.items():
            print(f"{column}: {values}")
        return pii_status, pii_details
    return pii_status, None

# Variable containing column names
abc = 'phone_number:first_name:last_name'  # Example input

# Splitting the string into a list of column names
columns = abc.split(':')

# Create a dictionary to hold the mapped values, initializing all to None
mapped_columns = {
    'phone_column': None,
    'first_name_column': None,
    'last_name_column': None,
    'email_column': None
}

# Populate the mapped_columns based on the input columns
for col in columns:
    mapped_columns[f'{col}_column'] = col  # Create keys dynamically

# Assuming you have a CSV file path defined
csv_file_path = 'your_file.csv'

# Call the process_pii function using the mapped_columns dictionary
status, pii_columns = process_pii(csv_file_path, **mapped_columns)

# Use the pii_columns in another function if needed
if status is False:
    for column, values in pii_columns.items():
        print(f"In column {column}, these values were detected as PII: {values}")

import re
import phonenumbers
import pandas as pd

# Function to detect PII in a specified column from a CSV file
def pii_detection_from_csv(csv_file, column_name, attribute):
    try:
        # Load the CSV into a DataFrame
        df = pd.read_csv(csv_file)
        
        # Check if the column exists in the DataFrame
        if column_name not in df.columns:
            print(df.columns)
            return f"Error: Column '{column_name}' not found in CSV. Please provide a valid column name.", None
        
        # Proceed with loading the specified column
        df = df[[column_name]]
    
    except ValueError as e:
        return f"Error: {e}", None
    
    detected_columns = {}  # To store columns with detected PII and their first 10 values


    if attribute == 'email':
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        df['email_detected'] = df[column_name].apply(lambda x: bool(re.search(email_pattern, str(x))))
        if df['email_detected'].any():
            detected_columns[column_name] = df[df['email_detected']][column_name].head(10).tolist()
    
    elif attribute == 'phone':
        def is_phone_number(value):
            try:
                parsed = phonenumbers.parse(str(value), None)
                return phonenumbers.is_valid_number(parsed)
            except:
                return False
        df['phone_detected'] = df[column_name].apply(is_phone_number)
        if df['phone_detected'].any():
            detected_columns[column_name] = df[df['phone_detected']][column_name].head(10).tolist()

    elif attribute in ['first name', 'last name', 'full name']:
        # Match names starting with upper or lowercase letters
        name_pattern = r'^[A-Za-z]+'
        df['name_detected'] = df[column_name].apply(lambda x: bool(re.match(name_pattern, str(x))))
        if df['name_detected'].any():
            detected_columns[column_name] = df[df['name_detected']][column_name].head(10).tolist()

    # If any PII is detected in the column, return False and the detected data
    if detected_columns:
        return False, detected_columns
    
    # If no PII is detected, return True
    return True, None


# Generalized function for processing PII detection
def process_pii(csv_file, attribute, column_name):
    # Call the PII detection function based on the attribute type
    pii_status, pii_details = pii_detection_from_csv(csv_file, column_name, attribute)

    if isinstance(pii_status, str) and "Error" in pii_status:
        # If there's an error (such as column not found), print the error and return
        print(pii_status)
        return None, None
    
    if pii_status is True:
        print(f"No PII detected in column: {column_name}")
    elif pii_status is False:
        # If PII is detected, print the column names and the detected PII values
        print(f"PII detected in the following column:")
        for column, values in pii_details.items():
            print(f"{column}: {values}")
        
        # You can use the returned pii_details for further processing
        return pii_status, pii_details
    
    return pii_status, None

# Example usage:
csv_file_path = 'pii.csv'
'''
# Checking PII for phone numbers
status, pii_columns = process_pii(csv_file_path, attribute='phone', column_name='phone_number')
'''
# Checking PII for first names
status, pii_columns = process_pii(csv_file_path, attribute='first name', column_name='FIRSTi_NME')
'''
# Checking PII for emails
status, pii_columns = process_pii(csv_file_path, attribute='email', column_name='email_ID')
'''
# Use the pii_columns in another function if needed
# Check if PII was detected or if an error occurred
if status is None:
    # This means there was an error, and it was already printed
    pass
elif status is False:
    for column, values in pii_columns.items():
        print(f"In column {column}, these values were detected as PII: {values}")
else:
    print("No PII detected.")


# Check if PII was detected or if an error occurred
if status is None:
    # This means there was an error, and it was already printed
    pass
elif status is False:
    assert False, '\n'.join(f"In column {column}, these values were detected as PII: {values}" for column, values in pii_columns.items())
else:
    print("No PII detected.")


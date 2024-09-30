import re
import phonenumbers
import pandas as pd

# Function to detect emails, phone numbers, and names in the specified columns from a CSV file
def pii_detection_from_csv(csv_file, phone_column, name_column, email_column):
    # Load the specified columns from the CSV file into a DataFrame
    try:
        df = pd.read_csv(csv_file, usecols=[phone_column, name_column, email_column])
    except ValueError as e:
        return f"Error: {e}", None
    
    # Regular expression for detecting email addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    detected_columns = {}  # To store columns with detected PII and their first 5 values
    
    # Detect emails in the specified column
    if email_column:
        df['email_detected'] = df[email_column].apply(lambda x: bool(re.search(email_pattern, str(x))))
        if df['email_detected'].any():
            detected_columns[email_column] = df[df['email_detected']][email_column].head(5).tolist()
    
    # Detect phone numbers in the specified column
    if phone_column:
        def is_phone_number(value):
            try:
                parsed = phonenumbers.parse(str(value), None)
                return phonenumbers.is_valid_number(parsed)
            except:
                return False
        df['phone_detected'] = df[phone_column].apply(is_phone_number)
        if df['phone_detected'].any():
            detected_columns[phone_column] = df[df['phone_detected']][phone_column].head(5).tolist()
    
    # Detect names in the specified column (heuristic: starts with capital letters)
    if name_column:
        df['name_detected'] = df[name_column].apply(lambda x: bool(re.match(r'^[A-Z][a-z]+', str(x))))
        if df['name_detected'].any():
            detected_columns[name_column] = df[df['name_detected']][name_column].head(5).tolist()
    
    # If any PII detected in any of the columns, return False and the detected data
    if detected_columns:
        return False, detected_columns
    
    # If no PII detected, return True
    return True, None

# Example usage in another function
def process_pii(csv_file, phone_column, name_column, email_column):
    pii_status, pii_details = pii_detection_from_csv(csv_file, phone_column, name_column, email_column)
    
    if pii_status is True:
        print("No PII detected")
    elif pii_status is False:
        # Use pii_details (detected columns and values) in this function
        print("PII detected in the following columns:")
        for column, values in pii_details.items():
            print(f"{column}: {values}")
        
        # You can use the returned pii_details for further processing
        return pii_status, pii_details
    
    return pii_status, None

# Example CSV file and columns
csv_file_path = 'your_file.csv'
phone_col = 'phone_number'
name_col = 'first_name'
email_col = 'email_client'

# Call the process_pii function
status, pii_columns = process_pii(csv_file_path, phone_col, name_col, email_col)

# Use the pii_columns in another function if needed
if status is False:
    # Access column names and values
    for column, values in pii_columns.items():
        print(f"In column {column}, these values were detected as PII: {values}")

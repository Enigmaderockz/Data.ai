import re
import phonenumbers
import pandas as pd

# Function to detect PII in specified columns from a CSV file
def pii_detection_from_csv(csv_file, phone_column=None, first_name_column=None, last_name_column=None, email_column=None):
    # Build the list of columns to load from the CSV based on which ones are not None
    columns_to_load = [col for col in [phone_column, first_name_column, last_name_column, email_column] if col]
    
    # Load only the specified columns from the CSV file into a DataFrame
    try:
        df = pd.read_csv(csv_file, usecols=columns_to_load)
    except ValueError as e:
        return f"Error: {e}", None
    
    # Regular expression for detecting email addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    detected_columns = {}  # To store columns with detected PII and their first 5 values
    
    # Detect emails if email_column is provided
    if email_column:
        df['email_detected'] = df[email_column].apply(lambda x: bool(re.search(email_pattern, str(x))))
        if df['email_detected'].any():
            detected_columns[email_column] = df[df['email_detected']][email_column].head(5).tolist()
    
    # Detect phone numbers if phone_column is provided
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
    
    # Detect first names if first_name_column is provided
    if first_name_column:
        df['first_name_detected'] = df[first_name_column].apply(lambda x: bool(re.match(r'^[A-Z][a-z]+', str(x))))
        if df['first_name_detected'].any():
            detected_columns[first_name_column] = df[df['first_name_detected']][first_name_column].head(5).tolist()
    
    # Detect last names if last_name_column is provided
    if last_name_column:
        df['last_name_detected'] = df[last_name_column].apply(lambda x: bool(re.match(r'^[A-Z][a-z]+', str(x))))
        if df['last_name_detected'].any():
            detected_columns[last_name_column] = df[df['last_name_detected']][last_name_column].head(5).tolist()
    
    # If any PII is detected in any of the columns, return False and the detected data
    if detected_columns:
        return False, detected_columns
    
    # If no PII is detected, return True
    return True, None

# Example usage in another function
def process_pii(csv_file, phone_column=None, first_name_column=None, last_name_column=None, email_column=None):
    pii_status, pii_details = pii_detection_from_csv(csv_file, phone_column, first_name_column, last_name_column, email_column)
    
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

# Example: Only checking PII for phone numbers
csv_file_path = 'your_file.csv'
phone_col = 'phone_number'

# Call the process_pii function, only passing the phone number column
status, pii_columns = process_pii(csv_file_path, phone_column=phone_col)

# Use the pii_columns in another function if needed
if status is False:
    # Access column names and values
    for column, values in pii_columns.items():
        print(f"In column {column}, these values were detected as PII: {values}")

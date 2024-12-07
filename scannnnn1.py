Here's the modified Python program that adds a loading bar when scanning for phone numbers, and then moves on to scan for other PII:

```
import re
import time
from tqdm import tqdm

# Define regular expressions for US phone numbers
us_phone_regex = re.compile(r'(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?:\s?ext\.?\s?\d{1,5})?')

# Define regular expressions for India phone numbers
in_phone_regex = re.compile(r'\+91\s?\d{10}|\+91\s?\(?\d{3}\)?\s?\d{3}\s?\d{4}')

# Define regular expressions for other PII
email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
ssn_regex = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
passport_regex = re.compile(r'\b[A-Z]{1}[0-9]{7}\b')

def scan_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            lines = content.splitlines()

            print("Scanning for US phone numbers...")
            us_phone_matches = []
            for line in tqdm(lines, desc="Progress", unit="lines"):
                matches = us_phone_regex.findall(line)
                us_phone_matches.extend(matches)
            print(f"Found {len(us_phone_matches)} US phone numbers.")

            print("Scanning for India phone numbers...")
            in_phone_matches = []
            for line in tqdm(lines, desc="Progress", unit="lines"):
                matches = in_phone_regex.findall(line)
                in_phone_matches.extend(matches)
            print(f"Found {len(in_phone_matches)} India phone numbers.")

            print("Scanning for email addresses...")
            email_matches = email_regex.findall(content)
            print(f"Found {len(email_matches)} email addresses.")

            print("Scanning for SSN numbers...")
            ssn_matches = ssn_regex.findall(content)
            print(f"Found {len(ssn_matches)} SSN numbers.")

            print("Scanning for passport numbers...")
            passport_matches = passport_regex.findall(content)
            print(f"Found {len(passport_matches)} passport numbers.")

            print("\nPII Values:")
            if us_phone_matches:
                print("US Phone numbers:")
                for match in us_phone_matches:
                    print(match)
            if in_phone_matches:
                print("India Phone numbers:")
                for match in in_phone_matches:
                    print(match)
            if email_matches:
                print("Email addresses:")
                for match in email_matches:
                    print(match)
            if ssn_matches:
                print("SSN numbers:")
                for match in ssn_matches:
                    print(match)
            if passport_matches:
                print("Passport numbers:")
                for match in passport_matches:
                    print(match)
    except FileNotFoundError:
        print("File not found.")

# Example usage
scan_file('example.txt')
```

This program uses the `tqdm` library to display a loading bar when scanning for US phone numbers and India phone numbers. The `tqdm` library is a Python progress bar library that can be used to display a progress bar in the terminal.

Note that you may need to install the `tqdm` library using pip:

```
bash
pip install tqdm
```
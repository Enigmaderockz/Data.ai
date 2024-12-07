Here's the modified Python program that supports the additional US phone number formats:

```
import re

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
            us_phone_matches = us_phone_regex.findall(content)
            in_phone_matches = in_phone_regex.findall(content)
            email_matches = email_regex.findall(content)
            ssn_matches = ssn_regex.findall(content)
            passport_matches = passport_regex.findall(content)

            if us_phone_matches:
                print("US Phone numbers found:")
                for match in us_phone_matches:
                    print(match)
            if in_phone_matches:
                print("India Phone numbers found:")
                for match in in_phone_matches:
                    print(match)
            if email_matches:
                print("Email addresses found:")
                for match in email_matches:
                    print(match)
            if ssn_matches:
                print("SSN numbers found:")
                for match in ssn_matches:
                    print(match)
            if passport_matches:
                print("Passport numbers found:")
                for match in passport_matches:
                    print(match)
    except FileNotFoundError:
        print("File not found.")

# Example usage
scan_file('example.txt')
```

This modified program uses an updated regular expression for US phone numbers that supports the additional formats:

```
us_phone_regex = re.compile(r'(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?:\s?ext\.?\s?\d{1,5})?')
```

This regular expression supports the following formats:

- XXX-XXX-XXXX
- XXX.XXX.XXXX
- (XXX) XXX-XXXX
- XXX XXX XXXX
- +1 XXX XXX XXXX
- +1-XXX-XXX-XXXX
- 001-XXX-XXX-XXXX
- 1-800-XXX-XXXX
- 1-900-XXX-XXXX
- XXX-XXX-XXXX ext. XXXX
- (XXX) XXX-XXXX ext. XXXX

Note that this regular expression may still not support all possible formats, and you may need to modify it further to suit your specific requirements.
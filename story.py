import re
from tqdm import tqdm
import spacy

# Load the spaCy model for named entity recognition
nlp = spacy.load('en_core_web_sm')

# Use a single, more comprehensive regex for phone numbers to avoid duplicates
phone_regex = re.compile(r'\+?1?\s?[-\(\)\s]*\d{3}[-\)\s]*\d{3}[-\s]*\d{4}')

# Email regex pattern
email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

def find_matches(line, regex):
    """Find all matches in a line for a given regex pattern."""
    return regex.findall(line)

def scan_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.splitlines()

            # Scan for phone numbers
            print("Scanning for phone numbers...")
            phone_matches = []
            for line in tqdm(lines, desc="Progress", unit="lines", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
                phone_matches.extend(find_matches(line, phone_regex))
            # Use set to remove duplicates
            phone_matches = list(set(phone_matches))
            print(f"Found {len(phone_matches)} unique phone numbers.")

            # Scan for emails
            print("\nScanning for emails...")
            email_matches = []
            for line in tqdm(lines, desc="Progress", unit="lines", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
                email_matches.extend(find_matches(line, email_regex))
            print(f"Found {len(email_matches)} email addresses.")

            # Scan for names
            print("\nScanning for names...")
            name_matches = set()
            for line in tqdm(lines, desc="Progress", unit="lines", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
                # Remove email addresses from the line to avoid false positives
                line = email_regex.sub('', line)

                doc = nlp(line)
                for entity in doc.ents:
                    if entity.label_ == 'PERSON':
                        name_matches.add(entity.text)
            print(f"Found {len(name_matches)} names.")

            # Output results
            print("\nPII Values:")
            for category, matches in [("Phone Numbers", phone_matches), ("Emails", email_matches), ("Names", name_matches)]:
                print(f"\n{category} with PII values:")
                print(f"Count: {len(matches)}")
                for match in matches:
                    print(match)

    except FileNotFoundError:
        print("File not found.")
    except UnicodeDecodeError:
        print("Error decoding file. Ensure the file is in UTF-8 encoding.")

# Example usage
scan_file('pii.log')

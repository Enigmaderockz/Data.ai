import pandas as pd
import re
import os

# Paths
EXCEL_FILE = "tables.xlsx"
FEATURE_FILES = ["abc.feature", "kh.feature", "mn.feature", "sj.feature"]

# Load Excel
df = pd.read_excel(EXCEL_FILE, sheet_name="Main", usecols=["NME_DB", "NME_SCHM", "NME_TBL"])

# Create new example rows
new_rows = [f"      | {row.NME_TBL:<25} | {row.NME_DB:<10} | {row.NME_SCHM:<12} |" for _, row in df.iterrows()]

# Pattern to match Examples blocks with our target header
pattern = re.compile(r'(Examples:\s*\n\s*\|\s*profile_name\s*\|\s*db_name\s*\|\s*schema_name\s*\|\s*\n)(?:\s*\|.*\n)+', re.MULTILINE)

# Function to replace Examples block
def replace_examples_block(match):
    header = match.group(1).rstrip()
    return f"{header}\n" + "\n".join(new_rows)

# Process each feature file
for feature_file in FEATURE_FILES:
    output_file = f"updated_{feature_file}"

    with open(feature_file, "r", encoding="utf-8") as f:
        content = f.read()

    updated_content = re.sub(pattern, replace_examples_block, content)
    updated_content = re.sub(r'(\|\s.*\n)(?=@)', r'\1\n', updated_content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Updated feature file written to {output_file}")

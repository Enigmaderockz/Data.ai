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




from pyspark.sql.functions import col

# Assuming src_df and db_df are your DataFrames with the same schema

# First, find the differences between the two dataframes
diff_df = src_df.subtract(db_df).union(db_df.subtract(src_df))

# If there's no difference, the count will be 0
if diff_df.count() == 0:
    print("No differences found between the DataFrames.")
else:
    # Find columns with differences
    columns = src_df.columns
    diff_cols = []
    
    for col_name in columns:
        src_col = src_df.select(col_name).distinct()
        db_col = db_df.select(col_name).distinct()
        if src_col.subtract(db_col).union(db_col.subtract(src_col)).count() > 0:
            diff_cols.append(col_name)
    
    print(f"Columns with differences: {', '.join(diff_cols)}")
    
    # Now, show the differences for those columns
    if diff_cols:
        src_values = src_df.select(*[col(c) for c in diff_cols]).distinct().collect()
        db_values = db_df.select(*[col(c) for c in diff_cols]).distinct().collect()
        
        print("\nDifferences in values:")
        print(f"{'DataFrames':<10}{', '.join(diff_cols)}")
        print(f"{'src_df':<10}{', '.join(str(row.asDict()) for row in src_values)}")
        print(f"{'db_df':<10}{', '.join(str(row.asDict()) for row in db_values)}")


#############################################3 perplexity AI


from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder.appName("DataFrameComparison").getOrCreate()

# Sample DataFrames (replace these with your actual DataFrames)
src_data = [(1, "val1", "val2"), (2, "val2", "val3")]
db_data = [(1, "val1", "val2"), (2, "val3", "val3")]

src_df = spark.createDataFrame(src_data, ["id", "col1", "col2"])
db_df = spark.createDataFrame(db_data, ["id", "col1", "col2"])

# Identify differences
diff_df = src_df.subtract(db_df).union(db_df.subtract(src_df))

if diff_df.count() == 0:
    print("No differences found.")
else:
    # Identify columns with differences
    diff_columns = []
    
    for column in src_df.columns:
        # Create a temporary DataFrame for each column to check for differences
        temp_diff_df = src_df.select("id", column).join(db_df.select("id", column), on="id", how="outer")
        
        # Check if there are any differences in the current column
        if temp_diff_df.filter(col(f"{column}_left") != col(f"{column}_right")).count() > 0:
            diff_columns.append(column)

    print(f"Columns with differences: {', '.join(diff_columns)}")

    # Show differences between the two DataFrames
    for column in diff_columns:
        print(f"Differences in column '{column}':")
        
        # Create a DataFrame showing the differing values from both DataFrames
        diff_values_df = src_df.select("id", column).join(db_df.select("id", column), on="id", how="outer") \
            .withColumnRenamed(f"{column}_left", f"{column}_src") \
            .withColumnRenamed(f"{column}_right", f"{column}_db") \

            .filter(col(f"{column}_src") != col(f"{column}_db"))

        diff_values_df.show()

























from pyspark.sql.functions import col

# Find common columns between src_df and db_df
common_cols = list(set(src_df.columns) & set(db_df.columns))

# Only proceed with the comparison on common columns
if common_cols:
    # Find the differences between the two dataframes for common columns
    diff_df = src_df.select(*common_cols).subtract(db_df.select(*common_cols)).union(db_df.select(*common_cols).subtract(src_df.select(*common_cols)))

    if diff_df.count() == 0:
        print("No differences found between the DataFrames for common columns.")
    else:
        diff_cols = []
        
        for col_name in common_cols:
            src_col = src_df.select(col_name).distinct()
            db_col = db_df.select(col_name).distinct()
            if src_col.subtract(db_col).union(db_col.subtract(src_col)).count() > 0:
                diff_cols.append(col_name)
        
        if diff_cols:
            print(f"Columns with differences: {', '.join(diff_cols)}")
            
            # Now, show the differences for those columns
            src_values = src_df.select(*[col(c) for c in diff_cols]).distinct().collect()
            db_values = db_df.select(*[col(c) for c in diff_cols]).distinct().collect()
            
            print("\nDifferences in values:")
            print(f"{'DataFrames':<10}{', '.join(diff_cols)}")
            print(f"{'src_df':<10}{', '.join(str(row.asDict()) for row in src_values)}")
            print(f"{'db_df':<10}{', '.join(str(row.asDict()) for row in db_values)}")
        else:
            print("No differences found in common columns.")
else:
    print("No common columns between the DataFrames to compare.")

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


def calculate_percentage_change(old, new, total_old, total_new, metric):
    if metric == "Automation" and total_old > 0 and total_new > 0:
        percentage_old = (old / total_old) * 100
        percentage_new = (new / total_new) * 100
        if percentage_old - percentage_new == 0.0:
            return f"100% {metric} complete"
    
    if total_old == 0 and total_new == 0:
        return f"{metric} remained constant with no change"
    
    percentage_old = (old / total_old) * 100 if total_old != 0 else 0
    percentage_new = (new / total_new) * 100
    change = percentage_new - percentage_old

    return f"{metric} {'increased' if change > 0 else 'decreased' if change < 0 else 'remains constant'} {'by' if change != 0 else 'at'} {abs(change):.2f}%"
        else:
            print("No differences found in common columns.")
else:
    print("No common columns between the DataFrames to compare.")




###################################1

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import statistics

def detect_trends(data):
    # Calculate overall totals
    total_automated = data['AUTOMATED'].sum()
    total_manual = data['MANUAL'].sum()
    total_backlog = data['BACKLOG'].sum()
    total_cases = data['TOTAL'].sum()
    total_percent_automated = round((total_automated / total_cases) * 100, 2) if total_cases > 0 else 0

    # Calculate summary statistics
    summary_stats = {
        'Automated': {
            'Total': total_automated,
            'Average Monthly': round(data['AUTOMATED'].mean(), 2),
            'Median': int(data['AUTOMATED'].median()),
            'Std Dev': round(data['AUTOMATED'].std(), 2)
        },
        'Manual': {
            'Total': total_manual,
            'Average Monthly': round(data['MANUAL'].mean(), 2),
            'Median': int(data['MANUAL'].median()),
            'Std Dev': round(data['MANUAL'].std(), 2)
        },
        'Backlog': {
            'Total': total_backlog,
            'Average Monthly': round(data['BACKLOG'].mean(), 2),
            'Median': int(data['BACKLOG'].median()),
            'Std Dev': round(data['BACKLOG'].std(), 2)
        },
        'Overall': {
            'Total TCs': total_cases,
            'Overall Automated Percentage': f"{total_percent_automated}%"
        }
    }

    # Start constructing HTML
    trends_html = f"""
    <h2>Overall Summary</h2>
    <table border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th>Category</th>
            <th>Total TCs</th>
            <th>Average Monthly</th>
            <th>Median</th>
            <th>Std Dev</th>
        </tr>
        <tr>
            <td>Automated</td>
            <td>{summary_stats['Automated']['Total']}</td>
            <td>{summary_stats['Automated']['Average Monthly']}</td>
            <td>{summary_stats['Automated']['Median']}</td>
            <td>{summary_stats['Automated']['Std Dev']}</td>
        </tr>
        <tr>
            <td>Manual</td>
            <td>{summary_stats['Manual']['Total']}</td>
            <td>{summary_stats['Manual']['Average Monthly']}</td>
            <td>{summary_stats['Manual']['Median']}</td>
            <td>{summary_stats['Manual']['Std Dev']}</td>
        </tr>
        <tr>
            <td>Backlog</td>
            <td>{summary_stats['Backlog']['Total']}</td>
            <td>{summary_stats['Backlog']['Average Monthly']}</td>
            <td>{summary_stats['Backlog']['Median']}</td>
            <td>{summary_stats['Backlog']['Std Dev']}</td>
        </tr>
        <tr>
            <td colspan="5"><strong>Overall Automated Percentage: {summary_stats['Overall']['Overall Automated Percentage']}</strong></td>
        </tr>
    </table>

    <h2>Data Trends</h2>
    <ul style="list-style-type: none; padding: 0;">
    """

    # Function to calculate confidence intervals
    def confidence_interval(x, y, model, confidence=0.95):
        predictions = model.predict(x)
        residuals = y - predictions
        mean_x = np.mean(x)
        n = len(x)
        t_value = 2.306  # Approximate for 95% confidence with df= n-2=6
        s_err = np.sqrt(np.sum(residuals**2) / (n - 2))
        conf_int = t_value * s_err / np.sqrt(np.sum((x - mean_x)**2))
        return conf_int

    # Iterate through each category for trend analysis
    for category in ['Automated', 'Manual', 'Backlog']:
        category_data = data[['MONTH', 'CREATED', category]].copy()
        category_data.rename(columns={category: 'Count'}, inplace=True)
        category_data['Created'] = pd.to_datetime(category_data['CREATED'].str.split(' to ').str[0], dayfirst=True)
        category_data['Month_Num'] = category_data['Created'].dt.year * 12 + category_data['Created'].dt.month
        category_data.sort_values('Month_Num', inplace=True)

        x = category_data['Month_Num'].values.reshape(-1, 1)
        y = category_data['Count'].values

        if len(x) < 2:
            continue  # Not enough data points for trend analysis

        model = LinearRegression().fit(x, y)
        slope = model.coef_[0]
        r_squared = model.score(x, y)
        conf_int = confidence_interval(x, y, model)

        trend = "increasing" if slope > 0 else "decreasing"
        trend_icon = "↑" if slope > 0 else "↓"
        trend_color = "green" if slope > 0 else "red"

        start_count = y[0]
        end_count = y[-1]
        percentage_change = ((end_count - start_count) / start_count) * 100 if start_count != 0 else 0

        # Adding more detailed information
        trends_html += f"""
        <li style='margin-bottom: 10px;'>
            <span style='color: {trend_color}; font-size: 20px;'>{trend_icon}</span>
            <strong>{category}</strong> is <em>{trend}</em> over time with a slope of {slope:.2f}.
            <br>
            <strong>Trend Details:</strong>
            <ul>
                <li>Starting count (earliest month): {start_count}</li>
                <li>Ending count (latest month): {end_count}</li>
                <li>Percentage change: {percentage_change:.2f}%</li>
                <li>R-squared: {r_squared:.2f}</li>
                <li>95% Confidence Interval for Slope: [{slope - conf_int:.2f}, {slope + conf_int:.2f}]</li>
            </ul>
        </li>
        """

    trends_html += "</ul>"

    # Adding Monthly Breakdown Table
    trends_html += """
    <h2>Monthly Breakdown</h2>
    <table border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th>Month</th>
            <th>Automated</th>
            <th>Manual</th>
            <th>Backlog</th>
            <th>Total</th>
            <th>% Automated</th>
        </tr>
    """
    for index, row in data.iterrows():
        trends_html += f"""
        <tr>
            <td>{row['MONTH']}</td>
            <td>{row['AUTOMATED']}</td>
            <td>{row['MANUAL']}</td>
            <td>{row['BACKLOG']}</td>
            <td>{row['TOTAL']}</td>
            <td>{row['% AUTOMATED']}</td>
        </tr>
        """
    trends_html += "</table>"

    return trends_html


###############################33 2

from sklearn.linear_model import LinearRegression

def detect_trends(data):
    total_automated = (data['Category'] == 'Automated').sum()
    total_manual = (data['Category'] == 'Manual').sum()
    total_backlog = (data['Category'] == 'Backlog').sum()
    total_cases = total_automated + total_manual + total_backlog
    total_percent_automated = round((total_automated / total_cases) * 100, 2) if total_cases > 0 else 0

    trends_html = f"""
    <h3>Overall Summary</h3>
    <p>Total TCs: {total_cases}, Total automated TCs: {total_automated}, Total manual TCs: {total_manual}, 
    Total backlog TCs: {total_backlog}, Overall Automated Percentage: {total_percent_automated}%</p>
    <h3>Data Trends</h3>
    <ul class='trends-list'>
    """

    for category in ['Automated', 'Manual', 'Backlog']:
        category_data = data[data['Category'] == category]
        if not category_data.empty:
            category_data = category_data.copy()
            category_data['Count'] = category_data.groupby('Month')['Month'].transform('count')
            category_data['Month_Num'] = category_data['Created'].dt.month + category_data['Created'].dt.year * 12
            category_data = category_data.sort_values('Month_Num')
            x = category_data['Month_Num'].values.reshape(-1, 1)
            y = category_data['Count'].values

            model = LinearRegression().fit(x, y)
            trend = "increasing" if model.coef_[0] > 0 else "decreasing"
            trend_icon = "↑" if trend == "increasing" else "↓"

            # Determine trend color
            if category == 'Automated':
                trend_color = "green" if trend == "increasing" else "red"
            else:
                trend_color = "green" if trend == "decreasing" else "red"

            # Metrics
            start_count = y[0]
            end_count = y[-1]
            percentage_change = ((end_count - start_count) / start_count) * 100 if start_count != 0 else 0
            abs_change = end_count - start_count
            max_count = max(y)
            min_count = min(y)
            avg_count = sum(y) / len(y)

            # Time range
            first_month = category_data['Created'].min().strftime('%B-%Y')
            last_month = category_data['Created'].max().strftime('%B-%Y')

            trends_html += f"""
            <li style='color: {trend_color};'>
            {trend_icon} <b>{category}</b> is {trend} over time.
            <ul>
                <li><b>Slope:</b> {model.coef_[0]:.2f}</li>
                <li><b>Starting Count:</b> {start_count}, <b>Ending Count:</b> {end_count}</li>
                <li><b>Absolute Change:</b> {abs_change}, <b>Percentage Change:</b> {percentage_change:.2f}%</li>
                <li><b>Max Count:</b> {max_count}, <b>Min Count:</b> {min_count}, <b>Average Count:</b> {avg_count:.2f}</li>
                <li><b>Time Range:</b> {first_month} to {last_month}</li>
            </ul>
            </li>
            """

    trends_html += "</ul>"
    return trends_html

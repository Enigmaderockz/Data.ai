import sys
import csv

# Function to fetch the character length of all the columns from a file
def process_csv(input_file_name, output_file_name, delimiter=',', skip_first=False):
    # Open the input CSV file
    with open(input_file_name, 'r') as input_file:
        # Create a CSV reader
        reader = csv.reader(input_file, delimiter=delimiter)
        
        # Skip the first line if needed
        if skip_first:
            next(reader)
        
        # Read the header and the first row
        header = next(reader)
        first_row = next(reader)
        
        # Prepare the data for the output CSV file
        output_data = []
        for i in range(len(header)):
            output_data.append([header[i], len(first_row[i]), first_row[i]])

    # Open the output CSV file
    with open(output_file_name, 'w', newline='') as output_file:
        # Create a CSV writer
        writer = csv.writer(output_file, delimiter=delimiter)
        
        # Write the header
        writer.writerow(['Columns', 'Char length', 'Sample'])
        
        # Write the data
        for row in output_data:
            writer.writerow(row)

# Call the function with your file names and whether to skip the first line
process_csv(sys.argv[1], sys.argv[2], delimiter='|', skip_first=False)

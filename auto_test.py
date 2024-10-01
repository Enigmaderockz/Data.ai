import sys

def process_template(file_path, configs):
    # Read the contents of the file with UTF-8 encoding
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        print(f"Error: Unable to decode the file {file_path}. Please ensure it is encoded in UTF-8.")
        sys.exit(1)
    
    # Separate the feature line (first occurrence) and scenario template (remaining content)
    feature_line = None
    scenario_template = content
    
    if 'Feature:' in content:
        # Extract the feature line
        feature_line, scenario_template = content.split('Feature:', 1)
        feature_line = 'Feature:' + scenario_template.splitlines()[0]  # Re-attach "Feature:"
        scenario_template = '\n'.join(scenario_template.splitlines()[1:])  # Remainder is the scenario

    # Iterate through each config to create a corresponding scenario
    scenarios = []
    for config in configs:
        # Replace {} placeholders with the current config
        scenario = scenario_template.replace('{}', config)
        # Add the @tag annotation with the config
        scenario = scenario.replace('@{}', f'@{config}')
        scenarios.append(scenario)

    # Output the final generated content
    final_output = feature_line + '\n\n' + '\n\n'.join(scenarios)
    return final_output

def main():
    # Get command-line arguments
    if len(sys.argv) < 4:
        print("Usage: python auto_test.py <file> <configs> <config_values_comma_separated>")
        sys.exit(1)

    file_path = sys.argv[1]
    configs = sys.argv[3].split(', ')

    # Process the template and generate test cases
    result = process_template(file_path, configs)
    
    # Write the output to 'Test.feature' file
    output_file = "Test.feature"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Output has been written to {output_file}")

if __name__ == "__main__":
    main()


python gen.py temp.txt configs "ETRTMACCTSUM, ETRTM"
python gen.py temp.txt configs ETRTMACCTSUM




Feature: ET Margin data load

@ingestion @e2e @{}
Scenario Outline: GBTDRMFLEET-39287_{}_loading_Source_file_to_fact
        Given config file <conf> for product "ETMARGIN" and TestCaseId <id>
        Given able to run copy file JCL "mswmcopyDaily" <conf>
        Given able to run JCL for Fact load "mswmdataCheckExecute" <conf>
        Then data between source file with header trailer and Fact table should match for config "{}" with transformation "N"
        Examples:
        | conf ❘ id |
        ❘ {}.cfg | {}_stage_load |

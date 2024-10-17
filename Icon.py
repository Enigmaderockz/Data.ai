DD
today_date = datetime.today().strftime('%Y-%m-%d')

# Define the filename with today's date
filename = f"result_{today_date}.json"

import json
import requests
import argparse
from requests_kerberos import HTTPKerberosAuth, OPTIONAL, DISABLED

# Set up argument parsing
parser = argparse.ArgumentParser(description="Fetch data from API with Kerberos authentication")
parser.add_argument("fleet", type=str, help="The fleet parameter for the API")
parser.add_argument("start_created_date", type=str, help="The start created date (format: YYYY-MM-DD)")
parser.add_argument("end_created_date", type=str, help="The end created date (format: YYYY-MM-DD)")

# Parse the arguments
args = parser.parse_args()

# Define the API endpoint with parsed arguments
domain = "http://oneqretest.ms.com/"
get_url = f"{domain}api/Jira/jira_issue_tracking_batch?fleet={args.fleet}&start_created_date={args.start_created_date}&end_created_date={args.end_created_date}"

# Function to perform a GET request with Kerberos authentication
def get_call(url):
    try:
        with requests.Session() as session:
            response = session.get(url, verify=False, auth=HTTPKerberosAuth(force_preemptive=True, mutual_authentication=OPTIONAL))
            response.raise_for_status()
            data = response.json()

            with open("response_data.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
            print("Response has been successfully written to response_data.json")
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error occurred: {json_err}")
    except IOError as io_err:
        print(f"File I/O error occurred: {io_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

# Call the function with the specified URL
get_call(get_url)




import json
import requests

try:
    # Example: API request to get the response
    response = requests.get("https://api.example.com/endpoint")
    response.raise_for_status()  # Raises an HTTPError for bad responses

    # Parse the response text into JSON format
    data = response.json()

    # Write the JSON data to a file
    with open("response_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("Response has been successfully written to response_data.json")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
except json.JSONDecodeError as json_err:
    print(f"JSON decoding error occurred: {json_err}")
except IOError as io_err:
    print(f"File I/O error occurred: {io_err}")
except Exception as err:
    print(f"An unexpected error occurred: {err}")




def generate_html_report(data, table1_html, table2_html, file1_name="File 1", file2_name="File 2", table_border_color="#4a90e2", table_font_family="Arial"):
    html_content = f"""
    <html>
    <head>
        <title>Comparison Report</title>
        <style>
            body {{ 
                font-family: 'Aptos Display', sans-serif;
                background-color: #333;
                color: #eee;
                padding: 20px;
                line-height: 1.6;
                transition: background-color 0.3s, color 0.3s;
            }}
            h1 {{
                text-align: center;
                font-size: 36px;
                margin-bottom: 20px;
                background: linear-gradient(to right, #ff7e5f, #feb47b);
                -webkit-background-clip: text;
                color: transparent;
                display: inline-block;
            }}
            h2 {{
                font-size: 24px;
                cursor: pointer;
                margin: 10px 0;
                background: linear-gradient(to right, #6a11cb, #2575fc);
                -webkit-background-clip: text;
                color: transparent;
                display: flex;
                align-items: center;
            }}
            .arrow {{
                margin-left: 10px;
                transition: transform 0.3s ease;
            }}
            .section-content {{
                display: none;
                padding-left: 20px;
            }}
            ul {{
                list-style-type: disc;
                padding-left: 40px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                font-family: {table_font_family};
            }}
            th, td {{
                border: 1px solid {table_border_color};
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: {table_border_color};
                color: white;
            }}
            td {{
                background-color: #444;
            }}
            .toggle-switch {{
                position: fixed;
                top: 10px;
                right: 10px;
                display: flex;
                align-items: center;
            }}
            .toggle-switch input[type="checkbox"] {{
                display: none;
            }}
            .toggle-switch-label {{
                width: 50px;
                height: 26px;
                background-color: #4CAF50;
                border-radius: 13px;
                cursor: pointer;
                position: relative;
                transition: background-color 0.3s;
            }}
            .toggle-switch-label::after {{
                content: '';
                width: 20px;
                height: 20px;
                background-color: white;
                border-radius: 50%;
                position: absolute;
                top: 3px;
                left: 4px;
                transition: transform 0.3s;
            }}
            .toggle-switch input[type="checkbox"]:checked + .toggle-switch-label {{
                background-color: #ccc;
            }}
            .toggle-switch input[type="checkbox"]:checked + .toggle-switch-label::after {{
                transform: translateX(24px);
            }}
        </style>
        <script>
            function toggleSection(id, iconId) {{
                var section = document.getElementById(id);
                var icon = document.getElementById(iconId);
                var isHidden = section.style.display === 'none';
                
                // Toggle the section display
                section.style.display = isHidden ? 'block' : 'none';
                
                // Rotate the icon based on section visibility
                icon.style.transform = isHidden ? 'rotate(90deg)' : 'rotate(0deg)';
            }}
            function toggleTheme() {{
                var body = document.body;
                body.style.backgroundColor = body.style.backgroundColor === 'rgb(51, 51, 51)' ? '#f4f4f9' : '#333';
                body.style.color = body.style.color === 'rgb(51, 51, 51)' ? '#333' : '#eee';
            }}
        </script>
    </head>
    <body>
        <div class="toggle-switch">
            <input type="checkbox" id="themeToggle" onclick="toggleTheme()">
            <label for="themeToggle" class="toggle-switch-label"></label>
        </div>

        <h1>Comparison Report</h1>

        <h2 onclick="toggleSection('table1', 'icon1')">Data from {file1_name} <span id="icon1" class="arrow">▶</span></h2>
        <div id="table1" class="section-content" style="display: block;">
            {table1_html}
        </div>

        <h2 onclick="toggleSection('table2', 'icon2')">Data from {file2_name} <span id="icon2" class="arrow">▶</span></h2>
        <div id="table2" class="section-content" style="display: block;">
            {table2_html}
        </div>
    """

    # Section ids and titles
    section_ids = ['comparison_summary', 'max_numbers', 'min_numbers', 'focus_points', 'total_test_cases', 'automation_percentage']
    section_titles = [
        'Comparison Summary', 
        'By MAX of numbers', 
        'By MINIMUM of numbers', 
        'Points to be focused', 
        'Entities sorted by total test cases and their automation percentages', 
        'Entities sorted by automation percentage based on total test cases'
    ]

    for i, title in enumerate(section_titles):
        icon_id = f"icon{i+3}"  # Start icon ID from icon3 to avoid conflicts
        default_display = 'block' if i == 0 else 'none'
        icon_rotation = 'rotate(90deg)' if i == 0 else 'rotate(0deg)'
        html_content += f"<h2 onclick=\"toggleSection('{section_ids[i]}', '{icon_id}')\">{title} <span id=\"{icon_id}\" class=\"arrow\" style=\"transform: {icon_rotation};\">▶</span></h2>"
        html_content += f"<div id='{section_ids[i]}' class='section-content' style='display: {default_display};'>"
        html_content += "<ul>"
        for line in data[title].split("<br>"):
            if line.strip():
                html_content += f"<li>{line.strip()}</li>"
        html_content += "</ul>"
        html_content += "</div>"

    html_content += """
    </body>
    </html>
    """

    # Save the HTML to a file with UTF-8 encoding
    with open('comparison_report.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    print("HTML report with expandable headings, icons, and theme toggle has been generated.")

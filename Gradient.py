<!DOCTYPE html>
<html>
<head>
    <style>
        /* General styles */
        body {
            font-family: Calibri, Arial, sans-serif; /* Fallback to Arial if Calibri is unavailable */
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }
        p, ul, li, h2, h3 {
            font-family: Calibri, Arial, sans-serif;
            line-height: 1.5;
            margin-left: 20px;
        }
        h2 {
            color: #4A766E;
        }
        h3 {
            color: #536493;
        }
        ul {
            list-style-type: disc;
            margin-left: 40px;
        }

        /* Table styles */
        table {
            width: 65%;
            border: 1px solid #ddd;
            margin-bottom: 20px;
            margin-left: 20px;
            font-size: 12px; /* Reduced font size for compactness */
            line-height: 1.2;
            font-family: Calibri, Arial, sans-serif; /* Ensure Calibri is used in tables */
        }
        th {
            background-color: #2C5F8A; /* Deep blue for headers */
            color: white;
            font-weight: bold;
            border: 1px solid #ddd;
            text-align: center;
            vertical-align: middle;
            padding: 4px 8px; /* Slightly increased padding for readability */
            font-family: Calibri, Arial, sans-serif; /* Ensure Calibri is used in headers */
        }
        td {
            border: 1px solid #ddd;
            text-align: center;
            vertical-align: middle;
            padding: 4px 8px; /* Consistent padding */
            font-size: 12px;
            font-family: Calibri, Arial, sans-serif; /* Ensure Calibri is used in cells */
        }
        .even-row {
            background-color: #F9F9F9; /* Light gray for even rows */
        }
        .odd-row {
            background-color: #FFFFFF; /* White for odd rows */
        }
    </style>
</head>
<body>
<p>Hello team,</p>
<p>Please review the release compliance report & fix any discrepancies if required.</p>
<p>Base JQL used: {jql}</p>
<h2>Summary</h2>
<ul>
    <li>Total Issues: {len(issues)}</li>
    <li>Squads with No QA required stories: {squads_without_qa_str}</li>
    <li>Squads with No Functional Test plan: {squads_without_functional_test_plans_str}</li>
    <li>Squads with No Regression Test plan: {squads_without_regression_test_plans_str}</li>
</ul>
<h3>User Stories</h3>
<p>Total User Stories: {user_stories_count}</p>
"""
# Add first table with alternate row colors
if component_story_counts:
    body += """<table cellpadding="0" cellspacing="0">
    <tr>
        <th style="background-color: #2C5F8A; color: white; font-weight: bold; border: 1px solid #ddd; padding: 4px 8px; font-family: Calibri, Arial, sans-serif;">Squad</th>
        <th style="background-color: #2C5F8A; color: white; font-weight: bold; border: 1px solid #ddd; padding: 4px 8px; font-family: Calibri, Arial, sans-serif;">User Story Count</th>
    </tr>"""
    for i, (component, count) in enumerate(component_story_counts.items()):
        row_class = "even-row" if i % 2 == 0 else "odd-row"
        body += f"""<tr style="background-color: {'#F9F9F9' if row_class == 'even-row' else '#FFFFFF'};">
            <td style="border: 1px solid #ddd; padding: 4px 8px; font-size: 12px; font-family: Calibri, Arial, sans-serif;">{component}</td>
            <td style="border: 1px solid #ddd; padding: 4px 8px; font-size: 12px; font-family: Calibri, Arial, sans-serif;">{count}</td>
        </tr>"""
    body += "</table><br><br>"
# Add second table with alternate row colors
body += f"<p>QA Required User Stories: {qa_required_count}</p>"
if component_qa_counts:
    body += """<table cellpadding="0" cellspacing="0">
    <tr>
        <th style="background-color: #2C5F8A; color: white; font-weight: bold; border: 1px solid #ddd; padding: 4px 8px; font-family: Calibri, Arial, sans-serif;">Squad</th>
        <th style="background-color: #2C5F8A; color: white; font-weight: bold; border: 1px solid #ddd; padding: 4px 8px; font-family: Calibri, Arial, sans-serif;">QA Scope Count</th>
    </tr>"""
    for i, (component, count) in enumerate(component_qa_counts.items()):
        row_class = "even-row" if i % 2 == 0 else "odd-row"
        body += f"""<tr style="background-color: {'#F9F9F9' if row_class == 'even-row' else '#FFFFFF'};">
            <td style="border: 1px solid #ddd; padding: 4px 8px; font-size: 12px; font-family: Calibri, Arial, sans-serif;">{component}</td>
            <td style="border: 1px solid #ddd; padding: 4px 8px; font-size: 12px; font-family: Calibri, Arial, sans-serif;">{count}</td>
        </tr>"""
    body += "</table><br><br>"
# Closing HTML
body += "</body></html>"

body = f"""
<html>
<head>
    <style>
        table {{
            border-collapse: collapse;
            width: 60%;
            margin-bottom: 20px;
            margin-left: 20px;
        }}
        th, td {{
            border: 1px solid #536493;
            text-align: center;
            vertical-align: middle;
        }}
        th {{
            background-color: #88C273;
            color: white;
        }}
    </style>
</head>
<body>
<p>Hello team,</p>
<p>Please review the release compliance report & fix any discrepancies if required.</p>
<p>Base JQL used: {jql}</p>
<h2>Summary</h2>
<li>Total Issues: {len(issues)}</li>
<li>Squads with No QA required stories: {squads_without_qa_str}</li>
<li>Squads with No Functional Test plan: {squads_without_functional_test_plans_str}</li>
<li>Squads with No Regression Test plan: {squads_without_regression_test_plans_str}</li>
<h3>User Stories</h3>
<p>Total User Stories: {user_stories_count}</p>
"""

# Add first table with compact cells
if component_story_counts:
    body += """<table cellspacing="0" cellpadding="0" style="border-collapse: collapse; width: 60%; margin-left: 20px;">
    <tr style="background-color: #88C273; color: white; font-size: 12px; height: 25px;">
        <th style="padding: 2px;">Squad</th>
        <th style="padding: 2px;">User Story Count</th>
    </tr>"""
    for i, (component, count) in enumerate(component_story_counts.items()):
        row_color = "#F2F2F2" if i % 2 == 0 else "#FFFFFF"
        body += f"""<tr style="background-color: {row_color}; font-size: 12px; height: 20px;">
            <td style="padding: 2px;">{component}</td>
            <td style="padding: 2px;">{count}</td>
        </tr>"""
    body += "</table><br><br>"

# Add second table with compact cells
body += f"<p>QA Required User Stories: {qa_required_count}</p>"
if component_qa_counts:
    body += """<table cellspacing="0" cellpadding="0" style="border-collapse: collapse; width: 60%; margin-left: 20px;">
    <tr style="background-color: #88C273; color: white; font-size: 12px; height: 25px;">
        <th style="padding: 2px;">Squad</th>
        <th style="padding: 2px;">QA Scope Count</th>
    </tr>"""
    for i, (component, count) in enumerate(component_qa_counts.items()):
        row_color = "#F2F2F2" if i % 2 == 0 else "#FFFFFF"
        body += f"""<tr style="background-color: {row_color}; font-size: 12px; height: 20px;">
            <td style="padding: 2px;">{component}</td>
            <td style="padding: 2px;">{count}</td>
        </tr>"""
    body += "</table><br><br>"

# Closing HTML
body += "</body></html>"

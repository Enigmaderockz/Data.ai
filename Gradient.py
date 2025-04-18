def table_design():
    table_styles = """
    <style>
    table {
        border-collapse: separate;
        border-spacing: 0;
        width: 65%;
        margin: 10px auto;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 9pt;
        background: #fff;
        box-shadow: 0 2px 8px rgba(80, 80, 120, 0.07);
        border-radius: 8px;
        overflow: hidden;
    }
    th, td {
        border: 1px solid #e0e0e0;
        padding: 4px 8px; /* Compact padding */
        line-height: 1.25;
        text-align: center;
    }
    th {
        background: linear-gradient(90deg, #5864A6 0%, #7B8BD1 100%);
        color: #fff;
        font-weight: 600;
        font-size: 9.5pt;
        border-bottom: 2px solid #48508a;
        letter-spacing: 0.02em;
    }
    tr:nth-child(even) td {
        background: #f7f9fc;
    }
    tr:nth-child(odd) td {
        background: #eef1f7;
    }
    tr:hover td {
        background: #e3eaff !important;
        transition: background 0.2s;
    }
    td:first-child {
        text-align: left;
        font-weight: 500;
    }
    h2 {
        text-align: left;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
        margin: 18px 0 6px 0;
        color: #3d4777;
        letter-spacing: 0.01em;
    }
    </style>
    """
    overall_summary_html = table_styles
    for month_name_str, summaries in grouped_summaries.items():
        overall_summary_html += f"""
        <h2>Overall Summary - {month_name_str} Releases</h2>
        <table>
            <thead>
                <tr>
                    <th>Release Date</th>
                    <th>Total Stories</th>
                    <th>Total QA Stories</th>
                    <th>Stories Completed</th>
                    <th>Requirement Gaps</th>
                    <th>Total # of Test Cases</th>
                    <th>Total # of Defects</th>
                    <th>New Automation Count</th>
                    <th>In Scope QA%</th>
                </tr>
            </thead>
            <tbody>
        """
        for summary in summaries:
            overall_summary_html += f"""
                <tr>
                    <td>{summary['fix_version']}</td>
                    <td>{summary['user_stories_count']}</td>
                    <td>{summary['qa_required_count']}</td>
                    <td>{summary['stories_completed']}</td>
                    <td>{summary['requirement_gaps']}</td>
                    <td>{summary['total_test_cases']}</td>
                    <td>{summary['total_defects']}</td>
                    <td>{summary['new_automation_count']}</td>
                    <td>{summary['in_scope_qa_percentage']:.2f}%</td>
                </tr>
        """
        overall_summary_html += "</tbody></table>"
    return overall_summary_html

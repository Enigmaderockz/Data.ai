def table_design():
    # Inline styles for email compatibility
    table_header_bg = "#5864A6"
    table_header_color = "#fff"
    row_even_bg = "#f7f9fc"
    row_odd_bg = "#eef1f7"
    cell_padding = "3px 6px"
    font_family = "'Segoe UI', Arial, sans-serif"
    font_size = "9pt"
    border_color = "#e0e0e0"

    overall_summary_html = ""
    for month_name_str, summaries in grouped_summaries.items():
        overall_summary_html += f"""
        <h2 style="text-align:left; font-family:{font_family}; font-size:10pt; color:#3d4777; margin:18px 0 6px 0;">
            Overall Summary - {month_name_str} Releases
        </h2>
        <table style="border-collapse:collapse; width:65%; margin:10px auto; font-family:{font_family}; font-size:{font_size}; background:#fff;">
            <tr>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Release Date</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Total Stories</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Total QA Stories</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Stories Completed</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Requirement Gaps</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Total # of Test Cases</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">Total # of Defects</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">New Automation Count</th>
                <th style="background:{table_header_bg}; color:{table_header_color}; font-weight:600; padding:{cell_padding}; border:1px solid {border_color};">In Scope QA%</th>
            </tr>
        """
        for i, summary in enumerate(summaries):
            row_bg = row_even_bg if i % 2 == 0 else row_odd_bg
            overall_summary_html += f"""
            <tr>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg}; text-align:left;">{summary['fix_version']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['user_stories_count']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['qa_required_count']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['stories_completed']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['requirement_gaps']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['total_test_cases']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['total_defects']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['new_automation_count']}</td>
                <td style="padding:{cell_padding}; border:1px solid {border_color}; background:{row_bg};">{summary['in_scope_qa_percentage']:.2f}%</td>
            </tr>
            """
        overall_summary_html += "</table>"
    return overall_summary_html

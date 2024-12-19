def generate_predictions_with_tabs(df):
    predictions_html = """
    <style>
        body {
            font-family: Microsoft JhengHei UI, sans-serif;
            margin: 20px;
        }
        .tabs {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 20px;
            cursor: pointer;
        }
        .tab {
            padding: 10px 20px;
            margin-right: 5px;
            background-color: #f1f1f1;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .tab.active {
            background-color: #0078D4;
            color: white;
        }
        .tab-content {
            display: none;
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .tab-content.active {
            display: block;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table th, table td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        table th {
            background-color: #0078D4;
            color: white;
        }
        .highlight-green {
            color: #6EC207; /* Green */
            font-weight: bold;
        }
        .highlight-red {
            color: red;
            font-weight: bold;
        }
        .highlight-orange {
            color: orange;
            font-weight: bold;
        }
        .no-data {
            text-align: center;
            font-style: italic;
        }
    </style>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tabs = document.querySelectorAll('.tab');
            const tabContents = document.querySelectorAll('.tab-content');

            tabs.forEach((tab, index) => {
                tab.addEventListener('click', () => {
                    tabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(tc => tc.classList.remove('active'));

                    tab.classList.add('active');
                    tabContents[index].classList.add('active');
                });
            });

            // Activate the first tab by default
            tabs[0].classList.add('active');
            tabContents[0].classList.add('active');
        });
    </script>

    <div class="tabs">
        <div class="tab">Squads with 0 Backlog</div>
        <div class="tab">Squads to be Focused On</div>
        <div class="tab">Squads Tend to Complete Soon</div>
        <div class="tab">Squads to Review</div>
    </div>

    <div class="tab-content">
        <h3>Squads with 0 Backlog</h3>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Project</th>
                    <th>Automated</th>
                    <th>Manual</th>
                </tr>
            </thead>
            <tbody>
    """
    # "Squads with 0 Backlog" section
    for month, month_group in df.groupby('Month'):
        squad_stats = month_group.groupby(['Project', 'Components']).agg(
            Automated=('Category', lambda x: (x == 'Automated').sum()),
            Manual=('Category', lambda x: (x == 'Manual').sum()),
        ).reset_index()
        completed_automation_squads = squad_stats[squad_stats['Automated'] > 0]

        if not completed_automation_squads.empty:
            for _, row in completed_automation_squads.iterrows():
                predictions_html += f"""
                <tr>
                    <td>{row['Components']}</td>
                    <td>{row['Project']}</td>
                    <td class="highlight-green">{row['Automated']}</td>
                    <td>{row['Manual']}</td>
                </tr>
                """
        else:
            predictions_html += "<tr><td colspan='4' class='no-data'>No squads with 0 backlog</td></tr>"

    predictions_html += """
            </tbody>
        </table>
    </div>

    <div class="tab-content">
        <h3>Squads to be Focused On</h3>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Project</th>
                    <th>Backlog</th>
                    <th>Automated</th>
                </tr>
            </thead>
            <tbody>
    """

    # "Squads to be Focused On" section
    focus_squads = squad_stats[squad_stats['Automated'] == 0]
    if not focus_squads.empty:
        for _, row in focus_squads.iterrows():
            predictions_html += f"""
            <tr>
                <td>{row['Components']}</td>
                <td>{row['Project']}</td>
                <td class="highlight-red">{row['Backlog']}</td>
                <td>{row['Automated']}</td>
            </tr>
            """
    else:
        predictions_html += "<tr><td colspan='4' class='no-data'>No squads to focus on</td></tr>"

    predictions_html += """
            </tbody>
        </table>
    </div>

    <div class="tab-content">
        <h3>Squads Tend to Complete Soon</h3>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Project</th>
                    <th>Backlog</th>
                    <th>Automated</th>
                </tr>
            </thead>
            <tbody>
    """

    # "Squads Tend to Complete Soon" section
    complete_soon_squads = squad_stats[squad_stats['Backlog'] - squad_stats['Automated'] <= 20]
    if not complete_soon_squads.empty:
        for _, row in complete_soon_squads.iterrows():
            predictions_html += f"""
            <tr>
                <td>{row['Components']}</td>
                <td>{row['Project']}</td>
                <td class="highlight-orange">{row['Backlog']}</td>
                <td>{row['Automated']}</td>
            </tr>
            """
    else:
        predictions_html += "<tr><td colspan='4' class='no-data'>No squads tend to complete soon</td></tr>"

    predictions_html += """
            </tbody>
        </table>
    </div>

    <div class="tab-content">
        <h3>Squads to Review</h3>
        <p>No squads fall into this prediction</p>
    </div>
    """
    return predictions_html





def generate_predictions(df):
    predictions_html = """
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .section {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        .section-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .sub-section-title {
            font-size: 1em;
            font-weight: bold;
            margin: 10px 0;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 5px 0;
            font-size: 0.9em;
            line-height: 1.5;
        }
        .green {
            color: #28a745;
            font-weight: bold;
        }
        .red {
            color: #dc3545;
            font-weight: bold;
        }
        .orange {
            color: #fd7e14;
            font-weight: bold;
        }
        .neutral {
            color: #6c757d;
        }
    </style>
    """

    for month, month_group in df.groupby('Month'):
        month_name = month_group['Created'].dt.strftime('%B-%Y').iloc[0]
        squad_stats = month_group.groupby(['Project', 'Components']).agg(
            Automated=('Category', lambda x: (x == 'Automated').sum()),
            Manual=('Category', lambda x: (x == 'Manual').sum()),
            Backlog=('Category', lambda x: (x == 'Backlog').sum()),
            Total=('Category', 'size')
        ).reset_index()

        squad_stats['Backlog_Difference'] = squad_stats['Total'] - squad_stats['Backlog']
        completed_automation_squads = squad_stats[(squad_stats['Backlog'] == 0) & (squad_stats['Automated'] > 0)]
        focus_squads = squad_stats[
            ((squad_stats['Automated'] == 0) & (squad_stats['Backlog'] > 0) & (squad_stats['Backlog'] - squad_stats['Automated'] >= 20)) |
            ((squad_stats['Backlog'] != 0) & (abs(squad_stats['Automated'] - squad_stats['Backlog']) >= 20))
        ]
        complete_soon_squads = squad_stats[
            (squad_stats['Backlog'] != 0) & (abs(squad_stats['Automated'] - squad_stats['Backlog']) <= 20)
        ]
        no_backlog_no_automation_squads = squad_stats[(squad_stats['Backlog'] == 0) & (squad_stats['Automated'] == 0)]

        predictions_html += f"""
        <div class='section'>
            <div class='section-title'>{month_name}</div>

            <div class='sub-section'>
                <div class='sub-section-title'>Squads with 0 Backlog:</div>
                <ul>
        """
        if completed_automation_squads.empty:
            predictions_html += "<li class='neutral'>No squad falls into this prediction</li>"
        else:
            for idx, row in completed_automation_squads.iterrows():
                predictions_html += (
                    f"<li><b>{row['Components']} ({row['Project']})</b> - "
                    f"<span class='green'>{row['Automated']}</span> TCs are automated along with {row['Manual']} Manual TCs</li>"
                )
        predictions_html += "</ul></div>"

        predictions_html += """
            <div class='sub-section'>
                <div class='sub-section-title'>Squads to be focused on:</div>
                <ul>
        """
        if focus_squads.empty:
            predictions_html += "<li class='neutral'>No squad falls into this prediction</li>"
        else:
            for idx, row in focus_squads.iterrows():
                yet_to_be_automated = row['Backlog'] - row['Automated']
                predictions_html += (
                    f"<li><b>{row['Components']} ({row['Project']})</b> - "
                    f"<span class='red'>{yet_to_be_automated}</span> TCs are yet to be automated based on Automated/Backlog: "
                    f"{row['Automated']}/{row['Backlog']}</li>"
                )
        predictions_html += "</ul></div>"

        predictions_html += """
            <div class='sub-section'>
                <div class='sub-section-title'>Squads tend to complete automation soon:</div>
                <ul>
        """
        if complete_soon_squads.empty:
            predictions_html += "<li class='neutral'>No squad falls into this prediction</li>"
        else:
            for idx, row in complete_soon_squads.iterrows():
                yet_to_be_automated = row['Backlog'] - row['Automated']
                predictions_html += (
                    f"<li><b>{row['Components']} ({row['Project']})</b> - "
                    f"<span class='orange'>{yet_to_be_automated}</span> TCs can be automated based on Automated/Backlog: "
                    f"{row['Automated']}/{row['Backlog']}</li>"
                )
        predictions_html += "</ul></div>"

        predictions_html += """
            <div class='sub-section'>
                <div class='sub-section-title'>Squads to review:</div>
                <ul>
        """
        if no_backlog_no_automation_squads.empty:
            predictions_html += "<li class='neutral'>No squad falls into this prediction</li>"
        else:
            for idx, row in no_backlog_no_automation_squads.iterrows():
                predictions_html += (
                    f"<li><b>{row['Components']} ({row['Project']})</b> has "
                    f"{row['Automated']} Automated TCs & {row['Backlog']} Backlog TCs with only "
                    f"{row['Manual']} Manual TCs. Please review.</li>"
                )
        predictions_html += "</ul></div></div>"

    return predictions_html


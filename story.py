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

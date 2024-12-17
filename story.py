def detect_trends(data):
    # Summarize Overall TCs
    total_automated = (data['Category'] == 'Automated').sum()
    total_manual = (data['Category'] == 'Manual').sum()
    total_backlog = (data['Category'] == 'Backlog').sum()
    total_cases = total_automated + total_manual + total_backlog
    total_percent_automated = round((total_automated / total_cases) * 100, 2) if total_cases > 0 else 0

    # Create HTML structure
    trends_html = f"""
    <div style='font-family: Arial, sans-serif; color: #333;'>
        <h2 style='color: #004085;'>📊 Overall Test Case Summary</h2>
        <p style='font-size: 14px;'>
            <b>Total Test Cases:</b> {total_cases} <br>
            <b>Automated Test Cases:</b> {total_automated} <br>
            <b>Manual Test Cases:</b> {total_manual} <br>
            <b>Backlog Test Cases:</b> {total_backlog} <br>
            <b>Overall Automation Percentage:</b> {total_percent_automated}% 
        </p>
        <hr style='border: 1px solid #ccc;'>
        <h3 style='color: #004085;'>📈 Trend Analysis by Category</h3>
        <ul style='list-style-type: square; font-size: 14px;'>
    """

    # Helper Function: Fill Missing Months
    def fill_missing_months(df):
        df['YearMonth'] = df['Created'].dt.to_period('M').dt.to_timestamp()
        grouped = df.groupby('YearMonth').size().reset_index(name='Count')
        full_range = pd.date_range(grouped['YearMonth'].min(), grouped['YearMonth'].max(), freq='MS')
        full_df = pd.DataFrame({'YearMonth': full_range})
        merged = full_df.merge(grouped, on='YearMonth', how='left').fillna(0)
        merged['Count'] = merged['Count'].astype(int)
        return merged

    # Analyze trends per category
    for category in ['Automated', 'Manual', 'Backlog']:
        category_data = data[data['Category'] == category]
        if not category_data.empty:
            filled_data = fill_missing_months(category_data)

            # Prepare data for trend analysis
            filled_data['Month_Num'] = filled_data['YearMonth'].dt.month + filled_data['YearMonth'].dt.year * 12
            x = filled_data['Month_Num'].values.reshape(-1, 1)
            y = filled_data['Count'].values

            # Linear regression model
            model = LinearRegression().fit(x, y)
            slope = model.coef_[0]
            start_count = y[0]
            end_count = y[-1]
            abs_change = end_count - start_count
            percentage_change = ((end_count - start_count) / start_count) * 100 if start_count != 0 else 0

            # Trend direction and color
            if start_count < end_count:
                trend_direction = "Increasing 📈"
                trend_color = "#28a745"
            elif start_count > end_count:
                trend_direction = "Decreasing 📉"
                trend_color = "#dc3545"
            else:
                trend_direction = "Stable ➡️"
                trend_color = "#6c757d"

            # Add detailed category trends
            trends_html += f"""
            <li>
                <h4 style='color: {trend_color};'>{category} Trend: {trend_direction}</h4>
                <p>
                    <b>Starting Count:</b> {start_count} <br>
                    <b>Ending Count:</b> {end_count} <br>
                    <b>Absolute Change:</b> {abs_change} <br>
                    <b>Percentage Change:</b> {percentage_change:.2f}% <br>
                    <b>Slope of Trend:</b> {slope:.2f}
                </p>
            </li>
            """

            # Detect significant changes (jumps/drops)
            trends_html += f"""
            <h5 style='color: #004085; margin-top: 10px;'>🔍 Significant Changes in {category}</h5>
            <ul style='margin-left: 20px;'>
            """
            filled_data['Prev_Count'] = filled_data['Count'].shift(1)
            filled_data['Change'] = filled_data['Count'] - filled_data['Prev_Count']
            filled_data['Percent_Change'] = filled_data['Change'] / filled_data['Prev_Count'].replace(0, np.nan) * 100

            for _, row in filled_data.dropna().iterrows():
                if abs(row['Percent_Change']) > 20:  # Only show significant changes > 20%
                    month = row['YearMonth'].strftime('%B-%Y')
                    prev_count = int(row['Prev_Count'])
                    current_count = int(row['Count'])
                    change = row['Change']
                    percent_change = row['Percent_Change']

                    # Trend message
                    if change > 0:
                        direction = "jumped ⬆️"
                        color = "#28a745"
                    else:
                        direction = "dropped ⬇️"
                        color = "#dc3545"

                    trends_html += f"""
                    <li style='color: {color};'>
                        In <b>{month}</b>, the count {direction} from <b>{prev_count}</b> to <b>{current_count}</b>, 
                        leading to a change of <b>{change} ({percent_change:.2f}%)</b>.
                    </li>
                    """

            trends_html += "</ul>"

    trends_html += "</ul></div>"
    return trends_html

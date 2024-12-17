import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def detect_trends(data):
    total_automated = (data['Category'] == 'Automated').sum()
    total_manual = (data['Category'] == 'Manual').sum()
    total_backlog = (data['Category'] == 'Backlog').sum()
    total_cases = total_automated + total_manual + total_backlog
    total_percent_automated = round((total_automated / total_cases) * 100, 2) if total_cases > 0 else 0

    trends_html = f"""
    <h3>Overall Summary</h3>
    <p>Total TCs: {total_cases}, Total automated TCs: {total_automated}, Total manual TCs: {total_manual}, 
    Total backlog TCs: {total_backlog}, Overall Automated Percentage: {total_percent_automated}%</p>
    <h3>Data Trends</h3>
    <ul class='trends-list'>
    """

    # Helper function to fill missing months
    def fill_missing_months(df):
        df['Created'] = pd.to_datetime(df['Created'])
        df = df.set_index('Created')

        # Generate continuous month range
        all_months = pd.date_range(df.index.min(), df.index.max(), freq='MS')
        df_resampled = df.resample('MS').size().reindex(all_months, fill_value=0)

        # Return filled DataFrame
        df_filled = pd.DataFrame({
            'Created': df_resampled.index,
            'Count': df_resampled.values
        })
        return df_filled

    for category in ['Automated', 'Manual', 'Backlog']:
        category_data = data[data['Category'] == category]
        if not category_data.empty:
            # Fill missing months
            filled_data = fill_missing_months(category_data)
            filled_data['Month_Num'] = filled_data['Created'].dt.month + filled_data['Created'].dt.year * 12

            # Linear regression
            x = filled_data['Month_Num'].values.reshape(-1, 1)
            y = filled_data['Count'].values

            model = LinearRegression().fit(x, y)
            slope = model.coef_[0]
            start_count = y[0]
            end_count = y[-1]
            abs_change = end_count - start_count
            percentage_change = ((end_count - start_count) / start_count) * 100 if start_count != 0 else 0
            max_count = max(y)
            min_count = min(y)
            avg_count = np.mean(y)

            # Time range
            first_month = filled_data['Created'].min().strftime('%B-%Y')
            last_month = filled_data['Created'].max().strftime('%B-%Y')

            # Determine trend direction and color
            if start_count < end_count:
                trend = "increasing"
                trend_icon = "↑"
                trend_color = "red" if category in ['Manual', 'Backlog'] else "green"
            elif start_count > end_count:
                trend = "decreasing"
                trend_icon = "↓"
                trend_color = "green" if category in ['Manual', 'Backlog'] else "red"
            else:
                trend = "stable"
                trend_icon = "→"
                trend_color = "gray"

            # Add to trends
            trends_html += f"""
            <li style='color: {trend_color};'>
            {trend_icon} <b>{category}</b> is {trend} over time.
            <ul>
                <li><b>Slope:</b> {slope:.2f}</li>
                <li><b>Starting Count:</b> {start_count}, <b>Ending Count:</b> {end_count}</li>
                <li><b>Absolute Change:</b> {abs_change}, <b>Percentage Change:</b> {percentage_change:.2f}%</li>
                <li><b>Max Count:</b> {max_count}, <b>Min Count:</b> {min_count}, <b>Average Count:</b> {avg_count:.2f}</li>
                <li><b>Time Range:</b> {first_month} to {last_month}</li>
            </ul>
            </li>
            """

            # Detect significant jumps/drops
            trends_html += f"<h4>Significant Changes in {category}</h4><ul>"
            filled_data['Prev_Count'] = filled_data['Count'].shift(1)
            filled_data['Change'] = filled_data['Count'] - filled_data['Prev_Count']
            filled_data['Percent_Change'] = filled_data['Change'] / filled_data['Prev_Count'].replace(0, np.nan) * 100

            for _, row in filled_data.dropna().iterrows():
                month = row['Created'].strftime('%B-%Y')
                change = row['Change']
                percent_change = row['Percent_Change']

                if abs(percent_change) > 20:  # Threshold for "significant" changes
                    direction = "jumped" if change > 0 else "dropped"
                    trends_html += f"<li>In {month}, the count {direction} by {abs(change)} ({percent_change:.2f}%).</li>"

            trends_html += "</ul>"

    trends_html += "</ul>"
    return trends_html

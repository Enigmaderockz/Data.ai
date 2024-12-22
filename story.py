import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA

# Data preparation
data = {
    "MONTH": [
        "December-2024", "December-2024", "December-2024",
        "November-2024", "November-2024", "November-2024",
        "October-2024", "October-2024", "October-2024",
        "September-2024", "September-2024", "September-2024"
    ],
    "FLEET": [
        "Client Onboarding", "GBT DRM Fleet", "LEAD Fleet",
        "Client Onboarding", "GBT DRM Fleet", "LEAD Fleet",
        "Client Onboarding", "GBT DRM Fleet", "LEAD Fleet",
        "Client Onboarding", "GBT DRM Fleet", "LEAD Fleet"
    ],
    "% AUTOMATED": [26.35, 33.78, 0.0, 29.56, 71.9, 83.87, 33.95, 75.73, 76.92, 49.89, 25.82, 50.77]
}

df = pd.DataFrame(data)

# Convert MONTH to datetime for sorting
df["MONTH"] = pd.to_datetime(df["MONTH"], format="%B-%Y")
df = df.sort_values(by="MONTH")

# Prepare future predictions, excluding months that already have data
future_predictions = []

for fleet in df["FLEET"].unique():
    fleet_data = df[df["FLEET"] == fleet].set_index("MONTH")["% AUTOMATED"]
    model = ARIMA(fleet_data, order=(1, 1, 1))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=3)
    future_months = pd.date_range(
        start=fleet_data.index.max() + pd.DateOffset(months=1),
        periods=3,
        freq='M'
    )
    future_predictions.append(pd.DataFrame({
        "MONTH": future_months,
        "FLEET": fleet,
        "% AUTOMATED": forecast
    }))

future_df = pd.concat(future_predictions)
future_df = future_df[~future_df["MONTH"].isin(df["MONTH"])]  # Exclude existing months

df_combined = pd.concat([df, future_df]).reset_index(drop=True)
df_combined["MONTH_STR"] = df_combined["MONTH"].dt.strftime("%b'%y")
df_combined["% AUTOMATED"] = df_combined["% AUTOMATED"] / 100  # Normalize for percentage

# Create the interactive plot
fig = go.Figure()

# Define colors for fleets
fleet_colors = {"Client Onboarding": "#FFA07A", "GBT DRM Fleet": "#9370DB", "LEAD Fleet": "#20B2AA"}

for fleet, color in fleet_colors.items():
    fleet_data = df_combined[df_combined["FLEET"] == fleet]
    fleet_data["Is_Historical"] = fleet_data["MONTH"] <= df["MONTH"].max()

    # Separate historical and predicted data
    historical_data = fleet_data[fleet_data["Is_Historical"]]
    prediction_data = fleet_data[~fleet_data["Is_Historical"]]

    # Add historical line with markers
    fig.add_trace(go.Scatter(
        x=historical_data["MONTH_STR"],
        y=historical_data["% AUTOMATED"],
        mode="lines+markers",  # Lines with markers for historical data
        name=f"{fleet}",
        line=dict(color=color, width=3),
        marker=dict(size=6),  # Dots for historical data
        hovertemplate=
            f"<b>Fleet:</b> {fleet}<br>" +
            "<b>Month:</b> %{x}<br>" +
            "<b>% Automated:</b> %{y:.2%}<extra></extra>",
        hoverlabel=dict(
            bgcolor="white",   # Background color of tooltip
            font=dict(color=color)  # Text color matches the line color
        )
    ))

    # Add predicted line with dotted style
    fig.add_trace(go.Scatter(
        x=pd.concat([historical_data["MONTH_STR"].tail(1), prediction_data["MONTH_STR"]]),
        y=pd.concat([historical_data["% AUTOMATED"].tail(1), prediction_data["% AUTOMATED"]]),
        mode="lines+markers",  # Lines and markers for dotted prediction
        name=f"{fleet} (Prediction)",
        line=dict(color=color, width=2, dash="dot"),  # Dotted line
        marker=dict(size=8),  # Larger dots for predictions
        hovertemplate=
            f"<b>Fleet:</b> {fleet}<br>" +
            "<b>Month:</b> %{x}<br>" +
            "<b>% Automated:</b> %{y:.2%}<extra></extra>",
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color=color)
        ),
        showlegend=False  # Avoid duplicate legend entries
    ))

# Customize the layout
fig.update_layout(
    title="Fleet Progress: Automated Task Percentage Over Months",
    xaxis_title="Month",
    yaxis_title="% Automated",
    yaxis=dict(
        tickformat=".0%",
        range=[0, 1]  # Ensure Y-axis goes from 0 to 100%
    ),
    legend_title="Fleet",
    template="plotly_white",  # Use a dark theme
    font=dict(
        family="Helvetica, sans-serif",  # Customize font
        size=14,  # Font size
        color="black"  # Font color
    ),
    legend=dict(
        itemclick=False,  # Disable single-click interaction
        itemdoubleclick=False,  # Disable double-click interaction
    )
)

# Save the plot as an interactive HTML file
fig.write_html("fleet_progress_interactive.html")
fig.show()

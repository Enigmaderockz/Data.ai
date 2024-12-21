import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from pmdarima import auto_arima

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

# Prepare a dictionary for storing future predictions
future_predictions = []

# Fit ARIMA and forecast for each fleet using auto_arima for optimal parameters
for fleet in df["FLEET"].unique():
    fleet_data = df[df["FLEET"] == fleet].set_index("MONTH")["% AUTOMATED"]
    
    # Check for stationarity and difference if necessary
    result = adfuller(fleet_data)
    if result[1] > 0.05:  # Not stationary
        fleet_data = fleet_data.diff().dropna()
    
    # Use auto_arima to find the best parameters automatically
    model = auto_arima(fleet_data, seasonal=False, stepwise=True)
    
    # Fit the model
    model_fit = model.fit(fleet_data)
    
    # Forecast future values (next 3 months)
    forecast = model_fit.predict(n_periods=3)
    future_months = pd.date_range(start=fleet_data.index[-1] + pd.Timedelta(days=1), periods=3, freq='M')
    
    # Store predictions
    future_predictions.append(pd.DataFrame({
        "MONTH": future_months,
        "FLEET": fleet,
        "% AUTOMATED": forecast
    }))

# Combine all predictions
future_df = pd.concat(future_predictions)
df_combined = pd.concat([df, future_df]).reset_index(drop=True)

# Add MONTH labels for the x-axis
df_combined["MONTH_STR"] = df_combined["MONTH"].dt.strftime("%b'%y")

# Set plot style
sns.set_theme(style="whitegrid")

# Interactive visualization setup
fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)

# Assign unique colors for fleets
palette = sns.color_palette("husl", len(df["FLEET"].unique()))
line_objects = {}
marker_objects = []

# Plot data for each fleet
for i, fleet in enumerate(df["FLEET"].unique()):
    fleet_data = df_combined[df_combined["FLEET"] == fleet]
    historical_data = fleet_data[fleet_data["MONTH"] <= df["MONTH"].max()]
    prediction_data = fleet_data[fleet_data["MONTH"] > df["MONTH"].max()]
    
    # Plot the historical line (solid)
    line, = ax.plot(
        historical_data["MONTH_STR"], 
        historical_data["% AUTOMATED"], 
        label=fleet, 
        linewidth=2.5, 
        color=palette[i],
        alpha=0.8,
        marker='o'
    )
    line_objects[fleet] = line

    # Plot the prediction line (dotted)
    ax.plot(
        prediction_data["MONTH_STR"], 
        prediction_data["% AUTOMATED"], 
        linestyle='dotted', 
        linewidth=2.5, 
        color=palette[i],
        alpha=0.8,
        marker='X'
    )
    
# Enhance the chart with titles and labels
ax.set_title("Fleet Progress: Automated Task Percentage Over Months", fontsize=16, weight="bold")
ax.set_xlabel("Month", fontsize=14)
ax.set_ylabel("% Automated", fontsize=14)
ax.yaxis.set_major_formatter(PercentFormatter())
ax.tick_params(axis='x', labelsize=12, rotation=45)
ax.tick_params(axis='y', labelsize=12)

# Place the legend outside the plot area
ax.legend(title="Fleet", fontsize=12, title_fontsize=14, loc="upper left", bbox_to_anchor=(1.05, 1))

# Add grid lines with enhanced visibility
ax.grid(visible=True, linestyle="--", alpha=0.6)

# Tooltip for hovering (remains unchanged)
def on_hover(event):
    for text in ax.texts:
        text.remove()

    for marker, fleet, percentage in marker_objects:
        if marker.contains(event)[0]:
            ax.annotate(
                f"{fleet}: {percentage:.2f}%",
                xy=(event.xdata, event.ydata),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=10,
                color="black",
                backgroundcolor="white",
                bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white")
            )
            fig.canvas.draw()
            return

# Click event to highlight lines (remains unchanged)
def on_click(event):
    for text in ax.texts:
        text.remove()

    for fleet, line in line_objects.items():
        if line.contains(event)[0]:
            line.set_linewidth(4)
            line.set_alpha(1.0)
        else:
            line.set_linewidth(2)
            line.set_alpha(0.3)
    fig.canvas.draw()

# Connect hover and click events (remains unchanged)
fig.canvas.mpl_connect('motion_notify_event', on_hover)
fig.canvas.mpl_connect('button_press_event', on_click)

# Show the chart
plt.show()




import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
import numpy as np
from sklearn.linear_model import LinearRegression

# Data preparation (same as before)
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
    "AUTOMATED": [122, 25, 0, 214, 238, 681, 793, 387, 460, 1170, 166, 132],
    "MANUAL": [39, 1, 7, 140, 14, 55, 397, 16, 51, 362, 11, 42],
    "BACKLOG": [302, 48, 30, 370, 79, 76, 1146, 108, 87, 813, 466, 86],
    "% AUTOMATED": [26.35, 33.78, 0.0, 29.56, 71.9, 83.87, 33.95, 75.73, 76.92, 49.89, 25.82, 50.77]
}

df = pd.DataFrame(data)

# Convert MONTH to datetime for sorting
df["MONTH"] = pd.to_datetime(df["MONTH"], format="%B-%Y")
df = df.sort_values(by="MONTH")

# Set plot style
sns.set_theme(style="whitegrid")

# Prepare months for x-axis labels
df["MONTH_STR"] = df["MONTH"].dt.strftime("%B")

# Train a simple linear regression model for each fleet to predict future values
def predict_future(fleet_data, months_to_predict=3):
    # Prepare data for regression
    fleet_data = fleet_data.sort_values(by="MONTH")
    X = np.array(range(len(fleet_data))).reshape(-1, 1)  # Months as integer values
    y = fleet_data["% AUTOMATED"].values  # Target variable (% Automated)

    # Fit a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict future months
    future_months = np.array(range(len(fleet_data), len(fleet_data) + months_to_predict)).reshape(-1, 1)
    future_predictions = model.predict(future_months)
    
    # Generate future month labels
    last_month = fleet_data["MONTH"].max()
    future_dates = [last_month + pd.DateOffset(months=i) for i in range(1, months_to_predict + 1)]
    
    return future_dates, future_predictions

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)

# Assign unique colors for fleets
palette = sns.color_palette("husl", len(df["FLEET"].unique()))
line_objects = {}
marker_objects = []

# Plot data for each fleet
for i, fleet in enumerate(df["FLEET"].unique()):
    fleet_data = df[df["FLEET"] == fleet]
    
    # Plot historical data
    line, = ax.plot(
        fleet_data["MONTH_STR"], 
        fleet_data["% AUTOMATED"], 
        label=fleet, 
        marker="o", 
        linewidth=2.5, 
        color=palette[i],
        alpha=0.8
    )
    line_objects[fleet] = line
    # Add markers
    for x, y in zip(fleet_data["MONTH_STR"], fleet_data["% AUTOMATED"]):
        marker, = ax.plot(x, y, "o", color=palette[i], markersize=6, alpha=0.8, picker=True)
        marker_objects.append((marker, fleet, y))
    
    # Predict future values
    future_dates, future_predictions = predict_future(fleet_data)
    future_months = [date.strftime("%B-%Y") for date in future_dates]
    
    # Plot future predictions with a dotted line
    ax.plot(
        future_months, 
        future_predictions, 
        linestyle="--",  # Dotted line
        color=palette[i],
        linewidth=2,
        alpha=0.6,
        label=f"{fleet} Prediction"
    )

# Enhance the chart
ax.set_title("Fleet Progress: Automated Task Percentage Over Months with Future Predictions", fontsize=14, weight="bold")
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("% Automated", fontsize=12)
ax.yaxis.set_major_formatter(PercentFormatter())
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.legend(title="Fleet", fontsize=10, title_fontsize=12, loc="upper left")

# Add grid lines
ax.grid(visible=True, linestyle="--", alpha=0.6)

# Tooltip for hovering
def on_hover(event):
    for marker, fleet, percentage in marker_objects:
        if marker.contains(event)[0]:
            ax.annotate(
                f"{fleet}: {percentage:.2f}% Automated",
                xy=(event.xdata, event.ydata),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=10,
                color="black",
                backgroundcolor="white",
                bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white")
            )
            fig.canvas.draw()
            return
    # Clear previous annotations
    for text in ax.texts:
        text.remove()
    fig.canvas.draw()

# Click event to highlight lines and clear previous tooltips
def on_click(event):
    # Clear previous annotations when clicking
    for text in ax.texts:
        text.remove()

    for fleet, line in line_objects.items():
        if line.contains(event)[0]:  # Check if the line is clicked
            # Make this line bold (increased linewidth)
            line.set_linewidth(4)
            line.set_alpha(1.0)
        else:
            # Reduce opacity of other lines
            line.set_linewidth(2)
            line.set_alpha(0.3)
    fig.canvas.draw()

# Connect hover and click events
fig.canvas.mpl_connect('motion_notify_event', on_hover)
fig.canvas.mpl_connect('button_press_event', on_click)

# Show the chart
plt.show()



import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fbprophet import Prophet
from matplotlib.ticker import PercentFormatter

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
    "AUTOMATED": [122, 25, 0, 214, 238, 681, 793, 387, 460, 1170, 166, 132],
    "MANUAL": [39, 1, 7, 140, 14, 55, 397, 16, 51, 362, 11, 42],
    "BACKLOG": [302, 48, 30, 370, 79, 76, 1146, 108, 87, 813, 466, 86],
    "% AUTOMATED": [26.35, 33.78, 0.0, 29.56, 71.9, 83.87, 33.95, 75.73, 76.92, 49.89, 25.82, 50.77]
}

df = pd.DataFrame(data)

# Convert MONTH to datetime for sorting
df["MONTH"] = pd.to_datetime(df["MONTH"], format="%B-%Y")
df = df.sort_values(by="MONTH")

# Set plot style
sns.set_theme(style="whitegrid")

# Prepare months for x-axis labels
df["MONTH_STR"] = df["MONTH"].dt.strftime("%B")

# Function to predict future using Prophet
def predict_future_prophet(fleet_data, months_to_predict=3):
    df_prophet = fleet_data[["MONTH", "% AUTOMATED"]].rename(columns={'MONTH': 'ds', '% AUTOMATED': 'y'})
    
    model = Prophet()
    model.fit(df_prophet)
    
    future = model.make_future_dataframe(periods=months_to_predict, freq='M')
    forecast = model.predict(future)
    
    return forecast['ds'].dt.strftime('%B-%Y').tolist(), forecast['yhat'].tolist(), forecast['yhat_lower'].tolist(), forecast['yhat_upper'].tolist()

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)

# Assign unique colors for fleets
palette = sns.color_palette("husl", len(df["FLEET"].unique()))
line_objects = {}

# Plot data for each fleet
for i, fleet in enumerate(df["FLEET"].unique()):
    fleet_data = df[df["FLEET"] == fleet]
    
    # Plot historical data
    line, = ax.plot(
        fleet_data["MONTH_STR"], 
        fleet_data["% AUTOMATED"], 
        label=fleet, 
        marker="o", 
        linewidth=2.5, 
        color=palette[i],
        alpha=0.8
    )
    line_objects[fleet] = line
    
    # Predict future values
    future_dates, future_predictions, lower_bound, upper_bound = predict_future_prophet(fleet_data)
    
    # Plot future predictions with confidence intervals
    ax.plot(
        future_dates, 
        future_predictions, 
        linestyle="--",  
        color=palette[i],
        linewidth=2,
        alpha=0.6,
        label=f"{fleet} Prediction"
    )
    ax.fill_between(future_dates, lower_bound, upper_bound, alpha=0.1, color=palette[i])

# Enhance the chart
ax.set_title("Fleet Progress: Automated Task Percentage Over Months with Future Predictions", fontsize=14, weight="bold")
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("% Automated", fontsize=12)
ax.yaxis.set_major_formatter(PercentFormatter())
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.legend(title="Fleet", fontsize=10, title_fontsize=12, loc="upper left")

# Add grid lines
ax.grid(visible=True, linestyle="--", alpha=0.6)

# Show the chart
plt.show()

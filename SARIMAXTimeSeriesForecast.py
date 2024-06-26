import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import boxcox
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np

# Define the inverse Box-Cox transformation function
def invboxcox(y, lam):
    if lam == 0:
        return np.exp(y)
    else:
        return np.exp(np.log(lam * y + 1) / lam)

# Load the Excel file
file_path = r'C:\Users\19792\Documents\BrentCrudePrices.xlsx'

# Read the data, ensure it's sorted and has no missing dates
df = pd.read_excel(file_path, parse_dates=['Date'])
df.sort_values('Date', inplace=True)
df.set_index('Date', inplace=True)
df = df.asfreq('D')
df['Price'] = df['Price'].ffill()

# Transform data with Box-Cox
df['Price_transformed'], lam = boxcox(df['Price'])

# Fit the SARIMAX model on transformed data
model = SARIMAX(df['Price_transformed'], order=(0, 1, 0), seasonal_order=(0, 1, 1, 12))
results = model.fit()

# Diagnostics plot on transformed data
results.plot_diagnostics(figsize=(15, 12))
plt.show()

# Forecasting
forecast_steps = 365 * 3  # Forecasting 3 years into the future
forecast = results.get_forecast(steps=forecast_steps)
forecast_index = pd.date_range(start=df.index[-1], periods=forecast_steps + 1, freq='D')[1:]
forecast_transformed = forecast.predicted_mean

# Inverse transform the forecast
forecast_values = invboxcox(forecast_transformed, lam)
forecast_df = pd.DataFrame({'Forecast': forecast_values}, index=forecast_index)

# Plot the results
plt.figure(figsize=(15, 7))
plt.plot(df['Price'], label='Historical Prices')
plt.plot(forecast_df['Forecast'], label='Forecast (Transformed)', linestyle='--')
plt.title('Brent Crude Prices Forecast with Transformed SARIMAX')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.show()
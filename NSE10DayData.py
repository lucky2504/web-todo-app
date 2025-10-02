import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# List of common NSE stocks
nse_stocks = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC',
    'SBIN', 'BHARTIARTL', 'HDFC', 'KOTAKBANK', 'LT', 'AXISBANK', 'BAJFINANCE',
    'MARUTI', 'ASIANPAINT', 'WIPRO', 'HCLTECH', 'SUNPHARMA', 'ULTRACEMCO'
]


def fetch_stock_data(symbol, start_date, end_date):
    try:
        stock = yf.Ticker(f"{symbol}.NS")
        data = stock.history(start=start_date, end=end_date)
        if not data.empty:
            data = data.reset_index()
            # Convert timezone-aware datetime to timezone-naive datetime
            data['Date'] = data['Date'].dt.tz_localize(None)
            data['Stock'] = symbol
            return data[['Stock', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None


# Set date range
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Fetch data for all stocks
all_data = []
total_stocks = len(nse_stocks)

print("Fetching data for NSE stocks...")
for i, symbol in enumerate(nse_stocks, 1):
    print(f"Processing {symbol} ({i}/{total_stocks})")
    stock_data = fetch_stock_data(symbol, start_date, end_date)
    if stock_data is not None:
        all_data.append(stock_data)

if all_data:
    # Combine all data
    final_df = pd.concat(all_data, ignore_index=True)

    # Rename columns to match requested format
    final_df = final_df.rename(columns={
        'Open': 'Open Price',
        'High': 'High Price',
        'Low': 'Low Price',
        'Close': 'Close Price'
    })

    # Sort by Stock and Date
    final_df = final_df.sort_values(['Stock', 'Date'])

    # Ensure all datetime columns are timezone-naive
    final_df['Date'] = pd.to_datetime(final_df['Date']).dt.tz_localize(None)

    try:
        # Save to Excel
        output_file = "NSE_stocks_last_365_days.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"\n✅ Data exported to {output_file}")
        print(f"Total records: {len(final_df)}")
        print(f"Unique stocks: {final_df['Stock'].nunique()}")

        # Display first few rows
        print("\nSample of the data:")
        print(final_df.head())
    except Exception as e:
        print(f"Error saving to Excel: {str(e)}")

        # Alternative: Save to CSV if Excel fails
        csv_file = "NSE_stocks_last_365_days.csv"
        final_df.to_csv(csv_file, index=False)
        print(f"Data saved to CSV instead: {csv_file}")
else:
    print("No data was collected. Please check your internet connection and try again.")

# Display data info
print("\nDataFrame Info:")
print(final_df.info())

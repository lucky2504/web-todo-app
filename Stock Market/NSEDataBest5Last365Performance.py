import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

# Define the Nifty top 5 stocks
# You can add more symbols to this list
NIFTY_STOCKS = [

'TATAINVEST','HINDCOPPER','MUTHOOTFIN','AGARWALEYE','NAM-INDIA',

]


def fetch_stock_data(symbol, start_date, end_date):
    try:
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(f"{symbol}.NS")
        data = stock.history(start=start_date, end=end_date)

        if not data.empty:
            # Reset index to make date a column
            data = data.reset_index()
            # Remove timezone info
            data['Date'] = data['Date'].dt.tz_localize(None)
            # Add symbol column
            data['Symbol'] = symbol

            # Get market cap
            info = stock.info
            market_cap = info.get('marketCap', 0)
            data['Market_Cap'] = market_cap

            # Select and rename relevant columns
            return data[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market_Cap']]

        return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None


def main():
    # Set date range for last 365 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"Fetching data for {len(NIFTY_STOCKS)} stocks...")
    print(f"Date range: {start_date.date()} to {end_date.date()}")

    # Store all data
    all_data = []
    successful_fetches = 0
    failed_fetches = 0

    # Process each symbol
    for i, symbol in enumerate(NIFTY_STOCKS, 1):
        print(f"Processing {symbol} ({i}/{len(NIFTY_STOCKS)})")

        data = fetch_stock_data(symbol, start_date, end_date)
        if data is not None:
            all_data.append(data)
            successful_fetches += 1
        else:
            failed_fetches += 1

        # Add delay to avoid rate limiting
        time.sleep(1)

    if all_data:
        # Combine all data
        final_df = pd.concat(all_data, ignore_index=True)

        # Convert market cap to crores
        final_df['Market_Cap_Cr'] = final_df['Market_Cap'] / 10000000

        # Sort by market cap and date
        final_df = final_df.sort_values(['Market_Cap', 'Date'], ascending=[False, True])

        # Create summary DataFrame with latest data and market cap
        latest_data = final_df.sort_values('Date').groupby('Symbol').last()
        summary_df = latest_data.sort_values('Market_Cap', ascending=False)
        summary_df = summary_df.reset_index()

        # Calculate additional metrics
        summary_df['30_Day_High'] = final_df.groupby('Symbol')['High'].max().values
        summary_df['30_Day_Low'] = final_df.groupby('Symbol')['Low'].min().values
        summary_df['Avg_Volume'] = final_df.groupby('Symbol')['Volume'].mean().values

        # Save detailed data
        output_file = "../nifty_stocks_top_5_365days_detailed.xlsx"
        final_df.to_excel(output_file, index=False)

        # Save summary data
        summary_file = "../nifty_stocks_summary.xlsx"
        summary_df.to_excel(summary_file, index=False)

        print("\nProcessing complete!")
        print(f"Successful fetches: {successful_fetches}")
        print(f"Failed fetches: {failed_fetches}")
        print(f"\nDetailed data saved to: {output_file}")
        print(f"Summary data saved to: {summary_file}")

        print("\nTop 10 companies by market cap:")
        print(summary_df[['Symbol', 'Market_Cap_Cr', 'Close', '30_Day_High', '30_Day_Low']].head(10))

        # Calculate some statistics
        print("\nMarket Statistics:")
        print(f"Total market cap: ₹{summary_df['Market_Cap_Cr'].sum():,.2f} Cr")
        print(f"Average market cap: ₹{summary_df['Market_Cap_Cr'].mean():,.2f} Cr")
        print(f"Average daily volume: {summary_df['Avg_Volume'].mean():,.0f}")

    else:
        print("No data was collected")


if __name__ == "__main__":
    main()

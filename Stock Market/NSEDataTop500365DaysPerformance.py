import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

# Define the Nifty top 50 stocks
# You can add more symbols to this list
NIFTY_STOCKS = [

'RELIANCE','HDFCBANK','BHARTIARTL','TCS','ICICIBANK','SBIN','BAJFINANCE','INFY','HINDUNILVR','LICI','LT','ITC','MARUTI','M&M','KOTAKBANK','SUNPHARMA','HCLTECH','AXISBANK','ULTRACEMCO','NTPC','HAL','BAJAJFINSV','ADANIPORTS','ONGC','TITAN','ADANIENT','ETERNAL','BEL','ADANIPOWER','DMART','JSWSTEEL','TATAMOTORS','POWERGRID','WIPRO','BAJAJ-AUTO','COALINDIA','ASIANPAINT','NESTLEIND','INDIGO','TATASTEEL','HYUNDAI','IOC','HINDZINC','EICHERMOT','JIOFIN','GRASIM','VEDL','SBILIFE','DLF','ADANIGREEN','TRENT','HINDALCO','HDFCLIFE','IRFC','TVSMOTOR','LTIM','DIVISLAB','PIDILITIND','VBL','BPCL','BRITANNIA','AMBUJACEM','BAJAJHLDNG','PFC','CHOLAFIN','BANKBARODA','PNB','MUTHOOTFIN','TECHM','TATAPOWER','CIPLA','SOLARINDS','TORNTPHARM','SHRIRAMFIN','ENRIN','HDFCAMC','GODREJCP','CGPOWER','GAIL','MAZDOCK','LODHA','BOSCHLTD','TATACONSUM','CANBK','MOTHERSON','SIEMENS','POLYCAB','ABB','HEROMOTOCO','CUMMINSIND','JINDALSTEL','MAXHEALTH','ADANIENSOL','APOLLOHOSP','SHREECEM','UNIONBANK','DRREDDY','INDHOTEL','MANKIND','ZYDUSLIFE','DIXON','RECLTD','INDIANB','IDBI','UNITDSPR','SWIGGY','WAAREEENER','GMRAIRPORT','ICICIGI','HINDPETRO','JSWENERGY','HAVELLS','INDUSTOWER','BAJAJHFL','IDEA','MARICO','LUPIN','DABUR','NHPC','NAUKRI','ICICIPRULI','SRF','BSE','BHEL','ASHOKLEY','SBICARD','BHARTIHEXA','NTPCGREEN','POWERINDIA','ABCAPITAL','GVT&D','PERSISTENT','POLICYBZR','UNOMINDA','IOB','OFSS','SUZLON','FORTIS','PAYTM','RVNL','ATGL','VMM','NYKAA','YESBANK','OIL','NMDC','COROMANDEL','PRESTIGE','JSWINFRA','SCHAEFFLER','ALKEM','LLOYDSME','LTF','GICRE','ABBOTINDIA','HDBFS','AUROPHARMA','MRF','PATANJALI','JSL','BERGEPAINT','TORNTPOWER','GODREJPROP','COLPAL','TIINDIA','BHARATFORG','OBEROIRLTY','INDUSINDBK','FACT','BANKINDIA','BDL','IRCTC','NAM-INDIA','SAIL','PHOENIXLTD','MFSL','GLENMARK','AUBANK','MOTILALOFS','PIIND','UPL','TATAINVEST','SUPREMEIND','COFORGE','LINDEINDIA','GODFRYPHLP','AIIL','MPHASIS','IDFCFIRSTB','COCHINSHIP','JKCEMENT','SUNDARMFIN','APLAPOLLO','KALYANKJIL','KAYNES','UBL','FEDERALBNK','LAURUSLABS','PAGEIND','HUDCO','BIOCON','ITCHOTELS','PGHH','TATACOMM','PREMIERENE','GLAXO','VOLTAS','BALKRISIND','LTTS','ANTHEM','MAHABANK','IREDA','360ONE','DALBHARAT','PETRONET','HEXT','JUBLFOOD','FLUOROCHEM','MCX','GODREJIND','POONAWALLA','ESCORTS','CONCOR','ENDURANCE','NATIONALUM','RADICO','BLUESTARCO','KEI','UCOBANK','NLCINDIA','M&MFIN','ASTRAL','KPRMILL','THERMAX','SJVN','CHOLAHLDNG','MEDANTA','NH','ACC','METROBRAND','CENTRALBK','AWL','IPCALAB','EXIDEIND','COHANCE','3MINDIA','APARINDS','CRISIL','ASTERDM','GLAND','DELHIVERY','TATAELXSI','HINDCOPPER','GODIGIT','HONAUT','LICHSGFIN','NIACL','KPITTECH','GILLETTE','CDSL','MSUMI','GRSE','AIAENG','GUJGASLTD','APOLLOTYRE','AJANTPHARM','ITI','NBCC','IGL','AEGISVOPAK','AMBER','TATATECH','AEGISLOG','AFFLE','KIMS','SUMICHEM','STARHEALTH','KIOCL','JBCHEPHARM','PPLPHARMA','BANDHANBNK','LALPATHLAB','TVSHLTD','SONACOMS','SHYAMMETL','SYNGENE','DEEPAKNTR','IRB','EMCURE','IKS','ZFCVINDIA','INOXWIND','URBANCO','SANDUMA','WOCKPHARMA','MANAPPURAM','ANANTRAJ','ANANDRATHI','EMAMILTD','NAVINFLUOR','SKFINDIA','PFIZER','PTCIL','TATACHEM','RAMCOCEM','NUVAMA','MRPL','OLAELEC','HBLENGINE','SUNTV','ABSLAMC','NETWEB','ASTRAZEN','TIMKEN','PNBHOUSING','EIHOTEL','KEC','FSL','WELCORP','CREDITACC','FORCEMOT','ATHERENERG','HSCL','ERIS','BAYERCROP','ASAHIINDIA','AADHARHFC','BRIGADE','REDINGTON','CESC','PSB','KPIL','SUNDRMFAST','CHALET','DEVYANI','ONESOURCE','CHAMBLFERT','SAGILITY','HATSUN','KARURVYSYA','KANSAINER','JYOTICNC','CASTROLIND','BASF','SCHNEIDER','POLYMED','NEULANDLAB','ANGELONE','GMDCLTD','MAHSCOOTER','DEEPAKFERT','SARDAEN','IIFL','CAMS','RPOWER','CROMPTON','KAJARIACER','JSWCEMENT','ECLERX','ABREL','SAILIFE','KFINTECH','EIDPARRY','BIKAJI','NAVA','ARE&M','ATUL','CGCL','DCMSHRIRAM','GRINDWELL','BEML','GSPL','APLLTD','VINATIORGA','GABRIEL','FIRSTCRY','TRAVELFOOD','CENTURYPLY','JUBLPHARMA','CARBORUNIV','ZENSARTECH','ACMESOLAR','JSWHL','CONCORDBIO','RATNAMANI','VENTIVE','RBLBANK','MANYAVAR','AFCONS','UTIAMC','TRITURBINE','IRCON','ABLBL','APTUS','SOBHA','VGUARD','TBOTEK','JBMA','AGARWALEYE','CRAFTSMAN','GALLANTT','GPIL','PARADEEP','KIRLOSBROS','CHOICEIN','FIVESTAR','CAPLIPOINT','CUB','CIEINDIA','SPLPETRO','JMFINANCIL','LMW','CPPLUS','TECHNOE','SYRMA','IGIL','DOMS','BATAINDIA','ELGIEQUIP','WHIRLPOOL','NIVABUPA','ABDL','NUVOCO','AKZOINDIA','IFCI','DATAPATTNS','TARIL','SIGNATURE','ZYDUSWELL','SWANCORP','PGEL','TRIDENT','NATCOPHARM','PCBL','INDIAMART','THELEELA','RRKABEL','JWL','KSB','GESHIP','BELRISE','LTFOODS','CEATLTD','CEMPRO','NSLNISP','FINEORG','USHAMART','AARTIIND','SAMMAANCAP','BLS','RAINBOW','MINDACORP','SUNDARMHLD','INDGN','BLUEDART','INTELLECT','KIRLOSENG','PFOCUS','GODREJAGRO','EMBDL','ZENTEC','GRANULES','LEMONTREE','NCC','ELECON','JINDALSAW','INGERRAND','AAVAS','OLECTRA','TEGA','HOMEFIRST','ACE','CYIENT','CELLO','MGL','BBTC','IEX','NEWGEN','FINCABLES','FINPIPE','RAILTEL','BANCOINDIA','JPPOWER','RITES','INDIACEM','ANURAS','VIKRAMSOLR','SHRIPISTON','VTL','TITAGARH','GRINFRA','SBFC','JYOTHYLAB','CLEAN','CARTRADE','ALIVUS','BLUEJET','J&KBANK','GRAVITA','CCL'

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
    # Set date range for last 15 days
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
        output_file = "../nifty_stocks_top_500_365days_detailed.xlsx"
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

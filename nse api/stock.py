import yfinance as yf

def get_stock_info():
    # Step 1: Take stock symbol as input
    stock_symbol = input("Enter stock symbol (e.g., TCS.NS, RELIANCE.NS, INFY.NS): ").upper()

    # Fetch stock data using Yahoo Finance
    stock = yf.Ticker(stock_symbol)

    # Get basic stock price details
    stock_info = stock.history(period="1d")
    
    if stock_info.empty:
        print("Invalid stock symbol or data not available. Please try again.")
        return

    last_price = stock_info['Close'].iloc[-1]
    day_high = stock_info['High'].iloc[-1]
    day_low = stock_info['Low'].iloc[-1]

    print(f"\nStock: {stock_symbol}")
    print(f"Last Traded Price: {last_price}")
    print(f"Day High: {day_high}")
    print(f"Day Low: {day_low}")

    # Available parameters
    parameters = {
        "1": ("PE Ratio", stock.info.get("trailingPE", "N/A")),
        "2": ("PB Ratio", stock.info.get("priceToBook", "N/A")),
        "3": ("Book Value", stock.info.get("bookValue", "N/A")),
        "4": ("ROE (Return on Equity)", stock.info.get("returnOnEquity", "N/A")),
        "5": ("ROCE (Return on Capital Employed)", "N/A"),  # Not available in Yahoo Finance
        "6": ("Debt to Equity", stock.info.get("debtToEquity", "N/A")),
        "7": ("Face Value", stock.info.get("faceValue", "N/A")),
        "8": ("52-Week High", stock.info.get("fiftyTwoWeekHigh", "N/A")),
        "9": ("52-Week Low", stock.info.get("fiftyTwoWeekLow", "N/A")),
    }

    # Step 3: Run a loop to allow multiple parameter selections
    while True:
        print("\nAvailable Parameters:")
        for key, (param, _) in parameters.items():
            print(f"{key}. {param}")
        print("0 or e to exit")

        choice = input("\nEnter the number of the parameter you want to view (or '0'/'e' to exit): ").lower()

        if choice in ['0', 'e']:
            print("Exiting program. Thank you!")
            break
        elif choice in parameters:
            param_name, param_value = parameters[choice]
            print(f"\n{param_name}: {param_value}")
        else:
            print("Invalid choice. Please try again.")

# Run the function
get_stock_info()

#pip install nsetools
from nsetools import Nse

nse = Nse()

# Get NIFTY 50 data
nifty = nse.get_index_quote("nifty 50")
print(f"NIFTY 50: {nifty['last']} (Change: {nifty['variation']} | {nifty['percentChange']}%)")

# Get stock quote
stock_symbol = input("Enter stock symbol (e.g., TCS, RELIANCE, INFY): ").upper()

# Get stock quote
stock = nse.get_quote(stock_symbol)

if stock:
    print(f"\n{stock_symbol} Stock Price: {stock['lastPrice']} (Change: {stock['change']} | {stock['pChange']}%)")
    print(f"Day Range: {stock['intraDayHighLow']['min']} - {stock['intraDayHighLow']['max']}")
    print(f"52-Week Range: {stock['weekHighLow']['min']} - {stock['weekHighLow']['max']}")
else:
    print("Invalid stock symbol. Please try again.")



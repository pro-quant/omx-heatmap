def fetch_data():
    """
    Fetch market data from Yahoo Finance for each symbol in omxs30_info.
    Returns a DataFrame containing:
        Symbol, MarketCap, CloseToday, CloseYesterday, PctChange
    """
    data = []
    for symbol in [info["SymbolYahoo"] for info in omxs30_info]:
        try:
            print(f"Fetching data for {symbol}...")
            stock = yf.Ticker(symbol)
            info = stock.info  # Retrieve company information

            # Extract market cap and daily percentage change
            market_cap = info.get("marketCap", None)
            stock_data = yf.download(
                symbol, period="5d", interval="1d", progress=False)

            if len(stock_data) >= 2:
                stock_data = stock_data.tail(2)
                close_today = stock_data["Close"].iloc[-1]
                close_yesterday = stock_data["Close"].iloc[-2]
                pct_change = ((close_today - close_yesterday) /
                              close_yesterday) * 100
            else:
                close_today = close_yesterday = pct_change = None

            data.append({
                "Symbol": symbol,
                "MarketCap": market_cap,
                "CloseToday": close_today,
                "CloseYesterday": close_yesterday,
                "PctChange": pct_change
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            data.append({
                "Symbol": symbol,
                "MarketCap": None,
                "CloseToday": None,
                "CloseYesterday": None,
                "PctChange": None
            })

        time.sleep(1)  # Rate limiting to avoid issues with Yahoo Finance API

    return pd.DataFrame(data)

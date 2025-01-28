import yfinance as yf
import pandas as pd
import time


def fetch_data(omxs30_info):
    """
    Fetch stock data for OMXS30 symbols and calculate market cap and daily percentage change.
    """
    data = []
    for symbol in [info["SymbolYahoo"] for info in omxs30_info]:
        try:
            print(f"Fetching data for {symbol}...")
            stock = yf.Ticker(symbol)
            info = stock.info

            market_cap = info.get("marketCap", 0)
            stock_data = yf.download(
                symbol, period="5d", interval="1d", progress=False)

            if len(stock_data) >= 2:
                stock_data = stock_data.tail(2)
                close_today = stock_data["Close"].iloc[-1]
                close_yesterday = stock_data["Close"].iloc[-2]
                pct_change = float(
                    ((close_today - close_yesterday) / close_yesterday) * 100)
            else:
                print(f"Not enough data for {symbol}")
                close_today = close_yesterday = pct_change = None

            data.append({
                "Symbol": symbol,
                "MarketCap": market_cap,
                "CloseToday": close_today,
                "CloseYesterday": close_yesterday,
                "PctChange": pct_change,
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            data.append({
                "Symbol": symbol,
                "MarketCap": None,
                "CloseToday": None,
                "CloseYesterday": None,
                "PctChange": None,
            })
        time.sleep(1)

    return pd.DataFrame(data)


def prepare_data(df_pct_change, omxs30_info):
    """
    Prepare and clean data for plotting.
    """
    df_info = pd.DataFrame(omxs30_info)
    df_combined = pd.merge(df_info, df_pct_change,
                           left_on="SymbolYahoo", right_on="Symbol", how="left")

    df_combined["PctChange"] = pd.to_numeric(
        df_combined["PctChange"], errors="coerce")
    df_combined = df_combined.dropna(subset=["PctChange"])
    df_combined["SumMarketCap"] = df_combined["MarketCap"]
    df_combined["WeightedDailyChange"] = df_combined["PctChange"]

    return df_combined

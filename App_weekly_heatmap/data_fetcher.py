import yfinance as yf
import pandas as pd
import time


def fetch_data(omxs30_info, start_date, end_date, save_to_csv=True, output_file="fetched_data.csv"):
    """
    Fetch stock data for OMXS30 symbols and calculate market cap and daily percentage change.
    """
    data = []
    for symbol in [info["SymbolYahoo"] for info in omxs30_info]:
        try:
            print(f"Fetching data for {symbol} from {
                  start_date} to {end_date}...")

            # Fetch stock info
            stock = yf.Ticker(symbol)
            info = stock.info
            market_cap = info.get("marketCap", None)

            # Download historical price data
            stock_data = yf.download(
                symbol, start=start_date, end=end_date, interval="1d", progress=False)

            # Skip stocks with no valid data
            if stock_data.empty or "Close" not in stock_data.columns:
                print(f"Warning: No valid trading data for {symbol} between {
                      start_date} and {end_date}. Skipping...")
                continue

            # Extract the close prices (ensure scalar values)
            close_start = stock_data["Close"].iloc[0]
            close_end = stock_data["Close"].iloc[-1]

            # Ensure values are scalars (convert from Series if necessary)
            if isinstance(close_start, pd.Series):
                close_start = close_start.iloc[0]
            if isinstance(close_end, pd.Series):
                close_end = close_end.iloc[0]

            close_start = float(close_start) if not pd.isna(
                close_start) else None
            close_end = float(close_end) if not pd.isna(close_end) else None

            # Validate close prices
            if close_start is None or close_end is None:
                print(f"Warning: Missing close prices for {
                      symbol}. Skipping...")
                continue

            # Calculate percentage change
            pct_change = ((close_end - close_start) / close_start) * 100

            # Append data
            data.append({
                "Symbol": symbol,
                "MarketCap": market_cap,
                "CloseStart": close_start,
                "CloseEnd": close_end,
                "PctChange": pct_change,
            })

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

        # Sleep to prevent rate limiting
        time.sleep(1)

    # Convert the data to a DataFrame
    df_result = pd.DataFrame(data)

    # Save the DataFrame to a CSV file if requested
    if save_to_csv:
        df_result.to_csv(output_file, index=False)
        print(f"Fetched data saved to {output_file}")

    return df_result


def prepare_data(df_pct_change, omxs30_info):
    """
    Prepare and clean data for plotting.
    """
    # Convert OMXS30 info into DataFrame
    df_info = pd.DataFrame(omxs30_info)

    # Merge stock data with sector info
    df_combined = pd.merge(
        df_info, df_pct_change, left_on="SymbolYahoo", right_on="Symbol", how="inner")

    # Convert to numeric and drop missing values
    df_combined["PctChange"] = pd.to_numeric(
        df_combined["PctChange"], errors="coerce")
    df_combined.dropna(subset=["PctChange"], inplace=True)

    # Ensure at least one stock has valid data
    if df_combined.empty:
        raise ValueError(
            "No valid stock data available after merging. Please check the stock tickers or date range.")

    # Aggregate sector-level data
    df_combined["SumMarketCap"] = df_combined["MarketCap"]
    df_combined["WeightedDailyChange"] = df_combined["PctChange"]

    print("Data prepared successfully for plotting.")
    return df_combined

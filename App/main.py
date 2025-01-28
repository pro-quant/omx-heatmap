from fetchdata import fetch_data
from omx_symbols import omxs30_info
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import squarify
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
from matplotlib.patheffects import withStroke
# Suppress FutureWarnings from yfinance
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Step 1: Fetch data
data = []

for symbol in [info["SymbolYahoo"] for info in omxs30_info]:
    try:
        print(f"Fetching data for {symbol}...")
        stock = yf.Ticker(symbol)
        info = stock.info

        market_cap = info.get("marketCap", 0)  # Default to 0 if missing
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

    time.sleep(1)

# Step 2: Create DataFrame and merge
df_pct_change = pd.DataFrame(data)
df_info = pd.DataFrame(omxs30_info)
df_combined = pd.merge(df_info, df_pct_change,
                       left_on="SymbolYahoo", right_on="Symbol", how="left")

# Step 3: Clean and aggregate
df_combined["PctChange"] = pd.to_numeric(
    df_combined["PctChange"], errors="coerce")
df_combined = df_combined.dropna(subset=["PctChange"])
df_combined["SumMarketCap"] = df_combined["MarketCap"]
df_combined["WeightedDailyChange"] = df_combined["PctChange"]

# Group by BaseSymbol and Sector
df_combined = (
    df_combined
    .groupby(["BaseSymbol", "Sector"], as_index=False)
    .agg({
        "SumMarketCap": "sum",
        "WeightedDailyChange": "mean",
    })
)

# Output final DataFrame
print("Final grouped DataFrame:")
print(df_combined)


def prepare_combined_df():
    """
    Fetch data for OMXS30, merge, and aggregate MarketCap + WeightedDailyChange.
    Returns the aggregated DataFrame 'df_combined'.
    """
    df_pct_change = fetch_data()
    df_info = pd.DataFrame(omxs30_info)

    df_combined = pd.merge(
        df_info, df_pct_change, left_on="SymbolYahoo", right_on="Symbol", how="left"
    )

    # Assign columns
    df_combined["SumMarketCap"] = df_combined["MarketCap"]
    df_combined["WeightedDailyChange"] = df_combined["PctChange"]

    # Combine duplicate companies (e.g., ATCO-A and ATCO-B)
    df_combined = (
        df_combined
        .groupby(["BaseSymbol", "Sector"], as_index=False)
        .agg({
            "SumMarketCap": "sum",        # Sum market caps
            "WeightedDailyChange": "mean"  # Average percentage change
        })
    )
    return df_combined


def save_plot_with_date(fig, prefix, folder="daily heatmap"):
    """
    Save the plot with a unique filename based on the current date and time.
    Returns the filepath of the saved plot.

    Parameters:
    - fig: The matplotlib figure object to save.
    - prefix: A string prefix for the filename (e.g., 'OMXS30_StockHeatmap').
    - folder: The directory where the plot should be saved.
    """
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Generate the filename with date + time => YYYY-MM-DD_HH-MM-SS
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{folder}/{prefix}_{timestamp}.png"

    # Save the figure
    fig.savefig(filename, dpi=800, bbox_inches="tight")
    print(f"Plot saved successfully at: {filename}")
    return filename


def plot_omxs30_treemap_instagram(df_combined):
    """
    Create a treemap where each company's area is proportional to its market capitalization.
    Returns the filename for the created plot.
    """
    # ----- (Plot logic remains unchanged) -----
    sector_agg = (
        df_combined
        .groupby("Sector", as_index=False)["SumMarketCap"]
        .sum()
        .rename(columns={"SumMarketCap": "TotalSectorMcap"})
        .sort_values("TotalSectorMcap", ascending=False)
    )

    total_market_cap = sector_agg["TotalSectorMcap"].sum()
    sector_sizes = sector_agg["TotalSectorMcap"].values / \
        total_market_cap * (100 * 100)
    sector_names = sector_agg["Sector"].values
    sector_rects = squarify.squarify(sector_sizes, 0, 0, 100, 100)

    min_chg = df_combined["WeightedDailyChange"].min()
    max_chg = df_combined["WeightedDailyChange"].max()

    light_red_to_red = LinearSegmentedColormap.from_list(
        "light_red_to_red", ["#FF0000", "#FFCCCC"]
    )
    light_green_to_strong_green = LinearSegmentedColormap.from_list(
        "light_green_to_strong_green", ["#CCFFCC", "#009900"]
    )

    norm_neg = mcolors.Normalize(vmin=min_chg, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_chg)

    fig, ax = plt.subplots(figsize=(10.8, 19.2))
    margin = 1
    ax.set_xlim(-margin, 100 + margin)
    ax.set_ylim(-margin, 103 + margin)
    ax.axis("off")

    for srect, sector_name in zip(sector_rects, sector_names):
        subdf = df_combined[df_combined["Sector"] == sector_name]

        sub_total_market_cap = subdf["SumMarketCap"].sum()
        sub_sizes = subdf["SumMarketCap"].values / \
            sub_total_market_cap * (srect["dx"] * srect["dy"])
        sub_rects = squarify.squarify(
            sub_sizes, srect["x"], srect["y"], srect["dx"], srect["dy"])

        for sbox, row in zip(sub_rects, subdf.itertuples()):
            chg_val = row.WeightedDailyChange
            if chg_val >= 0:
                color_rgba = light_green_to_strong_green(norm_pos(chg_val))
            else:
                color_rgba = light_red_to_red(norm_neg(chg_val))

            ax.add_patch(
                plt.Rectangle(
                    (sbox["x"], sbox["y"]), sbox["dx"], sbox["dy"],
                    facecolor=color_rgba, edgecolor="white"
                )
            )

            if sbox["dx"] * sbox["dy"] > 2:
                sym = row.BaseSymbol
                label_str = f"{sym}\n{chg_val:.2f}%"
                ax.text(
                    sbox["x"] + sbox["dx"] / 2,
                    sbox["y"] + sbox["dy"] / 2,
                    label_str,
                    ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white",
                    path_effects=[withStroke(linewidth=2, foreground="black")]
                )

        ax.add_patch(
            plt.Rectangle(
                (srect["x"], srect["y"]),
                srect["dx"],
                srect["dy"],
                fill=False,
                edgecolor="black",
                linewidth=2
            )
        )

    fig.suptitle(
        f"OMXS30: {datetime.now().strftime('%Y-%m-%d')}",
        fontsize=24, fontweight="bold", y=0.96
    )
    plt.tight_layout()

    plot_file = save_plot_with_date(fig, prefix="OMXS30_heatmap")
    plt.close()
    return plot_file


def plot_omxs30_sector_treemap(df_combined):
    """
    Create a treemap where each sector's area is proportional to its total market capitalization.
    Returns the filename for the created plot.
    """
    # ----- (Plot logic remains unchanged) -----
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patheffects import withStroke
    import squarify
    import matplotlib.colors as mcolors

    required_columns = {"Sector", "SumMarketCap", "WeightedDailyChange"}
    if not required_columns.issubset(df_combined.columns):
        missing_columns = required_columns - set(df_combined.columns)
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df_combined.empty:
        raise ValueError("The provided DataFrame is empty.")

    sector_agg = (
        df_combined
        .groupby("Sector", as_index=False)
        .agg({"SumMarketCap": "sum", "WeightedDailyChange": "mean"})
        .sort_values("SumMarketCap", ascending=False)
    )
    total_market_cap = sector_agg["SumMarketCap"].sum()
    if total_market_cap == 0:
        raise ValueError(
            "Total market capitalization is zero. Check the data for correctness.")

    sector_sizes = sector_agg["SumMarketCap"].values / \
        total_market_cap * (100 * 100)
    sector_names = sector_agg["Sector"].values
    sector_changes = sector_agg["WeightedDailyChange"].values
    sector_rects = squarify.squarify(sector_sizes, 0, 0, 100, 100)

    short_sector_names = {
        "Consumer Discretionary": "Cons. Disc.",
        "Consumer Staples": "Cons. Stap.",
        "Health Care": "Health",
        "Telecommunications": "Telecom",
        "Basic Materials": "Materials",
        "Financials": "Finance",
        "Industrials": "Industry",
        "Real Estate": "Real Est."
    }
    sector_names_short = [short_sector_names.get(
        name, name) for name in sector_names]

    min_chg = sector_agg["WeightedDailyChange"].min()
    max_chg = sector_agg["WeightedDailyChange"].max()

    light_red_to_red = LinearSegmentedColormap.from_list(
        "light_red_to_red", ["#FF0000", "#FFCCCC"]
    )
    light_green_to_strong_green = LinearSegmentedColormap.from_list(
        "light_green_to_strong_green", ["#CCFFCC", "#009900"]
    )

    norm_neg = mcolors.Normalize(vmin=min_chg, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_chg)

    fig, ax = plt.subplots(figsize=(10.8, 19.2))
    margin = 1
    ax.set_xlim(-margin, 100 + margin)
    ax.set_ylim(-margin, 103 + margin)
    ax.axis("off")

    for srect, sector_name, sector_change in zip(sector_rects, sector_names_short, sector_changes):
        if sector_change >= 0:
            color_rgba = light_green_to_strong_green(norm_pos(sector_change))
        else:
            color_rgba = light_red_to_red(norm_neg(sector_change))

        ax.add_patch(
            plt.Rectangle(
                (srect["x"], srect["y"]), srect["dx"], srect["dy"],
                facecolor=color_rgba, edgecolor="black", linewidth=2
            )
        )

        font_size = max(
            13, min(18, int(srect["dx"] * srect["dy"] ** 0.5 / 40)))
        label_str = f"{sector_name}\n{sector_change:.2f}%"
        ax.text(
            srect["x"] + srect["dx"] / 2,
            srect["y"] + srect["dy"] / 2,
            label_str,
            ha="center", va="center",
            fontsize=font_size, fontweight="bold",
            color="white",
            path_effects=[withStroke(linewidth=2, foreground="black")]
        )

    fig.suptitle(
        f"OMXS30 Sectors: {datetime.now().strftime('%Y-%m-%d')}",
        fontsize=20, fontweight="bold", y=0.96
    )
    plt.tight_layout()

    plot_file = save_plot_with_date(fig, prefix="OMXS30_Sector_HeatMap")
    plt.show()
    return plot_file


def upload_plots_to_repo(folder="daily heatmap"):
    """
    Add and commit specific plot files to the Git repository.
    """
    today_date = datetime.now().strftime('%Y-%m-%d')
    expected_files = [
        f"{folder}/OMXS30_Sector_heatmap_{today_date}.png",
        f"{folder}/OMXS30_Sector_HeatMap_{today_date}.png"
    ]

    for file in expected_files:
        if not os.path.exists(file):
            print(f"Error: Expected plot not found: {file}")
            exit(1)

    print(f"All expected plots found: {expected_files}")

    for file in expected_files:
        result = subprocess.run(["git", "add", file],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error adding file {file}: {result.stderr}")
            exit(1)

    commit_message = f"Add daily plots for {today_date}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_message], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error committing changes: {result.stderr}")
        exit(1)

    result = subprocess.run(
        ["git", "push", "origin", "main"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error pushing changes: {result.stderr}")
        exit(1)

    print(f"Successfully committed and pushed daily plots for {today_date}")


def main():
    """
    Main function to:
    1) Prepare combined DataFrame.
    2) Generate both plots (stock-level heatmap & sector heatmap).
    3) Commit the generated plots to GitHub.
    """
    # Prepare data
    df_combined = prepare_combined_df()
    print(df_combined)

    # Generate two plots
    # "OMXS30_heatmap_YYYY-MM-DD_HH-MM-SS.png"
    plot_omxs30_treemap_instagram(df_combined)
    # "OMXS30_Sector_HeatMap_YYYY-MM-DD_HH-MM-SS.png"
    plot_omxs30_sector_treemap(df_combined)

    # Upload to repository (with existing date-based checks)
    upload_plots_to_repo(folder="daily heatmap")


if __name__ == "__main__":
    main()

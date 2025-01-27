# %%
import subprocess
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import squarify
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
from matplotlib.patheffects import withStroke
import os

# OMXS30 tickers information
# omxs30_info = [
#     {"SymbolYahoo": "ATCO-A.ST", "BaseSymbol": "ATCO", "Sector": "Industrials"},
#     {"SymbolYahoo": "ATCO-B.ST", "BaseSymbol": "ATCO", "Sector": "Industrials"},
#     {"SymbolYahoo": "ABB.ST",    "BaseSymbol": "ABB",  "Sector": "Industrials"},
#     {"SymbolYahoo": "AZN.ST",    "BaseSymbol": "AZN",  "Sector": "Healthcare"},
#     {"SymbolYahoo": "INVE-B.ST", "BaseSymbol": "INVE", "Sector": "Financials"},
#     {"SymbolYahoo": "VOLV-B.ST", "BaseSymbol": "VOLV", "Sector": "Industrials"},
#     {"SymbolYahoo": "NDA-SE.ST", "BaseSymbol": "NDA",  "Sector": "Financials"},
#     {"SymbolYahoo": "ASSA-B.ST", "BaseSymbol": "ASSA", "Sector": "Industrials"},
#     {"SymbolYahoo": "SEB-A.ST",  "BaseSymbol": "SEB",  "Sector": "Financials"},
#     {"SymbolYahoo": "ERIC-B.ST", "BaseSymbol": "ERIC", "Sector": "Technology"},
#     {"SymbolYahoo": "HEXA-B.ST", "BaseSymbol": "HEXA", "Sector": "Technology"},
#     {"SymbolYahoo": "SWED-A.ST", "BaseSymbol": "SWED", "Sector": "Financials"},
#     {"SymbolYahoo": "SAND.ST",   "BaseSymbol": "SAND", "Sector": "Industrials"},
#     {"SymbolYahoo": "SHB-A.ST",  "BaseSymbol": "SHB",  "Sector": "Financials"},
#     {"SymbolYahoo": "HM-B.ST",   "BaseSymbol": "HM",   "Sector": "Consumer Discretionary"},
#     {"SymbolYahoo": "ESSITY-B.ST","BaseSymbol": "ESSITY","Sector": "Consumer Staples"},
#     {"SymbolYahoo": "ALFA.ST",   "BaseSymbol": "ALFA", "Sector": "Industrials"},
#     {"SymbolYahoo": "EVO.ST",    "BaseSymbol": "EVO",  "Sector": "Technology"},
#     {"SymbolYahoo": "SAAB-B.ST", "BaseSymbol": "SAAB", "Sector": "Industrials"},
#     {"SymbolYahoo": "TELIA.ST",  "BaseSymbol": "TELIA","Sector": "Communication Services"},
#     {"SymbolYahoo": "SKF-B.ST",  "BaseSymbol": "SKF",  "Sector": "Industrials"},
#     {"SymbolYahoo": "SCA-B.ST",  "BaseSymbol": "SCA",  "Sector": "Materials"},
#     {"SymbolYahoo": "BOL.ST",    "BaseSymbol": "BOL",  "Sector": "Materials"},
#     {"SymbolYahoo": "NIBE-B.ST", "BaseSymbol": "NIBE", "Sector": "Industrials"},
#     {"SymbolYahoo": "TEL2-B.ST", "BaseSymbol": "TEL2", "Sector": "Communication Services"},
#     {"SymbolYahoo": "GETI-B.ST", "BaseSymbol": "GETI", "Sector": "Healthcare"},
#     {"SymbolYahoo": "ELUX-B.ST", "BaseSymbol": "ELUX", "Sector": "Consumer Discretionary"},
#     {"SymbolYahoo": "KINV-B.ST", "BaseSymbol": "KINV", "Sector": "Financials"},
#     {"SymbolYahoo": "SINCH.ST",  "BaseSymbol": "SINCH","Sector": "Technology"},
#     {"SymbolYahoo": "SBB-B.ST",  "BaseSymbol": "SBB",  "Sector": "Real Estate"}
# ]

omxs30_info = [
    {"SymbolYahoo": "ATCO-A.ST", "BaseSymbol": "ATCO", "Sector": "Industrials"},
    {"SymbolYahoo": "ATCO-B.ST", "BaseSymbol": "ATCO", "Sector": "Industrials"},
    {"SymbolYahoo": "ABB.ST",    "BaseSymbol": "ABB",  "Sector": "Industrials"},
    {"SymbolYahoo": "AZN.ST",    "BaseSymbol": "AZN",  "Sector": "Health Care"},
    {"SymbolYahoo": "INVE-B.ST", "BaseSymbol": "INVE", "Sector": "Financials"},
    {"SymbolYahoo": "VOLV-B.ST", "BaseSymbol": "VOLV", "Sector": "Industrials"},
    {"SymbolYahoo": "NDA-SE.ST", "BaseSymbol": "NDA",  "Sector": "Financials"},
    {"SymbolYahoo": "ASSA-B.ST", "BaseSymbol": "ASSA", "Sector": "Industrials"},
    {"SymbolYahoo": "SEB-A.ST",  "BaseSymbol": "SEB",  "Sector": "Financials"},
    {"SymbolYahoo": "ERIC-B.ST", "BaseSymbol": "ERIC",
        "Sector": "Telecommunications"},
    {"SymbolYahoo": "HEXA-B.ST", "BaseSymbol": "HEXA", "Sector": "Technology"},
    {"SymbolYahoo": "SWED-A.ST", "BaseSymbol": "SWED", "Sector": "Financials"},
    {"SymbolYahoo": "SAND.ST",   "BaseSymbol": "SAND", "Sector": "Industrials"},
    {"SymbolYahoo": "SHB-A.ST",  "BaseSymbol": "SHB",  "Sector": "Financials"},
    {"SymbolYahoo": "HM-B.ST",   "BaseSymbol": "HM",
        "Sector": "Consumer Discretionary"},
    {"SymbolYahoo": "ESSITY-B.ST", "BaseSymbol": "ESSITY",
        "Sector": "Consumer Staples"},
    {"SymbolYahoo": "ALFA.ST",   "BaseSymbol": "ALFA", "Sector": "Industrials"},
    {"SymbolYahoo": "EVO.ST",    "BaseSymbol": "EVO",  "Sector": "Technology"},
    {"SymbolYahoo": "SAAB-B.ST", "BaseSymbol": "SAAB", "Sector": "Industrials"},
    {"SymbolYahoo": "TELIA.ST",  "BaseSymbol": "TELIA",
        "Sector": "Telecommunications"},
    {"SymbolYahoo": "SKF-B.ST",  "BaseSymbol": "SKF",  "Sector": "Industrials"},
    {"SymbolYahoo": "SCA-B.ST",  "BaseSymbol": "SCA",  "Sector": "Basic Materials"},
    {"SymbolYahoo": "BOL.ST",    "BaseSymbol": "BOL",  "Sector": "Basic Materials"},
    {"SymbolYahoo": "NIBE-B.ST", "BaseSymbol": "NIBE", "Sector": "Industrials"},
    {"SymbolYahoo": "TEL2-B.ST", "BaseSymbol": "TEL2",
        "Sector": "Telecommunications"},
    {"SymbolYahoo": "GETI-B.ST", "BaseSymbol": "GETI", "Sector": "Health Care"},
    {"SymbolYahoo": "ELUX-B.ST", "BaseSymbol": "ELUX",
        "Sector": "Consumer Discretionary"},
    {"SymbolYahoo": "KINV-B.ST", "BaseSymbol": "KINV", "Sector": "Financials"},
    {"SymbolYahoo": "SINCH.ST",  "BaseSymbol": "SINCH", "Sector": "Technology"},
    {"SymbolYahoo": "SBB-B.ST",  "BaseSymbol": "SBB",  "Sector": "Real Estate"}
]


# Step 1: Fetch data and calculate market capitalization
data = []

for symbol in [info["SymbolYahoo"] for info in omxs30_info]:
    try:
        print(f"Fetching data for {symbol}...")
        stock = yf.Ticker(symbol)
        info = stock.info  # Retrieve company information

        # Extract market cap and daily percentage change
        market_cap = info.get("marketCap", None)  # Market capitalization
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

df_pct_change = pd.DataFrame(data)

# Step 2: Merge `df_pct_change` with `omxs30_info`
df_info = pd.DataFrame(omxs30_info)
df_combined = pd.merge(df_info, df_pct_change,
                       left_on="SymbolYahoo", right_on="Symbol", how="left")

# # Step 3: Assign MarketCap and WeightedDailyChange
# df_combined["SumMarketCap"] = df_combined["MarketCap"]
# df_combined["WeightedDailyChange"] = df_combined["PctChange"]

# # Step 4: Combine duplicate companies (e.g., ATCO-A and ATCO-B)
# # Group by `BaseSymbol` and `Sector`, then aggregate `SumMarketCap` and `WeightedDailyChange`
# df_combined = (
#     df_combined
#     .groupby(["BaseSymbol", "Sector"], as_index=False)
#     .agg({
#         "SumMarketCap": "sum",  # Sum market caps
#         "WeightedDailyChange": "mean",  # Average percentage change
#     })
# )

# # Print the updated DataFrame
# print(df_combined)

# Step 3: Assign MarketCap and WeightedDailyChange
df_combined["SumMarketCap"] = df_combined["MarketCap"]
df_combined["WeightedDailyChange"] = df_combined["PctChange"]

# Step 4: Combine duplicate companies (e.g., ATCO-A and ATCO-B)
# Group by `BaseSymbol` and `Sector`, then aggregate `SumMarketCap` and `WeightedDailyChange`
df_combined = (
    df_combined
    .groupby(["BaseSymbol", "Sector"], as_index=False)
    .agg({
        "SumMarketCap": "sum",  # Sum market caps
        "WeightedDailyChange": "mean",  # Average percentage change
    })
)

# Assign a temporary market cap if it's missing or zero
df_combined["SumMarketCap"] = df_combined["SumMarketCap"].replace(0, 1e9)

# Print the updated DataFrame for debugging
print(df_combined)

# %%
# Step 3: Simulate MarketCap and WeightedDailyChange for demonstration purposes
print(df_combined.columns)

# %% [markdown]
# ## Fixing heatmap size for each company

# %%


def save_plot_with_date(fig, prefix, folder="daily heatmap"):
    """
    Save the plot with a unique filename based on the current date.

    Parameters:
    - fig: The matplotlib figure object to save.
    - prefix: A string prefix for the filename (e.g., 'OMXS30_Treemap').
    - folder: The directory where the plot should be saved (default is 'daily heatmap').
    """
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Generate the filename with the current date
    today_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"{folder}/{prefix}_{today_date}.png"

    # Save the figure
    fig.savefig(filename, dpi=800, bbox_inches="tight")
    print(f"Plot saved as {filename}")
    return filename


def plot_omxs30_treemap_instagram(df_combined):
    """
    Create a treemap where each company's area is proportional to its market capitalization.
    """
    # Aggregate sector market caps for top-level rectangles
    sector_agg = (
        df_combined
        .groupby("Sector", as_index=False)["SumMarketCap"]
        .sum()
        .rename(columns={"SumMarketCap": "TotalSectorMcap"})
        .sort_values("TotalSectorMcap", ascending=False)
    )

    # Normalize sector sizes to fit within the plot bounds
    total_market_cap = sector_agg["TotalSectorMcap"].sum()
    sector_sizes = sector_agg["TotalSectorMcap"].values / \
        total_market_cap * (100 * 100)
    sector_names = sector_agg["Sector"].values
    sector_rects = squarify.squarify(sector_sizes, 0, 0, 100, 100)

    # Find min and max change for coloring
    min_chg = df_combined["WeightedDailyChange"].min()
    max_chg = df_combined["WeightedDailyChange"].max()

    # Two custom gradients: red-ish for negative, green-ish for positive
    light_red_to_red = LinearSegmentedColormap.from_list(
        "light_red_to_red", ["#FF0000", "#FFCCCC"]
    )
    light_green_to_strong_green = LinearSegmentedColormap.from_list(
        "light_green_to_strong_green", ["#CCFFCC", "#009900"]
    )

    # Normalizers for negative and positive changes
    norm_neg = mcolors.Normalize(vmin=min_chg, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_chg)

    # Create figure and axis
    # Square figure for balanced treemap
    fig, ax = plt.subplots(figsize=(10.8, 19.2))

    # Add margins
    margin = 1
    ax.set_xlim(-margin, 100 + margin)
    ax.set_ylim(-margin, 103 + margin)
    ax.axis("off")

    # Main loop: each sector is subdivided into stocks
    for srect, sector_name in zip(sector_rects, sector_names):
        subdf = df_combined[df_combined["Sector"] == sector_name]

        # Normalize company sizes within the sector to fit its allocated area
        sub_total_market_cap = subdf["SumMarketCap"].sum()
        sub_sizes = subdf["SumMarketCap"].values / \
            sub_total_market_cap * (srect["dx"] * srect["dy"])
        sub_rects = squarify.squarify(
            sub_sizes, srect["x"], srect["y"], srect["dx"], srect["dy"]
        )

        # Plot each stock rectangle
        for sbox, row in zip(sub_rects, subdf.itertuples()):
            chg_val = row.WeightedDailyChange
            # Decide which colormap (negative or positive)
            if chg_val >= 0:
                color_rgba = light_green_to_strong_green(norm_pos(chg_val))
            else:
                color_rgba = light_red_to_red(norm_neg(chg_val))

            # Draw rectangle
            ax.add_patch(
                plt.Rectangle(
                    (sbox["x"], sbox["y"]), sbox["dx"], sbox["dy"],
                    facecolor=color_rgba, edgecolor="white"
                )
            )

            # Only add label if area is large enough
            if sbox["dx"] * sbox["dy"] > 2:  # Threshold for small areas
                sym = row.BaseSymbol
                # addign new line for percent
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

        # Draw sector-level bounding box with uniform line width
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

    # Add title and control its position
    fig.suptitle(
        f"OMXS30: {datetime.now().strftime('%Y-%m-%d')}",
        fontsize=24, fontweight="bold", y=0.96  # Use `y` to control vertical position
    )

    os.makedirs("daily heatmap", exist_ok=True)
    # Save and show plot
    plt.tight_layout()
    save_plot_with_date(fig, prefix="OMXS30_Sector_heatmap")
    plt.close()


plot_omxs30_treemap_instagram(df_combined)

# %% [markdown]
# ### Sector heatmap

# %%


def plot_omxs30_sector_treemap(df_combined):
    """
    Create a treemap where each sector's area is proportional to its total market capitalization,
    and the label shows the sector name and its average daily percentage change with a custom font.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patheffects import withStroke
    import squarify
    import matplotlib.colors as mcolors
    from matplotlib import rcParams
    from datetime import datetime

    # Ensure necessary columns exist
    required_columns = {"Sector", "SumMarketCap", "WeightedDailyChange"}
    if not required_columns.issubset(df_combined.columns):
        missing_columns = required_columns - set(df_combined.columns)
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Check for non-empty data
    if df_combined.empty:
        raise ValueError("The provided DataFrame is empty.")

    # Aggregate data by sector
    sector_agg = (
        df_combined
        .groupby("Sector", as_index=False)
        .agg({
            "SumMarketCap": "sum",  # Sum market caps
            "WeightedDailyChange": "mean",  # Average percentage change
        })
        .sort_values("SumMarketCap", ascending=False)
    )

    # Normalize sector sizes to fit within the plot bounds
    total_market_cap = sector_agg["SumMarketCap"].sum()
    if total_market_cap == 0:
        raise ValueError(
            "Total market capitalization is zero. Check the data for correctness.")

    sector_sizes = sector_agg["SumMarketCap"].values / \
        total_market_cap * (100 * 100)
    sector_names = sector_agg["Sector"].values
    sector_changes = sector_agg["WeightedDailyChange"].values
    sector_rects = squarify.squarify(sector_sizes, 0, 0, 100, 100)

    # Shorten sector names for clarity
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

    # Find min and max change for coloring
    min_chg = sector_agg["WeightedDailyChange"].min()
    max_chg = sector_agg["WeightedDailyChange"].max()

    # Two custom gradients: red-ish for negative, green-ish for positive
    light_red_to_red = LinearSegmentedColormap.from_list(
        "light_red_to_red", ["#FF0000", "#FFCCCC"]
    )
    light_green_to_strong_green = LinearSegmentedColormap.from_list(
        "light_green_to_strong_green", ["#CCFFCC", "#009900"]
    )

    # Normalizers for negative and positive changes
    norm_neg = mcolors.Normalize(vmin=min_chg, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_chg)

    # Create figure and axis
    # Adjusted size for better layout
    fig, ax = plt.subplots(figsize=(10.8, 19.2))

    # Add margins
    margin = 1
    ax.set_xlim(-margin, 100 + margin)
    ax.set_ylim(-margin, 103 + margin)
    ax.axis("off")

    # Specify custom font for sector names
    sector_font = "DejaVu Sans"

    # Plot each sector rectangle
    for srect, sector_name, sector_change in zip(sector_rects, sector_names_short, sector_changes):
        # Decide which colormap (negative or positive)
        if sector_change >= 0:
            color_rgba = light_green_to_strong_green(norm_pos(sector_change))
        else:
            color_rgba = light_red_to_red(norm_neg(sector_change))

        # Draw rectangle with a dark black frame
        ax.add_patch(
            plt.Rectangle(
                (srect["x"], srect["y"]), srect["dx"], srect["dy"],
                facecolor=color_rgba, edgecolor="black", linewidth=2
            )
        )

        # Increase font size for better visibility
        font_size = max(
            13, min(18, int(srect["dx"] * srect["dy"] ** 0.5 / 40)))

        # Add sector name and average percentage change
        label_str = f"{sector_name}\n{sector_change:.2f}%"
        ax.text(
            srect["x"] + srect["dx"] / 2,
            srect["y"] + srect["dy"] / 2,
            label_str,
            ha="center", va="center",
            fontsize=font_size, fontweight="bold",
            fontname=sector_font,  # Apply custom font
            color="white",
            path_effects=[withStroke(linewidth=2, foreground="black")]
        )

    # Add title and control its position
    fig.suptitle(
        f"OMXS30 Sectors: {datetime.now().strftime('%Y-%m-%d')}",
        fontsize=20, fontweight="bold", y=0.96
    )

    os.makedirs("daily heatmap", exist_ok=True)
    # Save and show plot
    plt.tight_layout()
    save_plot_with_date(fig, prefix="OMXS30_Sector_HeatMap")
    plt.show()


plot_omxs30_sector_treemap(df_combined)


def upload_plots_to_repo(folder="daily heatmap"):
    """
    Add and commit all PNG files in the specified folder to the Git repository.
    """
    # Ensure the folder exists
    if not os.path.exists(folder):
        print(f"Folder '{folder}' does not exist. No plots to upload.")
        return

    # Collect all PNG files in the folder
    plot_files = [os.path.join(folder, f)
                  for f in os.listdir(folder) if f.endswith(".png")]

    if not plot_files:
        print("No PNG files found to commit.")
        return

    # Add files to Git
    for plot in plot_files:
        subprocess.run(["git", "add", plot])

    # Commit message
    commit_message = f"Add daily plots for {
        datetime.now().strftime('%Y-%m-%d')}"

    # Commit and push changes
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push", "origin", "main"])


# %%

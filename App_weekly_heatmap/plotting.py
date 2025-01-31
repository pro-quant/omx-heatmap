import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patheffects import withStroke
import squarify
import os
from datetime import datetime
import matplotlib.colors as mcolors

import os
from datetime import datetime


def save_plot_with_week(fig, prefix, week_number, year=None, base_folder="App_weekly_heatmap", subfolder="weekly_heatmap"):
    """
    Save the plot with a filename based on the provided week number inside 'App_weekly_heatmap/weekly_heatmap/'.

    Parameters:
    - fig: The matplotlib figure object to save.
    - prefix: A string prefix for the filename (e.g., 'OMXS30_StockHeatmap').
    - week_number: The ISO week number provided by the user.
    - year: The year (defaults to the current year if not provided).
    - base_folder: The main directory where weekly heatmaps are stored.
    - subfolder: The subdirectory inside base_folder for weekly heatmaps.
    """
    if year is None:
        year = datetime.now().year

    # Full folder path: App_weekly_heatmap/weekly_heatmap/
    folder_path = os.path.join(base_folder, subfolder)
    os.makedirs(folder_path, exist_ok=True)

    # Generate the filename inside App_weekly_heatmap/weekly_heatmap/
    filename = f"{folder_path}/{prefix}_Week_{week_number}_{year}.png"

    # Save the figure
    fig.savefig(filename, dpi=800, bbox_inches="tight")
    print(f"Plot saved successfully at: {filename}")
    return filename


def plot_omxs30_treemap_instagram(df_combined, week_number, year=None):
    """
    Create a treemap where each company's area is proportional to its market capitalization.
    The file is saved with a week-based filename.

    Parameters:
    - df_combined: DataFrame containing OMXS30 stock data.
    - week_number: ISO week number provided by the user.
    - year: Year of the analysis (defaults to the current year).
    """
    if year is None:
        year = datetime.now().year

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

    # Define color gradients for gain/loss
    light_red_to_red = LinearSegmentedColormap.from_list(
        "light_red_to_red", ["#FF0000", "#FFCCCC"])
    light_green_to_strong_green = LinearSegmentedColormap.from_list(
        "light_green_to_strong_green", ["#CCFFCC", "#009900"])

    # Normalizers for negative and positive changes
    norm_neg = mcolors.Normalize(vmin=min_chg, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_chg)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10.8, 19.2))

    # Add margins and remove axis labels
    margin = 1
    ax.set_xlim(-margin, 100 + margin)
    ax.set_ylim(-margin, 103 + margin)
    ax.axis("off")

    # Loop through each sector and create stock rectangles
    for srect, sector_name in zip(sector_rects, sector_names):
        subdf = df_combined[df_combined["Sector"] == sector_name]

        # Normalize company sizes within the sector to fit its allocated area
        sub_total_market_cap = subdf["SumMarketCap"].sum()
        sub_sizes = subdf["SumMarketCap"].values / \
            sub_total_market_cap * (srect["dx"] * srect["dy"])
        sub_rects = squarify.squarify(
            sub_sizes, srect["x"], srect["y"], srect["dx"], srect["dy"])

        # Plot each stock rectangle
        for sbox, row in zip(sub_rects, subdf.itertuples()):
            chg_val = row.WeightedDailyChange

            # Choose color based on stock performance
            color_rgba = light_green_to_strong_green(
                norm_pos(chg_val)) if chg_val >= 0 else light_red_to_red(norm_neg(chg_val))

            # Draw the rectangle
            ax.add_patch(
                plt.Rectangle((sbox["x"], sbox["y"]), sbox["dx"],
                              sbox["dy"], facecolor=color_rgba, edgecolor="white")
            )

            # Only add labels if area is large enough
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

        # Draw sector-level bounding box
        ax.add_patch(
            plt.Rectangle(
                (srect["x"], srect["y"]), srect["dx"], srect["dy"], fill=False, edgecolor="black", linewidth=2
            )
        )

    # Add title with week number
    fig.suptitle(
        f"OMXS30 Week {week_number}, {year}",
        fontsize=24, fontweight="bold", y=0.876
    )

    # Save plot using week number
    save_plot_with_week(fig, prefix="OMXS30_Weekly_Heatmap",
                        week_number=week_number, year=year)

    plt.close()


def plot_omxs30_sector_treemap(df_combined, week_number, year=None):
    """
    Create a sector-level treemap where each sector's area is proportional to its total market capitalization.
    The file is saved using the specified week number.

    Parameters:
    - df_combined: DataFrame containing OMXS30 sector data.
    - week_number: ISO week number provided by the user.
    - year: Year of the analysis (defaults to the current year).
    """
    if year is None:
        year = datetime.now().year

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

    # Define color gradients for gain/loss
    light_red_to_red = LinearSegmentedColormap.from_list(
        "light_red_to_red", ["#FF0000", "#FFCCCC"])
    light_green_to_strong_green = LinearSegmentedColormap.from_list(
        "light_green_to_strong_green", ["#CCFFCC", "#009900"])

    # Normalizers for negative and positive changes
    norm_neg = mcolors.Normalize(vmin=min_chg, vmax=0)
    norm_pos = mcolors.Normalize(vmin=0, vmax=max_chg)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10.8, 19.2))

    # Add margins and remove axis labels
    margin = 1
    ax.set_xlim(-margin, 100 + margin)
    ax.set_ylim(-margin, 103 + margin)
    ax.axis("off")

    # Plot each sector rectangle
    for srect, sector_name, sector_change in zip(sector_rects, sector_names_short, sector_changes):
        # Choose color based on sector performance
        color_rgba = light_green_to_strong_green(norm_pos(
            sector_change)) if sector_change >= 0 else light_red_to_red(norm_neg(sector_change))

        # Draw sector rectangle
        ax.add_patch(
            plt.Rectangle((srect["x"], srect["y"]), srect["dx"], srect["dy"],
                          facecolor=color_rgba, edgecolor="black", linewidth=2)
        )

        # Adjust font size dynamically based on rectangle size
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
            color="white",
            path_effects=[withStroke(linewidth=2, foreground="black")]
        )

    # Add title with week number
    fig.suptitle(
        f"OMXS30 Sectors - Week {week_number}, {year}",
        fontsize=24, fontweight="bold", y=0.876
    )

    # Save plot using week number
    save_plot_with_week(fig, prefix="OMXS30_Sector_Weekly_Heatmap",
                        week_number=week_number, year=year)

    plt.close()

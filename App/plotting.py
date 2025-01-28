import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patheffects import withStroke
import squarify
import os
from datetime import datetime
import matplotlib.colors as mcolors


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
    save_plot_with_date(fig, prefix="OMXS30_heatmap")
    plt.close()


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

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

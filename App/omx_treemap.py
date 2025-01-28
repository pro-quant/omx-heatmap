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

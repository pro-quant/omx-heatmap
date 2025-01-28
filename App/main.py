from data_fetcher import fetch_data, prepare_data
from plotting import plot_omxs30_treemap_instagram, plot_omxs30_sector_treemap
from repo_utils import upload_plots_to_repo
from omx_symbols import omxs30_info
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    # Step 1: Fetch data
    df_pct_change = fetch_data(omxs30_info)

    # Step 2: Prepare data
    df_combined = prepare_data(df_pct_change, omxs30_info)

    # Step 3: Plot treemaps
    plot_omxs30_treemap_instagram(df_combined)
    plot_omxs30_sector_treemap(df_combined)

    # Step 4: Upload plots to repository
    upload_plots_to_repo()


if __name__ == "__main__":
    main()

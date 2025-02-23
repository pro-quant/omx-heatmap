# from data_fetcher import fetch_data, prepare_data
# from plotting import plot_omxs30_treemap_instagram, plot_omxs30_sector_treemap
# from repo_utils import upload_plots_to_repo
# from omx_symbols import omxs30_info
# import warnings
# from datetime import datetime

# warnings.filterwarnings("ignore", category=FutureWarning)


# week_number = 8
# year = 2025
# start_date = "2025-02-17"
# end_date = "2025-02-22"


# def main():
#     print(f"Fetching data for OMXS30 Week {week_number}, {
#           year} ({start_date} to {end_date})...\n")

#     # Step 1: Fetch data for the specified range
#     try:
#         df_pct_change = fetch_data(omxs30_info, start_date, end_date)
#         if df_pct_change.empty:
#             raise ValueError(
#                 "No stock data retrieved. Ensure Yahoo Finance is returning valid results.")
#     except Exception as e:
#         print(f"Error fetching data: {e}")
#         return

#     print("Fetched DataFrame:\n", df_pct_change.head())  # Debugging step

#     # Step 2: Prepare data
#     try:
#         df_combined = prepare_data(df_pct_change, omxs30_info)
#         if df_combined.empty:
#             raise ValueError(
#                 "No valid stock data after merging. Please check ticker symbols and date range.")
#     except Exception as e:
#         print(f"Error preparing data: {e}")
#         return

#     print("Prepared DataFrame:\n", df_combined.head())  # Debugging step

#     # Step 3: Plot treemaps with week number
#     try:
#         plot_omxs30_treemap_instagram(df_combined, week_number, year)
#         plot_omxs30_sector_treemap(df_combined, week_number, year)
#     except Exception as e:
#         print(f"Error plotting heatmaps: {e}")
#         return

#     # # Step 4: Upload plots to repository
#     # try:
#     #     upload_plots_to_repo(week_number, year)
#     # except Exception as e:
#     #     print(f"Error uploading plots: {e}")
#     #     return

#     print(f"Successfully completed heatmap generation and upload for Week {
#           week_number}, {year}.")


# if __name__ == "__main__":
#     main()


from data_fetcher import fetch_data, prepare_data
from plotting import plot_omxs30_treemap_instagram, plot_omxs30_sector_treemap
from repo_utils import upload_plots_to_repo
from omx_symbols import omxs30_info
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=FutureWarning)

week_number = 8
year = 2025
start_date = "2025-02-17"
end_date = "2025-02-22"


def main():
    # Step 1: Fetch data for the specified range
    try:
        df_pct_change = fetch_data(omxs30_info, start_date, end_date)
        if df_pct_change.empty:
            return
    except Exception:
        return

    # Step 2: Prepare data
    try:
        df_combined = prepare_data(df_pct_change, omxs30_info)
        if df_combined.empty:
            return
    except Exception:
        return

    # Step 3: Plot treemaps with week number
    try:
        plot_omxs30_treemap_instagram(df_combined, week_number, year)
        plot_omxs30_sector_treemap(df_combined, week_number, year)
    except Exception:
        return

    # # Step 4: Upload plots to repository
    # try:
    #     upload_plots_to_repo(week_number, year)
    # except Exception:
    #     return


if __name__ == "__main__":
    main()

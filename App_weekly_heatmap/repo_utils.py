import os
import subprocess
from datetime import datetime


def upload_plots_to_repo(week_number, year=None, base_folder="App_weekly_heatmap", subfolder="weekly_heatmap"):
    """
    Commit and push weekly plots to a Git repository.

    Parameters:
    - week_number (int): The ISO week number provided by the user.
    - year (int, optional): The year (defaults to the current year).
    - base_folder (str): The main directory where weekly heatmaps are stored.
    - subfolder (str): The subdirectory inside base_folder for weekly heatmaps.
    """
    if year is None:
        year = datetime.now().year

    # Full folder path: App_weekly_heatmap/weekly_heatmap/
    folder_path = os.path.join(base_folder, subfolder)

    # Expected files inside App_weekly_heatmap/weekly_heatmap/
    expected_files = [
        f"{folder_path}/OMXS30_Weekly_Heatmap_Week_{week_number}_{year}.png",
        f"{folder_path}/OMXS30_Sector_Weekly_Heatmap_Week_{week_number}_{year}.png",
    ]

    # Check if files exist before committing
    missing_files = [
        file for file in expected_files if not os.path.exists(file)]
    if missing_files:
        print(f"Error: Missing files: {', '.join(missing_files)}")
        return

    # Add, commit, and push the plots to the repository
    for file in expected_files:
        subprocess.run(["git", "add", file], check=True)

    subprocess.run(
        ["git", "commit", "-m", f"Add weekly plots for Week {week_number}, {year}"], check=True
    )
    subprocess.run(["git", "push", "origin", "main"], check=True)

    print(f"Successfully committed and pushed weekly plots for Week {
          week_number}, {year}")

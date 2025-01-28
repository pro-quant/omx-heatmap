import os
import subprocess
from datetime import datetime


def upload_plots_to_repo(folder="daily heatmap"):
    """
    Commit and push daily plots to a Git repository.
    """
    today_date = datetime.now().strftime('%Y-%m-%d')
    expected_files = [
        f"{folder}/OMXS30_heatmap_{today_date}.png",
        f"{folder}/OMXS30_Sector_HeatMap_{today_date}.png",
    ]

    for file in expected_files:
        if not os.path.exists(file):
            print(f"Error: Expected plot not found: {file}")
            return

    for file in expected_files:
        subprocess.run(["git", "add", file], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Add daily plots for {today_date}"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(f"Successfully committed and pushed daily plots for {today_date}")

import os
import glob
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# Slack Bot Token and Channel ID (replace with your own values)
SLACK_BOT_TOKEN = ""  # insert your slack bot token here
SLACK_CHANNEL_ID = ""  # insert your slack channel id here.

# Define the folder containing CSV files
CSV_FOLDER = "news"


def get_latest_csv(folder: str) -> str:
    """Find the latest CSV file in the folder."""
    csv_files = glob.glob(os.path.join(folder, "*_blacklisted.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the 'news' folder.")

    return max(csv_files, key=os.path.getmtime)  # Get the most recently modified file


def get_latest_text(folder: str) -> str:
    """Find the latest text file in the folder."""
    txt_files = glob.glob(os.path.join(folder, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No txt files found in the 'news' folder.")

    return max(txt_files, key=os.path.getmtime)  # Get the most recently modified file


def upload_to_slack(file_paths: list):
    """Uploads multiple files to Slack."""
    client = WebClient(token=SLACK_BOT_TOKEN)

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue  # Skip non-existent files

        try:
            response = client.files_upload_v2(
                channels=SLACK_CHANNEL_ID,
                file=file_path,
                title=os.path.basename(file_path),
                initial_comment="Here is today's table of competitor news and an AI summary of the contents",
            )
            print("File uploaded successfully:", response["file"]["permalink"])
        except SlackApiError as e:
            print(f"Error uploading file {file_path}: {e.response['error']}")


if __name__ == "__main__":
    try:
        files_to_upload = [get_latest_csv(CSV_FOLDER), get_latest_text(CSV_FOLDER)]
        upload_to_slack(files_to_upload)
    except Exception as e:
        print("Error:", e)

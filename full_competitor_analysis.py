# %%
from automatic_competitor_updates_functions import *
from automatic_competitor_updates import process_competitor_updates
from filter_through_llm import *
from send_news_to_slack import *
from move_news_to_legacy import move_news_files


# Web scraping and creation of Initial CSV.
process_competitor_updates(
    companies_file="companies_to_search.txt", output_folder="news", retries=3
)

# Process file through blacklist to remove unnecessary entries and process competitor news through LLM
process_competitor_news("blacklist.txt")

# Upload the relevant files to Slack
files_to_upload = [get_latest_csv("news"), get_latest_text("news")]
upload_to_slack(files_to_upload)

# move the now-uploaded news files to the legacy folder.
move_news_files()

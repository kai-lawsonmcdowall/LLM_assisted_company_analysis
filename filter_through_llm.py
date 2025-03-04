from datetime import datetime
import pandas as pd
import boto3
import json
import sys
import io
import os

# Initialize the Bedrock Runtime client with the specified region
bedrock_client = boto3.client("bedrock-runtime", region_name="eu-central-1")

CSV_FOLDER = "news"


def filter_blacklisted_rows(blacklist_filename: str):
    # Get the input CSV file from the "news" folder
    news_folder = "news"
    csv_files = [f for f in os.listdir(news_folder) if f.endswith(".csv")]

    if not csv_files:
        print("No CSV files found in the news folder.")
        return

    input_filename = os.path.join(news_folder, csv_files[0])
    output_filename = os.path.join(
        news_folder, csv_files[0].replace(".csv", "_blacklisted.csv")
    )

    # Load blacklist words
    with open(blacklist_filename, "r", encoding="utf-8") as f:
        blacklist = {word.strip().lower() for word in f if word.strip()}

    # Load CSV file
    df = pd.read_csv(input_filename, encoding="utf-8")

    # Filter rows that contain blacklisted words as substrings
    def row_contains_blacklist(row):
        return any(
            any(blackword in str(value).lower() for value in row)
            for blackword in blacklist
        )

    filtered_df = df[~df.apply(row_contains_blacklist, axis=1)]

    # Create a row column called "Source"
    filtered_df["Source"] = filtered_df["url"].str.extract(r"//([^/]+)")
    # Set as 3rd column
    filtered_df.insert(2, "Source", filtered_df.pop("Source"))

    # Save filtered data to a new CSV file
    filtered_df.to_csv(output_filename, index=False, encoding="utf-8")

    print(f"Filtered data saved to {output_filename}")


def read_csv_as_string(folder: str) -> str:
    """Reads the most recent csv file found in the specified folder and returns its content as a string."""
    for file in os.listdir(folder):
        if file.endswith("_blacklisted.csv"):
            file_path = os.path.join(folder, file)
            df = pd.read_csv(file_path)
            return df.to_csv(index=False)  # Convert DataFrame to CSV string
    raise FileNotFoundError("No CSV file found in the 'news' folder.")


def claude_sentiment_analysis(prompt, content: str = None):
    """
    Queries the Claude 3.5 Sonnet model hosted on Amazon Bedrock and returns a formatted response.

    :param prompt: The input prompt to send to Claude.
    :param content: Additional content to provide context.
    :return: The formatted model's response.
    """
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"  # Ensure this is the correct version

    # New payload format for Messages API
    payload = {
        "max_tokens": 1024,
        "system": "You are a biotech market analyst expert, your goal is to provide a detailed analysis of the facts relating to competitor data that is provided to you. Please talk specifically about the news and facts relating to each individual company",
        "messages": [
            {"role": "user", "content": content}
        ],  # Our prompt we want to give to Claude
        "anthropic_version": "bedrock-2023-05-31",
    }

    # Convert payload to JSON
    payload_json = json.dumps(payload)

    # Invoke Claude through Amazon Bedrock using the Messages API
    response = bedrock_client.invoke_model(modelId=model_id, body=payload_json)

    # Extract and decode response
    response_body = json.loads(response["body"].read().decode("utf-8"))

    # Beautify the text output
    text = response_body.get("content", [{"text": "No response received."}])[0]["text"]

    # Format the output with dividers
    formatted_output = f"\n{'=' * 60}\n{text}\n{'=' * 60}"

    return formatted_output  # Return the formatted output instead of printing


# parameters relating to sentiment analysis

print("creating blacklisted csv")
filter_blacklisted_rows("blacklist.txt")

sentiment_user_input = "You have been provided a table of information that contains the names of different companies, and recent news pertaining to their activities. as an expert in biotechnology and competitive analysis, please provide a concise yet informative summary of the news you are presented with, including key facts or headlines relating to these companies. I must emphasize however you must stick to the facts. Note that some rows in this table may not be relevant, use your expert judgement to ignore rows that do not related to biotech, for example, if the row contains Tik Tok on Instagram. Please also exclude non-english results."

print("reading in blacklisted csv")
content = read_csv_as_string(CSV_FOLDER)

result = claude_sentiment_analysis(prompt=sentiment_user_input, content=content)

# Get current date and time in the format YYYY_MM_DD_HH_MM_SS
timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
file_path = f"news/LLM_summary_competitor_news_{timestamp}.txt"

# Capture printed output
captured_output = io.StringIO()
sys.stdout = captured_output  # Redirect stdout

# Output
print(result)

# Reset stdout to default
sys.stdout = sys.__stdout__

# Get the captured text
output_text = captured_output.getvalue()

# Write the captured output to the file
with open(file_path, "w") as file:
    file.write(f"competitor news {timestamp}")
    file.write(output_text)

print(
    f"Output has been written to the file competitor_news_{timestamp} in the news folder"
)

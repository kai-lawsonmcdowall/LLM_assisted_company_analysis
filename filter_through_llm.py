from datetime import datetime
import pandas as pd
import boto3
import json
import sys
import io
import os
from typing import Optional

# Initialize the Bedrock Runtime client with the specified region
bedrock_client = boto3.client("bedrock-runtime", region_name="eu-central-1")

CSV_FOLDER = "news"


def filter_blacklisted_rows(blacklist_filename: str) -> Optional[str]:
    """
    Filters rows in the latest CSV file in the 'news' folder based on a blacklist.
    Returns the path of the filtered CSV file or None if no CSV file is found.
    """
    csv_files = [f for f in os.listdir(CSV_FOLDER) if f.endswith(".csv")]
    if not csv_files:
        print("No CSV files found in the news folder.")
        return None

    input_filename = os.path.join(CSV_FOLDER, csv_files[0])
    output_filename = os.path.join(
        CSV_FOLDER, csv_files[0].replace(".csv", "_blacklisted.csv")
    )

    with open(blacklist_filename, "r", encoding="utf-8") as f:
        blacklist = {word.strip().lower() for word in f if word.strip()}

    df = pd.read_csv(input_filename, encoding="utf-8")

    def row_contains_blacklist(row):
        return any(
            any(blackword in str(value).lower() for value in row)
            for blackword in blacklist
        )

    filtered_df = df[~df.apply(row_contains_blacklist, axis=1)]
    filtered_df["Source"] = filtered_df["url"].str.extract(r"//([^/]+)")
    filtered_df.insert(2, "Source", filtered_df.pop("Source"))

    filtered_df.to_csv(output_filename, index=False, encoding="utf-8")
    print(f"Filtered data saved to {output_filename}")

    return output_filename


def read_csv_as_string(file_path: str) -> str:
    """Reads a CSV file and returns its content as a string."""
    df = pd.read_csv(file_path)
    return df.to_csv(index=False)


def claude_sentiment_analysis(prompt: str, content: str) -> str:
    """
    Queries the Claude 3.5 Sonnet model hosted on Amazon Bedrock and returns a formatted response.
    """
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    payload = {
        "max_tokens": 1024,
        "system": "You are a biotech market analyst expert, your goal is to provide a detailed analysis of the facts relating to competitor data that is provided to you. Please talk specifically about the news and facts relating to each individual company",
        "messages": [{"role": "user", "content": content}],
        "anthropic_version": "bedrock-2023-05-31",
    }

    payload_json = json.dumps(payload)
    response = bedrock_client.invoke_model(modelId=model_id, body=payload_json)
    response_body = json.loads(response["body"].read().decode("utf-8"))

    text = response_body.get("content", [{"text": "No response received."}])[0]["text"]
    return f"\n{'=' * 60}\n{text}\n{'=' * 60}"


def process_competitor_news(blacklist_filename: str) -> None:
    """
    Wrapper function that executes the full competitor news filtering,
    sentiment analysis, and result saving process.
    """
    print("Creating blacklisted CSV...")
    filtered_csv = filter_blacklisted_rows(blacklist_filename)

    if not filtered_csv:
        print("No valid CSV to process.")
        return

    print("Reading in blacklisted CSV...")
    content = read_csv_as_string(filtered_csv)

    sentiment_user_input = (
        "You have been provided a table of information that contains the names..."
    )

    result = claude_sentiment_analysis(prompt=sentiment_user_input, content=content)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_path = f"news/LLM_summary_competitor_news_{timestamp}.txt"

    with open(file_path, "w") as file:
        file.write(f"competitor news {timestamp}\n")
        file.write(result)

    print(f"Output has been written to {file_path}")


# Example usage
if __name__ == "__main__":
    process_competitor_news("blacklist.txt")

import csv
from datetime import datetime
from automatic_competitor_updates_functions import *


def process_competitor_updates(
    companies_file: str, output_folder: str = "news", retries: int = 3
) -> None:
    """
    Processes competitor updates by reading company names, searching for updates, and saving results to CSV.

    Args:
        companies_file (str): Path to the text file containing company names.
        output_folder (str): Directory where the resulting CSV file will be saved.
        retries (int): Number of retry attempts for failed searches.

    Raises:
        FileNotFoundError: If the companies file is not found.
        Exception: For unexpected issues during processing.
    """
    try:
        # Read company names from companies.txt
        with open(companies_file, "r") as f:
            search_terms = [line.strip() for line in f.readlines()]

        # List to store all the results
        all_results = []
        failed_terms = []

        # Perform search with retries
        search_with_retries(search_terms, all_results, failed_terms, retries=retries)

        # Export results to CSV
        header = ["company", "released", "title", "url", "description"]
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"{output_folder}/competitor_news_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(all_results)

        # Log failed terms
        if failed_terms:
            with open("failed_terms.txt", "w") as f:
                for term in failed_terms:
                    f.write(f"{term}\n")
            print(
                f"Failed to process the following terms after retries: {failed_terms}"
            )

        print(f"Results saved to {filename}")

    except FileNotFoundError:
        print(f"Error: The file '{companies_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

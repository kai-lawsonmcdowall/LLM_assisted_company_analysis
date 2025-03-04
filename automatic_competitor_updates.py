import csv
import time
from datetime import datetime
from automatic_competitor_updates_functions import *


# Read company names from companies.txt
with open("companies.txt", "r") as f:
    search_terms = [line.strip() for line in f.readlines()]

# List to store all the results
all_results = []
failed_terms = []

search_with_retries(search_terms, all_results, failed_terms, retries=3)

# Export results to CSV
header = ["company", "released", "title", "url", "description"]
timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = f"news/competitor_news_{timestamp}.csv"

with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(all_results)

# Log failed terms
if failed_terms:
    with open("failed_terms.txt", "w") as f:
        for term in failed_terms:
            f.write(f"{term}\n")
    print(f"Failed to process the following terms after retries: {failed_terms}")

### LLM assisted company analysis

This project is designed to perform web-scraping of google via selenium for relevant on biotech companies (However, this could be modified to be anything) Followed by passing these results through a large-language model (in this case, the foundation model is anthropic.claude-3-5-sonnet), to provide and output analysis of these data, and optionally provide to this to a slack channel (If for example, you wanted to share these results)

#### Workflow

The idea behind this project is to allow an automated analysis and updating of competitors, clients, investors, portfolio companies, or other organizations of interest. It does so by performing web scraping of terms in the companies_to_search.txt, creating a table/csv of web-scraped results from the last 24 hours, this looks like so:

| Company  | Released      | Title                                               | URL                                                                 | Description |
|----------|-------------|-----------------------------------------------------|---------------------------------------------------------------------|-------------|
| Dnanexus | 7 hours ago  | Digital Health Market Dynamics: How AI and mHealth are ... | [Link](https://www.openpr.com/news/3873354/digital-health-market-dynamics-how-ai-and-mhealth-are-reshaping) | Accelerated by the COVID-19 pandemic, telehealth adoption, remote patient monitoring, and wearable technologies are key drivers propelling the market forward. |
| Velsera  | 17 hours ago | Layoff Tracker: Kojin Will Soon Close Its Doors, Affecting ... | [Link](https://www.biospace.com/biospace-layoff-tracker) | Approximately 50% of the company's employees will be affected by the layoffs, mostly those working in its field force, the biotech revealed in its news release. |
| Velsera  | 41 minutes ago | Fierce Biotech News & Reports | [Link](https://www.fiercebiotech.com/) | Fierce Biotech recounts the top 10 clinical trial failures of 2024 that sent ripples across the industry. James Waldron Feb 18, 2025 3:00am. |

From here, this table is then filtered through the blacklist to remove non-relevant entries (the csv is filtered to remove rows which contain any of these terms). From here, the blacklisted csv is passed through our foundational model, which is provided a prompt along the lines of: 

```
"You have been provided a table of information that contains the names of different companies, and recent news pertaining to their activities. as an expert in biotechnology and competitive analysis, please provide a concise yet informative summary of the news you are presented with, including key facts or headlines relating to these companies. I must emphasize however you must stick to the facts. Note that some rows in this table may not be relevant, use your expert judgement to ignore rows that do not related to biotech, for example, if the row contains Tik Tok on Instagram. Please also exclude non-english results."
```
This will provide an analysis, like so: 

```
Tempus:
- Stock soared over 160% following acquisition of Ambry Genetics for $600 million
- Launching new AI assistant called Tempus One to support clinical decision-making
Evotec:
- Received grant from Korean government to develop novel antibody treatments for lung diseases
- Reported record financial results for 2024, but sees uncertainty in 2025 outlook
```


It will then generate a text file (the CSV, blacklisted CSV, and LLM-filtered text file are generated in the folder called `news`). Lastly, assuming that you want to share these findings with others, there is the option of publishing these results to slack (the filtered csv and LLM-generated text). After which, these 3 files are moved to legacy news, and the process above can be repeated.

#### Pre-requisites.

- Create the conda environment with the relevant packages using `conda env create --file=environment.yml`. This should create a conda environment called `LLM_assisted_company_analysis`. Then activate this conda environment using `conda activate LLM_assisted_company_analysis`.
  &nbsp;

- Update the `companies_to_search.txt` file with the companies, organisations, or entities you wish to search for. In parallel, update your `blacklist.txt` file. Due to the imperfect nature of web-scraping, returning search results that are always relevant is more of an art than science. However, when the first part of the pipeline has run, it will generate a csv with relevant information. The blacklist will filter this CSV for keywords you want to exclude. The LLM prompt has also been engineered to try and avoid non-essential information.
  &nbsp;

- Access to Amazon bedrock and the foundation models on it. A core component of this pipeline is analysis using an LLM. In order to successfully do this, I have used the claude 3.5 from Sonnet to perform this analysis. However, if you have the technical expertise, you may wish to use a different foundation model or even cloud platform to do so. You will also need to make sure you have relevant aws credentials locally (i.e. your Access Key, Secret Access Key ID, potentially session token, and make sure you region is set correctly). Make sure to update your region in the `filter_through_llm.py` script
  &nbsp;

- _(Optional)_ - A slack channel ID and a slack bot token. These are required to send the csv generated by the webscraping and analysis by the LLM to a slack channel of interest. Update these in the `send_news_to_slack.py` script
  &nbsp;

- _(Optional)_ Create a cronjob that allows execution of this every day, to make sure you have daily updates on the companies in the `companies_to_search.txt`. If you are using Ubuntu, for instance, you can follow [this guide](https://askubuntu.com/questions/2368/how-do-i-set-up-a-cron-job) to set up a cron job
  &nbsp;


#### To-do 

- Create a params.json which can allow several of the parameters to be coalesced into one place and allow optionality (e.g. to publish or not publish to slack)

- Ensure that I have updated the Slack API publishing to the newest version (as Slack was generating warnings about this being potentially deprecated)

- Additional performance boosting on the LLM (e.g. implementation of agent)
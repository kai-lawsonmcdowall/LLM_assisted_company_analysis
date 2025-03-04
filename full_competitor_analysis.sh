echo "scraping the web"
python automatic_competitor_updates.py

echo "adding llm interpretation"
python filter_through_llm.py

echo "sending news to slack channel" 
python send_news_to_slack.py

echo "moving news to legacy"
bash move_news_to_legacy.sh
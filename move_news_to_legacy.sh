#!/bin/bash

# Define source and destination folders
SOURCE_DIR="news"
DEST_DIR="legacy_news"

# Create the destination folder if it doesn't exist
mkdir -p "$DEST_DIR"

# Move all CSV files from news to legacy_news
mv "$SOURCE_DIR"/*.csv "$DEST_DIR"/ 2>/dev/null

mv "$SOURCE_DIR"/*.txt "$DEST_DIR"/ 2>/dev/null

# Check if the move was successful
if [ $? -eq 0 ]; then
    echo "All CSV files have been moved to $DEST_DIR."
else
    echo "No CSV files found in $SOURCE_DIR or an error occurred."
fi

# Event Discovery & Tracking Tool

This project is a Python-based automation tool that extracts upcoming events from BookMyShow for a selected city and stores them in Excel.

## Features
- Extracts event name, date, venue, city, category, and URL
- Updates existing events
- Marks expired events
- Excel-based storage
- Automation-ready

## Tech Stack
- Python
- Selenium
- Pandas
- Excel

## How to Run
1. Install dependencies:
   pip install -r requirements.txt
2. Run the script:
   python event_tracker.py

## Notes
- Uses Selenium due to JavaScript-rendered content on BookMyShow

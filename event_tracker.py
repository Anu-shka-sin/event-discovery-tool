from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime
import time
import os


CITY = "jaipur"   
URL = f"https://in.bookmyshow.com/explore/events-{CITY}"
EXCEL_FILE = "events_data.xlsx"
MIN_EVENTS = 6    

def fetch_events():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(10)  

    print("Page title:", driver.title)

    events = []

    # Find containers having event titles
    cards = driver.find_elements(By.XPATH, "//div[.//h3]")
    print(f"Cards found: {len(cards)}")

    for card in cards:
        if len(events) >= MIN_EVENTS:
            break   

        try:
            name = card.find_element(By.TAG_NAME, "h3").text.strip()

            spans = card.find_elements(By.TAG_NAME, "span")
            date = spans[0].text.strip() if len(spans) > 0 else "Unknown"
            venue = spans[-1].text.strip() if len(spans) > 1 else "Unknown"

            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

            
            if not name or not link:
                continue

            events.append({
                "Event Name": name,
                "Date": date,
                "Venue": venue,
                "City": CITY.capitalize(),
                "Category": "Event",
                "URL": link,
                "Status": "Upcoming",
                "Last Updated": datetime.now().strftime("%Y-%m-%d")
            })

        except:
            continue

    driver.quit()
    return events


def load_existing_data():
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Event Name", "Date", "Venue", "City",
            "Category", "URL", "Status", "Last Updated"
        ])


def update_events(new_events, existing_df):
    new_df = pd.DataFrame(new_events)
    combined = pd.concat([existing_df, new_df], ignore_index=True)

    # Remove duplicates using URL
    combined.drop_duplicates(subset=["URL"], keep="last", inplace=True)

    today = datetime.now().date()

    for i, row in combined.iterrows():
        try:
            event_date = pd.to_datetime(row["Date"], errors="coerce")
            if pd.notna(event_date) and event_date.date() < today:
                combined.at[i, "Status"] = "Expired"
        except:
            pass

    return combined


def main():
    print("Fetching events using Selenium...")
    events = fetch_events()

    if len(events) < MIN_EVENTS:
        print("Warning: Less than 6 events fetched.")

    existing_df = load_existing_data()
    final_df = update_events(events, existing_df)

    final_df.to_excel(EXCEL_FILE, index=False)
    print("Excel updated successfully!")

    
    os.startfile(EXCEL_FILE)


if __name__ == "__main__":
    main()

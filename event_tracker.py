from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime
import time

CITY = "mumbai"
URL = f"https://in.bookmyshow.com/explore/events-{CITY}"
EXCEL_FILE = "events_data.xlsx"

def fetch_events():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(10)  # IMPORTANT: allow full JS render

    print("Page title:", driver.title)

    events = []

    # BookMyShow event cards
    cards = driver.find_elements(By.XPATH, "//div[.//h3]")

    print(f"Cards found: {len(cards)}")

    for card in cards:
        try:
            name = card.find_element(By.TAG_NAME, "h3").text.strip()

            spans = card.find_elements(By.TAG_NAME, "span")
            date = spans[0].text.strip() if len(spans) > 0 else "Unknown"
            venue = spans[-1].text.strip() if len(spans) > 1 else "Unknown"

            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

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
    combined = pd.concat([existing_df, new_df])

    combined.drop_duplicates(subset=["URL"], keep="last", inplace=True)

    today = datetime.now().date()

    for i, row in combined.iterrows():
        try:
            event_date = pd.to_datetime(row["Date"]).date()
            if event_date < today:
                combined.at[i, "Status"] = "Expired"
        except:
            pass

    return combined

def main():
    print("Fetching events using Selenium...")
    events = fetch_events()

    if not events:
        print("No events fetched.")
        return

    existing_df = load_existing_data()
    final_df = update_events(events, existing_df)

    final_df.to_excel(EXCEL_FILE, index=False)
    print("Excel updated successfully!")

if __name__ == "__main__":
    main()

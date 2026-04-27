"""
You are given access to the GNews API (free tier at gnews.io). Build a complete automated data pipeline that answers the following questions:

Which country out of Nepal, India, USA, UK and Australia published the most headlines today?
What is the average number of words in a headline title — per country?
Are there any headlines that appeared in more than one country? If yes, which ones?
Which news source published the most headlines across all 5 countries combined?
What percentage of all headlines were published in the last 6 hours vs older than 6 hours?
If you run your script twice, does your database end up with duplicate rows? How did you prevent that?
Save only headlines with a title longer than 6 words to a CSV. How many passed that filter?
Which country had the longest headline on average — and which had the shortest?

Rules:
All fetched data must be saved to a CSV file first — answer every question by reading from that CSV, not from the API response directly
CSV must have clean column names — no spaces, all lowercase
If a field is missing from the API response, write "N/A" — never leave a cell empty
Running the script twice must not create duplicate rows in the CSV
"""

# Import necessary libraries
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Fetch API URL and key from environment variables
url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")

# Define the countries to fetch news for
COUNTRIES = {
    "np" : "Nepal",
    "in" : "India",
    "us" : "USA",
    "gb" : "UK",
    "au" : "Australia"
}

CSV_FILE = "news_data.csv"

# Function to fetch news data from GNews API
def fetch_news(country_code):
    params = {
        "country": country_code,
        "token": api_key,
        "max": 100  # Fetch up to 100 headlines per country
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {COUNTRIES[country_code]}: {e}")
        return []
    
# Function to clean data articles
def clean_articles(article, country):
    return {
        "title": article.get("title", "N/A"),
        "description": article.get("description", "N/A"),
        "published_at": article.get("publishedAt", "N/A"),
        "source": article.get("source", {}).get("name", "N/A"),
        "url": article.get("url", "N/A"),
        "country": country
    }

# Load existing data if CSV exists
def load_existing_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["title", "description", "published_at", "source", "url", "country"])

# Save data to CSV without duplicates
def save_data(data):
    existing_data = load_existing_data()
    new_data = pd.DataFrame(data)
    combined_data = pd.concat([existing_data, new_data])
    combined_data.drop_duplicates(subset=["title", "source"], inplace=True)
    combined_data.to_csv(CSV_FILE, index=False)
    return combined_data

# Function to run the data pipeline
def run_pipeline():
    all_articles = []
    for code, country in COUNTRIES.items():
        articles = fetch_news(code)
        time.sleep(2)  # wait 2 seconds
        for a in articles:
            cleaned = clean_articles(a, country)
            all_articles.append(cleaned)
    df = save_data(all_articles)
    return df

# Main execution
if __name__ == "__main__":
    news_df = run_pipeline()
    print(f"Total unique headlines saved: {len(news_df)}")
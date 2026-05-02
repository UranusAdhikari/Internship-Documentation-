"""
Task 05 · The Full System [Hard — Capstone]

Bring everything together — Weeks 1, 2, and 3 in one script

Goal  
Build a complete automated data system — fetch, store, analyse, and export. No manual steps.

Flow:
Fetch API → Error handle → Store MySQL → Analyse → Export(csv+text)

Must:
- Fetch data from any public API with error handling
- Store ALL fetched data in a properly structured MySQL database
- Run at least 3 meaningful SQL queries and print results with labels
- Export query results to a CSV file (combine Week 1 + Week 3)
- Handle errors at every step — API, database, file

Should:
- Write reusable functions: fetch_data(), store_data(), run_report()

Bonus:
- Schedule it: run the whole thing every time you run the script fresh
"""

import requests
import mysql.connector
import pandas as pd
import os, time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Fetch API URL and key from environment variables
url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")

# Define the countries to fetch news for
COUNTRIES = {
    "np" : "Nepal",
    "in" : "India",
    "us" : "USA"
}

# Define MySQL connection =
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cursor = conn.cursor()
    print("Connected to MySQL database successfully!")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)
    
# Create database and table
cursor.execute("CREATE DATABASE IF NOT EXISTS news_db")
cursor.execute("USE news_db")
cursor.execute("DROP TABLE IF EXISTS articles") # Start with a clean slate each time

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    description TEXT,
    content TEXT,
    url TEXT,
    lang VARCHAR(10),
    source_name VARCHAR(255),
    source_url TEXT,
    country VARCHAR(10),
    published_at DATETIME
)
""")

# Function to fetch news data from API
def fetch_news():
    all_articles = []
    for country_code in COUNTRIES.keys():
        time.sleep(2)  # wait 2 seconds between requests
        params = {
            "apikey": api_key,
            "country": country_code
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            # all_articles.extend(data.get("data", []))  # Add articles to the list
            # FIXED HERE
            for article in data.get("articles", []):
                all_articles.append((article, country_code))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for {COUNTRIES[country_code]}: {e}")
    
    return all_articles

# function to clean and prepare data for MySQL insertion
def clean_article(article):
    # Fix datetime format
    raw_date = article.get("publishedAt")
    try:
        published_at = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ") if raw_date else None
    except Exception:
        published_at = None
    return {
        "id": article.get("id"),  # FIXED (NOT uuid)
        "title": article.get("title", "N/A"),
        "description": article.get("description", "N/A"),
        "content": article.get("content", "N/A"),
        "url": article.get("url", "N/A"),
        "lang": article.get("lang", "N/A"),
        "source_name": article.get("source", {}).get("name", "N/A"),
        "source_url": article.get("source", {}).get("url", "N/A"),
        "published_at": published_at
    }

# Function to store news data in MySQL without duplicates
def store_news(articles):
    for raw_article, country_code in articles:
        article = clean_article(raw_article)   # ✅ USE CLEAN FUNCTION

        try:
            cursor.execute("""
            INSERT INTO articles 
            (id, title, description, content, url, lang, source_name, source_url, country, published_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                description = VALUES(description),
                content = VALUES(content),
                url = VALUES(url),
                lang = VALUES(lang),
                source_name = VALUES(source_name),
                source_url = VALUES(source_url),
                country = VALUES(country),
                published_at = VALUES(published_at)
            """, (
                article["id"],                
                article["title"],
                article["description"],
                article["content"],
                article["url"],
                article["lang"],
                article["source_name"],       # ✅ cleaned
                article["source_url"],        # ✅ cleaned
                country_code,
                article["published_at"]       # ✅ fixed datetime
            ))

        except mysql.connector.Error as err:
            print(f"Error inserting article {article['id']}: {err}")

    conn.commit()
# Close MySQL connection
def close_connection():
    cursor.close()
    conn.close()

# save to CSV without duplicates
def export_to_csv():
    try:
        df = pd.read_sql("SELECT * FROM articles", conn) # ✅ FIXED: use SQL query to get data from MySQL
        df.drop_duplicates(subset=["id"], inplace=True) # ✅ Remove duplicates based on '
        df.to_csv("news_data.csv", index=False)
        print("Data exported to news_data.csv successfully!")
    except Exception as e:
        print(f"Error exporting data to CSV: {e}")

# Main flow
if __name__ == "__main__":
    articles = fetch_news()
    store_news(articles)
    export_to_csv()
    close_connection()
    print("Done: News fetched and stored successfully.")
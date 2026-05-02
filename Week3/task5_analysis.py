import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to DB
try:
    conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database="news_db"
        )
    cursor = conn.cursor()
    print("Connected to MySQL database successfully!")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)



# Function to run queries and collect results
def run_analysis():
    results = []

    # 1. Articles per country
    cursor.execute("""
        SELECT country, COUNT(*) 
        FROM articles 
        GROUP BY country
    """)
    country_data = cursor.fetchall()
    results.append("Articles per country:")
    for row in country_data:
        results.append(f"{row[0]}: {row[1]}")

    # 2. Top 5 sources
    cursor.execute("""
        SELECT source_name, COUNT(*) as total
        FROM articles
        GROUP BY source_name
        ORDER BY total DESC
        LIMIT 5
    """)
    source_data = cursor.fetchall()
    results.append("\nTop 5 news sources:")
    for row in source_data:
        results.append(f"{row[0]}: {row[1]} articles")

    # 3. Latest 5 articles
    cursor.execute("""
        SELECT title, country, published_at
        FROM articles
        ORDER BY published_at DESC
        LIMIT 5
    """)
    latest_data = cursor.fetchall()
    results.append("\nLatest 5 articles:")
    for row in latest_data:
        results.append(f"{row[0]} ({row[1]}) - {row[2]}")

    # 4. Articles per language
    cursor.execute("""
        SELECT lang, COUNT(*)
        FROM articles
        GROUP BY lang
    """)
    lang_data = cursor.fetchall()
    results.append("\nArticles per language:")
    for row in lang_data:
        results.append(f"{row[0]}: {row[1]}")

    # 5. Oldest and newest article
    cursor.execute("""
        SELECT MIN(published_at), MAX(published_at)
        FROM articles
    """)
    time_data = cursor.fetchone()
    results.append("\nTime range:")
    results.append(f"Oldest: {time_data[0]}")
    results.append(f"Newest: {time_data[1]}")

    return results


# Save to summary_5.txt
def save_summary(results):
    with open("summary_5.txt", "w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")

    print("Summary saved to summary_5.txt")


# MAIN
if __name__ == "__main__":
    analysis_results = run_analysis()

    # Print to console
    print("\n--- ANALYSIS REPORT ---")
    for line in analysis_results:
        print(line)

    # Save to file
    save_summary(analysis_results)

    cursor.close()
    conn.close()
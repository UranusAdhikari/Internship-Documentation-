"""
Which country out of Nepal, India, USA, UK and Australia published the most headlines today?
What is the average number of words in a headline title — per country?
Are there any headlines that appeared in more than one country? If yes, which ones?
Which news source published the most headlines across all 5 countries combined?
What percentage of all headlines were published in the last 6 hours vs older than 6 hours?
# If you run your script twice, does your database end up with duplicate rows? How did you prevent that?
Save only headlines with a title longer than 6 words to a CSV. How many passed that filter?
Which country had the longest headline on average — and which had the shortest?
"""

import pandas as pd
from datetime import datetime, timedelta, timezone


def load_data():
    try:
        df = pd.read_csv("news_data.csv")
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_') # Clean column names: no spaces, all lowercase
        return df
    except FileNotFoundError:
        print("CSV file not found. Please run the data pipeline script first.")
        return None
    
def preprocess_data(df):
    # word count in headline titles
    df["word_count"] = df["title"].str.split().str.len() # Add a new column for word count in headline titles
    # Datetime parsing
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    return df


def analyze_data(df):
    # 1. Which country published the most headlines today?
    today = datetime.now().date()
    df_today = df[df["published_at"].dt.date == today] # Filter headlines published today
    most_headlines_country = df_today["country"].value_counts().idxmax()
    print(f"Country with most headlines today: {most_headlines_country}")
    
    # 2. Average number of words in a headline title — per country
    avg_words_per_country = df.groupby("country")["word_count"].mean()
    print("\nAverage number of words in a headline title per country:")
    for country, avg_words in avg_words_per_country.items():
        print(f"  {country}: {avg_words:.2f}")
    
    # 3. Headlines that appeared in more than one country
    duplicate_headlines = df[df.duplicated(subset=["title"], keep=False)] # Find duplicate headlines based on title
    if not duplicate_headlines.empty:
        print("\nHeadlines that appeared in more than one country:")
        for title in duplicate_headlines["title"].unique(): # Print unique duplicate headlines
            print(f"1.  {title}")
    else:
        print("\nNo headlines appeared in more than one country.")
        
    # 4. News source that published the most headlines across all 5 countries combined
    most_common_source = df["source"].value_counts().idxmax()
    print(f"\nNews source that published the most headlines across all countries: {most_common_source}")
    
    # 5. Percentage of all headlines published in the last 6 hours vs older than 6 hours
    now = datetime.now(timezone.utc)
    df["recent"] = (now - df["published_at"]) <= pd.Timedelta(hours=6) # Create a boolean column to indicate if the headline is recent (published within the last 6 hours)
    recent_percentage = df["recent"].mean() * 100
    older_percentage = 100 - recent_percentage
    print(
        f"\nRecent (<6h): {recent_percentage:.2f}% | Older: {older_percentage:.2f}%"
    )
    
    # 6. Save only headlines with a title longer than 6 words to a CSV. How many passed that filter?
    long_headlines = df[df["word_count"] > 6] # Filter headlines with title longer than 6 words
    long_headlines.to_csv("Filtered_Headlines.csv", index=False) # Save to a
    print(f"\nNumber of headlines with titles longer than 6 words: {len(long_headlines)}")

    # 7. Which country had the longest headline on average — and which had the shortest?
    avg_word_count = df.groupby("country")["word_count"].mean()
    longest_avg_headline_country = avg_word_count.idxmax()
    shortest_avg_headline_country = avg_word_count.idxmin()
    print(f"\nCountry with longest average headline: {longest_avg_headline_country}")
    print(f"Country with shortest average headline: {shortest_avg_headline_country}")

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        df = preprocess_data(df)
        analyze_data(df)
    else:
        print("No data to analyze.")
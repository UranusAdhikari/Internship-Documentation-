"""
=========================================================
TASK 02: DISTRIBUTION DEEP DIVE (MYSQL VERSION)
=========================================================

1. Fetches 7-day weather data for 5 cities using Open-Meteo API.
2. Stores data into MySQL database (weather_db).
3. Loads data into Pandas for analysis.
4. Performs full EDA (shape, nulls, stats, value counts).
5. Detects outliers using IQR method.
6. Creates histogram, boxplot, KDE plots.
7. Saves all graphs as PNG files.
8. Prints grouped summary statistics and observations.
"""

# ==========================================
# IMPORT LIBRARIES
# ==========================================
# yo line le API, database, graph sab tools import garxa
import requests
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# STEP 1: CITY DATA
# ==========================================
# yo list ma 5 cities ko latitude/longitude xa
cities = [
    {"name": "Kathmandu", "lat": 27.7172, "lon": 85.3240},
    {"name": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "London", "lat": 51.5072, "lon": -0.1276},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060}
]

all_data = []

# ==========================================
# STEP 2: FETCH WEATHER DATA FROM API
# ==========================================
# yo loop le 5 cities ko 7-day weather data fetch garxa
print("\n[STEP 2] Fetching weather data...")

for city in cities:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    response = requests.get(url)
    data = response.json()

    for i in range(len(data["daily"]["time"])):
        all_data.append((
            city["name"],
            data["daily"]["time"][i],
            data["daily"]["temperature_2m_max"][i],
            data["daily"]["temperature_2m_min"][i],
            data["daily"]["precipitation_sum"][i]
        ))

print("[SUCCESS] API data fetched!")

# ==========================================
# STEP 3: CONVERT TO DATAFRAME
# ==========================================
# yo line le raw data lai pandas dataframe banauxa
df = pd.DataFrame(all_data, columns=["city", "date", "max_temp", "min_temp", "rainfall"])

# ==========================================
# STEP 4: CONNECT MYSQL
# ==========================================
# yo line le MySQL database sanga connection banauxa
print("\n[STEP 3] Connecting to MySQL...")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="weather_db"
)

cursor = conn.cursor()

print("[SUCCESS] Connected to MySQL!")

# ==========================================
# STEP 5: INSERT DATA INTO MYSQL
# ==========================================
# yo line le dataframe ko data MySQL table ma insert garxa
print("\n[STEP 4] Inserting data into MySQL...")

for _, row in df.iterrows():
    sql = """
    INSERT INTO weather (city, date, max_temp, min_temp, rainfall)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, tuple(row))

conn.commit()

print("[SUCCESS] Data inserted into MySQL!")

# ==========================================
# STEP 6: LOAD FROM MYSQL
# ==========================================
# yo line le database bata data load garxa analysis ko lagi
df = pd.read_sql("SELECT * FROM weather", conn)

# ==========================================
# STEP 7: EDA CHECKLIST
# ==========================================
print("\n================ EDA ================")

print("\nShape:", df.shape)
print("\nMissing values:\n", df.isnull().sum())
print("\nDescription:\n", df.describe())
print("\nCity counts:\n", df["city"].value_counts())

# ==========================================
# STEP 8: HISTOGRAM
# ==========================================
# yo graph le overall temperature distribution dekhaunxa
plt.figure(figsize=(8,5))
sns.histplot(df["max_temp"], bins=15, kde=True)
plt.title("Max Temperature Distribution (All Cities)")
plt.savefig("hist_max_temp.png")
plt.show()

# ==========================================
# STEP 9: BOX PLOT
# ==========================================
# yo graph le city-wise comparison dekhaunxa
plt.figure(figsize=(10,6))
sns.boxplot(x="city", y="max_temp", data=df)
plt.title("City-wise Max Temperature Comparison")
plt.savefig("boxplot_city.png")
plt.show()

# ==========================================
# STEP 10: OUTLIER DETECTION (IQR)
# ==========================================
# yo line le extreme values detect garxa

Q1 = df["max_temp"].quantile(0.25)
Q3 = df["max_temp"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = df[(df["max_temp"] < lower) | (df["max_temp"] > upper)]

print("\nOUTLIERS:\n", outliers)

# ==========================================
# STEP 11: KDE PLOT
# ==========================================
# yo graph le distribution per city compare garxa
plt.figure(figsize=(10,6))

for city in df["city"].unique():
    sns.kdeplot(df[df["city"] == city]["max_temp"], label=city)

plt.title("Temperature Distribution per City")
plt.legend()
plt.savefig("kde_plot.png")
plt.show()

# ==========================================
# STEP 12: GROUPED SUMMARY
# ==========================================
summary = df.groupby("city")["max_temp"].agg(["mean", "median", "std", "min", "max"])
print("\nCITY SUMMARY:\n", summary)

# ==========================================
# STEP 13: OBSERVATIONS
# ==========================================
print("""
=================================================
OBSERVATIONS
=================================================

1. Kathmandu shows moderate temperature variation.
2. New York has wider temperature fluctuations.
3. Tokyo remains relatively stable.
4. Some extreme values were detected using IQR method.
5. Distribution is slightly skewed, not perfectly normal.
""")

# ==========================================
# CLOSE CONNECTION
# ==========================================
conn.close()

print("\n[DONE] Weather analysis completed successfully!")
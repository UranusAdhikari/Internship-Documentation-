"""
Task 03 · Weather Data + Analysis [Hard]
Store real weather data in MySQL and run meaningful analysis queries
Goal
Use the Open-Meteo API to fetch 7-day weather for 3 cities and store + compare them in MySQL
1. Fetch 7-day forecast (max + min temp) for 3 cities of your choice using Open-Meteo API
2. Create weather.db with a forecasts table: id, city, date, max_temp, min_temp
3. Insert all 21 rows (3 cities * 7 days) into the database
4. Query 1: Which city has the highest average max temperature?
5. Query 2: Find the single hottest day across all 3 cities
6. Query 3: Find days where the temperature difference (max - min) is greater than 10°C
7. Save a summary report to a summary.txt file using Python file handling (Week 1 skill!)
Deliverable: weather.db + summary.txt + script showing all 3 query outputs  
Bonus: add humidity data as a 4th column
"""
import os
import requests
from dotenv import load_dotenv
import mysql.connector
from collections import defaultdict

# load environment variables
load_dotenv()

# Connect to MySQL server
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cursor = conn.cursor()
    print("Connected to MySQL server successfully!")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)

# Create database and table
cursor.execute("CREATE DATABASE IF NOT EXISTS weather_db")
cursor.execute("USE weather_db")

cursor.execute("""
CREATE TABLE IF NOT EXISTS forecasts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    date DATE,
    max_temp FLOAT,
    min_temp FLOAT,
    humidity FLOAT,
    UNIQUE KEY unique_city_date (city, date)
)
""")

# Fetch weather data for 3 cities
params = {
    "daily": "temperature_2m_max,temperature_2m_min",
    "hourly": "relative_humidity_2m",
    "timezone": "auto",
}

cities = {
    "New York": {"latitude": 40.7128, "longitude": -74.0060},
    "London": {"latitude": 51.5074, "longitude": -0.1278},
    "Tokyo": {"latitude": 35.6762, "longitude": 139.6503}
}

for city, coords in cities.items():

    params["latitude"] = coords["latitude"]
    params["longitude"] = coords["longitude"]

    response = requests.get(os.getenv("WEATHER_API_URL"), params=params)

    if response.status_code == 200:
        data = response.json()

        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])

        hourly_times = hourly.get("time", [])
        hourly_humidity = hourly.get("relative_humidity_2m", [])

        # Convert hourly humidity → daily average by grouping by date and averaging 
        humidity_map = defaultdict(list) 

        for t, h in zip(hourly_times, hourly_humidity):
            day = t.split("T")[0] # Extract date part
            humidity_map[day].append(h) # Group humidity values by date each day has a list of hourly humidity values

        daily_humidity = {
            day: sum(values) / len(values)
            for day, values in humidity_map.items()
        }

        # Insert into database
        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):

            cursor.execute("""
                INSERT INTO forecasts (city, date, max_temp, min_temp, humidity)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    max_temp = VALUES(max_temp),
                    min_temp = VALUES(min_temp),
                    humidity = VALUES(humidity)
            """, (
                city,
                date,
                max_temp,
                min_temp,
                daily_humidity.get(date)
            ))

        conn.commit()
        print(f"{city} data inserted successfully!")

    else:
        print(f"Failed to fetch data for {city}: {response.status_code}")

# ----------------------------
# Query 1
cursor.execute("""
SELECT city, AVG(max_temp) as avg_max
FROM forecasts
GROUP BY city
ORDER BY avg_max DESC
LIMIT 1
""")
hottest_city = cursor.fetchone()

# Query 2
cursor.execute("""
SELECT city, date, max_temp
FROM forecasts
ORDER BY max_temp DESC
LIMIT 1
""")
hottest_day = cursor.fetchone()

# Query 3
cursor.execute("""
SELECT city, date, max_temp, min_temp, humidity
FROM forecasts
WHERE (max_temp - min_temp) > 10
""")
hot_days = cursor.fetchall()

# ----------------------------
# Save report
with open("summary_3.txt", "w", encoding="utf-8") as f:

    f.write("Weather Summary Report\n")
    f.write("=====================\n\n")

    if hottest_city:
        f.write(f"Hottest city on average: {hottest_city[0]} with avg max temp {hottest_city[1]:.2f}°C\n\n")

    if hottest_day:
        f.write(f"Hottest day: {hottest_day[0]} on {hottest_day[1]} with {hottest_day[2]:.2f}°C\n\n")

    f.write("Days with temperature difference > 10°C:\n")

    for city, date, max_temp, min_temp, humidity in hot_days:
        diff = max_temp - min_temp
        f.write(f"{city} on {date}: Max {max_temp:.2f}°C, Min {min_temp:.2f}°C, Humidity {humidity:.2f}% | Diff {diff:.2f}°C\n")

print("summary.txt created successfully!")

# Close connection
cursor.close()
conn.close()
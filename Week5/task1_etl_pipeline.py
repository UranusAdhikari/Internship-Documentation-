import pandas as pd
import requests
import threading
import os
from dotenv import load_dotenv
import mysql.connector

# =========================
# LOAD ENV
# =========================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# =========================
# API SOURCE
# =========================
API_USERS_URL = "https://jsonplaceholder.typicode.com/users"

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "local_users.csv")

# =========================
# CREATE MESSY CSV
# =========================
def create_messy_csv():
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": [" john doe ", "JANE DOE", "alice smith", "Bob brown", "john doe"],
        "email": [
            "JOHN@EMAIL.COM",
            "jane@email.com ",
            "alice@email.com",
            "bob@EMAIL.com",
            "john@EMAIL.com"
        ],
        "city": ["kathmandu", " Pokhara ", "lalitpur", "kathmandu", "kathmandu"]
    }
    pd.DataFrame(data).to_csv(CSV_PATH, index=False)

# =========================
# EXTRACT API DATA
# =========================
api_users = []

def fetch_users():
    global api_users
    try:
        api_users = requests.get(API_USERS_URL, timeout=5).json()
    except Exception as e:
        print("[ERROR] API failed:", e)
        api_users = []

# =========================
# RUN EXTRACTION
# =========================
create_messy_csv()

t1 = threading.Thread(target=fetch_users)
t1.start()
t1.join()

# =========================
# LOAD DATA
# =========================
csv_df = pd.read_csv(CSV_PATH)
api_df = pd.json_normalize(api_users)

api_df = api_df[["id", "name", "email"]]
csv_df = csv_df[["id", "name", "email", "city"]]

# =========================
# MERGE
# =========================
merged = pd.merge(
    api_df,
    csv_df,
    on="email",
    how="outer",
    suffixes=("_api", "_csv")
)

merged["name"] = merged["name_api"].combine_first(merged["name_csv"])

# SAFE CITY HANDLING (IMPORTANT FIX)
if "city_csv" in merged.columns:
    merged["city"] = merged["city_csv"]
else:
    merged["city"] = "Unknown"

final_df = merged[["email", "name", "city"]]

# =========================
# CLEANING (SAFE VERSION)
# =========================
final_df = final_df.copy()

final_df = final_df.fillna("Unknown")

final_df["email"] = final_df["email"].str.lower()
final_df["name"] = final_df["name"].str.title()
final_df["city"] = final_df["city"].str.title()

final_df = final_df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

final_df = final_df.drop_duplicates(subset=["email"])
final_df = final_df[final_df["email"].str.contains("@")]

# =========================
# MYSQL CONNECTION (FIXED)
# =========================
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=int(DB_PORT),
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255)
)
""")

# =========================
# UPSERT
# =========================
for _, row in final_df.iterrows():
    cursor.execute("""
    INSERT INTO users (email, name, city)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        city = VALUES(city)
    """, (row["email"], row["name"], row["city"]))

conn.commit()
cursor.close()
conn.close()

# =========================
# OUTPUT
# =========================
output_path = os.path.join(BASE_DIR, "final_output.csv")
final_df.to_csv(output_path, index=False)

print("[INFO] ETL completed successfully")
print("[INFO] CSV saved:", output_path)
print("[INFO] Loaded into MySQL (week5)")
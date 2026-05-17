import pandas as pd
import requests
import sqlite3
import os

# =========================================================
# TASK 2 : DATA QUALITY AUDIT SYSTEM + ETL PIPELINE

# yo BASE_DIR lya current python file ko location dinxa
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# yo audit report save garna ko lagi path ho
AUDIT_REPORT_PATH = os.path.join(BASE_DIR, "audit_report.csv")

# yo cleaned output save garna ko lagi path ho
CLEAN_OUTPUT_PATH = os.path.join(BASE_DIR, "clean_posts.csv")

# yo SQLite database ko naam ho
SQLITE_DB_PATH = os.path.join(BASE_DIR, "task2_week5")

# =========================================================
# EXTRACT
# =========================================================

print("[INFO] Fetching API data...")

try:
    # yo API bata 100 posts fetch garxa
    response = requests.get(
        "https://jsonplaceholder.typicode.com/posts",
        timeout=5
    )

    # yo line lya HTTP error xa vane throw garxa
    response.raise_for_status()

    # yo JSON data lai python object ma convert garxa
    posts_data = response.json()

except Exception as e:
    print("[ERROR] API fetch failed:", e)
    posts_data = []

# yo fetched data lai DataFrame ma convert garxa
df = pd.DataFrame(posts_data)

# =========================================================
# INTENTIONALLY ADD SOME BAD DATA
# (audit system dekhauna ko lagi)
# =========================================================

# yo null value create garxa
df.loc[0, "title"] = None

# yo duplicate row create garxa
df = pd.concat([df, df.iloc[[1]]], ignore_index=True)

# yo wrong datatype create garxa
df.loc[2, "userId"] = "INVALID"

# yo outlier value create garxa
df.loc[3, "id"] = 99999

# yo inconsistent casing create garxa
df.loc[4, "title"] = "   HELLO WORLD FROM ETL   "

# =========================================================
# BEFORE CLEANING AUDIT
# =========================================================

print("[INFO] Running data quality audit...")

# yo variable ma before cleaning row count save hunxa
before_rows = len(df)

# =========================================================
# NULL COUNT
# =========================================================

# yo line lya column-wise null count calculate garxa
null_counts = df.isnull().sum()

# =========================================================
# DUPLICATE COUNT
# =========================================================

# yo duplicate rows count garxa
duplicate_count = df.duplicated().sum()

# =========================================================
# TYPE MISMATCH DETECTION
# =========================================================

# yo userId numeric hunuparxa
# numeric nabhako rows detect garxa
type_mismatch_count = 0

for value in df["userId"]:
    try:
        int(value)
    except:
        type_mismatch_count += 1

# =========================================================
# OUTLIER DETECTION
# =========================================================

# yo unrealistic ID detect garxa
outlier_count = len(df[df["id"] > 1000])

# =========================================================
# INCONSISTENT STRING FORMAT
# =========================================================

# yo inconsistent title format detect garxa
format_issue_count = 0

for title in df["title"].dropna():

    # yo whitespace issue detect garxa
    if title != title.strip():

        format_issue_count += 1

    # yo all-uppercase issue detect garxa
    elif title.isupper():

        format_issue_count += 1

# =========================================================
# CLEANING + TRANSFORMATION
# =========================================================

print("[INFO] Cleaning data...")

# yo dataframe copy garxa warning avoid garna
clean_df = df.copy()

# =========================================================
# NULL HANDLING
# =========================================================

# yo null title replace garxa
clean_df["title"] = clean_df["title"].fillna("Unknown Title")

# =========================================================
# REMOVE DUPLICATES
# =========================================================

# yo duplicate rows remove garxa
clean_df = clean_df.drop_duplicates()

# =========================================================
# FIX TYPE MISMATCH
# =========================================================

# yo invalid datatype lai numeric ma convert garxa
clean_df["userId"] = pd.to_numeric(
    clean_df["userId"],
    errors="coerce"
)

# yo invalid datatype rows remove garxa
clean_df = clean_df.dropna(subset=["userId"])

# yo datatype int ma convert garxa
clean_df["userId"] = clean_df["userId"].astype(int)

# =========================================================
# REMOVE OUTLIERS
# =========================================================

# yo unrealistic IDs remove garxa
clean_df = clean_df[clean_df["id"] <= 1000]

# =========================================================
# STRING CLEANING
# =========================================================

# yo extra whitespace remove garxa
clean_df["title"] = clean_df["title"].str.strip()

# yo title casing apply garxa
clean_df["title"] = clean_df["title"].str.title()

# =========================================================
# ENRICHMENT
# =========================================================

# yo title ko word count calculate garxa
clean_df["title_word_count"] = clean_df["title"].apply(
    lambda x: len(x.split())
)

# yo body ko word count calculate garxa
clean_df["body_word_count"] = clean_df["body"].apply(
    lambda x: len(x.split())
)

# yo ranking create garxa based on body length
clean_df["body_rank"] = clean_df["body_word_count"].rank(
    ascending=False
)

# =========================================================
# FILTERING
# =========================================================

# yo empty body vako rows remove garxa
clean_df = clean_df[
    clean_df["body_word_count"] > 0
]

# =========================================================
# AFTER CLEANING AUDIT
# =========================================================

after_rows = len(clean_df)

# =========================================================
# CREATE AUDIT REPORT
# =========================================================

# yo structured audit report dataframe create garxa
audit_report = pd.DataFrame({
    "Issue Type": [
        "Null Values",
        "Duplicate Rows",
        "Type Mismatches",
        "Outliers",
        "String Format Issues"
    ],

    "Issues Found": [
        int(null_counts.sum()),
        int(duplicate_count),
        int(type_mismatch_count),
        int(outlier_count),
        int(format_issue_count)
    ],

    "Issues Fixed": [
        int(null_counts.sum()),
        int(duplicate_count),
        int(type_mismatch_count),
        int(outlier_count),
        int(format_issue_count)
    ]
})

# yo before/after row count add garxa
audit_report["Before Row Count"] = before_rows
audit_report["After Row Count"] = after_rows

# =========================================================
# SAVE AUDIT REPORT
# =========================================================

# yo audit report CSV ma save garxa
audit_report.to_csv(
    AUDIT_REPORT_PATH,
    index=False
)

print("\n[INFO] AUDIT REPORT")
print(audit_report)

# =========================================================
# SAVE CLEAN OUTPUT
# =========================================================

# yo cleaned dataset CSV ma save garxa
clean_df.to_csv(
    CLEAN_OUTPUT_PATH,
    index=False
)

# =========================================================
# LOAD INTO SQLITE
# =========================================================

print("\n[INFO] Loading into SQLite...")

# yo SQLite database connection create garxa
conn = sqlite3.connect(SQLITE_DB_PATH)

# yo cleaned dataframe SQLite table ma load garxa
clean_df.to_sql(
    "clean_posts",
    conn,
    if_exists="replace",
    index=False
)

# yo DB connection close garxa
conn.close()

# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n[INFO] ETL + Audit completed successfully")
print("[INFO] Audit Report Saved:", AUDIT_REPORT_PATH)
print("[INFO] Clean Data Saved:", CLEAN_OUTPUT_PATH)
print("[INFO] SQLite DB Saved:", SQLITE_DB_PATH)

print("\n[INFO] Sample Clean Data")
print(clean_df.head())
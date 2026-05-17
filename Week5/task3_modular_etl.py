import pandas as pd
import requests
import sqlite3
import logging
import os

# =========================================================
# MODULAR PRODUCTION-STYLE ETL PIPELINE
# MONTH 1 CAPSTONE
# =========================================================

# =========================================================
# PATH SETUP
# =========================================================

# yo line lya current file ko directory path dinxa
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# yo cleaned CSV output ko path ho
CSV_OUTPUT_PATH = os.path.join(BASE_DIR, "capstone_output.csv")

# yo SQLite database ko path ho
SQLITE_DB_PATH = os.path.join(BASE_DIR, "capstone_week5")

# =========================================================
# LOGGING CONFIG
# =========================================================

# yo logging system setup ho
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================================================
# EXTRACT FUNCTION
# =========================================================

def extract():
    """
    yo function lya API bata raw data extract garxa
    """

    logging.info("Starting extract() function")

    API_URL = "https://jsonplaceholder.typicode.com/todos"

    try:

        # yo API request pathauxa with timeout
        response = requests.get(API_URL, timeout=5)

        # yo line lya HTTP error check garxa
        response.raise_for_status()

        # yo JSON response lai python object ma convert garxa
        data = response.json()

        # yo raw data lai dataframe ma convert garxa
        df = pd.DataFrame(data)

        logging.info(f"extract() received {len(df)} rows")

        return df

    except requests.exceptions.Timeout:
        logging.error("API request timed out")
        return pd.DataFrame()

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return pd.DataFrame()

    except Exception as e:
        logging.error(f"Unexpected error in extract(): {e}")
        return pd.DataFrame()

# =========================================================
# CLEAN FUNCTION
# =========================================================

def clean(df):
    """
    yo function lya dirty data clean garxa
    """

    logging.info(f"Starting clean() with {len(df)} rows")

    # yo dataframe copy garxa warning avoid garna
    clean_df = df.copy()

    # =====================================================
    # NULL HANDLING
    # =====================================================

    # yo missing title fill garxa
    clean_df["title"] = clean_df["title"].fillna("Unknown Task")

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    before_duplicates = len(clean_df)

    # yo duplicate rows remove garxa
    clean_df = clean_df.drop_duplicates(subset=["id"])

    after_duplicates = len(clean_df)

    logging.info(
        f"Removed {before_duplicates - after_duplicates} duplicate rows"
    )

    # =====================================================
    # STRING CLEANING
    # =====================================================

    # yo whitespace remove garxa
    clean_df["title"] = clean_df["title"].str.strip()

    # yo title formatting clean garxa
    clean_df["title"] = clean_df["title"].str.title()

    # =====================================================
    # TYPE FIXING
    # =====================================================

    # yo completed column boolean ma ensure garxa
    clean_df["completed"] = clean_df["completed"].astype(bool)

    logging.info(f"clean() output rows: {len(clean_df)}")

    return clean_df

# =========================================================
# TRANSFORM FUNCTION
# =========================================================

def transform(df):
    """
    yo function lya enrichment + calculated columns create garxa
    """

    logging.info(f"Starting transform() with {len(df)} rows")

    transform_df = df.copy()

    # =====================================================
    # CALCULATED COLUMN 1
    # =====================================================

    # yo title ko word count calculate garxa
    transform_df["title_word_count"] = transform_df["title"].apply(
        lambda x: len(x.split())
    )

    # =====================================================
    # CALCULATED COLUMN 2
    # =====================================================

    # yo completion status category banaunxa
    transform_df["status"] = transform_df["completed"].apply(
        lambda x: "Completed" if x else "Pending"
    )

    # =====================================================
    # CALCULATED COLUMN 3
    # =====================================================

    # yo task difficulty assign garxa
    transform_df["difficulty"] = transform_df["title_word_count"].apply(
        lambda x:
            "Easy" if x <= 3
            else "Medium" if x <= 6
            else "Hard"
    )

    # =====================================================
    # CALCULATED COLUMN 4
    # =====================================================

    # yo ranking create garxa based on word count
    transform_df["task_rank"] = transform_df[
        "title_word_count"
    ].rank(
        ascending=False
    )

    # =====================================================
    # GROUPBY SUMMARY
    # =====================================================

    logging.info("Generating groupby summary table")

    # yo status-wise statistics calculate garxa
    summary_table = transform_df.groupby("status").agg({
        "title_word_count": ["mean", "min", "max"],
        "task_rank": ["mean", "min", "max"]
    })

    print("\n================ GROUPBY SUMMARY ================\n")
    print(summary_table)

    logging.info(f"transform() output rows: {len(transform_df)}")

    return transform_df

# =========================================================
# LOAD FUNCTION
# =========================================================

def load(df):
    """
    yo function lya CSV + SQLite ma data load garxa
    """

    logging.info(f"Starting load() with {len(df)} rows")

    # =====================================================
    # SAVE CSV
    # =====================================================

    # yo cleaned data CSV ma save garxa
    df.to_csv(
        CSV_OUTPUT_PATH,
        index=False
    )

    logging.info(f"CSV saved at: {CSV_OUTPUT_PATH}")

    # =====================================================
    # SQLITE LOAD
    # =====================================================

    # yo SQLite DB connection create garxa
    conn = sqlite3.connect(SQLITE_DB_PATH)

    # =====================================================
    # IDEMPOTENCY FIX
    # =====================================================

    # yo duplicate avoid garna old table replace garxa
    # second run ma duplicate create hudaina
    df.to_sql(
        "tasks",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    logging.info("SQLite load completed")
    logging.info("No duplicate rows created on rerun")

# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    logging.info("========== ETL PIPELINE STARTED ==========")

    # =====================================================
    # STEP 1 : EXTRACT
    # =====================================================

    raw_df = extract()

    # extract fail vayo vane stop garxa
    if raw_df.empty:
        logging.error("Pipeline stopped because extract() failed")
        return

    # =====================================================
    # STEP 2 : CLEAN
    # =====================================================

    clean_df = clean(raw_df)

    # =====================================================
    # STEP 3 : TRANSFORM
    # =====================================================

    transformed_df = transform(clean_df)

    # =====================================================
    # STEP 4 : LOAD
    # =====================================================

    load(transformed_df)

    logging.info("========== ETL PIPELINE COMPLETED ==========")

# =========================================================
# RUN PIPELINE
# =========================================================

if __name__ == "__main__":
    main()
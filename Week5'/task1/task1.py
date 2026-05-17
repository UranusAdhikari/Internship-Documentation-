"""
=========================================================
EDA SUMMARY (FOR MENTOR SUBMISSION)
=========================================================

1. This project connects Python with a MySQL database (internship_eda).
2. Data is loaded from a table called 'tasks' using SQL queries.
3. The dataset contains task tracking information like status, priority, and assigned users.
4. Basic exploratory data analysis (EDA) is performed using Pandas.
5. Visualizations are created using Matplotlib and Seaborn, and saved as image files.

Conclusion:
The dataset shows how tasks are distributed across users, priorities, and statuses.
This helps understand workload balance and project progress.
"""

# ==========================================
# IMPORT LIBRARIES
# ==========================================
# yo line le data analysis, database connection, graph banawne tools import garxa
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# STEP 1: CONNECT TO MYSQL DATABASE
# ==========================================
# yo line le MySQL database sanga connection establish garxa
print("\n[STEP 1] Connecting to MySQL database...")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",   # yo line ma timro MySQL password halne
    database="internship_eda"   # yo database ma data store xa
)

print("[SUCCESS] Connected to MySQL!")

# ==========================================
# STEP 2: LOAD DATA FROM MYSQL
# ==========================================
# yo line le SQL table 'tasks' bata data fetch garxa pandas dataframe ma
print("\n[STEP 2] Loading data from tasks table...")

query = "SELECT * FROM tasks"
df = pd.read_sql(query, conn)

print("[SUCCESS] Data loaded successfully!")

# ==========================================
# STEP 3: SHOW SAMPLE DATA
# ==========================================
# yo line le dataset ko first 5 rows display garxa
print("\n[STEP 3] First 5 rows:")
print(df.head())

# ==========================================
# STEP 4: DATASET INFO
# ==========================================
# yo line le dataset structure (columns, types, null values) dekhaunxa
print("\n[STEP 4] Dataset Info:")
print(df.info())

# ==========================================
# STEP 5: MISSING VALUES CHECK
# ==========================================
# yo line le kun column ma missing value xa check garxa
print("\n[STEP 5] Missing Values:")
print(df.isnull().sum())

# ==========================================
# STEP 6: STATISTICAL SUMMARY
# ==========================================
# yo line le dataset ko summary statistics dekhaunxa
print("\n[STEP 6] Statistical Summary:")
print(df.describe(include="all"))

# ==========================================
# STEP 7: STATUS VISUALIZATION
# ==========================================
# yo graph le task ko status (Pending, Completed, In Progress) dekhaunxa
plt.figure(figsize=(8,5))
sns.countplot(data=df, x="status")
plt.title("Task Status Distribution")

plt.savefig("status_graph.png")   # graph save hunxa file ma
plt.show()

# ==========================================
# STEP 8: PRIORITY VISUALIZATION
# ==========================================
# yo graph le task priority (High, Medium, Low) dekhaunxa
plt.figure(figsize=(8,5))
sns.countplot(data=df, x="priority")
plt.title("Task Priority Distribution")

plt.savefig("priority_graph.png")
plt.show()

# ==========================================
# STEP 9: ASSIGNED USER VISUALIZATION
# ==========================================
# yo graph le kun user le kati task gareko xa dekhaunxa
plt.figure(figsize=(10,5))
sns.countplot(data=df, x="assigned_to")
plt.title("Tasks Assigned to Users")
plt.xticks(rotation=45)

plt.savefig("assigned_tasks.png")
plt.show()

# ==========================================
# STEP 10: CLOSE DATABASE CONNECTION
# ==========================================
# yo line le MySQL connection safely close garxa
conn.close()

print("\n[DONE] EDA completed successfully and graphs saved!")
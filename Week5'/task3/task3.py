"""
=========================================================
TASK 03: CORRELATION ANALYSIS (STUDENT DATASET)
=========================================================

1. Creates synthetic dataset of 50 students.
2. Saves dataset as CSV file (students.csv).
3. Performs full EDA (shape, nulls, stats).
4. Computes correlation matrix.
5. Visualizes correlation using heatmap.
6. Finds strongest and weakest correlations.
7. Plots scatter plots with regression lines.
8. Uses pairplot to analyze class separation (passed vs failed).
"""

# ==========================================
# IMPORT LIBRARIES
# ==========================================
# yo line le data create, analysis, visualization tools import garxa
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================
# STEP 1: CREATE SYNTHETIC DATA
# ==========================================
# yo line le 50 students ko fake dataset banauxa
np.random.seed(42)

n = 50

data = {
    "name": [f"Student_{i}" for i in range(1, n+1)],

    # study hours (0-10 range)
    "study_hours": np.random.normal(5, 2, n).clip(0, 10),

    # sleep hours (4-10 range)
    "sleep_hours": np.random.normal(7, 1.5, n).clip(4, 10),

    # attendance percentage (50-100)
    "attendance_pct": np.random.normal(80, 10, n).clip(50, 100),
}

df = pd.DataFrame(data)

# ==========================================
# STEP 2: CREATE SCORE (REALISTIC RELATIONSHIP)
# ==========================================
# yo line le study, attendance, sleep ko based ma score generate garxa

df["score"] = (
    df["study_hours"] * 10 +
    df["attendance_pct"] * 0.5 +
    df["sleep_hours"] * 2 +
    np.random.normal(0, 5, n)   # noise added
)

# normalize score to 0–100 range
df["score"] = df["score"].clip(0, 100)

# ==========================================
# STEP 3: PASS/FAIL COLUMN
# ==========================================
# yo line le score >= 40 bhaye pass, natra fail
df["passed"] = df["score"].apply(lambda x: "Pass" if x >= 40 else "Fail")

# ==========================================
# STEP 4: SAVE TO CSV
# ==========================================
# yo line le dataset lai students.csv file ma save garxa
df.to_csv("students.csv", index=False)

print("\n[STEP 1] Dataset created and saved as students.csv")

# ==========================================
# STEP 5: LOAD DATA
# ==========================================
# yo line le CSV file reload garxa analysis ko lagi
df = pd.read_csv("students.csv")

print("\n[STEP 2] Data Loaded")

# ==========================================
# STEP 6: EDA CHECKLIST
# ==========================================
print("\n================ EDA ================")

print("\nShape:", df.shape)          # dataset size
print("\nNull values:\n", df.isnull().sum())  # missing values
print("\nDescribe:\n", df.describe())         # stats
print("\nValue counts:\n", df["passed"].value_counts())  # pass/fail count

# ==========================================
# STEP 7: CORRELATION MATRIX
# ==========================================
# yo line le numerical columns ko correlation nikalxa

corr = df[["study_hours", "sleep_hours", "attendance_pct", "score"]].corr()

print("\nCORRELATION MATRIX:\n")
print(corr)

# ==========================================
# STEP 8: HEATMAP
# ==========================================
# yo graph le correlation visualize garxa

plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap")

plt.savefig("heatmap.png")
plt.show()

# ==========================================
# STEP 9: STRONGEST & WEAKEST CORRELATIONS
# ==========================================
# yo line le correlation flatten garera sort garxa

corr_pairs = corr.unstack().sort_values()

# remove self-correlation
corr_pairs = corr_pairs[corr_pairs != 1]

print("\nTOP 3 STRONGEST CORRELATIONS:")
print(corr_pairs.tail(3))

print("\nTOP 3 WEAKEST CORRELATIONS:")
print(corr_pairs.head(3))

# ==========================================
# STEP 10: SCATTER PLOTS (TOP RELATIONSHIPS)
# ==========================================
# study_hours vs score
plt.figure(figsize=(7,5))
sns.regplot(x="study_hours", y="score", data=df)
plt.title("Study Hours vs Score")
plt.savefig("scatter_study_score.png")
plt.show()

# attendance vs score
plt.figure(figsize=(7,5))
sns.regplot(x="attendance_pct", y="score", data=df)
plt.title("Attendance vs Score")
plt.savefig("scatter_attendance_score.png")
plt.show()

# ==========================================
# STEP 11: PAIRPLOT BONUS
# ==========================================
# yo line le multi-variable relationship show garxa

sns.pairplot(df, hue="passed")
plt.savefig("pairplot.png")
plt.show()

# ==========================================
# STEP 12: WRITTEN ANALYSIS
# ==========================================
print("""
=================================================
ANALYSIS
=================================================

1. Study hours has strong positive correlation with score.
2. Attendance also positively affects performance.
3. Sleep hours has weak/moderate influence.
4. Score is mainly driven by study + attendance, not sleep alone.
5. Students with higher study hours mostly fall into 'Pass' category.

CONCLUSION:
More study generally improves score, but it is not the only factor.
Attendance also plays a major role in performance.
""")

print("\n[DONE] Task 03 completed successfully!")
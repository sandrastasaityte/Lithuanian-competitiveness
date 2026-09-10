from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================
# 1. FIND PROJECT FILE
# ============================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

FILE = PROJECT_DIR / "Lithuania_Competitiveness_Model.xlsx"


# ============================================
# 2. CHECK FILE
# ============================================

if not FILE.exists():
    raise FileNotFoundError(
        f"\nCould not find:\n{FILE}\n\n"
        f"Expected location:\n{PROJECT_DIR}"
    )


# ============================================
# 3. LOAD DATA
# ============================================

df = pd.read_excel(FILE)


# ============================================
# 4. CHECK REQUIRED COLUMNS
# ============================================

required_columns = [
    "Year",
    "Sector",
    "RCA"
]

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}\n\n"
        f"Available columns:\n{list(df.columns)}"
    )


# ============================================
# 5. CALCULATE RCA CHANGE
# ============================================

df = df.sort_values(
    ["Sector", "Year"]
)

df["RCA_Change"] = (
    df.groupby("Sector")["RCA"]
    .diff()
)


# ============================================
# 6. CLASSIFY CHANGE
# ============================================

df["RCA_Trend"] = "Stable"

df.loc[
    df["RCA_Change"] > 0,
    "RCA_Trend"
] = "Improving"

df.loc[
    df["RCA_Change"] < 0,
    "RCA_Trend"
] = "Deteriorating"


# ============================================
# 7. CREATE SUMMARY
# ============================================

summary = (
    df.groupby("Sector")
    .agg(
        Average_RCA=("RCA", "mean"),
        Latest_RCA=("RCA", "last"),
        RCA_Change=("RCA_Change", "sum")
    )
    .reset_index()
)

summary = summary.sort_values(
    "RCA_Change",
    ascending=False
)


# ============================================
# 8. DISPLAY RESULTS
# ============================================

print("\nRCA CHANGE ANALYSIS")
print("=" * 60)

print(summary.to_string(index=False))


# ============================================
# 9. PLOT RCA CHANGE
# ============================================

plt.figure(figsize=(12, 7))

plt.barh(
    summary["Sector"],
    summary["RCA_Change"]
)

plt.axvline(
    0,
    linewidth=1
)

plt.xlabel("Change in RCA")
plt.ylabel("Sector")
plt.title(
    "Lithuania: Change in Revealed Comparative Advantage"
)

plt.tight_layout()

# Save chart
output_file = (
    SCRIPT_DIR /
    "RCA_change_analysis.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    f"\n✓ Chart saved to:\n{output_file}"
)
# ============================================================
# CHINA PRESSURE TREND ANALYSIS
# Lithuania Competitiveness Project
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

# Folder containing this Python script
SCRIPT_DIR = Path(__file__).resolve().parent

# Main project folder
PROJECT_DIR = SCRIPT_DIR.parent

# Main integrated dataset
INPUT_FILE = PROJECT_DIR / "Lithuania_Competitiveness_Model.xlsx"

# Output folder
OUTPUT_DIR = SCRIPT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. CHECK INPUT FILE
# ============================================================

print("=" * 70)
print("CHINA PRESSURE TREND ANALYSIS")
print("=" * 70)

print(f"\nLooking for dataset:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\n\nERROR: Dataset not found.\n\n"
        f"Expected location:\n{INPUT_FILE}\n\n"
        f"Please make sure 'Lithuania_Competitiveness_Model.xlsx' "
        f"is in the main project folder."
    )

print("\n✓ Dataset found")


# ============================================================
# 3. LOAD DATA
# ============================================================

df = pd.read_excel(INPUT_FILE)

print(f"✓ Dataset loaded")
print(f"  Rows: {len(df):,}")
print(f"  Columns: {len(df.columns):,}")


# ============================================================
# 4. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Year",
    "SITC_Group",
    "China_Pressure_Index"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(f"  - {x}" for x in missing_columns)
        + "\n\nAvailable columns:\n"
        + "\n".join(f"  - {x}" for x in df.columns)
    )

print("✓ Required columns found")


# ============================================================
# 5. CLEAN DATA
# ============================================================

df = df.copy()

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df["China_Pressure_Index"] = pd.to_numeric(
    df["China_Pressure_Index"],
    errors="coerce"
)

df["SITC_Group"] = df["SITC_Group"].astype(str).str.strip()

# Remove observations without year or pressure index
df = df.dropna(
    subset=[
        "Year",
        "China_Pressure_Index"
    ]
)

df["Year"] = df["Year"].astype(int)


# ============================================================
# 6. SORT DATA
# ============================================================

df = df.sort_values(
    [
        "SITC_Group",
        "Year"
    ]
)


# ============================================================
# 7. CALCULATE YEAR-ON-YEAR CHANGE
# ============================================================

df["China_Pressure_Change"] = (
    df.groupby("SITC_Group")[
        "China_Pressure_Index"
    ].diff()
)


# Percentage change
df["China_Pressure_Pct_Change"] = (
    df.groupby("SITC_Group")[
        "China_Pressure_Index"
    ].pct_change()
    * 100
)


# ============================================================
# 8. CLASSIFY PRESSURE TREND
# ============================================================

df["Pressure_Trend"] = np.select(
    [
        df["China_Pressure_Change"] > 0,
        df["China_Pressure_Change"] < 0
    ],
    [
        "Increasing",
        "Decreasing"
    ],
    default="Stable"
)


# ============================================================
# 9. CREATE SECTOR SUMMARY
# ============================================================

summary = (
    df.groupby("SITC_Group")
    .agg(
        Average_China_Pressure=(
            "China_Pressure_Index",
            "mean"
        ),

        Latest_China_Pressure=(
            "China_Pressure_Index",
            "last"
        ),

        First_China_Pressure=(
            "China_Pressure_Index",
            "first"
        ),

        Total_Change=(
            "China_Pressure_Change",
            "sum"
        ),

        Observations=(
            "China_Pressure_Index",
            "count"
        )
    )
    .reset_index()
)


# ============================================================
# 10. OVERALL CHANGE
# ============================================================

summary["Overall_Change"] = (
    summary["Latest_China_Pressure"]
    - summary["First_China_Pressure"]
)


summary["Overall_Pct_Change"] = np.where(
    summary["First_China_Pressure"] != 0,

    (
        (
            summary["Latest_China_Pressure"]
            - summary["First_China_Pressure"]
        )
        /
        summary["First_China_Pressure"]
    ) * 100,

    np.nan
)


# ============================================================
# 11. PRESSURE CLASSIFICATION
# ============================================================

median_pressure = (
    summary["Average_China_Pressure"].median()
)

summary["Pressure_Level"] = np.where(
    summary["Average_China_Pressure"]
    >= median_pressure,

    "Higher Pressure",

    "Lower Pressure"
)


# ============================================================
# 12. RANK SECTORS
# ============================================================

summary["Pressure_Rank"] = (
    summary["Average_China_Pressure"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)

summary = summary.sort_values(
    "Average_China_Pressure",
    ascending=False
)


# ============================================================
# 13. PRINT ECONOMIC SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CHINA PRESSURE SUMMARY")
print("=" * 70)

print(
    summary[
        [
            "Pressure_Rank",
            "SITC_Group",
            "Average_China_Pressure",
            "Latest_China_Pressure",
            "Overall_Change",
            "Overall_Pct_Change"
        ]
    ].to_string(index=False)
)


# ============================================================
# 14. IDENTIFY HIGHEST PRESSURE
# ============================================================

highest_pressure = summary.iloc[0]

print("\n" + "=" * 70)
print("HIGHEST PRESSURE SECTOR")
print("=" * 70)

print(
    f"SITC Group: {highest_pressure['SITC_Group']}"
)

print(
    f"Average Pressure: "
    f"{highest_pressure['Average_China_Pressure']:.2f}"
)

print(
    f"Change over period: "
    f"{highest_pressure['Overall_Change']:.2f}"
)


# ============================================================
# 15. IDENTIFY INCREASING PRESSURE
# ============================================================

increasing_pressure = summary[
    summary["Overall_Change"] > 0
].sort_values(
    "Overall_Change",
    ascending=False
)

print("\n" + "=" * 70)
print("SECTORS WITH INCREASING CHINA PRESSURE")
print("=" * 70)

if len(increasing_pressure) > 0:

    print(
        increasing_pressure[
            [
                "SITC_Group",
                "Overall_Change",
                "Overall_Pct_Change"
            ]
        ].to_string(index=False)
    )

else:

    print("No sectors show increasing pressure.")


# ============================================================
# 16. IDENTIFY DECREASING PRESSURE
# ============================================================

decreasing_pressure = summary[
    summary["Overall_Change"] < 0
].sort_values(
    "Overall_Change"
)

print("\n" + "=" * 70)
print("SECTORS WITH DECREASING CHINA PRESSURE")
print("=" * 70)

if len(decreasing_pressure) > 0:

    print(
        decreasing_pressure[
            [
                "SITC_Group",
                "Overall_Change",
                "Overall_Pct_Change"
            ]
        ].to_string(index=False)
    )

else:

    print("No sectors show decreasing pressure.")


# ============================================================
# 17. CHART 1 — PRESSURE TREND BY SITC GROUP
# ============================================================

plt.figure(figsize=(13, 8))

for group in sorted(df["SITC_Group"].unique()):

    group_data = df[
        df["SITC_Group"] == group
    ]

    plt.plot(
        group_data["Year"],
        group_data["China_Pressure_Index"],
        marker="o",
        linewidth=2,
        label=f"SITC {group}"
    )


plt.title(
    "China Competitive Pressure on Lithuania by SITC Group",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel(
    "Year",
    fontsize=12
)

plt.ylabel(
    "China Pressure Index",
    fontsize=12
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend(
    title="SITC Group",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.tight_layout()

chart1 = (
    OUTPUT_DIR /
    "china_pressure_trend.png"
)

plt.savefig(
    chart1,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"\n✓ Saved: {chart1}")


# ============================================================
# 18. CHART 2 — AVERAGE PRESSURE RANKING
# ============================================================

ranking = summary.sort_values(
    "Average_China_Pressure"
)

plt.figure(figsize=(12, 7))

plt.barh(
    ranking["SITC_Group"].astype(str),
    ranking["Average_China_Pressure"]
)

plt.xlabel(
    "Average China Pressure Index"
)

plt.ylabel(
    "SITC Group"
)

plt.title(
    "Average China Competitive Pressure by SITC Group",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

chart2 = (
    OUTPUT_DIR /
    "china_pressure_ranking.png"
)

plt.savefig(
    chart2,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✓ Saved: {chart2}")


# ============================================================
# 19. CHART 3 — PRESSURE CHANGE
# ============================================================

change_plot = summary.sort_values(
    "Overall_Change"
)

plt.figure(figsize=(12, 7))

plt.barh(
    change_plot["SITC_Group"].astype(str),
    change_plot["Overall_Change"]
)

plt.axvline(
    0,
    linewidth=1
)

plt.xlabel(
    "Change in China Pressure Index"
)

plt.ylabel(
    "SITC Group"
)

plt.title(
    "Change in China Competitive Pressure",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

chart3 = (
    OUTPUT_DIR /
    "china_pressure_change.png"
)

plt.savefig(
    chart3,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✓ Saved: {chart3}")


# ============================================================
# 20. CHART 4 — HEATMAP
# ============================================================

heatmap_data = df.pivot_table(
    index="SITC_Group",
    columns="Year",
    values="China_Pressure_Index",
    aggfunc="mean"
)

plt.figure(figsize=(13, 7))

plt.imshow(
    heatmap_data,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(
    label="China Pressure Index"
)

plt.xticks(
    range(len(heatmap_data.columns)),
    heatmap_data.columns
)

plt.yticks(
    range(len(heatmap_data.index)),
    heatmap_data.index
)

plt.xlabel("Year")
plt.ylabel("SITC Group")

plt.title(
    "China Pressure Index Heatmap",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()

chart4 = (
    OUTPUT_DIR /
    "china_pressure_heatmap.png"
)

plt.savefig(
    chart4,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✓ Saved: {chart4}")


# ============================================================
# 21. EXPORT RESULTS
# ============================================================

summary_file = (
    OUTPUT_DIR /
    "China_Pressure_Analysis.xlsx"
)

with pd.ExcelWriter(
    summary_file,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Detailed Analysis",
        index=False
    )

    summary.to_excel(
        writer,
        sheet_name="Sector Summary",
        index=False
    )

    increasing_pressure.to_excel(
        writer,
        sheet_name="Increasing Pressure",
        index=False
    )

    decreasing_pressure.to_excel(
        writer,
        sheet_name="Decreasing Pressure",
        index=False
    )


# ============================================================
# 22. FINISH
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print(f"\nOutput folder:")
print(OUTPUT_DIR)

print("\nFiles created:")

print("✓ China_Pressure_Analysis.xlsx")
print("✓ china_pressure_trend.png")
print("✓ china_pressure_ranking.png")
print("✓ china_pressure_change.png")
print("✓ china_pressure_heatmap.png")

print("\n✓ China Pressure Trend analysis completed successfully.")
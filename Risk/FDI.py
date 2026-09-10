# ============================================================
# RCA TREND ANALYSIS
# Lithuanian Competitiveness Project
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment


# ============================================================
# 1. PROJECT PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

INPUT_FILE = PROJECT_DIR / "Lithuania_Competitiveness_Model.xlsx"

OUTPUT_DIR = SCRIPT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "RCA_Trend_Analysis.xlsx"


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("RCA TREND ANALYSIS")
print("Lithuanian Competitiveness Project")
print("=" * 70)

print("\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\n\nFile not found:\n{INPUT_FILE}\n\n"
        "Make sure Lithuania_Competitiveness_Model.xlsx "
        "is located in the main project folder."
    )

df = pd.read_excel(INPUT_FILE)

print("\n✓ Dataset loaded")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Year",
    "SITC_Group",
    "RCA"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )

print("✓ Required columns found")


# ============================================================
# 4. CLEAN DATA
# ============================================================

df = df.copy()

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df["RCA"] = pd.to_numeric(
    df["RCA"],
    errors="coerce"
)

df["SITC_Group"] = (
    df["SITC_Group"]
    .astype(str)
    .str.strip()
)

df = df.dropna(
    subset=[
        "Year",
        "RCA"
    ]
)

df["Year"] = df["Year"].astype(int)

df = df.sort_values(
    [
        "SITC_Group",
        "Year"
    ]
)


# ============================================================
# 5. RCA CATEGORY
# ============================================================

# RCA interpretation:
#
# RCA > 1  = comparative advantage
# RCA = 1  = neutral position
# RCA < 1  = comparative disadvantage


df["RCA_Category"] = np.select(
    [
        df["RCA"] > 1,
        df["RCA"] < 1
    ],
    [
        "Comparative Advantage",
        "Comparative Disadvantage"
    ],
    default="Neutral"
)


# ============================================================
# 6. DISTANCE FROM RCA = 1
# ============================================================

df["RCA_Distance_From_1"] = (
    df["RCA"] - 1
)


# ============================================================
# 7. YEAR-ON-YEAR RCA CHANGE
# ============================================================

df["RCA_Change"] = (
    df.groupby("SITC_Group")[
        "RCA"
    ].diff()
)


# ============================================================
# 8. YEAR-ON-YEAR RCA PERCENTAGE CHANGE
# ============================================================

df["RCA_Pct_Change"] = np.where(
    df.groupby("SITC_Group")["RCA"].shift(1) != 0,

    (
        df["RCA"]
        /
        df.groupby("SITC_Group")["RCA"].shift(1)
        - 1
    ) * 100,

    np.nan
)


# ============================================================
# 9. RCA TREND CLASSIFICATION
# ============================================================

df["RCA_Trend"] = np.select(
    [
        df["RCA_Change"] > 0.01,
        df["RCA_Change"] < -0.01
    ],
    [
        "Improving",
        "Deteriorating"
    ],
    default="Stable"
)


# ============================================================
# 10. LONG-TERM RCA CHANGE
# ============================================================

sector_summary = (
    df.groupby("SITC_Group")
    .agg(
        First_Year=(
            "Year",
            "min"
        ),

        Latest_Year=(
            "Year",
            "max"
        ),

        First_RCA=(
            "RCA",
            "first"
        ),

        Latest_RCA=(
            "RCA",
            "last"
        ),

        Average_RCA=(
            "RCA",
            "mean"
        ),

        Maximum_RCA=(
            "RCA",
            "max"
        ),

        Minimum_RCA=(
            "RCA",
            "min"
        ),

        Observations=(
            "RCA",
            "count"
        )
    )
    .reset_index()
)


# ============================================================
# 11. TOTAL RCA CHANGE
# ============================================================

sector_summary["RCA_Change"] = (
    sector_summary["Latest_RCA"]
    -
    sector_summary["First_RCA"]
)


# ============================================================
# 12. RCA PERCENTAGE CHANGE
# ============================================================

sector_summary["RCA_Pct_Change"] = np.where(
    sector_summary["First_RCA"] != 0,

    (
        (
            sector_summary["Latest_RCA"]
            -
            sector_summary["First_RCA"]
        )
        /
        sector_summary["First_RCA"]
    ) * 100,

    np.nan
)


# ============================================================
# 13. LATEST RCA CATEGORY
# ============================================================

sector_summary["Latest_RCA_Category"] = np.select(
    [
        sector_summary["Latest_RCA"] > 1,
        sector_summary["Latest_RCA"] < 1
    ],
    [
        "Comparative Advantage",
        "Comparative Disadvantage"
    ],
    default="Neutral"
)


# ============================================================
# 14. LONG-TERM TREND
# ============================================================

sector_summary["Long_Term_Trend"] = np.select(
    [
        sector_summary["RCA_Change"] > 0.01,
        sector_summary["RCA_Change"] < -0.01
    ],
    [
        "Improving",
        "Deteriorating"
    ],
    default="Stable"
)


# ============================================================
# 15. COMPETITIVE POSITION
# ============================================================

sector_summary["Competitive_Position"] = np.select(
    [
        (
            (sector_summary["Latest_RCA"] > 1)
            &
            (sector_summary["RCA_Change"] > 0)
        ),

        (
            (sector_summary["Latest_RCA"] > 1)
            &
            (sector_summary["RCA_Change"] < 0)
        ),

        (
            (sector_summary["Latest_RCA"] < 1)
            &
            (sector_summary["RCA_Change"] > 0)
        ),

        (
            (sector_summary["Latest_RCA"] < 1)
            &
            (sector_summary["RCA_Change"] < 0)
        )
    ],
    [
        "Strong and Improving",
        "Advantage but Deteriorating",
        "Weak but Improving",
        "Weak and Deteriorating"
    ],
    default="Stable"
)


# ============================================================
# 16. RCA RANKING
# ============================================================

sector_summary["RCA_Rank"] = (
    sector_summary["Latest_RCA"]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)

sector_summary = sector_summary.sort_values(
    "Latest_RCA",
    ascending=False
)


# ============================================================
# 17. STRONGEST SECTORS
# ============================================================

strongest = sector_summary[
    sector_summary["Latest_RCA"] > 1
].copy()

strongest = strongest.sort_values(
    "Latest_RCA",
    ascending=False
)


# ============================================================
# 18. WEAKEST SECTORS
# ============================================================

weakest = sector_summary[
    sector_summary["Latest_RCA"] < 1
].copy()

weakest = weakest.sort_values(
    "Latest_RCA"
)


# ============================================================
# 19. IMPROVING SECTORS
# ============================================================

improving = sector_summary[
    sector_summary["RCA_Change"] > 0
].copy()

improving = improving.sort_values(
    "RCA_Change",
    ascending=False
)


# ============================================================
# 20. DETERIORATING SECTORS
# ============================================================

deteriorating = sector_summary[
    sector_summary["RCA_Change"] < 0
].copy()

deteriorating = deteriorating.sort_values(
    "RCA_Change"
)


# ============================================================
# 21. PRINT SECTOR SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("RCA SECTOR RANKING")
print("=" * 70)

print(
    sector_summary[
        [
            "RCA_Rank",
            "SITC_Group",
            "Latest_RCA",
            "Average_RCA",
            "RCA_Change",
            "Latest_RCA_Category",
            "Long_Term_Trend"
        ]
    ].to_string(index=False)
)


# ============================================================
# 22. EXECUTIVE STATISTICS
# ============================================================

latest_year = df["Year"].max()

latest_data = df[
    df["Year"] == latest_year
]

average_latest_rca = (
    latest_data["RCA"].mean()
)

advantage_count = (
    latest_data["RCA"] > 1
).sum()

disadvantage_count = (
    latest_data["RCA"] < 1
).sum()


print("\n" + "=" * 70)
print("EXECUTIVE RCA SUMMARY")
print("=" * 70)

print(
    f"\nLatest year: {latest_year}"
)

print(
    f"Average RCA: "
    f"{average_latest_rca:.2f}"
)

print(
    f"Sectors with comparative advantage: "
    f"{advantage_count}"
)

print(
    f"Sectors with comparative disadvantage: "
    f"{disadvantage_count}"
)

print(
    f"Improving sectors: "
    f"{len(improving)}"
)

print(
    f"Deteriorating sectors: "
    f"{len(deteriorating)}"
)


# ============================================================
# 23. CHART 1 — RCA TREND
# ============================================================

plt.figure(figsize=(13, 8))

for group in sorted(
    df["SITC_Group"].unique()
):

    group_data = df[
        df["SITC_Group"] == group
    ]

    plt.plot(
        group_data["Year"],
        group_data["RCA"],
        marker="o",
        linewidth=2,
        label=f"SITC {group}"
    )


plt.axhline(
    1,
    linewidth=2,
    linestyle="--",
    label="RCA = 1"
)

plt.title(
    "Revealed Comparative Advantage by SITC Group",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Year")
plt.ylabel("RCA")

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

chart1 = OUTPUT_DIR / "RCA_trends.png"

plt.savefig(
    chart1,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"\n✓ Saved: {chart1}")


# ============================================================
# 24. CHART 2 — LATEST RCA RANKING
# ============================================================

ranking = sector_summary.sort_values(
    "Latest_RCA"
)

plt.figure(figsize=(12, 7))

plt.barh(
    ranking["SITC_Group"].astype(str),
    ranking["Latest_RCA"]
)

plt.axvline(
    1,
    linewidth=2,
    linestyle="--"
)

plt.xlabel("Latest RCA")
plt.ylabel("SITC Group")

plt.title(
    "Lithuania's Latest Revealed Comparative Advantage",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

chart2 = OUTPUT_DIR / "RCA_latest_ranking.png"

plt.savefig(
    chart2,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✓ Saved: {chart2}")


# ============================================================
# 25. CHART 3 — RCA CHANGE
# ============================================================

change_data = sector_summary.sort_values(
    "RCA_Change"
)

plt.figure(figsize=(12, 7))

plt.barh(
    change_data["SITC_Group"].astype(str),
    change_data["RCA_Change"]
)

plt.axvline(
    0,
    linewidth=1
)

plt.xlabel("Change in RCA")
plt.ylabel("SITC Group")

plt.title(
    "Long-Term Change in Lithuania's Comparative Advantage",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

chart3 = OUTPUT_DIR / "RCA_change.png"

plt.savefig(
    chart3,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✓ Saved: {chart3}")


# ============================================================
# 26. CHART 4 — RCA HEATMAP
# ============================================================

heatmap_data = df.pivot_table(
    index="SITC_Group",
    columns="Year",
    values="RCA",
    aggfunc="mean"
)

plt.figure(figsize=(13, 7))

plt.imshow(
    heatmap_data,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(
    label="RCA"
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
    "RCA Evolution Across SITC Groups",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()

chart4 = OUTPUT_DIR / "RCA_heatmap.png"

plt.savefig(
    chart4,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"✓ Saved: {chart4}")


# ============================================================
# 27. CREATE ECONOMIC INTERPRETATION TABLE
# ============================================================

interpretation = sector_summary[
    [
        "SITC_Group",
        "Latest_RCA",
        "RCA_Change",
        "Latest_RCA_Category",
        "Long_Term_Trend",
        "Competitive_Position"
    ]
].copy()


interpretation["Economic_Interpretation"] = np.select(
    [
        interpretation["Competitive_Position"]
        == "Strong and Improving",

        interpretation["Competitive_Position"]
        == "Advantage but Deteriorating",

        interpretation["Competitive_Position"]
        == "Weak but Improving",

        interpretation["Competitive_Position"]
        == "Weak and Deteriorating"
    ],
    [
        "Existing comparative advantage is strengthening.",

        "Lithuania remains competitive, but the advantage is weakening.",

        "The sector remains below RCA=1 but is becoming more competitive.",

        "The sector lacks comparative advantage and competitiveness is deteriorating."
    ],
    default="Competitive position is broadly stable."
)


# ============================================================
# 28. EXPORT EXCEL
# ============================================================

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Detailed RCA",
        index=False
    )

    sector_summary.to_excel(
        writer,
        sheet_name="Sector Summary",
        index=False
    )

    interpretation.to_excel(
        writer,
        sheet_name="Economic Interpretation",
        index=False
    )

    strongest.to_excel(
        writer,
        sheet_name="Comparative Advantage",
        index=False
    )

    weakest.to_excel(
        writer,
        sheet_name="Comparative Disadvantage",
        index=False
    )

    improving.to_excel(
        writer,
        sheet_name="Improving Sectors",
        index=False
    )

    deteriorating.to_excel(
        writer,
        sheet_name="Deteriorating Sectors",
        index=False
    )


# ============================================================
# 29. FORMAT EXCEL
# ============================================================

workbook = load_workbook(
    OUTPUT_FILE
)

for worksheet in workbook.worksheets:

    worksheet.freeze_panes = "A2"

    # Header formatting
    for cell in worksheet[1]:

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    # Column widths
    for column in worksheet.columns:

        max_length = 0

        column_letter = (
            column[0].column_letter
        )

        for cell in column:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            40
        )


workbook.save(
    OUTPUT_FILE
)


# ============================================================
# 30. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("RCA TREND ANALYSIS COMPLETE")
print("=" * 70)

print("\nExcel output:")
print(OUTPUT_FILE)

print("\nCharts created:")
print(f"✓ {chart1.name}")
print(f"✓ {chart2.name}")
print(f"✓ {chart3.name}")
print(f"✓ {chart4.name}")

print("\nAnalysis includes:")
print("✓ RCA trends")
print("✓ RCA = 1 benchmark")
print("✓ Year-on-year RCA changes")
print("✓ Long-term RCA changes")
print("✓ Comparative advantage/disadvantage")
print("✓ Improving sectors")
print("✓ Deteriorating sectors")
print("✓ Sector ranking")
print("✓ Economic interpretation")

print("\n✓ RCA analysis completed successfully.")
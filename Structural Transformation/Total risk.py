# ============================================================
# STRUCTURAL CHANGE ANALYSIS
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

OUTPUT_FILE = OUTPUT_DIR / "Structural_Change_Analysis.xlsx"


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("STRUCTURAL CHANGE ANALYSIS")
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
    "FDI_Inflow_EUR",
    "Tech_Level"
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
        + "\n\nAvailable columns:\n"
        + "\n".join(
            f"  - {column}"
            for column in df.columns
        )
    )


# ============================================================
# 4. CLEAN DATA
# ============================================================

df = df.copy()

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df["FDI_Inflow_EUR"] = pd.to_numeric(
    df["FDI_Inflow_EUR"],
    errors="coerce"
)

df["Tech_Level"] = (
    df["Tech_Level"]
    .astype(str)
    .str.strip()
)

df["SITC_Group"] = (
    df["SITC_Group"]
    .astype(str)
    .str.strip()
)

df = df.dropna(
    subset=[
        "Year"
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
# 5. TECHNOLOGY SCORE
# ============================================================

# Low technology       = 1
# Medium technology    = 2
# High technology      = 3

technology_mapping = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

df["Technology_Score"] = (
    df["Tech_Level"]
    .str.title()
    .map(technology_mapping)
)


# ============================================================
# 6. TECHNOLOGY CHANGE
# ============================================================

df["Technology_Change"] = (
    df.groupby("SITC_Group")[
        "Technology_Score"
    ].diff()
)


df["Technology_Trend"] = np.select(
    [
        df["Technology_Change"] > 0,
        df["Technology_Change"] < 0
    ],
    [
        "Upgrading",
        "Downgrading"
    ],
    default="Stable"
)


# ============================================================
# 7. FDI CHANGE
# ============================================================

df["FDI_Change"] = (
    df.groupby("SITC_Group")[
        "FDI_Inflow_EUR"
    ].diff()
)


df["FDI_Pct_Change"] = np.where(
    df.groupby("SITC_Group")[
        "FDI_Inflow_EUR"
    ].shift(1) != 0,

    (
        df["FDI_Inflow_EUR"]
        /
        df.groupby("SITC_Group")[
            "FDI_Inflow_EUR"
        ].shift(1)
        - 1
    ) * 100,

    np.nan
)


df["FDI_Trend"] = np.select(
    [
        df["FDI_Change"] > 0,
        df["FDI_Change"] < 0
    ],
    [
        "Increasing",
        "Decreasing"
    ],
    default="Stable"
)


# ============================================================
# 8. RCA CHANGE IF AVAILABLE
# ============================================================

if "RCA" in df.columns:

    df["RCA"] = pd.to_numeric(
        df["RCA"],
        errors="coerce"
    )

    df["RCA_Change"] = (
        df.groupby("SITC_Group")[
            "RCA"
        ].diff()
    )

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

else:

    df["RCA"] = np.nan
    df["RCA_Change"] = np.nan
    df["RCA_Trend"] = "Not Available"


# ============================================================
# 9. NORMALISATION FUNCTION
# ============================================================

def normalise(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(
            0.5,
            index=series.index
        )

    if maximum == minimum:
        return pd.Series(
            0.5,
            index=series.index
        )

    return (
        (series - minimum)
        /
        (maximum - minimum)
    )


# ============================================================
# 10. STRUCTURAL CHANGE SCORE
# ============================================================

# Structural change should capture actual movement in
# the economic structure.
#
# Components:
#
# Technology upgrading      40%
# FDI change                30%
# RCA change                30%
#
# Positive score = structural upgrading
# Negative score = structural deterioration


technology_change_score = (
    df["Technology_Change"]
    .fillna(0)
    / 2
)


fdi_change_score = (
    normalise(
        df["FDI_Change"]
    )
    - 0.5
)


if df["RCA_Change"].notna().any():

    rca_change_score = (
        normalise(
            df["RCA_Change"]
        )
        - 0.5
    )

else:

    rca_change_score = pd.Series(
        0,
        index=df.index
    )


df["Structural_Change_Score"] = (

    technology_change_score * 0.40

    +

    fdi_change_score * 0.30

    +

    rca_change_score * 0.30

)


# ============================================================
# 11. STRUCTURAL CHANGE 0–100
# ============================================================

df["Structural_Change_100"] = (
    (
        df["Structural_Change_Score"]
        + 0.5
    )
    * 100
)


df["Structural_Change_100"] = (
    df["Structural_Change_100"]
    .clip(
        lower=0,
        upper=100
    )
)


# ============================================================
# 12. STRUCTURAL CHANGE CATEGORY
# ============================================================

df["Structural_Change_Category"] = np.select(
    [
        df["Structural_Change_100"] >= 75,
        df["Structural_Change_100"] >= 55,
        df["Structural_Change_100"] <= 25,
        df["Structural_Change_100"] <= 45
    ],
    [
        "Strong Upgrading",
        "Moderate Upgrading",
        "Strong Deterioration",
        "Moderate Deterioration"
    ],
    default="Limited Change"
)


# ============================================================
# 13. LONG-TERM SECTOR SUMMARY
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

        First_Technology=(
            "Technology_Score",
            "first"
        ),

        Latest_Technology=(
            "Technology_Score",
            "last"
        ),

        Average_Technology=(
            "Technology_Score",
            "mean"
        ),

        First_FDI=(
            "FDI_Inflow_EUR",
            "first"
        ),

        Latest_FDI=(
            "FDI_Inflow_EUR",
            "last"
        ),

        Average_FDI=(
            "FDI_Inflow_EUR",
            "mean"
        ),

        Average_Structural_Change=(
            "Structural_Change_100",
            "mean"
        ),

        Latest_Structural_Change=(
            "Structural_Change_100",
            "last"
        ),

        First_RCA=(
            "RCA",
            "first"
        ),

        Latest_RCA=(
            "RCA",
            "last"
        )
    )
    .reset_index()
)


# ============================================================
# 14. LONG-TERM CHANGES
# ============================================================

sector_summary["Technology_Change"] = (
    sector_summary["Latest_Technology"]
    -
    sector_summary["First_Technology"]
)


sector_summary["FDI_Change"] = (
    sector_summary["Latest_FDI"]
    -
    sector_summary["First_FDI"]
)


sector_summary["RCA_Change"] = (
    sector_summary["Latest_RCA"]
    -
    sector_summary["First_RCA"]
)


# ============================================================
# 15. TECHNOLOGY CLASSIFICATION
# ============================================================

sector_summary["Technology_Trend"] = np.select(
    [
        sector_summary["Technology_Change"] > 0,
        sector_summary["Technology_Change"] < 0
    ],
    [
        "Upgrading",
        "Downgrading"
    ],
    default="Stable"
)


# ============================================================
# 16. OVERALL STRUCTURAL POSITION
# ============================================================

sector_summary["Structural_Position"] = np.select(
    [
        (
            (sector_summary["Technology_Change"] > 0)
            &
            (sector_summary["RCA_Change"] > 0)
        ),

        (
            (sector_summary["Technology_Change"] > 0)
            &
            (sector_summary["RCA_Change"] < 0)
        ),

        (
            (sector_summary["Technology_Change"] < 0)
            &
            (sector_summary["RCA_Change"] > 0)
        ),

        (
            (sector_summary["Technology_Change"] < 0)
            &
            (sector_summary["RCA_Change"] < 0)
        )
    ],
    [
        "Structural Upgrading",
        "Technology Upgrading but RCA Weakening",
        "RCA Improving but Technology Weakening",
        "Structural Deterioration"
    ],
    default="Limited Structural Change"
)


# ============================================================
# 17. STRUCTURAL CHANGE RANK
# ============================================================

sector_summary["Structural_Rank"] = (
    sector_summary[
        "Average_Structural_Change"
    ]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)


sector_summary = sector_summary.sort_values(
    "Average_Structural_Change",
    ascending=False
)


# ============================================================
# 18. IDENTIFY UPGRADING SECTORS
# ============================================================

upgrading = sector_summary[
    sector_summary["Structural_Position"]
    == "Structural Upgrading"
].copy()


# ============================================================
# 19. IDENTIFY DETERIORATING SECTORS
# ============================================================

deteriorating = sector_summary[
    sector_summary["Structural_Position"]
    == "Structural Deterioration"
].copy()


# ============================================================
# 20. IDENTIFY TECHNOLOGY UPGRADING
# ============================================================

technology_upgrading = sector_summary[
    sector_summary["Technology_Change"] > 0
].copy()


# ============================================================
# 21. PRINT SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("STRUCTURAL CHANGE RANKING")
print("=" * 70)

print(
    sector_summary[
        [
            "Structural_Rank",
            "SITC_Group",
            "Technology_Change",
            "FDI_Change",
            "RCA_Change",
            "Average_Structural_Change",
            "Structural_Position"
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("EXECUTIVE SUMMARY")
print("=" * 70)

print(
    f"\nStructural upgrading sectors: "
    f"{len(upgrading)}"
)

print(
    f"Structural deterioration sectors: "
    f"{len(deteriorating)}"
)

print(
    f"Technology upgrading sectors: "
    f"{len(technology_upgrading)}"
)


# ============================================================
# 22. CHART 1 — TECHNOLOGY EVOLUTION
# ============================================================

technology_trend = (
    df.groupby(
        [
            "Year",
            "Tech_Level"
        ]
    )
    .size()
    .reset_index(
        name="Sector_Count"
    )
)


plt.figure(figsize=(12, 7))

for technology in sorted(
    technology_trend["Tech_Level"].unique()
):

    data = technology_trend[
        technology_trend["Tech_Level"]
        == technology
    ]

    plt.plot(
        data["Year"],
        data["Sector_Count"],
        marker="o",
        linewidth=2,
        label=technology
    )


plt.title(
    "Evolution of Sector Technology Levels",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Year")
plt.ylabel("Number of Sector Observations")

plt.grid(
    True,
    alpha=0.3
)

plt.legend(
    title="Technology Level"
)

plt.tight_layout()

chart1 = (
    OUTPUT_DIR /
    "Technology_Evolution.png"
)

plt.savefig(
    chart1,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 23. CHART 2 — STRUCTURAL CHANGE RANKING
# ============================================================

plot_data = sector_summary.sort_values(
    "Average_Structural_Change"
)

plt.figure(figsize=(12, 7))

plt.barh(
    plot_data["SITC_Group"].astype(str),
    plot_data["Average_Structural_Change"]
)

plt.axvline(
    50,
    linewidth=2,
    linestyle="--",
    label="Neutral point"
)

plt.xlabel(
    "Structural Change Score (0–100)"
)

plt.ylabel(
    "SITC Group"
)

plt.title(
    "Structural Change by SITC Group",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.legend()

plt.tight_layout()

chart2 = (
    OUTPUT_DIR /
    "Structural_Change_Ranking.png"
)

plt.savefig(
    chart2,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 24. CHART 3 — FDI CHANGE VS RCA CHANGE
# ============================================================

plot_data = sector_summary.dropna(
    subset=[
        "FDI_Change",
        "RCA_Change"
    ]
)

plt.figure(figsize=(11, 8))

plt.scatter(
    plot_data["FDI_Change"],
    plot_data["RCA_Change"],
    s=120
)

plt.axhline(
    0,
    linewidth=1
)

plt.axvline(
    0,
    linewidth=1
)

plt.xlabel(
    "Long-Term FDI Change"
)

plt.ylabel(
    "Long-Term RCA Change"
)

plt.title(
    "FDI Change vs Comparative Advantage Change",
    fontsize=16,
    fontweight="bold"
)

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

chart3 = (
    OUTPUT_DIR /
    "FDI_vs_RCA_Structural_Change.png"
)

plt.savefig(
    chart3,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 25. CHART 4 — TECHNOLOGY VS RCA
# ============================================================

latest_year = df["Year"].max()

latest = df[
    df["Year"] == latest_year
].dropna(
    subset=[
        "Technology_Score",
        "RCA"
    ]
)


plt.figure(figsize=(11, 8))

plt.scatter(
    latest["Technology_Score"],
    latest["RCA"],
    s=120
)

plt.axhline(
    1,
    linewidth=2,
    linestyle="--",
    label="RCA = 1"
)

plt.xlabel(
    "Technology Score"
)

plt.ylabel(
    "RCA"
)

plt.title(
    f"Technology Level vs Comparative Advantage — {latest_year}",
    fontsize=16,
    fontweight="bold"
)

plt.xticks(
    [1, 2, 3],
    [
        "Low",
        "Medium",
        "High"
    ]
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

chart4 = (
    OUTPUT_DIR /
    "Technology_vs_RCA.png"
)

plt.savefig(
    chart4,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 26. ECONOMIC INTERPRETATION
# ============================================================

interpretation = sector_summary[
    [
        "SITC_Group",
        "Technology_Change",
        "FDI_Change",
        "RCA_Change",
        "Structural_Position"
    ]
].copy()


interpretation["Economic_Interpretation"] = np.select(
    [
        interpretation["Structural_Position"]
        == "Structural Upgrading",

        interpretation["Structural_Position"]
        == "Structural Deterioration",

        interpretation["Structural_Position"]
        == "Technology Upgrading but RCA Weakening",

        interpretation["Structural_Position"]
        == "RCA Improving but Technology Weakening"
    ],
    [
        "Technology and comparative advantage are both improving, indicating structural upgrading.",

        "Technology and comparative advantage are both weakening, indicating structural deterioration.",

        "Technology is improving, but the sector is losing comparative advantage.",

        "Comparative advantage is improving despite weaker technology characteristics."
    ],
    default="The sector shows limited or mixed structural change."
)


# ============================================================
# 27. EXPORT EXCEL
# ============================================================

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Detailed Analysis",
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

    upgrading.to_excel(
        writer,
        sheet_name="Structural Upgrading",
        index=False
    )

    deteriorating.to_excel(
        writer,
        sheet_name="Structural Deterioration",
        index=False
    )

    technology_upgrading.to_excel(
        writer,
        sheet_name="Technology Upgrading",
        index=False
    )


# ============================================================
# 28. FORMAT EXCEL
# ============================================================

workbook = load_workbook(
    OUTPUT_FILE
)

for worksheet in workbook.worksheets:

    worksheet.freeze_panes = "A2"

    for cell in worksheet[1]:

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

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
# 29. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("STRUCTURAL CHANGE ANALYSIS COMPLETE")
print("=" * 70)

print("\nExcel output:")
print(OUTPUT_FILE)

print("\nCharts created:")
print(f"✓ {chart1.name}")
print(f"✓ {chart2.name}")
print(f"✓ {chart3.name}")
print(f"✓ {chart4.name}")

print("\nAnalysis includes:")
print("✓ Technology upgrading/downgrading")
print("✓ FDI structural changes")
print("✓ RCA structural changes")
print("✓ Structural change score")
print("✓ Sector rankings")
print("✓ Structural upgrading")
print("✓ Structural deterioration")
print("✓ Economic interpretation")

print("\n✓ Structural change analysis completed successfully.")
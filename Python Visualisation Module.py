# ============================================
# 1. Imports
# ============================================
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="whitegrid", font_scale=1.2)

# ============================================
# 2. Load the merged dataset
# ============================================
df = pd.read_excel("Lithuania_Competitiveness_Model.xlsx")

# ============================================
# 3. RCA by Sector (Bar Chart)
# ============================================
plt.figure(figsize=(12,6))
sns.barplot(data=df, x="Sector", y="RCA", hue="Year")
plt.title("RCA by Sector Across Years")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ============================================
# 4. China Pressure Index (Heatmap)
# ============================================
pivot_cpi = df.pivot_table(
    index="SITC_Group",
    columns="Year",
    values="China_Pressure_Index"
)

plt.figure(figsize=(10,6))
sns.heatmap(pivot_cpi, cmap="Reds", annot=True, fmt=".1f")
plt.title("China Pressure Index by SITC Group")
plt.tight_layout()
plt.show()

# ============================================
# 5. Competitiveness Risk Score (Horizontal Bars)
# ============================================
risk_df = df.groupby("Sector")["Total_Risk_Score"].mean().reset_index()

plt.figure(figsize=(12,6))
sns.barplot(data=risk_df, y="Sector", x="Total_Risk_Score", palette="viridis")
plt.title("Average Competitiveness Risk Score by Sector")
plt.tight_layout()
plt.show()

# ============================================
# 6. FDI Structural Change (Scatter Plot)
# ============================================
plt.figure(figsize=(10,6))
sns.scatterplot(
    data=df,
    x="FDI_Inflow_EUR",
    y="RCA",
    hue="Tech_Level",
    size="Structural_Change",
    sizes=(50, 300)
)
plt.title("FDI vs RCA (Structural Change Highlighted)")
plt.tight_layout()
plt.show()

# ============================================
# 7. Vulnerability vs Competitiveness (Bubble Chart)
# ============================================
plt.figure(figsize=(12,7))
sns.scatterplot(
    data=df,
    x="Scale_Vulnerability_Score",
    y="Competitiveness_Risk",
    size="Export_Share_Pct",
    hue="Sector",
    sizes=(50, 500),
    alpha=0.7
)
plt.title("Industrial Vulnerability vs Competitiveness Risk")
plt.tight_layout()
plt.show()

from pathlib import Path
import pandas as pd

# Folder containing Export share.py
SCRIPT_DIR = Path(__file__).resolve().parent

# Main project folder
PROJECT_DIR = SCRIPT_DIR.parent

# Example Excel file in the main project folder
file_path = PROJECT_DIR / "Lithuania_Competitiveness_Model.xlsx"

print("Looking for:")
print(file_path)

if not file_path.exists():
    raise FileNotFoundError(
        f"File not found:\n{file_path}"
    )

df = pd.read_excel(file_path)

print("✓ Dataset loaded")
print(df.head())
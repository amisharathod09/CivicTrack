
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs"

# Load extracted complaints
df = pd.read_csv(OUTPUT_DIR / "complaints.csv")

print("Starting complaints data cleaning...")
print("Original rows:", len(df))


# 1. Remove exact duplicate rows
df = df.drop_duplicates()


# 2. Convert date columns
df["created_at"] = pd.to_datetime(
    df["created_at"], errors="coerce"
)

df["resolved_at"] = pd.to_datetime(
    df["resolved_at"], errors="coerce"
)


# 3. Clean text columns
text_columns = [
    "title",
    "description",
    "priority",
    "status",
    "category_name",
    "department_name",
    "area",
    "city",
    "state"
]

for column in text_columns:
    df[column] = df[column].str.strip()


# 4. Validate priority values
valid_priorities = ["Low", "Medium", "High", "Critical"]

invalid_priorities = df[
    ~df["priority"].isin(valid_priorities)
]

if not invalid_priorities.empty:
    raise ValueError("Invalid priority values found.")


# 5. Validate status values
valid_statuses = [
    "Submitted",
    "Assigned",
    "In Progress",
    "Resolved",
    "Closed",
    "Cancelled"
]

invalid_statuses = df[
    ~df["status"].isin(valid_statuses)
]

if not invalid_statuses.empty:
    raise ValueError("Invalid status values found.")


# 6. Validate required fields
required_columns = [
    "request_id",
    "title",
    "created_at",
    "priority",
    "status"
]

if df[required_columns].isnull().any().any():
    raise ValueError("Missing required values found.")


# 7. Validate date consistency
if (df["resolved_at"] < df["created_at"]).any():
    raise ValueError("Resolution date before creation date found.")

completed = df["status"].isin(["Resolved", "Closed"])

if df.loc[completed, "resolved_at"].isnull().any():
    raise ValueError("Completed complaint missing resolution date.")


# 8. Save cleaned dataset
output_file = OUTPUT_DIR / "cleaned_complaints.csv"

df.to_csv(output_file, index=False)


# 9. Display cleaning report
print("\nCleaning completed successfully!")
print("Final rows:", len(df))
print("Final columns:", len(df.columns))
print("Duplicate rows:", df.duplicated().sum())
print("Missing values:\n", df.isnull().sum())
print("\nSaved to:", output_file)

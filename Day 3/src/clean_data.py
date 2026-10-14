
from pathlib import Path

import pandas as pd


RAW_FILE = Path("data/raw/books_raw.csv")
CLEAN_CSV = Path("data/processed/books_clean.csv")
CLEAN_JSON = Path("data/processed/books_clean.json")


def clean_data():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            "Raw dataset not found. Run src/scraper.py first."
        )

    df = pd.read_csv(RAW_FILE)

    # Standardize text fields.
    for column in ["title", "availability", "rating"]:
        df[column] = df[column].fillna("").astype(str).str.strip()

    # Convert prices such as "£51.77" into numeric values.
    df["price"] = pd.to_numeric(
        df["price"]
        .fillna("")
        .astype(str)
        .str.replace("£", "", regex=False),
        errors="coerce",
    )

    # Remove rows without essential data.
    df = df.dropna(subset=["price"])
    df = df[df["title"] != ""]

    # Remove duplicate products.
    df = df.drop_duplicates(subset=["product_url"])

    # Add a derived field useful for analysis.
    df["price_category"] = df["price"].apply(
        lambda price: (
            "Budget" if price < 20
            else "Mid-range" if price < 40
            else "Premium"
        )
    )

    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(CLEAN_CSV, index=False)
    df.to_json(
        CLEAN_JSON,
        orient="records",
        indent=2,
        force_ascii=False,
    )

    print("\nData cleaning completed.")
    print(f"Clean records: {len(df)}")
    print(f"Missing values per column:\n{df.isna().sum()}")
    print(f"CSV saved to: {CLEAN_CSV}")
    print(f"JSON saved to: {CLEAN_JSON}")


if __name__ == "__main__":
    clean_data()

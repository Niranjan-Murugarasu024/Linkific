from datetime import datetime, timezone
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import sqlalchemy_url

API_URL = "https://jsonplaceholder.typicode.com/posts"

def extract_posts(limit: int = 100) -> list[dict]:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    response = requests.get(API_URL, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("Unexpected API response")
    return payload[:limit]

def transform_posts(posts: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(posts)
    required = {"userId", "id", "title", "body"}
    if not required.issubset(df.columns):
        raise ValueError(f"API response missing: {sorted(required-set(df.columns))}")
    df = df.rename(columns={"userId":"user_id","id":"post_id"})
    df["title"] = df.title.astype("string").str.strip()
    df["body"] = df.body.astype("string").str.strip()
    df["extracted_at"] = datetime.now(timezone.utc)
    return df[["post_id","user_id","title","body","extracted_at"]].drop_duplicates("post_id")

def load_posts(df: pd.DataFrame) -> int:
    engine = create_engine(sqlalchemy_url(), pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS api_posts (
            post_id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,title TEXT NOT NULL,
            body TEXT NOT NULL,extracted_at TIMESTAMPTZ NOT NULL)"""))
        for row in df.itertuples(index=False):
            conn.execute(text("""INSERT INTO api_posts(post_id,user_id,title,body,extracted_at)
                VALUES (:post_id,:user_id,:title,:body,:extracted_at)
                ON CONFLICT(post_id) DO UPDATE SET user_id=EXCLUDED.user_id,
                title=EXCLUDED.title,body=EXCLUDED.body,extracted_at=EXCLUDED.extracted_at"""),
                row._asdict())
    engine.dispose()
    return len(df)

def run(limit: int = 100) -> int:
    df = transform_posts(extract_posts(limit))
    count = load_posts(df)
    print(f"Upserted {count} API posts.")
    return count

if __name__ == "__main__":
    run()

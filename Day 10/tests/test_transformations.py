from src.etl_csv_to_postgres import transform_csv

def test_csv_transform_deduplicates_and_drops_invalid_rows(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text(
        "event_id,event_date,region,orders_count,sales_amount\n"
        "a,2026-10-01, South ,3,10.5\n"
        "a,2026-10-02,South,4,11.5\n"
        "b,not-a-date,West,2,9.0\n"
        "c,2026-10-03,East,-1,7.0\n", encoding="utf-8")
    df = transform_csv(str(path))
    assert len(df) == 1
    assert df.iloc[0]["event_id"] == "a"
    assert df.iloc[0]["region"] == "South"
    assert int(df.iloc[0]["orders_count"]) == 4

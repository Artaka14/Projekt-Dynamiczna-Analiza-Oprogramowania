import pandas as pd
from CDPdata import df_from_entry

def test_df_from_entry_valid():
    df = pd.DataFrame({"bitcoin": [1, 2, 3]}, index=pd.date_range("2024-01-01", periods=3))
    entry = {"json": df.to_json(orient="split")}

    out = df_from_entry(entry)

    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ["bitcoin"]
    assert len(out) == 3


def test_df_from_entry_invalid_json():
    entry = {"json": "{kielbasa XD"}        # Reference
    assert df_from_entry(entry) is None


def test_df_from_entry_empty():
    assert df_from_entry({}) is None
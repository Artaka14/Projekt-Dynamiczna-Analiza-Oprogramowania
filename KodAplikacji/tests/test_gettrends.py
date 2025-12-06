import pandas as pd
from CDPdata import getTrendsData, load_cache

class FakePytrends:
    def __init__(self, df):
        self.df = df
        self.payload = None

    def build_payload(self, kw, cat, timeframe, geo, gprop):
        self.payload = kw

    def interest_over_time(self):
        return self.df


def test_gettrends_fetches_and_saves(monkeypatch):
    df = pd.DataFrame({"bitcoin": [10, 20]}, index=pd.date_range("2024-01-01", periods=2))
    
    monkeypatch.setattr("CDPdata.TrendReq", lambda hl, tz: FakePytrends(df))

    out = getTrendsData("bitcoin", "7d")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 2

    cache = load_cache()
    assert "bitcoin" in cache
    assert "7d" in cache["bitcoin"]


def test_gettrends_uses_cache(monkeypatch):
    # do cache
    df = pd.DataFrame({"bitcoin": [10]}, index=pd.date_range("2024-01-01", periods=1))
    monkeypatch.setattr("CDPdata.TrendReq", lambda hl, tz: FakePytrends(df))

    _ = getTrendsData("bitcoin", "7d")

    # pytrends NIE powinien być wywołany
    def fail_pytrends(*a, **kw):
        raise AssertionError("Nie powinno być zapytania do pytrends!")

    monkeypatch.setattr("CDPdata.TrendReq", fail_pytrends)

    out = getTrendsData("bitcoin", "7d")
    assert len(out) == 1    # z cache


def test_gettrends_fallback_on_error(monkeypatch):
    # zapisujemy JAKIEKOLWIEK dane do cache
    df = pd.DataFrame({"bitcoin": [10]}, index=pd.date_range("2024-01-01", periods=1))
    monkeypatch.setattr("CDPdata.TrendReq", lambda hl, tz: FakePytrends(df))
    _ = getTrendsData("bitcoin", "7d")

    # wymuszamy błąd API
    def exploding_pytrends(*a, **kw):
        raise Exception("API ERROR")

    monkeypatch.setattr("CDPdata.TrendReq", exploding_pytrends)

    out = getTrendsData("bitcoin", "7d")
    assert len(out) == 1    # fallback działa
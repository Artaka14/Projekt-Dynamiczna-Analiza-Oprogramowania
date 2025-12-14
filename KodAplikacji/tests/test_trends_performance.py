import time
import pandas as pd
from CDPdata import save_cache, getTrendsData

KEYWORD = "CD Projekt"
PERIOD = "7d"

def test_cache_read_is_fast(tmp_path, monkeypatch):
    # duży DataFrame
    df = pd.DataFrame(
        {"CD Projekt": range(365)},
        index=pd.date_range("2023-01-01", periods=365)
    )

    save_cache({
        KEYWORD: {
            PERIOD: {
                "period": PERIOD,
                "json": df.to_json(orient="split")
            }
        }
    })

    # pomiar czasu
    start = time.perf_counter()
    result = getTrendsData(KEYWORD, PERIOD)
    elapsed = time.perf_counter() - start

    assert result is not None
    assert len(result) == 365

    # twardy limit (twitch chat mowi ze lokalnie powinno być < 10 ms)
    assert elapsed < 0.05  # 50 ms
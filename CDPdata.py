import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import json, os

#Funkcja, która zdobywa informacje o kursie CDPu do wykresu
def getCdpData(period): 
    end_time = datetime.now()

    if end_time.weekday() >= 5: 
       days_to_subtract = end_time.weekday() - 4 
       end_time -= timedelta(days=days_to_subtract)

    if period == "1d":
        start_time = end_time - timedelta(days=1)
        interval = "1m"
    elif period == "7d":
        start_time = end_time - timedelta(days=7)
        interval = "1m"
    elif period == "1m":
        start_time = end_time - timedelta(days=30)
        interval = "15m"

    data = yf.download("CDR.WA", start=start_time, end=end_time, interval=interval, progress=False)

    if data.empty:
        raise ValueError("Brak danych dla wybranego okresu.")

    data = data.reset_index(drop=False)
    data["sample_index"] = range(len(data))

    return data

#Funkcja, która zdobywa informacje o kursie CDPu dla customowej daty wybranej przez u¿ytkownika
def getCustomCdpData(start_time, end_time): 

    if end_time.weekday() >= 5: 
       days_to_subtract = end_time.weekday() - 4 
       end_time -= timedelta(days=days_to_subtract)

    time_difference = (end_time - start_time).days
    if time_difference <= 3:
        interval = "1m"
    elif time_difference <= 14:
        interval = "5m"
    elif time_difference <= 30:
        interval = "15m"
    elif time_difference <= 250:
        interval = "1h"  
    else:
        interval = "1d"
    data = yf.download("CDR.WA", start=start_time, end=end_time, interval = interval, progress=False)

    if data.empty:
        raise ValueError("Brak danych dla wybranego okresu.")

    data = data.reset_index(drop=False)
    data.rename(columns={'Date': 'Datetime'}, inplace=True)
    data["sample_index"] = range(len(data))

    return data

#Funkcja, która pobiera informacje o kursie
def getCurrentPrice():
    ticker = yf.Ticker("CDR.WA")
    data = ticker.history(period="1d", interval="1m")
    if not data.empty:
        return round(data["Close"].iloc[-1], 2)
    return None

#Funkcja szukająca minimalnej i maksymalnej wartości 
def getMinMaxPrice(data=None):
    min_val = data["Close"].min()
    max_val = data["Close"].max()

    if isinstance(min_val, pd.Series):
        min_val = min_val.iloc[0]
    if isinstance(max_val, pd.Series):
        max_val = max_val.iloc[0]

    min_price = round(float(min_val), 2)
    max_price = round(float(max_val), 2)

    return min_price, max_price

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR  = os.path.join(BASE_DIR, "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "trends_cache.json")

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def load_cache():
    """Wczytaj cache; jeśli plik uszkodzony -> przenieś do *.bad.json i zwróć pusty."""
    ensure_cache_dir()
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                return {}
            return json.loads(txt)
    except Exception as e:
        # odsuń zły plik i pozwól pobrać na nowo
        bad_name = os.path.join(
            CACHE_DIR,
            f"trends_cache.bad.{int(time.time())}.json"
        )
        try:
            os.replace(CACHE_FILE, bad_name)
            print(f"Uszkodzony cache przeniesiono do: {bad_name} ({e})")
        except Exception:
            pass
        return {}

def save_cache(cache: dict):
    """Atomowy zapis cache (do pliku tymczasowego + replace)."""
    ensure_cache_dir()
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CACHE_FILE)

def invalidate_trends_period(period: str):
    """Dobrowolnie: usuń z cache tylko dany okres (np. '7d'), żeby wymusić ponowne pobranie."""
    cache = load_cache()
    if period in cache:
        cache.pop(period, None)
        save_cache(cache)
        print(f"Usunięto z cache okres: {period}")

def timeframe_for(period: str) -> str:
    if period == "1d":
        return "now 1-d"
    if period == "7d":
        return "now 7-d"
    if period == "1m":
        return "today 1-m"
    # fallback
    return "today 3-m"

def df_from_entry(entry: dict) -> pd.DataFrame | None:
    """Z enkapsulowanego wpisu cache -> DataFrame (walidacja)."""
    if not entry or "json" not in entry:
        return None
    try:
        df = pd.read_json(entry["json"], orient="split")
        if df.empty:
            return None
        # porządek: jeśli jest kolumna isPartial, wyrzuć
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])
        return df
    except Exception as e:
        print(f"Błąd odczytu wpisu cache: {e}")
        return None

def getTrendsData(period: str) -> pd.DataFrame | None:
    """
    Zwraca DataFrame dla 'period' z cache (jeśli OK),
    a jeśli brak/zepsuty -> pobiera z Google i bezpiecznie zapisuje.
    """
    cache = load_cache()

    # Spróbuj z cache
    if period in cache:
        df = df_from_entry(cache[period])
        if df is not None and not df.empty:
            print(f"Wczytano {period} z cache (wierszy: {len(df)})")
            return df
        else:
            # zepsuty wpis -> usuń i kontynuuj pobieranie
            print(f"Wpis cache dla {period} jest niepoprawny; pobieram ponownie…")
            cache.pop(period, None)
            save_cache(cache)

    # Pobierz z Google
    print(f"Pobieranie Google Trends dla: {period}")
    pytrends = TrendReq(hl="pl-PL", tz=360)
    timeframe = timeframe_for(period)

    try:
        pytrends.build_payload(["CD Projekt"], cat=0, timeframe=timeframe, geo="", gprop="")
        df = pytrends.interest_over_time()
        if df.empty:
            print("Puste dane Google Trends")
            return None
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        # 3) Zapisz do cache
        entry = {
            "period": period,
            "timeframe": timeframe,
            "saved_at": datetime.now().isoformat(),
            "json": df.to_json(orient="split"),  # trzymamy jako string JSON
        }
        cache[period] = entry
        save_cache(cache)
        print(f"Zapisano {period} do cache")
        return df

    except Exception as e:
        print(f"Błąd pobierania Trends: {e}")
        return None

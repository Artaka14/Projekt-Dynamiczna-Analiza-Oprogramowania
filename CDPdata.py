import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq

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

CACHE_DIR = "cache"

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def getTrendsData(period):
        
    ensure_cache_dir()
    CACHE_FILE = os.path.join(CACHE_DIR, f"trends_{period}.json")
    
    # jeśli istnieje cache
    if os.path.exists(CACHE_FILE):
        try:
            print(f"Wczytano dane Trends z pliku cache ({CACHE_FILE})")
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            df = pd.DataFrame.from_dict(cached)
            df.index = pd.to_datetime(df.index)
            return df
        except Exception as e:
            print(f"Nie udało się wczytać pliku cache ({e}), pobieram nowe dane...")

    # Jeśli nie ma cache — pobierz z Google
    print(f"Pobieranie danych Trends ({period}) z Google...")
    pytrends = TrendReq(hl="pl-PL", tz=360)

    if period == "1d":
        timeframe = "now 1-d"
    elif period == "7d":
        timeframe = "now 7-d"
    elif period == "1m":
        timeframe = "today 1-m"
    else:
        timeframe = "today 12-m"

    pytrends.build_payload(["CD Projekt"], cat=0, timeframe=timeframe, geo="", gprop="")
    df = pytrends.interest_over_time()

    if df.empty:
        print("Nie udało się pobrać danych z Google Trends.")
        return None

    # Usuń kolumnę isPartial, jeśli istnieje
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])

    # Zapisz do pliku cache w formacie JSON
    df_to_save = df.copy()
    df_to_save.index = df_to_save.index.astype(str)

    # Tu jest ważna poprawka — zapisujemy DataFrame.to_dict()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(df_to_save.to_dict(orient="index"), f, ensure_ascii=False, indent=2)

    print(f"Zapisano dane do cache: {CACHE_FILE}")
    return df

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import json, os, time
import os
import requests
import tkinter as tk
from tkinter import filedialog

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

#Wczytuje cache, jeśli plik uszkodzony -> przenosi do *.bad.json i zwraca pusty
def load_cache():
    
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

#Atomowy zapis cache (do pliku tymczasowego + replace)
def save_cache(cache: dict):
    ensure_cache_dir()
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CACHE_FILE)

#Usuwa z cache tylko dany okres (np. '7d'), żeby wymusić ponowne pobranie
def invalidate_trends_period(keyword: str,period: str):
    cache = load_cache()
    if keyword in cache and period in cache[keyword]:
        cache[keyword].pop(period, None)
        if not cache[keyword]:
            cache.pop(keyword, None)
        save_cache(cache)
        print(f"Usunięto cache dla: {keyword} / {period}")

    safe_kw = keyword.replace(" ", "_").lower()
    filename = f"cache/{safe_kw}_{period}.json"

    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Usunięto plik: {filename}")
        else:
            print(f"Plik już nie istnieje: {filename}")
    except Exception as e:
        print(f"Błąd przy usuwaniu pliku {filename}: {e}")
              
def timeframe_for(period: str) -> str:
    if period == "1d":
        return "now 1-d"
    if period == "7d":
        return "now 7-d"
    if period == "1m":
        return "today 1-m"
    # fallback
    return "today 3-m"

#Z enkapsulowanego wpisu cache -> DataFrame (walidacja)
def df_from_entry(entry: dict) -> pd.DataFrame | None:
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

#Zwraca DataFrame dla 'period' z cache (jeśli OK),a jeśli brak/zepsuty -> pobiera z Google i bezpiecznie zapisuje
def getTrendsData(keyword: str, period: str) -> pd.DataFrame | None:
    cache = load_cache()

    if keyword in cache and period in cache[keyword]:
        df = df_from_entry(cache[keyword][period])
        if df is not None:
            print(f"Wczytano z cache: {keyword} / {period} (wiersze: {len(df)})")
            return df
        else:
            # usuwamy uszkodzony wpis i zapisujemy cache bez niego
            cache[keyword].pop(period, None)
            if not cache[keyword]:
                cache.pop(keyword, None)
            save_cache(cache)
            print(f"Usunięto uszkodzony wpis cache: {keyword} / {period}")

    #Pobieranie z Google (pytrends)
    print(f"Pobieranie Google Trends: {keyword} / {period}")
    pytrends = TrendReq(hl="pl-PL", tz=360)
    timeframe = timeframe_for(period)
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo="", gprop="")
        df = pytrends.interest_over_time()
        if df.empty:
            print("Google zwróciło puste dane")
            return None
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        #Zapisywanie do cache w postaci JSON-stringa orient='split'
        entry = {
            "period": period,
            "timeframe": timeframe,
            "saved_at": datetime.now().isoformat(),
            "json": df.to_json(orient="split")
        }
        cache.setdefault(keyword, {})[period] = entry
        save_cache(cache)
        print(f"Zapisano cache: {keyword} / {period}")
        return df

    except Exception as e:
        print(f"Błąd pytrends/pobierania: {e}")
        return None

# SŁOWNIK KWARTAŁÓW
QUARTER_REPORTS = {
    # ===== 2025 =====
    "III 2025": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2025-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/11/podstawowe-dane-finansowe-q3-2025.xlsx",
        "press_pdf" : "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/11/informacja-prasowa-wyniki-q3-2025.pdf"
    },
    "I 2025": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2025-r.pdf",
        "xlsx":"https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/11/podstawowe-dane-finansowe-q3-2025.xlsx",
        "press_pdf" : "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/11/informacja-prasowa-wyniki-q3-2025.pdf"
    },
    "II 2025": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/05/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-i-kwartal-2025-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/05/podstawowe-dane-finansowe-q1-2025.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2025/05/informacja-prasowa-wyniki-q1-2025.pdf"
    },

    # ===== 2024 =====
    "I 2024": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/05/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-i-kwartal-2024-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/05/podstawowe-dane-finansowe-q1-2024.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/05/informacja-prasowa-wyniki-q1-2024.pdf"
    },
    "II 2024": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/05/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-i-kwartal-2024-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/05/podstawowe-dane-finansowe-q1-2024.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/05/informacja-prasowa-wyniki-q1-2024.pdf"
    },
    "III 2024": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2024-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/11/podstawowe-dane-finansowe-q3-2024.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/11/informacja-prasowa-wyniki-q3-2024.pdf"
    },
    "IV 2024": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2024-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/11/podstawowe-dane-finansowe-q3-2024.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2024/11/informacja-prasowa-wyniki-q3-2024.pdf"
    },

    # ===== 2023 =====
    "I 2023": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/05/skonsolidowane-sprawozdanie-finansowe-grupy-cd-projekt-za-q1-2023.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/05/podstawowe-dane-finansowe-q1-2023.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/05/informacja-prasowa-wyniki-q1-2023.pdf"
    },
    "II 2023": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/05/skonsolidowane-sprawozdanie-finansowe-grupy-cd-projekt-za-q1-2023.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/05/podstawowe-dane-finansowe-q1-2023.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/05/informacja-prasowa-wyniki-q1-2023.pdf"
    },
    "III 2023": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2023-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/11/podstawowe-dane-finansowe-q3-2023.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/11/informacja-prasowa-wyniki-q3-2023.pdf"
    },
    "IV 2023": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2023-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/11/podstawowe-dane-finansowe-q3-2023.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2023/11/informacja-prasowa-wyniki-q3-2023.pdf"
    },

    # ===== 2022 =====
    "I 2022": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/05/sf-skonsolidowane-q1-2022.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/05/podstawowe-dane-finansowe-q1-2022.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/05/informacja-prasowa-wyniki-q1-2022.pdf"
    },
    "II 2022": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/05/sf-skonsolidowane-q1-2022.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/05/podstawowe-dane-finansowe-q1-2022.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/05/informacja-prasowa-wyniki-q1-2022.pdf"
    },
    "III 2022": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2022-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/11/podstawowe-dane-finansowe-q3-2022.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/11/informacja-prasowa-wyniki-q3-2022.pdf"
    },
    "IV 2022": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/11/skonsolidowane-sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2022-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/11/podstawowe-dane-finansowe-q3-2022.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2022/11/informacja-prasowa-wyniki-q3-2022.pdf"
    },

    # ===== 2021 =====
    "I 2021": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/05/srodroczne-skrocone-skonsolidowane-sprawozdanie-finansowe-za-i-kw-2021.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/05/podstawowe-dane-finansowe-q1-2021-1.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/05/informacja-prasowa-wyniki-q1-2021.pdf"
    },
    "II 2021": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/05/srodroczne-skrocone-skonsolidowane-sprawozdanie-finansowe-za-i-kw-2021.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/05/podstawowe-dane-finansowe-q1-2021-1.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/05/informacja-prasowa-wyniki-q1-2021.pdf"
    },
    "III 2021": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/11/skonsolidowane-sprawozdanie-finansowe-za-iii-kwartal-2021-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/11/podstawowe-dane-finansowe-q3-2021.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/11/informacja-prasowa-wyniki-q3-2021.pdf"
    },
    "IV 2021": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/11/skonsolidowane-sprawozdanie-finansowe-za-iii-kwartal-2021-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/11/podstawowe-dane-finansowe-q3-2021.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/11/informacja-prasowa-wyniki-q3-2021.pdf"
    },

    # ===== 2020 =====
    "I 2020": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/05/sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-1-kw-2020-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/05/podstawowe-dane-finansowe_q1-2020.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/05/press-q1_pl.pdf"
    },
    "II 2020": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/05/sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-1-kw-2020-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/05/podstawowe-dane-finansowe_q1-2020.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/05/press-q1_pl.pdf"
    },
    "III 2020": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/11/spr_fin_skons_-q3_2020.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/04/podstawowe-dane-finansowe-q3-2020.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/11/informacja-prasowa-wyniki-za-iii-kwartal-2020-r.pdf"
    },
    "IV 2020": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/11/spr_fin_skons_-q3_2020.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2021/04/podstawowe-dane-finansowe-q3-2020.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2020/11/informacja-prasowa-wyniki-za-iii-kwartal-2020-r.pdf"
    },

    # ===== 2019 =====
    "I 2019": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/05/spr_fin_-q1_2019_signed-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/05/podstawowe-dane-finansowe_q1-2019.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/05/grupa-cd-projekt-podsumowuje-poczatek-roku-informacja-prasowa.pdf"
    },
    "II 2019": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2019-r-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/podstawowe-dane-finansowe_q3-2019.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/informacja-prasowa-wyniki-q3-2019.pdf"
     },
    "III 2019": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2019-r-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/podstawowe-dane-finansowe_q3-2019.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/informacja-prasowa-wyniki-q3-2019.pdf"
    },
    "IV 2019": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/sprawozdanie-finansowe-grupy-kapitalowej-cd-projekt-za-iii-kwartal-2019-r-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/podstawowe-dane-finansowe_q3-2019.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2019/11/informacja-prasowa-wyniki-q3-2019.pdf"
    },

    # ===== 2018 =====
    "I 2018": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/05/spr_fin_-q1_2018-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/05/podstawowe-dane-finansowe_q1-2018.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/05/informacja-prasowa_pl.pdf"
    },
    "II 2018": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/srodroczne-skrocone-skonsolidowane-sprawozdanie-finansowe-za-3-kw-2018-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/podstawowe-dane-finansowe_q3-2018-1.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/cd-projekt-podsumowuje-trzeci-kwartal-2018-r-1.pdf"
   },
    "III 2018": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/srodroczne-skrocone-skonsolidowane-sprawozdanie-finansowe-za-3-kw-2018-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/podstawowe-dane-finansowe_q3-2018-1.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/cd-projekt-podsumowuje-trzeci-kwartal-2018-r-1.pdf"
    },
    "IV 2018": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/srodroczne-skrocone-skonsolidowane-sprawozdanie-finansowe-za-3-kw-2018-r.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/podstawowe-dane-finansowe_q3-2018-1.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2018/11/cd-projekt-podsumowuje-trzeci-kwartal-2018-r-1.pdf"
    },

    # ===== 2017 =====
    "I 2017": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/05/2017_qsr1_spraw-2.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/01/podstawowe-dane-finansowe-2017q1.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/05/1q-2017-cd-projekt-informacja-prasowa.pdf"
    },
    "II 2017": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/11/spr_fin_skons_-q3_2017-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/01/podstawowe-dane-finansowe_3q2017.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/11/grupa-cd-projekt-informacja-prasowa-3q-2017.pdf"
    },
    "III 2017": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/11/spr_fin_skons_-q3_2017-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/01/podstawowe-dane-finansowe_3q2017.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/11/grupa-cd-projekt-informacja-prasowa-3q-2017.pdf"
    },
    "IV 2017": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/11/spr_fin_skons_-q3_2017-1.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/01/podstawowe-dane-finansowe_3q2017.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2017/11/grupa-cd-projekt-informacja-prasowa-3q-2017.pdf"
    },

    # ===== 2016 =====
    "I 2016": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/05/2016_qsr1_spraw.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/05/podstawowe-dane-firnsowe-w-xls-1-kw-2016-r.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/05/20160512-cd-projekt-publikuje-solidne-wyniki-za-pierwszy-kwartal-2016-roku-informacja-prasowa.pdf"
    },
    "II 2016": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/skonsolidowane-sprawozdanie-finansowe_q3-2016.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/podstawowe_dane_finansowe_2016q3.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/wysoka-sprzedazcc87-gry-wiedzmin-3-dziki-gon-i-dodatkow-napecca8dza-wyniki-grupy-cd-projekt-informacja-prasowa.pdf"
     },
    "III 2016": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/skonsolidowane-sprawozdanie-finansowe_q3-2016.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/podstawowe_dane_finansowe_2016q3.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/wysoka-sprzedazcc87-gry-wiedzmin-3-dziki-gon-i-dodatkow-napecca8dza-wyniki-grupy-cd-projekt-informacja-prasowa.pdf"
    },
    "IV 2016": {
        "pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/skonsolidowane-sprawozdanie-finansowe_q3-2016.pdf",
        "xlsx": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/podstawowe_dane_finansowe_2016q3.xlsx",
        "press_pdf": "https://www.cdprojekt.com/pl/wp-content/uploads-pl/2016/11/wysoka-sprzedazcc87-gry-wiedzmin-3-dziki-gon-i-dodatkow-napecca8dza-wyniki-grupy-cd-projekt-informacja-prasowa.pdf"
    },
}
#FUNKCJE

#Wyświetla okno wyboru folderu i zwraca jego ścieżkę
def choose_folder() -> str:
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Wybierz folder do pobierania raportów")
    root.destroy()
    if not folder:
        folder = os.path.join(os.path.dirname(__file__), "downloads")
        os.makedirs(folder, exist_ok=True)
    return folder

# Pobiera plik z internetu do folderu wybranego przez użytkownika
def download_file(url: str, default_name: str) -> str:
    folder = choose_folder()
    path = os.path.join(folder, default_name)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return path
    except Exception as e:
        print(f"Błąd pobierania {url}: {e}")
        return ""



import yfinance as yf
from datetime import datetime, timedelta

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
#Funkcja, która pobiera informacje o kursie
def getCurrentPrice():
    ticker = yf.Ticker("CDR.WA")
    data = ticker.history(period="1d", interval="1m")
    if not data.empty:
        return round(data["Close"].iloc[-1], 2)
    return None

#Funkcja szukająca minimalnej i maksymalnej wartości 
def getMinMaxPrice(data=None, period="7d"):
    min_price = round(float(data["Close"].min()), 2)
    max_price = round(float(data["Close"].max()), 2)
    return min_price, max_price




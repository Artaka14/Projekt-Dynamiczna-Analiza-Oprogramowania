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

def getTrendsData():
        
    pytrends = TrendReq(hl="pl-PL", tz=360)
    pytrends.build_payload(["CD Projekt"], cat=0,timeframe="today 12-m", geo='', gprop='')
    data = pytrends.interest_over_time()
    if data.empty or data is None:
        raise ValueError("Brak danych z Google Trends dla tego okresu.")
    
    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])
    
    data = data.reset_index()
    data["sample_index"] = range(len(data))
    return data

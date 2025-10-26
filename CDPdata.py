import yfinance as yf

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



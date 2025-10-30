import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import CDPdata
import main
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#Funkcja tworząca wykres
def createCdpPlot(frame, period, data):
    if period == "1d":
       periodName = "1 dzień"
    elif period == "7d":
        periodName = "7 dni"
    elif period == "1m":
        periodName = "1 miesiąc"
        period = "1mo"

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(data["sample_index"], data["Close"], label="CD Projekt S.A.")
    ax.set_title(f"CD Projekt S.A. — okres: {periodName}")
    ax.set_ylabel("Cena (PLN)")

    session_bounds = data.groupby(data["Datetime"].dt.date)["sample_index"].agg(['min', 'max'])

    ticks = session_bounds['min'].tolist()
    labels = [str(d) for d in session_bounds.index]
    ticks.append(session_bounds['max'].iloc[-1])
    labels.append(str(session_bounds.index[-1]+timedelta(days=1)))

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45)

    ax.set_xlim(data['sample_index'].min(), data['sample_index'].max())

    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def createCustomDataCdpPlot(frame, start_date, end_date, data):
    if data.empty:
       raise ValueError("Brak danych dla wybranego zakresu.")

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(data["sample_index"], data["Close"], label="CD Projekt S.A.")
    ax.set_title(f"CD Projekt S.A. — {start_date} → {end_date}")
    ax.set_ylabel("Cena (PLN)")

    session_bounds = data.groupby(data["Datetime"].dt.date)["sample_index"].agg(['min', 'max'])

    data = data.copy()
    data["date"] = pd.to_datetime(data["Datetime"].dt.date)

    session_bounds = data.groupby("date")["sample_index"].agg(["min", "max"])
    total_days = (data["date"].max() - data["date"].min()).days

    miesiace = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]

    if total_days <= 14:  
        ticks = session_bounds["min"].tolist()
        labels = [d.strftime("%d %b %Y") for d in session_bounds.index]
        ticks.append(session_bounds["max"].iloc[-1])
        labels.append((session_bounds.index[-1] + pd.Timedelta(days=1)).strftime("%d %b %Y"))
    else: 
        first_day = session_bounds.index.min()
        last_day = session_bounds.index.max()

        month_starts = []
        current = pd.Timestamp(first_day.replace(day=1))
        while current <= last_day:
            month_starts.append(current)
            year = current.year + (current.month // 12)
            month = 1 if current.month == 12 else current.month + 1
            current = pd.Timestamp(year=year, month=month, day=1)

        ticks = []
        for m in month_starts:
            if m in session_bounds.index:
                ticks.append(session_bounds.loc[m, "min"])
            else:
                nearest = min(session_bounds.index, key=lambda x: abs((x - m).days))
                ticks.append(session_bounds.loc[nearest, "min"])

        labels = [f"{miesiace[m.month - 1]} {m.year}" for m in month_starts]

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45)

    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
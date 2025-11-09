import matplotlib.pyplot as plt
import yfinance as yf
import customtkinter
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
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

#Funkcja do generowania wykresu z customową datą
def createCustomDataCdpPlot(frame, start_date, end_date, data):
    if data.empty:
        raise ValueError("Brak danych dla wybranego zakresu.")

    data = data.copy()
    data["date"] = pd.to_datetime(data["Datetime"].dt.date)
    session_bounds = data.groupby("date")["sample_index"].agg(["min", "max"])
    total_days = (data["date"].max() - data["date"].min()).days

    first_day = session_bounds.index.min()
    last_day = session_bounds.index.max()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data["sample_index"], data["Close"], label="CD Projekt S.A.")
    ax.set_title(f"CD Projekt S.A. — {start_date} → {end_date}")
    ax.set_ylabel("Cena (PLN)")

    miesiace = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]

    if total_days <= 85:
        ticks = session_bounds["min"].tolist()
        labels = [d.strftime("%d %b %Y") for d in session_bounds.index]
        ticks.append(session_bounds["max"].iloc[-1])
        labels.append((session_bounds.index[-1] + pd.Timedelta(days=1)).strftime("%d %b %Y"))

    elif total_days <= 800:
        month_starts = []
        current = pd.Timestamp(first_day.replace(day=1))
        while current <= last_day:
            month_starts.append(current)
            year = current.year + (current.month // 12)
            month = 1 if current.month == 12 else current.month + 1
            current = pd.Timestamp(year=year, month=month, day=1)

        ticks = []
        for m in month_starts:
            nearest = min(session_bounds.index, key=lambda x: abs((x - m).days))
            ticks.append(session_bounds.loc[nearest, "min"])

        labels = [f"{miesiace[m.month - 1]} {m.year}" for m in month_starts]

    elif total_days <= 1500:
        quarter_starts = []
        current = pd.Timestamp(first_day.replace(month=1, day=1))
        while current <= last_day:
            for month in [1, 4, 7, 10]:
                q_date = pd.Timestamp(year=current.year, month=month, day=1)
                if first_day <= q_date <= last_day:
                    quarter_starts.append(q_date)
            current = pd.Timestamp(year=current.year + 1, month=1, day=1)

        ticks = []
        for q in quarter_starts:
            nearest = min(session_bounds.index, key=lambda x: abs((x - q).days))
            ticks.append(session_bounds.loc[nearest, "min"])

        labels = [f"Q{((q.month - 1)//3) + 1} {q.year}" for q in quarter_starts]

    else:
        year_starts = []
        current = pd.Timestamp(first_day.replace(month=1, day=1))
        while current <= last_day:
            year_starts.append(current)
            current = pd.Timestamp(year=current.year + 1, month=1, day=1)

        ticks = []
        for y in year_starts:
            nearest = min(session_bounds.index, key=lambda x: abs((x - y).days))
            ticks.append(session_bounds.loc[nearest, "min"])

        labels = [str(y.year) for y in year_starts]

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45)
    ax.tick_params(axis='x', labelsize=9)
    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def createTrendsPlot(frame, period, data):

    if data is None or data.empty:
        label = customtkinter.CTkLabel(frame, text="Nie udało się pobrać danych z Google Trends", text_color="red")
        label.pack(expand=True)
        return

    fig, ax = plt.subplots(figsize=(8, 3))

    end = data.index.max()
    if period == "1d":
        start = end - timedelta(days=1)
    elif period == "7d":
        start = end - timedelta(days=7)
    elif period == "1m":
        start = end - timedelta(days=30)
    else:
        start = data.index.min()

    filtered = data.loc[start:end]

    ax.plot(filtered.index, filtered["CD Projekt"], label="Zainteresowanie wyszukiwań CD Projekt")
    ax.set_title("Popularność wyszukiwań (Google Trends)")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
def showError(frame, message="Nie udało się pobrać danych"):
    for widget in frame.winfo_children():
        widget.destroy()
    error_label = customtkinter.CTkLabel(
        frame,
        text=message,
        font=("Arial", 16, "bold"),
        text_color="red"
    )
    error_label.pack(expand=True)

    canvas.get_tk_widget().pack(fill="both", expand=True)




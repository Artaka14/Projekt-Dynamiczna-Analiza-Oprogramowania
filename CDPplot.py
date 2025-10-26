import matplotlib.pyplot as plt
import yfinance as yf
import CDPdata
import main
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from CTkMessagebox import CTkMessagebox

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

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()

    canvas.get_tk_widget().pack(fill="both", expand=True)

def createCustomDataCdpPlot(frame, start_date, end_date, data):
        today = datetime.now().date()

        if start_date > end_date:
            CTkMessagebox(
                title="Błędny zakres dat",
                message="Data początkowa nie może być późniejsza niż końcowa.",
                icon="cancel"
            )
            return

        if start_date > today or end_date > today:
            CTkMessagebox(
                title="Błędny zakres dat",
                message="Nie można wybrać dat z przyszłości.",
                icon="warning"
            )
            return
            
        if data.empty:
           raise ValueError("Brak danych dla wybranego zakresu.")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(data.index, data["Close"], label="CD Projekt S.A.")
        ax.set_title(f"CD Projekt S.A. — {start_date} → {end_date}")
        ax.set_ylabel("Cena (PLN)")

        session_bounds = data.groupby(data["Datetime"].dt.date)["sample_index"].agg(['min', 'max'])
        ticks = session_bounds['min'].tolist()
        labels = [str(d) for d in session_bounds.index]
        ticks.append(session_bounds['max'].iloc[-1])
        labels.append(str(session_bounds.index[-1]+timedelta(days=1)))

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45)

        ax.grid(True)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


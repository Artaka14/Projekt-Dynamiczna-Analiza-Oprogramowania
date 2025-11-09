import time
import customtkinter
import threading
import main
import CDPdata
from PIL import Image

class SplashScreen(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ekran startowy")

        width, height = 400, 250
        self.geometry(f"{width}x{height}+{self.center_x(width)}+{self.center_y(height)}")
        self.resizable(False, False)
        self.overrideredirect(True)

        # XDlogo
        self.logo = customtkinter.CTkImage(light_image=Image.open("asety\XDlogo.png"), size=(400, 250))
        customtkinter.CTkLabel(self, image=self.logo, text="").pack()

        # pobierańsko w tle
        threading.Thread(target=self.load_data_with_delay, daemon=True).start()

    def center_x(self, window_width):
        screen_width = self.winfo_screenwidth()
        return int((screen_width / 2) - (window_width / 2))

    def center_y(self, window_height):
        screen_height = self.winfo_screenheight()
        return int((screen_height / 2) - (window_height / 2))

    def load_data_with_delay(self):
        start_time = time.time()
        try:
            data = CDPdata.getCdpData("7d")
        except Exception as e:
            print("Błąd pobierania danych:", e)
            data = None
            
        try:
            trends_data = CDPdata.getTrendsData("7d")
        except Exception as e:
            print("Błąd pobierania danych - trends:", e)
            trends_data=None

        elapsed = time.time() - start_time
        if elapsed < 2.5:
            time.sleep(2.5 - elapsed)

        self.after(0, lambda: self.open_main_app(data,trends_data))

    def open_main_app(self, data, trends_data):
        self.destroy()
        app = main.App(preloaded_data=data, preloaded_trends=trends_data)
        app.mainloop()

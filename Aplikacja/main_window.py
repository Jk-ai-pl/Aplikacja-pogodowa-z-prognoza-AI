import tkinter as tk
import sys
from data_gminy import WOJEWODZTWA, GMNY, update_gminy
from weather import pobierz

def main():
    root = tk.Tk()
    root.title("Polska Pogoda")
    root.geometry("500x450")
    root.resizable(False, False)

    tk.Label(root, text="Aplikacja Pogodowa Z Użyciem AI", font=("Arial", 16, "bold")).pack(pady=10)

    def on_close():
        for w in root.winfo_children():
            if isinstance(w, tk.Toplevel):
                w.destroy()
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(root, text="Wybierz województwo:", font=("Arial", 12)).pack(pady=5)
    woj_select = tk.StringVar()
    menu = tk.OptionMenu(root, woj_select, *sorted(WOJEWODZTWA.keys()))
    menu.config(width=30, font=("Arial", 10))
    menu.pack(pady=5)

    tk.Label(root, text="Wybierz gminę (opcjonalnie):", font=("Arial", 12)).pack(pady=5)
    gmina_select = tk.StringVar()
    gmina_select_menu = tk.OptionMenu(root, gmina_select, "")
    gmina_select_menu.config(width=30, font=("Arial", 10))
    gmina_select_menu.pack(pady=5)

    woj_select.trace("w", lambda *args: update_gminy(woj_select, gmina_select, gmina_select_menu))

    tk.Button(root, text="Pokaż pogodę", font=("Arial", 12), bg="#baffc4",
              command=lambda: pobierz(woj_select, gmina_select)).pack(pady=10)

    root.mainloop()

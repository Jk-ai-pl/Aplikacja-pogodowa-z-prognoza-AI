import asyncio
import httpx
import tkinter as tk
from tkinter import Toplevel, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
from data_gminy import WOJEWODZTWA, GMNY
from ai_forecast import predict

# ======================================================
# Pobieranie pogody z Open-Meteo
# ======================================================
async def get_weather(lat, lon):
    from datetime import date, timedelta
    today = date.today()
    end_date = today + timedelta(days=6)
    start_str = today.isoformat()
    end_str = end_date.isoformat()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "start_date": start_str,
        "end_date": end_str
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        return r.json()

# ======================================================
# Pobierz pogodę po wybraniu województwa/gminy
# ======================================================
def pobierz(woj_select, gmina_select):
    woj = woj_select.get()
    gmina = gmina_select.get() if gmina_select.get() != "" else None

    if woj == "":
        messagebox.showinfo("Info", "❗ wybierz województwo")
        return

    lat, lon = WOJEWODZTWA[woj]
    if gmina and woj in GMNY and gmina in GMNY[woj]:
        lat, lon = GMNY[woj][gmina]

    async def run_and_plot():
        data = await get_weather(lat, lon)
        daily = data.get("daily")
        times = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        prec = daily.get("precipitation_sum", [])

        srednia = [(a+b)/2 for a,b in zip(tmax,tmin)]

        typy_opadu = []
        kolory = []
        for i in range(len(times)):
            p = prec[i]
            if p > 0:
                if tmax[i] <= 0:
                    typy_opadu.append("Śnieg")
                    kolory.append("#80d4ff")
                elif tmin[i] < 0 < tmax[i]:
                    typy_opadu.append("Deszcz ze śniegiem")
                    kolory.append("#b97aff")
                else:
                    typy_opadu.append("Deszcz")
                    kolory.append("#4da6ff")
            else:
                typy_opadu.append("Brak opadów")
                kolory.append("#95a5a6")

        ai_times, ai_tmax, ai_tmin, ai_prec = predict(times, tmax, tmin, prec)
        srednia_ai = [(a+b)/2 for a,b in zip(ai_tmax, ai_tmin)]
        display_times = times + [d.split("T")[0] for d in ai_times]

        x_all = list(range(len(srednia) + len(ai_times)))

        win = Toplevel()
        win.title(f"Pogoda — {gmina if gmina else woj}")
        win.geometry("900x600")
        tk.Label(win, text=f"Prognoza dla: {gmina if gmina else woj}", font=("Arial",14,"bold")).pack(pady=8)

        fig, ax = plt.subplots(figsize=(9,4.5))

        ax.plot(x_all, srednia + srednia_ai, linestyle='-', linewidth=1.5, color='#1a1a1a', zorder=1)

        line_real = ax.plot(range(len(srednia)), srednia,
                            marker='o', color='#4da6ff', linestyle='None', label='Rzeczywiste', zorder=2)[0]
        line_ai = ax.plot(range(len(srednia), len(srednia)+len(ai_times)),
                          srednia_ai, marker='o', color='#ff7f0e', linestyle='None', label='AI prognoza', zorder=2)[0]

        ax.set_ylabel("Średnia temperatura (°C)")
        ax.set_xticks(x_all)
        ax.set_xticklabels(display_times, rotation=45, ha="right")
        ax.set_ylim(-30, 40)

        for i in range(len(x_all)):
            ax.axvline(i, color="#DDDDDD", linestyle="--", linewidth=1, alpha=0.55)

        ax2 = ax.twinx()
        ax2.bar(range(len(srednia)), prec, color=kolory, alpha=0.6, width=0.6)
        ax2.bar(range(len(srednia), len(srednia)+len(ai_times)), ai_prec,
                color=["#ffbb78"]*len(ai_times), alpha=0.6, width=0.6)
        ax2.set_ylabel("Opady (mm)")
        ax2.set_ylim(0,10)

        legend_typy = ["Deszcz", "Deszcz ze śniegiem", "Śnieg"]
        legend_kolory = {"Deszcz":"#4da6ff","Deszcz ze śniegiem":"#b97aff","Śnieg":"#80d4ff"}
        handles = [plt.Rectangle((0,0),1,1,color=legend_kolory[t]) for t in legend_typy]
        ax2.legend(handles, legend_typy, loc="upper left", bbox_to_anchor=(0.01,0.98))
        ax.legend(loc="upper right")

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        cursor = mplcursors.cursor([line_real, line_ai], hover=True)
        @cursor.connect("add")
        def on_add(sel):
            line = sel.artist
            idx = int(sel.index)
            if line.get_label() == "Rzeczywiste":
                sel.annotation.set(text=(
                    f"{times[idx]}\n"
                    f"Min: {tmin[idx]:.1f}°C\n"
                    f"Max: {tmax[idx]:.1f}°C\n"
                    f"Średnia: {srednia[idx]:.1f}°C\n"
                    f"Opady: {prec[idx]:.1f} mm"
                ))
            else:
                ai_idx = idx - len(srednia)
                sel.annotation.set(text=(
                    f"{ai_times[ai_idx].split('T')[0]}\n"
                    f"Min: {ai_tmin[ai_idx]:.1f}°C\n"
                    f"Max: {ai_tmax[ai_idx]:.1f}°C\n"
                    f"Średnia: {srednia_ai[ai_idx]:.1f}°C\n"
                    f"Opady: {ai_prec[ai_idx]:.1f} mm"
                ))

        canvas.draw()

    asyncio.run(run_and_plot())

import json

# ======================================================
# Wczytaj województwa i gminy z plików JSON
# ======================================================
with open("wojewodztwa.json", encoding="utf-8") as f:
    WOJEWODZTWA = json.load(f)

GMNY = {}

# ======================================================
# Aktualizacja listy gmin po wyborze województwa
# ======================================================
def update_gminy(woj_select, gmina_select, gmina_select_menu):
    woj = woj_select.get()
    menu = gmina_select_menu["menu"]
    menu.delete(0, "end")
    gmina_select.set("")  # reset

    if woj:
        fname = f"gminy_{woj.replace(' ', '_')}.json"
        try:
            with open(fname, encoding="utf-8") as f:
                gminy_data = json.load(f)
        except FileNotFoundError:
            gminy_data = []

        GMNY[woj] = {item["name"]: (item["lat"], item["lng"]) for item in gminy_data}

        menu.add_command(label="brak", command=lambda: gmina_select.set(""))

        for g in sorted(GMNY[woj].keys()):
            menu.add_command(label=g, command=lambda value=g: gmina_select.set(value))

import tkinter as tk

def show_search(parent, app):
    t = app.theme
    tk.Label(parent, text="Search Parked Vehicle", font=("Segoe UI", 18, "bold"), bg=t["bg"], fg=t["text"]).pack(pady=10)
    box = tk.Frame(parent, bg=t["card"], bd=1, relief="solid", padx=20, pady=10); box.pack(pady=5)
    tk.Label(box, text="Enter Vehicle Number:", font=("Segoe UI", 10), bg=t["card"], fg=t["text"]).pack(anchor="w", pady=(0,3))
    v = tk.StringVar()
    e = tk.Entry(box, textvariable=v, font=("Segoe UI", 11), width=25); e.pack(pady=4); e.focus()
    res_lbl = tk.Label(parent, text="", font=("Segoe UI", 11, "bold"), bg=t["bg"], fg=t["text"]); res_lbl.pack(pady=5)
    fl_lbl = tk.Label(parent, text="Showing: Ground", font=("Segoe UI", 10, "italic"), bg=t["bg"], fg=t["subtext"]); fl_lbl.pack()
    gf = tk.Frame(parent, bg=t["bg"]); gf.pack(pady=5)

    def render(fp="G", found=None):
        for w in gf.winfo_children(): w.destroy()
        fl_lbl.config(text=f"Showing: {next(f for f,p in app.FLOORS if p==fp)}")
        for i in range(1,9):
            s = f"{fp}-{i}"; info = app.slots[s]
            c = app.green_color if info is None else app.red_color
            vt = f" [{info.get('type','Car')[0]}]" if info else ""
            txt = f"{s}\nAvailable" if info is None else f"{s}{vt}\n{info['vehicle']}"
            if found == s: c, txt = app.yellow_color, f"{s}\nFOUND HERE!"
            tk.Label(gf, text=txt, font=("Segoe UI", 9, "bold"), bg=c,
                     fg="#FFFFFF" if c!=app.yellow_color else "#000000",
                     width=13, height=3, bd=1, relief="solid").grid(row=(i-1)//4, column=(i-1)%4, padx=5, pady=5)

    def search():
        num = v.get().strip().upper()
        if not num: res_lbl.config(text="Please enter a vehicle number!", fg=app.red_color); render(); return
        fs = next((s for s,i in app.slots.items() if i and i["vehicle"]==num), None)
        if fs:
            res_lbl.config(text=f"FOUND! {app.slots[fs].get('type','Car')} {num} is in Slot {fs} (Entry: {app.slots[fs]['entry_time']}).", fg=app.green_color)
            render(fs.split("-")[0], fs)
        else: res_lbl.config(text=f"NOT FOUND! Vehicle {num} is not currently parked.", fg=app.red_color); render()

    tk.Button(box, text="Search Vehicle", font=("Segoe UI", 10, "bold"), bg=t["btn"], fg=t["btn_text"], bd=0, padx=15, pady=4, command=search).pack(pady=8)
    render()

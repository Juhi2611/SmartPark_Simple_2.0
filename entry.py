import re, tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

def show_entry(parent, app):
    t = app.theme
    tk.Label(parent, text="Vehicle Entry", font=("Segoe UI", 18, "bold"), bg=t["bg"], fg=t["text"]).pack(pady=10)
    box = tk.Frame(parent, bg=t["card"], bd=1, relief="solid", padx=20, pady=15)
    box.pack(pady=5)
    tk.Label(box, text="Registration Number (e.g. GJ01AB1234):", font=("Segoe UI", 10), bg=t["card"], fg=t["text"]).pack(anchor="w", pady=(0,3))
    v = tk.StringVar()
    e = tk.Entry(box, textvariable=v, font=("Segoe UI", 11), width=25); e.pack(pady=4); e.focus()
    tk.Label(box, text="Vehicle Type:", font=("Segoe UI", 10), bg=t["card"], fg=t["text"]).pack(anchor="w", pady=(10,3))
    cb = ttk.Combobox(box, values=["Car","Bike"], state="readonly", font=("Segoe UI", 10), width=23); cb.set("Car"); cb.pack(pady=4)
    tk.Label(box, text="Rates: Car = Rs 30/hr (+20) | Bike = Rs 15/hr (+10)", font=("Segoe UI", 8), bg=t["card"], fg=t["subtext"]).pack(pady=5)

    def park():
        num, typ = v.get().strip().upper(), cb.get()
        if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$", num):
            return messagebox.showwarning("Invalid Plate", "Invalid Vehicle Number!\nMust follow Indian format (e.g., GJ01AB1234).")
        if any(i and i["vehicle"]==num for i in app.slots.values()):
            return messagebox.showerror("Error", f"Vehicle {num} is already parked!")
        slot, free = None, []
        if num in app.reservations:
            slot = app.reservations[num]["slot"]
        else:
            fi = {p:i for i,(_,p) in enumerate(app.FLOORS)}
            for k, info in app.slots.items():
                p, n = k.split("-")
                if int(n)>2 and info is None and all(r["slot"]!=k for r in app.reservations.values()):
                    free.append((fi[p], int(n), k))
            if free: slot = min(free)[2]
            else: return messagebox.showwarning("Full", "Parking is full. Please try later.")
        app.slots[slot] = {"vehicle":num, "type":typ, "entry_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        app.save_data()
        if num not in app.reservations:
            pf = next((f for f,p in app.FLOORS if slot.startswith(p)), "Ground")
            if free and min(free)[0]>0 and not any(s[0]==0 for s in free):
                messagebox.showinfo("Floor Full", f"Ground floor is full. Assigned to {pf}, Slot {slot}.")
            else: messagebox.showinfo("Success", f"{typ} {num} parked in Slot {slot}!")
        else: messagebox.showinfo("Success", f"Reserved vehicle {num} parked in Slot {slot}!")
        app.show_page("dashboard")

    tk.Button(box, text="Park Vehicle", font=("Segoe UI", 11, "bold"), bg=t["btn"], fg=t["btn_text"], bd=0, padx=15, pady=5, command=park).pack(pady=10)

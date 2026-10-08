import os, tkinter as tk
from tkinter import messagebox
from datetime import datetime

def show_exit(parent, app):
    t = app.theme
    tk.Label(parent, text="Vehicle Exit & Billing", font=("Segoe UI", 18, "bold"), bg=t["bg"], fg=t["text"]).pack(pady=10)
    box = tk.Frame(parent, bg=t["card"], bd=1, relief="solid", padx=20, pady=15); box.pack(pady=5)
    tk.Label(box, text="Enter Vehicle Number to Exit:", font=("Segoe UI", 10), bg=t["card"], fg=t["text"]).pack(anchor="w", pady=(0,5))
    v = tk.StringVar()
    e = tk.Entry(box, textvariable=v, font=("Segoe UI", 11), width=25); e.pack(pady=4); e.focus()

    def do_exit():
        num = v.get().strip().upper()
        if not num: return messagebox.showwarning("Warning", "Please enter a vehicle number!")
        slot = next((s for s,i in app.slots.items() if i and i["vehicle"]==num), None)
        if not slot: return messagebox.showerror("Not Found", f"Vehicle {num} is not currently parked!")
        d = app.slots[slot]; typ = d.get("type","Car"); entry_t = d["entry_time"]
        exit_t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hours, fee = app.calculate_fee(entry_t, exit_t, typ)
        is_res = num in app.reservations; adj = ""
        if is_res:
            fee = max(0, fee - app.reservations[num]["fee_paid"])
            adj = f"Booking fee adjusted: Rs {app.reservations[num]['fee_paid']}\n"
            del app.reservations[num]
        app.slots[slot] = None
        rec = {"vehicle":num,"type":typ,"slot":slot,"floor":next(f for f,p in app.FLOORS if p==slot.split("-")[0]),
               "entry_time":entry_t,"exit_time":exit_t,"duration":f"{hours} hr","fee":fee,
               "status":"Completed","reserved":"Yes" if is_res else "No"}
        app.history.append(rec); app.save_data()
        txt = (f"=== SMARTPARK PARKING RECEIPT ===\nVehicle No:   {num}\nVehicle Type: {typ}\n"
               f"Floor:        {rec['floor']}\nSlot Number:  {slot}\nReserved:     {rec['reserved']}\n"
               f"Entry Time:   {entry_t}\nExit Time:    {exit_t}\nDuration:     {hours} hour(s)\n"
               f"{adj}Total Fee:    Rs {fee}\n=================================\n")
        messagebox.showinfo("Receipt", txt)
        if messagebox.askyesno("Save Receipt", "Would you like to save this receipt as a text file?"):
            os.makedirs("receipts", exist_ok=True)
            fn = f"receipts/{num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            open(fn,"w",encoding="utf-8").write(txt)
            messagebox.showinfo("Saved", f"Receipt saved to {fn}!")
        app.show_page("dashboard")

    tk.Button(box, text="Process Exit", font=("Segoe UI", 11, "bold"), bg=app.red_color, fg="#FFFFFF", bd=0, padx=15, pady=5, command=do_exit).pack(pady=10)

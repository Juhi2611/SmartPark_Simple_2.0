import csv, tkinter as tk
from tkinter import messagebox, ttk

def show_history(parent, app):
    t = app.theme
    tk.Label(parent, text="Parking History", font=("Segoe UI", 18, "bold"), bg=t["bg"], fg=t["text"]).pack(pady=5)
    bar = tk.Frame(parent, bg=t["bg"]); bar.pack(fill="x", padx=20, pady=5)
    tk.Label(bar, text="Filter Vehicle:", font=("Segoe UI", 10), bg=t["bg"], fg=t["text"]).pack(side="left")
    fv = tk.StringVar()
    tk.Entry(bar, textvariable=fv, font=("Segoe UI", 10), width=18).pack(side="left", padx=5)
    tf = tk.Frame(parent, bg=t["bg"]); tf.pack(fill="both", expand=True, padx=20, pady=5)
    cols = ("Vehicle","Type","Floor","Slot","Reserved","Status","Fee (Rs)","Entry Time","Exit Time")
    tree = ttk.Treeview(tf, columns=cols, show="headings", height=9)
    for c, w in zip(cols, [90,60,80,60,70,130,60,140,140]):
        tree.heading(c, text=c); tree.column(c, anchor="center", width=w)
    sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
    sl = tk.Label(parent, text="", font=("Segoe UI", 11, "bold"), bg=t["bg"], fg=t["text"]); sl.pack(pady=5)

    def refresh(*_):
        for i in tree.get_children(): tree.delete(i)
        q = fv.get().strip().upper(); cnt = rev = 0
        for r in app.history:
            if q=="" or q in r["vehicle"]:
                if r.get("status","")!="Cancelled (refunded)": rev += r["fee"]
                tree.insert("","end",values=(r["vehicle"],r.get("type","Car"),r.get("floor","-"),r.get("slot","-"),
                    r.get("reserved","No"),r.get("status","Completed"),r["fee"],r["entry_time"],r["exit_time"])); cnt+=1
        sl.config(text=f"Showing: {cnt} vehicles   |   Total Revenue: Rs {rev}")

    fv.trace_add("write", refresh)

    def export():
        if not app.history: return messagebox.showwarning("Empty","No history data to export!")
        with open("parking_history.csv","w",newline="",encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(cols)
            for r in app.history: w.writerow([r["vehicle"],r.get("type","Car"),r.get("floor","-"),r.get("slot","-"),
                r.get("reserved","No"),r.get("status","Completed"),r["fee"],r["entry_time"],r["exit_time"]])
        messagebox.showinfo("Export Success","Successfully exported history to 'parking_history.csv'!")

    tk.Button(bar, text="Export to CSV", font=("Segoe UI", 9, "bold"), bg=t["btn"], fg=t["btn_text"], bd=0, padx=10, pady=3, command=export).pack(side="right")
    refresh()

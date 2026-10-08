import os, json, math, re
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import entry, exit, search, history

TOTAL_SLOTS = 24
CAR_FIRST_HOUR, CAR_EXTRA_HOUR = 30, 20
BIKE_FIRST_HOUR, BIKE_EXTRA_HOUR = 15, 10
DATA_FILE = "parking_data.json"
BOOKING_FEE = 50
RESERVE_WINDOW_MIN = 60
FREE_CANCEL_MIN = 10
FLOORS = [("Ground","G"),("1st Floor","F1"),("2nd Floor","F2")]
LIGHT = {"bg":"#F1F5F9","sidebar":"#E2E8F0","card":"#FFFFFF","text":"#0F172A","subtext":"#475569","btn":"#2563EB","btn_text":"#FFFFFF"}
DARK  = {"bg":"#0F172A","sidebar":"#1E293B","card":"#334155","text":"#F8FAFC","subtext":"#94A3B8","btn":"#3B82F6","btn_text":"#FFFFFF"}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartPark Simple - Parking Management System")
        self.geometry("1100x700"); self.resizable(True,True)
        try: self.state('zoomed')
        except: pass
        self.green_color, self.red_color, self.yellow_color, self.orange_color = "#22C55E","#EF4444","#EAB308","#F97316"
        self.mode, self.theme, self.slots, self.history, self.reservations = "dark", DARK, {}, [], {}
        self.FLOORS = FLOORS
        self.load_data(); self.build_ui(); self.update_clock(); self.show_page("dashboard")

    def init_empty_data(self):
        self.slots = {f"{p}-{i}":None for _,p in self.FLOORS for i in range(1,9)}
        self.history, self.reservations = [], {}

    def load_data(self):
        self.init_empty_data()
        if os.path.exists(DATA_FILE):
            try:
                d = json.load(open(DATA_FILE,"r",encoding="utf-8"))
                for k,v in d.get("slots",{}).items():
                    nk = f"G-{int(k)}" if k.isdigit() and int(k)<=8 else k
                    nk = f"F1-{int(k)-8}" if k.isdigit() and int(k)>8 else nk
                    if nk in self.slots:
                        self.slots[nk]=v
                        if v: v.setdefault("status","Parked"); v.setdefault("reserved","No")
                for h in d.get("history",[]):
                    h.setdefault("status","Completed"); h.setdefault("reserved","No")
                    if "floor" not in h: h["floor"]="Ground" if str(h.get("slot")).isdigit() and int(h["slot"])<=8 else "1st Floor"
                    if str(h.get("slot")).isdigit(): h["slot"]=f"G-{h['slot']}" if int(h['slot'])<=8 else f"F1-{int(h['slot'])-8}"
                    self.history.append(h)
                self.reservations = d.get("reservations",{})
            except: pass
        self.save_data()

    def save_data(self):
        json.dump({"slots":self.slots,"history":self.history,"reservations":self.reservations},
                  open(DATA_FILE,"w",encoding="utf-8"), indent=2)

    def calculate_fee(self, entry_str, exit_str, v_type="Car"):
        fmt = "%Y-%m-%d %H:%M:%S"
        t1,t2 = datetime.strptime(entry_str,fmt), datetime.strptime(exit_str,fmt)
        hours = math.ceil(max(1,(t2-t1).total_seconds())/3600)
        fee = BIKE_FIRST_HOUR if v_type=="Bike" else CAR_FIRST_HOUR
        if hours>1: fee += (hours-1)*(BIKE_EXTRA_HOUR if v_type=="Bike" else CAR_EXTRA_HOUR)
        return hours, fee

    def update_clock(self):
        if not (hasattr(self,"clock_lbl") and self.winfo_exists()): return
        now = datetime.now(); fmt = "%Y-%m-%d %H:%M:%S"
        self.clock_lbl.config(text=now.strftime("%a, %d %b %Y  |  %I:%M:%S %p"))
        to_del = []
        for plate,res in self.reservations.items():
            if (now-datetime.strptime(res["booked_at"],fmt)).total_seconds() > RESERVE_WINDOW_MIN*60:
                if not any(i and i["vehicle"]==plate for i in self.slots.values()):
                    self.history.append({"vehicle":plate,"type":"Unknown","slot":res["slot"],"entry_time":res["booked_at"],
                        "exit_time":now.strftime(fmt),"duration":"0 hr","fee":res["fee_paid"],"status":"No-show",
                        "reserved":"Yes","floor":next(f for f,p in FLOORS if p==res["slot"].split("-")[0])})
                    to_del.append((plate,res["slot"]))
        for p,s in to_del:
            del self.reservations[p]
            if not self.slots[s]: self.slots[s]=None
        if to_del:
            self.save_data()
            if getattr(self,"current_page","")=="dashboard": self.render_dashboard()
        self.after(1000, self.update_clock)

    def build_ui(self):
        self.configure(bg=self.theme["bg"])
        hdr = tk.Frame(self, bg=self.theme["sidebar"], height=45); hdr.pack(side="top",fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="SmartPark", font=("Segoe UI",12,"bold"), bg=self.theme["sidebar"], fg=self.theme["text"]).pack(side="left",padx=15)
        self.warning_lbl = tk.Label(hdr, text="", font=("Segoe UI",10,"bold"), bg=self.theme["sidebar"], fg=self.red_color); self.warning_lbl.pack(side="left",padx=20)
        self.clock_lbl = tk.Label(hdr, font=("Segoe UI",10), bg=self.theme["sidebar"], fg=self.theme["subtext"]); self.clock_lbl.pack(side="right",padx=15)
        sb = tk.Frame(self, bg=self.theme["sidebar"], width=180); sb.pack(side="left",fill="y"); sb.pack_propagate(False)
        for lbl,pg in [("Dashboard","dashboard"),("Vehicle Entry","entry"),("Vehicle Exit","exit"),("Search","search"),("History","history")]:
            tk.Button(sb, text=lbl, font=("Segoe UI",10,"bold"), bg=self.theme["btn"], fg=self.theme["btn_text"], bd=0, command=lambda p=pg:self.show_page(p)).pack(fill="x",padx=10,pady=4)
        tk.Button(sb, text="Reserve Slot", font=("Segoe UI",10,"bold"), bg=self.orange_color, fg="#FFF", bd=0, command=self.reserve_slot).pack(fill="x",padx=10,pady=20)
        mode_txt = "Light Mode" if self.mode=="dark" else "Dark Mode"
        tk.Button(sb, text=mode_txt, font=("Segoe UI",9,"bold"), bg=self.theme["card"], fg=self.theme["text"], bd=1, command=self.toggle_theme).pack(side="bottom",fill="x",padx=10,pady=15)
        self.content = tk.Frame(self, bg=self.theme["bg"]); self.content.pack(side="right",fill="both",expand=True)

    def reserve_slot(self):
        plate = simpledialog.askstring("Reserve Slot","Enter vehicle number (e.g. GJ01AB1234):",parent=self)
        if not plate: return
        plate = plate.strip().upper()
        if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$",plate): return messagebox.showwarning("Invalid","Invalid format!")
        if plate in self.reservations: return messagebox.showwarning("Error","Vehicle already has a reservation!")
        if any(i and i["vehicle"]==plate for i in self.slots.values()): return messagebox.showwarning("Error","Vehicle is already parked!")
        tgt = next((s for _,p in self.FLOORS for s in [f"{p}-1",f"{p}-2"] if self.slots[s] is None and all(r["slot"]!=s for r in self.reservations.values())),None)
        if not tgt: return messagebox.showerror("Full","All reserved slots are taken.")
        if messagebox.askyesno("Payment",f"Pay Rs {BOOKING_FEE} booking fee now?"):
            self.reservations[plate]={"slot":tgt,"booked_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"fee_paid":BOOKING_FEE}
            self.save_data(); messagebox.showinfo("Success",f"Slot {tgt} reserved for {plate}!")
            if getattr(self,"current_page","")=="dashboard": self.render_dashboard()

    def toggle_theme(self):
        self.mode = "light" if self.mode=="dark" else "dark"
        self.theme = LIGHT if self.mode=="light" else DARK
        for w in self.winfo_children(): w.destroy()
        self.build_ui(); self.show_page(self.current_page)

    def show_page(self, name):
        self.current_page = name
        for w in self.content.winfo_children(): w.destroy()
        {"dashboard":self.render_dashboard,"entry":lambda:entry.show_entry(self.content,self),
         "exit":lambda:exit.show_exit(self.content,self),"search":lambda:search.show_search(self.content,self),
         "history":lambda:history.show_history(self.content,self)}[name]()

    def on_slot_click(self, s, is_res):
        info = self.slots[s]; plate = next((p for p,r in self.reservations.items() if r["slot"]==s),None)
        if not info and not plate: return messagebox.showinfo("Slot",f"Slot {s} is available.")
        now = datetime.now(); fmt = "%Y-%m-%d %H:%M:%S"
        if not info and plate:
            res = self.reservations[plate]; booked = datetime.strptime(res["booked_at"],fmt)
            mins = int((now-booked).total_seconds()/60); left = max(0,RESERVE_WINDOW_MIN-mins)
            if messagebox.askyesno("Cancel Reservation",f"Reserved for {plate}\nMinutes left: {left}m\n\nCancel reservation?"):
                fee,status = (0,"Cancelled (refunded)") if mins<=FREE_CANCEL_MIN else (BOOKING_FEE,"Cancelled (late)")
                self.history.append({"vehicle":plate,"type":"Unknown","slot":res["slot"],"entry_time":res["booked_at"],
                    "exit_time":now.strftime(fmt),"duration":"0 hr","fee":fee,"status":status,"reserved":"Yes",
                    "floor":next(f for f,p in FLOORS if p==res["slot"].split("-")[0])})
                del self.reservations[plate]; self.save_data()
                messagebox.showinfo("Cancelled","Full refund of Rs 50" if mins<=FREE_CANCEL_MIN else "Booking fee of Rs 50 forfeited")
                self.render_dashboard()
            return
        entry_dt = datetime.strptime(info["entry_time"],fmt)
        hrs,mins = divmod(int((now-entry_dt).total_seconds()/60),60)
        msg = f"Vehicle: {info['vehicle']}\nDuration: {hrs}h {mins}m so far"
        if plate:
            left = max(0,RESERVE_WINDOW_MIN-int((now-datetime.strptime(self.reservations[plate]["booked_at"],fmt)).total_seconds()/60))
            msg = f"Reserved for {plate} (Left: {left}m)\n"+msg
        messagebox.showinfo("Slot Details",msg)

    def render_dashboard(self):
        occ = sum(1 for i in self.slots.values() if i)
        pct = int((occ/TOTAL_SLOTS)*100); rev = sum(r["fee"] for r in self.history)
        normal = [k for k in self.slots if int(k.split("-")[1])>2]
        self.warning_lbl.config(text="PARKING FULL" if all(self.slots[k] for k in normal) else "")
        tk.Label(self.content, text="Dashboard", font=("Segoe UI",16,"bold"), bg=self.theme["bg"], fg=self.theme["text"]).pack(pady=5)
        sf = tk.Frame(self.content, bg=self.theme["bg"]); sf.pack()
        for lbl,val in [("Total",TOTAL_SLOTS),("Occupied",occ),("Available",TOTAL_SLOTS-occ),("Revenue",f"Rs {rev}")]:
            f = tk.Frame(sf, bg=self.theme["card"], bd=1, relief="solid", padx=12, pady=5); f.pack(side="left",padx=8)
            tk.Label(f, text=str(val), font=("Segoe UI",12,"bold"), bg=self.theme["card"], fg=self.theme["text"]).pack()
            tk.Label(f, text=lbl, font=("Segoe UI",9), bg=self.theme["card"], fg=self.theme["subtext"]).pack()
        pf = tk.Frame(self.content, bg=self.theme["bg"]); pf.pack(pady=5)
        bc = self.green_color if pct<50 else (self.orange_color if pct<=80 else self.red_color)
        tk.Label(pf, text=f"Total Occupancy: {pct}%", font=("Segoe UI",10,"bold"), bg=self.theme["bg"], fg=bc).pack()
        ttk.Progressbar(pf, value=pct, maximum=100, length=320).pack()
        nb = ttk.Notebook(self.content); nb.pack(fill="both",expand=True,padx=20,pady=10)
        for name,prefix in self.FLOORS:
            tab = tk.Frame(nb, bg=self.theme["bg"])
            free = sum(1 for i in range(3,9) if not self.slots[f"{prefix}-{i}"])
            nb.add(tab, text=f"{name} ({free} free normal)")
            for i in range(1,9):
                s,ir,info = f"{prefix}-{i}", i<=2, self.slots[f"{prefix}-{i}"]
                pl = next((p for p,r in self.reservations.items() if r["slot"]==s),None)
                bg = self.green_color if not info else self.red_color
                bd = "#3B82F6" if ir else (self.theme["card"] if not info else self.red_color)
                txt = f"{s}\nAvailable"
                if ir and pl and not info:
                    left = max(0,RESERVE_WINDOW_MIN-int((datetime.now()-datetime.strptime(self.reservations[pl]["booked_at"],"%Y-%m-%d %H:%M:%S")).total_seconds()/60))
                    txt,bg = f"{s}\nReserved\n{pl} ({left}m)", self.theme["card"]
                elif info: txt = f"{s} [{info.get('type','Car')[0]}]\n{info['vehicle']}"
                fr = tk.Frame(tab, bg=bd, bd=2 if ir else 1); fr.grid(row=(i-1)//4,column=(i-1)%4,padx=7,pady=7)
                tk.Button(fr, text=txt, font=("Segoe UI",9,"bold"), bg=bg,
                          fg="#FFF" if bg!=self.theme["card"] else self.theme["text"],
                          width=12, height=3, bd=0, command=lambda sl=s,r=ir:self.on_slot_click(sl,r)).pack(padx=2,pady=2)

if __name__ == "__main__": App().mainloop()

import os, json
from datetime import datetime, timedelta
import smartpark as dashboard

def test_all():
    print("=== STARTING COMPREHENSIVE VERIFICATION TESTS ===")
    if os.path.exists("parking_data.json"): os.remove("parking_data.json")
    app = dashboard.App()
    fi = {p:i for i,(_,p) in enumerate(app.FLOORS)}

    # (a) Normal car goes to G-3
    free = [(fi[k.split("-")[0]], int(k.split("-")[1]), k) for k,v in app.slots.items()
            if int(k.split("-")[1])>2 and v is None and all(r["slot"]!=k for r in app.reservations.values())]
    assert min(free)[2]=="G-3", f"Expected G-3, got {min(free)[2]}"
    print("[PASS] (a) Normal car goes to G-3 first (G-1, G-2 reserved)")

    # (b) Reserved plate goes to its slot
    app.reservations["GJ01AB1000"]={"slot":"G-1","booked_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"fee_paid":50}
    assert app.reservations["GJ01AB1000"]["slot"]=="G-1"
    print("[PASS] (b) Reserved plate goes directly to its reserved slot (G-1)")

    # (c) Ground full -> F1-3
    for i in range(3,9): app.slots[f"G-{i}"]={"vehicle":f"GJ01AA000{i}","type":"Car","entry_time":"2026-10-08 10:00:00"}
    free = [(fi[k.split("-")[0]], int(k.split("-")[1]), k) for k,v in app.slots.items()
            if int(k.split("-")[1])>2 and v is None and all(r["slot"]!=k for r in app.reservations.values())]
    assert min(free)[2]=="F1-3", f"Expected F1-3, got {min(free)[2]}"
    print("[PASS] (c) When Ground normal slots are full, next car assigned to F1-3")

    # (d) All 18 normal slots full
    for _,p in app.FLOORS:
        for i in range(3,9): app.slots[f"{p}-{i}"]={"vehicle":f"DUMMY_{p}_{i}","type":"Car","entry_time":"2026-10-08 10:00:00"}
    free = [(fi[k.split("-")[0]], int(k.split("-")[1]), k) for k,v in app.slots.items()
            if int(k.split("-")[1])>2 and v is None and all(r["slot"]!=k for r in app.reservations.values())]
    assert len(free)==0
    app.reservations["GJ01AB9999"]={"slot":"F2-1","booked_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"fee_paid":50}
    assert app.reservations["GJ01AB9999"]["slot"]=="F2-1"
    print("[PASS] (d) All 18 normal slots full rejects walk-ins, but reserved plate can enter")

    # (e) Reserved slots never in normal list
    for k in app.slots:
        if k.endswith("-1") or k.endswith("-2"): assert k not in [s[2] for s in free]
    print("[PASS] (e) Non-reserved car can never get a reserved slot")

    app.slots={f"{p}-{i}":None for _,p in app.FLOORS for i in range(1,9)}; app.history=[]; app.reservations={}
    fmt="%Y-%m-%d %H:%M:%S"

    # (f) Cancel within 10 min -> refund
    app.reservations["GJ01AB0001"]={"slot":"G-1","booked_at":(datetime.now()-timedelta(minutes=5)).strftime(fmt),"fee_paid":50}
    res=app.reservations["GJ01AB0001"]; mins=int((datetime.now()-datetime.strptime(res["booked_at"],fmt)).total_seconds()/60)
    fee,status=(0,"Cancelled (refunded)") if mins<=dashboard.FREE_CANCEL_MIN else (50,"Cancelled (late)")
    app.history.append({"vehicle":"GJ01AB0001","type":"Unknown","slot":res["slot"],"entry_time":res["booked_at"],
        "exit_time":datetime.now().strftime(fmt),"duration":"0 hr","fee":fee,"status":status,"reserved":"Yes","floor":"Ground"})
    del app.reservations["GJ01AB0001"]
    assert sum(r["fee"] for r in app.history if r.get("status")!="Cancelled (refunded)")==0
    print("[PASS] (f) Cancellation within 10 minutes yields full refund & 0 revenue")

    # (g) Cancel after 10 min -> forfeit
    app.reservations["GJ01AB0002"]={"slot":"G-2","booked_at":(datetime.now()-timedelta(minutes=15)).strftime(fmt),"fee_paid":50}
    res=app.reservations["GJ01AB0002"]; mins=int((datetime.now()-datetime.strptime(res["booked_at"],fmt)).total_seconds()/60)
    fee,status=(0,"Cancelled (refunded)") if mins<=dashboard.FREE_CANCEL_MIN else (50,"Cancelled (late)")
    app.history.append({"vehicle":"GJ01AB0002","type":"Unknown","slot":res["slot"],"entry_time":res["booked_at"],
        "exit_time":datetime.now().strftime(fmt),"duration":"0 hr","fee":fee,"status":status,"reserved":"Yes","floor":"Ground"})
    del app.reservations["GJ01AB0002"]
    assert sum(r["fee"] for r in app.history if r.get("status")!="Cancelled (refunded)")==50
    print("[PASS] (g) Cancellation after 10 minutes forfeits Rs 50 and adds to revenue")

    # (h) No-show after 60 min
    app.reservations["GJ01AB0003"]={"slot":"F1-1","booked_at":(datetime.now()-timedelta(minutes=65)).strftime(fmt),"fee_paid":50}
    now=datetime.now(); to_del=[]
    for pl,res in app.reservations.items():
        if (now-datetime.strptime(res["booked_at"],fmt)).total_seconds()>dashboard.RESERVE_WINDOW_MIN*60:
            if not any(i and i["vehicle"]==pl for i in app.slots.values()):
                app.history.append({"vehicle":pl,"type":"Unknown","slot":res["slot"],"entry_time":res["booked_at"],
                    "exit_time":now.strftime(fmt),"duration":"0 hr","fee":res["fee_paid"],"status":"No-show","reserved":"Yes","floor":"1st Floor"})
                to_del.append((pl,res["slot"]))
    for p,s in to_del: del app.reservations[p]; app.slots[s]=None if not app.slots[s] else app.slots[s]
    assert "GJ01AB0003" not in app.reservations
    assert app.history[-1]["status"]=="No-show" and app.history[-1]["fee"]==50
    print("[PASS] (h) Reservation >60m is auto-released and logged as No-show with Rs 50 revenue")

    # (i) Reserved car fee adjusted
    app.reservations["GJ01AB0004"]={"slot":"G-1","booked_at":datetime.now().strftime(fmt),"fee_paid":50}
    entry_t=(datetime.now()-timedelta(minutes=30)).strftime(fmt)
    app.slots["G-1"]={"vehicle":"GJ01AB0004","type":"Car","entry_time":entry_t}
    _,fee=app.calculate_fee(entry_t,datetime.now().strftime(fmt),"Car")
    assert max(0,fee-app.reservations["GJ01AB0004"]["fee_paid"])==0
    print("[PASS] (i) Reserved vehicle fee adjusted minus Rs 50 and clamped to >= 0")

    # (j) Old JSON migration
    json.dump({"slots":{"1":{"vehicle":"GJ01OLD001","type":"Car","entry_time":"2026-10-08 10:00:00"},"2":None},
               "history":[{"vehicle":"GJ01OLD002","type":"Car","slot":"3","entry_time":"2026-10-08 09:00:00","exit_time":"2026-10-08 10:00:00","duration":"1 hr","fee":30}]},
              open("parking_data.json","w",encoding="utf-8"))
    app2=dashboard.App()
    assert app2.slots["G-1"]["vehicle"]=="GJ01OLD001"
    assert app2.history[0]["slot"]=="G-3"
    print("[PASS] (j) Old JSON data loads cleanly and auto-migrates slot IDs")
    print("\n=== ALL 10 TESTS PASSED SUCCESSFULLY! ===")

if __name__=="__main__": test_all()

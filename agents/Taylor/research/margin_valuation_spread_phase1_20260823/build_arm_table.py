"""Bang dieu kien ARM tai 15 su kien CAPIT cua engine (do phan giai NGAY — sua loi Phase 0 do theo THANG).
INPUT-ONLY: khong dung bat ky cot forward/outcome nao. Chay TRUOC prereg."""
import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"
P="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_20260823"
H="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_phase1_20260823"

EV = [(0,"2014-05-08"),(2,"2015-08-24"),(3,"2016-01-18"),(4,"2018-05-28"),(5,"2018-07-05"),
      (6,"2020-02-03"),(7,"2020-03-11"),(8,"2020-07-27"),(10,"2022-06-15"),(12,"2023-10-30"),
      (13,"2024-04-17"),(14,"2024-08-05"),(15,"2025-04-03"),(16,"2025-10-20"),(17,"2026-03-09")]

d = pd.read_csv(f"{D}/daily_panel_spread.csv", parse_dates=["time"]).sort_values("time")
dy = pd.read_csv(f"{H}/_dy_daily.csv", parse_dates=["time"]).sort_values("time")
dy["dy_med_payers_pct"] = dy["dy_med_payers"]*100.0
d = pd.merge_asof(d, dy[["time","dy_med_payers_pct","n_payers","n_uni"]], on="time", direction="backward")
d["sp_dy_dep"] = d["dy_med_payers_pct"] - d["deposit_use"]

st = pd.read_csv(f"{P}/_dt5g_daily.csv", parse_dates=["time"]).sort_values("time")
scol = [c for c in st.columns if c.lower() in ("state","dt5g_state")][0]
d = pd.merge_asof(d, st[["time",scol]].rename(columns={scol:"dt5g"}), on="time", direction="backward")

rows=[]
for i,ds in EV:
    t=pd.Timestamp(ds)
    r=d[d["time"]<=t].iloc[-1]
    rows.append(dict(event=i, date=ds, panel_asof=str(r["time"].date()),
        dd52=round(float(r["dd52"]),2), ey_med=round(float(r["ey_med_pct"]),2),
        deposit=float(r["deposit_use"]), margin=float(r["margin_rate"]),
        sp_ey_mgn=round(float(r["sp_ey_mgn"]),2), sp_ey_dep=round(float(r["sp_ey_dep"]),2),
        dy_payer=round(float(r["dy_med_payers_pct"]),2), sp_dy_dep=round(float(r["sp_dy_dep"]),2),
        dt5g=int(r["dt5g"]) if pd.notna(r["dt5g"]) else -1))
t=pd.DataFrame(rows)
t.to_csv(f"{H}/arm_conditions_events.csv", index=False)
pd.set_option("display.width",250)
print(t.to_string(index=False))

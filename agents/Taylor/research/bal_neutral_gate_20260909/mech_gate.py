"""VONG 3 — co che: dot sut giam cua chan A den tu dau. Doc tu chinh file audit cua tung chan."""
import numpy as np
import pandas as pd

B = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
     "_etfliqcustompitg_wtnamecap_advprice_univpit_exp_balgate%s.csv")
LEGS = ["ctrl", "a1", "a2", "a3", "a4", "b1", "b2", "b3"]
out = []
for t in LEGS:
    d = pd.read_csv(B % t, low_memory=False)
    D = d[d.record_type == "DAILY"].copy()
    D["ymd"] = pd.to_datetime(D["ymd"])
    D = D.set_index("ymd").sort_index()
    nav = pd.to_numeric(D["combined_nav"])
    dd = nav / nav.cummax() - 1
    st = pd.to_numeric(D["state"], errors="coerce")
    tx = d[(d.record_type == "TX") & (d.book == "BAL") & (d.action == "buy")].copy()
    tx = tx[~tx.play_type.astype(str).str.startswith(("CAPIT", "ETF_PARK"))]
    tx["ymd"] = pd.to_datetime(tx["ymd"])
    ent = tx.groupby("holding_id").agg(d0=("ymd", "min"), pt=("play_type", "first"))
    ent["st"] = ent.d0.map(st.to_dict())
    out.append(dict(leg=t, n_entries=len(ent),
                    n_entry_state3=int((ent.st == 3).sum()),
                    n_entry_state45=int(ent.st.isin([4, 5]).sum()),
                    maxdd_pct=dd.min() * 100, maxdd_date=str(dd.idxmin().date()),
                    dd_trough_2020=str(dd["2020-01-01":"2020-12-31"].min() * 100)[:6],
                    dd_trough_2022=str(dd["2022-01-01":"2022-12-31"].min() * 100)[:6]))
M = pd.DataFrame(out).set_index("leg")
pd.set_option("display.width", 220)
print(M.to_string())
M.to_csv("mech_gate.csv")

# where does a1 lose vs ctrl, month by month (top 8 worst / best)
nc = pd.read_csv(B % "ctrl", low_memory=False)
nc = nc[nc.record_type == "DAILY"].assign(ymd=lambda x: pd.to_datetime(x.ymd)).set_index("ymd").sort_index()
rc = np.log(pd.to_numeric(nc.combined_nav)).diff()
for t in ["a1", "a4", "b1", "b2"]:
    na = pd.read_csv(B % t, low_memory=False)
    na = na[na.record_type == "DAILY"].assign(ymd=lambda x: pd.to_datetime(x.ymd)).set_index("ymd").sort_index()
    ra = np.log(pd.to_numeric(na.combined_nav)).diff()
    dm = (ra - rc).dropna().resample("ME").sum() * 100
    print(f"\n--- {t}: 5 thang te nhat / 5 thang tot nhat (delta log-ret, pp) ---")
    print("  worst:", {str(k.date())[:7]: round(v, 2) for k, v in dm.nsmallest(5).items()})
    print("  best :", {str(k.date())[:7]: round(v, 2) for k, v in dm.nlargest(5).items()})

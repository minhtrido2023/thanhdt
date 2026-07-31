"""Viec 4 — kich ban stress TONG HOP: washout SAU (khong co trong mau lich su).

Killer objection cua quant-skeptic: 15 su kien CAPIT that KHONG chua mot lan washout that bai
sau (lo te nhat quan sat duoc chi -4,7%). Ket luan "co so sizing gan nhu khong quan trong" vi vay
chi duoc kiem chung o duong di nhe-vua.

Cach lam (auditable, khong bia so):
  - %NAV TONG thuc su trien khai o MOI su kien va MOI cong thuc = doc TRUC TIEP tu audit CSV
    cua chinh leg do (sum ENTRY buy_amount cua arm CAPIT / combined_nav tai ngay fire).
    => phan "phoi nhiem" la DU LIEU THAT, khong gia dinh.
  - Chi phan "duong gia sau khi mua" moi la gia dinh (day chinh la thu con thieu trong mau).
  - Ap 4 kich ban shock len rieng arm CAPIT, giu moi thu khac nhu cu.
"""
import glob, re
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
LEGS = [("capsz_ctrl", "cash"), ("capsz_idle", "idle"), ("capsz_booknav", "booknav (LIVE)"),
        ("capsz_nav20", "nav:0.20"), ("capsz_navsize15", "navsize:0.15"),
        ("capsz_navsize25", "navsize:0.25"), ("capsz_navsize30", "navsize:0.30"),
        ("capsz_navsize35", "navsize:0.35"), ("capsz_navsize40", "navsize:0.40")]

# kich ban: (ten, sut them sau khi mua, phan hoi phuc lai duoc)
SCEN = [("S0 lich su (quan sat)",  None, None),
        ("S1 -20% roi hoi ve hoa", -0.20, 1.00),
        ("S2 -30% hoi nua duong",  -0.30, 0.50),
        ("S3 -30% cat lo tai day", -0.30, 0.00),
        ("S4 -45% hoi nua duong",  -0.45, 0.50)]


def leg_exposure(tag):
    f = glob.glob(f"{W}/data/v23_golive_audit_2014_now_*_exp_{tag}_univpit.csv")
    if not f:
        return None
    df = pd.read_csv(f[0], low_memory=False)
    # QUAN TRONG (META combination_note): TX ghi bang VND cua SO THAM CHIEU doc lap (25B/so),
    # con combined_nav = cap_bal+cap_lag la NAV danh muc that. Muon %NAV danh muc phai quy hai
    # buoc: w_book = buy_book / nav_book_ref, roi w_pf = SUM_book w_book * cap_book / combined_nav.
    cols = ["ymd", "combined_nav", "nav_bal_ref", "nav_lag_ref", "cap_bal", "cap_lag"]
    d = df[df.record_type == "DAILY"][cols].copy()
    d["ymd"] = pd.to_datetime(d.ymd)
    for c in cols[1:]:
        d[c] = pd.to_numeric(d[c])
    d = d.set_index("ymd").sort_index()
    tx = df[(df.record_type == "TX") & df.play_type.astype(str).str.startswith("CAPIT")].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd)
    tx["eid"] = tx.play_type.str.extract(r"_E(\d+)$")[0].astype(int)
    tx["buy_amount"] = pd.to_numeric(tx.buy_amount, errors="coerce").fillna(0.0)
    tx["sell_amount"] = pd.to_numeric(tx.sell_amount, errors="coerce").fillna(0.0)
    ent = tx[tx.reason.astype(str).str.startswith("ENTRY")]
    out = []
    for eid, g in ent.groupby("eid"):
        d0 = g.ymd.min()
        row = d.asof(d0)
        w_pf = 0.0
        for bk, navc, capc in (("BAL", "nav_bal_ref", "cap_bal"), ("LAG", "nav_lag_ref", "cap_lag")):
            amt = g[g.book == bk].buy_amount.sum()
            if amt > 0 and row[navc] > 0:
                w_pf += (amt / row[navc]) * (row[capc] / row["combined_nav"])
        arm = tx[tx.eid == eid]
        pnl = (arm.sell_amount.sum() - arm.buy_amount.sum()) / max(arm.buy_amount.sum(), 1.0)
        out.append(dict(E=eid, ngay=d0.date(), deployed=g.buy_amount.sum(),
                        nav=row["combined_nav"], w=w_pf, ret_obs=pnl))
    return pd.DataFrame(out)


rows = []
detail = {}
for tag, name in LEGS:
    X = leg_exposure(tag)
    if X is None:
        print(f"  (bo qua {name}: chua co CSV)"); continue
    detail[name] = X
    r = dict(cong_thuc=name, n_ev=len(X), w_med=X.w.median(), w_max=X.w.max(),
             w_min=X.w.min(), w_sum=X.w.sum())
    for sname, shock, rec in SCEN:
        if shock is None:
            # lo TE NHAT quan sat duoc, quy ve % NAV danh muc
            worst = (X.w * X.ret_obs.clip(upper=0)).min()
            r[sname] = worst
        else:
            # ton that vinh vien = shock * (1-rec); rut von tam thoi = shock (dinh drawdown)
            perm = shock * (1 - rec)
            r[sname] = (X.w * perm).min() if perm < 0 else 0.0
            r[sname + "|DD"] = (X.w * shock).min()
    rows.append(r)

R = pd.DataFrame(rows)
pd.set_option("display.width", 260, "display.max_columns", 60)
pct = lambda x: f"{100*x:+.2f}%"

print("A. PHOI NHIEM THAT (doc tu audit CSV, % NAV TONG danh muc tai ngay fire)")
print(R[["cong_thuc", "n_ev", "w_min", "w_med", "w_max"]]
      .to_string(index=False, formatters={"w_min": pct, "w_med": pct, "w_max": pct}))

print("\nB. CU DANH VAO NAV DANH MUC o SU KIEN TE NHAT — ton that VINH VIEN")
cols = ["cong_thuc"] + [s[0] for s in SCEN]
print(R[cols].to_string(index=False, formatters={c: pct for c in cols[1:]}))

print("\nC. CU DANH VAO NAV DANH MUC o SU KIEN TE NHAT — DAY drawdown tam thoi (truoc hoi phuc)")
cols2 = ["cong_thuc"] + [s[0] + "|DD" for s in SCEN if s[1] is not None]
print(R[cols2].to_string(index=False, formatters={c: pct for c in cols2[1:]}))

print("\nD. PHAN HOA giua cong thuc (do rong: te nhat - tot nhat, o TUNG kich ban)")
for s in [x[0] for x in SCEN]:
    v = R[s]
    print(f"  {s:26s} spread = {100*(v.min()-v.max()):.2f}pp   "
          f"(te nhat {R.loc[v.idxmin(),'cong_thuc']} {100*v.min():+.2f}%, "
          f"tot nhat {R.loc[v.idxmax(),'cong_thuc']} {100*v.max():+.2f}%)")

print("\nE. Su kien nao la 'te nhat' cho tung cong thuc trong S3 (-30% cat lo)")
for name, X in detail.items():
    i = (X.w * -0.30).idxmin()
    print(f"  {name:16s} E{int(X.loc[i,'E'])} {X.loc[i,'ngay']}  w={100*X.loc[i,'w']:.1f}% NAV "
          f"-> hit {100*X.loc[i,'w']*-0.30:+.2f}% NAV")

R.to_csv(f"{W}/mike/agents/Taylor/research/capit_stress_deep_20260731.csv", index=False)
print(f"\nwrote research/capit_stress_deep_20260731.csv")

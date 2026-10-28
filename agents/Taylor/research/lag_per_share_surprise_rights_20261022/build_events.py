# -*- coding: utf-8 -*-
"""Q1: dựng tập sự kiện LAG production (mirror pt_v23_audit_2014.py §4) + biến thể per-share PS1/PS2.
Paper-only. Đọc: data/earnings_events_classified.csv, data/earnings_surprise_data.pkl,
data/forensic_flags.csv, iss_raw.csv/tf_oshares.csv/vni.csv (kéo BQ 2026-10-21). Ghi: events_ps.csv
"""
import os, pickle
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR = 1e9; LN2 = np.log(2); HL = 3.0

with open(f"{WC}/data/earnings_surprise_data.pkl", "rb") as f:
    fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])

def surprise(np0, np1, np2, np3, np4):
    exp = np.nanmean(np.vstack([np1, np2, np3, np4]), axis=0)
    return np.clip((np0 - exp) / np.maximum(np.abs(exp), FLOOR), -5, 5)

fin["surprise_B_MA"] = surprise(*(fin[f"NP_P{k}"].values for k in range(5)))
ev = pd.read_csv(f"{WC}/data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.merge(fin[["ticker", "quarter", "Release_Date", "surprise_B_MA"] + [f"NP_P{k}" for k in range(5)] + ["NP_R"]]
              .rename(columns={"NP_R": "NP_R_pkl"}),
              on=["ticker", "quarter", "Release_Date"], how="left")
ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]; cur = row["Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
            ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))
ff = pd.read_csv(f"{WC}/data/forensic_flags.csv")
forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in ff.iterrows() if str(r["severity"]).strip() == "exclude"}
ev["forbid"] = [(tk in forx) and (rd >= forx[tk]) for tk, rd in zip(ev["ticker"], ev["Release_Date"])]

# calendar + entry = Release+5 (offset_date semantics: pos = last session <= ref)
vni = pd.read_csv(f"{HERE}/vni.csv", parse_dates=["time"]).sort_values("time")
cal = vni["time"].values.astype("datetime64[ns]")
vclose = vni.set_index("time")["Close"]
def off(ref, k):
    pos = np.searchsorted(cal, np.datetime64(ref), side="right") - 1 + k
    return pd.Timestamp(cal[pos]) if 0 <= pos < len(cal) else pd.NaT
ev["entry"] = [off(d, 5) for d in ev["Release_Date"]]
ev["exit30"] = [off(d, 30) for d in ev["Release_Date"]]
ev["vni_ret"] = [(vclose[x] / vclose[e] - 1) * 100 if pd.notna(e) and pd.notna(x) else np.nan
                 for e, x in zip(ev["entry"], ev["exit30"])]
ev["y_ex"] = ev["post_ret"] - ev["vni_ret"]
ev["C"] = (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & ~ev["forbid"] & (ev["entry"] >= "2014-01-01")
ev["U"] = ev["C"] & (ev["NP_R"] >= 15)
ev = ev[ev["C"]].copy()

# --- share counts per quarter ---
tf = pd.read_csv(f"{HERE}/tf_oshares.csv", parse_dates=["time"])
tf = tf.sort_values("time").drop_duplicates(["ticker", "quarter"], keep="last").set_index(["ticker", "quarter"])
def qminus(q, k):
    y, qq = int(q[:4]), int(q[-1]); n = y * 4 + (qq - 1) - k
    return f"{n // 4}Q{n % 4 + 1}"
iss = pd.read_csv(f"{HERE}/iss_raw.csv", parse_dates=["exright_date"])
iss = iss[(iss["event_status"] == "executed") & iss["exright_date"].notna()].copy()
iss["r"] = iss["exercise_ratio"].fillna(0.0)
NONCASH = {"Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng"}
iss["noncash"] = iss["meth"].isin(NONCASH)
iss_by = {tk: g for tk, g in iss.groupby("ticker")}

rows = []
for r in ev.itertuples():
    q = r.quarter; out = {"idx": r.Index}
    S, T = [], []
    for k in range(5):
        key = (r.ticker, qminus(q, k))
        if key in tf.index and pd.notna(tf.loc[key, "OShares"]) and tf.loc[key, "OShares"] > 0:
            S.append(float(tf.loc[key, "OShares"])); T.append(tf.loc[key, "time"])
        else:
            S.append(np.nan); T.append(pd.NaT)
    g_iss = iss_by.get(r.ticker)
    def factor(t_from, t_to, only_noncash):
        if g_iss is None or pd.isna(t_from) or pd.isna(t_to): return 1.0, 0
        m = (g_iss["exright_date"] > t_from) & (g_iss["exright_date"] <= t_to)
        if only_noncash: m &= g_iss["noncash"]
        sub = g_iss[m]
        return float(np.prod(1 + sub["r"].values)), int(((sub["r"] <= 0) & ~sub["noncash"]).sum())
    out["S0"], out["S4"] = S[0], S[4]
    out["g"] = S[0] / S[4] if np.isfinite(S[0]) and np.isfinite(S[4]) else np.nan
    E, nmiss = factor(T[4], T[0], False)
    B = [factor(T[k], T[0], True)[0] for k in range(5)]
    out["E"], out["n_ratio_missing"], out["B4"] = E, nmiss, B[4]
    if np.isfinite(out["g"]):
        if abs(out["g"] / E - 1) <= 0.02: out["share_src"] = "explained"
        elif nmiss > 0: out["share_src"] = "ratio_missing"
        else: out["share_src"] = "unexplained"
    else:
        out["share_src"] = "no_share_data"
    NP = [getattr(r, f"NP_P{k}") for k in range(5)]
    for v, useB in (("ps1", False), ("ps2", True)):
        if all(np.isfinite(S)) and all(pd.notna(x) for x in NP):
            npstar = [NP[k] * S[0] / (S[k] * (B[k] if useB else 1.0)) for k in range(5)]
            out[f"sur_{v}"] = float(surprise(*(np.array([x]) for x in npstar))[0])
            out[f"NP_R_{v}"] = ((npstar[0] / npstar[4] - 1) * 100) if (NP[4] > 0 and NP[0] > 0) else r.NP_R
            out[f"has_{v}"] = True
        else:
            out[f"sur_{v}"], out[f"NP_R_{v}"], out[f"has_{v}"] = r.surprise_B_MA, r.NP_R, False
    rows.append(out)
ps = pd.DataFrame(rows).set_index("idx")
ev = ev.join(ps)
ev["tier"] = np.where(ev["surprise_B_MA"] > 0.5, "HI", "LO")
for v in ("ps1", "ps2"):
    ev[f"U_{v}"] = ev[f"NP_R_{v}"] >= 15
    ev[f"tier_{v}"] = np.where(ev[f"sur_{v}"] > 0.5, "HI", "LO")
ev["dil2"] = ev["S0"] / (ev["S4"] * ev["B4"])
ev.to_csv(f"{HERE}/events_ps.csv", index=False)
print("C:", len(ev), "U:", int(ev["U"].sum()), "U dates:", ev.loc[ev.U, "Release_Date"].nunique())
# sanity: NP_R pkl vs CSV
chk = ev[ev.U & ev.NP_R_pkl.notna()]
print("NP_R csv vs pkl*100 max abs diff:", float((chk.NP_R - chk.NP_R_pkl * 100).abs().max()))
print("NP_R vs NP_P0/NP_P4-1 (P4>0) max abs diff:",
      float((chk.NP_R - (chk.NP_P0 / chk.NP_P4 - 1) * 100)[chk.NP_P4 > 0].abs().max()))

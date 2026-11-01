# -*- coding: utf-8 -*-
"""Việc 3: tách cú nhảy P/FV sau bước OShares quý (>10%) thành pha loãng (có ISS/AIS executed giải thích số CP mới)
vs restatement/không giải thích. Toàn bộ bước (2014+) để thống kê + 10 sự kiện cụ thể (5 nhảy lớn nhất + 5 ngẫu nhiên, seed cố định)."""
import os, sys
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "dcf_vn_calibration_20261101")
sys.path.insert(0, HERE); sys.path.insert(0, OLD); sys.path.insert(0, WC)
import level as LV      # noqa: E402  (nạp engine/D, GRID, fv)
import oshares_live as OL  # noqa: E402
P = print
pd.set_option("display.width", 250, "display.max_columns", 40)
p = pd.read_parquet(os.path.join(HERE, "data", "panel_live.parquet")).sort_values(["ticker", "t"]).reset_index(drop=True)
GT = 0.045
f = LV.fv(p, p.OShares.values, 0.0, GT)
p["lPFV"] = np.log(p.Price / f)
p["lFV"] = np.log(f); p["lP"] = np.log(p.Price); p["lO"] = np.log(p.OShares)
# bước: tháng đầu tiên mà dòng tài chính mới nhất có step=True (dòng mới xuất hiện); so với tháng ngay trước (dòng cũ)
p["new_row"] = p.groupby("ticker").time.transform(lambda s: s != s.shift(1))
prev = p.groupby("ticker")[["lPFV", "lFV", "lP", "lO", "time", "OShares", "t"]].shift(1)
ev = p[p.new_row & p.step.fillna(False).astype(bool) & (p.t.dt.year >= 2014)].copy()
for c in ("lPFV", "lFV", "lP", "lO", "time", "OShares", "t"):
    ev["prev_" + c] = prev.loc[ev.index, c]
ev = ev[ev.prev_lPFV.notna() & (ev.prev_t.notna()) & ((ev.t - ev.prev_t).dt.days < 45)]
ev["d_lPFV"] = ev.lPFV - ev.prev_lPFV
ev["d_lP"] = ev.lP - ev.prev_lP
ev["d_lO"] = ev.lO - ev.prev_lO
ev["d_lFV"] = ev.lFV - ev.prev_lFV
ev["d_lbase_g"] = ev.d_lFV + ev.d_lO            # phần FV không do số CP: FCFE nền + tăng trưởng
tks = sorted(ev.ticker.unique())
quarters, corp = OL._fetch(tks, "2026-10-30")
C = pd.DataFrame(corp)
for c in ("exright_date", "effective_date", "listing_date"):
    C[c] = pd.to_datetime(C[c], errors="coerce")
C["d"] = C.listing_date.fillna(C.exright_date).fillna(C.effective_date)
C["shares_delta"] = pd.to_numeric(C.shares_delta, errors="coerce")
C["issue_volumn"] = pd.to_numeric(C.issue_volumn, errors="coerce")
C["delta_used"] = C.shares_delta.fillna(C.issue_volumn.where(C.event_code == "ISS"))   # ISS không có shares_delta ⇒ khối lượng phát hành
C["issue_method_name_vi"] = C.issue_method_name_vi.fillna("").astype(str)
P("corp rows", len(C), "| shares_delta non-null:", f"{C.shares_delta.notna().mean():.2f}", "| delta_used non-null:", f"{C.delta_used.notna().mean():.2f}")


def explain(r):
    lo, hi = r.prev_time - pd.Timedelta(days=45), r.time - pd.Timedelta(days=0)
    e = C[(C.ticker == r.ticker) & (C.d > lo) & (C.d <= hi)]
    dl = e.delta_used.sum(min_count=1)
    tot = r.OShares - r.prev_OShares
    return pd.Series({"n_ev": len(e), "ev_delta": dl, "ev_codes": ";".join(f"{x.event_code}:{x.issue_method_name_vi[:18]}:{str(x.d)[:10]}" for x in e.itertuples()),
                      "explained": (dl / tot) if (tot != 0 and pd.notna(dl)) else np.nan})


ev = pd.concat([ev, ev.apply(explain, axis=1)], axis=1)
ev["dir"] = np.where(ev.d_lO > 0, "tang", "giam")
ev["klass"] = np.where((ev.dir == "tang") & (ev.explained >= 0.8), "PHA_LOANG(ISS/AIS khop>=80%)",
                np.where((ev.dir == "tang") & (ev.n_ev > 0), "TANG_giai_thich_1_phan",
                np.where(ev.dir == "tang", "TANG_khong_su_kien(restate?)", "GIAM(restate/gop)")))
cols = ["ticker", "prev_time", "time", "prev_OShares", "OShares", "d_lO", "d_lP", "d_lbase_g", "d_lPFV", "n_ev", "explained", "klass", "ev_codes"]
ev[cols].to_csv(os.path.join(HERE, "out", "events_all_steps.csv"), index=False)
P(f"=== TOÀN BỘ bước OShares quý >10% (2014+, hai tháng liên tiếp, FV hợp lệ cả hai): n={len(ev)}")
g = ev.groupby("klass").agg(n=("d_lPFV", "size"), med_dlPFV=("d_lPFV", "median"), med_dlO=("d_lO", "median"), med_dlP=("d_lP", "median"),
                            med_dbase_g=("d_lbase_g", "median"))
P(g.round(3).to_string())
P("tất cả: median ΔlogP/FV", round(ev.d_lPFV.median(), 3), "| median ΔlogOShares", round(ev.d_lO.median(), 3), "| median ΔlogP", round(ev.d_lP.median(), 3),
  "| median Δlog(FCFE nền+tăng trưởng)", round(ev.d_lbase_g.median(), 3))
# 10 sự kiện cụ thể
big = ev.reindex(ev.d_lPFV.abs().sort_values(ascending=False).index).head(5)
rest = ev.drop(big.index)
rnd = rest.sample(5, random_state=20261102)
sel = pd.concat([big.assign(chon="top|ΔlogP/FV|"), rnd.assign(chon="ngau nhien(seed 20261102)")])
sel[["chon"] + cols].to_csv(os.path.join(HERE, "out", "events_10.csv"), index=False)
P("=== 10 sự kiện")
P(sel[["chon", "ticker", "prev_time", "time", "prev_OShares", "OShares", "d_lO", "d_lP", "d_lbase_g", "d_lPFV", "explained", "klass", "ev_codes"]].round(3).to_string(index=False))
# đóng góp trung bình tới ΔlogP/FV: d_lPFV = d_lP − d_lFV = d_lP + d_lO − d_lbase_g
P("kiểm đồng nhất d_lPFV = d_lP + d_lO − d_lbase_g (max sai):", float((ev.d_lPFV - (ev.d_lP + ev.d_lO - ev.d_lbase_g)).abs().max()))

# ---- (A) cùng cú nhảy nhưng trên đường LIVE: live có triệt cú nhảy không?
fl = LV.fv(p, p.os_live.values, 0.0, GT)
p["lPFV_live"] = np.log(p.Price / fl)
pl_prev = p.groupby("ticker").lPFV_live.shift(1)
ev["d_lPFV_live"] = (p.lPFV_live - pl_prev).loc[ev.index]
P("=== (A) ΔlogP/FV qua bước, đường fin vs live (median theo lớp)")
P(ev.groupby("klass")[["d_lPFV", "d_lPFV_live"]].median().round(3).to_string())
P("tất cả: fin", round(ev.d_lPFV.median(), 3), "live", round(ev.d_lPFV_live.median(), 3))
# ---- (B) dai dẳng: log P/FV theo số tháng kể từ bước TĂNG OShares quý >10% gần nhất (live, s=0, g_T 4,5%)
ri = pd.read_parquet(os.path.join(OLD, "data", "row_inputs.parquet")).sort_values(["ticker", "time"])
ri["up"] = (ri.OShares / ri.groupby("ticker").OShares.shift(1) - 1) > 0.10
up = ri[ri.up][["ticker", "time"]].rename(columns={"time": "up_time"}).sort_values("up_time")
q = pd.merge_asof(p.sort_values("t"), up, left_on="t", right_on="up_time", by="ticker", direction="backward")
q["m_since"] = (q.t - q.up_time).dt.days / 30.4
q["bucket"] = pd.cut(q.m_since, [-1, 3, 6, 12, 24, 36, 60, 1e9], labels=["0-3m", "3-6m", "6-12m", "12-24m", "24-36m", "36-60m", ">60m"])
q["bucket"] = q.bucket.cat.add_categories("chưa bước").fillna("chưa bước")
tab = q.groupby("bucket", observed=True).agg(n=("lPFV_live", "size"), med_lPFV_live=("lPFV_live", "median"), med_lPFV_fin=("lPFV", "median"))
tab["medPFV_live"] = np.exp(tab.med_lPFV_live)
P("=== (B) median Price/FV (live, s=0, g_T 4,5%) theo số tháng kể từ bước TĂNG OShares quý >10% gần nhất")
P(tab.round(3).to_string())
tab.to_csv(os.path.join(HERE, "out", "events_persistence.csv"))
ev[cols + ["d_lPFV_live"]].to_csv(os.path.join(HERE, "out", "events_all_steps.csv"), index=False)

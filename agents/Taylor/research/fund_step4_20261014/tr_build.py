#!/usr/bin/env python3
"""Việc 1 — VN-Index CÓ CỔ TỨC tự dựng (nguyên mẫu nghiên cứu, CHỈ ĐỌC).

    /home/trido/thanhdt/wc_venv/bin/python tr_build.py [--cache /tmp/fund_step4_tr] [--out .]

CÔNG THỨC (một chỗ: `div_yield_daily` + `chain`)
  Rổ ngày t  = mã đang niêm yết HOSE ngày t (bảng sàn VNDirect + sự kiện chuyển sàn của
               `tav2_bq.corporate_action`), có giá phiên t-1 và số CP lưu hành.
  Trọng số   = vốn hoá ĐẦY ĐỦ phiên t-1 = Price_{t-1} × OShares_{t-1}  (VN-Index không điều chỉnh
               free-float, không trần 10%).
  y_t (điểm % cổ tức của chỉ số ngày t) = Σ_i OShares_{i,t-1} × DIV_{i,t} / Σ_i vốn hoá_{i,t-1}
               DIV_{i,t} = tổng `value_per_share` của mọi dòng DIV có `exright_date` = t (GỘP).
  TR_t = TR_{t-1} × ( VNINDEX_t / VNINDEX_{t-1} + k × y_t ),  k=1 (gộp) hoặc 0,95 (sau thuế 5%).
  ⇒ chuỗi có cổ tức = chỉ số GIÁ CHÍNH THỨC + phần cổ tức tự ước; sai số của rổ/trọng số CHỈ đi
    vào số hạng cổ tức (vài điểm cơ bản), không đi vào phần giá.

HAI KIỂM CHỨNG ĐỘC LẬP (in ra, không ép khớp)
  K1 — số tiền cổ tức: phương pháp B không đọc `corporate_action`. Với mỗi mã-ngày:
       d = Close_t/Close_{t-1} − Price_t/Price_{t-1}  (tỉ suất có cổ tức − tỉ suất giá thô) — đúng bằng
       D/P_{t-1} ở ngày chốt quyền tiền mặt, 0 ở ngày thường. Bỏ mã-ngày có sự kiện ISS (±1 phiên)
       và |d| > 25% (chia tách không gắn nhãn). So tổng theo năm với phương pháp A.
  K2 — rổ + trọng số: chỉ số GIÁ tổng hợp từ rổ (Σ w × Close-return − y) so với VN-Index chính
       thức theo năm. Lệch lớn ⇒ rổ/trọng số sai ⇒ đừng tin y.
"""
import argparse
import json
import os
import re

import db_dtypes  # noqa: F401 — cần để đọc cột DATE của BQ trong parquet
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TAX = 0.05
FAR = pd.Timestamp("2100-01-01")


def hose_spells(ca: pd.DataFrame, first_seen: pd.Series) -> pd.DataFrame:
    """Khoảng thời gian mỗi mã nằm trên HOSE: [start, end). Hai nguồn, hợp lại."""
    rows = []
    cur_floor = {}
    for fl in ("HOSE", "HNX", "UPCOM"):
        for r in json.load(open(os.path.join(HERE, "web", f"vndirect_stocks_{fl}.json")))["data"]:
            cur_floor[r["code"]] = (fl, r.get("status"), r.get("listedDate"), r.get("delistedDate"))
    # (1) mã HIỆN ở HOSE: từ listedDate (ngày lên sàn hiện tại) tới khi huỷ niêm yết.
    for code, (fl, st, ld, dd) in cur_floor.items():
        if fl != "HOSE" or not ld:
            continue
        end = pd.Timestamp(dd) if (st == "delisted" and dd and dd > ld) else FAR
        rows.append((code, pd.Timestamp(ld), end, "vnd_master"))
    # (2) mã đã RỜI HOSE (nay ở HNX/UPCOM/biến mất): sự kiện rời HOSE trong corporate_action.
    t = ca[ca.event_code.isin(["MOVE", "SUSP", "NLIS"])].copy()
    t["title"] = t.event_title_vi.fillna("")
    leave = t[t.title.str.contains(r"từ HOSE sang|Hủy niêm yết.*HOSE|GDCC trên HOSE", regex=True)]
    enter = t[t.title.str.contains(r"niêm yết.*trên (?:sàn )?HOSE|sang HOSE|giao dịch trên sàn HOSE",
                                   regex=True) & ~t.title.str.contains("Hủy")]
    have = {r[0] for r in rows}
    for code, g in leave.groupby("ticker"):
        end = pd.Timestamp(g.effective_date.max())
        if code in have:
            # đang ở HOSE lại (đã quay về) — khoảng (1) đã phủ từ listedDate; thêm khoảng TRƯỚC khi rời
            ld = pd.Timestamp(cur_floor[code][2])
            if end >= ld:
                continue
        e = enter[(enter.ticker == code) & (pd.to_datetime(enter.effective_date) < end)]
        start = pd.Timestamp(e.effective_date.min()) if len(e) else first_seen.get(code, pd.NaT)
        if pd.isna(start):
            continue
        rows.append((code, start, end, "ca_leave" if len(e) else "ca_leave_start_assumed"))
    return pd.DataFrame(rows, columns=["ticker", "start", "end", "src"])


def load(cache):
    p = pd.read_parquet(os.path.join(cache, "panel.parquet"))
    p["time"] = pd.to_datetime(p["time"])
    p = p.sort_values(["ticker", "time"]).reset_index(drop=True)
    ca = pd.read_parquet(os.path.join(cache, "ca.parquet"))
    for c in ("exright_date", "effective_date"):
        ca[c] = pd.to_datetime(ca[c])
    return p, ca


def dividends(ca):
    """DIV tiền mặt theo (mã, ex-date), GỘP. Trả (bảng tổng, thống kê lọc)."""
    d = ca[(ca.event_code == "DIV") & ca.exright_date.notna()].copy()
    n0 = len(d)
    d = d[d.event_status == "executed"]
    n1 = len(d)
    d = d[d.value_per_share > 0]
    n2 = len(d)
    # trùng HOÀN TOÀN (cùng đợt, cùng số tiền) = bản ghi lặp; khác đợt/khác tiền = hai đợt thật (cộng).
    d = d.drop_duplicates(["ticker", "exright_date", "value_per_share", "dividend_year",
                           "dividend_stage_vi"])
    n3 = len(d)
    g = d.groupby(["ticker", "exright_date"], as_index=False).value_per_share.sum()
    g.columns = ["ticker", "time", "div"]
    return g, {"div_rows": n0, "executed": n1, "value>0": n2, "sau_bo_trung": n3, "ma_ngay": len(g)}


def build(cache, out):
    p, ca = load(cache)
    idx = p[p.ticker == "VNINDEX"].set_index("time").Price.sort_index()
    s = p[p.ticker != "VNINDEX"].copy()
    first_seen = s.groupby("ticker").time.min()
    sp = hose_spells(ca, first_seen)
    div, dstat = dividends(ca)

    g = s.groupby("ticker")
    s["P1"] = g.Price.shift(1)
    s["C1"] = g.Close.shift(1)
    s["S1"] = g.OShares.shift(1)
    s["t1"] = g.time.shift(1)
    s = s[s.time >= "2013-12-31"]
    # thành viên HOSE ngày t
    s["hose"] = False
    spg = {k: v[["start", "end"]].values for k, v in sp.groupby("ticker")}
    for code, sub in s.groupby("ticker").groups.items():
        if code not in spg:
            continue
        tt = s.loc[sub, "time"].values
        m = np.zeros(len(tt), bool)
        for a, b in spg[code]:
            m |= (tt >= a) & (tt < b)
        s.loc[sub, "hose"] = m
    s = s.merge(div, on=["ticker", "time"], how="left")
    s["div"] = s["div"].fillna(0.0)
    # phiên t-1 phải là phiên liền trước của chỉ số (mã ngừng giao dịch lâu ⇒ loại ngày nối lại)
    prev_idx = pd.Series(idx.index[:-1], index=idx.index[1:])
    s["t1_ok"] = s.t1.values == s.time.map(prev_idx).values
    u = s[s.hose & s.t1_ok & s.P1.gt(0) & s.S1.gt(0) & s.Price.gt(0)].copy()
    u["mc1"] = u.P1 * u.S1
    u["divcash"] = u.S1 * u["div"]
    u["dy_i"] = u["div"] / u.P1
    bad = u[u.dy_i > 0.5]
    u.loc[u.dy_i > 0.5, ["divcash"]] = 0.0          # cổ tức > 50% giá: dữ liệu hỏng, loại + in ra
    u["tr_i"] = u.Close / u.C1 - 1
    u["pr_i"] = u.Price / u.P1 - 1
    # K1 — phương pháp B
    iss = ca[(ca.event_code == "ISS") & ca.exright_date.notna()][["ticker", "exright_date"]]
    iss_keys = set()
    days = idx.index
    pos = {d: i for i, d in enumerate(days)}
    for tk, d in iss.itertuples(index=False):
        i = pos.get(d)
        if i is None:
            j = days.searchsorted(d)
            cand = [j - 1, j, j + 1]
        else:
            cand = [i - 1, i, i + 1]
        for k in cand:
            if 0 <= k < len(days):
                iss_keys.add((tk, days[k]))
    u["iss_near"] = [(a, b) in iss_keys for a, b in zip(u.ticker, u.time)]
    u["dB"] = (u.tr_i - u.pr_i).where(~u.iss_near, 0.0)
    u.loc[u.dB.abs() > 0.25, "dB"] = 0.0
    u["divcashB"] = u.dB * u.mc1

    day = u.groupby("time").agg(mc=("mc1", "sum"), divcash=("divcash", "sum"),
                                divcashB=("divcashB", "sum"), n=("ticker", "size"),
                                trw=("tr_i", lambda x: np.nan))
    day["tr_synth"] = (u.tr_i * u.mc1).groupby(u.time).sum() / day.mc
    day["y"] = day.divcash / day.mc
    day["yB"] = day.divcashB / day.mc
    day = day.join(idx.rename("vnindex")).dropna(subset=["vnindex"])
    day["pr"] = day.vnindex / day.vnindex.shift(1) - 1
    day = day.iloc[1:] if np.isnan(day.pr.iloc[0]) else day
    day["pr_synth"] = day.tr_synth - day.y
    day["tr_gross"] = day.pr + day.y
    day["tr_net"] = day.pr + (1 - TAX) * day.y
    base = day.vnindex.iloc[0] / (1 + day.pr.iloc[0])
    day["VNINDEX_TR_gross"] = base * (1 + day.tr_gross).cumprod()
    day["VNINDEX_TR_net"] = base * (1 + day.tr_net).cumprod()
    day[["vnindex", "y", "yB", "n", "mc", "VNINDEX_TR_gross", "VNINDEX_TR_net"]].to_csv(
        os.path.join(out, "vnindex_tr_daily_proto.csv"), float_format="%.8g")
    return day, u, sp, dstat, bad, idx


def comp(x):
    return (1 + x).prod() - 1


def period(day, a, b):
    """Kỳ (a, b]: a là phiên MỐC (giá chốt ngày a), giống quy ước sổ đơn vị."""
    w = day[(day.index > a) & (day.index <= b)]
    return {"pr": comp(w.pr), "tr_gross": comp(w.tr_gross), "tr_net": comp(w.tr_net),
            "y_sum": w.y.sum(), "yB_sum": w.yB.sum(), "pr_synth": comp(w.pr_synth), "n_days": len(w)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="/tmp/fund_step4_tr")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    day, u, sp, dstat, bad, idx = build(a.cache, a.out)
    pc = lambda v: f"{100 * v:7.2f}"   # noqa: E731
    print("Lọc DIV:", dstat)
    print("Khoảng HOSE theo nguồn:", sp.src.value_counts().to_dict(), "| số mã:", sp.ticker.nunique())
    print(f"Cổ tức > 50% giá (loại): {len(bad)} mã-ngày", bad[["ticker", "time", "div", "P1"]].head(8).values.tolist())
    print("\nBẢNG 1b — theo NĂM (đv: %)  [chênh = TR − giá, điểm %]")
    print("năm   n_mã  VNI_giá  cổ_tức_A  cổ_tức_B  TR_gộp  TR_ròng  chênh_gộp chênh_ròng | giá_tổng_hợp  lệch_K2")
    out = []
    day["yr"] = day.index.year
    for yr, w in day[day.index >= "2014-01-01"].groupby("yr"):
        r = {"year": int(yr), "n": int(w.n.median()), "pr": comp(w.pr), "yA": w.y.sum(), "yB": w.yB.sum(),
             "tr_gross": comp(w.tr_gross), "tr_net": comp(w.tr_net), "pr_synth": comp(w.pr_synth),
             "last": str(w.index.max().date())}
        out.append(r)
        print(f"{yr}  {r['n']:4d}  {pc(r['pr'])}  {pc(r['yA'])}   {pc(r['yB'])}  {pc(r['tr_gross'])}  {pc(r['tr_net'])}"
              f"   {pc(r['tr_gross'] - r['pr'])}   {pc(r['tr_net'] - r['pr'])} |   {pc(r['pr_synth'])}   {pc(r['pr_synth'] - r['pr'])}")
    full = [r for r in out if r["year"] < 2026]
    print(f"TB 2014-2025: cổ tức A {100 * np.mean([r['yA'] for r in full]):.2f} | B {100 * np.mean([r['yB'] for r in full]):.2f}"
          f" | chênh gộp {100 * np.mean([r['tr_gross'] - r['pr'] for r in full]):.2f}"
          f" | |lệch K2| TB {100 * np.mean([abs(r['pr_synth'] - r['pr']) for r in full]):.2f}")
    print("\nKỲ BÁO CÁO (mốc = giá chốt ngày đầu; tới phiên cuối của dữ liệu)")
    last = day.index.max()
    per = {}
    for name, a0 in [("SpaceX từ 2026-07-01", "2026-07-01"), ("ZaloPay từ 2026-07-06", "2026-07-06"),
                     ("MTD từ 2026-09-30", "2026-09-30"), ("WTD từ 2026-10-09", "2026-10-09")]:
        r = period(day, pd.Timestamp(a0), last)
        per[name] = r
        print(f"{name:24s} → {last.date()}: giá {pc(r['pr'])}  TR gộp {pc(r['tr_gross'])}  TR ròng {pc(r['tr_net'])}"
              f"  chênh gộp {pc(r['tr_gross'] - r['pr'])}  ròng {pc(r['tr_net'] - r['pr'])}  (B: {pc(r['yB_sum'])})")
    # 10 khoản cổ tức lớn nhất trong kỳ từ 07-01 — để người đọc kiểm tay
    w = u[(u.time > "2026-07-01") & (u.divcash > 0)].copy()
    w["contrib_bp"] = 1e4 * w.divcash / w.time.map(day.mc)
    print("\nĐóng góp cổ tức lớn nhất 2026-07-02 → nay (điểm cơ bản của chỉ số):")
    print(w.sort_values("contrib_bp", ascending=False).head(12)[["time", "ticker", "div", "P1", "contrib_bp"]].to_string(index=False))
    json.dump({"asof": str(last.date()), "years": out, "periods": per, "div_filter": dstat},
              open(os.path.join(a.out, "vnindex_tr_summary.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()

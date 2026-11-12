"""E2 (job Taylor_20261112_151839/…162006) — truy các phiên |Σbook − mtm_stock|/NAV > 2% (cùng định nghĩa decompose3.live()).
Phân rã chênh D = Σbook_mv − mtm_ref thành:
  Q (lượng)  = Σ_t (qty_book_t − qty_broker_t) × px_book_t          (lô thiếu/thừa trong sổ: CORP_ACTION, bootstrap…)
  P (giá)    = Σ_t qty_broker_t × (px_book_t − broker_market_price_t) (sổ định giá bằng giá ĐÃ XÁC MINH ≠ giá broker)
  R (dư)     = D − Q − P   (mtm_stock của nav_history ≠ Σ broker qty × broker price: snapshot giờ khác / excluded / dư)
Nhãn nguyên nhân theo thành phần lớn nhất + mã đóng góp lớn nhất + cờ corp-action trong warnings phiên đó.
Pre-04/08 không có sổ: park := phần dư ⇒ D ≡ 0 theo cấu trúc (không thể > 2%)."""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../live_gap_phase1c_20261112")))
import decompose3 as D3
R = os.path.dirname(os.path.abspath(__file__)); LB = f"{D3.R}/live_books"
rows = []
for acct in ("SpaceX", "ZaloPay"):
    h = pd.read_csv(f"{D3.EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last").set_index("date")
    if acct == "ZaloPay":
        s = pd.read_csv(f"{D3.EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last").set_index("date")
    for ds in sorted(h.index):
        f = f"{LB}/{acct}_{ds}.json"
        if ds < "2026-08-04" or not os.path.exists(f) or os.path.getsize(f) == 0: continue
        H = json.load(open(f)); bb = H["by_book"]
        if acct == "SpaceX": nav = float(h.loc[ds, "nav"]); mtm = float(h.loc[ds, "mtm_stock"])
        else:
            if ds not in s.index: continue
            nav = float(s.loc[ds, "nav_b"]); mtm = float(h.loc[ds, "mtm_stock"]) - float(s.loc[ds, "outside_mv"])
        book = sum(v["mv_vnd"] for k, v in bb.items() if k != "EXCLUDED")
        D = book - mtm
        if abs(D) / nav <= 0.02: continue
        excl = set(H.get("excluded_tickers") or []) if acct == "ZaloPay" else set()
        qb, pb = {}, {}
        for l in H["lots"]:  # park_lots ⊂ lots (trùng)
            if l.get("book") == "EXCLUDED" or l["ticker"] in excl: continue
            qb[l["ticker"]] = qb.get(l["ticker"], 0) + l["qty"]
        bp = {t: v for t, v in H["broker_positions"].items() if t not in excl}
        Q = P = 0.0; per = {}
        for t in set(qb) | set(bp):
            px_b = bp.get(t, {}).get("market_price") or 0.0
            px_k = bp.get(t, {}).get("broker_market_price") or px_b
            q = (qb.get(t, 0) - bp.get(t, {}).get("qty", 0)) * px_b; p = bp.get(t, {}).get("qty", 0) * (px_b - px_k)
            Q += q; P += p; per[t] = q + p
        K = sum(v["qty"] * (v.get("broker_market_price") or v["market_price"]) for v in bp.values())
        Rr = D - Q - P  # = Σbroker qty×broker_px − mtm (đã kiểm: R ≈ K − mtm khi Q,P tách đúng)
        top = sorted(per.items(), key=lambda x: -abs(x[1]))[:3]
        ca = [w[:70] for w in H.get("warnings", []) if "corp action" in w and ds[:7] in w[:10]]
        comp = max((("lượng (lô thiếu/thừa)", Q), ("giá (verified≠broker)", P), ("dư (mtm nav_history)", Rr)), key=lambda x: abs(x[1]))[0]
        topP = sorted(((t, v["qty"] * (v["market_price"] - (v.get("broker_market_price") or v["market_price"]))) for t, v in bp.items()), key=lambda x: -abs(x[1]))[:3]
        rows.append(dict(TK=acct, date=ds, nav=nav, D_pct=100 * D / nav, Q_pct=100 * Q / nav, P_pct=100 * P / nav, R_pct=100 * Rr / nav,
                         chinh=comp, top=";".join(f"{t}:{v/nav*100:+.2f}%" for t, v in top), topP=";".join(f"{t}:{v/nav*100:+.2f}%" for t, v in topP if v), CORP_ACTION_mv=bb.get("CORP_ACTION", {}).get("mv_vnd", 0),
                         reconcile_ok=H["reconcile"].get("ok"), frame_blocked=",".join(H.get("frame_blocked_tickers") or []), n_ca_warn=len(ca)))
T = pd.DataFrame(rows); T.to_csv(f"{R}/e2_trace.csv", index=False, float_format="%.3f")
pd.set_option("display.width", 250); print(T.drop(columns=["nav"]).to_string(index=False))
print("\nN phiên >2%:", len(T), T.groupby("TK").size().to_dict()); print(T.groupby(["TK", "chinh"]).size())

# ---- Kết luận cơ học: Q≡0 (lượng sổ = broker mọi phiên) ⇒ toàn bộ chênh = giá. market_price trong live_books (replay p1c chạy
# 12/11) = BQ Close ĐIỀU CHỈNH HỒI TỐ theo corp-action xảy ra SAU ngày t; broker_market_price = Price thực = cơ sở của mtm_stock.
# Méo β do dùng Close hồi tố: Σ_t D_{t−1}·r_VNI,t (D = chênh/NAV, âm = sổ thấp hơn thực).
VNI = pd.read_csv(sorted(__import__("glob").glob(f"{R}/ledgers/*gapE_SXcold_fidT_*.csv"))[0], low_memory=False)
VNI = VNI[VNI.record_type == "DAILY"].assign(d=lambda x: pd.to_datetime(x.ymd.astype(str).str[:10])).set_index("d").vni_close.astype(float)
rv = VNI.pct_change()
allD = []
for acct in ("SpaceX", "ZaloPay"):
    import json as _j
    h = pd.read_csv(f"{D3.EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last").set_index("date")
    s = pd.read_csv(f"{D3.EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last").set_index("date") if acct == "ZaloPay" else None
    ser = {}
    for ds in sorted(h.index):
        f = f"{LB}/{acct}_{ds}.json"
        if ds < "2026-08-04" or not os.path.exists(f) or os.path.getsize(f) == 0: continue
        H = _j.load(open(f)); bp = H["broker_positions"]; ex = set(H.get("excluded_tickers") or []) if acct == "ZaloPay" else set()
        nav = float(h.loc[ds, "nav"]) if acct == "SpaceX" else (float(s.loc[ds, "nav_b"]) if ds in s.index else None)
        if nav is None: continue
        ser[pd.Timestamp(ds)] = sum(v["qty"] * (v["market_price"] - (v.get("broker_market_price") or v["market_price"])) for t, v in bp.items() if t not in ex) / nav
    S = pd.Series(ser).reindex(VNI.index).fillna(0.0)
    distort = float((S.shift(1) * rv).sum()) * 100
    allD.append(dict(TK=acct, n_gt2=int((S.abs() > 0.02).sum()), max_abs_pct=100 * float(S.abs().max()), beta_distort_pp=distort))
print(pd.DataFrame(allD).to_string(index=False)); pd.DataFrame(allD).to_csv(f"{R}/e2_beta_distort.csv", index=False, float_format="%.4f")

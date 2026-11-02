"""Peer study TV1 (r7→r8, 02/11/2026) — P/E, P/B, tỷ suất cổ tức nhóm điện / thuỷ điện VN.

Tái lập:  python3 -I peer_study.py   (đọc bq_*.csv cùng thư mục; SQL ở q_*.sql)
Nguồn:    tav2_bq.ticker (panel tháng: Price chưa điều chỉnh, PE, PB, ADV), tav2_bq.ticker_financial
          (NP quý, OShares, ROE_Trailing), tav2_bq.corporate_action (DIV = cổ tức TIỀN, VND/cp gộp).
PIT:      PE/PB trong ticker được join theo ngày công bố; yield = DPS có ngày GDKHQ trong 12T trước / giá
          tại thời điểm. Bảng 'ca cắt lợi nhuận' có thêm P/E "biết trước" (giá năm Y / LNST năm Y) — CỐ Ý
          dùng số tương lai để mô tả thị trường đã trả bao nhiêu cho lợi nhuận sau cắt; KHÔNG phải tín hiệu.
Nhãn nhóm: tự gán theo tên doanh nghiệp (ICB 7535 không tách thuỷ/nhiệt) — xem GROUP; mã không rõ = 'khac'.
"""
import numpy as np, pandas as pd, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

H = os.path.dirname(os.path.abspath(__file__))
OUT = []
def P(*a):
    s = " ".join(str(x) for x in a); OUT.append(s); print(s)

HYDRO = "AVC BHA BSA CHP DNH DRL GHC GSM HJS HNA HPD ISH ND2 NED NTH PIC QPH S4A SBA SBH SBM SEB SHP SJD SP2 TBC TMP TTE VCP VPD VSH XMP".split()
GROUP = {**{t: "thuy_dien" for t in HYDRO},
         **{t: "nhiet_dien" for t in "BTP DTK HND NBP NT2 PGV POW PPC QTP".split()},
         **{t: "tai_tao_hon_hop" for t in "BGE GEG HDG HIO REE TTA".split()},
         "KHP": "phan_phoi", "TV1": "TV1"}
BANNED = {"PC1","VVS","KSF","NKG","HSG","HVN","VJC","NVL","GEG","SBA","DMC","IMP","TRA","TOS","VTP","BAF"}

pm = pd.read_csv(f"{H}/bq_panel_monthly.csv", parse_dates=["m", "time"])
fin = pd.read_csv(f"{H}/bq_fin.csv", parse_dates=["time", "Release_Date"])
dv = pd.read_csv(f"{H}/bq_div.csv", parse_dates=["exright_date"])
ex = pd.read_csv(f"{H}/bq_exch.csv")
pm["grp"] = pm.ticker.map(GROUP).fillna("khac"); pm["y"] = pm.m.dt.year

# ---------- sàn: tiêu đề sự kiện mới nhất, đối chiếu biên độ (HOSE ±7, HNX ±10, UPCOM ±15) ----------
def exch_title(s):
    s = str(s).upper()
    if " SANG " in s: s = s.split(" SANG ", 1)[1]   # "Chuyển sàn từ UPCoM sang HOSE" ⇒ sàn đích
    for k in ("UPCOM", "HOSE", "HNX"):
        if k in s: return k
    return None
ex["ex_title"] = ex.event_title_vi.map(exch_title)
band = pm[pm.m >= "2025-01-01"].groupby("ticker").max_absret.max()
def exch_band(r):
    return "HOSE" if r <= 0.0705 else ("HNX" if r <= 0.1005 else "UPCOM")
EX = {t: exch_band(r) for t, r in band.items()}
for _, r in ex.iterrows():
    if r.ex_title and r.ticker in EX and r.ex_title != EX[r.ticker]:
        EX[r.ticker + "_note"] = f"tieu de {r.ex_title} vs bien do {EX[r.ticker]}"
    # r8 (N1): mã chuyển sàn (MOVE) từ 2025 ⇒ sàn đích theo tiêu đề sự kiện, không theo biên độ giá của giai đoạn cũ
    if r.event_code == "MOVE" and r.ex_title and str(r.effective_date) >= "2025-01-01" and r.ticker in EX:
        EX[r.ticker] = r.ex_title; EX[r.ticker + "_note"] = f"MOVE {r.effective_date} -> {r.ex_title} (ghi đè biên độ)"
pm["exch"] = pm.ticker.map(EX)

# ---------- cổ tức tiền: dedup (cùng mã, ngày, năm cổ tức, đợt) lấy max; các đợt khác nhau cùng ngày thì cộng ----------
dv = dv[dv.event_status == "executed"]
dv1 = (dv.groupby(["ticker", "exright_date", "dividend_year", "dividend_stage_vi"], dropna=False).dps.max()
       .reset_index())
dv_alt = dv.groupby(["ticker", "exright_date"]).dps.max().reset_index()   # độ nhạy: chỉ lấy max mỗi ngày
def dps_by_year(d):
    d = d.assign(y=d.exright_date.dt.year)
    return d.groupby(["ticker", "y"]).dps.sum()
DPSY, DPSY_ALT = dps_by_year(dv1), dps_by_year(dv_alt)
DPS_FY = dv1.groupby(["ticker", "dividend_year"]).dps.sum()   # theo năm tài chính cổ tức

# yield TTM tại mỗi phiên cuối tháng = tổng DPS có GDKHQ trong (t-365, t] / Price(t)
def ttm_dps(tk, t, src=dv1):
    s = src[(src.ticker == tk) & (src.exright_date > t - pd.Timedelta(days=365)) & (src.exright_date <= t)]
    return s.dps.sum()
pm["dps_ttm"] = [ttm_dps(a, b) for a, b in zip(pm.ticker, pm.time)]
pm["yld_ttm"] = pm.dps_ttm / pm.Price

# ---------- LNST năm (quý Q4 thật: Release_Date gần time) ----------
fr = fin[(fin.time - fin.Release_Date).dt.days.abs() <= 45].copy()   # bỏ dòng placeholder (Q chưa công bố)
q4 = fr[fr.quarter.str.endswith("Q4")].copy(); q4["y"] = q4.quarter.str[:4].astype(int)
q4["NP_Y"] = q4[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4)
q4 = q4.drop_duplicates(["ticker", "y"], keep="last").set_index(["ticker", "y"])
last = fr.sort_values("time").groupby("ticker").tail(1).set_index("ticker")
last["NP_TTM"] = last[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4)

def payout(tk, y):
    try:
        np_y, sh = q4.loc[(tk, y), "NP_Y"], q4.loc[(tk, y), "OShares"]
    except KeyError:
        return np.nan
    d = DPS_FY.get((tk, y), 0.0)
    return d * sh / np_y if np_y and np_y > 0 else np.nan

# ---------- 1a. danh mục peer ----------
rows = []
for tk, g in pm.groupby("ticker"):
    g = g.sort_values("m"); g26 = g[g.y == 2026]
    if g26.empty: continue
    lr = last.loc[tk] if tk in last.index else None
    sh = lr.OShares if lr is not None else np.nan
    fy = sorted(y for (t, y), v in DPS_FY.items() if t == tk and v > 0)
    run = 0   # năm cổ tức liên tục; FY2025 có thể chưa chi tới 11/2026 ⇒ bắt đầu từ 2024 nếu 2025 chưa có
    for y in range(2025 if 2025 in fy else 2024, 2010, -1):
        if y in fy: run += 1
        else: break
    rows.append(dict(ticker=tk, nhom=GROUP.get(tk, "khac"), san=EX.get(tk), banned=tk in BANNED,
                     von_hoa_ty=round(g26.Price.iloc[-1] * sh / 1e9, 0) if sh == sh else np.nan,
                     adv_2026_ty=round(g26.adv_med.median(), 3),
                     roe_ttm=round(lr.ROE_Trailing, 3) if lr is not None and lr.ROE_Trailing == lr.ROE_Trailing else np.nan,
                     pe_t10=round(g26[g26.m.dt.month == 10].PE.median(), 2) if (g26.m.dt.month == 10).any() else np.nan,
                     pb_t10=round(g26[g26.m.dt.month == 10].PB.median(), 2) if (g26.m.dt.month == 10).any() else np.nan,
                     yld_ttm_t10=round(g26.yld_ttm.iloc[-1], 4),
                     payout_2024=round(payout(tk, 2024), 2), payout_2025=round(payout(tk, 2025), 2),
                     nam_co_tuc_lien_tuc=run))
U = pd.DataFrame(rows); U.to_csv(f"{H}/out_peer_universe.csv", index=False)
P("=== 1a. Danh mục (ICB 7535 + TV1, có giao dịch 2026) — n =", len(U)); P(U.nhom.value_counts().to_dict())
P("Sàn (thuỷ điện):", U[U.nhom == "thuy_dien"].san.value_counts().to_dict())
for k, v in EX.items():
    if k.endswith("_note"): P("  ghi chú sàn", k, v)

# ---------- 1b. P/E, P/B theo nhóm-năm ----------
def tk_year(df, col, lo=0, hi=60):
    d = df[(df[col] > lo) & (df[col] < hi)]
    return d.groupby(["grp", "ticker", "y"])[col].median().reset_index()
pe_ty = tk_year(pm, "PE"); pb_ty = tk_year(pm, "PB", 0, 20)
P("\n=== 1b. P/E (trung vị theo mã-năm, 0<PE<60; rồi phân vị theo nhóm) ===")
n_drop = ((pm.PE <= 0) | (pm.PE >= 60)).groupby(pm.grp).mean().round(3).to_dict()
P("tỷ lệ mã-tháng bị loại (PE<=0 hoặc >=60):", n_drop)
tabs = []
for (gname, y), g in pe_ty.groupby(["grp", "y"]):
    if gname == "TV1": continue
    tabs.append(dict(nhom=gname, y=y, n=len(g), pe_p25=g.PE.quantile(.25), pe_med=g.PE.median(), pe_p75=g.PE.quantile(.75)))
T = pd.DataFrame(tabs)
pbm = pb_ty.groupby(["grp", "y"]).PB.agg(["median"]).rename(columns={"median": "pb_med"}).reset_index().rename(columns={"grp": "nhom"})
T = T.merge(pbm, on=["nhom", "y"], how="left")
tv = pe_ty[pe_ty.ticker == "TV1"].set_index("y").PE; tvb = pb_ty[pb_ty.ticker == "TV1"].set_index("y").PB
T.round(2).to_csv(f"{H}/out_pe_pb_by_group_year.csv", index=False)
P(T[T.nhom.isin(["thuy_dien", "nhiet_dien", "tai_tao_hon_hop"])].round(2).to_string(index=False))
P("TV1 P/E theo năm:", tv.round(2).to_dict(), "| P/B:", tvb.round(2).to_dict())

hy = pm[(pm.grp == "thuy_dien") & (pm.PE > 0) & (pm.PE < 60)].copy()
hy["adv_tier"] = pd.cut(hy.adv_med, [-1, 0.05, 0.3, 1e9], labels=["<0,05", "0,05-0,3", ">0,3"])
P("\n-- Thuỷ điện: P/E theo SÀN (trung vị mã-năm), 2019-2026 --")
SX = hy.groupby(["exch", "ticker", "y"]).PE.median().reset_index()
P(SX.groupby(["y", "exch"]).PE.median().unstack().round(2).to_string())
P("số mã theo sàn:", SX.groupby("exch").ticker.nunique().to_dict())
P("\n-- Thuỷ điện: P/E theo bậc ADV tháng (tỷ đ), gộp mã-tháng 2023-2026 --")
h2 = hy[hy.y >= 2023]
P(h2.groupby("adv_tier", observed=True).agg(n_ma_thang=("PE", "size"), n_ma=("ticker", "nunique"),
                                              pe_med=("PE", "median"), pb_med=("PB", "median")).round(2).to_string())
P("\n-- Thuỷ điện: P/E theo sàn, gộp mã-tháng 2023-2026 --")
P(h2.groupby("exch").agg(n_ma_thang=("PE", "size"), n_ma=("ticker", "nunique"), pe_med=("PE", "median"),
                         pb_med=("PB", "median"), adv_med=("adv_med", "median")).round(2).to_string())

# hồi quy mô tả log(PE) theo mã-năm thuỷ điện 2021-2026
reg = []
for (tk, y), g in hy[hy.y >= 2021].groupby(["ticker", "y"]):
    sh = q4.loc[(tk, min(y, 2025)), "OShares"] if (tk, min(y, 2025)) in q4.index else np.nan
    reg.append(dict(ticker=tk, y=y, pe=g.PE.median(), adv=g.adv_med.median(), price=g.Price.median(), sh=sh,
                    upcom=float(EX.get(tk) == "UPCOM"), hnx=float(EX.get(tk) == "HNX"),
                    payout=payout(tk, y - 1), roe=fr[(fr.ticker == tk) & (fr.time.dt.year == y)].ROE_Trailing.median()))
R = pd.DataFrame(reg); R["mcap"] = R.price * R.sh / 1e9
R = R.dropna(subset=["pe", "adv", "mcap", "payout", "roe"]); R = R[(R.payout >= 0) & (R.payout < 2) & (R.roe > 0)]
X = np.column_stack([np.ones(len(R)), R.upcom, R.hnx, np.log(R.adv + 0.005), np.log(R.mcap), R.payout, R.roe])
b, *_ = np.linalg.lstsq(X, np.log(R.pe), rcond=None)
res = np.log(R.pe) - X @ b; r2 = 1 - res.var() / np.log(R.pe).var()
P(f"\n-- Hồi quy mô tả log(PE) ~ UPCOM + HNX + log(ADV) + log(vốn hoá) + payout(năm trước) + ROE; N={len(R)} mã-năm, {R.ticker.nunique()} mã, R2={r2:.2f}")
P("   hệ số:", dict(zip(["const", "UPCOM", "HNX", "logADV", "logMcap", "payout", "ROE"], np.round(b, 3))))
P("   (mã-năm không độc lập — chỉ mô tả, không suy diễn ý nghĩa thống kê)")
R.to_csv(f"{H}/out_reg_panel.csv", index=False)

# ---------- 1c. Tỷ suất cổ tức ----------
P("\n=== 1c. Tỷ suất cổ tức tiền thực hiện theo năm (DPS có GDKHQ trong năm / giá TB cuối tháng trong năm) ===")
yr = []
for (tk, y), g in pm.groupby(["ticker", "y"]):
    if y > 2025: continue
    yr.append(dict(ticker=tk, grp=GROUP.get(tk, "khac"), y=y, px=g.Price.mean(),
                   dps=DPSY.get((tk, y), 0.0), dps_alt=DPSY_ALT.get((tk, y), 0.0)))
Y = pd.DataFrame(yr); Y["yld"] = Y.dps / Y.px; Y["yld_alt"] = Y.dps_alt / Y.px
Y.to_csv(f"{H}/out_yield_ticker_year.csv", index=False)
yh = Y[Y.grp == "thuy_dien"]
t = yh.groupby("y").agg(n=("yld", "size"), tra=("dps", lambda s: (s > 0).sum()), med_all=("yld", "median"),
                        med_payers=("yld", lambda s: s[s > 0].median()), p75=("yld", lambda s: s.quantile(.75)),
                        n_gt8=("yld", lambda s: (s > .08).sum()), n_gt10=("yld", lambda s: (s > .10).sum()),
                        n_gt12=("yld", lambda s: (s > .12).sum()))
P(t.round(3).to_string())
P("độ nhạy dedup (max/ngày) — trung vị yield người trả theo năm:",
  yh[yh.dps_alt > 0].groupby("y").yld_alt.median().round(3).to_dict())
P("TV1 yield theo năm:", Y[Y.ticker == "TV1"].set_index("y").yld.round(3).to_dict())

# chuỗi >=10%: mã nào, mấy năm liên tiếp
P("\n-- Thuỷ điện: số năm yield >=10% (2019-2025) và chuỗi liên tiếp dài nhất --")
runs = []
for tk, g in yh.groupby("ticker"):
    g = g.sort_values("y"); f = (g.yld >= .10).values
    best = cur = 0
    for v in f:
        cur = cur + 1 if v else 0; best = max(best, cur)
    runs.append(dict(ticker=tk, n_nam=len(g), n_ge10=int(f.sum()), chuoi_max=best,
                     n_ge8=int((g.yld >= .08).sum()), yld_med=round(g.yld.median(), 3),
                     yld_2023_25=round(g[g.y >= 2023].yld.mean(), 3)))
RU = pd.DataFrame(runs).sort_values(["chuoi_max", "n_ge10"], ascending=False)
RU.to_csv(f"{H}/out_yield_runs_hydro.csv", index=False)
P(RU.head(15).to_string(index=False))

# yield TTM hiện tại (tháng 10/2026) — phân bố
cur = pm[(pm.m == pm.m.max()) | (pm.m == "2026-10-01")].sort_values("m").groupby("ticker").tail(1)
ch = cur[cur.grp == "thuy_dien"]
P(f"\nYield TTM cuối kỳ (thuỷ điện, n={len(ch)}): trung vị {ch.yld_ttm.median():.3f}; người trả {ch[ch.yld_ttm>0].yld_ttm.median():.3f}; "
  f"p75 {ch.yld_ttm.quantile(.75):.3f}; >8%: {(ch.yld_ttm>.08).sum()}, >10%: {(ch.yld_ttm>.10).sum()}, >12%: {(ch.yld_ttm>.12).sum()}")
P("  mã >10%:", ch[ch.yld_ttm > .10][["ticker", "Price", "dps_ttm", "yld_ttm", "PE"]].round(3).to_dict("records"))

# lợi suất yêu cầu ngầm định = yield + g cho người trả ỔN ĐỊNH (trả >=6/7 năm 2019-2025)
P("\n-- Người trả ổn định (thuỷ điện, có cổ tức tiền >=6/7 năm 2019-2025): yield TB 2021-25 + g(DPS) --")
st = []
for tk, g in yh.groupby("ticker"):
    g = g.set_index("y")
    if (g.loc[2019:2025].dps > 0).sum() < 6: continue
    a, z = g.loc[2019:2021].dps.mean(), g.loc[2023:2025].dps.mean()
    gr = (z / a) ** (1 / 4) - 1 if a > 0 and z > 0 else np.nan
    yl = g.loc[2021:2025].yld.mean()
    cv = g.loc[2019:2025].dps.std() / g.loc[2019:2025].dps.mean()
    st.append(dict(ticker=tk, san=EX.get(tk), yld_2125=round(yl, 3), g_dps=round(gr, 3), r_ngam=round(yl + gr, 3),
                   cv_dps=round(cv, 2), pe_2025=round(pe_ty[(pe_ty.ticker == tk) & (pe_ty.y == 2025)].PE.median(), 1)))
S = pd.DataFrame(st).sort_values("yld_2125", ascending=False); S.to_csv(f"{H}/out_stable_payers.csv", index=False)
P(S.to_string(index=False))
P(f"n={len(S)}; trung vị yield {S.yld_2125.median():.3f} (p25 {S.yld_2125.quantile(.25):.3f}, p75 {S.yld_2125.quantile(.75):.3f}); "
  f"trung vị g {S.g_dps.median():.3f}; trung vị yield+g {S.r_ngam.median():.3f} (p25 {S.r_ngam.quantile(.25):.3f}, p75 {S.r_ngam.quantile(.75):.3f})")
lo_cv = S[S.cv_dps <= 0.35]
P(f"  riêng DPS ổn định (CV<=0,35, n={len(lo_cv)}): yield trung vị {lo_cv.yld_2125.median():.3f}, yield+g {lo_cv.r_ngam.median():.3f}")

# hồi quy P ~ DPS qua gốc (mã-năm thuỷ điện người trả, 2019-2025)
pp = yh[yh.dps > 0]
bslope = (pp.px * pp.dps).sum() / (pp.dps ** 2).sum()
P(f"Hồi quy P = b·DPS (qua gốc, mã-năm thuỷ điện có trả, n={len(pp)}): b={bslope:.1f} ⇒ yield ngầm {1/bslope:.3f}; "
  f"trung vị P/DPS {(pp.px/pp.dps).median():.1f} ⇒ {1/(pp.px/pp.dps).median():.3f}")

# ---------- ca cắt lợi nhuận (thí nghiệm tự nhiên) ----------
P("\n=== 1b'. Ca LNST giảm mang tính CẤU TRÚC (thuỷ điện) — P/E thị trường áp trên lợi nhuận sau cắt ===")
npy = q4.NP_Y.unstack()   # ticker x year
npy = npy.loc[[t for t in npy.index if GROUP.get(t) == "thuy_dien"]]
gmed = (npy / npy.shift(1, axis=1) - 1).median()   # tăng trưởng trung vị nhóm (thuỷ văn chung)
P("Tăng trưởng LNST trung vị nhóm theo năm (thuỷ văn chung):", gmed.round(2).dropna().to_dict())
ep = []
for tk in npy.index:
    s = npy.loc[tk]
    for y in range(2019, 2026):
        if y - 1 not in s or y not in s: continue
        a, c = s.get(y - 1), s.get(y)
        if not (a and a > 0 and c == c): continue
        rel = (c / a - 1) - gmed.get(y, 0)
        nxt = s.get(y + 1, np.nan)
        persist = (nxt == nxt) and nxt <= 0.8 * a
        if rel <= -0.30 and (persist or y == 2025):
            g = pm[(pm.ticker == tk)]
            pe_after = g[(g.y == y + 1) & (g.PE > 0)].PE.median()
            sh = q4.loc[(tk, y), "OShares"]
            pe_fore = g[g.y == y].Price.mean() * sh / c if c > 0 else np.nan
            ep.append(dict(ticker=tk, san=EX.get(tk), nam_cat=y, np_truoc=round(a / 1e9, 1), np_sau=round(c / 1e9, 1),
                           doi=round(c / a - 1, 2), doi_so_nhom=round(rel, 2),
                           np_nam_sau=round(nxt / 1e9, 1) if nxt == nxt else None,
                           pe_nam_sau_ttm=round(pe_after, 1) if pe_after == pe_after else None,
                           pe_biet_truoc=round(pe_fore, 1) if pe_fore == pe_fore else None))
E = pd.DataFrame(ep); E.to_csv(f"{H}/out_cut_episodes.csv", index=False)
P(E.to_string(index=False))
if len(E):
    P(f"Trung vị: P/E TTM năm sau cắt {E.pe_nam_sau_ttm.median():.1f} (n={E.pe_nam_sau_ttm.notna().sum()}); "
      f"P/E biết trước {E.pe_biet_truoc.median():.1f} (n={E.pe_biet_truoc.notna().sum()})")
NAMED = "BSA S4A VSH SJD HNA SHP TMP".split()
P("\n-- Các mã user nêu: LNST năm (tỷ) và P/E trung vị năm --")
for tk in NAMED:
    s = npy.loc[tk] / 1e9 if tk in npy.index else pd.Series(dtype=float)
    pe = pe_ty[pe_ty.ticker == tk].set_index("y").PE
    P(f"{tk} ({EX.get(tk)}): NP " + ", ".join(f"{y}:{v:.0f}" for y, v in s.dropna().items() if y >= 2019)
      + " | PE " + ", ".join(f"{y}:{v:.1f}" for y, v in pe.items()))
    if tk in last.index:
        lr = last.loc[tk]; px = pm[pm.ticker == tk].sort_values("m").Price.iloc[-1]
        P(f"    TTM đến {lr.quarter}: NP {lr.NP_TTM/1e9:.1f} tỷ; P/E TTM tại giá cuối {px:.0f} = {px*lr.OShares/lr.NP_TTM:.1f}")

# ---------- hình ----------
FIG = os.path.join(H, "figs"); os.makedirs(FIG, exist_ok=True)
th = T[T.nhom == "thuy_dien"].set_index("y")
fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.fill_between(th.index, th.pe_p25, th.pe_p75, color="#9ecae1", alpha=.6, label="Thuỷ điện niêm yết: p25–p75")
ax.plot(th.index, th.pe_med, color="#08519c", lw=2, marker="o", label="Thuỷ điện: trung vị")
tn = T[T.nhom == "nhiet_dien"].set_index("y")
ax.plot(tn.index, tn.pe_med, color="#999", lw=1.2, ls="--", label="Nhiệt điện: trung vị")
ax.plot(tv.index, tv.values, color="#d62728", marker="s", lw=1.5, label="TV1")
ax.set_ylabel("P/E (lần)"); ax.set_title("P/E trailing theo năm (trung vị theo mã-năm)", fontsize=10)
ax.legend(fontsize=7.5, frameon=False); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(f"{FIG}/peer_pe_hist.png", dpi=150)
fig, ax = plt.subplots(figsize=(7.2, 3.6))
v = yh[yh.dps > 0].yld * 100
ax.hist(v.clip(upper=25), bins=np.arange(0, 26, 1), color="#6baed6", edgecolor="white")
for x, c, l in [(6.8, "#2ca02c", "Tiết kiệm 12T Big-4 (online) 6,8%"), (7.4, "#ff7f0e", "CCTG 12T Big-4 7,4%"), (4.58, "#7f7f7f", "TPCP 10 năm 4,58%")]:
    ax.axvline(x, color=c, ls="--", lw=1.3, label=l)
ax.axvline(v.median(), color="#08519c", lw=2, label=f"Trung vị thuỷ điện có trả {v.median():.1f}%")
ax.set_xlabel("Tỷ suất cổ tức tiền thực hiện trong năm (%), 2019–2025 (cắt đuôi ở 25%)"); ax.set_ylabel("số mã-năm")
ax.legend(fontsize=7.5, frameon=False); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(f"{FIG}/peer_yield_dist.png", dpi=150)
fig, ax = plt.subplots(figsize=(7.2, 3.6))
cc = U[(U.nhom == "thuy_dien") & U.pe_t10.between(0, 40)]
col = cc.san.map({"HOSE": "#08519c", "HNX": "#ff7f0e", "UPCOM": "#6baed6"})
ax.scatter(cc.adv_2026_ty + 0.002, cc.pe_t10, c=col, s=28)
for _, r in cc.iterrows(): ax.annotate(r.ticker, (r.adv_2026_ty + 0.002, r.pe_t10), fontsize=6.5, xytext=(2, 2), textcoords="offset points")
t1 = U[U.ticker == "TV1"].iloc[0]
ax.scatter([t1.adv_2026_ty], [t1.pe_t10], c="#d62728", marker="s", s=40); ax.annotate("TV1", (t1.adv_2026_ty, t1.pe_t10), color="#d62728", fontsize=8, xytext=(3, 3), textcoords="offset points")
ax.set_xscale("log"); ax.set_xlabel("GTGD trung vị/phiên 2026 (tỷ đ, log)"); ax.set_ylabel("P/E tháng 10/2026")
ax.set_title("Thuỷ điện: P/E so với thanh khoản (xanh đậm HOSE · cam HNX · xanh nhạt UPCOM)", fontsize=9)
ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(f"{FIG}/peer_pe_vs_adv.png", dpi=150)



# ---------- r8: ước lượng vững của lợi suất yêu cầu (B1) ----------
P("\n=== r8-B1. Lợi suất yêu cầu: các ước lượng vững (mã-năm thuỷ điện có trả cổ tức) ===")
pp2 = pp.copy(); pp2["w"] = pp2.dps ** 2
ob = pp2.assign(contrib=pp2.w / pp2.w.sum()).sort_values("contrib", ascending=False)
P("5 quan sát nặng nhất trong hồi quy qua gốc (trọng số DPS²):", [(r.ticker, int(r.y), round(r.dps), round(r.yld, 3), round(r.contrib, 3)) for r in ob.head(5).itertuples()])
pay_fy = {}
for r in pp2.itertuples():   # payout theo năm cổ tức: DPS năm đó × cổ phần / LNST năm trước
    pay_fy[(r.ticker, r.y)] = payout(r.ticker, r.y - 1)
pp2["pay"] = [pay_fy[(a, b)] for a, b in zip(pp2.ticker, pp2.y)]
spec = pp2[(pp2.pay > 1.5)]
P("quan sát payout>150% (cổ tức đặc biệt/trả từ lợi nhuận giữ lại) bị loại khi ước lượng vững:", [(r.ticker, int(r.y), round(r.pay, 2)) for r in spec.itertuples()])
q = pp2[~pp2.index.isin(spec.index)]
b_ex = (q.px * q.dps).sum() / (q.dps ** 2).sum()
q5 = ob.iloc[5:]; b_ex5 = (q5.px * q5.dps).sum() / (q5.dps ** 2).sum()
r_med = float(1 / (pp.px / pp.dps).median()); r_mean = float(pp.yld.mean())
P(f"  hồi quy qua gốc đủ mẫu {1/bslope:.4f} | bỏ payout>150% {1/b_ex:.4f} | bỏ 5 quan sát nặng nhất {1/b_ex5:.4f} | trung vị yield {pp.yld.median():.4f} (P/DPS: {r_med:.4f}) | trung bình {r_mean:.4f}")
P(f"  nhóm DPS ổn định (CV<=0,35, n={len(lo_cv)}): yield+g p25 {lo_cv.r_ngam.quantile(.25):.3f} · trung vị {lo_cv.r_ngam.median():.3f} · p75 {lo_cv.r_ngam.quantile(.75):.3f}; dải r_ngầm min..max {S.r_ngam.min():.3f}..{S.r_ngam.max():.3f}")
P(f"  yield TTM trung vị người trả 2026 (g=0): {ch[ch.yld_ttm>0].yld_ttm.median():.4f}")
P("  ⇒ Ke KHÔNG xác định được từ peer: yield thuần 7–9%, yield+g 7–21% (rơi theo mã); khung fleet domestic_v2 r=12,25%.")
P("\n=== r8. Lịch sử cổ tức tiền TV1 theo năm cổ tức (corporate_action DIV, đã thực hiện) ===")
P({int(k[1]): float(v) for k, v in DPS_FY.items() if k[0] == "TV1"})
P("  (DPS_FY chỉ có từ 2015 theo q_div.sql; năm vắng = không có sự kiện DIV tiền trong dữ liệu)")

# ---------- r8-N2: cách suy hệ số payout ----------
P("\n=== r8-N2. Cách suy hệ số payout (P/E thuỷ điện theo bậc payout năm trước) ===")
padj_all = R[R.payout < .5].pe.median() / R.pe.median()
R["pt0"] = np.where(R.payout == 0, "p=0", np.where(R.payout < .5, "0<p<50%", "p>=50%"))
P(R.groupby("pt0").agg(n=("pe", "size"), n_ma=("ticker", "nunique"), pe_med=("pe", "median")).round(2).to_string())
by_y = R.groupby("y").apply(lambda g: pd.Series(dict(n_all=len(g), n_low=int((g.payout < .5).sum()), r=(g[g.payout < .5].pe.median() / g.pe.median()) if (g.payout < .5).sum() >= 3 else np.nan)), include_groups=False)
P(by_y.round(3).to_string())
fac_year = float(by_y.r.median())
fac_0p = float(R[(R.payout > 0) & (R.payout < .5)].pe.median() / R.pe.median())
P(f"hệ số gộp {padj_all:.3f} | chuẩn hoá theo năm (trung vị các năm đủ ≥3 quan sát) {fac_year:.3f} | chỉ nhóm 0<p<50% {fac_0p:.3f}")
P(f"payout trung vị FY2025: UPCOM {U[(U.nhom=='thuy_dien')&(U.san=='UPCOM')].payout_2025.median():.2f} vs HOSE {U[(U.nhom=='thuy_dien')&(U.san=='HOSE')].payout_2025.median():.2f} ⇒ P/E UPCOM đã phản ánh payout thấp một phần: chiết khấu payout chồng nhẹ (chân P/E nghiêng bảo thủ)")

# ---------- r8-N4: peer tư vấn ICB 2791 (TV2/TV3/TV4) + ghi chú nhãn ----------
P("\n=== r8-N4. Peer TƯ VẤN (ICB 2791): TV2, TV3, TV4 — P/E trung vị năm và E/P ===")
ad = pd.read_csv(f"{H}/bq_adv.csv", parse_dates=["m", "time"]); ad["y"] = ad.m.dt.year
adp = ad[(ad.PE > 0) & (ad.PE < 60)].groupby(["ticker", "y"]).PE.median().unstack()
adp.round(2).to_csv(f"{H}/out_adv_peers_pe.csv")
P(adp.round(1).to_string())
ep26 = (1 / adp[2026]).round(3).to_dict(); ep2425 = (1 / adp[[2024, 2025]].median(axis=1)).round(3).to_dict()
P("E/P 2026 YTD:", ep26, "| E/P trung vị 2024-25:", ep2425, "(TV2 P/E 2023-25 bị méo bởi LNST thấp sau lỗ — loại khỏi trung vị)")
vals = [1 / adp.loc[t, 2026] for t in ("TV3", "TV4")] + [1 / adp.loc[t, [2024, 2025]].median() for t in ("TV3", "TV4")]
P(f"  E/P tư vấn (TV3, TV4; 2026 YTD & 2024-25): {min(vals):.3f}–{max(vals):.3f}; TV2 2026: {1/adp.loc['TV2',2026]:.3f}")
adv = pd.read_csv(f"{H}/bq_adv_div.csv", parse_dates=["exright_date"])
P("DPS tư vấn theo năm cổ tức:", {t: g.set_index("dividend_year").dps.to_dict() for t, g in adv.groupby("ticker")})
P("GHI CHÚ NHÃN: nhóm thuỷ điện gán theo TÊN doanh nghiệp (không universe_pit); chỉ mã còn giao dịch 2026 ⇒ survivorship nhẹ cho yield 2019–25;"
  " SBA thuộc danh sách hạn chế của fleet nhưng vẫn là peer hiệu chuẩn (không phải mã khuyến nghị).")
n_sba = pm[(pm.ticker == "SBA") & (pm.y == 2026) & (pm.PE > 0) & (pm.PE < 60)].PE.median()
P(f"  SBA P/E 2026 YTD {n_sba:.2f}; bỏ SBA khỏi mẫu 2026 YTD ⇒ trung vị nhóm {SX[(SX.y==2026)&(SX.ticker!='SBA')].PE.median():.2f} (có SBA {SX[SX.y==2026].PE.median():.2f}); UPCOM p25/median {SX[(SX.y==2026)&(SX.exch=='UPCOM')&(SX.ticker!='SBA')].PE.quantile(.25):.2f}/{SX[(SX.y==2026)&(SX.exch=='UPCOM')&(SX.ticker!='SBA')].PE.median():.2f}")

# ---------- 1d. Hiệu chuẩn cho TV1 (ghi peer_calib.json để valuation.py đọc) ----------
import json
h26 = SX[SX.y == 2026]
up26 = h26[h26.exch == "UPCOM"].PE
cal = dict(
    pe_lo=round(up26.quantile(.25), 2), pe_mid=round(up26.median(), 2), pe_hi=round(h26.PE.median(), 2),
    pe_note="lo = p25 thuỷ điện UPCOM 2026 YTD; mid = trung vị thuỷ điện UPCOM 2026 YTD; hi = trung vị toàn nhóm thuỷ điện 2026 YTD (trung vị mã-năm, 0<PE<60)",
    n_upcom=int(up26.size), n_all=int(h26.PE.size),
    r_lo=round(float(ch[ch.yld_ttm > 0].yld_ttm.median()), 4),
    r_mid=round(float(1 / bslope), 4),
    r_hi=round(float(lo_cv.r_ngam.median()), 4),
    r_note="lo = yield TTM trung vị thuỷ điện có trả (cuối kỳ 2026, g=0); mid = yield ngầm hồi quy P=b·DPS (mã-năm 2019-25); hi = yield+g trung vị nhóm DPS ổn định (CV<=0,35)",
    ke_range=[0.09, 0.13], ke_centre=0.12,
    ke_note="Ke = KHOẢNG chưa xác định 9–13%; tâm 12% (khung fleet domestic_v2 r=12,25% + E/P chân P/E ≈13,5% + tư vấn E/P 11–16%); peer yield thuần 7–9% là cận dưới",
    r_robust_median=round(float(pp.yld.median()), 4), r_robust_ex_special=round(float(1 / b_ex), 4), r_robust_ex_top5=round(float(1 / b_ex5), 4),
    upcom_coef=round(float(b[1]), 3), yld_payers_med_2019_25=round(float(yh[yh.dps > 0].yld.median()), 4))
# Điều chỉnh payout: TV1 trả 27–40% LNST (+20% quỹ KTPL); thị trường trả P/E thấp hơn cho thuỷ điện payout <50%
padj_all = R[R.payout < .5].pe.median() / R.pe.median(); padj_24 = R[(R.y >= 2024) & (R.payout < .5)].pe.median() / R[R.y >= 2024].pe.median()
R["pt"] = pd.cut(R.payout, [-.01, .5, .8, 2], labels=["<50%", "50-80%", ">80%"])
P("\n-- P/E thuỷ điện theo bậc payout năm trước (mã-năm 2021-26) --")
P(R.groupby("pt", observed=True).agg(n=("pe", "size"), n_ma=("ticker", "nunique"), pe_med=("pe", "median")).round(2).to_string())
P(f"hệ số điều chỉnh payout <50% / toàn mẫu: 2021-26 {padj_all:.3f}; 2024-26 {padj_24:.3f}; payout trung vị thuỷ điện 2024 {U[U.nhom=='thuy_dien'].payout_2024.median():.2f}, 2025 {U[U.nhom=='thuy_dien'].payout_2025.median():.2f}")
# kiểm chéo bằng hồi quy mô tả: TV1 (UPCOM, ADV 0,4 tỷ, vốn hoá 528 tỷ, payout 0,335, ROE 0,14–0,185)
for roe in (0.14, 0.185):
    xv = np.array([1, 1, 0, np.log(0.405), np.log(528), 0.335, roe])
    P(f"   hồi quy ⇒ P/E dự báo cho hồ sơ TV1 (ROE {roe}): {np.exp(xv @ b):.2f}")
cal.update(payout_adj=round(float(padj_all), 3), payout_adj_2024=round(float(padj_24), 3),
           pe_lo_adj=round(cal["pe_lo"] * padj_all, 2), pe_mid_adj=round(cal["pe_mid"] * padj_all, 2), pe_hi_adj=round(cal["pe_hi"] * padj_all, 2))
json.dump(cal, open(f"{H}/peer_calib.json", "w"), ensure_ascii=False, indent=1)
P("\n=== 1d. Hiệu chuẩn ===", json.dumps(cal, ensure_ascii=False))
P("Thuỷ điện UPCOM 2026 YTD: n", up26.size, "p25", round(up26.quantile(.25), 2), "median", round(up26.median(), 2),
  "| HOSE median", round(h26[h26.exch == "HOSE"].PE.median(), 2), "| HNX", round(h26[h26.exch == "HNX"].PE.median(), 2))
P("P/B thuỷ điện 2026 (trung vị mã-năm): p25", round(pb_ty[(pb_ty.grp == 'thuy_dien') & (pb_ty.y == 2026)].PB.quantile(.25), 2),
  "median", round(pb_ty[(pb_ty.grp == 'thuy_dien') & (pb_ty.y == 2026)].PB.median(), 2))
open(f"{H}/peer_study_out.txt", "w").write("\n".join(OUT) + "\n")

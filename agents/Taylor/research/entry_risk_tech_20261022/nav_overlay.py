#!/usr/bin/env python3
"""Q1 (timing) + Q2 (nhóm rủi ro đuôi) cho BAL + LAG trên ledger R3 park0 đã pin — theo PREREG.md (md5 ba8a81f1…).

Overlay bậc 1: NAV'(t) = NAV_pin(t) + Σ Δ_i(t) (PREREG §5). KHÔNG chạy lại engine, KHÔNG ghi file canonical.
Chạy (threads=1): OMP_NUM_THREADS=1 BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate \
    /home/trido/thanhdt/wc_venv/bin/python nav_overlay.py
"""
import gzip, hashlib, itertools, os, sys
import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
os.environ["BQ_LOCAL_CACHE"] = "data/bq_cache_asof20260729_postrestate"  # CÙNG vintage ledger pin (ép, không setdefault: env phiên = data/bq_cache)
sys.path.insert(0, WC); os.chdir(WC)
from simulate_holistic_nav import bq  # noqa: E402

LEDGERS = {
    "pin0": ("data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz", "537e349b5589408c994f8aceafeb9a39"),
    "pin1M": ("data/pinned_ledgers/2026-10-08__R3-park0-pin1M-SO-CHINH__a6ba34d8.csv.gz", "a6ba34d83a4d374a73293d897c0b43d9"),
}
PINNED = {"pin0": dict(cagr=0.2212070836714919, maxdd=-0.16231313361254973), "pin1M": dict(cagr=0.2542, maxdd=-0.139)}
SEED, NB = 20261022, 2000
IS_END = pd.Timestamp("2019-12-31")
IRP_DIR = os.environ.get("IRP_DEP1M_DIR", "/tmp/irp_dep1m")
sys.path.insert(0, IRP_DIR); import idle_rate_proxy as irp  # noqa: E402

RULES = ["R1_LIMIT2", "R2_GAPSKIP3", "R3_PULLBACK"]
GROUPS = ["G_VOL", "G_RUN", "G_DEEP"]


def load(tag):
    path, md5 = LEDGERS[tag]
    raw = gzip.open(path).read()
    got = hashlib.md5(raw).hexdigest()
    assert got == md5, (tag, got)
    d = pd.read_csv(path, low_memory=False)
    tx = d[d.record_type == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx["ymd"])
    for c in ("shares", "adj_price", "buy_amount", "sell_amount", "fee"):
        tx[c] = tx[c].astype(float)
    dl = d[d.record_type == "DAILY"].copy(); dl["ymd"] = pd.to_datetime(dl["ymd"])
    dl = dl.set_index("ymd")[["nav_bal_ref", "nav_lag_ref", "combined_nav", "bal_stocks_ref", "lag_stocks_ref",
                              "cap_bal", "cap_lag", "rebal_cost"]].astype(float)
    dl["rebal_cost"] = dl["rebal_cost"].fillna(0.0)
    met = d[d.record_type == "METRIC"].set_index("key")["value"].astype(float)
    print(f"[{tag}] md5 OK {md5} | TX {len(tx)} | DAILY {len(dl)} {dl.index.min().date()}→{dl.index.max().date()}")
    return tx, dl, met


def metrics(nav):
    nav = nav.dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    sh = r.mean() / r.std(ddof=1) * np.sqrt(252)
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr, sharpe=sh, maxdd=dd, calmar=cagr / abs(dd))


def loyo_cagr(nav):
    """CAGR khi bỏ từng năm: tích (1+r_năm) trừ năm k, mũ 1/(số năm-lịch còn lại)."""
    nav = nav.dropna()
    last = nav.groupby(nav.index.year).apply(lambda s: s.index[-1])
    prev_v, prev_t, rets, fr = nav.iloc[0], nav.index[0], {}, {}
    for y, t in last.items():
        rets[int(y)] = nav[t] / prev_v - 1; fr[int(y)] = (t - prev_t).days / 365.25; prev_v, prev_t = nav[t], t
    out = {}
    for y in rets:
        ks = [k for k in rets if k != y]
        out[y] = np.prod([1 + rets[k] for k in ks]) ** (1 / sum(fr[k] for k in ks)) - 1
    return out, rets


def combine(dl, nav_bal, nav_lag):
    """NAV tổng = replay lợi suất 2 book ref × trọng số allocator (cap_*) phiên trước − rebal_cost (control: khớp 1e-14)."""
    rb, rl = nav_bal.pct_change(), nav_lag.pct_change()
    c0 = dl["combined_nav"].shift()
    r = (dl["cap_bal"].shift() * (1 + rb) + dl["cap_lag"].shift() * (1 + rl)) / c0 - 1 - dl["rebal_cost"] / c0
    return (1 + r.fillna(0)).cumprod() * dl["combined_nav"].iloc[0]


def cluster_boot(vals, clus, mask_a=None, stat="mean", seed=SEED):
    """Bootstrap cụm. stat mean (Δ trung bình của vals) hoặc diff (mean vals|a − mean vals|~a)."""
    us, ci = np.unique(clus, return_inverse=True)
    rng = np.random.default_rng(seed)
    nc = len(us)
    if stat == "mean":
        s = np.bincount(ci, weights=vals, minlength=nc); n = np.bincount(ci, minlength=nc).astype(float)
        est = s.sum() / n.sum()
        bs = []
        for _ in range(NB):
            b = rng.integers(0, nc, nc); bs.append(s[b].sum() / n[b].sum())
    else:
        a = mask_a
        sA = np.bincount(ci, weights=vals * a, minlength=nc); nA = np.bincount(ci, weights=a.astype(float), minlength=nc)
        sB = np.bincount(ci, weights=vals * ~a, minlength=nc); nB = np.bincount(ci, weights=(~a).astype(float), minlength=nc)
        est = sA.sum() / nA.sum() - sB.sum() / nB.sum()
        bs = []
        for _ in range(NB):
            b = rng.integers(0, nc, nc)
            bs.append(sA[b].sum() / max(nA[b].sum(), 1) - sB[b].sum() / max(nB[b].sum(), 1))
    bs = np.array(bs)
    p = min(2 * min((bs >= 0).mean(), (bs <= 0).mean()), 1.0)
    return est, np.percentile(bs, [2.5, 97.5]), p, nc


def holm(ps, alpha=0.05):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); ok = np.zeros(m, bool)
    for i, j in enumerate(o):
        if ps[j] <= alpha / (m - i): ok[j] = True
        else: break
    return ok


# ---------------------------------------------------------------- dữ liệu
ledg = {t: load(t) for t in LEDGERS}
tks = sorted(set(ledg["pin0"][0]["ticker"].dropna()) | set(ledg["pin1M"][0]["ticker"].dropna()))
px = bq(f"""SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({",".join(f"'{x}'" for x in tks)}) AND t.time >= DATE '2012-10-01' AND t.Close > 0""")
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"])
SER = {tk: g.set_index("time")[["Open", "High", "Low", "Close"]].astype(float) for tk, g in px.groupby("ticker")}
CAL = ledg["pin0"][1].index
CLOSE = px.pivot(index="time", columns="ticker", values="Close").reindex(CAL.union(px["time"].unique())).ffill().reindex(CAL)
print(f"[panel] {len(px):,} dòng / {len(SER)} mã")
RATE = pd.Series(np.asarray(irp.r_idle_series(pd.Series(CAL.date), tier="dep1m"), float) / 100, index=CAL)  # %/năm → tỷ lệ
DAYS = pd.Series(np.r_[0, np.diff(CAL.values).astype("timedelta64[D]").astype(int)], index=CAL)


def selfcheck_stocks(tag):
    tx, dl, _ = ledg[tag]
    t = tx[~tx["reason"].astype(str).str.startswith("MTM")]
    sgn = np.where(t["action"] == "buy", 1.0, -1.0)
    flow = pd.DataFrame({"ymd": t["ymd"], "book": t["book"], "ticker": t["ticker"], "sh": sgn * t["shares"]})
    res = {}
    for bk, col in (("BAL", "bal_stocks_ref"), ("LAG", "lag_stocks_ref")):
        f = flow[flow.book == bk].pivot_table(index="ymd", columns="ticker", values="sh", aggfunc="sum")
        hold = f.reindex(CAL).fillna(0).cumsum()
        hold = hold.where(hold.abs() > 1e-6, 0.0)
        val = (hold * CLOSE[hold.columns]).sum(axis=1)
        err = (val - dl[col]).abs()
        res[bk] = (err.max(), (err > 1).mean(), err.idxmax())
    return res


SKIPPED = []


def positions(tag):
    tx, dl, _ = ledg[tag]
    out = []
    for hid, g in tx.groupby("holding_id"):
        s = g[g.action == "sell"]
        if s.empty or not s["reason"].isin(["TIME", "STOP", "MTM_UNREALIZED"]).any():
            continue
        b = g[g.action == "buy"].sort_values("ymd")
        if b.empty:
            SKIPPED.append(hid); continue
        bd = b.groupby("ymd").agg(sh=("shares", "sum"), amt=("buy_amount", "sum"), fee=("fee", "sum"))
        x = s["ymd"].max(); sell_amt = s["sell_amount"].sum(); sell_fee = s["fee"].sum()
        sf = sell_fee / sell_amt if sell_amt > 0 else 0.0
        if (s["reason"] == "MTM_UNREALIZED").all():
            sf = 0.0035
            sell_fee = sell_amt * sf
        B = bd["amt"].sum() + bd["fee"].sum()
        out.append(dict(hid=hid, tag=tag, book=g["book"].iloc[0], ticker=g["ticker"].iloc[0], play=g["play_type"].iloc[0],
                        e=bd.index[0], x=x, bd=bd, S=bd["sh"].sum(), B=B, bcf=1 + bd["fee"].sum() / bd["amt"].sum(),
                        sf=sf, px_exit=sell_amt / s["shares"].sum(), pc=bd["amt"].sum() / bd["sh"].sum(),
                        ret=(sell_amt - sell_fee) / B - 1, reason=",".join(sorted(set(s["reason"])))))
    return out


def features_and_rules(p):
    g = SER.get(p["ticker"])
    o = dict(VOL60=np.nan, RUN20=np.nan, DIST52=np.nan, GAP=np.nan, MAE=np.nan, open_dev=np.nan)
    rules = {r: None for r in RULES}
    if g is None or p["e"] not in g.index:
        return o, rules
    t = g.index; k = t.get_loc(p["e"])
    C, O, H, L = g["Close"].values, g["Open"].values, g["High"].values, g["Low"].values
    xi = t.searchsorted(p["x"], side="right") - 1
    o["MAE"] = L[k:xi + 1].min() / p["pc"] - 1
    o["open_dev"] = O[k] / p["pc"] - 1
    if k >= 61:
        lr = np.diff(np.log(C[k - 61:k])); o["VOL60"] = lr.std(ddof=1) * np.sqrt(250)
    if k >= 21: o["RUN20"] = C[k - 1] / C[k - 21] - 1
    if k >= 250: o["DIST52"] = C[k - 1] / H[k - 250:k].max() - 1
    if k < 1 or k + 2 >= len(t):
        return o, rules
    R = C[k - 1]; o["GAP"] = O[k] / R - 1
    # R1 LIMIT2
    lim = R * 0.98; r1 = ("NOFILL", None, None)
    for j in range(3):
        if L[k + j] <= lim:
            r1 = ("FILL", t[k + j], min(O[k + j], lim)); break
    rules["R1_LIMIT2"] = r1
    rules["R2_GAPSKIP3"] = ("NOFILL", None, None) if o["GAP"] > 0.03 else ("CONTROL", None, None)
    f = k + 1 if C[k] < R else (k + 2)
    rules["R3_PULLBACK"] = ("FILL", t[f], O[f])
    for r, v in rules.items():  # khớp sau/bằng ngày thoát ⇒ coi như không khớp (ghi Deviation)
        if v[0] == "FILL" and v[1] >= p["x"]:
            rules[r] = ("NOFILL_LATE", None, None)
    return o, rules


def delta_series(p, kind, fill=None, carry=False):
    """Δ_i(t) trên CAL. kind: 'fill' (khớp ngày fill[0] giá fill[1], cùng ngân sách B) | 'nofill' | 'half'."""
    idx = CAL[(CAL >= p["e"])]
    bd = p["bd"]
    Sc = bd["sh"].reindex(idx).fillna(0).cumsum(); Ac = (bd["amt"] + bd["fee"]).reindex(idx).fillna(0).cumsum()
    if kind == "half":
        Sv, Av = Sc / 2, Ac / 2
    elif kind == "nofill":
        Sv, Av = Sc * 0, Ac * 0
    else:
        fd, fpx = fill
        Sv = pd.Series(np.where(idx >= fd, p["B"] / (fpx * p["bcf"]), 0.0), index=idx)
        Av = pd.Series(np.where(idx >= fd, p["B"], 0.0), index=idx)
    Ct = CLOSE[p["ticker"]].reindex(idx).values
    pre = idx < p["x"]
    d = np.where(pre, (Sv.values - Sc.values) * Ct + (Ac.values - Av.values), 0.0)
    xi = np.argmax(idx >= p["x"])
    Sfin_c, Sfin_v = Sc.values[xi], Sv.values[xi]
    frozen = (Sfin_v - Sfin_c) * p["px_exit"] * (1 - p["sf"]) + (Ac.values[xi] - Av.values[xi])
    d = np.where(pre, d, frozen)
    if carry:
        cashdiff = np.where(pre, Ac.values - Av.values, frozen)
        acc = np.cumsum(np.r_[0, cashdiff[:-1] * RATE.reindex(idx).values[1:] * DAYS.reindex(idx).values[1:] / 365.0])
        d = d + acc
    s = pd.Series(0.0, index=CAL); s.loc[idx] = d
    return s


# ---------------------------------------------------------------- self-check control
print("\n[SELF-CHECK]")
for tag in LEDGERS:
    tx, dl, met = ledg[tag]
    m = metrics(dl["combined_nav"])
    print(f"  ({tag}) tính lại từ DAILY: CAGR {m['cagr']*100:.4f}% Sharpe {m['sharpe']:.4f} MaxDD {m['maxdd']*100:.4f}% "
          f"Calmar {m['calmar']:.4f} | METRIC pin: {met.get('cagr', np.nan)*100:.4f}% {met.get('sharpe_252', np.nan):.4f} "
          f"{met.get('max_dd', np.nan)*100:.4f}% {met.get('calmar', np.nan):.4f}")
    rep = combine(dl, dl["nav_bal_ref"], dl["nav_lag_ref"])
    print(f"  ({tag}) replay NAV tổng từ 2 book ref × cap_* (Δ=0): max |err| {(rep - dl['combined_nav']).abs().max():.4f} VND, "
          f"lệch NAV cuối {rep.iloc[-1] - dl['combined_nav'].iloc[-1]:.4f} VND")
    for bk, (mx, frac, at) in selfcheck_stocks(tag).items():
        print(f"  ({tag}) [chẩn đoán, KHÔNG phải cổng] dựng lại {bk} stocks = Σ cp×Close cache vs DAILY: max |err| {mx:,.0f} VND (ngày {at.date()}), "
              f"tỷ lệ ngày err>1 VND {frac*100:.2f}%")

POS = {tag: positions(tag) for tag in LEDGERS}
print(f"  holding_id có lệnh bán thoát nhưng KHÔNG có buy (bỏ qua): {len(SKIPPED)} {SKIPPED[:5]}")
rows = []
for tag, ps in POS.items():
    for p in ps:
        f, rl = features_and_rules(p)
        p["feat"], p["rules"] = f, rl
        rows.append(dict(tag=tag, hid=p["hid"], book=p["book"], ticker=p["ticker"], play=p["play"], e=p["e"], x=p["x"],
                         B=p["B"], ret=p["ret"], reason=p["reason"], **f,
                         **{f"{r}_st": (rl[r][0] if rl[r] else "NA") for r in RULES},
                         **{f"{r}_px": (rl[r][2] if rl[r] else np.nan) for r in RULES},
                         **{f"{r}_fd": (rl[r][1] if rl[r] else pd.NaT) for r in RULES}))
P = pd.DataFrame(rows)
P["q"] = P["e"].dt.year.astype(str) + "Q" + P["e"].dt.quarter.astype(str)
P["IS"] = P["e"] <= IS_END
for tag in LEDGERS:
    sub = P[P.tag == tag]
    print(f"  ({tag}) vị thế: " + ", ".join(f"{b}={int((sub.book==b).sum())}" for b in ("BAL", "LAG")) +
          f" | quý(cụm) BAL={sub[sub.book=='BAL'].q.nunique()} LAG={sub[sub.book=='LAG'].q.nunique()} | "
          f"Open cache vs giá vốn ledger: |dev| median {sub.open_dev.abs().median()*1e4:.2f} bps, "
          f">1bps {(sub.open_dev.abs()>1e-4).mean()*100:.1f}% (multi-day fill ⇒ giá TB khác Open e)")
    d0 = sum((delta_series(p, "half") * 0).abs().sum() for p in POS[tag][:50])
    print(f"  ({tag}) overlay rỗng (Δ×0) = {d0:.1f} VND")

# ---------------------------------------------------------------- ngưỡng Q2 (IS, riêng mỗi book, trên ledger pin0)
cut = {}
for bk in ("BAL", "LAG"):
    s = P[(P.tag == "pin0") & (P.book == bk) & P.IS]
    cut[bk] = dict(VOL60=np.nanpercentile(s.VOL60, 80), RUN20=np.nanpercentile(s.RUN20, 80), DIST52=np.nanpercentile(s.DIST52, 20))
print("\n[ngưỡng IS] " + "; ".join(f"{bk}: VOL60≥{c['VOL60']:.3f} RUN20≥{c['RUN20']:.3f} DIST52≤{c['DIST52']:.3f}" for bk, c in cut.items()))
for bk in ("BAL", "LAG"):
    m = P.book == bk
    P.loc[m, "G_VOL"] = P.loc[m, "VOL60"] >= cut[bk]["VOL60"]
    P.loc[m, "G_RUN"] = P.loc[m, "RUN20"] >= cut[bk]["RUN20"]
    P.loc[m, "G_DEEP"] = P.loc[m, "DIST52"] <= cut[bk]["DIST52"]
for g in GROUPS: P[g] = P[g].fillna(False).astype(bool)
P["HIT15"] = (P["MAE"] <= -0.15).astype(float)

# ---------------------------------------------------------------- Q1 event-level (per trade) + Q2 event-level
idle_ret = {}
for tag in LEDGERS:
    for p in POS[tag]:
        if tag == "pin1M":
            idx = CAL[(CAL > p["e"]) & (CAL <= p["x"])]
            idle_ret[p["hid"], tag] = float((RATE.reindex(idx) * DAYS.reindex(idx) / 365).sum())
        else:
            idle_ret[p["hid"], tag] = 0.0


def var_ret(row, r):
    st, px_ = row[f"{r}_st"], row[f"{r}_px"]
    px_ = float(px_) if px_ is not None else np.nan
    if st == "CONTROL" or st == "NA":
        return row["ret"]
    if st.startswith("NOFILL"):
        return idle_ret[row["hid"], row["tag"]]
    p = POSD[row["tag"], row["hid"]]
    Sv = p["B"] / (px_ * p["bcf"])
    return Sv * p["px_exit"] * (1 - p["sf"]) / p["B"] - 1


POSD = {(p["tag"], p["hid"]): p for tag in POS for p in POS[tag]}
print("\n[Q1 event-level] per vị thế, Δ = lợi suất biến thể − control (pp); CI cụm theo quý vào lệnh")
q1ev = []
for tag in LEDGERS:
    for bk in ("BAL", "LAG"):
        s = P[(P.tag == tag) & (P.book == bk)].copy()
        top = s["ret"] >= s["ret"].quantile(2 / 3)
        for r in RULES:
            vr_ = s.apply(lambda row: var_ret(row, r), axis=1).values
            dlt = vr_ - s["ret"].values
            est, ci, p_, nc = cluster_boot(dlt, s["q"].values)
            nof = s[f"{r}_st"].str.startswith("NOFILL").values
            fil = (s[f"{r}_st"] == "FILL").values
            pc = np.array([POSD[w_tag, w_hid]["pc"] for w_tag, w_hid in zip(s["tag"], s["hid"])])
            imp = (1 - pd.to_numeric(s[f"{r}_px"], errors="coerce").values / pc)[fil]
            q1ev.append(dict(tag=tag, book=bk, rule=r, n=len(s), clusters=nc, d_ret=est, ci_lo=ci[0], ci_hi=ci[1], p=p_,
                             d_IS=dlt[s.IS.values].mean(), d_OOS=dlt[~s.IS.values].mean(),
                             nofill=nof.mean(), nofill_top=nof[top.values].mean() if top.any() else np.nan,
                             px_impr_bps=np.mean(imp) * 1e4 if len(imp) else np.nan, n_fill_moved=int(fil.sum())))
Q1E = pd.DataFrame(q1ev)
Q1E["holm"] = False
for tag in LEDGERS:
    m = Q1E.tag == tag; Q1E.loc[m, "holm"] = holm(Q1E.loc[m, "p"].values)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
sh = Q1E.copy()
for c in ("d_ret", "ci_lo", "ci_hi", "d_IS", "d_OOS", "nofill", "nofill_top"): sh[c] = (sh[c] * 100).round(3)
sh["px_impr_bps"] = sh["px_impr_bps"].round(1); sh["p"] = sh["p"].round(4)
print(sh.to_string(index=False))

print("\n[Q2 event-level ledger] ΔHIT15 = P(MAE≤−15% | nhóm) − P(còn lại); CI cụm theo quý")
q2ev = []
for tag in LEDGERS:
    for bk in ("BAL", "LAG"):
        s = P[(P.tag == tag) & (P.book == bk)]
        yrs = s["e"].dt.year.values
        for g in GROUPS:
            a = s[g].values
            est, ci, p_, nc = cluster_boot(s["HIT15"].values, s["q"].values, a, "diff")
            mae_d = s.MAE.values[a].mean() - s.MAE.values[~a].mean()
            loyo = [s.HIT15.values[a & (yrs != y)].mean() - s.HIT15.values[~a & (yrs != y)].mean() for y in np.unique(yrs)]
            isv, oo = s.IS.values, ~s.IS.values
            q2ev.append(dict(tag=tag, book=bk, group=g, n_grp=int(a.sum()), n_rest=int((~a).sum()), clusters=nc,
                             hit_grp=s.HIT15.values[a].mean(), hit_rest=s.HIT15.values[~a].mean(), d_hit=est, ci_lo=ci[0], ci_hi=ci[1], p=p_,
                             d_IS=s.HIT15.values[a & isv].mean() - s.HIT15.values[~a & isv].mean(),
                             d_OOS=s.HIT15.values[a & oo].mean() - s.HIT15.values[~a & oo].mean(),
                             loyo_min=np.nanmin(loyo), loyo_max=np.nanmax(loyo), d_mae=mae_d,
                             p5_grp=np.percentile(s.ret.values[a], 5) if a.sum() >= 5 else np.nan, p5_rest=np.percentile(s.ret.values[~a], 5),
                             ret_grp=s.ret.values[a].mean(), ret_rest=s.ret.values[~a].mean()))
Q2E = pd.DataFrame(q2ev)
Q2E["holm"] = False
for tag in LEDGERS:
    m = Q2E.tag == tag; Q2E.loc[m, "holm"] = holm(Q2E.loc[m, "p"].values)
Q2E["c1"] = (Q2E.d_hit > 0) & (Q2E.ci_lo > 0); Q2E["c2"] = (Q2E.d_IS > 0) & (Q2E.d_OOS > 0); Q2E["c3"] = Q2E.loyo_min > 0
sh = Q2E.copy()
for c in ("hit_grp", "hit_rest", "d_hit", "ci_lo", "ci_hi", "d_IS", "d_OOS", "loyo_min", "loyo_max", "d_mae", "p5_grp", "p5_rest", "ret_grp", "ret_rest"):
    sh[c] = (sh[c] * 100).round(2)
sh["p"] = sh["p"].round(4)
print(sh.to_string(index=False))

# ---------------------------------------------------------------- NAV overlay
print("\n[NAV overlay] Δ so với control (cùng ledger); NAV tổng + từng book")
navrows, daily_ret = [], {}
for tag in LEDGERS:
    tx, dl, met = ledg[tag]
    carry = tag == "pin1M"
    base = {"ALL": dl["combined_nav"], "BAL": dl["nav_bal_ref"], "LAG": dl["nav_lag_ref"]}
    mb = {k: metrics(v) for k, v in base.items()}
    loyo_b, yr_b = loyo_cagr(base["ALL"])
    if tag == "pin0":
        daily_ret["CONTROL"] = base["ALL"].pct_change().fillna(0)
    variants = [(f"Q1_{r}", bk, r) for r in RULES for bk in ("BAL", "LAG")] + [(f"Q2_{g}_half", bk, g) for g in GROUPS for bk in ("BAL", "LAG")]
    for name, bk, key in variants:
        D = pd.Series(0.0, index=CAL)
        for p in POS[tag]:
            if p["book"] != bk:
                continue
            if key in RULES:
                st, fd, fpx = p["rules"][key] if p["rules"][key] else ("NA", None, None)
                if st in ("CONTROL", "NA"):
                    continue
                D += delta_series(p, "nofill" if st.startswith("NOFILL") else "fill", (fd, fpx), carry)
            else:
                if P.loc[(P.tag == tag) & (P.hid == p["hid"]), key].iloc[0]:
                    D += delta_series(p, "half", None, carry)
        nav_bk = base[bk] + D
        nav_all = combine(dl, nav_bk if bk == "BAL" else base["BAL"], nav_bk if bk == "LAG" else base["LAG"])
        m_all, m_bk = metrics(nav_all), metrics(nav_bk)
        is_c, is_v = metrics(base["ALL"][:IS_END]), metrics(nav_all[:IS_END])
        oo_c, oo_v = metrics(base["ALL"][IS_END:]), metrics(nav_all[IS_END:])
        loyo_v, yr_v = loyo_cagr(nav_all)
        navrows.append(dict(tag=tag, variant=f"{name}:{bk}", dCAGR=m_all["cagr"] - mb["ALL"]["cagr"], dSharpe=m_all["sharpe"] - mb["ALL"]["sharpe"],
                            dMaxDD=m_all["maxdd"] - mb["ALL"]["maxdd"], dCalmar=m_all["calmar"] - mb["ALL"]["calmar"],
                            CAGR=m_all["cagr"], MaxDD=m_all["maxdd"], Calmar=m_all["calmar"],
                            book_dCAGR=m_bk["cagr"] - mb[bk]["cagr"], book_dMaxDD=m_bk["maxdd"] - mb[bk]["maxdd"], book_dCalmar=m_bk["calmar"] - mb[bk]["calmar"],
                            dCAGR_IS=is_v["cagr"] - is_c["cagr"], dCAGR_OOS=oo_v["cagr"] - oo_c["cagr"],
                            dCalmar_IS=is_v["calmar"] - is_c["calmar"], dCalmar_OOS=oo_v["calmar"] - oo_c["calmar"],
                            loyo_dCAGR_min=min(loyo_v[y] - loyo_b[y] for y in loyo_b), loyo_dCAGR_max=max(loyo_v[y] - loyo_b[y] for y in loyo_b),
                            yrs_neg=int(sum((yr_v[y] - yr_b[y]) < 0 for y in yr_b)), dFinalNAV_B=(nav_all.iloc[-1] - base["ALL"].iloc[-1]) / 1e9))
        if tag == "pin0":
            daily_ret[f"{name}:{bk}"] = nav_all.pct_change().fillna(0)
    print(f"  ({tag}) control: " + " | ".join(f"{k} CAGR {v['cagr']*100:.2f}% Sharpe {v['sharpe']:.2f} MaxDD {v['maxdd']*100:.1f}% Calmar {v['calmar']:.2f}" for k, v in mb.items()))
NAVT = pd.DataFrame(navrows)
sh = NAVT.copy()
for c in sh.columns:
    if c.startswith(("dCAGR", "dMaxDD", "CAGR", "MaxDD", "book_dCAGR", "book_dMaxDD", "loyo")):
        sh[c] = (sh[c] * 100).round(3)
    elif c in ("dSharpe", "dCalmar", "Calmar", "book_dCalmar", "dCalmar_IS", "dCalmar_OOS", "dFinalNAV_B"):
        sh[c] = sh[c].round(3)
print(sh.to_string(index=False))

# ---------------------------------------------------------------- DSR (Δ ngày) + PBO
R = pd.DataFrame(daily_ret)
names = [c for c in R.columns if c != "CONTROL"]
Dd = R[names].sub(R["CONTROL"], axis=0).iloc[1:]
SR = Dd.mean() / Dd.std(ddof=1)
SR = SR.replace([np.inf, -np.inf], np.nan).fillna(0)
best = SR.idxmax(); x = Dd[best].values; Tn = len(x); sr = SR[best]; m = len(names)
emc = 0.5772156649
sr0 = np.sqrt(SR.var(ddof=1)) * ((1 - emc) * norm.ppf(1 - 1 / m) + emc * norm.ppf(1 - 1 / (m * np.e)))
g3, g4 = skew(x), kurtosis(x, fisher=False)
dsr = norm.cdf((sr - sr0) * np.sqrt(Tn - 1) / np.sqrt(max(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2, 1e-12)))
print(f"\n[DSR] Δ ngày (biến thể − control, NAV tổng pin0%), N trials={m}: best={best} SR/ngày={sr:.4f} (năm hoá {sr*np.sqrt(252):.2f}), "
      f"SR0={sr0:.4f}, T={Tn}, skew={g3:.2f}, kurt={g4:.1f} → DSR={dsr:.3f}")
cols = ["CONTROL"] + names
blocks = np.array_split(np.arange(1, len(R)), 16)
lam = []
for comb in itertools.combinations(range(16), 8):
    isx = np.concatenate([blocks[i] for i in comb]); oox = np.concatenate([blocks[i] for i in range(16) if i not in comb])
    si = R.iloc[isx][cols]; so = R.iloc[oox][cols]
    s_is = (si.mean() / si.std(ddof=1)).values; s_oo = (so.mean() / so.std(ddof=1)).values
    bi = s_is.argmax(); w = (s_oo < s_oo[bi]).sum() / (len(cols) - 1)
    w = min(max(w, 1e-6), 1 - 1e-6); lam.append(np.log(w / (1 - w)))
pbo = float((np.array(lam) <= 0).mean())
print(f"[PBO] CSCV S=16 ({len(lam)} tổ hợp), {len(cols)} cấu hình (12 biến thể + control), metric Sharpe → PBO={pbo:.3f}")

P.drop(columns=[]).to_csv(f"{OUT}/positions_features.csv", index=False)
Q1E.to_csv(f"{OUT}/q1_event_ledger.csv", index=False); Q2E.to_csv(f"{OUT}/q2_event_ledger.csv", index=False)
NAVT.to_csv(f"{OUT}/nav_overlay.csv", index=False)
print("\n[ghi] positions_features.csv, q1_event_ledger.csv, q2_event_ledger.csv, nav_overlay.csv")

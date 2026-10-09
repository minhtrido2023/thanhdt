#!/usr/bin/env python3
"""Nhánh 4 — chấm lại nhóm B trên engine đã sửa, theo PREREG.md (md5 4d73b7e8). Job Taylor_20261008_172556.
Chỉ đọc ledger CSV do run_leg.sh sinh + file trọng số w/<tag>.csv. PAPER-ONLY.
Chạy: $DNA_PYEXE analyze.py  (cwd bất kỳ)"""
import bisect, hashlib, io, json, os, sys
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC); sys.path.insert(0, os.path.join(WC, "mike/bin"))
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr, cscv_pbo  # noqa
from pin_ledger import parse_ledger_metrics, selfcheck_ok  # noqa

CONV = ["off", "1m"]                       # off = pin0% (SÀN) · 1m = pin1M dep1m (TRẦN)
TREAT = ["q8", "q12", "qf8", "secA", "secB", "secBx", "eyonly", "fc30", "fc45", "fc55", "l1a", "l1b"]
N_TRIALS = 12
VERDICT_ANCHOR = {t: "c70" for t in TREAT}                    # neo chấm verdict (PREREG §4)
VERDICT_ANCHOR.update(fc30="eyonly", fc45="eyonly", fc55="eyonly")
AXIS_ANCHOR = dict(q8="c70", q12="q8", qf8="c70", secA="c70", secB="secA", secBx="secB", eyonly="c70",
                   fc30="eyonly", fc45="fc30", fc55="fc45", l1a="c70", l1b="l1a")
PIN = {"c30_off": "4707bcbeb7e801d49a4a851ffd91d5e7", "c30_1m": "bcd0469f42c2f76937a6ebb10aae9b40"}
PARK0 = {"off": 22.12070836714919, "1m": 25.419622320387103}  # 537e349b / a6ba34d8 (registry 2026-10-08)
# Δ CŨ (registry, theo TÊN MỤC): FULL / IS / OOS vs neo chấm verdict ở trên
OLD = {
    "q8": (-2.89, -6.48, +0.78), "q12": (-2.93, -6.76, +0.99), "qf8": (-3.08, -2.95, -3.21),   # 2026-07-12 Q-SLEEVE
    "secA": (-0.21, -0.07, -0.35), "secB": (-0.16, -0.15, -0.18), "secBx": (-0.04, -0.10, +0.02),  # Sector-cap 07-14
    "eyonly": (-0.05, -0.37, +0.27), "fc30": (-0.64, -0.55, -0.73),                            # v4final 07-14
    "fc45": (-0.84, -0.37, -1.31), "fc55": (-0.32, -0.16, -0.48),                              # v4final A4 07-14
    "l1a": (+1.07, +0.20, +1.90), "l1b": (+2.62, +1.44, +3.75),                                # 2026-09-09 (d)
}
OLD_VERDICT = {k: "NO-GO" for k in OLD}; OLD_VERDICT.update(l1a="chưa chứng minh", l1b="chưa chứng minh")
NOISE = 0.385; BLOCK = 63; BOOT = 4000; SEED = 12345


def leg_path(tag):
    txt = io.open(os.path.join(HERE, "logs", f"{tag}.log"), encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: chân không EXIT=0 — từ chối đọc số"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, f"{tag}: {hits}"
    return hits[0]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()


def sub(s, a, b): return s[(s.index >= a) & (s.index <= b)]


def met(s):
    r = daily_logret(s); yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1; dd = (s / s.cummax() - 1).min()
    return dict(cagr=cagr * 100, sharpe=r.mean() / r.std(ddof=1) * np.sqrt(len(r) / yrs), maxdd=dd * 100,
                calmar=cagr / abs(dd), nav_B=s.iloc[-1] / 1e9)


def full_row(s):
    m = met(s)
    m["is"] = met(sub(s, "2014-01-01", "2019-12-31"))["cagr"]
    m["oos"] = met(sub(s, "2020-01-01", "2026-06-19"))["cagr"]
    return m


def yearly(s):
    e = s.groupby(s.index.year).last(); first = s.iloc[0]
    return (e / e.shift(1).fillna(first) - 1) * 100


def loo(s):
    """CAGR (log-annualised theo thời gian lịch) khi bỏ từng năm dương lịch."""
    r = np.log(s).diff().dropna(); yrs_tot = (s.index[-1] - s.index[0]).days / 365.25
    out = {}
    for y in sorted(set(r.index.year)):
        ry = r[r.index.year == y]
        span = (min(s.index[-1], pd.Timestamp(f"{y}-12-31")) - max(s.index[0], pd.Timestamp(f"{y-1}-12-31"))).days / 365.25
        out[y] = (np.exp((r.sum() - ry.sum()) / (yrs_tot - span)) - 1) * 100
    return pd.Series(out)


def cbb(d, yrs):
    rng = np.random.default_rng(SEED); n = len(d); nb = int(np.ceil(n / BLOCK)); out = np.empty(BOOT)
    for b in range(BOOT):
        st = rng.integers(0, n, nb)
        idx = np.concatenate([(np.arange(x, x + BLOCK) % n) for x in st])[:n]
        out[b] = d[idx].sum()
    return out / yrs * 100


# ---- route PIT (quy ước đo y hệt vòng 4/5: value_panel_2014.csv, as-of quý) ----
vp = pd.read_csv(f"{WC}/data/value_panel_2014.csv", parse_dates=["time"], usecols=["ticker", "time", "route"])
vp["q"] = vp["time"].dt.to_period("Q").dt.start_time
_rt = vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker", "q"])["route"].last()
_rh = {tk: (list(g.index.get_level_values(1)), list(g.values)) for tk, g in _rt.groupby(level=0)}


def route_asof(tk, q):
    e = _rh.get(tk)
    if not e: return "UNKNOWN"
    i = bisect.bisect_right(e[0], pd.Timestamp(q)) - 1
    return e[1][i] if i >= 0 else e[1][0]


def bank_share(tag, ledger):
    w = pd.read_csv(os.path.join(HERE, "w", f"{tag}.csv"), parse_dates=["time"])
    w["q"] = w["time"].dt.to_period("Q").dt.start_time
    key = w[["ticker", "q"]].drop_duplicates()
    key["bank"] = [route_asof(t, q) == "BANK" for t, q in zip(key.ticker, key.q)]
    w = w.merge(key, on=["ticker", "q"])
    daily = w.assign(bw=w.w * w.bank).groupby("time").agg(bw=("bw", "sum"), tw=("w", "sum"))
    bw = daily.bw / daily.tw
    L = pd.read_csv(ledger, low_memory=False, usecols=["record_type", "ymd", "ticker"])
    M = L[L.record_type == "CUSTOM_MEMBERS"].copy(); M["ymd"] = pd.to_datetime(M["ymd"])
    nm = [np.mean([route_asof(t, pd.Timestamp(d).to_period("Q").start_time) == "BANK" for t in g.ticker])
          for d, g in M.groupby("ymd")]
    return dict(bank_w=bw.mean() * 100, bank_w_oos=bw[bw.index >= "2020-01-01"].mean() * 100,
                bank_names=np.mean(nm) * 100)


if __name__ == "__main__":
    out = {"job": "Taylor_20261008_172556", "prereg_md5": md5(os.path.join(HERE, "PREREG.md"))}
    # ---- 0. control vs pin ----
    for t, m in PIN.items():
        got = md5(leg_path(f"n4_{t}"))
        out[f"control_{t}"] = dict(md5=got, pin=m, byte_identical=(got == m))
        print(f"CONTROL {t}: {got} vs pin {m} -> {'BYTE-IDENTICAL' if got == m else '*** LỆCH — DỪNG ***'}")
        if got != m:
            json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1); sys.exit(3)
    legs = ["c70"] + TREAT
    # ---- họ trial GHIM (DSR_FAMILY_MANIFEST): 13 cấu hình × 2 quy ước, md5 từng ledger ----
    from dsr_family_manifest import load_manifest
    MAN = os.path.join(HERE, "dsr_family_manifest_n4.json")
    if not os.path.exists(MAN):
        ent = [dict(path=leg_path(f"n4_{t}_{cv}"), md5=md5(leg_path(f"n4_{t}_{cv}")), leg=f"{t}_{cv}")
               for cv in CONV for t in legs]
        json.dump(dict(_doc="Họ trial nhánh 4 (PREREG N=12 + control), ghim TRƯỚC khi tính DSR/PBO.",
                       manifest_version=1, criterion=dict(reason="job Taylor_20261008_172556 PREREG §2"),
                       n_entries=len(ent), entries=ent), open(MAN, "w"), indent=1, ensure_ascii=False)
    fam, _ = load_manifest(MAN)                         # fail-closed nếu md5 lệch
    assert len(fam) == 2 * len(legs), len(fam)
    out["dsr_family_manifest"] = dict(path=MAN, md5=md5(MAN), n=len(fam))
    res = {}
    for cv in CONV:
        nav, rows, paths = {}, {}, {}
        for t in ["c30"] + legs:
            tag = f"n4_{t}_{cv}"; p = leg_path(tag); paths[t] = p
            pm = parse_ledger_metrics(p)
            nav[t] = load_nav(p)
            r = full_row(nav[t]); r["selfcheck_0vnd"] = selfcheck_ok(pm["metrics"]); r["md5"] = md5(p)
            r["ledger"] = os.path.basename(p)
            if t != "c30": r.update(bank_share(tag, p))
            rows[t] = r
        yrs = (nav["c70"].index[-1] - nav["c70"].index[0]).days / 365.25
        idx = nav["c70"].index
        for t in legs: assert nav[t].index.equals(idx), f"{t}: lịch ngày khác control"
        lr = {t: pd.Series(daily_logret(nav[t]), index=idx[1:]) for t in legs}
        # DSR: chuỗi excess vs control c70, N=12; SR0 từ phương sai SR excess của 12 trial
        ex = {t: (lr[t] - lr["c70"]).dropna() for t in TREAT}
        srs = [ex[t].mean() / ex[t].std(ddof=1) for t in TREAT]
        sr0 = expected_max_sr(np.var(srs, ddof=1), N_TRIALS)
        rc = lr["c70"]; sr_c = rc.mean() / rc.std(ddof=1)
        for t in TREAT:
            a = VERDICT_ANCHOR[t]; R = rows[t]; A = rows[a]
            for k in ["cagr", "is", "oos", "sharpe", "maxdd", "calmar"]: R["d_" + k] = R[k] - A[k]
            R["anchor"] = a; R["d_bank_w"] = R["bank_w"] - A["bank_w"]
            R["d_bank_names"] = R["bank_names"] - A["bank_names"]
            ax = AXIS_ANCHOR[t]; R["axis_anchor"] = ax; R["axis_d_cagr"] = R["cagr"] - rows[ax]["cagr"]
            d = (lr[t] - lr[a]).dropna().values; bs = cbb(d, yrs)
            R["boot_pt"] = d.sum() / yrs * 100
            R["boot_lo"], R["boot_hi"] = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
            R["boot_p_pos"] = float((bs > 0).mean())
            sh, g3, g4 = moments(ex[t].values if a == "c70" else (lr[t] - lr[a]).dropna().values)
            R["dsr_excess"] = float(dsr(sh, sr0, g3, g4, len(d))[0])
            sh2, g32, g42 = moments(lr[t].values)
            R["dsr_raw_vs_srctrl"] = float(dsr(sh2, sr_c, g32, g42, len(lr[t]))[0])
            dy = yearly(nav[t]) - yearly(nav[a]); R["peryear"] = {int(k): round(v, 2) for k, v in dy.items()}
            dl = loo(nav[t]) - loo(nav[a]); R["loo"] = {int(k): round(v, 2) for k, v in dl.items()}
            R["loo_min"], R["loo_max"], R["loo_neg"] = dl.min(), dl.max(), int((dl < 0).sum())
            R["vs_park0"] = R["cagr"] - PARK0[cv]
        M = np.column_stack([lr[t].values for t in legs])
        pbo = float(cscv_pbo(M, S=16)[0])
        res[cv] = dict(rows=rows, sr0_excess=sr0, pbo=pbo, ctrl_park0_ref=PARK0[cv])
        print(f"\n===== conv={cv}  PBO(13 cfg, S=16)={pbo:.4f}  SR0_excess(N=12)={sr0:.5f} =====")
        c = rows["c70"]
        print(f"c30 CAGR {rows['c30']['cagr']:.2f} | c70 CAGR {c['cagr']:.2f} Sh {c['sharpe']:.2f} DD {c['maxdd']:.1f} "
              f"Cal {c['calmar']:.2f} IS {c['is']:.2f} OOS {c['oos']:.2f} bank_w {c['bank_w']:.1f}% "
              f"(OOS {c['bank_w_oos']:.1f}%) names {c['bank_names']:.1f}% sc0={c['selfcheck_0vnd']}")
        for t in TREAT:
            R = rows[t]
            print(f"{t:7s} CAGR {R['cagr']:6.2f} Sh {R['sharpe']:.2f} DD {R['maxdd']:6.1f} Cal {R['calmar']:.2f} "
                  f"| vs {R['anchor']:6s} Δ {R['d_cagr']:+.2f} IS {R['d_is']:+.2f} OOS {R['d_oos']:+.2f} "
                  f"DD {R['d_maxdd']:+.1f} | CI [{R['boot_lo']:+.2f},{R['boot_hi']:+.2f}] "
                  f"DSRx {R['dsr_excess']:.3f} DSRr {R['dsr_raw_vs_srctrl']:.3f} "
                  f"LOO[{R['loo_min']:+.2f},{R['loo_max']:+.2f}] neg {R['loo_neg']} "
                  f"| bank_w {R['bank_w']:.1f} (Δ{R['d_bank_w']:+.1f}) | park0 {R['vs_park0']:+.2f} sc0={R['selfcheck_0vnd']}")
    # ---- verdict theo PREREG §4 ----
    ver = {}
    for t in TREAT:
        o, m = res["off"]["rows"][t], res["1m"]["rows"][t]
        d = o["d_cagr"]; same = np.sign(d) == np.sign(m["d_cagr"])
        full = (d > NOISE and o["d_is"] > 0 and o["d_oos"] > 0 and o["calmar"] >= res["off"]["rows"][o["anchor"]]["calmar"]
                and (o["boot_lo"] > 0) and o["dsr_excess"] >= 0.95)
        if not same and abs(d) > NOISE: v = "HẾT Ý NGHĨA (2 quy ước trái dấu)"
        elif d <= -NOISE: v = "ĐỨNG (NO-GO)"
        elif abs(d) <= NOISE: v = "HẾT Ý NGHĨA"
        elif full: v = "ĐẢO → ứng viên GO"
        else: v = "ĐẢO DẤU, chưa chứng minh" if OLD[t][0] <= 0 else "ĐỨNG (dương, chưa chứng minh)"
        ver[t] = dict(old_d=OLD[t], old_verdict=OLD_VERDICT[t], new_d_off=d, new_d_1m=m["d_cagr"],
                      shift_off=d - OLD[t][0], d_bank_w=o["d_bank_w"], verdict=v)
    out.update(results=res, verdict=ver)
    sh = np.array([ver[t]["shift_off"] for t in TREAT]); db = np.array([ver[t]["d_bank_w"] for t in TREAT])
    out["h1_corr_shift_vs_dbank"] = float(np.corrcoef(sh, db)[0, 1])
    q_stand = all(ver[t]["verdict"].startswith("ĐỨNG (NO") for t in ["q8", "q12", "qf8"])
    out["h2_breadth_claim_stands"] = bool(q_stand)
    print("\n===== VERDICT =====")
    for t in TREAT:
        v = ver[t]
        print(f"{t:7s} cũ {v['old_d'][0]:+.2f} ({v['old_verdict']}) → mới pin0% {v['new_d_off']:+.2f} / pin1M "
              f"{v['new_d_1m']:+.2f} | dịch {v['shift_off']:+.2f} | Δbank_w {v['d_bank_w']:+.1f} | {v['verdict']}")
    print(f"H1 corr(dịch Δ, Δbank_w) = {out['h1_corr_shift_vs_dbank']:+.3f}  | H2 breadth-claim đứng: {q_stand}")

    def _j(x):
        if isinstance(x, dict): return {str(k): _j(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [_j(v) for v in x]
        if isinstance(x, (np.floating, np.integer)): return x.item()
        if isinstance(x, np.bool_): return bool(x)
        return x
    json.dump(_j(out), open(os.path.join(HERE, "results.json"), "w"), indent=1, ensure_ascii=False)

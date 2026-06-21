"""
Biodiversity Test (AMH proposal #5)
===================================
AMH: a portfolio of strategies is robust the way an ecosystem is — through
DIVERSITY. A new strategy earns its place only if it is ORTHOGONAL to the
existing book: it must survive / profit in the environments where the incumbents
DIE. (F-system FAILED this — redundant with DT5G, "cùng cò súng"; ORB intraday
PASSED — orthogonal to the daily book.)

This is a reusable screen. Given an ecosystem of strategy return streams and a
candidate, it scores three things and returns PASS/FAIL:
  1. ORTHOGONALITY   — corr(candidate, incumbent) and corr(candidate, blend)
  2. SURVIVAL        — does the candidate make money in the incumbent's worst
                       months? (% of incumbent-down months where candidate > 0;
                       mean candidate return in incumbent's worst quartile)
  3. MARGINAL UPLIFT — Sharpe/Calmar of incumbent vs incumbent + w*candidate
                       (does adding it actually improve risk-adjusted return?)

Demo ecosystem: monthly long/short quintile style streams (1-month holding, non-
overlapping) built from data/edge_panel.csv — VALUE / MOMENTUM / QUALITY — plus a
DT5G market-timing stream. Incumbent = MOMENTUM (the V4/V5 core). Candidates: the
other styles + flow/position/mean-reversion.

Run: python biodiversity_test.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PANEL = WORKDIR + r"\data\edge_panel.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
FWD = "fwd_1m"          # 1-month holding -> non-overlapping monthly stream
QTILE = 0.20
MIN_NAMES = 25
STATE_W = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}

# style -> (column, drop-exact-zero[bank placeholder])
STYLES = {
    "VALUE_PB":   ("PB", False),
    "VALUE_PE":   ("PE", False),
    "MOMENTUM":   ("mom_200", False),
    "RSI":        ("D_RSI", False),
    "QUALITY_ROE":("ROE_Min5Y", True),
    "QUALITY_ROIC":("ROIC5Y", True),
    "FSCORE":     ("FSCORE", False),
    "FLOW_CMF":   ("D_CMF", False),
    "POSITION":   ("C_L1M", False),
    "PBZ":        ("pb_z", False),
}


def ls_stream(df, col, drop_zero):
    """Monthly long/short top-vs-bottom quintile return (1m holding), oriented +profit."""
    out = {}
    for ym, g in df.groupby("ym"):
        s = g[[col, FWD]].dropna()
        if drop_zero:
            s = s[s[col] != 0.0]
        if len(s) < MIN_NAMES or s[col].nunique() < 5:
            continue
        k = max(3, int(len(s) * QTILE))
        ss = s.sort_values(col)
        out[ym] = ss[FWD].iloc[-k:].mean() - ss[FWD].iloc[:k].mean()
    st = pd.Series(out).sort_index()
    # orient so positive = profitable (long the favorable end)
    if st.mean() < 0:
        st = -st
    return st


def ann(stream):
    mu = stream.mean() * 12
    sd = stream.std(ddof=1) * np.sqrt(12)
    sharpe = mu / sd if sd > 0 else 0
    nav = (1 + stream).cumprod()
    dd = (nav / nav.cummax() - 1).min()
    calmar = mu / abs(dd) if dd < 0 else np.nan
    return dict(CAGR=mu, Vol=sd, Sharpe=sharpe, MaxDD=dd, Calmar=calmar)


def biodiversity(ecosystem, cand_name, cand, incumbent_name):
    """Score a candidate's biodiversity contribution. Returns a verdict dict."""
    inc = ecosystem[incumbent_name]
    blend = pd.DataFrame(ecosystem).mean(axis=1)   # equal-weight existing book
    idx = cand.index.intersection(inc.index)
    c, i, b = cand.loc[idx], inc.loc[idx], blend.loc[idx]
    corr_inc = c.corr(i)
    corr_blend = c.corr(b)
    # survival in incumbent's pain
    down = i < 0
    surv_rate = (c[down] > 0).mean() if down.sum() else np.nan
    worstq = i <= i.quantile(0.25)
    cand_in_worst = c[worstq].mean()
    inc_in_worst = i[worstq].mean()
    # marginal uplift: incumbent vs incumbent + 0.3*candidate (both rescaled later by user)
    w = 0.3
    combo = i + w * c
    s_inc = ann(i)["Sharpe"]; s_combo = ann(combo)["Sharpe"]
    cal_inc = ann(i)["Calmar"]; cal_combo = ann(combo)["Calmar"]
    sa = ann(c)   # standalone
    ortho = abs(corr_inc) < 0.30
    survives = (surv_rate is not np.nan) and surv_rate >= 0.50 and cand_in_worst > 0
    helps = (s_combo > s_inc) and sa["Sharpe"] > 0
    npass = sum([ortho, survives, helps])
    verdict = "PASS" if npass == 3 else ("PARTIAL" if npass == 2 else "FAIL")
    return dict(candidate=cand_name, corr_inc=round(corr_inc, 2), corr_blend=round(corr_blend, 2),
                surv_rate=round(surv_rate, 2), cand_in_incWorstQ=round(cand_in_worst*100, 2),
                sa_Sharpe=round(sa["Sharpe"], 2), dSharpe=round(s_combo - s_inc, 3),
                dCalmar=round(cal_combo - cal_inc, 2),
                orthogonal=ortho, survives=survives, helps=helps, verdict=verdict)


def main():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df = df[df[FWD].notna()].copy()
    lo, hi = df[FWD].quantile([0.005, 0.995]); df[FWD] = df[FWD].clip(lo, hi)
    df["ym"] = df["time"].dt.to_period("M")

    streams = {name: ls_stream(df, col, dz) for name, (col, dz) in STYLES.items()}

    # DT5G market-timing monthly stream: w_state(t) * index_ret(t->t+1)
    st = pd.read_csv(STATEF, parse_dates=["time"]).sort_values("time")
    st["ym"] = st["time"].dt.to_period("M")
    m = st.groupby("ym").agg(state=("state", lambda s: int(s.mode().iloc[0])),
                             px=("vnindex", "last"))
    m["w"] = m["state"].map(STATE_W)
    m["idx_ret"] = m["px"].pct_change().shift(-1)      # this month-end -> next month-end
    streams["DT5G_TIMING"] = (m["w"] * m["idx_ret"]).dropna()

    # align all to common monthly index
    S = pd.DataFrame(streams).dropna(how="all")
    print(f"Monthly style streams: {S.shape[1]} strategies x {len(S)} months "
          f"({S.index.min()} -> {S.index.max()})\n")

    print("=== STANDALONE (annualized, monthly LS) ===")
    perf = pd.DataFrame({n: ann(streams[n].dropna()) for n in streams}).T
    perf["CAGR"] = (perf["CAGR"]*100).round(1); perf["Vol"] = (perf["Vol"]*100).round(1)
    perf["MaxDD"] = (perf["MaxDD"]*100).round(1)
    print(perf[["CAGR", "Vol", "Sharpe", "MaxDD", "Calmar"]].round(2).to_string())

    print("\n=== BIODIVERSITY CORRELATION MATRIX (monthly returns) ===")
    print(S.corr().round(2).to_string())

    # incumbent book = MOMENTUM (V4/V5 core). Ecosystem = {MOMENTUM} for incumbent corr;
    # blend = the broader existing book it sits in.
    incumbent = "MOMENTUM"
    eco = {k: streams[k].dropna() for k in ["MOMENTUM", "VALUE_PB", "QUALITY_ROE"]}
    candidates = ["VALUE_PB", "VALUE_PE", "QUALITY_ROE", "QUALITY_ROIC", "FSCORE",
                  "RSI", "FLOW_CMF", "POSITION", "PBZ", "DT5G_TIMING"]
    rows = [biodiversity({**eco, c: streams[c].dropna()}, c, streams[c].dropna(), incumbent)
            for c in candidates if c != incumbent]
    bd = pd.DataFrame(rows)
    print(f"\n=== BIODIVERSITY VERDICT — candidates vs incumbent book = {incumbent} (V4/V5 core) ===")
    print("  PASS = orthogonal(|corr|<.3) AND survives incumbent's down-months AND improves Sharpe")
    print(bd[["candidate", "corr_inc", "surv_rate", "cand_in_incWorstQ", "sa_Sharpe",
              "dSharpe", "dCalmar", "verdict"]].to_string(index=False))

    bd.to_csv(WORKDIR + r"\data\biodiversity_verdict.csv", index=False)
    S.to_csv(WORKDIR + r"\data\biodiversity_streams.csv")
    print("\nSaved: data/biodiversity_verdict.csv | data/biodiversity_streams.csv")


if __name__ == "__main__":
    main()

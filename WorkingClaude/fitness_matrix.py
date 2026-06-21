"""
Fitness Matrix (AMH proposal #3)  —  signal/strategy x DT5G-state
=================================================================
AMH: a strategy's profitability is environment-dependent. This builds the living
matrix [signal x 5 market states], where each cell = the edge (forward-3M IC,
long/short quintile spread, hit-rate) of that signal CONDITIONED on the DT5G
market state at position-formation time. It turns the scattered regime-dependent
findings (memory: "FA edge ZERO in BULL", "CRISIS = only regime quality beats
junk", value/momentum sector splits) into ONE grid that drives regime-conditional
allocation: given today's state, which strategies are FIT?

Edge metrics (cross-sectional, not NAV-path -> Sharpe/Sortino/Calmar not used here;
those are for system-level NAV decisions):
  mean_IC   : mean monthly Spearman IC (signed) in that state
  t_stat    : significance across the state's months
  ls_spread : long/short top-vs-bottom-quintile fwd-3M return, oriented by full-
              history sign so positive = the strategy MADE money in that state
  hit       : % months IC matches the signal's full-history sign

Inputs : data/edge_panel.csv (signals+fwd_3m+sector), data/dt5g_vnindex.csv (state)
Outputs: data/fitness_matrix_ic.csv, data/fitness_matrix_spread.csv,
         fitness_matrix.png, console + current-state fit readout
Run: python fitness_matrix.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PANEL = WORKDIR + r"\data\edge_panel.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
FWD = "fwd_3m"
QTILE = 0.20            # top/bottom quintile for long-short spread
MIN_NAMES = 25
MIN_MONTHS = 6         # min months in a state to report a cell
STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

SIGNALS = {
    "pb_z":      (-1, "Val: PB_z"),
    "PB":        (-1, "Val: PB"),
    "PE":        (-1, "Val: PE"),
    "ROIC5Y":    (+1, "Qual: ROIC5Y"),
    "FSCORE":    (+1, "Qual: FSCORE"),
    "ROE_Min5Y": (+1, "Qual: ROE_Min5Y"),
    "mom_200":   ( 0, "Mom: Close/MA200"),
    "D_RSI":     ( 0, "Mom: D_RSI"),
    "D_CMF":     (+1, "Flow: CMF"),
    "C_L1M":     ( 0, "Pos: Close/Low1M"),
}
QUAL = {"ROIC5Y", "FSCORE", "ROE_Min5Y"}


def spearman(a, b):
    return pd.Series(a).rank().corr(pd.Series(b).rank())


def load():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df = df[df[FWD].notna()].copy()
    lo, hi = df[FWD].quantile([0.005, 0.995])
    df[FWD] = df[FWD].clip(lo, hi)
    df["ym"] = df["time"].dt.to_period("M")
    # modal DT5G state per calendar month (regime at formation)
    st = pd.read_csv(STATEF, parse_dates=["time"])
    st["ym"] = st["time"].dt.to_period("M")
    modal = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))
    df["state"] = df["ym"].map(modal)
    return df.dropna(subset=["state"])


def month_ic_spread(g, col, drop_zero, full_sign):
    s = g[[col, FWD]].dropna()
    if drop_zero:
        s = s[s[col] != 0.0]
    if len(s) < MIN_NAMES or s[col].nunique() < 5:
        return None
    ic = spearman(s[col].values, s[FWD].values)
    # long/short quintile spread (raw, top-by-signal minus bottom)
    n = len(s); k = max(3, int(n * QTILE))
    ss = s.sort_values(col)
    bot = ss[FWD].iloc[:k].mean(); top = ss[FWD].iloc[-k:].mean()
    raw_spread = top - bot
    strat = full_sign * raw_spread if full_sign != 0 else raw_spread
    return ic, strat


def main():
    df = load()
    states = sorted(df["state"].unique())
    print(f"Panel: {len(df):,} obs | {df['ym'].nunique()} months | "
          f"states present: {[STATE_LBL[s] for s in states]}")
    mcount = df.groupby("state")["ym"].nunique()
    print("Months per state:", {STATE_LBL[s]: int(mcount[s]) for s in states})

    ic_mat, sp_mat, t_mat, n_mat = {}, {}, {}, {}
    for col, (prior, label) in SIGNALS.items():
        dz = col in QUAL
        # full-history IC sign (for orienting the long/short spread)
        full_months = []
        for ym, g in df.groupby("ym"):
            r = month_ic_spread(g, col, dz, 0)
            if r is not None:
                full_months.append(r[0])
        full_sign = np.sign(np.nanmean(full_months)) if full_months else 1
        ic_mat[col], sp_mat[col], t_mat[col], n_mat[col] = {}, {}, {}, {}
        for s in states:
            sub = df[df["state"] == s]
            ics, sps = [], []
            for ym, g in sub.groupby("ym"):
                r = month_ic_spread(g, col, dz, full_sign)
                if r is not None:
                    ics.append(r[0]); sps.append(r[1])
            if len(ics) >= MIN_MONTHS:
                ics = np.array(ics)
                ic_mat[col][s] = ics.mean()
                sp_mat[col][s] = np.mean(sps)
                t_mat[col][s] = ics.mean() / (ics.std(ddof=1) / np.sqrt(len(ics))) if ics.std() > 0 else 0
                n_mat[col][s] = len(ics)

    IC = pd.DataFrame(ic_mat).T
    SP = pd.DataFrame(sp_mat).T
    TT = pd.DataFrame(t_mat).T
    NN = pd.DataFrame(n_mat).T
    cols = [s for s in states if s in IC.columns]
    IC, SP, TT, NN = IC[cols], SP[cols], TT[cols], NN[cols]
    lblmap = {c: SIGNALS[c][1] for c in IC.index}
    IC.index = [lblmap[c] for c in IC.index]
    SP.index = IC.index; TT.index = IC.index; NN.index = IC.index
    colnames = [STATE_LBL[s] for s in cols]
    for M in (IC, SP, TT, NN):
        M.columns = colnames

    IC.to_csv(WORKDIR + r"\data\fitness_matrix_ic.csv")
    (SP * 100).round(2).to_csv(WORKDIR + r"\data\fitness_matrix_spread.csv")

    pd.set_option("display.width", 200)
    print("\n=== FITNESS MATRIX — mean fwd-3M IC by (signal x state) ===")
    print("    (signed IC; thin states EXBULL n<6 dropped; * = |t|>=2)")
    def cellstr(r, c):
        v = IC.loc[r, c]
        if pd.notna(v):
            star = "*" if abs(TT.loc[r, c]) >= 2 else " "
            return f"{v:+.3f}{star}"
        return "  -  "
    show = pd.DataFrame({c: {r: cellstr(r, c) for r in IC.index} for c in IC.columns})
    print(show.to_string())

    print("\n=== STRATEGY RETURN — long/short quintile fwd-3M spread (%, oriented + = profitable) ===")
    print((SP * 100).round(1).to_string())

    # current state fit
    cur = int(df.sort_values("time")["state"].iloc[-1])
    print(f"\n=== CURRENT-STATE FIT — DT5G = {STATE_LBL[cur]} ===")
    if STATE_LBL[cur] in IC.columns:
        fit = pd.DataFrame({"IC": IC[STATE_LBL[cur]], "tstat": TT[STATE_LBL[cur]],
                            "LS_spread_%": (SP[STATE_LBL[cur]] * 100)}).dropna()
        fit = fit.sort_values("IC", key=lambda s: s.abs(), ascending=False)
        print(fit.round(3).to_string())

    # ---- heatmap ----
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(15, 7))
    for ax, M, title, scale in [(axa, IC, "mean fwd-3M IC", 0.10),
                                (axb, SP * 100, "L/S spread % (oriented)", None)]:
        data = M.values.astype(float)
        vmax = scale if scale else np.nanmax(np.abs(data))
        im = ax.imshow(data, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(M.columns))); ax.set_xticklabels(M.columns, fontsize=9)
        ax.set_yticks(range(len(M.index))); ax.set_yticklabels(M.index, fontsize=8)
        for i in range(len(M.index)):
            for j in range(len(M.columns)):
                v = data[i, j]
                if np.isfinite(v):
                    ax.text(j, i, f"{v:.2f}" if scale else f"{v:.1f}", ha="center",
                            va="center", fontsize=7)
        ax.set_title(title, fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("Fitness Matrix — strategy edge conditioned on DT5G market state (AMH #3)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(WORKDIR + r"\fitness_matrix.png", dpi=110)
    print("\nSaved: fitness_matrix.png | data/fitness_matrix_{ic,spread}.csv")


if __name__ == "__main__":
    main()

"""V2 §1-2 PREREG_V2: dựng U230 -> tập A/N theo quy tắc cố định; ghi data/v2_sets.json."""
import sys, json, os, glob
import pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_replay_20261020")
import svr_replay as R
from svr_lib import load_px
KP = "/home/trido/thanhdt/WorkingClaude/mike/kb/projects"
w = pd.read_csv(f"{KP}/delisted-tickers-survivorship-20261020.csv")
nd = w[w.in_data == False]
have = {os.path.basename(f)[:-4] for f in glob.glob(f"{KP}/delisted-tickers-survivorship-20261020.d/prices_all/*.csv")}
U = sorted(set(nd.ticker) & have); miss = sorted(set(nd.ticker) - have)
sa = pd.read_csv(f"{R.WIN}/stats_all.csv").set_index("ticker").exch2.to_dict()
rows, err = [], {}
for tk in U:
    try:
        px = load_px(tk)
        o = sa.get(tk)
        if o not in ("HOSE", "HNX", "UPCOM"):
            o = px.floor[px.floor != "UPCOM"].mode().iloc[0] if (px.floor != "UPCOM").any() else px.floor.iloc[0]
        po = px[px.floor == o]
        LT = po.index[po.nmVolume > 0].max()
        n_trd = int((po.nmVolume > 0).sum())
        rows.append(dict(ticker=tk, orig=o, LT=LT, n_trade_days=n_trd, cat=nd.set_index("ticker").cat.get(tk),
                         inA=bool(pd.notna(LT) and LT >= pd.Timestamp("2014-03-03") and n_trd >= 60)))
    except Exception as e:
        err[tk] = f"{type(e).__name__}: {e}"
df = pd.DataFrame(rows); df.to_csv("data/v2_universe.csv", index=False)
A = df[df.inA].ticker.tolist(); N = [t for t in A if t not in R.M and t != "HVG"]
json.dump(dict(U230=len(U), missing_price=miss, build_errors=err, A=A, N=N, M_in_A=[t for t in R.M if t in A],
               M_notin_A=[t for t in R.M if t not in A]), open("data/v2_sets.json", "w"), indent=1, default=str)
print(len(U), "miss", miss, "err", err, "A", len(A), "N", len(N), "M in A", sum(t in A for t in R.M))
print(df[~df.inA].assign(LT=lambda x: x.LT.astype(str)).groupby(df.LT < pd.Timestamp("2014-03-03")).size())
print(df[df.inA].cat.value_counts().to_dict())

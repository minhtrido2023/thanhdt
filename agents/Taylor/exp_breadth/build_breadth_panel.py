"""Candidate #3 — breadth sau hon. Buoc 1: dung panel breadth daily tu ticker_prune.

N TRIALS KHAI BAO TRUOC = 3 metric moi (B1 A/D line, B2 new-high/new-low 3M, B3 %>MA20/MA50).
Khong sweep tham so. Cua so divergence CO DINH = 60 phien (chon truoc, khong toi uu).
Tat ca causal: metric tinh tu du lieu DEN ngay t, forward return tinh TU ngay t.
"""
import duckdb, pandas as pd, numpy as np, os

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WC, "mike/agents/Taylor/exp_breadth")
GLOB = f"{WC}/data/bq_cache/ticker_prune/*.parquet"
MIN_UNIV = 100          # cung nguong voi breadth guard PROD (macro_state_live P['breadth_min_univ'])

con = duckdb.connect(config={"threads": "1"})

# --- breadth daily tu ticker_prune ---------------------------------------
q = f"""
SELECT t.time AS d,
       COUNT(*)                                                     AS univ,
       AVG(IF(t.Close > t.MA20 , 1.0, 0.0))                          AS b_ma20,
       AVG(IF(t.Close > t.MA50 , 1.0, 0.0))                          AS b_ma50,
       AVG(IF(t.Close > t.MA200, 1.0, 0.0))                          AS b_ma200,   -- PROD (guard)
       AVG(IF(t.D_RSI < 0.30   , 1.0, 0.0))                          AS b_rsi_os,  -- PROD (CAPIT)
       SUM(IF(t.Close > t.Close_T1, 1.0, 0.0))                       AS adv,
       SUM(IF(t.Close < t.Close_T1, 1.0, 0.0))                       AS dec,
       AVG(IF(t.Close >= t.HI_3M_T1, 1.0, 0.0))                      AS f_nh3m,
       AVG(IF(t.Close <= t.LO_3M_T1, 1.0, 0.0))                      AS f_nl3m
FROM read_parquet('{GLOB}') AS t
WHERE t.Close IS NOT NULL
GROUP BY 1 ORDER BY 1
"""
b = con.execute(q).df()
b["d"] = pd.to_datetime(b["d"])
b = b[b["univ"] >= MIN_UNIV].reset_index(drop=True)

# --- VNINDEX (mirror column, lay 1 dong/ngay) ----------------------------
v = con.execute(f"""
SELECT t.time AS d, MAX(t.VNINDEX) AS vni
FROM read_parquet('{GLOB}') AS t WHERE t.VNINDEX IS NOT NULL GROUP BY 1 ORDER BY 1
""").df()
v["d"] = pd.to_datetime(v["d"])

df = b.merge(v, on="d", how="inner").sort_values("d").reset_index(drop=True)

# --- 3 metric MOI --------------------------------------------------------
# B1: A/D line = cumsum cua net advance ratio (chuan hoa theo universe de khong bi
#     lech khi so ma tang dan theo nam)
df["ad_net"] = (df["adv"] - df["dec"]) / df["univ"]
df["ad_line"] = df["ad_net"].cumsum()
# B2: new-high/new-low 3M spread
df["nhnl"] = df["f_nh3m"] - df["f_nl3m"]
# B3: ladder ngan/trung han
#     (b_ma20, b_ma50 da co o tren)

# --- forward VNINDEX return (causal: tu ngay t) --------------------------
for h in (5, 20, 60):
    df[f"fwd{h}"] = df["vni"].shift(-h) / df["vni"] - 1.0

# --- divergence breadth-vs-index: z(breadth,60) - z(vnindex,60) ----------
W = 60
def z(s):
    m = s.rolling(W).mean(); sd = s.rolling(W).std(ddof=0)
    return (s - m) / sd.replace(0, np.nan)

df["z_vni"] = z(df["vni"])
METRICS = {
    "B1_ad_line": "ad_line",
    "B2_nhnl":    "nhnl",
    "B3_ma20":    "b_ma20",
    "B3_ma50":    "b_ma50",
    "P_ma200":    "b_ma200",   # PROD baseline (so sanh)
    "P_rsi_os":   "b_rsi_os",  # PROD baseline (so sanh)
}
for name, col in METRICS.items():
    df[f"z_{name}"] = z(df[col])
    df[f"div_{name}"] = df[f"z_{name}"] - df["z_vni"]

df.to_csv(f"{OUT}/breadth_panel.csv", index=False)
print(f"rows={len(df)} range={df.d.min().date()} -> {df.d.max().date()} univ={df.univ.min():.0f}..{df.univ.max():.0f}")
print(df[["d","univ","b_ma20","b_ma50","b_ma200","b_rsi_os","nhnl","ad_line","vni"]].tail(3).to_string(index=False))

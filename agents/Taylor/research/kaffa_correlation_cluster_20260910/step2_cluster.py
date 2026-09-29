"""Buoc 0 step 2: quet toan universe, tim cum tuong quan cao KHONG giai thich duoc bang ICB lv1.
Data-driven, khong doan ten cum truoc. Chi mo ta cau truc tuong quan, khong tinh forward return.
"""
import numpy as np
import pandas as pd

panel = pd.read_csv("panel.csv", parse_dates=["time"])
icb = pd.read_csv("icb_map.csv")
icb_map = dict(zip(icb.ticker, icb.icb_code_lv1))

wide = panel.pivot(index="time", columns="ticker", values="Close").sort_index()
counts = wide.notna().sum()
wide = wide.loc[:, counts[counts >= 100].index]
ret = np.log(wide / wide.shift(1))

THRESH = 0.6
MIN_OBS = 200


def build_clusters(ret_df, label):
    tickers = list(ret_df.columns)
    corr = ret_df.corr(min_periods=MIN_OBS)
    n = len(tickers)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    idx = {t: i for i, t in enumerate(tickers)}
    edges = []
    cvals = corr.values
    for i in range(n):
        for j in range(i + 1, n):
            c = cvals[i, j]
            if not np.isnan(c) and c > THRESH:
                union(i, j)
                edges.append((tickers[i], tickers[j], c))

    clusters = {}
    for i, t in enumerate(tickers):
        r = find(i)
        clusters.setdefault(r, []).append(t)

    # only clusters with >=3 members (pairs are too easy/noisy to call a "cluster")
    big = {k: v for k, v in clusters.items() if len(v) >= 3}

    rows = []
    for root, members in big.items():
        icbs = [icb_map.get(t) for t in members]
        icbs_known = [c for c in icbs if c is not None]
        n_distinct_icb = len(set(icbs_known))
        # avg internal correlation
        pairs_c = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                c = corr.loc[members[i], members[j]]
                if not np.isnan(c):
                    pairs_c.append(c)
        avgc = np.mean(pairs_c) if pairs_c else np.nan
        rows.append(dict(members=members, size=len(members), n_distinct_icb=n_distinct_icb,
                          icb_list=icbs, avg_internal_corr=avgc,
                          cross_sector=(n_distinct_icb >= 2)))

    df = pd.DataFrame(rows).sort_values(["cross_sector", "avg_internal_corr"], ascending=[False, False])
    df.to_csv(f"clusters_{label}.csv", index=False)
    print(f"\n=== {label}: threshold corr>{THRESH}, {len(edges)} edges, {len(big)} clusters (size>=3) ===")
    print(f"  cross-sector clusters (span >=2 ICB lv1): {df['cross_sector'].sum()} / {len(df)}")
    for _, row in df.head(10).iterrows():
        tag = "CROSS-SECTOR" if row["cross_sector"] else "single-ICB"
        print(f"  [{tag}] size={row['size']} avg_corr={row['avg_internal_corr']:.3f} "
              f"members={row['members']} icb={row['icb_list']}")
    return df


print(f"[scope] recent window: {ret.tail(252).index.min().date()} -> {ret.tail(252).index.max().date()}, 252d")
df_recent = build_clusters(ret.tail(252), "recent252d")

print(f"\n[scope] full sample: {ret.index.min().date()} -> {ret.index.max().date()}")
df_full = build_clusters(ret, "fullsample")

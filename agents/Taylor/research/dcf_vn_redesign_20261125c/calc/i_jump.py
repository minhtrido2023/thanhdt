# -*- coding: utf-8 -*-
"""i_jump.py — [V3 NB-1] tỉ lệ nhảy vốn hoá > 15% tại ngày công bố, đo trên CÁC KỲ BCTC THỰC SỰ vào mẫu (in-universe, as-of ≥ 2014-01), duy nhất theo (mã, ngày công bố).
nhảy_i = log(N_i/N_{i-1}) + (pf_i − pf_{i-1}),  pf = log(Price/Close) tại ngày công bố ⇒ 0 nếu số CP liên tục với hệ số điều chỉnh giá.
Dùng: OUT_DIR=<dir> python i_jump.py. Đọc panel2.parquet của dir đó. In theo nguồn (BQ: cách chọn N; VND)."""
import os, json, numpy as np, pandas as pd
OUT = os.environ["OUT_DIR"]
p = pd.read_parquet(os.path.join(OUT, "panel2.parquet"), columns=["ticker", "known", "src", "N", "N_how", "close_rel", "MC_rel", "in_universe", "ym"])
p["pf"] = np.log(p.MC_rel / p.N / p.close_rel)
res = {}
for scope, q in (("ALL_rows", p), ("IN_UNIVERSE_2014+", p[p.in_universe & (p.ym >= "2014-01")])):
    d = q.drop_duplicates(["ticker", "known"]).copy()
    # kỳ liền trước phải lấy từ TOÀN BỘ chuỗi kỳ của mã (không chỉ kỳ trong mẫu)
    allk = p.drop_duplicates(["ticker", "known"]).sort_values(["ticker", "known"]); allk["Nprev"] = allk.groupby("ticker").N.shift(1); allk["pfprev"] = allk.groupby("ticker").pf.shift(1)
    d = d.merge(allk[["ticker", "known", "Nprev", "pfprev"]], on=["ticker", "known"], how="left"); d = d[d.Nprev.notna()]
    d["jmp"] = np.log(d.N / d.Nprev) + (d.pf - d.pfprev); d["big"] = d.jmp.abs() > np.log(1.15)
    res[scope] = {"n": int(len(d)), "share_gt15": float(d.big.mean()), "by_src": {k: [int(len(x)), float(x.big.mean())] for k, x in d.groupby("src")},
                  "by_N_how": {k: [int(len(x)), float(x.big.mean())] for k, x in d.groupby("N_how")}}
print(json.dumps(res, ensure_ascii=False, indent=1)); json.dump(res, open(os.path.join(OUT, "jump.json"), "w"), ensure_ascii=False, indent=1)

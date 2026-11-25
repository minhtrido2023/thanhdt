# -*- coding: utf-8 -*-
"""selfcheck_pit.py — kiểm PIT: PHÁ mọi dòng dữ liệu SAU ngày as-of D (giá ×1,7 / BCTC ×0,3 / thêm dòng universe giả / route ngẫu nhiên / VND ×1,7)
rồi dựng lại ⇒ đầu ra phải BẰNG HỆT bản sạch (assert_frame_equal exact + md5 parquet). Dùng: python selfcheck_pit.py 2026-10 step"""
import sys, os, hashlib, tempfile
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lvens2_incremental as L
ym, mcp = sys.argv[1], sys.argv[2]
D = L.last_session(ym); rng = np.random.RandomState(20261125); hits = {}

def poison(df, col):
    df = df.copy(); after = df[col] > D; key = ",".join(sorted(df.columns))[:40]; hits[key] = int(after.sum())
    num = [c for c in df.columns if c != col and pd.api.types.is_float_dtype(df[c])]
    for c in num:
        df.loc[after, c] = df.loc[after, c] * (0.3 if "BVPS" in df.columns else 1.7)
    if "route" in df.columns:
        df.loc[after, "route"] = rng.choice(["BANK", "POWER", "COMPOUNDER"], int(after.sum()))
    if list(df.columns) == ["ticker", "time", "in_universe"]:     # universe_pit: thêm dòng giả sau D
        fake = df.drop_duplicates("ticker").head(300).copy(); fake[col] = D + pd.Timedelta(days=3); df = pd.concat([df, fake], ignore_index=True)
    return df

out = {}
for tag, pz in (("clean", None), ("poison", poison)):
    d = tempfile.mkdtemp(prefix=f"pitchk_{tag}_")
    L.run([ym], "pit", d, L.FROZEN, poison=pz, mc_pit=mcp)
    fp = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".parquet")][0]
    out[tag] = (pd.read_parquet(fp), hashlib.md5(open(fp, "rb").read()).hexdigest())
pd.testing.assert_frame_equal(out["clean"][0], out["poison"][0], check_exact=True)
print(f"PIT-SELFCHECK PASS {ym} mc_pit={mcp} D={D.date()} rows={len(out['clean'][0])} md5 clean={out['clean'][1]} poison={out['poison'][1]} "
      f"same_md5={out['clean'][1] == out['poison'][1]} | dòng bị phá sau D theo nguồn: {hits}")

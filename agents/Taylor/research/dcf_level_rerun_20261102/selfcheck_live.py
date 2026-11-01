# -*- coding: utf-8 -*-
"""SELFCHECK đường live: (1) engine vector tái lập dcf_valuation.fair_value (OSHARES_SOURCE=live) 0 VND khi cấp đúng số CP
mà fair_value đã dùng; (2) đo mức khớp giữa os_live dựng lịch sử (oshares_pit + R10, KHÔNG có khoá khung R5/R8/R9) và số CP production thật.
Dùng: python selfcheck_live.py 2026-10-30 [2024-10-31 ...]"""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import level as LV
D = LV.E.D
D.OSHARES_SOURCE = "live"                 # level/engine ghim fin lúc import — đặt lại đường production
import oshares_dcf as osd
p = pd.read_parquet(os.path.join(HERE, "data", "panel_live.parquet"))
fin = D._load_financials()
tot_bad = 0
for d in sys.argv[1:]:
    a = pd.Timestamp(d)
    q = p[p.t == a].reset_index(drop=True)
    if len(q) == 0:
        print(d, "không có tháng này trong panel"); continue
    osd.prime(list(q.ticker), d)
    res = [D.fair_value(r.ticker, d, price=float(r.Price), fin=fin, price_date=r.pxt.date().isoformat()) for r in q.itertuples()]
    okp = np.array([x["ok"] for x in res])
    osh_prod = np.array([x.get("oshares", np.nan) if x["ok"] else np.nan for x in res])
    fv_prod = np.array([x["fair_value_ps"] if x["ok"] else np.nan for x in res])
    # (1) engine với số CP production
    fv_eng = LV.fv(q, osh_prod, 0.5, 0.055)
    both = okp & np.isfinite(fv_eng)
    mism = int((np.abs(fv_eng[both] / fv_prod[both] - 1) > 1e-9).sum())
    # engine tự quyết ok? (base_valid đã lọc panel; fair_value ok ⇒ phải nằm trong panel; ngược lại khác)
    print(f"{d}: n panel {len(q)} | fair_value ok {okp.sum()} | engine-vs-production(số CP của production) mismatch = {mism} / {both.sum()} (ngưỡng 1e-9 tương đối)")
    # (2) os_live dựng lịch sử vs production
    m = okp
    diff = np.abs(q.os_live.values[m] / osh_prod[m] - 1)
    meth = pd.Series([x.get("oshares_method") for x in res])[m].value_counts().to_dict()
    print(f"   os_live(dựng) khác số CP production ở {(diff > 1e-9).sum()} / {m.sum()} mã (|diff|>10%: {(diff > .1).sum()}); phương pháp production: {meth}")
    fvl = LV.fv(q, q.os_live.values, 0.5, 0.055)
    both2 = okp & np.isfinite(fvl)
    print(f"   FV(os_live dựng)/FV(production): median {np.median(fvl[both2]/fv_prod[both2]):.6f}, max|lệch| {np.max(np.abs(fvl[both2]/fv_prod[both2]-1)):.4f}")
    tot_bad += mism
print("SELFCHECK rc =", 1 if tot_bad else 0)
sys.exit(1 if tot_bad else 0)

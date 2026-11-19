#!/usr/bin/env python3
"""Selfcheck macro_stress_ledger (dữ liệu tổng hợp, KHÔNG chạm BQ/Executor). Chạy: env -u TZ python3 ...; TZ=Asia/Tokyo python3 ..."""
import os, sys, tempfile
import numpy as np, pandas as pd
os.environ["MSL_LEDGER"] = os.path.join(tempfile.mkdtemp(), "led.csv")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import macro_stress_ledger as m

fails = []
def ck(c, msg):
    print(("PASS " if c else "FAIL ") + msg)
    if not c: fails.append(msg)

idx = pd.bdate_range("2026-01-01", periods=200)
def mk(k, v, ix=idx): return pd.DataFrame({"k": k, "d": ix, "v": v})
usd = np.full(200, 100.0); usd[150:] = 103.0            # +3% so với 60 quan sát trước, từ i=150 (kéo dài)
dxy = np.full(200, 100.0)                                 # phẳng -> không fire
bond = np.full(200, 4.0); ib = np.full(200, 3.0)
pol_ix = pd.to_datetime(["2026-01-31", "2026-06-30"])
df = pd.concat([mk("vn_usdvnd", usd), mk("us_dxy", dxy), mk("vn_bond_10y", bond), mk("vn_interbank_3m", ib),
                pd.DataFrame({"k": "vn_policy_rate", "d": pol_ix, "v": [4.5, 4.5]})])
asof = idx[-1]
fake = lambda d: ("NEUTRAL", "DT5G_macro")
# 1) episodes: USD/VND mở đúng 1 episode ở i=150, chết 126 quan sát
ep = m.episodes(m.trigger_values(df)["USDVND_60d"], 0.025)
ck(len(ep) == 1 and ep[0][0] == idx[150], f"1 episode USDVND tại {idx[150].date()} (dead window chặn lặp): {[str(d.date()) for d,_ in ep]}")
# 2) ghi sổ chỉ khi kích hoạt đúng quan sát cuối: ở asof (i=199) KHÔNG phải ngày kích hoạt -> không ghi
line, info = m.run(True, df, asof, fake)
ck(info["wrote"] == [] and len(m.load_ledger()) == 0, "episode cũ (không ở quan sát cuối) không ghi sổ")
# 3) cắt df đến i=150 -> ghi 1 dòng, chạy lại -> không trùng
df150 = df[~((df["d"] > idx[150]) & (df["k"] != "vn_policy_rate"))]
line, info = m.run(True, df150, idx[150], fake)
ck(info["wrote"] == ["USDVND_60d"], f"ghi sổ khi kích hoạt tại quan sát cuối: {info['wrote']}")
m.run(True, df150, idx[150], fake)
led = m.load_ledger()
ck(len(led) == 1 and led.iloc[0]["dt5g_state"] == "NEUTRAL" and led.iloc[0]["cluster_id"] == 1, "idempotent + state + cluster_id=1")
ck("GIẢ THUYẾT CHƯA KIỂM" in line and "cụm 1/10" in line and "1/5" in line, "dòng hiển thị có nhãn + đếm cụm")
# 4) fail-closed: asof cách quan sát cuối 10 ngày
line, info = m.run(True, df, idx[-1] + pd.Timedelta(days=10), fake)
ck("không có dữ liệu tươi" in line, "series cũ >7 ngày -> fail-closed, không số cũ")
before = len(m.load_ledger())
# 5) policy cũ (>100 ngày) chỉ vô hiệu T3
line, _ = m.run(False, df, idx[-1] + pd.Timedelta(days=0), fake)
ck("INTERBANK_MINUS_POLICY=n/a(stale)" not in line, "policy 2026-06-30 còn tươi tại asof 2026-10-07 (99 ngày)")
line, _ = m.run(False, df, pd.Timestamp("2026-10-12"), fake)  # policy 104 ngày; daily series 5 ngày
ck("INTERBANK_MINUS_POLICY=n/a(stale)" in line and "USDVND_60d=n/a" not in line, "policy >100 ngày chỉ làm T3 n/a")
# 6) cụm: dòng thứ 2 cách >60 ngày lịch -> cluster 2, DT5G=BEAR không tính vào cụm>=NEUTRAL
m.append_row("DXY_60d", "2026-12-01", 0.06, "BEAR", "DT5G_macro")
led = m.load_ledger()
ck(led["cluster_id"].tolist() == [1, 2] and m.cluster_counts(led) == (2, 1), f"cụm: {m.cluster_counts(led)}")
# 7) append-only: không có đường sửa/xoá — số dòng chỉ tăng
ck(len(led) == before + 1, "sổ chỉ thêm dòng")
# 8) get_gated_state thật trả state hợp lệ; lỗi -> UNAVAILABLE (stub ném lỗi)
real = m.dt5g_state("2026-11-18")
ck(real[0] in ("CRISIS", "BEAR", "NEUTRAL", "BULL", "EX-BULL", "EXBULL"), f"get_gated_state thật: {real}")
import types
stub = types.ModuleType("macro_state_live")
def _raise(*a, **k): raise RuntimeError("x")
stub.get_gated_state = _raise
sys.modules["macro_state_live"] = stub
st = m.dt5g_state("2026-01-05")
ck(st[0] == "UNAVAILABLE", f"get_gated_state lỗi -> UNAVAILABLE ({st[1][:40]})")
print("TZ=", os.environ.get("TZ"), "| FAILS:", len(fails))
sys.exit(1 if fails else 0)

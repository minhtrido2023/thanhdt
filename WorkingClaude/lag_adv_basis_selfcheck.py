# -*- coding: utf-8 -*-
"""Selfcheck ADV basis (Volume_3M_P50 thô × Price thô) cho pt_v22 / pt_v4 / pt_v12 — extract-and-exec đúng đoạn mã engine.
  $DNA_PYEXE lag_adv_basis_selfcheck.py            # 3 ca × 3 engine
  $DNA_PYEXE lag_adv_basis_selfcheck.py --mutate   # mỗi mutation phải làm ≥1 kiểm FAIL
Không đọc giờ hệ thống ⇒ chạy được dưới env -u TZ / TZ lạ."""
import os, sys, re, textwrap
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lag_adv_basis import raw_price_panel, adv_px
RES = []
def ok(n, c, info=""): RES.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n + ("" if c else f"  [{info}]"))

def src(f): return open(os.path.join(HERE, f), encoding="utf-8").read()
def seg(text, start, end, incl_end=True):
    i = text.index(start); j = text.index(end, i)
    return text[i:j + (len(end) if incl_end else 0)]

def entry_fn(fname, mut=None):
    """Đoạn 'apx = ... alloc = min(target, cap)' của pt_v4/pt_v12 bọc thành hàm."""
    s = seg(src(fname), "apx = adv_px(", "alloc = min(target, cap)")
    lines = textwrap.dedent("            " + s).replace("continue", "return None")
    if mut == "fpx": lines = lines.replace("adv*apx", "adv*fpx").replace("adv * MAX_FILL_L * apx", "adv * MAX_FILL_L * fpx").replace("MAX_FILL*apx", "MAX_FILL*fpx")
    if mut == "nocoalesce": lines = lines.replace("adv_px(px_raw_l, dt, tk, fpx)", "px_raw_l.at[dt, tk]")
    if mut == "dropgate": lines = lines.replace("if pd.isna(adv) or adv*apx < LIQ_MIN: return None", "pass")
    code = "def f(px_raw_l, dt, tk, fpx, adv, nav_now, en_row, LIQ_MIN, LIQ_CAP_L, MAX_FILL_L, LIQ_CAP, MAX_FILL, POS_PCT):\n" + textwrap.indent(lines, "    ") + "\n    return alloc\n"
    g = {"pd": pd, "np": np, "adv_px": adv_px}; exec(code, g); return g["f"]

def v22_fn(mut=None):
    s = seg(src("pt_v22_dt5g.py"), "liq_lag = {}", "liq_lag[(tk, d)] = float(adv) * float(px)")
    if mut == "close": s = s.replace("px = adv_px(px_raw_l, d, tk, px)", "pass")
    if mut == "nocoalesce": s = s.replace("px = adv_px(px_raw_l, d, tk, px)", "px = px_raw_l.at[d, tk]")
    code = "def f(liq_l, px_close, px_raw_l, win_idx):\n" + textwrap.indent(s, "    ") + "\n    return liq_lag\n"
    g = {"pd": pd, "np": np, "adv_px": adv_px}; exec(code, g); return g["f"]

def run(mut=None):
    RES.clear(); d = pd.Timestamp("2026-09-10"); idx = pd.DatetimeIndex([d])
    adj, raw = 10000.0, 30000.0
    mk = lambda v: pd.DataFrame({"AAA": [v]}, index=idx)
    ov_p = pd.DataFrame({"time": [d, d], "ticker": ["AAA", "BBB"], "Price": [raw, np.nan]})
    ok("raw_price_panel: có Price ⇒ panel", raw_price_panel(ov_p, idx).at[d, "AAA"] == raw)
    ok("raw_price_panel: pkl không cột Price ⇒ None", raw_price_panel(ov_p.drop(columns="Price"), idx) is None)
    # ---- pt_v4 / pt_v12
    kw = dict(nav_now=1e13, en_row={"surprise": 1.0}, LIQ_MIN=2e9, LIQ_CAP_L=0.2, MAX_FILL_L=5, LIQ_CAP=0.2, MAX_FILL=5, POS_PCT=0.08)
    for fn in ("pt_v4_dt5g.py", "pt_v12_macro.py"):
        f = entry_fn(fn, mut); tag = fn[:7]
        a = f(mk(raw), d, "AAA", adj, 1e5, **kw)          # có Price: ADV = 1e5*3e4 = 3e9 ≥ 2e9 ⇒ vào; cap = .2*1e5*5*3e4
        ok(f"{tag} có Price ⇒ dùng Price (qua gate + cap theo giá thô)", a is not None and abs(a - 0.2 * 1e5 * 5 * raw) < 1, a)
        b = f(mk(np.nan), d, "AAA", adj, 1e5, **kw)       # Price NaN ⇒ fpx: 1e5*1e4=1e9 < 2e9 ⇒ bị chặn
        ok(f"{tag} Price NaN ⇒ rơi về giá điều chỉnh (như cũ, bị gate)", b is None, b)
        c = f(None, d, "AAA", adj, 1e6, **kw)             # pkl không Price ⇒ y như cũ
        ok(f"{tag} không cột Price ⇒ y hệt cũ (cap = .2*adv*5*fpx)", c is not None and abs(c - 0.2 * 1e6 * 5 * adj) < 1, c)
        e = f(mk(raw), d, "ZZZ", adj, 1e6, **kw)          # mã không có trong panel Price
        ok(f"{tag} mã thiếu trong panel Price ⇒ như cũ", e is not None and abs(e - 0.2 * 1e6 * 5 * adj) < 1, e)
    # ---- pt_v22
    f = v22_fn(mut); liq = mk(1e5); pc = mk(adj)
    r1 = f(liq, pc, mk(raw), [d]); r2 = f(liq, pc, mk(np.nan), [d]); r3 = f(liq, pc, None, [d])
    ok("pt_v22 có Price ⇒ ADV = vol × Price", abs(r1[("AAA", d)] - 1e5 * raw) < 1, r1)
    ok("pt_v22 Price NaN ⇒ Close", abs(r2[("AAA", d)] - 1e5 * adj) < 1, r2)
    ok("pt_v22 không cột Price ⇒ Close (như cũ)", abs(r3[("AAA", d)] - 1e5 * adj) < 1, r3)
    return all(c for _, c in RES)

if __name__ == "__main__":
    if "--mutate" not in sys.argv:
        good = run(); print(f"\n{sum(c for _, c in RES)}/{len(RES)} PASS"); sys.exit(0 if good else 1)
    assert run(), "baseline phải xanh"; alive = []
    for m in ("fpx", "nocoalesce", "dropgate", "close"):
        import io, contextlib
        try:
            with contextlib.redirect_stdout(io.StringIO()): good = run(m)
        except Exception: good = False   # mutation làm engine nổ = bị bắt
        print(f"mutation {m}: {'SỐNG (xấu)' if good else 'bị bắt'}"); 
        if good: alive.append(m)
    print("còn sống:", alive or "không"); sys.exit(1 if alive else 0)

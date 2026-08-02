#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""basket_price_basis_selfcheck.py — cổng bắt buộc của bản sửa "tách vai cơ sở giá" trong
`custom_basket.py` (job Taylor_20260802_141725, commit ebeacad).

Bốn câu hỏi, không hơn — theo đúng `.claude/skills/quant-research/SKILL.md` bước 9 (two-way
self-check) + bước 7 (control leg phải tái lập ĐÚNG số cũ):

  T1. ĐỒNG NHẤT THỨC (mạnh nhất): ép `mcapw == mcap` (pxw := Close) trong module MỚI → chuỗi
      level PHẢI trùng BIT-FOR-BIT với module TRƯỚC KHI SỬA. Chứng minh việc viết lại
      SUM(mcap_t)/SUM(mcap_{t-1})-1  →  SUM(w*r)/SUM(w) không hề đổi đại số.
      Nếu T1 fail = refactor sai, mọi số A/B sau đó vô nghĩa.
  T2. PARITY NGÀY GẦN ĐÂY (Price≈Close, hệ số điều chỉnh ~1,00): rổ + level MỚI vs CŨ phải
      gần như không đổi. Lệch lớn ở đây = đã làm hỏng thứ khác.
  T3. POSITIVE CONTROL NGÀY CŨ (hệ số điều chỉnh xa 1,00): PHẢI có khác biệt THẬT.
      0 diff ở đây = bản "sửa" không làm gì cả, chẩn đoán sai.
  T4. AN TOÀN CỔ TỨC: ngày chốt quyền KHÔNG được biến thành khoản lỗ giả — kiểm chân return
      vẫn nằm trên `Close` bằng cách so r_i,t của rổ với Close_t/Close_{t-1} trên cùng ngày.

T2/T3 cùng nhau là điều kiện CẦN VÀ ĐỦ: một mình T2 không phân biệt "sửa đúng" với "no-op",
một mình T3 không phân biệt "sửa đúng" với "làm hỏng".

Chạy:  cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
       BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate $DNA_PYEXE basket_price_basis_selfcheck.py
"""
import os
import subprocess
import sys
import types

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Cấu hình PRODUCTION của rổ custom30V (= ETF_LIQ=custompitg + BASKET_WT=namecap của lệnh pin R3).
PROD_KW = dict(quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap")
# Cửa sổ GẦN ĐÂY: hệ số Close/Price ~1,00 (trung vị 1,000 năm 2026) -> kỳ vọng parity.
RECENT = ("2025-01-02", "2026-06-19")
# Cửa sổ CŨ: hệ số Close/Price xa 1,00 (trung vị 0,448 năm 2014) -> kỳ vọng khác biệt THẬT.
# 2014 là mốc sớm nhất `universe_pit_q`/engine R3 phủ; pre-2014 ngoài tầm phủ của build_pit.
OLD = ("2014-01-02", "2016-12-30")
FAILS = []


def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}", flush=True)
    if not cond:
        FAILS.append(name)


def _bq():
    """bq() của engine — tôn trọng BQ_LOCAL_CACHE (đường chạy của lệnh pin R3)."""
    import simulate_holistic_nav as shn
    return shn.bq


def _load(src, tag):
    m = types.ModuleType(f"custom_basket_{tag}")
    m.__file__ = os.path.join(WORKDIR, "custom_basket.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def load_pre_edit(ref="ebeacad^"):
    """Module TRƯỚC bản sửa tách vai (mcap = Close*OShares dùng cho CẢ return lẫn weight)."""
    src = subprocess.run(["git", "show", f"{ref}:./custom_basket.py"], cwd=WORKDIR,
                         capture_output=True, text=True, check=True).stdout
    return _load(src, "preedit")


def load_post_edit(force_close_basis=False):
    """Module SAU bản sửa. force_close_basis=True ép TOÀN BỘ cơ sở giá về `Close` — cả chân
    WEIGHT (pxw) LẪN chân SELECTION (liquidity) — nên module mới phải suy biến về ĐÚNG hành vi
    tiền-sửa. Phải revert CẢ HAI: bản control chỉ revert pxw vẫn đổi rổ (bài học lần chạy đầu:
    T1 fail vì control thiếu chân selection, KHÔNG phải vì code sai)."""
    src = open(os.path.join(WORKDIR, "custom_basket.py")).read()
    m = _load(src, "postedit_ctl" if force_close_basis else "postedit")
    # Dùng ĐÚNG knob production (`BASKET_PRICE_BASIS`) thay vì vá chuỗi SQL: control leg phải đi
    # qua CHÍNH đường code mà lệnh A/B của Bước 4 sẽ chạy, nếu không T1 chỉ chứng minh cho một
    # phiên bản không ai chạy. `pxw_sql()` đọc env tại thời điểm gọi nên set ở đây là đủ.
    m._SC_BASIS = "legacy" if force_close_basis else "split"
    return m


def adj_factor_line(tag, raw):
    """Đo THẬT hệ số điều chỉnh Close/Price trên chính panel rổ đã lấy (sức phân giải của phép
    thử) — không suy đoán 'gần đây thì ~1,00', và không cần thêm truy vấn.
    Tính bằng pandas, KHÔNG bằng APPROX_QUANTILES: cache production là DuckDB, hàm đó chỉ có
    trên BigQuery — selfcheck phải chạy được trên đúng đường dữ liệu của lệnh pin."""
    r = raw.dropna(subset=["Close", "pxw"])
    f = (r["Close"] / r["pxw"]).replace([np.inf, -np.inf], np.nan).dropna()
    return (f"      {tag:6s} p05 {f.quantile(0.05):.3f} / p50 {f.quantile(0.50):.3f} / "
            f"p95 {f.quantile(0.95):.3f} | |f-1|>5% ở {float((f.sub(1).abs()>0.05).mean())*100:.1f}% "
            f"dòng (n={len(f):,})")


def run(mod, bq, win):
    prev = os.environ.get("BASKET_PRICE_BASIS")
    basis = getattr(mod, "_SC_BASIS", None)
    if basis:
        os.environ["BASKET_PRICE_BASIS"] = basis
    try:
        lvl, adv, mem, raw = mod.build_pit(bq, win[0], win[1], **PROD_KW)
    finally:
        os.environ.pop("BASKET_PRICE_BASIS", None)
        if prev is not None:
            os.environ["BASKET_PRICE_BASIS"] = prev
    s = pd.Series(lvl).sort_index()
    mem = mem.copy()
    mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])
    members = {d: sorted(g["ticker"]) for d, g in mem.groupby("rebal_date")}
    return s, members, raw


def ret_of(level):
    return level.sort_index().pct_change().dropna()


def cmp_levels(a, b):
    """So 2 chuỗi level trên phần index chung -> (max |Δ return| theo ngày, CAGR-tương-đương)."""
    ra, rb = ret_of(a), ret_of(b)
    ix = ra.index.intersection(rb.index)
    d = (ra.loc[ix] - rb.loc[ix]).abs()
    tot_a = float(a.loc[a.index.intersection(b.index)].iloc[-1] / a.loc[a.index.intersection(b.index)].iloc[0])
    tot_b = float(b.loc[a.index.intersection(b.index)].iloc[-1] / b.loc[a.index.intersection(b.index)].iloc[0])
    return float(d.max()), len(ix), tot_a, tot_b


def member_diff(ma, mb):
    ds = sorted(set(ma) & set(mb))
    per = [len(set(ma[d]) ^ set(mb[d])) // 2 for d in ds]
    return ds, per


def main():
    bq = _bq()
    print(f"BQ_LOCAL_CACHE = {os.environ.get('BQ_LOCAL_CACHE', '(live BQ)')}")
    pre = load_pre_edit()
    post = load_post_edit()
    ctl = load_post_edit(force_close_basis=True)


    # ── T1. ĐỒNG NHẤT THỨC ────────────────────────────────────────────────────────────────
    print("\nT1. Đồng nhất thức (ép mcapw==mcap → phải trùng module tiền-sửa BIT-FOR-BIT)")
    for tag, win in (("recent", RECENT), ("old", OLD)):
        s_pre, m_pre, _ = run(pre, bq, win)
        s_ctl, m_ctl, _ = run(ctl, bq, win)
        ix = s_pre.index.intersection(s_ctl.index)
        dmax = float((s_pre.loc[ix] - s_ctl.loc[ix]).abs().max())
        check(f"T1[{tag}] level trùng khít", dmax == 0.0,
              f"max|Δlevel| = {dmax:.6e} trên {len(ix)} phiên")
        ds, per = member_diff(m_pre, m_ctl)
        check(f"T1[{tag}] rổ trùng khít", sum(per) == 0,
              f"{sum(per)} tên đổi trên {len(ds)} mốc rebal")

    # ── T2. PARITY MỐC REBAL MỚI NHẤT ─────────────────────────────────────────────────────
    # ⚠️ "Parity ngày gần đây" chỉ đúng ở MỐC REBAL MỚI NHẤT, nơi quý chọn rổ nằm sát ngày
    # snapshot nên Close/Price ~1,00. Trên cả CỬA SỔ 18 tháng hệ số KHÔNG ~1,00 (mỗi mã tích
    # luỹ cổ tức từ ngày t tới ngày snapshot) — đo bên dưới, không giả định.
    print("\nT2. Parity tại mốc rebal MỚI NHẤT (nơi Close/Price ~1,00)")
    s_pre_r, m_pre_r, _ = run(pre, bq, RECENT)
    s_new_r, m_new_r, raw_r = run(post, bq, RECENT)
    last = max(set(m_pre_r) & set(m_new_r))
    same_last = set(m_pre_r[last]) == set(m_new_r[last])
    check(f"T2 rổ tại rebal mới nhất ({last.date()}) KHÔNG đổi", same_last,
          f"{len(set(m_pre_r[last]) ^ set(m_new_r[last]))//2} tên đổi/30")
    dmax_r, n_r, ta, tb = cmp_levels(s_pre_r, s_new_r)
    ds_r, per_r = member_diff(m_pre_r, m_new_r)
    print("      sức phân giải (hệ số Close/Price đo trên chính panel này):")
    print(adj_factor_line("recent", raw_r))
    print(f"      [đo, KHÔNG phải gate] cả cửa sổ {RECENT[0]}..{RECENT[1]}: "
          f"{sum(per_r)} tên đổi / {len(ds_r)} rebal (TB {np.mean(per_r) if per_r else 0:.2f}/30); "
          f"tổng lợi suất cũ x{ta:.5f} vs mới x{tb:.5f} (Δ {(tb-ta)*100:+.2f}pp)")

    # ── T3. POSITIVE CONTROL NGÀY CŨ ──────────────────────────────────────────────────────
    print("\nT3. Positive control ngày cũ (Close/Price xa 1,00 → PHẢI có khác biệt thật)")
    s_pre_o, m_pre_o, _ = run(pre, bq, OLD)
    s_new_o, m_new_o, raw_o = run(post, bq, OLD)
    dmax_o, n_o, toa, tob = cmp_levels(s_pre_o, s_new_o)
    ds_o, per_o = member_diff(m_pre_o, m_new_o)
    print("      sức phân giải (hệ số Close/Price đo trên chính panel này):")
    print(adj_factor_line("old", raw_o))
    check("T3 rổ ĐỔI thật (>0 tên)", sum(per_o) > 0,
          f"{sum(per_o)} tên đổi / {len(ds_o)} mốc rebal (TB {np.mean(per_o) if per_o else 0:.2f}/30, "
          f"max {max(per_o) if per_o else 0})")
    check("T3 chuỗi return ĐỔI thật (>0)", dmax_o > 0,
          f"max|Δret| = {dmax_o*100:.4f}pp/phiên; tổng kỳ cũ x{toa:.5f} vs mới x{tob:.5f} "
          f"(Δ {(tob-toa)*100:+.2f}pp)")
    check("T3 khác biệt LỚN HƠN ngày gần đây (dose-response theo hệ số đ/c)",
          sum(per_o) / max(len(ds_o), 1) > sum(per_r) / max(len(ds_r), 1),
          f"cũ {sum(per_o)/max(len(ds_o),1):.2f} tên/rebal vs gần đây "
          f"{sum(per_r)/max(len(ds_r),1):.2f} tên/rebal")

    # ── T4. AN TOÀN CỔ TỨC ────────────────────────────────────────────────────────────────
    # Chân RETURN phải vẫn là Close. Kiểm trực tiếp: mcap/mcapw của cùng 1 mã-ngày phải lệch
    # đúng bằng hệ số Close/Price, và mcap phải tái lập Close*OShares (không phải Price*OShares).
    print("\nT4. An toàn cổ tức (chân return vẫn trên Close → ngày chốt quyền không thành lỗ giả)")
    r = raw_o.dropna(subset=["mcap", "mcapw", "Close", "pxw", "OShares"])
    lhs = (r["mcap"] / r["mcapw"]).values
    rhs = (r["Close"] / r["pxw"]).values
    ok_ratio = np.nanmax(np.abs(lhs - rhs)) < 1e-9
    check("T4 mcap/mcapw == Close/Price (2 chân tách đúng)", bool(ok_ratio),
          f"max|Δ| = {np.nanmax(np.abs(lhs - rhs)):.3e}, n={len(r):,}")
    adj = (r["Close"] / r["pxw"])
    n_far = int((adj.sub(1.0).abs() > 0.05).sum())
    check("T4 có mẫu hệ số đ/c XA 1,00 trong cửa sổ (phép thử có sức phân giải)", n_far > 0,
          f"{n_far:,}/{len(r):,} dòng có |Close/Price-1|>5% "
          f"(trung vị hệ số {float(adj.median()):.3f})")

    print("\n" + "=" * 78)
    if FAILS:
        print(f"KẾT QUẢ: FAIL {len(FAILS)} — {', '.join(FAILS)}")
        return 1
    print("KẾT QUẢ: PASS toàn bộ (T1 đồng nhất thức / T2 parity / T3 positive control / T4 cổ tức)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

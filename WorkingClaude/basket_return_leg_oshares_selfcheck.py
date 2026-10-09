#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""basket_return_leg_oshares_selfcheck.py — cổng bắt buộc của bản sửa "chuỗi return không được
mang số cổ phiếu" trong `custom_basket.py` (job Taylor_20260927_022253; finding
`custom30v-index-return-cong-tang-truong-so-CP`, quant-skeptic CONFIRMED high 2026-09-26).

Anh em với `basket_price_basis_selfcheck.py` (bản sửa 2026-08-02 tách vai GIÁ). Bản này khoá vai
SỐ LƯỢNG: `OShares` là đại lượng point-in-time theo QUÝ, nên mỗi bước nhảy số CP (bonus issue,
cổ tức CP, phát hành riêng lẻ) từng đi vào TỬ SỐ của r_i,t = mcap_t/mcap_{t-1} − 1 mà mẫu số
không thấy ⇒ một ngày return giả. Giả vì `Close` ĐÃ được điều chỉnh nguợc cho đúng sự kiện đó
⇒ đếm hai lần.

Năm câu hỏi, không hơn (theo `.claude/skills/quant-research/SKILL.md` bước 7 control leg + bước 9
two-way self-check). R1+R4 một mình không phân biệt "sửa đúng" với "no-op"; R3 một mình không
phân biệt "sửa đúng" với "làm hỏng". Phải có cả hai chiều.

  R1. BẤT BIẾN MỚI: chuỗi return của engine PHẢI trùng BIT-FOR-BIT với chuỗi dựng lại độc lập
      từ Σ w_prev·(Close_t/Close_{t-1}−1) — tức số CP đã ra khỏi chân return hoàn toàn.
  R2. CHÂN WEIGHT BYTE-IDENTICAL: bảng weight publish (đúng công thức `custom30_history.py`
      dùng: `mcapw` → `_cap_names`) phải có md5 GIỐNG HỆT giữa mới / legacy / tiền-sửa.
      Đây là ràng buộc bảo vệ ĐƯỜNG TIỀN LIVE (`data/custom30v_8l_publish.csv` →
      `tav2_bq.custom30v_8l` → `compute_park_trim.py`).
  R3. POSITIVE CONTROL: trên panel CÓ bước OShares thật, chuỗi mới PHẢI khác legacy, và khác
      biệt phải KHU TRÚ ĐÚNG vào các ngày có bước OShares (không phải lệch trải đều — lệch trải
      đều = đã làm hỏng cái khác).
  R4. THÀNH VIÊN + LEVEL-COLUMN KHÔNG ĐỔI: membership mỗi mốc rebal và đồng nhất thức
      mcap/mcapw == Close/Price phải y nguyên. Cột `mcap` KHÔNG bị sửa — chỉ thôi làm chân return.
  R5. LEGACY == TIỀN-SỬA: bật `BASKET_RETURN_OSHARES=legacy` phải tái lập module trước commit
      này BIT-FOR-BIT ⇒ knob rollback là thật, và R3 đo đúng một biến.
  (Từ 2026-10-09: R2-tiền-sửa/R4-membership/R5 đo trên CẶP COMMIT đông cứng 1b89881b vs cha —
   xem `load_fix()`; HEAD đã đổi chân weight có chủ đích ở 92aa43f2.)

Chạy:  cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
       BQ_LOCAL_CACHE=data/bq_cache $DNA_PYEXE basket_return_leg_oshares_selfcheck.py
"""
import hashlib
import os
import subprocess
import sys
import types

WORKDIR = os.environ.get("BASKET_RETLEG_WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Cấu hình PRODUCTION của rổ custom30V (= ETF_LIQ=custompitg + BASKET_WT=namecap của lệnh pin R3).
PROD_KW = dict(quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap")
NAME_CAP = 0.10          # = custom30_history.NAME_CAP (chân weight publish)
# Cửa sổ chính: phủ các bước OShares THẬT đã đo trên rổ live (ACB +13% 2026-07-22, HPG +10%
# 2026-07-30) nhưng vẫn đủ ngắn để selfcheck chạy được như một cổng.
WIN = ("2025-01-02", "2026-06-19")
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


def load_pre_edit(ref="1b89881b^"):
    """Module TRƯỚC bản sửa này (chuỗi return còn chạy trên `mcap`).

    Mặc định `1b89881b^` = cha của commit bản sửa (2026-09-27). Bản đầu mặc định `HEAD` (đúng lúc
    viết, khi bản sửa chưa commit) nên sau merge selfcheck tự dừng ở guard bên dưới mỗi đêm
    (selfcheck-red 2026-09-27→10-09). Override vẫn qua env `BASKET_RETLEG_PREREF`.
    """
    ref = os.environ.get("BASKET_RETLEG_PREREF", ref)
    src = subprocess.run(["git", "show", f"{ref}:./custom_basket.py"], cwd=WORKDIR,
                         capture_output=True, text=True, check=True).stdout
    if "BASKET_RETURN_OSHARES" in src:
        raise SystemExit(
            f"BASKET_RETLEG_PREREF={ref} ĐÃ chứa bản sửa (thấy chuỗi BASKET_RETURN_OSHARES) ⇒ "
            "control leg sẽ là no-op và R5/R3 mất ý nghĩa. Trỏ vào commit TRƯỚC bản sửa.")
    return _load(src, "preedit_retleg")


def load_fix(ref="1b89881b"):
    """Module ĐÚNG commit bản sửa (chưa có các thay đổi CÓ CHỦ ĐÍCH về sau).

    Vì sao cần (sweep selfcheck-red 2026-10-09): sau 1b89881b, `92aa43f2` (OShares bước tại
    EX-DATE), `d77f1123`, `e548fd73` đổi CÓ CHỦ ĐÍCH chân weight ⇒ HEAD vs `1b89881b^` khác ≥2
    trục, R2-tiền-sửa/R5 FAIL dù bản sửa đúng. A/B "knob legacy tái lập tiền-sửa BIT-FOR-BIT" là
    câu hỏi về CẶP COMMIT (sửa vs cha) ⇒ đo trên cặp đó, đông cứng, 1 trục. Các bất biến của
    HEAD (R1, R1b, R2 mới==legacy, R3, R4 đồng nhất thức) vẫn chạy trên HEAD.
    Override qua env `BASKET_RETLEG_FIXREF`.
    """
    ref = os.environ.get("BASKET_RETLEG_FIXREF", ref)
    src = subprocess.run(["git", "show", f"{ref}:./custom_basket.py"], cwd=WORKDIR,
                         capture_output=True, text=True, check=True).stdout
    if "BASKET_RETURN_OSHARES" not in src:
        raise SystemExit(f"BASKET_RETLEG_FIXREF={ref} KHÔNG chứa bản sửa (thiếu chuỗi "
                         "BASKET_RETURN_OSHARES) ⇒ cặp A/B vô nghĩa. Trỏ vào commit bản sửa.")
    return _load(src, "fix_retleg")


def load_cur():
    src = open(os.path.join(WORKDIR, "custom_basket.py"), encoding="utf-8").read()
    return _load(src, "cur_retleg")


def run(mod, bq, win, legacy=False):
    """build_pit dưới đúng 1 biến: BASKET_RETURN_OSHARES."""
    prev = os.environ.get("BASKET_RETURN_OSHARES")
    os.environ["BASKET_RETURN_OSHARES"] = "legacy" if legacy else "flat"
    try:
        lvl, adv, mem, raw = mod.build_pit(bq, win[0], win[1], **PROD_KW)
    finally:
        os.environ.pop("BASKET_RETURN_OSHARES", None)
        if prev is not None:
            os.environ["BASKET_RETURN_OSHARES"] = prev
    s = pd.Series(lvl).sort_index()
    memdf = mem.copy()
    memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
    members = {d: sorted(g["ticker"]) for d, g in memdf.groupby("rebal_date")}
    return s, members, raw, memdf


def ret_of(level):
    return level.sort_index().pct_change().dropna()


def publish_weight_md5(mod, mem, raw):
    """Tái lập ĐÚNG chân weight mà `custom30_history.py` publish lên đường tiền live:
    `mcapw` cuối cùng ≤ rebal_date, chuẩn hoá, rồi `_cap_names(·, NAME_CAP)`. Trả md5 của bảng
    (ticker, rebal_date, weight làm tròn 6 số) — cùng độ chính xác CSV publish thật dùng.
    """
    bx = raw.copy()
    bx["time"] = pd.to_datetime(bx["time"])
    memdf = mem.copy()
    memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
    rows = []
    for rd, g in memdf.groupby("rebal_date"):
        g = g.sort_values("liq_rank")
        tks = list(g["ticker"])
        sub = bx[(bx["ticker"].isin(tks)) & (bx["time"] <= rd)]
        mc = sub.sort_values("time").groupby("ticker")["mcapw"].last().reindex(tks).fillna(0.0)
        base = (mc / mc.sum()).values if mc.sum() > 0 else np.ones(len(tks)) / len(tks)
        w = mod._cap_names(base, NAME_CAP)
        for tk, wi in zip(tks, w):
            rows.append(f"{rd.date()},{tk},{round(float(wi), 6):.6f}")
    blob = "\n".join(rows)
    return hashlib.md5(blob.encode()).hexdigest(), len(rows)


def close_chain_ret(mod, raw, mem):
    """Dựng lại ĐỘC LẬP chuỗi return từ Close thuần + chân weight của engine, KHÔNG gọi build_pit.
    Đây là nửa thứ hai của two-way check: nếu cả engine và bản dựng lại đều sai cùng kiểu thì R1
    vô nghĩa, nên bản này viết thẳng từ raw panel chứ không tái dùng code vòng lặp của engine.
    """
    import bisect
    bx = raw.copy()
    bx["time"] = pd.to_datetime(bx["time"])
    mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    mcapw = (bx.pivot_table(index="time", columns="ticker", values="mcapw")
               .reindex(index=mcap.index, columns=mcap.columns))
    clo = (bx.pivot_table(index="time", columns="ticker", values="Close")
             .reindex(index=mcap.index, columns=mcap.columns))
    memdf = mem.copy()
    memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
    # `qmult` được đọc THẲNG từ members_df (cột engine tự xuất) và thứ tự theo `liq_rank` — đúng
    # thứ tự engine đưa vào `_cap_names`, vì phép cap phân phối lại phần vượt trần nên thứ tự có
    # ảnh hưởng. Tự tính lại qmult từ `rating` là chỗ bản nháp đầu sai (quality="none" ⇒ qmult≡1,0).
    members = {}
    for rd, g in memdf.groupby("rebal_date"):
        g = g.sort_values("liq_rank")
        members[rd] = list(zip(g["ticker"], g["qmult"].astype(float)))
    reb = sorted(members)
    out = pd.Series(0.0, index=mcap.index)
    prev = None
    for d in mcap.index:
        i = bisect.bisect_right(reb, d) - 1
        if i < 0 or prev is None:
            prev = d
            continue
        mem_d = members[reb[i]]
        tks = [t for t, _ in mem_d if t in mcap.columns]
        qm = np.array([q for t, q in mem_d if t in mcap.columns])
        today = mcap.loc[d, tks].values.astype(float)
        yest = mcap.loc[prev, tks].values.astype(float)
        yestw = mcapw.loc[prev, tks].values.astype(float)
        ok = ~np.isnan(today) & ~np.isnan(yest)
        if ok.sum() > 0:
            yvw = np.where(np.isnan(yestw[ok]), yest[ok], yestw[ok])
            r = clo.loc[d, tks].values.astype(float)[ok] / clo.loc[prev, tks].values.astype(float)[ok] - 1.0
            base = yvw * qm[ok]
            W = base / base.sum() if base.sum() > 0 else base
            W = mod._cap_names(W, 0.10)
            out.loc[d] = float(np.nansum(W * r))
        prev = d
    return out


def oshares_step_dates(raw):
    """Ngày CÓ bước OShares, đo THẬT trên chính panel (không đoán theo lịch quý)."""
    bx = raw.copy()
    bx["time"] = pd.to_datetime(bx["time"])
    bx = bx.sort_values(["ticker", "time"])
    steps = {}
    for tk, g in bx.groupby("ticker"):
        v = g["OShares"].values
        ts = g["time"].values
        for i in range(1, len(v)):
            if pd.notna(v[i]) and pd.notna(v[i - 1]) and v[i] != v[i - 1]:
                steps.setdefault(pd.Timestamp(ts[i]), []).append(
                    (tk, float(v[i - 1]), float(v[i])))
    return steps


def main():
    bq = _bq()
    print(f"BQ_LOCAL_CACHE = {os.environ.get('BQ_LOCAL_CACHE', '(live BQ)')}")
    # In ra ĐÚNG file module đang test (quant-skeptic recommended_reruns, 2026-09-27). Chạy trần từ
    # worktree mà quên `BASKET_RETLEG_WORKDIR=` thì selfcheck này test module CANONICAL: nó FAIL to
    # (R1/R3) nên không im lặng, nhưng thông điệp FAIL không nói ra nguyên nhân thật — §29 đòi in
    # bằng chứng đang cầm trong tay thay vì để người đọc đoán.
    print(f"WORKDIR        = {WORKDIR}")
    _cbmod = __import__("custom_basket")
    print(f"custom_basket  = {_cbmod.__file__}  (BASKET_RETURN_OSHARES="
          f"{os.environ.get('BASKET_RETURN_OSHARES', 'flat (default)')})")
    print(f"cửa sổ = {WIN[0]}..{WIN[1]}  |  PROD_KW = {PROD_KW}")
    cur = load_cur()
    pre = load_pre_edit()
    fix = load_fix()

    s_new, m_new, raw_new, md_new = run(cur, bq, WIN, legacy=False)
    s_leg, m_leg, raw_leg, md_leg = run(cur, bq, WIN, legacy=True)
    s_pre, m_pre, raw_pre, md_pre = run(pre, bq, WIN)
    s_fix, m_fix, raw_fix, md_fix = run(fix, bq, WIN, legacy=False)
    s_fixleg, _, _, _ = run(fix, bq, WIN, legacy=True)

    steps = oshares_step_dates(raw_new)
    n_step_in = sum(1 for d in steps if d in s_new.index)
    print(f"sức phân giải: {len(steps)} ngày có bước OShares trên panel "
          f"({n_step_in} nằm trong index level)")

    # ── R1. BẤT BIẾN MỚI ─────────────────────────────────────────────────────────────────
    print("\nR1. Bất biến mới (chuỗi engine == chuỗi Close thuần dựng lại độc lập)")
    ret_eng = ret_of(s_new)
    ret_flat = close_chain_ret(cur, raw_new, md_new)
    ix = ret_eng.index.intersection(ret_flat.index)
    dmax = float((ret_eng.loc[ix] - ret_flat.loc[ix]).abs().max())
    check("R1 max|ret_engine − ret_flat| ≈ 0", dmax < 1e-12,
          f"max|Δ| = {dmax:.3e} trên {len(ix)} phiên")

    # cùng phép so trên legacy: PHẢI lệch (chứng minh R1 có sức phân giải, không phải hằng đúng)
    dmax_leg = float((ret_of(s_leg).loc[ix] - ret_flat.loc[ix]).abs().max())
    check("R1b cùng phép so trên legacy PHẢI lệch (R1 không phải hằng đúng)", dmax_leg > 1e-9,
          f"max|Δ| = {dmax_leg:.3e}")

    # ── R2. CHÂN WEIGHT BYTE-IDENTICAL ───────────────────────────────────────────────────
    print("\nR2. Chân weight (đường tiền LIVE) byte-identical")
    h_new, n_new = publish_weight_md5(cur, md_new, raw_new)
    h_leg, _ = publish_weight_md5(cur, md_leg, raw_leg)
    h_pre, _ = publish_weight_md5(pre, md_pre, raw_pre)
    h_fix, n_fix = publish_weight_md5(fix, md_fix, raw_fix)
    check("R2 md5(weight) mới == legacy", h_new == h_leg, f"{h_new} vs {h_leg}")
    check("R2 md5(weight) bản-sửa == tiền-sửa (cặp commit 1b89881b vs cha)", h_fix == h_pre,
          f"{h_fix} vs {h_pre} ({n_fix} dòng ticker×rebal)")

    # ── R3. POSITIVE CONTROL ─────────────────────────────────────────────────────────────
    print("\nR3. Positive control (panel có bước OShares thật → PHẢI khác + phải khu trú)")
    d = (ret_of(s_new) - ret_of(s_leg)).reindex(ix).fillna(0.0)
    nz = d[d.abs() > 1e-9]
    check("R3 chuỗi return ĐỔI thật (>0)", len(nz) > 0,
          f"{len(nz)}/{len(ix)} phiên lệch; max|Δret| = {float(d.abs().max())*100:.4f}pp/phiên; "
          f"tổng kỳ legacy x{float(s_leg.iloc[-1]/s_leg.iloc[0]):.5f} vs "
          f"mới x{float(s_new.iloc[-1]/s_new.iloc[0]):.5f}")
    if len(nz) > 0:
        on_step = sum(1 for dt in nz.index if dt in steps)
        check("R3 khác biệt KHU TRÚ vào ngày có bước OShares (≥95%)",
              on_step / len(nz) >= 0.95,
              f"{on_step}/{len(nz)} phiên lệch trùng ngày bước OShares")
        top = d.abs().sort_values(ascending=False).head(5)
        for dt, v in top.items():
            who = ", ".join(f"{t} {o:.0f}→{n:.0f} ({n/o-1:+.1%})" for t, o, n in steps.get(dt, []))
            print(f"      {dt.date()}  Δret {float(d.loc[dt])*100:+.4f}%   {who or '(không có bước OShares)'}")

    # ── R4. MEMBERSHIP + ĐỒNG NHẤT THỨC ──────────────────────────────────────────────────
    print("\nR4. Membership và cột `mcap` không đổi")
    ds = sorted(set(m_fix) & set(m_pre))
    per = [len(set(m_fix[x]) ^ set(m_pre[x])) // 2 for x in ds]
    check("R4 membership bản-sửa == tiền-sửa", sum(per) == 0,
          f"{sum(per)} tên đổi trên {len(ds)} mốc rebal")
    r = raw_new.dropna(subset=["mcap", "mcapw", "Close", "pxw", "OShares"])
    dd = float(np.nanmax(np.abs((r["mcap"] / r["mcapw"]).values - (r["Close"] / r["pxw"]).values)))
    check("R4 mcap/mcapw == Close/Price vẫn đúng (cột mcap KHÔNG bị sửa)", dd < 1e-9,
          f"max|Δ| = {dd:.3e}, n={len(r):,}")
    dmc = float(np.nanmax(np.abs((r["mcap"] / (r["Close"] * r["OShares"])).values - 1.0)))
    check("R4 mcap == Close*OShares vẫn đúng", dmc < 1e-12, f"max|Δ| = {dmc:.3e}")

    # ── R5. LEGACY == TIỀN-SỬA ───────────────────────────────────────────────────────────
    print("\nR5. Knob rollback là thật (legacy trùng tiền-sửa BIT-FOR-BIT)")
    ixp = s_fixleg.index.intersection(s_pre.index)
    dl = float((s_fixleg.loc[ixp] - s_pre.loc[ixp]).abs().max())
    check("R5 level legacy (bản-sửa) == tiền-sửa", dl == 0.0,
          f"max|Δlevel| = {dl:.6e} trên {len(ixp)} phiên")

    print("\n" + "=" * 78)
    if FAILS:
        print(f"KẾT QUẢ: FAIL {len(FAILS)} — {', '.join(FAILS)}")
        return 1
    print("KẾT QUẢ: PASS toàn bộ (R1 bất biến / R2 weight byte-identical / R3 positive control / "
          "R4 membership+mcap / R5 rollback)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

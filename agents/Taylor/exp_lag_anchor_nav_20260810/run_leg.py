# -*- coding: utf-8 -*-
"""Harness A/B NAV-level cho trần `hard_no_chase_ceiling_vnd` của book LAG.

VÌ SAO CẦN HARNESS (đọc trước khi sửa): engine backtest `pt_v23_audit_2014.py` /
`simulate_holistic_nav.py` **KHÔNG mô hình hoá** cửa sổ entry 3 phiên và **KHÔNG có** khái niệm
trần anchor. Nó fill nhiều ngày (`max_fill_days=5`, mỗi ngày ở Open, trần 20% ADV/ngày) mà không
có ràng buộc giá nào. Nên số pin R3 hiện tại (28,86%) là chân "KHÔNG CÓ TRẦN" — không phải chân
"trần = anchor" đang chạy live. Muốn A/B được "trần = anchor" vs "trần = anchor×1,03" thì phải
TIÊM cơ chế trần vào engine.

CÁCH TIÊM — chèn text vào source lúc chạy, KHÔNG sửa file production, KHÔNG để lại bản sao
`simulate_holistic_nav.py` nào trong repo (bản sao tĩnh sẽ mốc khi engine đổi). Nếu chuỗi neo
không còn khớp ⇒ RAISE, không im lặng chạy sai.

MÔ HÌNH TRẦN (khớp luật V2.4 rule 2 tới đâu, lệch ở đâu — ghi rõ để không trích nhầm):
  - Anchor = giá xử lý của NGÀY ĐẦU TIÊN lệnh được chạm (Open phiên chuẩn trong engine).
    Live: `entry_anchor_price` = `tav2_bq.ticker.Price` (giá thô) của phiên chuẩn ≈ giá ĐÓNG CỬA.
    ⇒ engine dùng Open, live dùng Price cuối phiên. LỆCH NÀY CÓ THẬT, nhưng nó tác động
    NHƯ NHAU lên mọi chân (cùng định nghĩa anchor), nên Δ giữa các chân vẫn cô lập đúng 1 tham số.
  - Từ ngày fill thứ 2 trở đi: chỉ fill nếu `px <= anchor * (1 + cap)`. Vượt ⇒ bỏ phiên đó,
    giữ pending (đúng ngữ nghĩa "lệnh không khớp", không phải "huỷ lệnh").
  - `cap=None` ⇒ KHÔNG tiêm gì (chân đối chứng, phải tái lập đúng pin R3 28,86%).
  - Chỉ áp cho tier LAG. BAL/CAPIT/ETF không đụng (đúng §5.1 báo cáo gốc).
  - Engine cho tối đa 5 ngày fill, live chỉ 3 phiên. Chênh này GIỐNG NHAU ở mọi chân có trần
    ⇒ không làm nhiễu Δ, nhưng làm MỌI chân có trần rộng rãi hơn live một chút. Đã disclose.

Chạy: DNA_PYEXE run_leg.py <cap|none> <tag>   (mọi env config khác lấy từ run_all.sh)
"""
import os, sys, runpy

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

_ANCHOR_TEXT = '            entry["last_seen_price"] = px\n'

_INJECT = '''
            # ── [EXP anchor-ceiling harness — exp_lag_anchor_nav_20260810] ─────────────
            if _EXPA_CAP is not None and play_type in _EXPA_TIERS:
                if entry.get("_expa_anchor") is None:
                    entry["_expa_anchor"] = px          # phiên chuẩn = ngày xử lý đầu tiên
                    _EXPA_STATS["anchored"] += 1
                elif px > entry["_expa_anchor"] * (1.0 + _EXPA_CAP):
                    _EXPA_STATS["blocked_days"] += 1
                    if entry["days_filling"] < max_fill_days:
                        new_pending.append(entry)
                    else:
                        if entry["filled_shares"] > 0:
                            _finalize_partial(entry, positions, tk, play_type,
                                              ticker_sector_map, vni_dates, today)
                            abandoned_partial += 1
                        else:
                            _EXPA_STATS["never_filled"] += 1
                    continue
            # ── [/EXP] ─────────────────────────────────────────────────────────────────
'''


def _install_patched_shn(cap):
    """Nạp `simulate_holistic_nav` đã tiêm vào sys.modules TRƯỚC khi pt_v23 import nó."""
    import types
    src_path = os.path.join(WORKDIR, "simulate_holistic_nav.py")
    with open(src_path, encoding="utf-8") as fh:
        src = fh.read()

    n = src.count(_ANCHOR_TEXT)
    if n != 1:
        raise RuntimeError(
            f"chuỗi neo xuất hiện {n} lần trong simulate_holistic_nav.py (cần đúng 1) "
            "— engine đã đổi, harness DỪNG thay vì chạy sai")
    src = src.replace(_ANCHOR_TEXT, _ANCHOR_TEXT + _INJECT)

    header = (
        "_EXPA_CAP = %r\n"
        "_EXPA_TIERS = {'LAG_HI', 'LAG_LO', 'LAG_TOP'}\n"
        "_EXPA_STATS = {'anchored': 0, 'blocked_days': 0, 'never_filled': 0}\n"
    ) % (cap,)
    # chèn sau dòng import cuối cùng ở đầu file (an toàn: chèn ngay sau docstring+imports)
    marker = "\nimport pandas as pd\n"
    if marker not in src:
        raise RuntimeError("không tìm thấy điểm chèn header trong simulate_holistic_nav.py")
    src = src.replace(marker, marker + "\n" + header, 1)

    mod = types.ModuleType("simulate_holistic_nav")
    mod.__file__ = src_path
    code = compile(src, src_path + " [EXPA-patched]", "exec")
    sys.modules["simulate_holistic_nav"] = mod
    exec(code, mod.__dict__)
    return mod


def main():
    raw = sys.argv[1].strip().lower()
    cap = None if raw in ("none", "off", "") else float(raw)
    tag = sys.argv[2].strip()

    mod = _install_patched_shn(cap)
    print(f"[EXPA] cap={cap!r} tag={tag} — patched simulate_holistic_nav loaded "
          f"(id={id(mod)})", flush=True)

    os.environ["EXP_TAG"] = tag
    sys.argv = ["pt_v23_audit_2014.py", "v23a", "none", "postbull", "0", "edge"]
    pt_path = os.path.join(WORKDIR, "pt_v23_audit_2014.py")
    # Trục NHẠY CẢM phụ (không thuộc họ N_trials chính): rút cửa sổ fill của book LAG từ 5
    # phiên (mặc định engine) xuống N phiên để mô phỏng SÁT luật live "hết phiên 3 ⇒
    # WINDOW_PASSED". Chỉ đụng LIQ_LAG ⇒ BAL/CAPIT giữ nguyên 5.
    fd = os.environ.get("EXPA_LAG_FILLDAYS", "").strip()
    try:
        if fd:
            src = open(pt_path, encoding="utf-8").read()
            old = 'LIQ_LAG = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,'
            if src.count(old) != 1:
                raise RuntimeError("không tìm thấy đúng 1 chuỗi neo LIQ_LAG trong pt_v23")
            src = src.replace(old, old.replace('"max_fill_days": 5,', f'"max_fill_days": {int(fd)},'))
            print(f"[EXPA] LAG max_fill_days -> {int(fd)}", flush=True)
            g = {"__name__": "__main__", "__file__": pt_path, "__builtins__": __builtins__}
            exec(compile(src, pt_path + " [EXPA-filldays]", "exec"), g)
        else:
            runpy.run_path(pt_path, run_name="__main__")
    finally:
        print(f"[EXPA] stats: {mod._EXPA_STATS}", flush=True)


if __name__ == "__main__":
    main()

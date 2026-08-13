#!/usr/bin/env python3
"""oshares_wire_selfcheck.py — kiểm ĐIỂM NỐI, không kiểm lại `oshares_pit` (đã có selfcheck riêng).

Hai điểm được nối ngày 2026-08-13 (job `Taylor_20260813_125526`):
  Việc A — `custom30_core_select_audit.py`: số CP cap-weight tại 48 ngày rebal (LỊCH SỬ).
  Việc B — `rating_8l.py::_reconcile_oshares`: số CP nuôi `ps`/`sales_yield` (SỐNG, chạy 17:45 ICT).

Cái phải chứng minh ở đây không phải "chính sách rẽ đúng nhánh" (đó là việc của
`oshares_pit._selfcheck`) mà là **điểm nối không làm hỏng script chủ**: một phiên chấm rating
KHÔNG được chết, và KHÔNG được đổi số, chỉ vì lớp đối soát này gặp sự cố.

Chạy: python3 oshares_wire_selfcheck.py        (hermetic — KHÔNG chạm BQ)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")            # §5b

FAILS, RAN = [], []


def check(name, cond, detail=""):
    RAN.append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def main() -> int:
    import pandas as pd

    import rating_8l as R

    BASE = {"ticker": ["FPT", "MBB", "VNM", "NOFB"],
            "OShares": [1_714_326_422.0, 8_860_499_900.0, 2_089_955_445.0, float("nan")]}

    def fresh():
        return pd.DataFrame(BASE)

    orig_bq = R.bq
    R.bq = lambda _sql: pd.DataFrame({"asof": ["2026-08-13"]})

    print("== Việc B — điểm nối trong rating_8l.main() ==")
    try:
        # (1) CÔNG TẮC TẮT: phải là no-op TUYỆT ĐỐI, kể cả cột NaN.
        os.environ["OSHARES_RECONCILE"] = "0"
        off = R._reconcile_oshares(fresh())
        check("W1. OSHARES_RECONCILE=0 ⇒ cột OShares không đổi một đồng (đường rollback)",
              off["OShares"].fillna(-1).tolist() == fresh()["OShares"].fillna(-1).tolist())
        os.environ["OSHARES_RECONCILE"] = "1"

        # (2) HAI NGUỒN KHỚP ⇒ baseline không đổi. Đây là ca ĐỐI CHỨNG user yêu cầu cho Việc B.
        import oshares_pit as P
        real_at = P.oshares_at
        P.oshares_at = lambda tks, asof, _cache=None: {
            t: {"value": v, "method": "AIS_EXACT", "anchor_source": "ticker_financial"}
            for t, v in zip(BASE["ticker"], BASE["OShares"]) if t in tks and v == v}
        try:
            same = R._reconcile_oshares(fresh())
        finally:
            P.oshares_at = real_at
        check("W2. ĐỐI CHỨNG: hai nguồn TRÙNG KHỚP ⇒ OShares y hệt baseline",
              same["OShares"].fillna(-1).tolist() == fresh()["OShares"].fillna(-1).tolist(),
              str(same["OShares"].tolist()))

        # (3) LỆCH LỚN ⇒ vẫn phải là baseline (fail-safe). Nếu ca này đổi số thì wrapper đang
        #     LÀM ĐÚNG cái mà nó được dặn KHÔNG làm trong đợt burn-in.
        P.oshares_at = lambda tks, asof, _cache=None: {
            t: {"value": v * 1.15, "method": "ISS_ESTIMATE", "anchor_source": "ticker_financial"}
            for t, v in zip(BASE["ticker"], BASE["OShares"]) if t in tks and v == v}
        try:
            div = R._reconcile_oshares(fresh())
        finally:
            P.oshares_at = real_at
        check("W3. hai nguồn LỆCH 15% ⇒ VẪN là số bq_admin (không có mã nào bị đẩy lên +15%)",
              div["OShares"].fillna(-1).tolist() == fresh()["OShares"].fillna(-1).tolist(),
              str(div["OShares"].tolist()))

        # (4) TOÀN PHẦN: lớp đối soát nổ ⇒ phiên chấm rating vẫn chạy, số giữ nguyên.
        def boom(*_a, **_k):
            raise RuntimeError("oshares_pit sập giả lập")

        P.oshares_at = boom
        try:
            crashed = R._reconcile_oshares(fresh())
        finally:
            P.oshares_at = real_at
        check("W4. oshares_at NÉM LỖI ⇒ _reconcile_oshares không ném, OShares giữ nguyên",
              crashed["OShares"].fillna(-1).tolist() == fresh()["OShares"].fillna(-1).tolist())

        # (5) BQ hỏng ngay ở bước hỏi ngày dữ liệu ⇒ cũng phải nuốt.
        R.bq = boom
        nodate = R._reconcile_oshares(fresh())
        check("W5. không hỏi được ngày dữ liệu (bq lỗi) ⇒ trả df nguyên vẹn, không ném",
              nodate["OShares"].fillna(-1).tolist() == fresh()["OShares"].fillna(-1).tolist())
        R.bq = lambda _sql: pd.DataFrame({"asof": ["2026-08-13"]})

        # (6) BẤT BIẾN SỐNG CÒN: mã đang CÓ số nền thì sau đối soát KHÔNG BAO GIỜ được thành NaN.
        #     Mất OShares ⇒ ps=NaN ⇒ mã rơi khỏi trục sales_yield — một "cải tiến an toàn" mà
        #     lại làm mất phủ thì tệ hơn hiện trạng.
        P.oshares_at = lambda tks, asof, _cache=None: {}      # nguồn mới im lặng trả rỗng
        try:
            silent = R._reconcile_oshares(fresh())
        finally:
            P.oshares_at = real_at
        base_ok = [t for t, v in zip(BASE["ticker"], BASE["OShares"]) if v == v]
        got = dict(zip(silent["ticker"], silent["OShares"]))
        check("W6. nguồn mới im lặng ⇒ không mã nào đang có số bị mất số",
              all(got[t] == t_v for t, t_v in
                  zip(base_ok, [v for v in BASE["OShares"] if v == v])),
              str(got))

        # (7) CHỨNG MINH NGƯỢC: nếu KHÔNG có cổng nào thì số THẬT SỰ đổi được — nếu ca này cũng
        #     "không đổi" thì 6 ca trên chỉ đang chứng minh cái đường ống bị tắc.
        P.oshares_at = lambda tks, asof, _cache=None: {
            t: {"value": v * 1.0005, "method": "AIS_EXACT", "anchor_source": "ticker_financial"}
            for t, v in zip(BASE["ticker"], BASE["OShares"]) if t in tks and v == v}
        try:
            moved = R._reconcile_oshares(fresh())
        finally:
            P.oshares_at = real_at
        check("W7. CHỨNG MINH NGƯỢC: lệch 0,05% (TRONG ngưỡng) ⇒ số THẬT SỰ nhích sang nguồn mới",
              moved["OShares"].iloc[0] != fresh()["OShares"].iloc[0]
              and abs(moved["OShares"].iloc[0] / fresh()["OShares"].iloc[0] - 1 - 0.0005) < 1e-9,
              f"{fresh()['OShares'].iloc[0]:,.0f} -> {moved['OShares'].iloc[0]:,.0f}")
    finally:
        R.bq = orig_bq
        os.environ["OSHARES_RECONCILE"] = "1"

    print("== Việc A — điểm nối trong custom30_core_select_audit.py ==")
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "custom30_core_select_audit.py"), encoding="utf-8").read()
    check("A1. có gọi oshares_pit và CHỈ ghi đè mcap tại exec date (không đụng chuỗi giá)",
          "from oshares_pit import" in src
          and "mcap[t][_ed] = pxw_d[t][_ed] * r[\"value\"]" in src
          and "cls[t][_ed]" not in src)
    check("A2. bỏ qua khi không có số (r['value'] is None) thay vì ghi NaN vào mcap",
          'if r["value"] is None: continue' in src)
    check("A3. leg RETURN (`cls`, adjusted Close) KHÔNG bị đụng — chỉ leg WEIGHT đổi",
          src.count("cls = {t:dict(zip(g.time,g.Close.astype(float)))") == 1)

    # §5b — selfcheck này vừa chạy _reconcile_oshares 6 lần; nếu append_log không bị chặn thì
    # 6 dòng TEST đã nằm trong chính file mà đợt burn-in dùng để đếm tần suất thật.
    print("== §5b — selfcheck KHÔNG được ghi vào sổ đối soát thật ==")
    import oshares_pit as P
    n_after = 0
    if os.path.exists(P.LOG_PATH):
        with open(P.LOG_PATH, encoding="utf-8") as fh:
            n_after = sum(1 for ln in fh if ",rating_8l,2026-08-13," in ln
                          and ",4," in ln)          # n=4 = universe dựng tay của file này
    check("Z1. MIKE_BOT_TEST_MODE=1 ⇒ append_log không ghi dòng nào của selfcheck",
          os.environ.get("MIKE_BOT_TEST_MODE") == "1"
          and P.append_log("selfcheck", "2026-08-13", {"n": 4}) is None
          and n_after == 0, f"dòng test tìm thấy: {n_after}")

    print()
    if FAILS:
        print(f"FAILED {len(FAILS)}/{len(RAN)}: {FAILS}")
        return 1
    print(f"OK — oshares_wire selfcheck PASS {len(RAN)}/{len(RAN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

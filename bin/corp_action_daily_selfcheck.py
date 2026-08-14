#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""corp_action_daily_selfcheck.py — bộ hồi quy cho CODE MỚI của `corp_action_daily.py`.

PHẠM VI (§23 coding_guidelines): chỉ kiểm phần MỚI — cổng selfcheck, cổng freshness, bất biến
số học, đối soát chéo, lịch trigger, cảnh báo proactive, ghi snapshot. **KHÔNG** kiểm lại
`oshares_at`/`_roll`/`bq_corp_action`: chúng đã có bộ hồi quy riêng và đã qua quant-skeptic; chạy
lại ở đây chỉ tạo cảm giác an toàn kép mà không thêm thông tin. Điều file này DÙNG của chúng là
tính chất point-in-time, và nó dùng qua `_cache` dựng tay nên không chạm BQ.

HERMETIC — CỐ Ý. Không BQ, không Discord, không Telegram, không đọc file production. Mọi cổng đều
nhận được điểm bơm (`runner=`, `fresh=`, `rows=`, `nav_glob=`, `state_path=`) nên một hôm BQ hỏng
vẫn phải chạy được bộ này. Cái giá: cổng selfcheck THẬT (chạy 2 module nền, có gọi BQ) chỉ được
kiểm ở tầng "xử lý rc đúng chưa"; hành vi thật của nó thuộc về chính hai module đó.

MỖI CA CHẶN ĐỀU CÓ CA CHỨNG MINH NGƯỢC. "Cổng bắt được X" một mình không có giá trị — cổng
`return False` cũng bắt được mọi thứ. Nên mỗi ca chặn đi kèm một ca hợp lệ phải LỌT (ví dụ INV1
lọt vs INV2 chặn), và ca INV3 chứng minh rằng nếu KHÔNG đổi tên khoá sự kiện thì cổng bất biến
sẽ mù hoàn toàn — đó là một bug thật đã tồn tại trong bản nháp của chính file này.

Usage: python3 mike/bin/corp_action_daily_selfcheck.py [--no-subprocess]
"""
from __future__ import annotations

import datetime as dt
import inspect
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"))

import corp_action_daily as cad                                      # noqa: E402
from oshares_live import _roll                                       # noqa: E402

FAILS, RAN = [], []


def check(name, cond, detail=""):
    RAN.append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


# ─────────────────────────────────────────────────────────────────── fixtures

def _ais(tk, eff, total):
    return {"ticker": tk, "event_code": "AIS", "exright_date": None, "effective_date": eff,
            "exercise_ratio": None, "issue_method_name_vi": None, "shares_delta": None,
            "shares_total_after": total, "title": f"AIS {tk} {eff}"}


def _iss(tk, ex, ratio, method="Cổ phiếu thưởng"):
    return {"ticker": tk, "event_code": "ISS", "exright_date": ex, "effective_date": None,
            "exercise_ratio": ratio, "issue_method_name_vi": method, "shares_delta": None,
            "shares_total_after": None, "title": f"ISS {tk} {ex}"}


def _q(tk, time, shares):
    return {"ticker": tk, "time": time, "OShares": shares}


# AAA: sạch — AIS đầu năm, thưởng 15% ex 06-10, dòng quý 04-01 GIẢI THÍCH ĐƯỢC.
# BBB: hình dạng HAH — dòng quý 2026-02-02 mang số của AIS 2026-05-27 (RESTATE / look-ahead).
# CCC: chuyển đổi TP ratio 0,0 ⇒ mô hình fail-closed, không có số để đối soát.
CACHE = (
    [_q("AAA", "2026-04-01", 100_000_000), _q("BBB", "2026-02-02", 185_840_401),
     _q("CCC", "2026-04-01", 100_000_000)],
    [_ais("AAA", "2026-01-05", 100_000_000), _iss("AAA", "2026-06-10", 0.15),
     _ais("BBB", "2025-09-09", 168_861_212), _ais("BBB", "2026-05-27", 185_840_401),
     _ais("CCC", "2026-01-05", 100_000_000),
     _iss("CCC", "2026-03-20", 0.0, "Chuyển từ trái phiếu chuyển đổi")],
)


# ─────────────────────────────────────────────── LỚP 3 · cổng selfcheck xử lý rc

def t_gate_selfcheck():
    print("== LỚP 3 · cổng selfcheck (chạy TRƯỚC publish) ==")

    class R:
        def __init__(self, rc):
            self.returncode, self.stdout, self.stderr = rc, f"rc={rc}\nOK dòng cuối", ""

    ok, det = cad.gate_selfcheck(runner=lambda p: R(0))
    check("SC1. cả 2 module PASS ⇒ cổng mở", ok and len(det) == 2, str([d["rc"] for d in det]))

    ok, det = cad.gate_selfcheck(runner=lambda p: R(1 if "oshares" in p else 0))
    check("SC2. 1 module FAIL ⇒ cổng ĐÓNG, và nêu ĐÍCH DANH module nào",
          (not ok) and [d["module"] for d in det if d["rc"] != 0] == ["oshares_live"],
          str([(d["module"], d["rc"]) for d in det]))

    def boom(_p):
        raise RuntimeError("interpreter chết")

    ok, det = cad.gate_selfcheck(runner=boom)
    check("SC3. selfcheck KHÔNG CHẠY ĐƯỢC ⇒ cổng ĐÓNG (không coi 'không lỗi' là 'đã pass')",
          (not ok) and all(d["rc"] == 99 for d in det), str([d["rc"] for d in det]))


# ─────────────────────────────────────────── LỚP 5 · freshness + chống alert-fatigue

def t_freshness():
    print("== LỚP 5 · freshness của chính bảng corporate_action ==")
    REAL = {"max_ingested": "2026-08-12 15:48:52.141570+00", "max_public": "2026-08-12",
            "n": "36149"}

    st, d = cad.gate_freshness("2026-08-13", fresh=REAL)
    check("F1. lô nạp THẬT 08-12 22:48 ICT, hỏi ngày 08-13 (T5) ⇒ FRESH "
          "(mốc là phiên TRƯỚC, không phải 'hôm nay' — vendor nạp buổi tối)",
          st == "FRESH" and d["prev_trading_day"] == "2026-08-12", f"{st} {d.get('reason','')}")

    st, d = cad.gate_freshness("2026-08-14", fresh=REAL)
    check("F2. cùng lô đó, sang 08-14 (T6) ⇒ STALE (đã lỡ phiên 08-13)",
          st == "STALE" and d["age_days"] == 2, f"{st} age={d.get('age_days')}")

    fri = {"max_ingested": "2026-08-14 15:48:52+00", "max_public": "2026-08-14", "n": "1"}
    st, d = cad.gate_freshness("2026-08-17", fresh=fri)     # T2
    check("F3. nạp tối T6, hỏi sáng T2 ⇒ FRESH — cuối tuần KHÔNG được đẻ báo động giả",
          st == "FRESH" and d["prev_trading_day"] == "2026-08-14", f"{st} {d.get('reason','')}")

    st, d = cad.gate_freshness("2026-08-19", fresh=REAL)
    check("F4. cũ 7 ngày (> ngưỡng 5) ⇒ DEAD — 'refresh hàng ngày' không còn đúng",
          st == "DEAD" and d["age_days"] == 7, f"{st} age={d.get('age_days')}")

    st, d = cad.gate_freshness("2026-08-13", fresh={"max_ingested": None})
    check("F5. max_ingested rỗng/hỏng ⇒ DEAD (fail-closed, KHÔNG đoán là tươi)", st == "DEAD",
          f"{st} {d.get('reason','')}")

    # ranh giới TZ: 18:30 UTC = 01:30 ICT NGÀY HÔM SAU. Nếu ai đó so ngày trên chuỗi UTC thô thì
    # ca này ra 08-12 và bị xếp STALE oan. Phải thấy 08-13.
    st, d = cad.gate_freshness("2026-08-13",
                               fresh={"max_ingested": "2026-08-12 18:30:00+00"})
    check("F6. 18:30 UTC = 01:30 ICT HÔM SAU ⇒ ngày ICT phải là 2026-08-13, không phải 08-12",
          st == "FRESH" and d["max_ingested_ict"].startswith("2026-08-13"),
          f"{st} ict={d.get('max_ingested_ict')}")

    with tempfile.TemporaryDirectory() as tmp:
        sp = os.path.join(tmp, "state.json")
        a = cad.stale_streak("2026-08-14", "STALE", "sig-1", state_path=sp)
        b = cad.stale_streak("2026-08-17", "STALE", "sig-1", state_path=sp)
        c = cad.stale_streak("2026-08-18", "STALE", "sig-2", state_path=sp)
        e = cad.stale_streak("2026-08-19", "FRESH", "sig-3", state_path=sp)
        check("F7. chuỗi im lặng: cùng chữ ký thì cộng dồn (1→2), feed nhúc nhích thì reset (→1), "
              "FRESH thì về 0", (a, b, c, e) == (1, 2, 1, 0), str((a, b, c, e)))


# ─────────────────────────────────────────────────── LỚP 4 · bất biến số học

def t_invariants():
    print("== LỚP 4 · bất biến số CP (kỳ vọng = số hôm qua ĐÃ LĂN sự kiện, không phải %/ngày) ==")
    EV = [{"exright_date": "2026-06-10", "method_vi": "Cổ phiếu thưởng", "title": "t",
           "ratio": 0.15, "shares_delta": None, "applied_via": "exercise_ratio",
           "applied_size": 0.15}]
    prev = {"tickers": {"AAA": {"value": 100_000_000}}}

    v = cad.check_invariants("2026-06-10", {"AAA": {"value": 115_000_000, "events_applied": EV}},
                             "2026-06-09", prev)
    check("INV1. +15% CÓ đợt thưởng 15% giải thích ⇒ KHÔNG vi phạm (ca chứng minh ngược: cổng "
          "không chặn bừa mọi cú nhảy)", v == [], str(v))

    v = cad.check_invariants("2026-06-10", {"AAA": {"value": 130_000_000, "events_applied": EV}},
                             "2026-06-09", prev)
    check("INV2. +30% mà sự kiện chỉ giải thích được +15% ⇒ UNEXPLAINED_JUMP",
          len(v) == 1 and v[0]["kind"] == "UNEXPLAINED_JUMP"
          and abs(v[0]["expected"] - 115_000_000) < 1, str(v))

    # ── hồi quy bug THẬT của bản nháp: `_event_dict` xuất ratio dưới tên `ratio`, `_roll` đọc
    # `exercise_ratio`. Không đổi tên ⇒ mọi sự kiện thành blocker ⇒ INV2 lặng lẽ trả rỗng.
    _val, _ap, blockers_raw = _roll(100_000_000, EV)
    _val2, _ap2, blockers_fixed = _roll(100_000_000, [cad._as_roll_event(e) for e in EV])
    check("INV3. CHỨNG MINH NGƯỢC: đưa thẳng dict đã-áp vào _roll ⇒ 1 blocker (cổng sẽ MÙ); "
          "qua _as_roll_event ⇒ 0 blocker và ra đúng 115.000.000",
          len(blockers_raw) == 1 and not blockers_fixed and abs(_val2 - 115_000_000) < 1,
          f"raw_blockers={len(blockers_raw)} fixed={_val2:,.0f}")

    v = cad.check_invariants("2026-06-10", {"AAA": {"value": 95_000_000, "events_applied": []}},
                             "2026-06-09", prev)
    check("INV4. số CP GIẢM 5% không sự kiện nào giải thích ⇒ UNEXPLAINED_DROP (mua lại CP quỹ "
          "không có mã sự kiện trong bảng ⇒ phải người xem)",
          len(v) == 1 and v[0]["kind"] == "UNEXPLAINED_DROP", str(v))

    v = cad.check_invariants(
        "2025-09-12", {"FPT": {"value": 1_703_507_121, "events_applied": []}}, "2025-09-11",
        {"tickers": {"FPT": {"value": 1_703_529_640}}})
    check("INV5. ca THẬT FPT: ước lượng 1.703.529.640 nhường chỗ số đo 1.703.507.121 (−0,0013%) "
          "⇒ KHÔNG vi phạm (nếu không thì mỗi lần AIS về là một báo động giả)", v == [], str(v))

    blk = [{"exright_date": "2026-06-10", "method_vi": "Phát hành riêng lẻ", "title": "t",
            "ratio": None, "shares_delta": None}]
    v = cad.check_invariants("2026-06-10", {"AAA": {"value": 130_000_000, "events_applied": blk}},
                             "2026-06-09", prev)
    check("INV6. sự kiện KHÔNG có tỉ lệ ⇒ không dựng được kỳ vọng ⇒ KHÔNG kết luận (im lặng có "
          "chủ đích, khác với 'đã kiểm và sạch')", v == [], str(v))

    v = cad.check_invariants("2026-06-10", {"ZZZ": {"value": 1, "events_applied": []}},
                             "2026-06-09", prev)
    v += cad.check_invariants("2026-06-10", {"AAA": {"value": 1, "events_applied": []}},
                              "2026-06-09", {"tickers": {"AAA": {"value": None}}})
    check("INV7. mã mới xuất hiện / số hôm qua là None ⇒ bỏ qua, KHÔNG dựng vi phạm giả",
          v == [], str(v))

    check("INV8. ranh giới systemic: 1/5 và 2/5 là lẻ tẻ, 3/5 là diện rộng (sàn cứng 3 mã)",
          (cad.is_systemic(1, 5), cad.is_systemic(2, 5), cad.is_systemic(3, 5)) == (False, False, True))
    check("INV9. ranh giới systemic theo tỉ lệ: 5/100 chưa, 6/100 rồi (5%+1)",
          (cad.is_systemic(5, 100), cad.is_systemic(6, 100)) == (False, True))
    check("INV10. 0 vi phạm không bao giờ là systemic (kể cả n_cmp=0)",
          not cad.is_systemic(0, 0) and not cad.is_systemic(0, 100))
    # ca thật probe ACB: 1 mã sinh 2 vi phạm (JUMP + RETRO). Đếm theo DÒNG thì 2 mã hỏng đã đủ
    # 4 dòng ⇒ vượt sàn 3 ⇒ gọi nhầm là "feed hỏng diện rộng" và khoá cả ngày.
    viol2 = [{"ticker": t, "kind": k} for t in ("ACB", "BID")
             for k in ("UNEXPLAINED_JUMP", "RETRO_CHANGE")]
    n_tk, n_row = len({v["ticker"] for v in viol2}), len(viol2)
    check("INV10b. đếm theo MÃ chứ không theo DÒNG: 2 mã × 2 loại = 4 DÒNG sẽ vượt sàn 3 và khoá "
          "oan cả ngày; đếm 2 MÃ thì không",
          not cad.is_systemic(n_tk, 29) and cad.is_systemic(n_row, 29),
          f"n_ma={n_tk} (không systemic) vs n_dong={n_row} (systemic nếu đếm sai)")

    with tempfile.TemporaryDirectory() as tmp:
        sp = os.path.join(tmp, "s.json")
        old = cad.STATE_PATH
        try:
            cad.STATE_PATH = sp
            cad.stale_streak("2026-08-14", "STALE", "sig", state_path=None)
            check("INV13. gán `cad.STATE_PATH` trong probe PHẢI có tác dụng (mặc định phân giải "
                  "trong thân hàm) — nếu không, probe lặng lẽ ghi đè state production",
                  os.path.exists(sp) and not os.path.exists(old + ".probe-leak"),
                  f"đã ghi {os.path.basename(sp)}")
        finally:
            cad.STATE_PATH = old

    cur = {"AAA": {"value": 130_000_000}, "BBB": {"value": 5}}
    cad.withhold_suspect(cur, [{"ticker": "AAA", "kind": "UNEXPLAINED_JUMP"}])
    check("W1. vi phạm lẻ tẻ ⇒ GIẤU số của riêng mã đó (value=None, nhãn INVARIANT_SUSPECT, số "
          "gốc lưu lại để đối chiếu); mã sạch KHÔNG bị đụng",
          cur["AAA"]["value"] is None and cur["AAA"]["method"] == "INVARIANT_SUSPECT"
          and cur["AAA"]["value_withheld"] == 130_000_000 and cur["BBB"] == {"value": 5},
          str(cur))

    cur = {"AAA": {"value": 130_000_000}}
    cad.withhold_suspect(cur, [{"ticker": "AAA", "kind": "UNEXPLAINED_JUMP"},
                               {"ticker": "AAA", "kind": "RETRO_CHANGE"}])
    check("W2. MỘT mã dính HAI vi phạm (ca thật probe ACB) ⇒ `value_withheld` vẫn là SỐ GỐC, "
          "không phải None của vòng trước; cả hai vi phạm được GOM chứ không đè nhau",
          cur["AAA"]["value_withheld"] == 130_000_000
          and [v["kind"] for v in cur["AAA"]["invariant_violations"]]
          == ["UNEXPLAINED_JUMP", "RETRO_CHANGE"], str(cur["AAA"]))

    cad.withhold_suspect({}, [{"ticker": "KHONGCO", "kind": "X"}])
    check("W3. vi phạm trỏ tới mã không có trong kết quả ⇒ bỏ qua, không nổ", True)

    # RETRO: hôm qua công bố 100.000.000 cho AAA tại 2026-06-09; feed hôm nay tính lại ra
    # 115.000.000 cho CHÍNH ngày đó ⇒ lịch sử vừa bị viết lại.
    r = cad.check_retro("2026-06-11", "2026-06-11", {"tickers": {"AAA": {"value": 100_000_000}}},
                        CACHE, {"AAA"})
    check("INV11. RETRO_CHANGE: tính lại quá khứ bằng feed hôm nay ra số khác đã công bố ⇒ báo",
          len(r) == 1 and r[0]["kind"] == "RETRO_CHANGE"
          and abs(r[0]["recomputed_now"] - 115_000_000) < 1, str(r))
    r = cad.check_retro("2026-06-11", "2026-06-09", {"tickers": {"AAA": {"value": 100_000_000}}},
                        CACHE, {"AAA"})
    check("INV12. quá khứ KHỚP ⇒ im lặng (chứng minh ngược cho INV11)", r == [], str(r))


# ────────────────────────────────────────────────────── LỚP 2 · đối soát chéo

def t_crosscheck():
    print("== LỚP 2 · đối soát corp-action ↔ ticker_financial.OShares (KHÔNG tự chọn số) ==")
    d = cad.crosscheck("2026-08-13", {"AAA"}, CACHE)
    check("X1. hai nguồn khớp tại ngày dòng quý ⇒ không báo (chứng minh ngược: không phải cái gì "
          "cũng lệch)", d == [], str(d))

    # MẪU SỐ là `ticker_financial` (số bị nghi RESTATE), nên 16.979.189/185.840.401 = 9,14% —
    # KHÔNG phải 10,05% mà docstring của `oshares_live` nêu (nó chia cho 168.861.212). Cùng một
    # sự kiện, hai mẫu số; ghi rõ ở đây vì trích nhầm con số giữa hai file là chuyện dễ xảy ra.
    d = cad.crosscheck("2026-08-13", {"BBB"}, CACHE)
    check("X2. dòng quý 2026-02-02 mang số của AIS 2026-05-27 ⇒ DIVERGENT 9,14% (mẫu số = số "
          "ticker_financial), và NÊU CẢ HAI SỐ + lý do của cổng giải thích",
          len(d) == 1 and d[0]["kind"] == "DIVERGENT"
          and abs(d[0]["err_pct_vs_ticker_financial"] - 9.136) < 0.01
          and d[0]["ticker_financial"] == 185_840_401 and d[0]["oshares_live"] == 168_861_212
          and bool(d[0]["explain_gate_reasons"]),
          f"{d[0]['err_pct_vs_ticker_financial']:.2f}% "
          f"lý do={bool(d[0]['explain_gate_reasons'])}" if d else "rỗng")

    check("X2b. tên trường MANG THEO MẪU SỐ (`err_pct_vs_ticker_financial`), không có `err_pct` "
          "trung tính — hai file chia cho hai mẫu số khác nhau cho cùng một sự kiện",
          "err_pct" not in d[0] and "err_pct_vs_ticker_financial" in d[0], str(sorted(d[0])))

    check("X3. đối soát KHÔNG chứa trường nào kiểu 'số đúng là' — script không được phán",
          all(not any(k in r for k in ("correct", "chosen", "winner"))
              for r in cad.crosscheck("2026-08-13", {"AAA", "BBB", "CCC"}, CACHE)))

    d = cad.crosscheck("2026-08-13", {"CCC"}, CACHE)
    check("X4. mô hình fail-closed (chuyển đổi TP ratio 0,0) ⇒ NO_MODEL_VALUE, KHÔNG suy ra dòng "
          "quý sai", len(d) == 1 and d[0]["kind"] == "NO_MODEL_VALUE"
          and d[0]["oshares_live"] is None, str(d))

    d = cad.crosscheck("2026-08-13", {"KHONGCO"}, CACHE)
    check("X5. mã không có dòng quý nào ⇒ bỏ qua im lặng, không dựng lệch giả", d == [], str(d))


# ──────────────────────────── LỚP 2b · CHUỖI HIỂN THỊ thật của dòng cảnh báo Discord

def t_render_divergence():
    """Kiểm CHUỖI người đọc thật sự nhìn thấy, không phải trường trong dict.

    Vì sao tách riêng khỏi `t_crosscheck`: ca X4 đã kiểm `oshares_live is None` và PASS trong khi
    dòng Discord vẫn in "corp-action 0 … (0,00%)". Một `None` đúng trong dict KHÔNG chứng minh
    gì về chuỗi render — giữa hai cái có một `or 0`. Bug thật (TCB, 2026-08-13, mã đang giữ ở cả
    hai tài khoản) sống đúng trong khoảng hở đó suốt các vòng trước.
    """
    print("== LỚP 2b · chuỗi hiển thị Discord cho đối soát Oshares ==")
    tcb = {"ticker": "TCB", "at": "2026-07-21", "ticker_financial": 7_086_240_414.0,
           "oshares_live": None, "kind": "NO_MODEL_VALUE", "method": "AIS_UNCERTIFIED",
           "note": "..."}
    evf = {"ticker": "EVF", "at": "2026-07-21", "ticker_financial": 760_565_802.0,
           "oshares_live": 704_248_289.0, "err_pct_vs_ticker_financial": 7.404686,
           "kind": "DIVERGENT", "model_method": "AIS_EXACT"}

    # dấu phân cách là DẤU PHẨY (`:,.0f`) — quy ước sẵn có của cả file này, không đổi ở đây (§3).
    s = cad._fmt_divergence([tcb])
    check("R1. NO_MODEL_VALUE KHÔNG BAO GIỜ in ra một con số cho corp-action — chuỗi phải nói "
          "TỪ CHỐI + nêu nhãn phương pháp + vẫn nêu số bq_admin để người đọc biết đang thiếu gì",
          "TỪ CHỐI trả số" in s and "AIS_UNCERTIFIED" in s and "7,086,240,414" in s, s)
    check("R2. CA CHỨNG MINH NGƯỢC — chính là bug đã ship: chuỗi KHÔNG được chứa 'corp-action 0' "
          "lẫn '(0,00%)' (khuôn cũ in đúng hai mảnh đó cho TCB)",
          "corp-action 0" not in s and "0,00%" not in s and "0.00%" not in s, s)
    check("R3. DIVERGENT vẫn in ĐỦ hai số + sai số đúng mẫu số (không hồi quy phần đang chạy)",
          "704,248,289" in (t := cad._fmt_divergence([evf])) and "760,565,802" in t
          and "7.40%" in t, t)

    s2 = cad._fmt_divergence([evf, tcb])
    check("R4. hai loại ĐẾM RIÊNG ở đầu dòng — '1 mã LỆCH + 1 mã KHÔNG đối soát được', không "
          "gộp thành '2 mã lệch'",
          "1 mã LỆCH" in s2 and "1 mã KHÔNG đối soát được" in s2 and "2 mã LỆCH" not in s2, s2)
    # so KHÔNG PHÂN BIỆT HOA/THƯỜNG: bản trước grep đúng chữ "LỆCH" viết hoa nên tiêu đề cũ
    # "**Lệch nguồn Oshares**" lọt qua PASS oan — ca này tự nó chẳng chứng minh gì.
    # (quant-skeptic vòng 5, mục residual 3.)
    check("R5. chỉ có NO_MODEL_VALUE ⇒ đầu dòng KHÔNG được nói 'lệch' ở BẤT KỲ kiểu chữ nào "
          "(không có mã nào lệch)",
          "lệch" not in cad._fmt_divergence([tcb]).lower(), s)
    check("R6. rỗng ⇒ None (không đẻ dòng trống)", cad._fmt_divergence([]) is None)
    check("R7. quá `limit` ⇒ nói rõ còn bao nhiêu mã nữa, không im lặng cắt cụt (§'no silent "
          "caps')", "… và 2 mã nữa" in cad._fmt_divergence([evf] * 5, limit=3),
          cad._fmt_divergence([evf] * 5, limit=3)[-40:])

    # phòng thủ: bản ghi thiếu `kind` nhưng `oshares_live` là None vẫn phải đi nhánh TỪ CHỐI —
    # không được rơi về khuôn số rồi nổ `TypeError` hay in "0".
    bare = {"ticker": "XXX", "at": "2026-07-21", "ticker_financial": 1_000.0,
            "oshares_live": None}
    check("R8. thiếu `kind` mà `oshares_live` None ⇒ vẫn đi nhánh TỪ CHỐI, không nổ, không in 0 "
          "— VÀ đầu dòng đếm nó là 'KHÔNG đối soát được', không phải 'LỆCH' (một vị ngữ dùng "
          "chung cho cả đầu dòng lẫn thân dòng; hai vị ngữ khác nhau đã cho một dòng tự mâu "
          "thuẫn ở bản nháp)",
          "TỪ CHỐI trả số" in (b := cad._fmt_divergence([bare])) and "corp-action 0" not in b
          and "1 mã KHÔNG đối soát được" in b and "LỆCH" not in b, b)

    # R10 mở rộng đúng fixture `bare` của R8 sang tầng LOG/BUS. R8 chỉ khoá được chuỗi Discord;
    # `run()` lại đếm `n_crosscheck_no_model_value` bằng vị ngữ chỉ-theo-`kind` của riêng nó, tức
    # khiếm khuyết R8 dời sang tầng khác — bus có thể nói "0 mã không đối soát được" trong khi
    # dòng Discord ngay dưới nói "1 mã". (quant-skeptic vòng 5, killer_objection.)
    n_bus = sum(1 for d in [bare] if cad.refused(d))     # đúng biểu thức `run()` dùng
    src = inspect.getsource(cad)
    check("R10. bản ghi THIẾU `kind`: đếm ở ĐẦU DÒNG == đếm ở BUS/LOG == nội dung THÂN DÒNG — và "
          "vị ngữ chỉ được VIẾT MỘT LẦN trong cả module (`refused`), không ai được cài lại bản "
          "chỉ-theo-`kind` ở tầng log/bus",
          n_bus == 1 and "1 mã KHÔNG đối soát được" in b and "TỪ CHỐI trả số" in b
          and src.count('== "NO_MODEL_VALUE"') == 1,
          f"n_bus={n_bus}, số bản sao vị ngữ={src.count('== ' + chr(34) + 'NO_MODEL_VALUE' + chr(34))}, "
          f"đầu dòng={b[:60]}")

    # R11: bản ghi DIVERGENT MÉO (thiếu trường sai số). Bản trước dùng `d[...]` ⇒ `KeyError` nổ
    # giữa luồng cảnh báo hàng ngày và giết luôn phần tin lành lặn của mọi mã khác trong cùng
    # dòng. Không được bịa `0` (đúng cái `or 0` đẻ ra bug TCB) — phải nói "không rõ sai số".
    malformed = {"ticker": "YYY", "at": "2026-07-21", "ticker_financial": 1_000.0,
                 "oshares_live": 900.0, "kind": "DIVERGENT"}
    m = cad._fmt_divergence([evf, malformed])
    check("R11. DIVERGENT thiếu `err_pct_vs_ticker_financial` ⇒ KHÔNG nổ KeyError, KHÔNG in "
          "'0.00%', nói thẳng 'không rõ sai số', và các mã LÀNH cùng dòng vẫn in đủ",
          "không rõ sai số" in m and "0.00%" not in m and "704,248,289" in m and "7.40%" in m, m)

    # ĐẦU-CUỐI: chạy thẳng `crosscheck()` trên fixture CCC (fail-closed thật) rồi render — chứng
    # minh hai đầu KHỚP NHAU, chứ không phải mỗi bên đúng với một hình dạng dict khác nhau.
    real = cad.crosscheck("2026-08-13", {"CCC"}, CACHE)
    check("R9. ĐẦU-CUỐI: bản ghi do chính `crosscheck()` sinh ra, render ra chuỗi TỪ CHỐI (hai "
          "đầu khớp hình dạng dict, không phải fixture tự bịa)",
          real and "TỪ CHỐI trả số" in (r := cad._fmt_divergence(real))
          and "corp-action 0" not in r, str(real))


# ────────────────────────────── LỚP 4b · giám sát DIỄN BIẾN của fail-closed (im lặng)

def t_none_value_watch():
    print("== LỚP 4b · lưới giám sát số mã bị TỪ CHỐI trả số ==")
    def snap(d):
        return {"tickers": {tk: {"value": v} for tk, v in d.items()}}

    prev = snap({"AAA": 1.0, "BBB": None, "CCC": 2.0})
    cur_same = {"AAA": {"value": 1.0, "method": "AIS_EXACT"},
                "BBB": {"value": None, "method": "UNKNOWN_RATIO"},
                "CCC": {"value": 2.0, "method": "AIS_EXACT"}}
    w = cad.none_value_watch(cur_same, prev)
    check("NW1. đứng yên (1→1, cùng mã) ⇒ KHÔNG báo — lưới này báo DIỄN BIẾN, không báo hiện "
          "trạng đã biết", w["alert"] is False and w["delta"] == 0, str(w["delta"]))

    cur_up = dict(cur_same, CCC={"value": None, "method": "AIS_UNCERTIFIED"})
    w = cad.none_value_watch(cur_up, prev)
    check("NW2. TĂNG 1→2 ⇒ BÁO, nêu đích danh mã MỚI + nhãn phương pháp của nó",
          w["alert"] and w["delta"] == 1 and w["newly_none"] == {"CCC": "AIS_UNCERTIFIED"},
          str(w["newly_none"]))

    cur_down = dict(cur_same, BBB={"value": 3.0, "method": "AIS_EXACT"})
    w = cad.none_value_watch(cur_down, prev)
    check("NW3. CA CHỨNG MINH NGƯỢC — GIẢM 1→0 ⇒ KHÔNG báo (feed lành lại không phải sự cố), "
          "nhưng vẫn ghi lại `recovered`",
          w["alert"] is False and w["delta"] == -1 and w["recovered"] == ["BBB"], str(w))

    swap = {"AAA": {"value": None, "method": "NO_ANCHOR"},
            "BBB": {"value": 1.0, "method": "AIS_EXACT"},
            "CCC": {"value": 2.0, "method": "AIS_EXACT"}}
    w = cad.none_value_watch(swap, prev)
    check("NW4. TỔNG ĐỨNG YÊN nhưng ĐỔI MÃ (BBB lành, AAA hỏng) ⇒ VẪN BÁO — đếm tổng một mình "
          "sẽ nuốt mất ca này",
          w["alert"] and w["delta"] == 0 and w["newly_none"] == {"AAA": "NO_ANCHOR"}, str(w))

    w = cad.none_value_watch(cur_up, None)
    check("NW5. chưa có mốc ⇒ CHƯA ĐÁNH GIÁ ĐƯỢC, KHÔNG báo và KHÔNG gọi là 'không tăng' "
          "(cùng kỷ luật với `invariant_evaluated`)",
          w["has_baseline"] is False and w["alert"] is False and w["delta"] is None
          and w["n_none"] == 2, str(w))

    check("NW6. gộp theo nhãn phương pháp để đọc được nguyên nhân, không chỉ con số",
          cad.none_value_watch(cur_up, prev)["by_method"]
          == {"AIS_UNCERTIFIED": ["CCC"], "UNKNOWN_RATIO": ["BBB"]},
          str(cad.none_value_watch(cur_up, prev)["by_method"]))

    # ── xoay vòng track set (`held ∪ ex_today ∪ ais_today` đổi thành viên mỗi ngày)
    # Tái dựng ĐÚNG ca quant-skeptic đo được ở `asof=2026-08-14`: tập từ chối đổi từ
    # {DHN,EVF,SHB,VPB} sang {EVF,HRB,SHB,VPB} — CÙNG SỐ LƯỢNG, khác thành viên, chỉ vì DHN hết
    # ex-right (rời track set) và HRB vào AIS (mới vào track set). Feed không hỏng gì.
    prev_real = {"tickers": {tk: {"value": None} for tk in ("DHN", "EVF", "SHB", "VPB")}}
    prev_real["tickers"].update({tk: {"value": 1.0} for tk in ("FPT", "MBB")})
    cur_real = {tk: {"value": None, "method": "AIS_UNCERTIFIED"}
                for tk in ("EVF", "HRB", "SHB", "VPB")}
    cur_real.update({tk: {"value": 1.0, "method": "AIS_EXACT"} for tk in ("FPT", "MBB")})
    w = cad.none_value_watch(cur_real, prev_real)
    check("NW7. CA THẬT 08-14 — track set xoay vòng (DHN ra, HRB vào) KHÔNG được bắn cảnh báo: "
          "mã mới vào chưa có mốc riêng thì không kết luận được nó 'vừa hỏng', mã rời đi cũng "
          "không phải 'lành lại'",
          w["alert"] is False and w["delta"] == 0 and w["newly_none"] == {}
          and w["recovered"] == [] and sorted(w["entered_none"]) == ["HRB"]
          and w["left_none"] == ["DHN"], str(w))
    check("NW8. …nhưng KHÔNG được vô hình: tổng vẫn nói đúng 4 mã bị từ chối hôm nay, và cơ sở "
          "so sánh (5 mã chung) được công bố tách khỏi tổng",
          w["n_none"] == 4 and w["n_total"] == 6 and w["n_comparable"] == 5
          and w["n_none_cmp"] == 3 and w["n_none_prev_cmp"] == 3, str(w))

    # CA CHỨNG MINH NGƯỢC cho NW7: cùng kiểu xoay vòng, nhưng có MỘT mã CÓ MỐC thật sự hỏng đi.
    # Nếu bộ lọc "tập so được" nuốt luôn ca này thì nó đã che mất chính thứ lưới được dựng để bắt.
    cur_real_bad = dict(cur_real, FPT={"value": None, "method": "NO_ANCHOR"})
    w2 = cad.none_value_watch(cur_real_bad, prev_real)
    check("NW9. CA CHỨNG MINH NGƯỢC — vẫn xoay vòng track set, nhưng FPT (có mốc, hôm qua có số) "
          "mất số ⇒ PHẢI báo, và chỉ nêu đích danh FPT, không nêu HRB",
          w2["alert"] is True and w2["delta"] == 1
          and w2["newly_none"] == {"FPT": "NO_ANCHOR"} and "HRB" not in w2["newly_none"], str(w2))

    # ── hai nguyên nhân của `value is None` không được trộn lời khuyên
    prev_inv = snap({"AAA": 1.0, "BBB": 2.0})
    cur_inv = {"AAA": {"value": None, "method": "INVARIANT_SUSPECT"},
               "BBB": {"value": 2.0, "method": "AIS_EXACT"}}
    w3 = cad.none_value_watch(cur_inv, prev_inv)
    check("NW10. mã bị GIẤU do vi phạm bất biến vẫn ĐƯỢC ĐẾM (không tạo điểm mù dưới ngưỡng "
          "systemic) nhưng được TÁCH NGUYÊN NHÂN ra để lời cảnh báo không chỉ sai hướng 'kiểm "
          "feed'",
          w3["alert"] is True and w3["n_none"] == 1 and w3["n_none_invariant"] == 1
          and w3["by_method"] == {"INVARIANT_SUSPECT": ["AAA"]}, str(w3))

    # ── nguyên nhân thứ BA: mô hình đổi, không phải feed đổi
    # Ca thật 2026-08-14: mốc 08-13 ghi lúc 17:07 ICT, hai commit nâng cổng chứng nhận neo AIS
    # lên lúc 22:15 + 23:08 cùng ngày ⇒ EVF/SHB "mới mất số" hoàn toàn do MÃ đổi (BQ xác nhận
    # không có dòng AIS/ISS mới nào của hai mã đó). Alert vẫn phải bắn (mất số là mất số), nhưng
    # chữ ký phải cho người đọc biết nghi phạm số một là bản vá của chính mình.
    prev_v1 = dict(snap({"AAA": 1.0, "BBB": 2.0}), model_version="aaaa11112222")
    cur_v = {"AAA": {"value": None, "method": "AIS_UNCERTIFIED"},
             "BBB": {"value": 2.0, "method": "AIS_EXACT"}}
    w4 = cad.none_value_watch(cur_v, prev_v1, mv="bbbb33334444")
    check("NW11. mốc do bản mô hình KHÁC sinh ra ⇒ vẫn BÁO (mất số là mất số) nhưng `model_"
          "changed=True` để văn bản chỉ đúng nghi phạm, không đổ cho feed",
          w4["alert"] is True and w4["model_changed"] is True
          and w4["model_version_prev"] == "aaaa11112222", str(w4))
    w5 = cad.none_value_watch(cur_v, prev_v1, mv="aaaa11112222")
    check("NW12. CA CHỨNG MINH NGƯỢC — CÙNG chữ ký mô hình ⇒ `model_changed=False`: lúc đó tăng "
          "số mã bị từ chối MỚI thật sự trỏ về feed/dữ liệu",
          w5["alert"] is True and w5["model_changed"] is False, str(w5))
    w6 = cad.none_value_watch(cur_v, snap({"AAA": 1.0, "BBB": 2.0}), mv="bbbb33334444")
    check("NW13. mốc CŨ chưa ghi chữ ký (mọi snapshot trước 2026-08-14) ⇒ `model_changed=None` = "
          "CHƯA LOẠI TRỪ ĐƯỢC, KHÔNG được tự nhận là 'cùng mô hình'",
          w6["model_changed"] is None and w6["alert"] is True, str(w6))

    # chữ ký phải ĐỔI khi nội dung file mô hình đổi, và ỔN ĐỊNH khi không đổi — nếu không thì
    # `model_changed` chỉ là trang trí.
    v1 = cad.model_version()
    check("NW14. `model_version()` ổn định giữa hai lần gọi liên tiếp (cùng file ⇒ cùng chữ ký)",
          v1 == cad.model_version() and len(v1) == 12, v1)
    import tempfile as _tf
    with _tf.TemporaryDirectory() as td:
        real = cad._model_files()
        fake = os.path.join(td, "oshares_live.py")
        with open(real[-1][1], "rb") as fh:
            body = fh.read()
        with open(fake, "wb") as fh:
            fh.write(body + "\n# một dòng đổi\n".encode())
        orig = cad._model_files
        cad._model_files = lambda: real[:-1] + [("oshares_live", fake)]
        try:
            v2 = cad.model_version()
        finally:
            cad._model_files = orig
    check("NW15. đổi NỘI DUNG file mô hình (dù chỉ 1 dòng, chưa commit) ⇒ chữ ký ĐỔI — chữ ký "
          "theo nội dung chứ không theo git, vì bản sửa chưa commit vẫn sinh ra số khác",
          v2 != v1 and cad.model_version() == v1, f"{v1} vs {v2}")


# ───────────── LỚP 4c · cổng BIÊN ĐỘ ×3 (WARN — đánh dấu, TUYỆT ĐỐI KHÔNG ẩn số)

# Fixture VHM tái lập ĐÚNG hình dạng ca thật, không phải một ca ×1000 bịa ra: bản ghi rò rỉ thật
# đo được ở `research/oshares_gate_move_20260813/sanity_direct_call.json` là
#   {ticker VHM, date 2021-12-31, live 4.354.367, quarterly 4.354.367.488,
#    ratio 0,000999999887928614, method AIS_EXACT, anchor_date 2021-10-12}
# và fixture dưới đây cho `oshares_at` trả về ĐÚNG bốn trường đó (M1 assert từng cái).
#
# HAI dòng AIS cùng mang số ×1000 là điểm mấu chốt, không phải chi tiết thừa: một dòng AIS sai
# ĐƠN ĐỘC bị cổng chứng nhận vòng 4-6 chặn (`AIS_UNCERTIFIED`, value=None) ⇒ không có số nào được
# công bố ⇒ không có gì cho cổng biên độ làm. Vendor sai ĐƠN VỊ thì sai cả một chuỗi, nên số sai
# TỰ NHẤT QUÁN với chính nó, qua được cổng chứng nhận, và §4 (chỉ bắt CHUYỂN TIẾP) mù hoàn toàn.
# Đó chính xác là lỗ hổng mà lớp 4c bịt — fixture phải nằm trong lỗ hổng đó mới chứng minh gì.
VHM_CACHE = (
    [_q("VHM", "2021-06-30", 4_354_367_488), _q("VHM", "2021-12-31", 4_354_367_488)],
    [_ais("VHM", "2021-03-05", 4_354_367), _ais("VHM", "2021-10-12", 4_354_367)],
)


def t_magnitude_gate():
    print("== LỚP 4c · cổng biên độ ×3 — CẢNH BÁO, không được đổi/ẩn số công bố ==")
    from oshares_live import oshares_at

    # ── M1-M2: ca THẬT, chạy qua chính `oshares_at`, không phải dict tự bịa
    rows = oshares_at(["VHM"], "2021-12-31", _cache=VHM_CACHE)
    before = float(rows["VHM"]["value"])
    check("MG1. ca THẬT VHM 2021-10-12 (vendor ×1000): fixture tái lập ĐÚNG bản ghi rò rỉ đã đo "
          "(live 4.354.367 / quý 4.354.367.488 / AIS_EXACT / neo 2021-10-12) — nếu không thì mọi "
          "ca dưới đây đang kiểm một ca bịa",
          before == 4_354_367.0 and rows["VHM"]["method"] == "AIS_EXACT"
          and rows["VHM"]["anchor_date"] == "2021-10-12",
          f"{before:,.0f} {rows['VHM']['method']}")

    w = cad.sanity_warns(rows, "2021-12-31", VHM_CACHE[0], "publish")
    check("MG1b. và cổng biên độ KÍCH đúng trên ca đó, với tỉ số khớp số đã đo "
          "(0,000999999887928614)",
          len(w) == 1 and w[0]["ticker"] == "VHM" and abs(w[0]["ratio"] - 0.000999999887928614)
          < 1e-15 and w[0]["quarterly"] == 4_354_367_488.0 and w[0]["where"] == "publish",
          str(w))

    check("MG2. BẤT BIẾN MẠNH NHẤT của phương án C — `value` sau khi gắn cờ Y HỆT trước đó, và "
          "KHÔNG có `value_withheld`/`INVARIANT_SUSPECT` nào được sinh ra (đó là hành vi của lớp "
          "4, không phải lớp này)",
          rows["VHM"]["value"] == before and "value_withheld" not in rows["VHM"]
          and rows["VHM"]["method"] == "AIS_EXACT"
          and rows["VHM"]["sanity_warn"]["quarterly"] == 4_354_367_488.0,
          str({k: rows["VHM"][k] for k in ("value", "method")}))

    # ── M3-M5: BIÊN. `_sane` là `1/F <= ratio <= F` ⇒ đúng ×3,0 chẵn là HỢP LỆ (luật `>F`), cùng
    # vị ngữ với con số 279 ô/34 mã của ROUND5 (nó cũng đo bằng `_sane`).
    def flag(live, q):
        return cad.sanity_flag(live, q)

    check("MG3. CA CHỨNG MINH NGƯỢC — số bình thường (lệch 0%) KHÔNG kích; cổng luôn-kích cũng "
          "'bắt được' ca M1 nên ca này mới làm M1 có nghĩa", flag(1_000.0, 1_000.0) is None)
    check("MG3b. lệch 2,999× (dưới ngưỡng) KHÔNG kích", flag(2_999.0, 1_000.0) is None)
    check("MG4. BIÊN ĐÚNG ×3,0 CHẴN ⇒ KHÔNG kích (luật là `>3`, không phải `>=3` — cùng vị ngữ "
          "`_pit._sane` với phép đo 279 ô/34 mã ở ROUND5)", flag(3_000.0, 1_000.0) is None)
    check("MG4b. và ngay trên biên (3,001×) thì KÍCH — chứng minh M4 không PASS vì cổng chết",
          flag(3_001.0, 1_000.0) is not None, str(flag(3_001.0, 1_000.0)))
    check("MG5. phía NGHỊCH ĐẢO đối xứng: đúng 1/3 KHÔNG kích, dưới 1/3 thì KÍCH (ca VHM nằm ở "
          "phía này — ×0,001 — nên một cổng chỉ kiểm `ratio > F` sẽ mù hoàn toàn với nó)",
          flag(1_000.0, 3_000.0) is None and flag(1_000.0, 3_001.0) is not None)

    # ── M6-M7: hai lối bỏ qua có chủ đích
    none_rows = {"XXX": {"value": None, "method": "AIS_UNCERTIFIED"}}
    # ⚠️ CÔNG BỐ GIỚI HẠN: ca này KHÔNG GIẾT ĐƯỢC mutation nào — đã thử bỏ hẳn dòng
    # `if r.get("value") is None: continue` trong `sanity_warns` và bộ này vẫn 178/178, vì
    # `sanity_flag(None, …)` tự trả None nên hành vi không đổi. Dòng guard đó là phòng thủ chồng
    # lớp, không phải chỗ duy nhất giữ tính chất. Ghi ra đây thay vì để ca này trông như một
    # bằng chứng bao phủ mà nó không phải.
    check("MG6. `value is None` (mô hình từ chối / lớp 4 đã giấu) ⇒ BỎ QUA — không có số công bố "
          "thì không có gì để nghi ngờ, và mã đó đã được đếm ở dòng 🔇 (`none_value_watch`); gắn "
          "cờ ở đây là đếm CÙNG một mã ở hai dòng cảnh báo như hai vấn đề",
          cad.sanity_warns(none_rows, "2021-12-31", VHM_CACHE[0], "publish") == []
          and "sanity_warn" not in none_rows["XXX"])
    check("MG7. mã KHÔNG có dòng quý nào ≤ ngày đó ⇒ bỏ qua im lặng, không dựng lệch giả",
          cad.sanity_warns({"ZZZ": {"value": 1.0}}, "2021-12-31", VHM_CACHE[0], "publish") == [])

    # ── M8: điểm gọi thứ ba — TÁI DÙNG bản ghi `crosscheck()` thật, không truy vấn lại
    cc = cad.crosscheck("2021-12-31", {"VHM"}, VHM_CACHE)
    mag_cc = cad.sanity_warns_from_crosscheck(cc)
    check("MG8. ĐẦU-CUỐI qua `crosscheck()` THẬT: bản ghi DIVERGENT do chính nó sinh ra được gắn "
          "cờ biên độ, `oshares_live` GIỮ NGUYÊN số, và `where='crosscheck'`",
          len(mag_cc) == 1 and mag_cc[0]["where"] == "crosscheck"
          and cc[0]["oshares_live"] == 4_354_367.0
          and cc[0]["sanity_warn"]["quarterly"] == 4_354_367_488.0, str(mag_cc))
    check("MG8b. bản ghi NO_MODEL_VALUE (mô hình từ chối) tự rơi ra khỏi cổng biên độ, không nổ "
          "TypeError trên `None`",
          cad.sanity_warns_from_crosscheck(
              cad.crosscheck("2026-08-13", {"CCC"}, CACHE)) == [])

    # ── M9-M11: CHUỖI người thật đọc (verify-before-done: assert trên OUTPUT, không trên hàm)
    s = cad._fmt_magnitude(w, held={"VHM"})
    check("MG9. tiêu đề nói THẲNG 'SỐ VẪN ĐƯỢC CÔNG BỐ NGUYÊN VẸN' — khác biệt quan trọng nhất so "
          "với dòng 🚨 ngay cạnh (ở đó số ĐÃ BỊ GIẤU), và nó phải ở TIÊU ĐỀ chứ không phải cuối "
          "dòng", "SỐ VẪN ĐƯỢC CÔNG BỐ NGUYÊN VẸN" in s and s.index("NGUYÊN VẸN") < 200, s)
    # BẢN ĐẦU CỦA CA NÀY SAI và tự nó bắt được: nó grep `"đã bị GIẤU):"` nên đỏ vì chính câu
    # ĐỐI CHIẾU trong tiêu đề ("KHÁC dòng 🚨 nơi số đã bị GIẤU") — tức là phạt đúng cái phải có.
    # Vị ngữ đúng: chuỗi 📏 không được mang câu KHẲNG ĐỊNH của dòng 🚨 về CHÍNH những mã của nó.
    check("MG9b. chuỗi KHÔNG mang câu khẳng định 'số đã bị giấu/không publish' của dòng 🚨 (grep "
          "đúng cụm mà `run()` in ở dòng 🚨), trong khi VẪN được phép nhắc tới 🚨 để đối chiếu",
          "không publish giá trị" not in s and "KHÔNG PUBLISH" not in s
          and "số đã bị GIẤU, không" not in s and "KHÁC dòng 🚨" in s, s)
    check("MG9c. chuỗi in ĐỦ hai số + tỉ số + ngưỡng + nhãn phương pháp (người đọc tự đánh giá "
          "được mà không phải mở snapshot)",
          "4,354,367" in s and "4,354,367,488" in s and "×3" in s and "AIS_EXACT" in s, s)
    check("MG10. mã ĐANG GIỮ tách RIÊNG và nêu trong tiêu đề — 2/34 mã lọt ở ROUND5 (VHM, VND) là "
          "mã đang giữ thật, đó mới là nhóm chạm tiền",
          "**ĐANG GIỮ**" in s and "1 ĐANG GIỮ" in s, s[:160])
    s_not_held = cad._fmt_magnitude(w, held=set())
    check("MG10b. cùng cảnh báo đó mà KHÔNG giữ mã ⇒ không có mục ĐANG GIỮ (chứng minh ngược: M10 "
          "không PASS vì chuỗi luôn in nhãn đó)",
          "**ĐANG GIỮ**" not in s_not_held and "không giữ —" in s_not_held, s_not_held[:160])

    check("MG11. BA loại cảnh báo về 'số CP đáng ngờ' PHÂN BIỆT ĐƯỢC trong cùng một tin nhắn: 📏 "
          "(biên độ, số còn nguyên) ≠ 🚨 (bất biến, số đã giấu) ≠ ⚠️ (hai nguồn khác nhau)",
          s.startswith("📏") and not s.startswith("🚨") and "⚠️ SỐ VẪN" in s
          and cad._fmt_divergence([{"ticker": "EVF", "at": "x", "ticker_financial": 1.0,
                                    "oshares_live": 2.0, "kind": "DIVERGENT",
                                    "err_pct_vs_ticker_financial": 1.0}]).startswith("⚠️"), s[:8])
    check("MG12. rỗng ⇒ None (không đẻ dòng trống)", cad._fmt_magnitude([], held={"VHM"}) is None)
    check("MG13. quá `limit` ⇒ nói rõ còn bao nhiêu mã nữa, không im lặng cắt cụt (§'no silent "
          "caps')", "… và 2 mã nữa" in cad._fmt_magnitude(w * 5, held=set(), limit=3),
          cad._fmt_magnitude(w * 5, held=set(), limit=3)[-40:])

    # ── M14: ngưỡng đọc TẠI LÚC GỌI, không đóng băng lúc import
    keep = cad._pit.SANITY_FACTOR
    try:
        cad._pit.SANITY_FACTOR = 1e9
        check("MG14. `_pit.SANITY_FACTOR` đọc tại LÚC GỌI: nới ngưỡng lên 1e9 ⇒ ca VHM thôi kích. "
              "Bản `from oshares_pit import SANITY_FACTOR` sẽ đóng băng giá trị lúc import và ca "
              "này PASS oan (cổng vẫn kích) — đúng chỗ hở 'hai phần fleet đọc hai giá trị'",
              cad.sanity_flag(4_354_367.0, 4_354_367_488.0) is None)
    finally:
        cad._pit.SANITY_FACTOR = keep
    check("MG14b. khôi phục ngưỡng ⇒ kích lại (chứng minh M14 không PASS vì cổng chết hẳn)",
          cad.sanity_flag(4_354_367.0, 4_354_367_488.0) is not None)

    # ── M15: một vị ngữ, và KHÔNG có đường nào trong lớp này chạm tới `value`
    src = inspect.getsource(cad)
    mag_src = "".join(inspect.getsource(getattr(cad, f)) for f in
                      ("sanity_flag", "sanity_warns", "sanity_warns_from_crosscheck",
                       "_fmt_magnitude"))
    # đếm ĐIỂM GỌI (`_pit._sane(`), không đếm mọi lần chuỗi xuất hiện: bản đầu đếm cái sau nên
    # đỏ vì một dòng DOCSTRING nhắc tên hàm — phạt đúng phần tài liệu đang làm việc tốt.
    check("MG15. vị ngữ biên độ được GỌI MỘT LẦN trong cả module (`_pit._sane(`) — không ai chép "
          "lại bất đẳng thức ×3 ở tầng log/Discord/bus (cùng kỷ luật `refused()`, ca R10)",
          src.count("_pit._sane(") == 1 and "SANITY_FACTOR <=" not in src
          and "<= _pit.SANITY_FACTOR" not in src, str(src.count("_pit._sane(")))
    check("MG15b. CHỐT PHƯƠNG ÁN C Ở TẦNG MÃ NGUỒN: toàn bộ lớp 4c KHÔNG có một phép gán nào lên "
          "`value`, không `None`-hoá, không gọi `withhold` — một bản vá sau này biến WARN thành "
          "SUPPRESS sẽ làm đỏ ca này",
          '["value"] =' not in mag_src and "['value'] =" not in mag_src
          and "withhold" not in mag_src and "value_withheld" not in mag_src)

    # ── M16: `check_retro(back=...)` tương thích ngược — mọi caller cũ không đổi một chữ
    prev_snap = {"tickers": {"VHM": {"value": 4_354_367.0}}}
    a = cad.check_retro("2021-12-31", "2021-12-30", prev_snap, VHM_CACHE, {"VHM"})
    b = cad.check_retro("2021-12-31", "2021-12-30", prev_snap, VHM_CACHE, {"VHM"},
                        back=oshares_at(["VHM"], "2021-12-30", _cache=VHM_CACHE))
    check("MG16. `check_retro` với `back=` truyền sẵn cho KẾT QUẢ Y HỆT bản tự tính — tham số mới "
          "chỉ để dùng lại phép tính, không đổi hành vi", a == b, f"{a} vs {b}")


# ─────────────────────────────────────── lịch trigger + LỚP 6 · cảnh báo proactive

def t_triggers_and_alerts():
    print("== lịch trigger (ex-right vs AIS effective) + cảnh báo ≤10 ngày ==")
    rows = [{"ticker": "AAA", "event_code": "DIV", "exright_date": "2026-08-13",
             "effective_date": None},
            {"ticker": "BBB", "event_code": "ISS", "exright_date": "2026-08-13",
             "effective_date": None},
            {"ticker": "CCC", "event_code": "AIS", "exright_date": None,
             "effective_date": "2026-08-13"},
            {"ticker": "DDD", "event_code": "DIV", "exright_date": "2026-08-14",
             "effective_date": None}]
    ex, ais, _ = cad.triggered_today("2026-08-13", rows=rows)
    check("T1. ex-right hôm nay ⇒ nhóm 'ex' (DIV + ISS), AIS hiệu lực hôm nay ⇒ nhóm RIÊNG "
          "(hai lần chạm khác nhau của cùng một sự kiện, lệch tới ~7 tuần)",
          ex == {"AAA", "BBB"} and ais == {"CCC"}, f"ex={ex} ais={ais}")
    check("T2. sự kiện NGÀY MAI không kích hoạt hôm nay", "DDD" not in ex | ais)

    asof = "2026-08-13"

    def ev(tk, code, ex_d=None, eff=None, status="announced", ratio=None, vps=None,
           method=None):
        return {"ticker": tk, "event_code": code, "exright_date": ex_d, "effective_date": eff,
                "event_status": status, "exercise_ratio": ratio, "value_per_share": vps,
                "issue_method_name_vi": method, "event_title_vi": f"{tk} {code}"}

    rows = [
        ev("AAA", "DIV", ex_d="2026-08-14", vps=1500),                       # mai, announced
        ev("BBB", "ISS", ex_d="2026-08-23", ratio=0.15, method="Cổ phiếu thưởng"),  # +10 ngày
        ev("CCC", "ISS", ex_d="2026-08-24", ratio=0.1),                      # +11 ngày → ngoài
        ev("DDD", "DIV", ex_d="2026-08-13", vps=800, status="executed"),     # đúng hôm nay
        ev("EEE", "DIV", ex_d="2026-08-15", status="not_executed"),          # đã huỷ
        ev("FFF", "AIS", eff="2026-08-18"),                                  # theo effective_date
        ev("GGG", "DIV", ex_d="2026-08-15", vps=900),                        # KHÔNG giữ
        ev("AAA", "DIV", ex_d="2026-08-01", vps=500, status="executed"),     # quá khứ
    ]
    held = {"AAA", "BBB", "CCC", "DDD", "EEE", "FFF"}
    up = cad.upcoming_events(asof, held, days=10, rows=rows)
    got = [(e["ticker"], e["date"], e["days_ahead"]) for e in up]
    check("T3. cửa sổ [hôm nay, +10] ĐÓNG hai đầu: hôm nay (DDD, 0n) và đúng +10 (BBB) đều vào; "
          "+11 (CCC) ra ngoài; quá khứ ra ngoài",
          got == [("DDD", "2026-08-13", 0), ("AAA", "2026-08-14", 1),
                  ("FFF", "2026-08-18", 5), ("BBB", "2026-08-23", 10)], str(got))
    check("T4. `announced` PHẢI vào (đo 2026-08-13: 35 DIV + 7 ISS tương lai, 0 dòng executed — "
          "lọc executed sẽ trả RỖNG mỗi ngày và trông y hệt 'không có sự kiện')",
          any(e["ticker"] == "AAA" and e["event_status"] == "announced" for e in up))
    check("T5. `not_executed` (đã huỷ) bị loại", all(e["ticker"] != "EEE" for e in up))
    check("T6. mã KHÔNG nắm giữ bị loại — cảnh báo này là về danh mục thật, không phải toàn thị "
          "trường", all(e["ticker"] != "GGG" for e in up))
    check("T7. AIS vào cửa sổ theo `effective_date`, và ghi rõ đọc từ trường nào",
          [e["date_field"] for e in up if e["ticker"] == "FFF"] == ["effective_date"])
    check("T8. nhãn điều chỉnh giá đúng theo taxonomy: DIV tiền mặt CÓ, thưởng CP CÓ",
          all(e["price_adjusting"] for e in up if e["ticker"] in ("AAA", "DDD", "BBB")))
    check("T9. tin nhắn có mã + ngày + số còn lại + nhãn 'dự kiến' cho announced",
          all(s in cad._fmt_event(up[1], {"AAA": [("SpaceX", 900)]})
              for s in ("AAA", "2026-08-14", "còn 1n", "1,500đ/cp", "dự kiến", "SpaceX")),
          cad._fmt_event(up[1], {"AAA": [("SpaceX", 900)]}))
    check("T10. lookahead=0 ⇒ chỉ còn sự kiện HÔM NAY (tham số thật sự có tác dụng)",
          [e["ticker"] for e in cad.upcoming_events(asof, held, days=0, rows=rows)] == ["DDD"])
    check("T11. không giữ mã nào ⇒ rỗng, không truy vấn gì",
          cad.upcoming_events(asof, set(), days=10) == [])


# ────────────────────────── HÌNH DẠNG TRUY VẤN của trigger ngày-sự-kiện + vòng xác nhận

def t_query_shape():
    """Ca hồi quy cho ĐÚNG lỗ hổng quant-skeptic đã chọc thủng vòng 1 (2026-08-13).

    Bug: `_all_events_on` ép `event_status = "executed"`, nên trigger ngày-sự-kiện trả RỖNG mỗi
    ngày (vendor chỉ đổi `announced → executed` trong lần reload ~22:2x ICT CỦA CHÍNH ngày đó,
    tức sau khi cron 07:30 đã chạy). Vì sao bộ hồi quy cũ mù: T1/T2 bơm `rows=` vào
    `triggered_today`, tức là đi VÒNG QUA mệnh đề WHERE — chúng kiểm bộ lọc SAU truy vấn, còn
    bug nằm TRONG truy vấn. Nên các ca dưới đây soi thẳng chuỗi SQL, và tầng `--live` chạy nó
    thật.
    """
    print("== hình dạng truy vấn (ca mà bộ cũ đi vòng qua) + vòng xác nhận T-1 ==")
    sql = cad._events_on_sql("2026-08-13")
    norm = " ".join(sql.split())

    check('Q1. KHÔNG được lọc `event_status = "executed"` — đây là chuỗi ký tự của chính bug '
          "vòng 1, giữ nguyên văn để lần sau ai gõ lại là đỏ ngay",
          'event_status = "executed"' not in norm, norm)
    check("Q2. nhưng sự kiện ĐÃ HUỶ vẫn phải bị loại (nới lỏng ≠ bỏ cổng)",
          'event_status != "not_executed"' in norm, norm)
    check("Q3. CHỨNG MINH NGƯỢC cho Q2: `include_cancelled=True` (vòng xác nhận) KHÔNG được lọc "
          "trạng thái nào — chính cái đã huỷ mới là thứ nó đi tìm; lọc mất thì CANCELLED sẽ bị "
          "báo nhầm thành VANISHED",
          "event_status" not in " ".join(
              cad._events_on_sql("2026-08-13", include_cancelled=True).split()
          ).split("WHERE")[1].split("AND")[0])
    check("Q4. hỏi CẢ HAI cột ngày bằng OR (ex-right và AIS-effective là hai lần chạm khác nhau; "
          "AND sẽ trả rỗng vì không dòng nào có cả hai)",
          'exright_date = DATE "2026-08-13" OR effective_date = DATE "2026-08-13"' in norm, norm)
    check("Q5. tham số `table=` thật sự đổi FROM — nếu không, ca --live dưới đây sẽ âm thầm đo "
          "bảng production thay vì bảng dựng tay và luôn xanh",
          "FROM `X_FAKE`" in " ".join(cad._events_on_sql("2026-08-13", table="X_FAKE").split()))

    # ── vòng xác nhận T-1: cái giá phải trả cho việc ghi trên `announced`
    def r(tk, status, ex="2026-08-12", code="DIV"):
        return {"ticker": tk, "event_code": code, "exright_date": ex, "effective_date": None,
                "event_status": status}

    prev = {"events_today": [r("AAA", "announced"), r("BBB", "announced"),
                             r("CCC", "announced"), r("DDD", "announced")]}
    now = [r("AAA", "executed"), r("BBB", "not_executed"), r("CCC", "announced")]  # DDD biến mất
    got = {c["ticker"]: c["kind"] for c in
           cad.confirm_prior_triggers("2026-08-12", prev, rows=now)}
    check("C1. `announced → executed` ⇒ CONFIRMED (đường bình thường phải LỌT, không phải chỉ "
          "cổng bắt được cái xấu)", got.get("AAA") == "CONFIRMED", str(got))
    check("C2. `announced → not_executed` ⇒ CANCELLED — khoản đã ghi hôm qua nay bị huỷ, đây là "
          "SAI SỐ THẬT phải tới tay người", got.get("BBB") == "CANCELLED", str(got))
    check("C3. vendor chưa đổi trạng thái ⇒ STILL_ANNOUNCED (chưa sai, nhưng chưa chắc — không "
          "được gộp vào CONFIRMED)", got.get("CCC") == "STILL_ANNOUNCED", str(got))
    check("C4. dòng BIẾN MẤT khỏi bảng ⇒ VANISHED, không phải im lặng bỏ qua",
          got.get("DDD") == "VANISHED", str(got))
    check("C5. khoá so khớp gồm CẢ NGÀY: cùng mã + cùng loại nhưng khác ex-date là sự kiện KHÁC, "
          "không được nhận nhầm là đã xác nhận",
          cad.confirm_prior_triggers(
              "2026-08-12", {"events_today": [r("AAA", "announced", ex="2026-08-12")]},
              rows=[r("AAA", "executed", ex="2026-07-01")])[0]["kind"] == "VANISHED")
    check("C6. chưa có snapshot hôm trước ⇒ rỗng, không nổ và không dựng cảnh báo giả",
          cad.confirm_prior_triggers(None, None) == []
          and cad.confirm_prior_triggers("2026-08-12", {"events_today": []}) == [])


# ─────────────────── khoá DUY NHẤT theo sự kiện + hàng treo (quant-skeptic vòng 2, 2026-08-13)

# Ca MBB 2026-08-11 — KHÔNG phải ca dựng: hai sự kiện này có thật trong `corporate_action` và
# chính docstring của `bq_corp_action` đã ghi chúng ra. Cùng ticker, cùng `event_code` (ISS),
# cùng `exright_date`; chỉ khác `exercise_ratio`/`issue_method_name_vi`.
_MBB_MUA = dict(ratio=0.1, method="Quyền mua CP cho Cổ đông hiện hữu",
                title="Phát hành cổ phiếu - Quyền mua CP cho Cổ đông hiện hữu tỉ lệ 10.0%")
_MBB_CTCP = dict(ratio=0.15, method="Trả Cổ tức bằng Cổ phiếu",
                 title="Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%")


def _mbb(spec, status, ev_id=None):
    return {"id": ev_id, "ticker": "MBB", "event_code": "ISS", "exright_date": "2026-08-11",
            "effective_date": None, "value_per_share": None, "exercise_ratio": spec["ratio"],
            "issue_method_name_vi": spec["method"], "event_title_vi": spec["title"],
            "event_status": status}


def _kinds_by_ratio(prev, now):
    return {(c["exercise_ratio"], c["kind"]) for c in
            cad.confirm_prior_triggers("2026-08-11", prev, rows=now)}


def t_confirm_unique_key():
    """Ca hồi quy cho lỗ hổng quant-skeptic chọc thủng VÒNG 2 (2026-08-13).

    Bug: khoá gộp `(ticker, event_code, exright_date, effective_date)` KHÔNG duy nhất. Hai sự
    kiện MBB cùng ngày rơi vào một khoá ⇒ một dòng đè dòng kia ⇒ khi một cái bị HUỶ còn một cái
    được xác nhận, kết quả CONFIRMED hay CANCELLED phụ thuộc THỨ TỰ DÒNG BigQuery trả về (không
    xác định trước). Nghĩa là một khoản đã huỷ có thể được báo là đã xác nhận, và vòng xác nhận
    — thứ DUY NHẤT biện minh cho việc ghi số trên `announced` — im lặng đúng lúc cần nó nhất.

    Mọi ca dưới đây chạy CẢ HAI thứ tự dòng và đòi KẾT QUẢ GIỐNG HỆT NHAU.
    """
    print("== khoá duy nhất theo TỪNG sự kiện (ca MBB 2 sự kiện cùng ngày) ==")
    want = {(0.1, "CANCELLED"), (0.15, "CONFIRMED")}

    # (a) KHÔNG có `id` — đúng hình dạng snapshot cũ đã ghi ra đĩa trước bản vá này.
    prev = {"events_today": [_mbb(_MBB_MUA, "announced"), _mbb(_MBB_CTCP, "announced")]}
    fwd = [_mbb(_MBB_MUA, "not_executed"), _mbb(_MBB_CTCP, "executed")]
    check("K1. 2 sự kiện MBB vào ⇒ 2 dòng xác nhận ra (bản cũ: 2 vào, 1 ra — một cái biến mất)",
          len(cad.confirm_prior_triggers("2026-08-11", prev, rows=fwd)) == 2)
    check("K2. quyền mua 10% bị HUỶ ⇒ CANCELLED, cổ tức CP 15% ⇒ CONFIRMED (không có `id`, khớp "
          "bằng khoá nội dung)", _kinds_by_ratio(prev, fwd) == want, str(_kinds_by_ratio(prev, fwd)))
    check("K3. ĐẢO THỨ TỰ DÒNG BQ trả về ⇒ KẾT QUẢ Y HỆT. Đây là chính ca quant-skeptic dựng: "
          "bản cũ lật giữa CONFIRMED và CANCELLED chỉ vì đổi thứ tự",
          _kinds_by_ratio(prev, list(reversed(fwd))) == want,
          str(_kinds_by_ratio(prev, list(reversed(fwd)))))
    check("K4. đảo cả thứ tự BẢN GHI hôm trước cũng không đổi kết luận",
          _kinds_by_ratio({"events_today": list(reversed(prev["events_today"]))}, fwd) == want)

    # (b) CÓ `id` vendor (36.149/36.149 duy nhất, 0 NULL — đã kiểm trên bảng thật)
    pid = {"events_today": [_mbb(_MBB_MUA, "announced", "aaa1"),
                            _mbb(_MBB_CTCP, "announced", "bbb2")]}
    nid = [_mbb(_MBB_CTCP, "executed", "bbb2"), _mbb(_MBB_MUA, "not_executed", "aaa1")]
    check("K5. có `id` ⇒ khớp thẳng từng dòng, thứ tự đảo vẫn đúng",
          _kinds_by_ratio(pid, nid) == want, str(_kinds_by_ratio(pid, nid)))
    check("K6. `id` ĐỔI HẾT (giả lập vendor sinh id mới mỗi lần nạp lại — KHÔNG kiểm chứng được "
          "vì cả bảng chỉ có 1 ngày `ingested_at`) ⇒ vẫn khớp bằng nội dung, KHÔNG bắn một trận "
          "VANISHED giả",
          _kinds_by_ratio(pid, [_mbb(_MBB_MUA, "not_executed", "zzz9"),
                                _mbb(_MBB_CTCP, "executed", "yyy8")]) == want)
    # Ca DUY NHẤT mà lớp `id` làm được còn khoá nội dung thì không: vendor ĐÍNH CHÍNH nội dung của
    # CHÍNH sự kiện đó (đổi tỉ lệ/số tiền) rồi huỷ nó. Khoá nội dung sẽ thấy "sự kiện cũ biến mất
    # + một sự kiện lạ xuất hiện" ⇒ báo VANISHED, sai bản chất: nó không biến mất, nó BỊ HUỶ.
    edited = cad.confirm_prior_triggers(
        "2026-08-11", {"events_today": [_mbb(_MBB_MUA, "announced", "aaa1")]},
        rows=[dict(_mbb(_MBB_MUA, "not_executed", "aaa1"), exercise_ratio=0.12,
                   event_title_vi="… đính chính tỉ lệ 12.0%")])
    check("K7. vendor ĐÍNH CHÍNH nội dung rồi HUỶ ⇒ vẫn là CANCELLED nhờ khớp theo `id` (chỉ có "
          "khoá nội dung thì ra VANISHED — báo sai bản chất, và bỏ lọt một vụ huỷ thật)",
          [c["kind"] for c in edited] == ["CANCELLED"], str(edited))

    # (c) ca bệnh lý: hai dòng GIỐNG NHAU tới từng ký tự và không `id`. Chúng KHÔNG phân biệt
    # được, và quy ước sẵn có của `bq_corp_action` đã coi hai dòng y hệt nhau là MỘT sự kiện
    # (bản đính chính), nên gộp làm một là đúng — dùng lại quy ước đó, không dựng quy ước thứ hai.
    # Cái phải chứng minh ở đây là: khi trạng thái MÂU THUẪN, kết quả vẫn phải THẬN TRỌNG và
    # KHÔNG phụ thuộc thứ tự — tức luôn ra CANCELLED, không bao giờ ra CONFIRMED.
    same = {"events_today": [_mbb(_MBB_MUA, "announced"), _mbb(_MBB_MUA, "announced")]}
    for order in ([_mbb(_MBB_MUA, "executed"), _mbb(_MBB_MUA, "not_executed")],
                  [_mbb(_MBB_MUA, "not_executed"), _mbb(_MBB_MUA, "executed")]):
        got = sorted(c["kind"] for c in cad.confirm_prior_triggers("2026-08-11", same, rows=order))
        check(f"K8. hai dòng KHÔNG phân biệt được, thứ tự {[r['event_status'][:4] for r in order]}"
              " ⇒ luôn CANCELLED (gán TỆ NHẤT TRƯỚC: không phân biệt được thì không được đoán về "
              "phía 'đã xác nhận')", got == ["CANCELLED"], str(got))
    check("K9. CHỨNG MINH NGƯỢC cho K8: không có dòng nào `not_executed` thì KHÔNG được tự dựng "
          "CANCELLED", all(c["kind"] == "CONFIRMED" for c in cad.confirm_prior_triggers(
              "2026-08-11", same, rows=[_mbb(_MBB_MUA, "executed"), _mbb(_MBB_MUA, "executed")])))

    # (d) nhãn *(dự kiến)* của số cổ tức GỘP — cùng lỗi gộp khoá, cùng cách sửa
    def _div(tk, status, vps, title):
        return {"id": None, "ticker": tk, "event_code": "DIV", "exright_date": "2026-08-13",
                "effective_date": None, "value_per_share": vps, "exercise_ratio": None,
                "issue_method_name_vi": None, "event_title_vi": title, "event_status": status}

    mixed = [_div("XXX", "executed", 1000, "đợt 1"), _div("XXX", "announced", 500, "đợt 2")]
    check("K10. mã có 2 đợt cổ tức cùng ngày, 1 chưa xác nhận ⇒ nhãn của SỐ GỘP không được là "
          "`executed`; và đảo thứ tự cho kết quả Y HỆT (bản cũ: dòng cuối thắng)",
          cad.dividend_event_status(mixed, "2026-08-13")["XXX"] != "executed"
          and cad.dividend_event_status(mixed, "2026-08-13")
          == cad.dividend_event_status(list(reversed(mixed)), "2026-08-13"),
          str(cad.dividend_event_status(mixed, "2026-08-13")))
    check("K11. CHỨNG MINH NGƯỢC cho K10: mọi đợt đều `executed` ⇒ nhãn `executed`, không dán "
          "'dự kiến' bừa lên số đã chắc",
          cad.dividend_event_status(
              [_div("XXX", "executed", 1000, "đợt 1"), _div("XXX", "executed", 500, "đợt 2")],
              "2026-08-13") == {"XXX": "executed"})
    check("K12. sự kiện của NGÀY KHÁC không được lọt vào nhãn hôm nay",
          cad.dividend_event_status(
              [dict(_div("YYY", "announced", 700, "hôm khác"), exright_date="2026-08-12")],
              "2026-08-13") == {})


def _f(lst, key):
    """Đọc trường của phần tử đầu — RỖNG thì trả None thay vì IndexError. Khi một mutation làm
    hàm trả rỗng, ca phải hiện ĐỎ chứ không được làm cả bộ chết giữa chừng."""
    return lst[0].get(key) if lst else None


def t_carry_forward():
    """Hàng CÒN TREO phải được kiểm lại ở D+2, D+3… — không phải một phát rồi thôi.

    Bug vòng 2: `recorded` dựng CHỈ từ `events_today` của snapshot liền trước, nên món trả
    `STILL_ANNOUNCED` ở D+1 không bao giờ được nhìn lại. Mà lượt chạy sống DUY NHẤT của vòng xác
    nhận cho 4/4 `STILL_ANNOUNCED` — đúng cái nhánh bị rơi lại là nhánh xảy ra thật.
    """
    print("== hàng treo mang qua nhiều lượt chạy (carry-forward) ==")

    def r(tk, status, ex="2026-08-12"):
        return {"id": f"id-{tk}", "ticker": tk, "event_code": "DIV", "exright_date": ex,
                "effective_date": None, "value_per_share": 1000.0, "exercise_ratio": None,
                "issue_method_name_vi": None, "event_title_vi": f"{tk} DIV",
                "event_status": status}

    d = "2026-08-12"
    # lượt 1 (D+1): vendor chưa đổi trạng thái
    c1 = cad.confirm_prior_triggers(d, {"events_today": [r("AAA", "announced")]},
                                    rows_by_date={d: [r("AAA", "announced")]})
    p1 = cad.carry_forward(c1)
    check("P1. lượt đầu còn `announced` ⇒ STILL_ANNOUNCED, n_checks=1, và ĐƯỢC mang sang lượt sau",
          [c["kind"] for c in c1] == ["STILL_ANNOUNCED"] and _f(c1, "n_checks") == 1
          and len(p1) == 1, str(c1))
    check("P2. món mang sang giữ đủ trường để lượt sau dựng lại khoá + ngày sự kiện",
          _f(p1, "event_date") == d and _f(p1, "first_seen_asof") == d
          and _f(p1, "status_then") == "announced" and _f(p1, "id") == "id-AAA", str(p1))

    # lượt 2 (D+2): `events_today` của snapshot liền trước RỖNG — chỉ hàng treo giữ được nó
    snap2 = {"events_today": [], "pending_confirmations": p1}
    c2 = cad.confirm_prior_triggers("2026-08-13", snap2,
                                    rows_by_date={d: [r("AAA", "announced")]})
    check("P3. D+2 VẪN kiểm lại đúng NGÀY SỰ KIỆN gốc dù `events_today` hôm qua rỗng — đây là ca "
          "bản trước trả rỗng (một phát rồi thôi)",
          len(c2) == 1 and _f(c2, "event_date") == d and _f(c2, "n_checks") == 2, str(c2))
    check("P4. đồng hồ `first_seen_asof` KHÔNG bị reset khi mang qua lượt",
          _f(c2, "first_seen_asof") == d, str(c2))
    check("P5. CHỨNG MINH NGƯỢC cho P3: không `events_today`, không hàng treo ⇒ RỖNG (hàm không "
          "tự bịa ra việc để làm)",
          cad.confirm_prior_triggers("2026-08-13", {"events_today": []}) == [])

    # ngã ngũ ⇒ thôi mang
    c3 = cad.confirm_prior_triggers("2026-08-14", {"events_today": [], "pending_confirmations": p1},
                                    rows_by_date={d: [r("AAA", "executed")]})
    check("P6. khi vendor đổi trạng thái ⇒ CONFIRMED và KHÔNG mang tiếp (hàng treo phải rút được, "
          "không thì nó chỉ dài ra mãi)",
          [c["kind"] for c in c3] == ["CONFIRMED"] and cad.carry_forward(c3) == [], str(c3))
    c4 = cad.confirm_prior_triggers("2026-08-14", {"events_today": [], "pending_confirmations": p1},
                                    rows_by_date={d: [r("AAA", "not_executed")]})
    check("P7. huỷ ở lượt SAU D+1 vẫn bắt được — bản cũ mù hoàn toàn với ca này",
          [c["kind"] for c in c4] == ["CANCELLED"] and cad.carry_forward(c4) == [], str(c4))

    # hết hạn kiểm
    old = [dict(p1[0], n_checks=cad.PENDING_MAX_CHECKS - 1)]
    c5 = cad.confirm_prior_triggers("2026-08-20", {"events_today": [], "pending_confirmations": old},
                                    rows_by_date={d: [r("AAA", "announced")]})
    check(f"P8. còn `announced` sau {cad.PENDING_MAX_CHECKS} lượt ⇒ UNRESOLVED_TIMEOUT và THÔI "
          "mang tiếp — báo người một lần rồi rút, không lặp cảnh báo tới khi hết ai đọc",
          [c["kind"] for c in c5] == ["UNRESOLVED_TIMEOUT"] and cad.carry_forward(c5) == [],
          str(c5))
    check("P9. CHỨNG MINH NGƯỢC cho P8: đúng một lượt TRƯỚC ngưỡng thì vẫn còn là STILL_ANNOUNCED "
          "và vẫn được mang tiếp (ngưỡng thật sự nằm ở đúng chỗ, không lệch một)",
          [c["kind"] for c in cad.confirm_prior_triggers(
              "2026-08-19",
              {"events_today": [], "pending_confirmations":
                  [dict(p1[0], n_checks=cad.PENDING_MAX_CHECKS - 2)]},
              rows_by_date={d: [r("AAA", "announced")]})] == ["STILL_ANNOUNCED"])

    # trùng giữa hàng treo và events_today
    dup = {"events_today": [r("AAA", "announced")],
           "pending_confirmations": [dict(p1[0], n_checks=3)]}
    c6 = cad.confirm_prior_triggers(d, dup, rows_by_date={d: [r("AAA", "announced")]})
    check("P10. cùng một sự kiện vừa nằm trong hàng treo vừa nằm trong `events_today` ⇒ MỘT dòng, "
          "và giữ n_checks THẬT (4) chứ không bị dòng mới reset về 1 — nếu không thì món treo tự "
          "làm mới đồng hồ mỗi ngày và KHÔNG BAO GIỜ chạm ngưỡng escalate",
          len(c6) == 1 and _f(c6, "n_checks") == 4, str(c6))

    # nhiều NGÀY sự kiện cùng lúc: món treo từ 08-12 + món mới ghi hôm 08-14
    c7 = cad.confirm_prior_triggers(
        "2026-08-14",
        {"events_today": [r("CCC", "announced", ex="2026-08-14")],
         "pending_confirmations": [dict(p1[0], n_checks=1)]},
        rows_by_date={d: [r("AAA", "not_executed")],
                      "2026-08-14": [r("CCC", "executed", ex="2026-08-14")]})
    check("P11. hàng treo NHIỀU NGÀY sự kiện khác nhau ⇒ mỗi ngày được hỏi bằng truy vấn của "
          "CHÍNH ngày đó, không dồn hết vào ngày mới nhất",
          {(c["ticker"], c["event_date"], c["kind"]) for c in c7}
          == {("AAA", d, "CANCELLED"), ("CCC", "2026-08-14", "CONFIRMED")}, str(c7))
    check("P12. điểm bơm `rows_by_date` KÍN: thiếu một ngày thì KHÔNG được lặng lẽ đi hỏi BQ "
          "(bộ này hermetic theo thiết kế) — ngày thiếu cho VANISHED, một kết quả NHÌN THẤY ĐƯỢC",
          [c["kind"] for c in cad.confirm_prior_triggers(
              "2026-08-14", {"events_today": [], "pending_confirmations": p1},
              rows_by_date={})] == ["VANISHED"])


# ───────────────────────────────────────────── phiên cron BỊ LỠ: phát hiện + backfill

def _ev(tk, d, status="announced", code="DIV", ev_id=None):
    """Một dòng sự kiện như `_events_on_sql` trả về (ex-right rơi đúng ngày `d`)."""
    return {"id": ev_id or f"id-{tk}-{d}", "ticker": tk, "event_code": code,
            "exright_date": d, "effective_date": None, "event_status": status,
            "value_per_share": 1000.0, "exercise_ratio": None, "issue_method_name_vi": None,
            "event_title_vi": f"{tk} {code} {d}"}


def _counting_fetch(by_date):
    """fetch giả + sổ ghi ngày đã hỏi — để đếm được ĐÚNG bao nhiêu ngày bị truy vấn (không thừa,
    không thiếu). Ngày không có trong `by_date` trả rỗng, KHÔNG nổ."""
    calls = []

    def fetch(d):
        calls.append(d)
        return list(by_date.get(d, []))
    return fetch, calls


def t_missed_runs():
    """Cron LỠ một phiên ⇒ sự kiện ngày đó phải được moi lại, không mất vĩnh viễn.

    Lỗ hổng (quant-skeptic khuyến nghị #5, vòng 2, nhắc lại vòng 3 như "the real remaining
    exposure"): `triggered_today` chỉ hỏi BQ cho ĐÚNG ngày hôm nay, và vòng xác nhận chỉ theo
    cái ĐÃ ghi — nên một lượt cron không chạy được làm sự kiện của ngày đó biến mất khỏi hệ mà
    không để lại dấu vết nào. Ca M0 dưới đây là bằng chứng lỗ hổng CÓ THẬT (chứng minh ngược),
    phần còn lại là bằng chứng nó đã được bịt.
    """
    print("== phiên cron BỊ LỠ: phát hiện theo LỊCH GIAO DỊCH + backfill ==")

    md, bfm = cad.missed_trading_days, cad.backfill_missed

    # ── (a) không lỡ phiên nào ⇒ HÀNH VI Y HỆT HIỆN TẠI
    check("M1. (ca a) lượt trước là đúng phiên liền trước ⇒ 0 phiên lỡ, không có gì đổi",
          md("2026-08-12", "2026-08-13") == [], str(md("2026-08-12", "2026-08-13")))
    check("M2. (ca a) T2 sau snapshot T6 ⇒ 0 phiên lỡ dù cách 3 NGÀY LỊCH — đếm bằng số ngày "
          "lịch sẽ báo động giả mỗi sáng thứ Hai",
          md("2026-08-14", "2026-08-17") == [], str(md("2026-08-14", "2026-08-17")))
    check("M3. (ca a) qua NGÀY LỄ (02/09) cũng 0 phiên lỡ — lịch lễ dùng chung "
          "`trading_bot.vn_market`, không tự khai bản thứ hai",
          md("2026-09-01", "2026-09-03") == [], str(md("2026-09-01", "2026-09-03")))
    check("M4. CHỨNG MINH NGƯỢC cho M3: cùng khoảng đó nhưng lùi mốc thêm 1 phiên thì 09-01 PHẢI "
          "hiện ra (cổng không phải lúc nào cũng trả rỗng)",
          md("2026-08-31", "2026-09-03") == ["2026-09-01"], str(md("2026-08-31", "2026-09-03")))

    # ── (b) lỡ đúng 1 phiên
    check("M5. (ca b) lỡ đúng 1 phiên ⇒ đúng 1 ngày", md("2026-08-11", "2026-08-13")
          == ["2026-08-12"], str(md("2026-08-11", "2026-08-13")))

    # ── (c) lỡ nhiều phiên liên tiếp
    check("M6. (ca c) cron chết 3 phiên ⇒ đủ 3 ngày, không thiếu ngày nào",
          md("2026-08-07", "2026-08-13") == ["2026-08-10", "2026-08-11", "2026-08-12"],
          str(md("2026-08-07", "2026-08-13")))
    check("M7. (ca c) khoảng lỡ VẮT QUA cuối tuần ⇒ chỉ đếm phiên giao dịch, T7/CN không phải "
          "phiên bị lỡ",
          md("2026-08-12", "2026-08-18") == ["2026-08-13", "2026-08-14", "2026-08-17"],
          str(md("2026-08-12", "2026-08-18")))

    check("M8. chưa từng có snapshot nào (`prev_asof=None`) ⇒ RỖNG — không có mốc thì không có "
          "khái niệm 'đã lỡ', và một lượt cron không được tự quyết backfill cả lịch sử",
          md(None, "2026-08-13") == [])
    check("M9. ngày HOÃN từ lượt trước được gộp vào, kể cả khi đã cũ hơn `prev_asof`; ngày ≥ hôm "
          "nay thì KHÔNG (chưa lỡ)",
          md("2026-08-12", "2026-08-13", deferred=["2026-07-20", "2026-08-13", "2026-08-99"])
          == ["2026-07-20"],
          str(md("2026-08-12", "2026-08-13", deferred=["2026-07-20", "2026-08-13"])))

    # ── backfill: truy vấn ĐÚNG ngày bị lỡ, không phải hôm nay
    f0, c0 = _counting_fetch({})
    b0 = bfm([], fetch=f0)
    check("M10. 0 phiên lỡ ⇒ KHÔNG một truy vấn nào (ca a không được tốn thêm gì)",
          c0 == [] and b0["events"] == [] and b0["ok"] is True, str(b0))

    rows = {"2026-08-10": [_ev("AAA", "2026-08-10", "executed")],
            "2026-08-11": [_ev("BBB", "2026-08-11"), _ev("CCC", "2026-08-11", "executed")],
            "2026-08-12": [_ev("DDD", "2026-08-12")]}
    f1, c1 = _counting_fetch(rows)
    b1 = bfm(["2026-08-12"], fetch=f1)
    check("M11. (ca b) lỡ 1 phiên ⇒ hỏi ĐÚNG ngày đó (không phải hôm nay), 1 sự kiện, có nhãn "
          "`backfilled` + `event_date` của chính ngày đó",
          c1 == ["2026-08-12"] and b1["n_events"] == 1
          and b1["events"][0]["ticker"] == "DDD"
          and b1["events"][0]["event_date"] == "2026-08-12"
          and b1["events"][0]["backfilled"] is True, str(b1))

    f2, c2 = _counting_fetch(rows)
    b2 = bfm(["2026-08-10", "2026-08-11", "2026-08-12"], fetch=f2)
    check("M12. (ca c) lỡ 3 phiên ⇒ hỏi ĐỦ 3 ngày, MỖI ngày ĐÚNG MỘT lần (không sót, không thừa)",
          c2 == ["2026-08-10", "2026-08-11", "2026-08-12"] and b2["n_events"] == 4
          and b2["days_backfilled"] == c2 and b2["deferred_days"] == [], str(b2))
    check("M13. (ca c) mỗi sự kiện mang ĐÚNG ngày sự kiện của nó — không bị dồn hết vào ngày mới "
          "nhất (nếu dồn thì vòng xác nhận sau đó sẽ hỏi sai ngày và báo VANISHED hàng loạt)",
          sorted((e["ticker"], e["event_date"]) for e in b2["events"])
          == [("AAA", "2026-08-10"), ("BBB", "2026-08-11"), ("CCC", "2026-08-11"),
              ("DDD", "2026-08-12")], str([(e["ticker"], e["event_date"]) for e in b2["events"]]))
    check("M14. gọi LẠI với cùng đầu vào cho kết quả GIỐNG HỆT (hàm thuần, không tích luỹ trạng "
          "thái ẩn giữa hai lần chạy)",
          bfm(["2026-08-10", "2026-08-11", "2026-08-12"], fetch=_counting_fetch(rows)[0])
          == b2)

    # ── trần + hoãn: không có cap im lặng
    many = [f"2026-06-{d:02d}" for d in range(1, 13)]              # 12 ngày (không cần là phiên)
    f3, c3 = _counting_fetch({})
    b3 = bfm(many, fetch=f3, max_days=10)
    check("M15. quá trần ⇒ backfill 10 ngày GẦN NHẤT, 2 ngày cũ nhất HOÃN (được ghi ra, không "
          "biến mất im lặng) và `ok=False`",
          c3 == many[2:] and b3["deferred_days"] == many[:2] and b3["ok"] is False, str(b3))
    check("M16. hàng HOÃN tự rút: lượt sau (không lỡ thêm phiên nào) nhặt đúng 2 ngày đó ra "
          "backfill ⇒ hàng đợi cạn, không có ngày nào kẹt lại vĩnh viễn",
          bfm(md("2026-08-12", "2026-08-13", deferred=b3["deferred_days"]),
              fetch=_counting_fetch({})[0], max_days=10)["days_backfilled"] == many[:2],
          str(md("2026-08-12", "2026-08-13", deferred=b3["deferred_days"])))

    # ── lỗi truy vấn: không nuốt, không làm hỏng cả lượt chạy
    def boom(d):
        if d == "2026-08-11":
            raise RuntimeError("BQ 503")
        return list(rows.get(d, []))

    b4 = bfm(["2026-08-10", "2026-08-11", "2026-08-12"], fetch=boom)
    check("M17. một ngày truy vấn LỖI ⇒ ngày đó vào `deferred_days` + `errors` (thử lại lượt "
          "sau), 2 ngày kia VẪN backfill xong, và hàm KHÔNG ném lỗi ra ngoài (mất snapshot hôm "
          "nay vì một ngày quá khứ là cái giá sai)",
          b4["days_backfilled"] == ["2026-08-10", "2026-08-12"]
          and b4["deferred_days"] == ["2026-08-11"] and len(b4["errors"]) == 1
          and "BQ 503" in b4["errors"][0]["error"] and b4["ok"] is False, str(b4))

    # ── nối vào vòng xác nhận: sự kiện backfill đi ĐÚNG đường của sự kiện ghi đúng ngày
    ex = "2026-08-12"
    conf = cad.confirm_prior_triggers(
        "2026-08-11", {"events_today": [], "pending_confirmations": []},
        backfilled=[dict(_ev("DDD", ex), event_date=ex, backfilled=True),
                    dict(_ev("EEE", ex, "executed"), event_date=ex, backfilled=True)],
        asof="2026-08-13",
        rows_by_date={ex: [_ev("DDD", ex), _ev("EEE", ex, "executed")]})
    check("M18. sự kiện backfill chảy vào ĐÚNG vòng xác nhận: cái `executed` ⇒ CONFIRMED, cái còn "
          "`announced` ⇒ STILL_ANNOUNCED",
          {(c["ticker"], c["kind"]) for c in conf}
          == {("DDD", "STILL_ANNOUNCED"), ("EEE", "CONFIRMED")}, str(conf))
    fwd = cad.carry_forward(conf)
    check("M19. cái còn `announced` được MANG SANG lượt sau, và giữ nhãn `backfilled` để người "
          "đọc snapshot phân biệt được 'ghi đúng ngày' với 'moi lại sau'",
          len(fwd) == 1 and fwd[0]["ticker"] == "DDD" and fwd[0]["backfilled"] is True, str(fwd))
    check("M20. `first_seen_asof` = NGÀY CHẠY chứ không phải ngày sự kiện — đồng hồ "
          f"`PENDING_MAX_CHECKS`={cad.PENDING_MAX_CHECKS} đếm số LƯỢT ĐÃ KIỂM; lấy ngày sự kiện "
          "làm mốc thì món backfill của 6 phiên trước hết hạn ngay lượt đầu",
          _f(conf, "first_seen_asof") == "2026-08-13" and _f(conf, "n_checks") == 1, str(conf))

    check("M0. CHỨNG MINH NGƯỢC — LỖ HỔNG CÓ THẬT: cùng snapshot đó nhưng KHÔNG có backfill "
          "(`backfilled=None`, tức bản trước bản này), sự kiện của phiên bị lỡ cho ĐÚNG 0 dòng — "
          "không ai biết nó từng tồn tại",
          cad.confirm_prior_triggers(
              "2026-08-11", {"events_today": [], "pending_confirmations": []},
              asof="2026-08-13", rows_by_date={ex: [_ev("DDD", ex)]}) == [])

    # ── (d) chạy lại cron 2 lần: không ghi trùng
    snap_run1 = {"events_today": [], "pending_confirmations": fwd}
    conf2 = cad.confirm_prior_triggers(
        "2026-08-13", snap_run1,
        backfilled=[dict(_ev("DDD", ex), event_date=ex, backfilled=True)],
        asof="2026-08-14", rows_by_date={ex: [_ev("DDD", ex)]})
    check("M21. (ca d) lượt sau backfill LẠI đúng ngày đó (vd ngày HOÃN được thử lại) trong khi "
          "món của chính ngày đó đang nằm trong hàng treo ⇒ MỘT dòng, không nhân đôi",
          len(conf2) == 1, str(conf2))
    check("M22. (ca d) và dòng thắng là dòng HÀNG TREO — giữ `n_checks` THẬT (2), không bị dòng "
          "backfill n_checks=0 reset đồng hồ; nếu bị reset thì món treo không bao giờ chạm ngưỡng "
          "escalate",
          _f(conf2, "n_checks") == 2 and _f(conf2, "first_seen_asof") == "2026-08-13", str(conf2))
    check("M23. (ca d) chạy y hệt lần thứ ba cho kết quả GIỐNG HỆT lần thứ hai — idempotent (§5)",
          cad.confirm_prior_triggers(
              "2026-08-13", snap_run1,
              backfilled=[dict(_ev("DDD", ex), event_date=ex, backfilled=True)],
              asof="2026-08-14", rows_by_date={ex: [_ev("DDD", ex)]}) == conf2)

    # ── hai lượt chạy nối tiếp thật sự: snapshot lượt 1 làm đầu vào lượt 2
    def one_run(prev_asof, prev_snap, asof, by_date, deferred_fetch=None):
        """Mô phỏng ĐÚNG chuỗi gọi của `run()`: dò phiên lỡ → backfill → xác nhận → snapshot."""
        bf = bfm(md(prev_asof, asof, (prev_snap or {}).get("backfill_deferred_days") or []),
                 fetch=deferred_fetch or (lambda d: list(by_date.get(d, []))))
        c = cad.confirm_prior_triggers(prev_asof, prev_snap, backfilled=bf["events"], asof=asof,
                                       rows_by_date=by_date)
        return {"events_today": [], "pending_confirmations": cad.carry_forward(c),
                "backfill_deferred_days": bf["deferred_days"], "_conf": c, "_bf": bf}

    by = {d: list(v) for d, v in rows.items()}
    s1 = one_run("2026-08-07", {}, "2026-08-13", by)          # cron chết 3 phiên
    check("M24. (ca c, đầu-cuối) một lượt chạy sau khi cron chết 3 phiên: 4 sự kiện của 3 ngày "
          "đều được ghi nhận, 2 cái còn `announced` mang sang lượt sau",
          s1["_bf"]["days_backfilled"] == ["2026-08-10", "2026-08-11", "2026-08-12"]
          and {(c["ticker"], c["kind"]) for c in s1["_conf"]}
          == {("AAA", "CONFIRMED"), ("BBB", "STILL_ANNOUNCED"), ("CCC", "CONFIRMED"),
              ("DDD", "STILL_ANNOUNCED")}
          and {p["ticker"] for p in s1["pending_confirmations"]} == {"BBB", "DDD"}, str(s1))
    s2 = one_run("2026-08-13", s1, "2026-08-13", by)           # CHẠY LẠI ĐÚNG NGÀY ĐÓ
    check("M25. (ca d) chạy lại cron NGAY trong cùng phiên: `prev_asof` giờ là hôm nay ⇒ 0 phiên "
          "lỡ, 0 truy vấn backfill, và hàng treo vẫn đúng 2 món — không nhân đôi",
          s2["_bf"]["days_missed"] == []
          and {p["ticker"] for p in s2["pending_confirmations"]} == {"BBB", "DDD"}
          and [p["n_checks"] for p in sorted(s2["_conf"], key=lambda c: c["ticker"])] == [2, 2],
          str(s2["_conf"]))
    by2 = {**by, "2026-08-11": [_ev("BBB", "2026-08-11", "executed")],
           "2026-08-12": [_ev("DDD", "2026-08-12", "not_executed")]}
    s3 = one_run("2026-08-13", s2, "2026-08-14", by2)
    check("M26. lượt kế: món backfill được theo TỚI KHI NGÃ NGŨ — BBB xác nhận, DDD lộ ra ĐÃ HUỶ "
          "(đây chính là cái mà một phiên bị lỡ trước đây giấu đi vĩnh viễn)",
          {(c["ticker"], c["kind"]) for c in s3["_conf"]}
          == {("BBB", "CONFIRMED"), ("DDD", "CANCELLED")}
          and s3["pending_confirmations"] == [], str(s3["_conf"]))

    # deferred sống qua lượt chạy
    s4 = one_run("2026-08-07", {}, "2026-08-13", by, deferred_fetch=boom)
    check("M27. ngày backfill LỖI được ghi vào `backfill_deferred_days` của snapshot — đây là "
          "đường DUY NHẤT tìm lại nó, vì lượt sau `prev_asof` đã nhảy qua nó rồi",
          s4["backfill_deferred_days"] == ["2026-08-11"], str(s4["backfill_deferred_days"]))
    s5 = one_run("2026-08-13", s4, "2026-08-14", by)
    check("M28. và lượt sau NHẶT LẠI đúng ngày đó (dù 08-11 đã nằm ngoài khoảng "
          "`prev_asof`→`asof`), backfill xong thì hàng hoãn RỖNG",
          s5["_bf"]["days_backfilled"] == ["2026-08-11"]
          and s5["backfill_deferred_days"] == []
          and {c["ticker"] for c in s5["_conf"] if c["event_date"] == "2026-08-11"}
          == {"BBB", "CCC"}, str(s5["_bf"]))

    # ── mốc "lượt chạy gần nhất" phải là ARTIFACT ĐÃ PUBLISH, không phải state file
    with tempfile.TemporaryDirectory() as tmp:
        old_out, old_state = cad.OUT_DIR, cad.STATE_PATH
        try:
            cad.OUT_DIR = os.path.join(tmp, "out")
            cad._atomic_write_json(cad.snapshot_path("2026-08-11"), {"asof": "2026-08-11"})
            cad._atomic_write_json(cad.snapshot_path("2026-08-12", True), {"status": "FAILED"})
            # `stale_streak` ghi `last_run` NGAY sau cổng freshness, tức TRƯỚC cả nhánh feed DEAD
            # ⇒ state file nhận ngày của một lượt chạy KHÔNG publish gì cả.
            cad.STATE_PATH = os.path.join(tmp, "state.json")
            cad.stale_streak("2026-08-12", "DEAD", "sig")
            st = json.load(open(cad.STATE_PATH, encoding="utf-8"))
            pa, _ps = cad.prior_snapshot("2026-08-13")
            check("M29. mốc dò phiên lỡ = SNAPSHOT ĐÃ PUBLISH gần nhất, KHÔNG phải `last_run` "
                  "của state file: lượt 08-12 hỏng (feed DEAD) vẫn ghi `last_run=2026-08-12` mà "
                  "không publish gì — lấy state làm mốc thì 08-12 bị NHẢY QUA vĩnh viễn, đúng "
                  "cái lỗ hổng đang vá. Lấy artifact làm mốc thì nó ĐƯỢC tính là phiên bị lỡ.",
                  st["last_run"] == "2026-08-12" and pa == "2026-08-11"
                  and md(pa, "2026-08-13") == ["2026-08-12"],
                  f"state.last_run={st['last_run']} prev_asof={pa} "
                  f"missed={md(pa, '2026-08-13')}")
        finally:
            cad.OUT_DIR, cad.STATE_PATH = old_out, old_state


def t_query_shape_live():
    """Tầng --live: chạy CHÍNH mệnh đề WHERE đó qua BigQuery thật.

    Ca hermetic ở trên là so chuỗi — nó bắt được bug vòng 1 nhưng không chứng minh được BQ hiểu
    mệnh đề đúng như ta nghĩ. Ở đây `table=` được thay bằng một bảng dựng tay inline, nên máy SQL
    THẬT chấm điểm, mà không đụng bảng production và không quét byte nào.
    """
    print("== --live: mệnh đề WHERE chạy thật trên BigQuery ==")
    from corp_action_lib import bq
    fake = """(SELECT * FROM UNNEST([
        STRUCT('ev-aaa' AS id, 'AAA' AS ticker, 'DIV' AS event_code,
               DATE '2026-08-13' AS exright_date,
               CAST(NULL AS DATE) AS effective_date, 'announced' AS event_status,
               1500.0 AS value_per_share, CAST(NULL AS FLOAT64) AS exercise_ratio,
               CAST(NULL AS STRING) AS issue_method_name_vi,
               CAST(NULL AS FLOAT64) AS shares_delta, CAST(NULL AS FLOAT64) AS shares_total_after,
               'AAA announced hom nay' AS event_title_vi),
        STRUCT('ev-bbb', 'BBB', 'DIV', DATE '2026-08-13', CAST(NULL AS DATE), 'executed',
               800.0, CAST(NULL AS FLOAT64), CAST(NULL AS STRING), CAST(NULL AS FLOAT64),
               CAST(NULL AS FLOAT64), 'BBB executed hom nay'),
        STRUCT('ev-ccc', 'CCC', 'DIV', DATE '2026-08-13', CAST(NULL AS DATE), 'not_executed',
               900.0, CAST(NULL AS FLOAT64), CAST(NULL AS STRING), CAST(NULL AS FLOAT64),
               CAST(NULL AS FLOAT64), 'CCC da huy'),
        STRUCT('ev-ddd', 'DDD', 'AIS', CAST(NULL AS DATE), DATE '2026-08-13', 'announced',
               CAST(NULL AS FLOAT64), CAST(NULL AS FLOAT64), CAST(NULL AS STRING),
               CAST(NULL AS FLOAT64), 123.0, 'DDD AIS hieu luc hom nay'),
        STRUCT('ev-eee', 'EEE', 'DIV', DATE '2026-08-14', CAST(NULL AS DATE), 'announced',
               700.0, CAST(NULL AS FLOAT64), CAST(NULL AS STRING), CAST(NULL AS FLOAT64),
               CAST(NULL AS FLOAT64), 'EEE ngay mai')]))"""
    got = {r["ticker"] for r in bq(cad._events_on_sql("2026-08-13", table=fake))}
    check("L1. máy SQL THẬT: dòng `announced` rơi đúng hôm nay ĐƯỢC lấy (AAA) — đây là ca mà "
          "bản vòng 1 trả rỗng", "AAA" in got, str(got))
    check("L2. `executed` vẫn lấy bình thường (BBB)", "BBB" in got, str(got))
    check("L3. `not_executed` bị loại (CCC), ngày mai bị loại (EEE)",
          "CCC" not in got and "EEE" not in got, str(got))
    check("L4. AIS vào theo `effective_date` qua nhánh OR (DDD)", "DDD" in got, str(got))
    everything = {r["ticker"] for r in
                  bq(cad._events_on_sql("2026-08-13", table=fake, include_cancelled=True))}
    check("L5. vòng xác nhận (`include_cancelled=True`) THẤY được dòng đã huỷ — nếu không, "
          "CANCELLED sẽ vĩnh viễn bị báo nhầm là VANISHED", "CCC" in everything, str(everything))

    # ── và trên BẢNG THẬT: chính con số quant-skeptic dùng để bác bỏ vòng 1
    real = cad._all_events_on("2026-08-13")
    check("L6. BẢNG THẬT ngày 2026-08-13 trả ≥1 dòng (quant-skeptic đo bản cũ: 0 dòng, trong khi "
          "có 4 sự kiện thật DHN/HGM/SAC DIV + BCF ISS)", len(real) >= 1,
          f"{len(real)} dòng: {sorted({r['ticker'] for r in real})}")
    check("L7. và chúng đúng là các mã đó (không phải lấy nhầm ngày khác)",
          {"DHN", "HGM", "SAC", "BCF"} <= {r["ticker"] for r in real},
          str(sorted({r["ticker"] for r in real})))


# ──────────────────────────────────────────────── vị thế thật + ghi snapshot

def t_positions_and_snapshot():
    print("== đọc vị thế thật (artifact 20:15 ICT) + snapshot có ngày trong tên ==")
    with tempfile.TemporaryDirectory() as tmp:
        for lb, computed, pos, exc in (
                ("SpaceX", "2026-08-12", [{"ticker": "ACB", "qty": 900},
                                          {"ticker": "DRI", "qty": 3700},
                                          {"ticker": "XXX", "qty": 0}], []),
                ("ZaloPay", "2026-07-20", [{"ticker": "DGC", "qty": 500}], ["DGC"])):
            with open(os.path.join(tmp, f"active_nav_{lb}.json"), "w", encoding="utf-8") as f:
                json.dump({"account": lb, "computed_at": computed, "positions": pos,
                           "excluded_tickers": exc}, f)
        p = cad.read_positions(nav_glob=os.path.join(tmp, "active_nav_*.json"),
                               asof="2026-08-13")
        check("P1. đọc đúng 2 account từ artifact, qty=0 bị loại",
              set(p) == {"SpaceX", "ZaloPay"} and p["SpaceX"]["positions"] == {"ACB": 900,
                                                                               "DRI": 3700},
              str(p["SpaceX"]["positions"]))
        check("P2. vị thế BỊ LOẠI khỏi rebalancing (DGC) VẪN nằm trong danh sách — không giao "
              "dịch nó không có nghĩa là không sở hữu nó",
              p["ZaloPay"]["positions"] == {"DGC": 500}
              and p["ZaloPay"]["excluded_tickers"] == ["DGC"])
        check("P3. artifact cũ 24 ngày ⇒ stale_days đúng để tầng trên cảnh báo",
              p["ZaloPay"]["stale_days"] == 24 and p["SpaceX"]["stale_days"] == 1,
              f"{p['ZaloPay']['stale_days']} / {p['SpaceX']['stale_days']}")

        old_out = cad.OUT_DIR
        try:
            cad.OUT_DIR = os.path.join(tmp, "out")
            check("P4. tên snapshot mang NGÀY, và bản hỏng mang hậu tố _FAILED (§8: không bao giờ "
                  "ghi vào một tên canonical)",
                  cad.snapshot_path("2026-08-13").endswith("corp_action_daily_2026-08-13.json")
                  and cad.snapshot_path("2026-08-13", True).endswith("_2026-08-13_FAILED.json"))
            for d, body in (("2026-08-10", {"tickers": {"A": {"value": 1}}}),
                            ("2026-08-12", {"tickers": {"A": {"value": 2}}})):
                cad._atomic_write_json(cad.snapshot_path(d), body)
            cad._atomic_write_json(cad.snapshot_path("2026-08-12", True), {"status": "FAILED"})
            pa, ps = cad.prior_snapshot("2026-08-13")
            check("P5. mốc so sánh = snapshot ĐÃ PUBLISH gần nhất; bản _FAILED cùng ngày KHÔNG "
                  "được làm mốc (một lần chạy hỏng không được tự hợp thức hoá)",
                  pa == "2026-08-12" and ps["tickers"]["A"]["value"] == 2, f"{pa} {ps}")
            check("P6. chưa có snapshot nào trước đó ⇒ (None, None), không nổ",
                  cad.prior_snapshot("2026-08-01") == (None, None))
            check("P7. ghi atomic — không để lại file .tmp nào sau khi ghi xong",
                  not [f for f in os.listdir(cad.OUT_DIR) if ".tmp." in f],
                  str(os.listdir(cad.OUT_DIR)))
        finally:
            cad.OUT_DIR = old_out


# ───────────────────────────────────────────────────── kênh báo + hành vi im lặng

def t_notify():
    print("== kênh báo: tra registry theo TÊN, và --no-alert phải THẬT SỰ câm ==")
    from discord_channels import resolve
    check("N1. kênh khai bằng TÊN có thật trong kb/discord_channels.json (bài học Việc D: "
          "hardcode ID là cách rò rỉ chéo topic)", bool(resolve(cad.CHANNEL)))
    check("N2. không có ID Discord trần (17-20 chữ số) nào trong file",
          not __import__("re").search(r"\b[0-9]{17,20}\b",
                                      open(os.path.join(os.path.dirname(
                                          os.path.abspath(__file__)), "corp_action_daily.py"),
                                          encoding="utf-8").read()))

    called = []
    orig = subprocess.run
    subprocess.run = lambda *a, **k: called.append(a) or orig(["true"], capture_output=True)
    try:
        cad.notify("thử", enabled=False)
        check("N3. enabled=False ⇒ KHÔNG gọi tiến trình gửi nào (chạy tay/dry-run không ping "
              "người thật)", called == [], str(called))
        cad.notify("thử", enabled=True, telegram=True)
        check("N4. HIGH ⇒ gọi CẢ notify_thread.sh (Discord) VÀ notify.sh (Telegram)",
              len(called) == 2
              and called[0][0][0].endswith("notify_thread.sh")
              and called[1][0][0].endswith("notify.sh"), str([c[0][0] for c in called]))
        check("N5. đối số 2 của notify_thread.sh là TÊN kênh, không phải ID",
              called[0][0][2] == "trading_daily", str(called[0][0]))
    finally:
        subprocess.run = orig


# ────────────────────────────────────────────── chạy lại dưới env THÙ ĐỊCH (TZ)

def t_tz_hostile():
    print("== chạy lại phần ngày/giờ dưới env THÙ ĐỊCH (§16 + verify-before-done) ==")
    probe = (
        "import sys, json;"
        f"sys.path.insert(0, {os.path.dirname(os.path.abspath(__file__))!r});"
        f"sys.path.insert(0, {os.environ.get('WORKDIR_8L', '/home/trido/thanhdt/WorkingClaude')!r});"
        "import corp_action_daily as c;"
        "f={'max_ingested':'2026-08-12 18:30:00+00'};"
        "s,d=c.gate_freshness('2026-08-13', fresh=f);"
        "print(json.dumps([s, d['max_ingested_ict'], d['prev_trading_day'],"
        " c.prev_trading_day(__import__('datetime').date(2026,8,17)).isoformat()]))")
    base = None
    for env_desc, env in (("TZ=Asia/Ho_Chi_Minh", {"TZ": "Asia/Ho_Chi_Minh"}),
                          ("KHÔNG có TZ", {}),
                          ("TZ=America/New_York", {"TZ": "America/New_York"}),
                          ("TZ=UTC", {"TZ": "UTC"})):
        e = {k: v for k, v in os.environ.items() if k != "TZ"}
        e.update(env)
        r = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                           timeout=180, env=e)
        got = (r.stdout or "").strip().splitlines()[-1:] or [f"rc={r.returncode} {r.stderr[-200:]}"]
        if base is None:
            base = got[0]
        check(f"TZ1. kết quả GIỐNG HỆT dưới {env_desc}", got[0] == base, got[0])
    check("TZ2. và kết quả đó ĐÚNG (18:30 UTC ⇒ 2026-08-13 ICT, FRESH, phiên trước 08-12; "
          "T2 17/08 lùi về T6 14/08)",
          base == json.dumps(["FRESH", "2026-08-13T01:30:00+07:00", "2026-08-12", "2026-08-14"]),
          str(base))


def main():
    live = "--live" in sys.argv
    print(f"== corp_action_daily_selfcheck (hermetic — không BQ/Discord"
          f"{'; + tầng --live CÓ chạm BQ' if live else ''}) ==\n")
    t_gate_selfcheck()
    t_freshness()
    t_invariants()
    t_crosscheck()
    t_render_divergence()
    t_none_value_watch()
    t_magnitude_gate()
    t_triggers_and_alerts()
    t_query_shape()
    t_confirm_unique_key()
    t_carry_forward()
    t_missed_runs()
    t_positions_and_snapshot()
    t_notify()
    t_tz_hostile()
    # tách tầng vì cron gọi bộ này ở chế độ hermetic: một hôm BQ hỏng KHÔNG được biến thành
    # "code sai". Ca --live là bằng chứng nghiệm thu, chạy tay, không phải cổng chặn hằng ngày.
    if live:
        t_query_shape_live()
    print()
    if FAILS:
        print(f"FAILED {len(FAILS)}/{len(RAN)}: {FAILS}")
        return 1
    print(f"OK — corp_action_daily selfcheck PASS {len(RAN)}/{len(RAN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

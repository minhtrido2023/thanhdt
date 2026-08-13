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


def t_query_shape_live():
    """Tầng --live: chạy CHÍNH mệnh đề WHERE đó qua BigQuery thật.

    Ca hermetic ở trên là so chuỗi — nó bắt được bug vòng 1 nhưng không chứng minh được BQ hiểu
    mệnh đề đúng như ta nghĩ. Ở đây `table=` được thay bằng một bảng dựng tay inline, nên máy SQL
    THẬT chấm điểm, mà không đụng bảng production và không quét byte nào.
    """
    print("== --live: mệnh đề WHERE chạy thật trên BigQuery ==")
    from corp_action_lib import bq
    fake = """(SELECT * FROM UNNEST([
        STRUCT('AAA' AS ticker, 'DIV' AS event_code, DATE '2026-08-13' AS exright_date,
               CAST(NULL AS DATE) AS effective_date, 'announced' AS event_status,
               1500.0 AS value_per_share, CAST(NULL AS FLOAT64) AS exercise_ratio,
               CAST(NULL AS STRING) AS issue_method_name_vi,
               CAST(NULL AS FLOAT64) AS shares_delta, CAST(NULL AS FLOAT64) AS shares_total_after,
               'AAA announced hom nay' AS event_title_vi),
        STRUCT('BBB', 'DIV', DATE '2026-08-13', CAST(NULL AS DATE), 'executed',
               800.0, CAST(NULL AS FLOAT64), CAST(NULL AS STRING), CAST(NULL AS FLOAT64),
               CAST(NULL AS FLOAT64), 'BBB executed hom nay'),
        STRUCT('CCC', 'DIV', DATE '2026-08-13', CAST(NULL AS DATE), 'not_executed',
               900.0, CAST(NULL AS FLOAT64), CAST(NULL AS STRING), CAST(NULL AS FLOAT64),
               CAST(NULL AS FLOAT64), 'CCC da huy'),
        STRUCT('DDD', 'AIS', CAST(NULL AS DATE), DATE '2026-08-13', 'announced',
               CAST(NULL AS FLOAT64), CAST(NULL AS FLOAT64), CAST(NULL AS STRING),
               CAST(NULL AS FLOAT64), 123.0, 'DDD AIS hieu luc hom nay'),
        STRUCT('EEE', 'DIV', DATE '2026-08-14', CAST(NULL AS DATE), 'announced',
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
    t_triggers_and_alerts()
    t_query_shape()
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

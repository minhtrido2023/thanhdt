#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho SỐ HẠNG DÒNG TIỀN của tỉ suất công bố (FAIL-H, audit measurement-integrity
2026-09-27) + cổng NAV-jump fail-closed ở `report_delivery_gate.py`.

Hai assertion cốt lõi mà audit yêu cầu:
  1. Nạp +200tr GIỮA KỲ ⇒ `return_pct` KHÔNG đổi (bản cũ: +3,0% thành +22,8%).
  2. Nạp mà KHÔNG ghi nhận ⇒ cổng CHẶN (raise), không cho gửi báo cáo.

Chạy: python3 mike/bin/nav_flow_term_selfcheck.py
      TZ=UTC python3 mike/bin/nav_flow_term_selfcheck.py      (§16 — phải PASS y nguyên)
Không đọc mạng, không gọi BQ, không ghi vào bất kỳ file canonical nào (mọi fixture ở tempdir).
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

import account_cash_flows as acf                      # noqa: E402
import nav_period_returns as npr                      # noqa: E402

D = datetime.date
INCEPTION = {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000}
# Chuỗi NAV nền: 4 mốc, lợi nhuận thật +3,0% từ 1,0B (không có dòng tiền nào).
BASE = [(D(2026, 7, 1), 1_000_000_000.0), (D(2026, 7, 2), 1_010_000_000.0),
        (D(2026, 7, 3), 1_020_000_000.0), (D(2026, 7, 6), 1_030_000_000.0)]
FLOW_DAY = D(2026, 7, 3)
N = 0


def ok(cond, msg):
    global N
    if not cond:
        raise AssertionError(msg)
    N += 1


def rows_only(seq):
    """nav_history thật KHÔNG có dòng ngày inception (07-01) — baseline đến từ starting_capital.
    Mỗi dòng mang `balance_ts` 19:10 cùng ngày (luật gán dòng tiền so với mốc này)."""
    return [acf.NavRow(d, nav, balance_ts=f"{d}T19:10:00") for d, nav in seq if d != D(2026, 7, 1)]


def must(fn, label):
    """`fn()` KHÔNG được raise — đầu vào hợp lệ mà bị từ chối phải thành ASSERTION, không sập."""
    try:
        return fn()
    except AssertionError:
        raise
    except Exception as exc:                                    # noqa: BLE001
        raise AssertionError(f"{label}: không được raise, được {type(exc).__name__}: {exc}") from exc


def with_flow(amount, timing):
    """Chuỗi NAV thật SẼ được ghi nhận nếu dòng tiền `amount` xảy ra ở FLOW_DAY, với CÙNG chuỗi
    lợi nhuận nền. Đây là điểm mấu chốt: cùng hiệu suất, chỉ khác vốn ⇒ TWR phải không đổi."""
    out = []
    prev_base = None
    for i, (d, nav) in enumerate(BASE):
        if i == 0:
            out.append((d, nav))
            prev_base = nav
            continue
        underlying = nav / BASE[i - 1][1]
        if d == FLOW_DAY and timing == "bod":
            new = (prev_base + amount) * underlying
        elif d == FLOW_DAY and timing == "eod":
            new = prev_base * underlying + amount
        else:
            new = prev_base * underlying
        out.append((d, new))
        prev_base = new
    return out


def flows_file(tmp, records, account="SpaceX"):
    path = Path(tmp) / "account_cash_flows.json"
    path.write_text(json.dumps({account: records}, ensure_ascii=False), encoding="utf-8")
    return str(path)


def ret(rows, flows):
    return npr.compute_period_returns("SpaceX", D(2026, 7, 6), rows, INCEPTION, flows)


def main():
    tmp = tempfile.mkdtemp(prefix="navflow_selfcheck_")

    # ---- 1. Không có dòng tiền: TWR == ĐÚNG công thức cũ nav1/nav0, và không thêm field nào.
    base_rows = rows_only(BASE)
    r0 = ret(base_rows, [])
    ok(r0["inception"]["return_pct"] == 3.0, f"nền phải +3,0%, được {r0['inception']['return_pct']}")
    ok("net_flow_vnd" not in r0["inception"] and "cash_flows" not in r0["inception"],
       "kỳ không có dòng tiền KHÔNG được thêm field (giữ output byte-identical)")
    ok(r0["inception"]["return_pct"] == round((base_rows[-1][1] / 1_000_000_000.0 - 1) * 100, 3),
       "không có flow ⇒ phải trùng ĐÚNG nav1/nav0 − 1")

    # ---- 2. YÊU CẦU CHÍNH: nạp +200tr giữa kỳ (bod) ⇒ return_pct KHÔNG đổi.
    dep_rows = rows_only(with_flow(+200_000_000, "bod"))
    fl = [{"date": "2026-07-03", "amount_vnd": 200_000_000, "kind": "deposit",
           "evidence": "selfcheck fixture", "timing": "bod", "time_ict": "10:30"}]
    rd = ret(dep_rows, acf.load_flows("SpaceX", flows_file(tmp, fl)))
    ok(rd["inception"]["return_pct"] == 3.0,
       f"nạp 200tr giữa kỳ: return_pct phải giữ +3,0%, được {rd['inception']['return_pct']}")
    naive = round((dep_rows[-1][1] / 1_000_000_000.0 - 1) * 100, 3)
    ok(naive > 20.0, f"sanity: công thức CŨ phải cho số sai to (được {naive}%)")
    ok(rd["inception"]["net_flow_vnd"] == 200_000_000 and len(rd["inception"]["cash_flows"]) == 1,
       "kỳ có dòng tiền phải công khai net_flow_vnd + cash_flows")
    # WTD/MTD của cùng report_date cũng phải sạch (flow nằm trong cả 2 kỳ)
    ok(rd["mtd"]["return_pct"] == round((dep_rows[-1][1] / (dep_rows[0][1] + 200_000_000)
                                        * (dep_rows[0][1] / 1_000_000_000.0) - 1) * 100, 3)
       or abs(rd["mtd"]["return_pct"] - 3.0) < 1e-9,
       f"MTD cũng phải khử dòng tiền, được {rd['mtd']['return_pct']}")

    # ---- 3. Rút −100tr (eod) ⇒ return_pct KHÔNG đổi.
    wd_rows = rows_only(with_flow(-100_000_000, "eod"))
    fl = [{"date": "2026-07-03", "amount_vnd": -100_000_000, "kind": "withdraw",
           "evidence": "selfcheck fixture", "timing": "eod", "time_ict": "16:00"}]
    rw = ret(wd_rows, acf.load_flows("SpaceX", flows_file(tmp, fl)))
    ok(abs(rw["inception"]["return_pct"] - 3.0) < 1e-9,
       f"rút 100tr (eod): return_pct phải giữ +3,0%, được {rw['inception']['return_pct']}")
    naive_w = round((wd_rows[-1][1] / 1_000_000_000.0 - 1) * 100, 3)
    ok(naive_w < -5.0, f"sanity: công thức CŨ phải báo LỖ giả (được {naive_w}%)")

    # ---- 4. Hai thời điểm tiền vào KHÔNG tương đương (nên phải khai GIỜ, code không đoán).
    bod_on_eod_series = ret(rows_only(with_flow(+200_000_000, "eod")),
                            acf.load_flows("SpaceX", flows_file(tmp, [
                                {"date": "2026-07-03", "amount_vnd": 200_000_000,
                                 "kind": "deposit", "evidence": "x", "timing": "bod",
                                 "time_ict": "10:30"}])))
    ok(bod_on_eod_series["inception"]["return_pct"] != 3.0,
       "khai SAI giờ tiền vào phải ra số KHÁC — nếu bằng nhau thì giờ khai là vô nghĩa")

    # ---- 5. Vốn khởi điểm KHÔNG phải flow: bản ghi ngày inception bị BỎ.
    r_inc = ret(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-07-01", "amount_vnd": 1_000_000_000, "kind": "deposit",
         "time_ict": "09:00", "evidence": "vốn khởi điểm — KHÔNG được tính lần hai"}])))
    ok(r_inc["inception"]["return_pct"] == 3.0,
       f"flow ngày inception phải bị bỏ, được {r_inc['inception']['return_pct']}")
    ok(len(r_inc["dropped_flows"]) == 1 and r_inc["pending_flows"] == [],
       f"flow bị bỏ phải HIỆN ở dropped_flows, được {r_inc['dropped_flows']}")

    # ---- 6. Flow sau lần chụp NAV cuối cùng: TREO — không vào số nào, không crash, và HIỆN ra.
    r_after = ret(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-12-31", "amount_vnd": 500_000_000, "kind": "deposit", "evidence": "x",
         "time_ict": "10:00"}])))
    ok(r_after["inception"]["return_pct"] == 3.0, "flow treo không được đổi tỉ suất")
    ok(len(r_after["pending_flows"]) == 1 and r_after["pending_flows"][0]["amount_vnd"] == 500e6
       and "net_flow_vnd" not in r_after["inception"],
       f"flow treo phải HIỆN ở pending_flows (không vô hình), được {r_after['pending_flows']}")

    # ---- 7. Flow ngày KHÔNG có phiên rơi vào phiên kế tiếp (dòng NAV đầu tiên chụp sau nó).
    mapped = acf.attach_flows_to_rows(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-07-04", "amount_vnd": 1, "kind": "deposit", "evidence": "thứ Bảy",
         "timing": "bod", "time_ict": "09:00"}])))
    ok(list(mapped) == [D(2026, 7, 6)] and mapped[D(2026, 7, 6)][0]["timing"] == "bod"
       and mapped[D(2026, 7, 6)][0]["session_date"] == D(2026, 7, 6),
       f"flow thứ Bảy 07-04 phải gán vào phiên 07-06 (bod), được {mapped}")

    # ---- 8. Schema fail-closed: 10 bản ghi hỏng, tất cả phải raise CashFlowError.
    bad = [
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit"},                     # thiếu evidence
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "  "},   # evidence rỗng
        {"date": "03/07/2026", "amount_vnd": 1, "kind": "deposit", "evidence": "x"},    # date sai
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "nap", "evidence": "x"},        # kind lạ
        {"date": "2026-07-03", "amount_vnd": 5, "kind": "market_only", "evidence": "x"},  # !=0
        {"date": "2026-07-03", "amount_vnd": -1, "kind": "deposit", "evidence": "x"},   # sai dấu
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "timing": "intraday"},                                                        # timing lạ
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "timing": "bod"},                                              # không khai giờ
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x"},  # không giờ, không timing
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "time_ict": "25:00"},                                          # giờ không hợp lệ
    ]
    for rec in bad:
        try:
            acf.load_flows("SpaceX", flows_file(tmp, [rec]))
            raise AssertionError(f"bản ghi hỏng phải raise: {rec}")
        except acf.CashFlowError:
            N_before = N
            ok(True, "")
            del N_before
    # KHÔNG có mặc định timing: không khai ⇒ None (code suy khi gán); giờ được chuẩn hoá.
    dflt = acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "time_ict": "16:00"},
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "timing": "bod", "time_ict": "9:05"}]))
    ok([f["timing"] for f in dflt] == ["bod", None] and not hasattr(acf, "DEFAULT_TIMING"),
       f"không khai timing phải là None (không mặc định), được {[f['timing'] for f in dflt]}")
    ok([f["time_ict"] for f in dflt] == ["09:05", "16:00"],
       f"time_ict phải chuẩn hoá HH:MM và sắp theo giờ, được {[f['time_ict'] for f in dflt]}")
    got = must(lambda: acf.attach_flows_to_rows(base_rows, dflt), "gán 2 bản ghi cùng ngày")
    ok([f["timing"] for f in got[D(2026, 7, 3)]] == ["bod", "eod"],
       f"09:05 ⇒ bod, 16:00 ⇒ eod trên cùng phiên 07-03, được {got}")
    # khai timing KHÁC kết quả suy ra ⇒ raise, nêu cả hai (không âm thầm chọn một bên)
    try:
        acf.attach_flows_to_rows(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
            {"date": "2026-07-04", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
             "timing": "eod", "time_ict": "10:00"}])))
        raise AssertionError("khai eod cho tiền thứ Bảy (suy ra bod trên 07-06) phải raise")
    except acf.CashFlowError as exc:
        ok("timing='eod'" in str(exc) and "'bod'" in str(exc) and "2026-07-06" in str(exc),
           f"thông điệp phải nêu cả quy ước khai lẫn quy ước suy ra, được: {exc}")

    # ---- 9. Cổng NAV-jump: nạp mà KHÔNG ghi nhận ⇒ CHẶN; ghi nhận ⇒ mở.
    import report_delivery_gate as gate
    jump_rows = rows_only(BASE + [(D(2026, 7, 7), 1_240_000_000.0)])   # +20,4% trong 1 phiên
    npr_orig = npr.load_nav_history
    npr.load_nav_history = lambda account, *a, **k: jump_rows
    report = Path("SpaceX_weekly_report_2026-07-01_to_2026-07-07.md")
    try:
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [])
        try:
            gate._check_nav_flow_records(report)
            raise AssertionError("cổng PHẢI chặn bước nhảy +20% không có bản ghi dòng tiền")
        except RuntimeError as exc:
            ok("nav-flow BLOCK" in str(exc) and "2026-07-07" in str(exc),
               f"thông điệp chặn phải nêu đúng ngày + lý do, được: {exc}")
        # ghi nhận deposit ⇒ mở cổng
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-07", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "10:00", "evidence": "sao kê DNSE"}])
        must(lambda: gate._check_nav_flow_records(report), "cổng với deposit đã ghi nhận")
        ok(True, "")
        # nạp thứ Bảy 07-04 KHÔNG giải thích bước nhảy thứ Ba 07-07 (nó được gán vào thứ Hai 07-06)
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-04", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "10:00", "evidence": "sao kê DNSE"}])
        try:
            gate._check_nav_flow_records(report)
            raise AssertionError("bản ghi gán vào phiên KHÁC không được mở cổng cho bước nhảy 07-07")
        except RuntimeError as exc:
            ok("nav-flow BLOCK" in str(exc) and "2026-07-07" in str(exc), f"sai thông điệp: {exc}")
        # ...còn nạp 20:00 thứ Hai 07-06 (sau lần chụp 19:10) thì ĐÚNG là của phiên 07-07
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-06", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "20:00", "evidence": "sao kê DNSE"}])
        must(lambda: gate._check_nav_flow_records(report), "cổng với nạp tối hôm trước")
        ok(True, "")
        # bản ghi thiếu giờ ⇒ cổng CHẶN (fail-closed), không sập và không cho qua
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-07", "amount_vnd": 200_000_000, "kind": "deposit", "evidence": "x"}])
        try:
            gate._check_nav_flow_records(report)
            raise AssertionError("bản ghi thiếu time_ict phải làm cổng CHẶN")
        except RuntimeError as exc:
            ok("nav-flow BLOCK" in str(exc) and "thiếu time_ict" in str(exc), f"sai thông điệp: {exc}")
        # market_only có bằng chứng ⇒ cũng mở (ngày biến động thị trường thật)
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-07", "amount_vnd": 0, "kind": "market_only",
             "evidence": "đối soát fill: toàn bộ biến động từ giá"}])
        must(lambda: gate._check_nav_flow_records(report), "cổng với market_only")
        ok(True, "")
        # báo cáo KHÔNG phải của account ⇒ cổng bỏ qua, không chặn oan
        # bước nhảy SAU ngày báo cáo không thuộc báo cáo này: kỳ tới 07-06 thì 07-07 không chặn
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [])
        must(lambda: gate._check_nav_flow_records(Path("SpaceX_weekly_report_2026-07-01_to_2026-07-06.md")),
             "cổng với bước nhảy sau ngày báo cáo")
        ok(True, "")
        # bản ghi hợp lệ nhưng KHÔNG GÁN được (nav_history thiếu balance_ts) ⇒ CHẶN, không sập
        npr.load_nav_history = lambda account, *a, **k: [tuple(r) for r in jump_rows]
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-07", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "10:00", "evidence": "sao kê DNSE"}])
        try:
            gate._check_nav_flow_records(report)
            raise AssertionError("bản ghi không gán được phải làm cổng CHẶN")
        except RuntimeError as exc:
            ok("nav-flow BLOCK" in str(exc) and "không có balance_ts" in str(exc), f"sai thông điệp: {exc}")
        except Exception as exc:                                    # noqa: BLE001
            raise AssertionError(f"cổng phải CHẶN bằng RuntimeError, lại sập {type(exc).__name__}: {exc}") from exc
        npr.load_nav_history = lambda account, *a, **k: jump_rows
        must(lambda: gate._check_nav_flow_records(Path("spend_report_weekly_2026-09-27.md")),
             "cổng với báo cáo không phải của account")
        ok(True, "")
        # tên file không có ngày ⇒ CHẶN (fail-closed, không đoán kỳ)
        try:
            gate._check_nav_flow_records(Path("SpaceX_weekly_report.md"))
            raise AssertionError("thiếu ngày trong tên file phải chặn (fail-closed)")
        except RuntimeError:
            ok(True, "")
    finally:
        npr.load_nav_history = npr_orig
        os.environ.pop("ACCOUNT_CASH_FLOWS_PATH", None)

    # ---- 9b. `deliver()` PHẢI gọi cổng — test hàm không bắt được việc tháo lời gọi (mutation M6).
    gate_src = (BIN / "report_delivery_gate.py").read_text(encoding="utf-8")
    ok("_check_nav_flow_records(report)" in gate_src.split("def deliver(")[1],
       "deliver() phải gọi _check_nav_flow_records — thiếu lời gọi thì cổng là trang trí")

    # ---- 10. Ngưỡng 5,0% có 0 false-positive trên TOÀN BỘ lịch sử thật của 2 TK.
    total = 0
    for account in ("SpaceX", "ZaloPay"):
        rows = npr.load_nav_history(account)
        total += len(rows) - 1
        jumps = acf.unexplained_nav_jumps(rows, [])
        ok(not jumps, f"{account}: ngưỡng {acf.NAV_JUMP_BLOCK_PCT}% phải 0 false-positive trên "
                      f"lịch sử thật, được {[(str(j['date']), round(j['change_pct'], 2)) for j in jumps]}")
    ok(total >= 110, f"phải kiểm >=110 cặp phiên thật, chỉ có {total}")

    # ---- 11. Không có flow ⇒ output trùng ĐÚNG số cũ trên TOÀN BỘ ngày thật của 2 TK.
    for account in ("SpaceX", "ZaloPay"):
        rows = npr.load_nav_history(account)
        inc = npr.load_inception(account)
        f0, n0 = npr._inception_baseline(rows, inc)
        for d, nav in rows:
            r = npr.compute_period_returns(account, d, rows, inc, [])
            ok(r["inception"]["return_pct"] == round((nav / n0 - 1) * 100, 3),
               f"{account} {d}: TWR không-flow phải == nav1/nav0 − 1")

    # ---- 12. §16 — report_date mặc định neo ICT, không theo TZ của tiến trình.
    outs = set()
    for tz in ("UTC", "Pacific/Kiritimati", "America/Los_Angeles"):
        env = dict(os.environ, TZ=tz)
        env.pop("ACCOUNT_CASH_FLOWS_PATH", None)
        p = subprocess.run([sys.executable, str(BIN / "nav_period_returns.py"),
                            "--account", "SpaceX"], capture_output=True, text=True, env=env)
        outs.add((p.returncode, p.stdout))
    ok(len(outs) == 1, f"report_date mặc định phải giống nhau dưới 3 TZ, được {len(outs)} kết quả")

    print(f"OK — {N} assertion PASS (nav_flow_term_selfcheck.py) · "
          f"ngưỡng cổng {acf.NAV_JUMP_BLOCK_PCT}% · {total} cặp phiên thật kiểm false-positive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Selfcheck — cổng KHỐI LƯỢNG của daily_nav_snapshot.main() hợp nhất fill journal bot + statement DNSE.

Ca gốc 2026-10-21: user bán TAY DRI (SpaceX 3.700→2.500, ZaloPay 1.900→1.300 @15.400) ⇒ journal bot
trống ⇒ net_fill=0 ⇒ qty_unexplained ⇒ rc=5 ⇒ mất dòng NAV 21/10. Chạy main() THẬT (đường --from-raw)
trong thư mục tạm — KHÔNG đọc/ghi data/execution_logs thật, KHÔNG gọi DNSE/Gmail/BQ.
Chạy dưới 3 TZ: env -u TZ / TZ=UTC / TZ=Asia/Ho_Chi_Minh.   exit 0 = PASS.
"""
import contextlib
import csv
import io
import json
import os
import sys
import tempfile
import types

TZ_AT_START = os.environ.get("TZ")
os.environ["NAV_SANITY_MAX_PCT"] = "1000"   # sandbox NAV ~90tr vs vốn 10tr: chỉ tắt cổng nhảy NAV, không liên quan cổng KL
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import daily_nav_snapshot as D  # noqa: E402
import exdate_frame as X  # noqa: E402
import verify_account_snapshot as V  # noqa: E402

SPX, ZLP = "0002023347", "0001743768"
D0, D1 = "2026-10-20", "2026-10-21"
FAILS = []


def check(name, cond, info=""):
    print(f"  {'PASS' if cond else 'FAIL'} {name}" + (f" — {info}" if info and not cond else ""))
    if not cond:
        FAILS.append(name)


def write_statement(tmp, rows):
    with open(os.path.join(tmp, "dnse_khoplenh_broker_confirm_21-10-2026.csv"), "w",
              newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ngay_gd", "loai_lenh", "ma", "tieu_khoan", "khoi_luong", "gia_khop",
                    "gia_tri_khop", "ty_le_phi", "phi_tra_so", "phi_dnse", "thue"])
        for side, tk, acct, q in rows:
            w.writerow(["21/10/2026", side, tk, acct, q, 15400, 0, 0.00088, 0, 0, 0])


def run_main(label, acct, qty_prev, qty_now, statement=None, ca_event=None):
    """D.main() thật, --from-raw, sandbox. Trả (rc, stderr, nav_history_tồn_tại, gate_block_json)."""
    root = tempfile.mkdtemp(prefix="dnsbf_")
    tmp = os.path.join(root, "data", "execution_logs")
    os.makedirs(tmp)
    os.makedirs(os.path.join(root, "secrets"))
    with open(os.path.join(root, "secrets", "trading_bot_accounts.json"), "w") as f:
        json.dump({"accounts": {"SpaceX": {"account_id": SPX}, "ZaloPay": {"account_id": ZLP}}}, f)
    if statement is not None:
        write_statement(tmp, statement)
    with open(os.path.join(tmp, f"exec_{label}_{D0}_journal.csv"), "w") as f:
        f.write("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
    def _rec(kind, day, acct, payload):
        return json.dumps({"kind": kind, "ts": f"{day}T19:10:00", "account_no": acct,
                           "payload": payload}) + "\n"
    stock = {"totalCash": 50_000_000, "totalDebt": 0, "availableCash": 50_000_000,
             "depositInterest": 1000, "depositFeeAmount": 10, "cashDividendReceiving": 0}
    with open(os.path.join(tmp, f"dnse_raw_{D0}.jsonl"), "w") as f:
        f.write(_rec("positions", D0, acct, {"positions": [
            {"symbol": "DRI", "openQuantity": qty_prev, "marketPrice": 15600}]}))
    with open(os.path.join(tmp, f"dnse_raw_{D1}.jsonl"), "w") as f:
        f.write(_rec("positions", D1, acct, {"positions": [
            {"symbol": "DRI", "openQuantity": qty_now, "marketPrice": 15600}]}))
        f.write(_rec("balances", D1, acct, {"stock": stock}))
    ca = os.path.join(tmp, "corp_actions.json")
    with open(ca, "w", encoding="utf-8") as f:
        json.dump({"actions": []}, f)
    saved = (D.EXEC_DIR, D.WC_ROOT, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, D.subprocess.run, D.bq_raw_prices, D._corp_action_daily_snapshot,
             D.held_event_next_session, V.bq_close_prices, V.EXEC_DIR, X.registry_fallback_enabled,
             sys.argv)
    D.EXEC_DIR = V.EXEC_DIR = tmp
    D.WC_ROOT = root
    D.CORP_ACTIONS_FILE = ca
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    D.bq_raw_prices = lambda tks, date: ({t: 15600.0 for t in tks}, {t: 15600.0 for t in tks}, None)
    D.subprocess.run = lambda *a, **k: types.SimpleNamespace(returncode=0, stdout="", stderr="")
    D._corp_action_daily_snapshot = lambda asof: None
    D.held_event_next_session = lambda snap, asof, tk: ca_event
    V.bq_close_prices = lambda tickers, date: ({"DRI": 15600.0}, None)
    X.registry_fallback_enabled = lambda: False
    sys.argv = ["daily_nav_snapshot.py", "--account", label, "--account-no", acct, "--date", D1,
                "--from-raw", "--starting-capital", "10000000"]
    err, out = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            try:
                rc = D.main()
            except SystemExit as e:
                rc = e.code
    finally:
        (D.EXEC_DIR, D.WC_ROOT, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, D.subprocess.run, D.bq_raw_prices, D._corp_action_daily_snapshot,
         D.held_event_next_session, V.bq_close_prices, V.EXEC_DIR, X.registry_fallback_enabled,
         sys.argv) = saved
    gb = os.path.join(tmp, f"nav_gate_block_{label}_{D1}.json")
    return (rc, err.getvalue(), os.path.exists(os.path.join(tmp, f"nav_history_{label}.csv")),
            json.load(open(gb)) if os.path.exists(gb) else None)


STMT = [("BÁN", "DRI", ZLP, 600), ("BÁN", "DRI", SPX, 800), ("BÁN", "DRI", SPX, 400)]


def blocked(rc, err):
    return rc == 5 and "KHỐI LƯỢNG vị thế đổi NGOÀI lệnh khớp thật" in err


def main():
    print(f"TZ lúc khởi chạy={TZ_AT_START!r}")

    print("[1] bán tay DRI 21/10, có statement ⇒ KHÔNG chặn, có dòng NAV")
    rc, err, hist, gb = run_main("SpaceX", SPX, 3700, 2500, STMT)
    check("SpaceX 3700→2500: không rc=5 + ghi nav_history", rc != 5 and hist and gb is None,
          f"rc={rc} hist={hist} {err[-400:]}")
    rc, err, hist, gb = run_main("ZaloPay", ZLP, 1900, 1300, STMT)
    check("ZaloPay 1900→1300 (lọc đúng tiểu khoản, không lấy 1200 của SpaceX)",
          rc != 5 and hist and gb is None, f"rc={rc} hist={hist} {err[-400:]}")

    print("[2] phần dư KHÔNG có ở statement ⇒ VẪN chặn rc=5")
    rc, err, hist, gb = run_main("SpaceX", SPX, 3700, 2500, [("BÁN", "DRI", SPX, 800)])
    check("statement chỉ 800 vs dư −1200 ⇒ rc=5, không ghi NAV", blocked(rc, err) and not hist,
          f"rc={rc} {err[-300:]}")
    check("thông điệp nêu lệch (lệnh khớp thật −800) và artifact gate-block có fill_notes",
          "-800" in err and gb is not None and "fill_notes" in gb["corp_action_gate_v2"], str(gb))
    rc, err, hist, gb = run_main("SpaceX", SPX, 3700, 2500, [("BÁN", "DRI", ZLP, 600)])
    check("statement chỉ có account khác ⇒ chặn", blocked(rc, err) and not hist, f"rc={rc}")
    rc, err, hist, gb = run_main("SpaceX", SPX, 3700, 2500, None)
    check("không có statement lẫn journal ⇒ chặn (hành vi cũ)", blocked(rc, err) and not hist,
          f"rc={rc}")

    print("[3] statement hỏng/NaN ⇒ không crash")
    for bad in ("", "nan"):
        try:
            rc, err, hist, gb = run_main("SpaceX", SPX, 3700, 2500, [("BÁN", "DRI", SPX, bad)])
            check(f"khối lượng {bad!r} ⇒ fail-closed rc=5, không raise",
                  blocked(rc, err) and not hist, f"rc={rc} {err[-300:]}")
        except Exception as e:
            check(f"khối lượng {bad!r} không raise", False, f"{type(e).__name__}: {e}")

    print("[4] corp-action thật (phần dư KHÔNG do lệnh) vẫn chặn dù có statement bán tay khác")
    rc, err, hist, gb = run_main("SpaceX", SPX, 3700, 4070, STMT)   # +10% không lệnh nào giải thích
    check("KL tăng 3700→4070 trong khi statement chỉ có BÁN ⇒ chặn", blocked(rc, err) and not hist,
          f"rc={rc} {err[-300:]}")

    print(f"\n{'ALL PASS' if not FAILS else f'FAIL {len(FAILS)}: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

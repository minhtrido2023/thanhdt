#!/usr/bin/env python3
"""Selfcheck — cổng khối lượng của compute_active_nav hợp nhất fill journal bot + statement DNSE.

Ca gốc 2026-10-21: user bán TAY DRI (SpaceX 3.700→2.500, ZaloPay 1.900→1.300 @15.400), journal bot
không có ⇒ rc=6 oan. Chạy dưới 3 TZ (env -u TZ, UTC, Asia/Ho_Chi_Minh); mọi file dựng trong thư
mục tạm — KHÔNG đọc/ghi data/execution_logs thật, KHÔNG gọi DNSE/Gmail.

    python3 bin/compute_active_nav_broker_fills_selfcheck.py      # exit 0 = PASS
"""
import csv
import datetime
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout

TZ_AT_START = os.environ.get("TZ")   # đọc TRƯỚC import: daily_nav_snapshot tự đặt TZ khi import
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compute_active_nav as can  # noqa: E402
import daily_nav_snapshot as dns  # noqa: E402
import exdate_frame as X  # noqa: E402
import verify_account_snapshot as vas  # noqa: E402

SPX, ZLP = "0002023347", "0001743768"
D0, D1 = "2026-10-20", "2026-10-21"
FAILS = []


def check(name, cond, info=""):
    print(f"  {'PASS' if cond else 'FAIL'} {name}" + (f" — {info}" if info and not cond else ""))
    if not cond:
        FAILS.append(name)


class Env:
    """Cây WC tạm: secrets + execution_logs; vá các hàm đọc dữ liệu thật của dns/vas."""

    def __init__(self, prev_qty, journal=None, statement=None):
        self.tmp = tempfile.mkdtemp(prefix="anbf_")
        self.exec_dir = os.path.join(self.tmp, "data", "execution_logs")
        os.makedirs(self.exec_dir)
        os.makedirs(os.path.join(self.tmp, "secrets"))
        with open(os.path.join(self.tmp, "secrets", "trading_bot_accounts.json"), "w") as f:
            json.dump({"accounts": {"SpaceX": {"account_id": SPX},
                                    "ZaloPay": {"account_id": ZLP}}}, f)
        for label, rows in (journal or {}).items():
            with open(os.path.join(self.exec_dir, f"exec_{label}_{D1}_journal.csv"), "w",
                      newline="") as f:
                w = csv.DictWriter(f, ["ts", "event", "child_oid", "ticker", "side", "qty", "price"])
                w.writeheader()
                for r in rows:
                    w.writerow(r)
        if statement is not None:
            with open(os.path.join(self.exec_dir, "dnse_khoplenh_broker_confirm_21-10-2026.csv"),
                      "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["ngay_gd", "loai_lenh", "ma", "tieu_khoan", "khoi_luong", "gia_khop",
                            "gia_tri_khop", "ty_le_phi", "phi_tra_so", "phi_dnse", "thue"])
                for side, tk, acct, q in statement:
                    w.writerow(["21/10/2026", side, tk, acct, q, 15400, q * 15400, 0.00088, 0, 0, 0])
        self.prev_qty = prev_qty

    def __enter__(self):
        self.saved = (vas.EXEC_DIR, dns.WC_ROOT, dns.previous_raw_qty,
                      dns._corp_action_daily_snapshot, dns.held_event_next_session,
                      X.registry_fallback_enabled)
        vas.EXEC_DIR, dns.WC_ROOT = self.exec_dir, self.tmp
        dns.previous_raw_qty = lambda acct, tk, asof: (self.prev_qty[acct].get(tk), D0)
        dns._corp_action_daily_snapshot = lambda asof: None
        dns.held_event_next_session = lambda snap, asof, tk: None
        X.registry_fallback_enabled = lambda: False
        return self

    def __exit__(self, *a):
        (vas.EXEC_DIR, dns.WC_ROOT, dns.previous_raw_qty, dns._corp_action_daily_snapshot,
         dns.held_event_next_session, X.registry_fallback_enabled) = self.saved


PREV = {SPX: {"DRI": 3700.0}, ZLP: {"DRI": 1900.0}}
DRI_STATEMENT = [("BÁN", "DRI", ZLP, 600), ("BÁN", "DRI", SPX, 800), ("BÁN", "DRI", SPX, 400)]
BOT_SELL_SPX = {"SpaceX": [{"ts": "2026-10-21T10:00:00", "event": "FILL", "child_oid": "c1",
                            "ticker": "DRI", "side": "sell", "qty": 1200, "price": 15400}]}


def classify(label, acct, qty_now, broker_statement=True):
    return X.classify_positions(label, acct, D1, {"DRI": {"total": qty_now}},
                                broker_statement=broker_statement)


def run_main(label, acct, qty_now):
    """compute_active_nav.main() đầu-cuối với broker/giá giả; trả (rc, stderr, out_path)."""
    out = os.path.join(tempfile.mkdtemp(prefix="anbf_out_"), f"active_nav_{label}.json")
    saved = (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices,
             can.today_ict, sys.argv)
    can.get_account_profile = lambda l: {"account_id": acct, "excluded_tickers": []}
    can.live_balance_and_positions = lambda a, l: (
        100_000_000.0, {"DRI": {"total": qty_now, "marketPrice": 15600}},
        {"reason": "", "cash_basis": "test", "cash_total_vnd": 100_000_000.0,
         "cash_debt_vnd": 0.0, "cash_available_vnd": 100_000_000.0,
         "cash_dividend_receiving_vnd": 0.0}, 0.0)
    can.resolve_prices = lambda tks, asof: ({t: 15600.0 for t in tks},
                                            {t: "test" for t in tks}, None)
    can.today_ict = lambda: datetime.date(2026, 10, 21)
    sys.argv = ["compute_active_nav.py", "--account", label, "--out", out]
    err, rc = io.StringIO(), 0
    try:
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            can.main()
    except SystemExit as e:
        rc = e.code or 0
    finally:
        (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices,
         can.today_ict, sys.argv) = saved
    return rc, err.getvalue(), out


def main():
    print(f"TZ lúc khởi chạy={TZ_AT_START!r}")

    print("[1] ca DRI 21/10, chỉ statement (bot không chạy) — cả 2 account giải thích được")
    with Env(PREV, statement=DRI_STATEMENT):
        cr, bl = classify("SpaceX", SPX, 2500)
        check("SpaceX 3700→2500 không chặn", not bl, str(bl))
        cr, bl = classify("ZaloPay", ZLP, 1300)
        check("ZaloPay 1900→1300 không chặn", not bl, str(bl))
        gaps, notes = [], []
        net = X.net_fills_journal_and_broker("SpaceX", D0, D1, missing_out=gaps, notes_out=notes)
        check("SpaceX net DRI = -1200 (lọc đúng tiểu khoản, không cộng 600 của ZaloPay)",
              net == {"DRI": -1200.0}, str(net))
        check("không báo thiếu bằng chứng khi statement có", gaps == [], str(gaps))
        rc, err, out = run_main("SpaceX", SPX, 2500)
        check("đầu-cuối SpaceX rc=0 + ghi file --out", rc == 0 and os.path.exists(out), f"rc={rc} {err}")
        rc, err, out = run_main("ZaloPay", ZLP, 1300)
        check("đầu-cuối ZaloPay rc=0 + ghi file --out", rc == 0 and os.path.exists(out), f"rc={rc} {err}")

    print("[2] số lượng broker KHÁC phần dư ⇒ vẫn rc=6 (fail-closed giữ nguyên)")
    with Env(PREV, statement=[("BÁN", "DRI", SPX, 800), ("BÁN", "DRI", ZLP, 600)]):
        cr, bl = classify("SpaceX", SPX, 2500)
        check("SpaceX statement 800 vs phần dư -1200 ⇒ chặn", "DRI" in bl, str(bl))
        check("thông điệp nêu lệnh khớp thật -800 + nguồn statement",
              "-800" in bl.get("DRI", "") and "statement DNSE" in bl.get("DRI", ""), bl.get("DRI", ""))
        rc, err, out = run_main("SpaceX", SPX, 2500)
        check("đầu-cuối rc=6, KHÔNG ghi file", rc == 6 and not os.path.exists(out), f"rc={rc}")
        cr, bl = classify("ZaloPay", ZLP, 1200)
        check("ZaloPay lệch 100cp (1900-600≠1200) ⇒ chặn", "DRI" in bl, str(bl))

    print("[3] fill có ở CẢ journal VÀ statement ⇒ không đếm đôi")
    with Env(PREV, journal=BOT_SELL_SPX, statement=DRI_STATEMENT):
        cr, bl = classify("SpaceX", SPX, 2500)
        check("journal 1200 + statement 1200 ⇒ net -1200, không chặn", not bl, str(bl))
        cr, bl = classify("SpaceX", SPX, 1300)
        check("nếu đếm đôi (-2400) thì 1300 mới khớp ⇒ phải CHẶN", "DRI" in bl, str(bl))
    with Env(PREV, journal=BOT_SELL_SPX,
             statement=DRI_STATEMENT + [("BÁN", "DRI", SPX, 1200)]):
        cr, bl = classify("SpaceX", SPX, 1300)
        check("bot 1200 + tay 1200 (statement 2400) ⇒ 3700→1300 giải thích được", not bl, str(bl))

    print("[4] journal > statement (statement thiếu dòng) ⇒ giữ journal, ghi lệch")
    with Env(PREV, journal=BOT_SELL_SPX, statement=[("BÁN", "DRI", ZLP, 600)]):
        notes = []
        net = X.net_fills_journal_and_broker("SpaceX", D0, D1, notes_out=notes)
        check("net = journal -1200", net == {"DRI": -1200.0}, str(net))
        check("ghi chú lệch journal > statement", any("journal 1,200 > statement 0" in n for n in notes),
              str(notes))

    print("[5] thiếu CẢ journal lẫn statement ⇒ giữ cảnh báo + chặn")
    import broker_fill_confirm as bfc
    fetched, orig_fetch = [], bfc._try_fetch
    bfc._try_fetch = lambda *a, **k: fetched.append(a) or False
    try:
        with Env(PREV):
            cr, bl = classify("SpaceX", SPX, 2500)
    finally:
        bfc._try_fetch = orig_fetch
    msg = bl.get("DRI", "")
    check("đường sizing KHÔNG tự gọi Gmail fetch khi thiếu statement", not fetched, str(fetched))
    if True:
        check("chặn", "DRI" in bl, str(bl))
        check("cảnh báo 'journal LẪN statement DNSE KHÔNG đọc được' + ngày 2026-10-21",
              "journal LẪN statement DNSE KHÔNG đọc được" in msg and "2026-10-21" in msg, msg)

    print("[6] statement chỉ có account KHÁC ⇒ account này khớp 0, phần dư vẫn chặn")
    with Env(PREV, statement=[("BÁN", "DRI", ZLP, 600)]):
        cr, bl = classify("SpaceX", SPX, 2500)
        check("SpaceX chặn", "DRI" in bl, str(bl))
        check("không coi là thiếu bằng chứng", "KHÔNG đọc được" not in bl.get("DRI", ""), bl.get("DRI", ""))

    print("[7] caller khác (broker_statement mặc định False) giữ nguyên hành vi cũ")
    with Env(PREV, statement=DRI_STATEMENT):
        cr, bl = X.classify_positions("SpaceX", SPX, D1, {"DRI": {"total": 2500}})
        check("gọi KHÔNG truyền kwarg ⇒ chỉ đọc journal ⇒ vẫn chặn như trước", "DRI" in bl, str(bl))

    print("[8] MUA tay + bán tay cùng ngày — dấu theo chiều")
    with Env(PREV, statement=[("MUA", "DRI", SPX, 500), ("BÁN", "DRI", SPX, 200)]):
        cr, bl = classify("SpaceX", SPX, 4000)
        check("3700 +500 −200 = 4000 không chặn", not bl, str(bl))
        cr, bl = classify("SpaceX", SPX, 3000)
        check("nếu coi mọi fill là bán (3000) ⇒ phải CHẶN", "DRI" in bl, str(bl))

    print("[9] statement có dòng hỏng (khối lượng rỗng/NaN) ⇒ KHÔNG crash, rơi về journal như cũ")
    with Env(PREV, journal=BOT_SELL_SPX, statement=[("BÁN", "DRI", SPX, "")]):
        try:
            cr, bl = classify("SpaceX", SPX, 2500)
            check("có journal bot 1200 ⇒ giải thích được, không chặn, không raise", not bl, str(bl))
        except Exception as e:
            check("không raise khi statement hỏng", False, f"{type(e).__name__}: {e}")
    with Env(PREV, statement=[("BÁN", "DRI", SPX, "")]):
        try:
            cr, bl = classify("SpaceX", SPX, 2500)
            check("không journal + statement hỏng ⇒ vẫn CHẶN (fail-closed)", "DRI" in bl, str(bl))
            check("lý do nêu statement không parse được",
                  "không parse được" in bl.get("DRI", ""), bl.get("DRI", ""))
        except Exception as e:
            check("không raise khi statement hỏng (không journal)", False, f"{type(e).__name__}: {e}")

    print(f"\n{'ALL PASS' if not FAILS else f'FAIL {len(FAILS)}: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

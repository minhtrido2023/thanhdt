#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck — ký quỹ phái sinh trong NAV (job Taylor_20261117_092943, sleeve ORB SpaceX).

Chạy:  python3 mike/bin/nav_derivative_margin_selfcheck.py [--mutations]
       env -u TZ python3 …   ;   TZ=America/New_York python3 …   ;   TZ=Pacific/Kiritimati python3 …
KHÉP KÍN: mọi ghi ở tempdir; không broker, không BQ. Đọc (không ghi) 2 file thật làm fixture:
`data/execution_logs/{verified_snapshot_SpaceX,dnse_raw}_2026-11-16.*` (nhóm F) và probe read-only
17/11 `agents/Taylor/research/nav_deriv_20261117/probe_1700.json` (nhóm A, số broker thật).

  A. derivative_margin.derivative_assets: block vắng ⇒ 0; probe thật ⇒ 4.999.059; field chưa xác
     minh ≠ 0 / vị thế mở / không đọc được vị thế (đường live) ⇒ TỪ CHỐI; backfill thì nhận.
  B. daily_nav_snapshot.main() --from-raw E2E: NAV = cũ + ký quỹ; cột derivative_assets ghi đúng;
     bất biến fund_restatement._check_row giữ; field chưa xác minh ≠ 0 ⇒ rc=2, KHÔNG ghi dòng.
  C. cash_identity K cộng ký quỹ (chuyển tiền cơ sở → ký quỹ triệt tiêu trong K).
  D. TWR (nav_period_returns.build_ledger): SpaceX nhận +5tr (NAV +5tr) + flow deposit 16:00 ⇒
     giá đơn vị KHÔNG đổi; ZaloPay −5tr + flow withdraw ⇒ KHÔNG đổi; thiếu flow ⇒ đổi (đối chứng).
  E. Mẫu số sizing cổ phiếu KHÔNG đổi khi có ký quỹ: compute_active_nav.cash_basis + egg đọc,
     park_holdings.read_broker_snapshot (nguồn của park/JIT-unpark) — cùng giá trị có/không block.
  G. read_derivative_positions (client giả) + cổng live derivative_margin.live_gate + dây nối live
     (G10-G13 daily_nav_snapshot.live_derivative_positions với trading_bot.brokers giả; G14 AST chỗ gọi).
  F. reconcile_equity: raw thật 16/11 + bơm ký quỹ X + flow nạp X ⇒ residual y hệt bản gốc (±1đ).
  --mutations: 14 mutant trên bản sao bin/ ở tempdir — mỗi mutant PHẢI làm selfcheck đỏ.
"""
import csv
import datetime
import io
import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

BIN = os.environ.get("NAV_DERIV_SELFCHECK_BIN") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(os.path.abspath(__file__))
EXEC = os.path.join(WC_ROOT, "data", "execution_logs")
PROBE = os.path.join(WC_ROOT, "mike", "agents", "Taylor", "research", "nav_deriv_20261117",
                     "probe_1700.json")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def deriv(**kw):
    base = {"pendingDepositWithdraw": 0, "remainSecure": 0, "usedSecure": 0, "pendingSecure": 0,
            "holdTaxAndFee": 0, "totalLoanDebt": 0}
    base.update(kw)
    return base


# ───────────────────────────── A ─────────────────────────────
def group_a():
    print("A. derivative_margin.derivative_assets")
    import derivative_margin as DM
    v, r = DM.derivative_assets({"stock": {}}, None)
    check("A1 block derivative vắng (raw cũ) ⇒ 0, không chặn", v == 0 and r is None, f"{v} {r}")
    v, r = DM.derivative_assets({"derivative": deriv()}, None)
    check("A2 block toàn 0 ⇒ 0, không cần đọc vị thế", v == 0 and r is None, f"{v} {r}")
    probe = json.load(open(PROBE, encoding="utf-8"))["SpaceX"]
    v, r = DM.derivative_assets(probe["balances"], probe["deriv_positions"]["positions"])
    check("A3 probe thật 17/11 SpaceX ⇒ 4.999.059 (remainSecure, vị thế rỗng)",
          v == 4_999_059 and r is None, f"{v} {r}")
    v, r = DM.derivative_assets({"derivative": deriv(remainSecure=5e6)}, None)
    check("A4 live: có ký quỹ mà KHÔNG đọc được vị thế ⇒ từ chối", v is None and r, f"{v} {r}")
    v, r = DM.derivative_assets({"derivative": deriv(remainSecure=5e6)}, None, positions_required=False)
    check("A5 backfill/reconcile: không có vị thế ⇒ nhận remainSecure", v == 5e6 and r is None, f"{v} {r}")
    v, r = DM.derivative_assets({"derivative": deriv(remainSecure=5e6)}, [{"symbol": "VN30F2612"}])
    check("A6 có vị thế phái sinh MỞ ⇒ từ chối (chưa có field PnL đã xác minh)", v is None and r, f"{v} {r}")
    for f in DM.UNVERIFIED_FIELDS:
        v, r = DM.derivative_assets({"derivative": deriv(remainSecure=5e6, **{f: 1000})}, [],
                                    positions_required=False)
        check(f"A7 {f}≠0 (chưa xác minh) ⇒ từ chối, kể cả backfill", v is None and f in (r or ""),
              f"{v} {r}")
    v, r = DM.derivative_assets({"derivative": deriv(remainSecure="abc")}, [])
    check("A8 remainSecure không phải số ⇒ từ chối", v is None and r, f"{v} {r}")


# ───────────────────────────── B ─────────────────────────────
ACCT, ACCT_NO, DATE, PRICE = "SpaceX", "0002023347", "2026-09-09", 21_000.0


def _e2e(tmp, dblock):
    """daily_nav_snapshot.main() --from-raw trong sandbox (khuôn nav_corpaction_gate_e2e_selfcheck,
    không import file đó vì nó tự chạy toàn bộ khi import). 500 VIB × 21.000 + tiền 5tr."""
    import daily_nav_snapshot as D
    import corp_action_daily as CAD
    import verify_account_snapshot as V
    bal = {"stock": {"totalCash": 5_000_000.0, "totalDebt": 0.0}}
    if dblock is not None:
        bal["derivative"] = dblock
    with open(os.path.join(tmp, f"dnse_raw_{DATE}.jsonl"), "w") as f:
        f.write(json.dumps({"kind": "positions", "ts": f"{DATE}T19:00:00", "account_no": ACCT_NO,
                            "payload": {"positions": [{"symbol": "VIB", "openQuantity": 500.0,
                                                       "marketPrice": PRICE}]}}) + "\n")
        f.write(json.dumps({"kind": "balances", "ts": f"{DATE}T19:05:00", "account_no": ACCT_NO,
                            "payload": bal}) + "\n")
    open(os.path.join(tmp, f"exec_{ACCT}_{DATE}_journal.csv"), "w").write(
        "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
    json.dump({"actions": []}, open(os.path.join(tmp, "corp_actions.json"), "w"))
    json.dump({"asof": DATE, "status": "OK", "usable": True, "feed_status": "FRESH",
               "upcoming_events_held": []}, open(os.path.join(tmp, f"corp_action_daily_{DATE}.json"), "w"))
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
           D.bq_raw_prices, D.cum_dividend_double_count, sys.argv,
           os.environ.get("NAV_SANITY_MAX_PCT"), V.EXEC_DIR)
    D.EXEC_DIR = V.EXEC_DIR = tmp
    D.CORP_ACTIONS_FILE = os.path.join(tmp, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(tmp, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
    D.bq_raw_prices = lambda tickers, date: ({t: PRICE for t in tickers}, {t: PRICE for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {
        "amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [], "bq_max_date": None,
        "note": "", "warnings": []}
    os.environ["NAV_SANITY_MAX_PCT"] = "1000000"
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO,
                "--date", DATE, "--from-raw", "--starting-capital", "10000000"]
    err, out = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path,
         D.bq_raw_prices, D.cum_dividend_double_count, sys.argv, _env, V.EXEC_DIR) = old
        if _env is None:
            os.environ.pop("NAV_SANITY_MAX_PCT", None)
        else:
            os.environ["NAV_SANITY_MAX_PCT"] = _env
    snap_p = os.path.join(tmp, f"nav_snapshot_{ACCT}_{DATE}.json")
    snap = json.load(open(snap_p, encoding="utf-8")) if os.path.exists(snap_p) else None
    hist = os.path.join(tmp, f"nav_history_{ACCT}.csv")
    rows = list(csv.DictReader(open(hist, encoding="utf-8"))) if os.path.exists(hist) else []
    return rc, err.getvalue() + out.getvalue(), snap, rows


def group_b():
    print("B. daily_nav_snapshot.main() --from-raw E2E")
    import fund_restatement as FR
    with tempfile.TemporaryDirectory() as t0, tempfile.TemporaryDirectory() as t1, \
            tempfile.TemporaryDirectory() as t2:
        rc0, err0, s0, _ = _e2e(t0, None)
        rc1, err1, s1, rows1 = _e2e(t1, deriv(remainSecure=4_999_059))
        check("B0 đối chứng (không block derivative) chạy rc=0", rc0 == 0 and s0, f"rc={rc0} {err0[-300:]}")
        check("B1 có ký quỹ ⇒ rc=0", rc1 == 0 and s1, f"rc={rc1} {err1[-300:]}")
        if s0 and s1:
            check("B2 NAV = NAV đối chứng + 4.999.059 (ký quỹ CỘNG vào NAV)",
                  abs(s1["nav"] - s0["nav"] - 4_999_059) < 1, f"{s1['nav']} vs {s0['nav']}")
            check("B3 snapshot JSON có derivative_assets = 4.999.059",
                  s1.get("derivative_assets") == 4_999_059, s1.get("derivative_assets"))
        row = rows1[-1] if rows1 else {}
        check("B4 nav_history: cột derivative_assets = 4999059, là cột CUỐI",
              row.get("derivative_assets") == "4999059" and list(row)[-1] == "derivative_assets",
              str(row))
        try:
            FR._check_row(row, list(row), "B5")
            ok = True
        except Exception as e:      # noqa: BLE001
            ok, row["_err"] = False, str(e)
        check("B5 bất biến fund_restatement (nav = Σ cột + derivative_assets) giữ trên dòng mới",
              ok, row.get("_err", ""))
        rc2, err2, s2, rows2 = _e2e(t2, deriv(remainSecure=4_999_059, usedSecure=1_000_000))
        check("B6 usedSecure≠0 (chưa xác minh) ⇒ rc=2, KHÔNG ghi nav_history",
              rc2 == 2 and not rows2 and "CHƯA XÁC MINH" in err2, f"rc={rc2} rows={len(rows2)}")


# ───────────────────────────── C ─────────────────────────────
HDR = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
       "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source", "derivative_assets"]


def _write_hist(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HDR)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in HDR})


def group_c():
    print("C. cash_identity K")
    import cash_identity as CI
    with tempfile.TemporaryDirectory() as t:
        # Số thật SpaceX 16/11 → 17/11 (giả định không biến động giá): cash 1.640 → 2.581, ký quỹ 4.999.059.
        _write_hist(os.path.join(t, "nav_history_SpaceX.csv"), [
            {"date": "2026-11-16", "nav": "940585870", "mtm_stock": "199083600", "cash": "1640",
             "margin_debt": "10812643", "offbook_assets": "0", "egg_assets": "752313273",
             "balance_ts": "2026-11-16T19:30:09", "cum_dividend_excl": "0"},
            {"date": "2026-11-17", "nav": str(940585870 + 5_000_000), "mtm_stock": "199083600",
             "cash": "2581", "margin_debt": "10812643", "offbook_assets": "0", "egg_assets": "752313273",
             "balance_ts": "2026-11-17T19:10:00", "cum_dividend_excl": "0",
             "derivative_assets": "4999059"}])
        rows = CI.load_nav_rows("SpaceX", nav_dir=t)
        dk = rows[1]["k"] - rows[0]["k"]
        check("C1 ΔK = +5.000.000 = đúng số tiền nạp (941 tiền cơ sở + 4.999.059 ký quỹ)",
              abs(dk - 5_000_000) < 1, dk)
        check("C2 dòng cũ thiếu cột derivative_assets ⇒ deriv=0 (không vỡ)", rows[0]["deriv"] == 0)


# ───────────────────────────── D ─────────────────────────────
def group_d():
    print("D. TWR — chuyển vốn nội bộ 5tr không thành lãi/lỗ")
    import nav_unit_ledger as NUL
    import nav_period_returns as NPR
    import account_cash_flows as ACF
    base = {"SpaceX": (940_585_870, "2026-11-16T19:30:09", +5_000_000),
            "ZaloPay": (930_559_021, "2026-11-16T19:30:22", -5_000_000)}
    for acct, (nav0, ts0, amt) in base.items():
        for with_flow in (True, False):
            with tempfile.TemporaryDirectory() as t:
                _write_hist(os.path.join(t, f"nav_history_{acct}.csv"), [
                    {"date": "2026-11-16", "nav": str(nav0), "balance_ts": ts0},
                    {"date": "2026-11-17", "nav": str(nav0 + amt), "balance_ts": "2026-11-17T19:10:00"}])
                fp = os.path.join(t, "flows.json")
                recs = [{"date": "2026-11-17", "time_ict": "16:00:00", "amount_vnd": amt,
                         "kind": "deposit" if amt > 0 else "withdraw",
                         "evidence": "selfcheck"}] if with_flow else []
                json.dump({acct: recs}, open(fp, "w"))
                rows = NUL.load_nav_history(acct, nav_dir=t)
                flows = ACF.load_flows(acct, flows_path=fp, today=datetime.date(2026, 11, 17))
                ledger, _ = NPR.build_ledger(rows, flows, datetime.date(2026, 11, 16), float(nav0))
                p0, p1 = ledger[0]["unit_price"], ledger[-1]["unit_price"]
                ret = p1 / p0 - 1
                if with_flow:
                    check(f"D1 {acct}: NAV {amt:+,} + flow {amt:+,} ⇒ tỉ suất ngày = 0",
                          abs(ret) < 1e-9, f"{ret:.6%}")
                else:
                    check(f"D2 {acct} đối chứng: thiếu flow ⇒ tỉ suất ≠ 0 (chỉ cash_identity bắt; cổng NAV-jump 5% KHÔNG bắt 0,5%)",
                          abs(ret) > 0.004, f"{ret:.6%}")


# ───────────────────────────── E ─────────────────────────────
def group_e():
    print("E. Mẫu số sizing cổ phiếu KHÔNG cộng ký quỹ")
    import compute_active_nav as CAN
    import park_holdings as PH
    probe = json.load(open(PROBE, encoding="utf-8"))["SpaceX"]["balances"]
    no_d = {k: v for k, v in probe.items() if k != "derivative"}
    check("E1 compute_active_nav.cash_basis giống hệt có/không block derivative",
          CAN.cash_basis(probe)[0] == CAN.cash_basis(no_d)[0], (CAN.cash_basis(probe)[0], CAN.cash_basis(no_d)[0]))
    check("E2 cash_basis = totalCash − totalDebt (2.581 − 10.812.643), không chứa 4.999.059",
          CAN.cash_basis(probe)[0] == 2581 - 10_812_643, CAN.cash_basis(probe)[0])
    outs = []
    for payload in (probe, no_d):
        with tempfile.TemporaryDirectory() as t:
            with open(os.path.join(t, "dnse_raw_2026-11-17.jsonl"), "w") as f:
                f.write(json.dumps({"kind": "positions", "ts": "2026-11-17T19:00:00",
                                    "account_no": "0002023347", "payload": {"positions": []}}) + "\n")
                f.write(json.dumps({"kind": "balances", "ts": "2026-11-17T19:00:01",
                                    "account_no": "0002023347", "payload": payload}) + "\n")
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    pos, cash, meta = PH.read_broker_snapshot("SpaceX", "0002023347", "2026-11-17",
                                                              exec_dir=t, need_price=False)[:3]
                outs.append((cash, meta.get("total_cash_vnd"), meta.get("total_debt_vnd"),
                             meta.get("egg_assets_vnd")))
            except SystemExit as e:
                outs.append(("SystemExit", str(e)))
    check("E3 park_holdings.read_broker_snapshot (park/JIT) giống hệt có/không ký quỹ",
          len(outs) == 2 and outs[0] == outs[1] and outs[0][0] != "SystemExit", outs)


# ───────────────────────────── F ─────────────────────────────
def group_f():
    print("F. reconcile_equity — identity với ký quỹ + dòng vốn")
    date, acct_no, x = "2026-11-16", "0002023347", 5_000_000
    src_snap = os.path.join(EXEC, f"verified_snapshot_SpaceX_{date}.json")
    src_raw = os.path.join(EXEC, f"dnse_raw_{date}.jsonl")
    if not (os.path.exists(src_snap) and os.path.exists(src_raw)):
        check("F0 fixture thật 16/11 tồn tại", False, f"{src_snap} / {src_raw}")
        return
    res = {}
    for variant in ("base", "deriv+flow", "deriv_only"):
        with tempfile.TemporaryDirectory() as t:
            snap = os.path.join(t, os.path.basename(src_snap))
            shutil.copy(src_snap, snap)
            recs = [json.loads(line) for line in open(src_raw, encoding="utf-8")]
            last = max(i for i, r in enumerate(recs)
                       if r.get("kind") == "balances" and str(r.get("account_no")) == acct_no)
            if variant != "base":
                recs[last]["payload"]["derivative"] = deriv(remainSecure=x)
            raw = os.path.join(t, f"dnse_raw_{date}.jsonl")
            with open(raw, "w", encoding="utf-8") as f:
                f.writelines(json.dumps(r) + "\n" for r in recs)
            fp = os.path.join(t, "flows.json")
            flows = [{"date": date, "time_ict": "16:00:00", "amount_vnd": x, "kind": "deposit",
                      "evidence": "selfcheck"}] if variant == "deriv+flow" else []
            json.dump({"SpaceX": flows, "ZaloPay": []}, open(fp, "w"))
            env = dict(os.environ, ACCOUNT_CASH_FLOWS_PATH=fp)
            p = subprocess.run([sys.executable, os.path.join(BIN, "reconcile_equity.py"),
                                "--account", "SpaceX", "--account-no", acct_no, "--snapshot", snap,
                                "--balance-raw", raw, "--starting-capital", "1000000000"],
                               capture_output=True, text=True, env=env)
            out = snap.replace("verified_snapshot", "reconcile_equity")
            res[variant] = (json.load(open(out, encoding="utf-8")) if os.path.exists(out)
                            else {"_err": f"rc={p.returncode} {p.stderr[-400:]}"})
    b, d, o = res["base"], res["deriv+flow"], res["deriv_only"]
    ok = all("residual" in r for r in (b, d, o))
    check("F1 3 biến thể reconcile đều chạy ra JSON", ok, {k: v.get("_err") for k, v in res.items()})
    if not ok:
        return
    check("F2 ký quỹ X + flow nạp X ⇒ residual y hệt bản gốc (±1đ)",
          abs(d["residual"] - b["residual"]) <= 1, (d["residual"], b["residual"]))
    check("F3 vế phải có derivative_assets = X; vế trái có external_flows_net = X",
          d.get("derivative_assets") == x and d.get("external_flows_net") == x,
          (d.get("derivative_assets"), d.get("external_flows_net")))
    check("F4 đối chứng: ký quỹ mà THIẾU flow ⇒ residual lệch đúng −X",
          abs(o["residual"] - (b["residual"] - x)) <= 1, (o["residual"], b["residual"]))


# ───────────────────────────── G ─────────────────────────────
def group_g():
    print("G. đọc vị thế phái sinh + cổng live (fail-closed)")
    import derivative_margin as DM

    class C:
        def __init__(self, r=None, exc=None):
            self.r, self.exc = r, exc

        def positions(self, acct, market_type=None):
            if self.exc:
                raise self.exc
            return self.r
    check("G1 client raise ⇒ None", DM.read_derivative_positions(C(exc=RuntimeError("x")), "a") is None)
    check("G2 {} ⇒ None", DM.read_derivative_positions(C({}), "a") is None)
    check("G3 {'positions': []} ⇒ []", DM.read_derivative_positions(C({"positions": []}), "a") == [])
    check("G4 có vị thế ⇒ list", DM.read_derivative_positions(C({"positions": [{"s": 1}]}), "a") == [{"s": 1}])
    pl = {"derivative": deriv(remainSecure=4_999_059)}
    v, rj = DM.live_gate(pl, lambda: None, False)
    check("G5 live: không đọc được vị thế ⇒ từ chối (rc=2)", v is None and rj, (v, rj))
    v, rj = DM.live_gate(pl, lambda: [], False)
    check("G6 live: vị thế rỗng ⇒ nhận ký quỹ (rc=0)", v == 4_999_059 and rj is None, (v, rj))
    v, rj = DM.live_gate(pl, lambda: [{"s": 1}], False)
    check("G7 live: có vị thế mở ⇒ từ chối (rc=2)", v is None and rj, (v, rj))
    called = []
    v, rj = DM.live_gate(pl, lambda: called.append(1) or None, True)
    check("G8 --from-raw: không gọi đọc vị thế, nhận ký quỹ", v == 4_999_059 and rj is None and not called, (v, rj, called))
    v, rj = DM.live_gate({"derivative": deriv()}, lambda: called.append(1) or None, False)
    check("G9 live, block toàn 0 ⇒ 0, không gọi đọc vị thế", v == 0 and rj is None and len(called) == 0, (v, rj, called))

    # ── G10-G14: DÂY NỐI live trong daily_nav_snapshot (arch-review vòng 2 BLOCKING) ──
    import ast
    import types
    import daily_nav_snapshot as D
    seen = {}

    class FC:
        def __init__(self, r=None, exc=None):
            self.r, self.exc = r, exc

        def positions(self, acct, market_type=None):
            seen["call"] = (acct, market_type)
            if self.exc:
                raise self.exc
            return self.r

    def run_live(client):
        """live_derivative_positions với trading_bot.brokers GIẢ (không chạm broker thật)."""
        mods = ("trading_bot", "trading_bot.brokers")
        saved = {m: sys.modules.get(m) for m in mods}
        pkg, brk = types.ModuleType("trading_bot"), types.ModuleType("trading_bot.brokers")
        brk.get_dnse_client = lambda _cfg=None: client
        pkg.brokers = brk
        sys.modules["trading_bot"], sys.modules["trading_bot.brokers"] = pkg, brk
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                return D.live_derivative_positions("ACCT-X")
        finally:
            for m, v in saved.items():
                if v is None:
                    sys.modules.pop(m, None)
                else:
                    sys.modules[m] = v
    check("G10 live_derivative_positions: client raise ⇒ None", run_live(FC(exc=RuntimeError("x"))) is None)
    check("G11 live_derivative_positions: {} ⇒ None", run_live(FC({})) is None)
    check("G12 live_derivative_positions: {'positions': []} ⇒ [] (và gọi đúng acct + DERIVATIVE)",
          run_live(FC({"positions": []})) == [] and seen.get("call") == ("ACCT-X", "DERIVATIVE"), seen)
    check("G13 live_derivative_positions: có vị thế ⇒ list đó",
          run_live(FC({"positions": [{"s": 1}]})) == [{"s": 1}])
    # Chỗ gọi live_gate trong main(): cấu trúc AST — args[2] = args.from_raw, args[1] = lambda
    # gọi live_derivative_positions(account_no).
    tree = ast.parse(open(os.path.join(BIN, "daily_nav_snapshot.py"), encoding="utf-8").read())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "live_gate" and isinstance(n.func.value, ast.Name)
             and n.func.value.id == "derivative_margin"]
    ok_shape = False
    if len(calls) == 1 and len(calls[0].args) == 3 and not calls[0].keywords:
        _, lam, fr = calls[0].args
        lam_ok = (isinstance(lam, ast.Lambda) and not lam.args.args
                  and isinstance(lam.body, ast.Call) and isinstance(lam.body.func, ast.Name)
                  and lam.body.func.id == "live_derivative_positions"
                  and len(lam.body.args) == 1 and isinstance(lam.body.args[0], ast.Name)
                  and lam.body.args[0].id == "account_no" and not lam.body.keywords)
        fr_ok = (isinstance(fr, ast.Attribute) and fr.attr == "from_raw"
                 and isinstance(fr.value, ast.Name) and fr.value.id == "args")
        ok_shape = lam_ok and fr_ok
    check("G14 main(): derivative_margin.live_gate(payload, lambda: live_derivative_positions(account_no), "
          "args.from_raw) — đúng dây nối live", ok_shape, f"{len(calls)} chỗ gọi")


# ─────────────────────────── mutations ───────────────────────────
MUTANTS = [
    ("daily_nav_snapshot.py", "nav = mtm_stock + cash - debt + offbook + egg_value + derivative_value",
     "nav = mtm_stock + cash - debt + offbook + egg_value"),
    ("derivative_margin.py", "    if nonzero:\n", "    if False:\n"),
    ("derivative_margin.py", "    if positions:\n", "    if False:\n"),
    ("derivative_margin.py", "    if positions is None and remain > 0 and positions_required:",
     "    if False:"),
    ("derivative_margin.py", "    return derivative_assets(payload, pos, positions_required=not from_raw)",
     "    return derivative_assets(payload, pos, positions_required=False)"),
    ("derivative_margin.py", "        pos = read_positions()", "        pos = []"),
    ("derivative_margin.py", "    if isinstance(r, dict) and isinstance(r.get(\"positions\"), list):\n        return r[\"positions\"]\n    return None",
     "    return []"),
    ("cash_identity.py", "+ row[\"egg\"]\n                        + row[\"deriv\"])", "+ row[\"egg\"])"),
    ("fund_restatement.py", "+ parts[\"egg_assets\"] + parts[\"derivative_assets\"])", "+ parts[\"egg_assets\"])"),
    ("reconcile_equity.py", "args.starting_capital + net_flows + unrealized_pnl",
     "args.starting_capital + unrealized_pnl"),
    ("reconcile_equity.py", "           + derivative_value)\n", "           )\n"),
    # X1/X2/X4 — dây nối live trong daily_nav_snapshot (arch-review vòng 2)
    ("daily_nav_snapshot.py", "lambda: live_derivative_positions(account_no), args.from_raw)",
     "lambda: live_derivative_positions(account_no), True)"),
    ("daily_nav_snapshot.py", "lambda: live_derivative_positions(account_no), args.from_raw)",
     "lambda: [], args.from_raw)"),
    ("daily_nav_snapshot.py", "        return derivative_margin.read_derivative_positions(get_dnse_client(None), account_no)",
     "        return []"),
]


def run_mutations():
    here = os.path.dirname(os.path.abspath(__file__))
    killed, control_ok = 0, False
    # M0 = ĐỐI CHỨNG: bản sao KHÔNG đột biến phải XANH — nếu đỏ thì "bị bắt" của mọi mutant là
    # do môi trường bản sao hỏng (WC_ROOT, import), không phải do assertion.
    for i, (fn, a, b) in enumerate([("derivative_margin.py", "", "")] + MUTANTS):
        with tempfile.TemporaryDirectory() as t:
            mb = os.path.join(t, "bin")
            shutil.copytree(here, mb, ignore=shutil.ignore_patterns("__pycache__", "fixtures"))
            # wc_paths tìm WC_ROOT theo marker wc_env.sh từ vị trí file ⇒ ghim lại về repo thật.
            p = os.path.join(mb, fn)
            s = open(p, encoding="utf-8").read()
            if i and s.count(a) != 1:
                print(f"  ✗ M{i} {fn}: không áp được mutant (khớp {s.count(a)} lần)")
                continue
            if i:
                open(p, "w", encoding="utf-8").write(s.replace(a, b))
            env = dict(os.environ, NAV_DERIV_SELFCHECK_BIN=mb, PYTHONDONTWRITEBYTECODE="1",
                       WC_ROOT=WC_ROOT)
            r = subprocess.run([sys.executable, os.path.join(here, os.path.basename(__file__))],
                               capture_output=True, text=True, env=env, cwd=t)
            dead = r.returncode != 0
            if not i:
                control_ok = not dead
                print(f"  {'✓' if control_ok else '✗'} M0 đối chứng (bản sao không đột biến) "
                      f"{'XANH' if control_ok else 'ĐỎ — kết quả mutant vô nghĩa'}"
                      + ("" if control_ok else f": {r.stdout[-800:]}{r.stderr[-400:]}"))
                continue
            killed += dead
            fails = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("✗")]
            print(f"  {'✓' if dead else '✗'} M{i} {fn}: {'BỊ BẮT' if dead else 'SỐNG SÓT'} "
                  f"— {fails[:2]}")
    print(f"MUTATIONS: {killed}/{len(MUTANTS)} bị bắt")
    return control_ok and killed == len(MUTANTS)


def main():
    if "--mutations" in sys.argv:
        return 0 if run_mutations() else 1
    print(f"BIN={BIN}  TZ={os.environ.get('TZ')!r}")
    for g in (group_a, group_b, group_c, group_d, group_e, group_f, group_g):
        try:
            g()
        except Exception as e:      # noqa: BLE001 — nhóm nổ = FAIL, các nhóm sau vẫn chạy
            import traceback
            check(f"{g.__name__} không nổ", False, f"{type(e).__name__}: {e} {traceback.format_exc()[-600:]}")
    print(f"\nPASS {len(PASS)} / FAIL {len(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

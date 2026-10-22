#!/usr/bin/env python3
"""Selfcheck `park_holdings.statement_extra_sells` — lệnh BÁN TAY trong statement DNSE (DRI 21/10).

Sandbox hoàn toàn offline (bootstrap/journal/statement/secrets giả trong tmp, `broker=` bơm tay,
corp_actions=[], rights_subs=[]). Chạy cho CẢ SpaceX và ZaloPay — statement DÙNG CHUNG 2 tiểu
khoản, nên kết quả 2 account phải KHÁC nhau (§12).

Kịch bản: bootstrap 2026-10-01 (chụp 2026-09-30T19:10). 20/10 bot bán FPT (có trong CẢ journal
LẪN statement). 21/10 user bán tay DRI (CHỈ statement): SpaceX 800+400, ZaloPay 600.

Mutant (phải bị bắt): M1 bỏ lọc tiểu khoản · M2 bỏ chống đếm đôi · M3 cho lệch dư lọt ·
M4 thêm lô cho MUA chỉ-có-ở-statement.

Chạy: python3 mike/bin/park_holdings_statement_selfcheck.py   (rc 0 = PASS)
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import broker_fill_confirm as BFC  # noqa: E402
import park_holdings as PH  # noqa: E402

ACCTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
ASOF = "2026-10-21"
BOOT = {"SpaceX": [("DRI", "DISCRETIONARY_SPECIAL", 3700), ("FPT", "PARK", 1000)],
        "ZaloPay": [("DRI", "DISCRETIONARY_SPECIAL", 1900), ("FPT", "PARK", 500)]}
BOT_FPT_SELL = {"SpaceX": 200, "ZaloPay": 100}
BROKER = {"SpaceX": {"DRI": 2500, "FPT": 800}, "ZaloPay": {"DRI": 1300, "FPT": 400}}
HDR = "ngay_gd,loai_lenh,ma,tieu_khoan,khoi_luong,gia_khop,gia_tri_khop,ty_le_phi,phi_tra_so,phi_dnse,thue\n"

FAILS = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)
    return cond


def build_sandbox():
    sb = tempfile.mkdtemp(prefix="ph_stmt_")
    ex, pl, sec = (os.path.join(sb, "data", "execution_logs"), os.path.join(sb, "data", "trade_plans"),
                   os.path.join(sb, "secrets"))
    for d in (ex, pl, sec):
        os.makedirs(d)
    json.dump({"accounts": [{"label": k, "account_id": v} for k, v in ACCTS.items()]},
              open(os.path.join(sec, "trading_bot_accounts.json"), "w"))
    for lab, pos in BOOT.items():
        json.dump({"_status": "APPROVED selfcheck", "reconcile_ok": True, "day0_date": "2026-10-01",
                   "broker_source": {"ts": "2026-09-30T19:10:00"},
                   "positions": [{"ticker": t, "book": b, "qty": q, "cost_price_vnd": 10000,
                                  "entry_date": "2026-09-01"} for t, b, q in pos]},
                  open(os.path.join(pl, f"bootstrap_book_snapshot_{lab}_20261001.json"), "w"))
        with open(os.path.join(ex, f"exec_{lab}_2026-10-20_journal.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ts", "event", "ticker", "side", "qty", "price", "child_oid", "parent_id",
                        "book", "play_type"])
            w.writerow(["2026-10-20T10:00:00", "FILL", "FPT", "sell", BOT_FPT_SELL[lab], 100000,
                        f"c-{lab}", f"p-{lab}", "PARK", ""])
    write_stmt(ex, "20-10-2026", [("20/10/2026", "BÁN", "FPT", ACCTS[l], BOT_FPT_SELL[l], 100000)
                                  for l in ACCTS])
    write_stmt(ex, "21-10-2026", [("21/10/2026", "BÁN", "DRI", ACCTS["ZaloPay"], 600, 15400),
                                  ("21/10/2026", "BÁN", "DRI", ACCTS["SpaceX"], 800, 15400),
                                  ("21/10/2026", "BÁN", "DRI", ACCTS["SpaceX"], 400, 15400)])
    return sb, ex, pl


def write_stmt(ex, ddmmyyyy, rows, raw_tail=""):
    with open(os.path.join(ex, f"dnse_khoplenh_broker_confirm_{ddmmyyyy}.csv"), "w") as f:
        f.write(HDR)
        for d, side, tk, acct, q, px in rows:
            f.write(f"{d},{side},{tk},{acct},{q},{px},{q * px},0.00088,0,0,0\n")
        f.write(raw_tail)


def run(mod, lab, ex, pl, broker=None, **kw):
    pos = {t: {"qty": q, "market_price": 10000.0} for t, q in (broker or BROKER[lab]).items()}
    return mod.park_holdings(lab, asof=ASOF, plan_dir=pl, exec_dir=ex,
                             broker=(pos, 0.0, {"source": "selfcheck"}),
                             corp_actions=[], rights_subs=[], **kw)


def dri(h):
    return sum(l["qty"] for l in h["lots"] if l["ticker"] == "DRI")


def scenarios(mod, ex, pl, quiet=False):
    """Trả dict tên-kịch-bản → bool đạt. Dùng chung cho bản thật và mutant."""
    res = {}
    h = {lab: run(mod, lab, ex, pl) for lab in ACCTS}
    res["T1_ok_both"] = all(h[l]["reconcile"]["ok"] for l in ACCTS)
    res["T1_dri"] = dri(h["SpaceX"]) == 2500 and dri(h["ZaloPay"]) == 1300
    res["T1_fpt_once"] = all(sum(x["qty"] for x in h[l]["lots"] if x["ticker"] == "FPT")
                             == BROKER[l]["FPT"] for l in ACCTS)
    res["T1_accounts_differ"] = dri(h["SpaceX"]) != dri(h["ZaloPay"])
    res["T1_dri_unverified"] = all("DRI" in h[l]["unverified_tickers"] for l in ACCTS)
    # T3: lệch dư (broker DRI thấp hơn 100cp nữa) KHÔNG được giải thích ⇒ vẫn chặn
    r3 = run(mod, "SpaceX", ex, pl, broker={"DRI": 2400, "FPT": 800})
    res["T3_residual_blocks"] = (not r3["reconcile"]["ok"]
                                 and [m["diff"] for m in r3["reconcile"]["mismatches"]] == [100])
    return res, h


def main():
    sb, ex, pl = build_sandbox()
    try:
        print("== bản thật ==")
        res, h = scenarios(PH, ex, pl)
        for k, v in res.items():
            check(k, v, json.dumps({l: h[l]["reconcile"]["mismatches"] for l in ACCTS}))
        check("T1_note_mentions_statement",
              any("chỉ có ở statement DNSE" in w for w in h["SpaceX"]["warnings"]))

        # T2: tắt cờ ⇒ hành vi cũ
        r = run(PH, "SpaceX", ex, pl, broker_statement=False)
        check("T2_flag_off_old_behavior", not r["reconcile"]["ok"] and dri(r) == 3700)

        # T4: statement 21/10 THIẾU ⇒ hành vi cũ, không đoán
        p21 = os.path.join(ex, "dnse_khoplenh_broker_confirm_21-10-2026.csv")
        bak = p21 + ".bak"
        shutil.move(p21, bak)
        r = run(PH, "SpaceX", ex, pl)
        check("T4_missing_statement_old_behavior", not r["reconcile"]["ok"] and dri(r) == 3700)
        # T5: statement HỎNG (khối lượng NaN) ⇒ không sập, ngày đó chỉ journal, có ghi chú
        write_stmt(ex, "21-10-2026", [("21/10/2026", "BÁN", "DRI", ACCTS["SpaceX"], 1200, 15400)],
                   raw_tail=f"21/10/2026,BÁN,DRI,{ACCTS['SpaceX']},,15400,,0.00088,0,0,0\n")
        try:
            r = run(PH, "SpaceX", ex, pl)
            check("T5_corrupt_statement_no_crash_old_behavior",
                  not r["reconcile"]["ok"] and dri(r) == 3700
                  and any("KHÔNG dùng được" in w for w in r["warnings"]))
        except Exception as e:
            check("T5_corrupt_statement_no_crash_old_behavior", False, f"{type(e).__name__}: {e}")
        # T6: MUA chỉ có ở statement ⇒ KHÔNG thêm lô, đối soát chặn
        write_stmt(ex, "21-10-2026", [("21/10/2026", "MUA", "HPG", ACCTS["SpaceX"], 500, 25000)])
        r = run(PH, "SpaceX", ex, pl, broker={"DRI": 3700, "FPT": 800, "HPG": 500})
        check("T6_manual_buy_not_added",
              not r["reconcile"]["ok"] and not any(l["ticker"] == "HPG" for l in r["lots"])
              and any("MUA +500cp" in w for w in r["warnings"]))
        os.remove(p21)
        shutil.move(bak, p21)
        # T7: statement ngày CHỤP snapshot (30/09) đã nằm trong bootstrap ⇒ bỏ qua
        write_stmt(ex, "30-09-2026", [("30/09/2026", "BÁN", "DRI", ACCTS["SpaceX"], 100, 15400)])
        r = run(PH, "SpaceX", ex, pl)
        check("T7_snapshot_day_ignored", r["reconcile"]["ok"] and dri(r) == 2500)
        os.remove(os.path.join(ex, "dnse_khoplenh_broker_confirm_30-09-2026.csv"))
        # T8: journal > statement (statement thiếu dòng của bot) ⇒ giữ journal + ghi chú
        p20 = os.path.join(ex, "dnse_khoplenh_broker_confirm_20-10-2026.csv")
        shutil.copy(p20, p20 + ".bak")
        write_stmt(ex, "20-10-2026", [("20/10/2026", "BÁN", "FPT", ACCTS["ZaloPay"], 100, 100000)])
        r = run(PH, "SpaceX", ex, pl)
        check("T8_journal_gt_statement_keeps_journal",
              r["reconcile"]["ok"] and any("journal 200 > statement 0" in w for w in r["warnings"]))
        shutil.move(p20 + ".bak", p20)

        # ── Mutant: mỗi mutant PHẢI làm ít nhất một kịch bản fail
        print("== mutant ==")
        ph_src = open(PH.__file__, encoding="utf-8").read()
        bfc_src = open(BFC.__file__, encoding="utf-8").read()
        mutants = {
            "M1_no_subaccount_filter": ("bfc", 'mine = df[df["_acct"] == target]', "mine = df"),
            "M2_no_double_count_guard": ("ph", "j, b = journal_qty.get((d, tk, side), 0), int(bf.qty(tk, side))",
                                         "j, b = 0, int(bf.qty(tk, side))"),
            "M3_residual_passes": ("ph", "if lq != bq:", "if False:"),
            "M4_apply_manual_buys": ("ph", 'elif b > j and side == "buy":', 'elif False:'),
        }
        for name, (which, old, new) in mutants.items():
            src = bfc_src if which == "bfc" else ph_src
            if old not in src:
                check(f"{name}_anchor_found", False, old)
                continue
            path = BFC.__file__ if which == "bfc" else PH.__file__
            m = types.ModuleType(f"mut_{name}")
            m.__file__ = path
            exec(compile(src.replace(old, new, 1), path, "exec"), m.__dict__)
            saved = sys.modules.get("broker_fill_confirm")
            if which == "bfc":
                sys.modules["broker_fill_confirm"] = m
                target = PH
            else:
                target = m
            try:
                mres, _ = scenarios(target, ex, pl)
                killed = not all(mres.values())
                if name == "M4_apply_manual_buys":
                    write_stmt(ex, "21-10-2026", [("21/10/2026", "MUA", "HPG", ACCTS["SpaceX"], 500, 25000)])
                    r = run(target, "SpaceX", ex, pl, broker={"DRI": 3700, "FPT": 800, "HPG": 500})
                    killed = not (not r["reconcile"]["ok"]
                                  and not any(l["ticker"] == "HPG" for l in r["lots"])
                                  and any("MUA +500cp" in w for w in r["warnings"])
                                  and not any("SELL HPG" in w for w in r["warnings"]))
                    write_stmt(ex, "21-10-2026", [("21/10/2026", "BÁN", "DRI", ACCTS["ZaloPay"], 600, 15400),
                                                  ("21/10/2026", "BÁN", "DRI", ACCTS["SpaceX"], 800, 15400),
                                                  ("21/10/2026", "BÁN", "DRI", ACCTS["SpaceX"], 400, 15400)])
            except Exception as e:
                killed, mres = True, {"exception": f"{type(e).__name__}: {e}"}
            finally:
                if saved is not None:
                    sys.modules["broker_fill_confirm"] = saved
            check(f"{name}_killed", killed,
                  json.dumps({k: v for k, v in mres.items() if v is not True}, ensure_ascii=False))
    finally:
        shutil.rmtree(sb, ignore_errors=True)
    print(f"\n{'PASS' if not FAILS else 'FAIL'} ({len(FAILS)} lỗi){': ' + ', '.join(FAILS) if FAILS else ''}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

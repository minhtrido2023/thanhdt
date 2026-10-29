#!/usr/bin/env python3
"""Selfcheck sổ lô (`park_holdings`) đọc LỆNH TAY ĐÃ KHAI — ca SCL 29/10/2026 (job Taylor_20261029_173430).

Hermetic: bootstrap/journal/statement/sổ khai/dnse_raw giả trong tmp, `broker=` bơm tay,
corp_actions=[], rights_subs=[]. Chạy CẢ SpaceX và ZaloPay (§12), đủ 2 TZ (§16/§19):
    env -u TZ python3 bin/park_holdings_manual_lot_selfcheck.py
    TZ=America/New_York python3 bin/park_holdings_manual_lot_selfcheck.py
    python3 bin/park_holdings_manual_lot_selfcheck.py --mutants   # mỗi mutant PHẢI làm selfcheck đỏ

Kịch bản: bootstrap 01/10 SCL LAG 500 (05/10) + 300 (10/10) ở SpaceX, 500 (05/10) ở ZaloPay; bot mua
28/10 SCL LAG 3×100 (SpaceX) / 2×100 (ZaloPay); user bán tay 29/10 800 / 500 @29.600 (VERIFIED).
Broker 30/10: SCL 300 / 200 ⇒ lô còn lại PHẢI là đúng các lô 28/10 (FIFO lô cũ trước), không gộp.
`PH_MLS_BIN=<dir>` = chạy trên bản bin khác (mutation test).
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b: không gửi cảnh báo thật
os.environ.pop("MIKE_MANUAL_ACTIONS_FILE", None)

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.environ.get("PH_MLS_BIN") or HERE
sys.path.insert(0, BIN)

ACCTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
ASOF, D = "2026-10-30", "2026-10-29"
BOOT = {"SpaceX": [("SCL", "LAG", 500, "2026-10-05"), ("SCL", "LAG", 300, "2026-10-10"),
                   ("FPT", "PARK", 1000, "2026-09-01")],
        "ZaloPay": [("SCL", "LAG", 500, "2026-10-05"), ("FPT", "PARK", 400, "2026-09-01")]}
BUY28 = {"SpaceX": 3, "ZaloPay": 2}                  # số lô 100cp mua 28/10
SOLD = {"SpaceX": (800, "20261029_344271"), "ZaloPay": (500, "20261029_346911")}
BROKER = {"SpaceX": {"SCL": 300, "FPT": 1000}, "ZaloPay": {"SCL": 200, "FPT": 400}}
HDR = "ngay_gd,loai_lenh,ma,tieu_khoan,khoi_luong,gia_khop,gia_tri_khop,ty_le_phi,phi_tra_so,phi_dnse,thue\n"
FAILS = []


def check(cond, name):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def order(oid, qty):
    return {"id": oid, "symbol": "SCL", "side": "NS", "orderType": "LO", "orderStatus": "Filled",
            "price": 29600, "quantity": qty, "fillQuantity": qty, "averagePrice": 29600,
            "transDate": D, "createdDate": f"{D}T07:26:56Z"}


def rec(account, qty=None, status="VERIFIED"):
    q, oid = SOLD[account]
    q = qty or q
    v = {"status": status, "envelope_account_no": ACCTS[account], "method": "dnse_api.order_history",
         "verified_at": f"{D}T23:45:00+07:00", "pages_read": 1, "broker_order": order(oid, q)}
    return {"id": f"MA-{account}-{oid}", "date": D, "time_ict": "14:26:56", "account": account,
            "account_no": ACCTS[account], "ticker": "SCL", "side": "sell", "qty": q, "price": 29600.0,
            "broker_order_id": oid, "source": "selfcheck", "declared_at": f"{D}T23:44:00+07:00",
            "verification": v}


class Sandbox:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="ph_mls_")
        self.ex = os.path.join(self.root, "data", "execution_logs")
        self.pl = os.path.join(self.root, "data", "trade_plans")
        for d in (self.ex, self.pl, os.path.join(self.root, "secrets")):
            os.makedirs(d)
        with open(os.path.join(self.root, "secrets", "trading_bot_accounts.json"), "w") as f:
            json.dump({"accounts": [{"label": k, "account_id": v} for k, v in ACCTS.items()]}, f)
        self.boot()
        for lab in ACCTS:
            with open(os.path.join(self.ex, f"exec_{lab}_2026-10-28_journal.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["ts", "event", "ticker", "side", "qty", "price", "child_oid", "parent_id",
                            "book", "play_type"])
                for i in range(BUY28[lab]):
                    w.writerow([f"2026-10-28T10:0{i}:00", "FILL", "SCL", "buy", 100, 32500,
                                f"c{i}-{lab}", f"BUY-SCL-{lab}", "LAG", ""])

    def boot(self, extra=()):
        for lab, pos in BOOT.items():
            rows = list(pos) + [x for x in extra if x[0] == lab for x in [x[1:]]]
            with open(os.path.join(self.pl, f"bootstrap_book_snapshot_{lab}_20261001.json"), "w") as f:
                json.dump({"_status": "APPROVED selfcheck", "reconcile_ok": True, "day0_date": "2026-10-01",
                           "broker_source": {"ts": "2026-09-30T19:10:00"},
                           "positions": [{"ticker": t, "book": b, "qty": q, "cost_price_vnd": 30000,
                                          "entry_date": e} for t, b, q, e in rows]}, f)

    def ledger(self, actions, raw_for=None):
        """Ghi sổ khai + bản sao thô order_history (evidence_check đòi khớp từng byte).
        `raw_for` = list record cần có bản sao thô (mặc định: mọi record)."""
        p = os.path.join(self.root, "data", "user_manual_actions.json")
        if actions is None:
            if os.path.exists(p):
                os.remove(p)
        else:
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"schema_version": 1, "actions": actions}, f)
        rawp = os.path.join(self.ex, f"dnse_raw_{D}.jsonl")
        if os.path.exists(rawp):
            os.remove(rawp)
        for a in (actions or []) if raw_for is None else raw_for:
            v = a["verification"]
            with open(rawp, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": f"{D}T23:45:00", "kind": "order_history",
                                    "account_no": v["envelope_account_no"], "account_label": a["account"],
                                    "payload": {"accountNo": v["envelope_account_no"],
                                                "data": [v["broker_order"]]}}, ensure_ascii=False) + "\n")

    def statement(self, rows):
        p = os.path.join(self.ex, "dnse_khoplenh_broker_confirm_29-10-2026.csv")
        if rows is None:
            if os.path.exists(p):
                os.remove(p)
            return
        with open(p, "w") as f:
            f.write(HDR)
            for lab, q in rows:
                f.write(f"29/10/2026,BÁN,SCL,{ACCTS[lab]},{q},29600,{q * 29600},0.00088,0,0,0\n")

    def run(self, lab, broker=None):
        import park_holdings as PH
        pos = {t: {"qty": q, "market_price": 30000.0} for t, q in (broker or BROKER[lab]).items()}
        return PH.park_holdings(lab, asof=ASOF, plan_dir=self.pl, exec_dir=self.ex,
                                broker=(pos, 0.0, {"source": "selfcheck"}), corp_actions=[],
                                rights_subs=[], need_price=False)


def scl_lots(h):
    return [(l["book"], l["entry_date"], l["qty"]) for l in h["lots"] if l["ticker"] == "SCL"]


def mism(h, tk="SCL"):
    return [(m["ledger_qty"], m["broker_qty"]) for m in h["reconcile"]["mismatches"] if m["ticker"] == tk]


def clean(h):
    """SCL khớp broker, không UNVERIFIED (⇒ auto-exit không chặn)."""
    return not mism(h) and "SCL" not in h["unverified_tickers"]


def main():
    s = Sandbox()
    want = {lab: [("LAG", "2026-10-28", 100)] * BUY28[lab] for lab in ACCTS}

    # T0 — inert: không có sổ / sổ rỗng ⇒ y hệt nhau, SCL vẫn lệch 1100/300 · 700/200 (hành vi cũ)
    s.ledger(None)
    absent = {lab: s.run(lab) for lab in ACCTS}
    s.ledger([])
    empty = {lab: s.run(lab) for lab in ACCTS}
    for lab in ACCTS:
        check(json.dumps(absent[lab], sort_keys=True, default=str) == json.dumps(empty[lab], sort_keys=True, default=str),
              f"T0 {lab}: sổ vắng == sổ rỗng (byte-identical)")
        check(mism(absent[lab]) == [(sum(q for t, _, q, _ in BOOT[lab] if t == "SCL") + 100 * BUY28[lab],
                                     BROKER[lab]["SCL"])], f"T0 {lab}: không sổ ⇒ vẫn lệch như cũ")

    # T1 — ca thật: 2 lệnh VERIFIED ⇒ sổ == broker, không UNVERIFIED, lô 28/10 giữ nguyên (FIFO cũ trước)
    s.ledger([rec("SpaceX"), rec("ZaloPay")])
    h = {lab: s.run(lab) for lab in ACCTS}
    for lab in ACCTS:
        check(h[lab]["reconcile"]["ok"] and clean(h[lab]), f"T1 {lab}: SCL khớp broker + không UNVERIFIED")
        check(scl_lots(h[lab]) == want[lab], f"T1 {lab}: còn đúng {BUY28[lab]} lô 28/10, entry_date giữ, không gộp "
                                             f"(thực: {scl_lots(h[lab])})")
        check(sum(l["qty"] for l in h[lab]["lots"] if l["ticker"] == "FPT") == BROKER[lab]["FPT"],
              f"T1 {lab}: mã khác không bị đụng")
    check(scl_lots(h["SpaceX"]) != scl_lots(h["ZaloPay"]), "T1 §12: 2 account ra KHÁC nhau")

    # T2 — §12: sổ chỉ có lệnh SpaceX ⇒ ZaloPay y hệt khi không có sổ
    s.ledger([rec("SpaceX")])
    z = s.run("ZaloPay")
    check(json.dumps(z, sort_keys=True, default=str) == json.dumps(absent["ZaloPay"], sort_keys=True, default=str),
          "T2 §12: lệnh tay SpaceX không ảnh hưởng ZaloPay")
    check(clean(s.run("SpaceX")), "T2: SpaceX vẫn sạch khi chỉ có lệnh của nó")

    # T3 — chưa VERIFIED (có bản ghi broker + bản sao thô nhưng status UNVERIFIED) ⇒ không trừ ⇒ vẫn chặn
    s.ledger([rec("SpaceX", status="UNVERIFIED")])
    r = s.run("SpaceX")
    check(mism(r) == [(1100, 300)] and "SCL" in r["unverified_tickers"], "T3: khai chưa VERIFIED ⇒ vẫn chặn")

    # T4 — khai ≠ thực: khai 700 (broker xác nhận 700) nhưng broker còn 300 ⇒ sổ 400 ≠ 300 ⇒ chặn
    s.ledger([rec("SpaceX", qty=700)])
    r = s.run("SpaceX")
    check(mism(r) == [(400, 300)] and "SCL" in r["unverified_tickers"], "T4: khai ≠ thực ⇒ vẫn chặn (fail-closed)")

    # T5 — statement 29/10 về, KHỚP khai ⇒ statement thắng, không double-count, vẫn sạch
    s.ledger([rec("SpaceX"), rec("ZaloPay")])
    s.statement([("SpaceX", 800), ("ZaloPay", 500)])
    for lab in ACCTS:
        r = s.run(lab)
        check(clean(r) and scl_lots(r) == want[lab], f"T5 {lab}: statement khớp khai ⇒ sạch, không trừ 2 lần")
        check(not any("lệnh tay ĐÃ KHAI + broker xác nhận" in w for w in r["warnings"]),
              f"T5 {lab}: statement thắng (không áp dòng sổ khai)")

    # T6 — statement ≠ khai (statement 600 vs khai 800) ⇒ không coi là đã khai ⇒ UNVERIFIED như cũ
    s.statement([("SpaceX", 600)])
    r = s.run("SpaceX", broker={"SCL": 500, "FPT": 1000})
    check("SCL" in r["unverified_tickers"], "T6: statement ≠ khai ⇒ vẫn chặn")

    # T7 — statement có, sổ rỗng ⇒ hành vi cũ (bán tay chỉ-statement vẫn UNVERIFIED)
    s.ledger([])
    s.statement([("SpaceX", 800)])
    r = s.run("SpaceX")
    check(not mism(r) and "SCL" in r["unverified_tickers"], "T7: statement-only, không khai ⇒ UNVERIFIED như cũ")
    s.statement(None)

    # T8 — mã ở >1 book (SCL LAG + PARK) ⇒ không xác định book bị trừ ⇒ vẫn chặn (B1)
    s.boot(extra=[("SpaceX", "SCL", "PARK", 100, "2026-09-01")])
    s.ledger([rec("SpaceX")])
    r = s.run("SpaceX", broker={"SCL": 400, "FPT": 1000})
    check("SCL" in r["unverified_tickers"] and mism(r), "T8: SCL ở 2 book ⇒ vẫn chặn")
    s.boot()
    shutil.rmtree(s.root, ignore_errors=True)

    print(f"\n{'PASS' if not FAILS else 'FAIL'}: {len(FAILS)} lỗi")
    return 1 if FAILS else 0


# (tên, file, chuỗi gốc, chuỗi thay) — mỗi mutant PHẢI làm selfcheck rc≠0
MUTANTS = [
    ("M1 bỏ trừ lệnh tay", "park_holdings.py",
     '"declared": m["id"]})', '"declared": m["id"], "qty": 0})'),
    ("M2a bỏ kiểm VERIFIED (sổ khai)", "manual_actions.py",
     'if v.get("status") != "VERIFIED":', 'if False:'),
    ("M2b bỏ cổng declared (mọi bán tay 1 book coi như đã khai)", "park_holdings.py",
     'if ev.get("declared") and len(bks) == 1:', 'if len(bks) == 1:'),
    ("M3 §12 bỏ lọc account", "manual_actions.py",
     'if rec["account"] != account_label or not', 'if not'),
    ("M4 statement ≠ khai vẫn coi là đã khai", "park_holdings.py",
     '.get((tk, "sell"), 0) == b - j:', '.get((tk, "sell"), 0) >= 0:'),
]


def run_mutants():
    bad = 0
    for name, fn, old, new in MUTANTS:
        tmp = tempfile.mkdtemp(prefix="ph_mls_mut_")
        mb = os.path.join(tmp, "bin")
        shutil.copytree(HERE, mb, ignore=shutil.ignore_patterns("__pycache__", "*.sh"))
        p = os.path.join(mb, fn)
        src = open(p, encoding="utf-8").read()
        if src.count(old) != 1:
            print(f"MUTANT-SETUP-FAIL {name}: chuỗi gốc xuất hiện {src.count(old)} lần")
            bad += 1
            continue
        if fn == "manual_actions.py" and "M3" in name:   # §12 thứ 2: bỏ luôn so tiểu khoản ở evidence_check
            src = src.replace("if not account_no or _norm_acct(account_no) != _norm_acct(rec[\"account_no\"]):",
                              "if False:")
        open(p, "w", encoding="utf-8").write(src.replace(old, new))
        rc = subprocess.run([sys.executable, os.path.join(HERE, os.path.basename(__file__))],
                            env=dict(os.environ, PH_MLS_BIN=mb), capture_output=True, text=True).returncode
        killed = rc != 0
        print(f"{'KILLED ' if killed else 'SURVIVED'} {name} (rc={rc})")
        bad += not killed
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nmutants: {len(MUTANTS) - bad}/{len(MUTANTS)} bị bắt")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(run_mutants() if "--mutants" in sys.argv else main())

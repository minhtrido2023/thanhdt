#!/usr/bin/env python3
"""Selfcheck sổ LỆNH TAY ĐÃ KHAI (`manual_actions.py`) + 5 consumer — hermetic, KHÔNG gọi DNSE/BQ.

Chạy đủ 2 TZ (§16/§19):
    env -u TZ python3 bin/manual_actions_selfcheck.py
    TZ=America/New_York python3 bin/manual_actions_selfcheck.py
`MA_SC_BIN=<dir>` = chạy trên bản bin KHÁC (mutation test: chép bin, phá 1 dòng, selfcheck phải FAIL).

Ca bắt buộc (job Taylor_20261029_132220): (a) phần dư KHÁC khai vẫn qty_unexplained (rc=5);
(b) khai không có xác nhận broker / bằng chứng lệch không mở cổng; (c) account khác không bị ảnh
hưởng (§12); sổ rỗng ⇒ kết quả y hệt không có sổ.
"""
import csv
import json
import os
import sys
import tempfile

BIN = os.environ.get("MA_SC_BIN") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)
os.environ.pop("MIKE_MANUAL_ACTIONS_FILE", None)
_RIGHTS = tempfile.mkdtemp(prefix="ma_sc_rights_")
os.environ["MIKE_LAG_RIGHTS_DIR"] = _RIGHTS          # sổ quyền mua production không được lọt vào

import manual_actions as ma  # noqa: E402
import daily_nav_snapshot as dns  # noqa: E402
import verify_account_snapshot as vas  # noqa: E402
import exdate_frame  # noqa: E402
import park_holdings  # noqa: E402
import broker_fill_confirm as bfc  # noqa: E402
import plan_position_drift_check as ppd  # noqa: E402

SPX, ZLP = "0002023347", "0001743768"
D, PREV = "2026-10-29", "2026-10-28"
FAILS = []


def check(cond, name):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def order(oid="20261029_344271", sym="SCL", side="NS", fq=800, td=D):
    return {"id": oid, "symbol": sym, "side": side, "orderType": "LO", "orderStatus": "Filled",
            "price": 29600, "quantity": fq, "fillQuantity": fq, "averagePrice": 29600,
            "transDate": td, "createdDate": f"{td}T07:26:56Z"}


def rec(account="SpaceX", acct_no=SPX, oid="20261029_344271", qty=800, side="sell", status="VERIFIED",
        bo=None, env_acct=None, ticker="SCL", time_ict="14:26:56"):
    v = {"status": status}
    if status == "VERIFIED":
        v.update(envelope_account_no=env_acct or acct_no, method="dnse_api.order_history",
                 verified_at="2026-10-29T14:40:00+07:00", pages_read=1,
                 broker_order=bo if bo is not None else order(oid=oid, fq=qty, sym=ticker,
                                                               side="NS" if side == "sell" else "NB"))
    return {"id": f"MA-{account}-{oid}", "date": D, "time_ict": time_ict, "account": account,
            "account_no": acct_no, "ticker": ticker, "side": side, "qty": qty, "price": 29600.0,
            "broker_order_id": oid, "source": "selfcheck", "declared_at": "2026-10-29T20:30:00+07:00",
            "verification": v}


class Sandbox:
    """wc_root tạm: data/execution_logs (journal, statement) + data/user_manual_actions.json."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="ma_sc_wc_")
        self.exec = os.path.join(self.root, "data", "execution_logs")
        os.makedirs(self.exec)
        self.ledger = os.path.join(self.root, "data", "user_manual_actions.json")
        os.makedirs(os.path.join(self.root, "secrets"))
        with open(os.path.join(self.root, "secrets", "trading_bot_accounts.json"), "w") as f:
            json.dump({"accounts": [{"label": "SpaceX", "account_id": SPX},
                                    {"label": "ZaloPay", "account_id": ZLP}]}, f)

    def journal(self, account, fills):
        p = os.path.join(self.exec, f"exec_{account}_{D}_journal.csv")
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
                        "filled_total", "book", "play_type", "note"])
            for oid, tk, side, q in fills:
                w.writerow([f"{D}T10:00:00", "FILL", "P", tk, side, oid, q, 23500, q, "PARK", "", ""])

    def statement(self, rows):
        p = bfc.broker_csv_path(self.root, D)
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["tieu_khoan", "ma", "loai_lenh", "khoi_luong", "gia_tri_khop"])
            for acct, tk, side, q in rows:
                w.writerow([acct, tk, side, q, q * 29600])

    def write_ledger(self, actions, raw=True):
        """Ghi sổ + (raw=True) bản sao THÔ kind=order_history của từng bản ghi broker đã lưu vào
        dnse_raw_<ngày>.jsonl — artifact độc lập mà evidence_check đòi khớp từng byte."""
        with open(self.ledger, "w", encoding="utf-8") as f:
            json.dump({"schema_version": 1, "actions": actions}, f)
        rawp = ma.raw_log_path(self.exec, D)
        if os.path.exists(rawp):
            os.remove(rawp)
        if raw:
            for a in actions:
                v = a.get("verification") or {}
                if v.get("status") == "VERIFIED" and isinstance(v.get("broker_order"), dict):
                    with open(rawp, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"ts": f"{D}T14:40:00", "kind": "order_history",
                                            "account_no": v["envelope_account_no"],
                                            "account_label": a["account"],
                                            "payload": {"accountNo": v["envelope_account_no"],
                                                        "data": [v["broker_order"]]}},
                                           ensure_ascii=False) + "\n")

    def net(self, account, acct_no):
        vas.EXEC_DIR = self.exec
        notes, miss = [], []
        out = exdate_frame.net_fills_journal_and_broker(account, PREV, D, cache=None, missing_out=miss,
                                                        wc_root=self.root, notes_out=notes,
                                                        account_no=acct_no)
        return out, notes, miss


def residual(net_fill, qty_now, qty_prev=1100.0):
    v, _ = dns.classify_qty_residual(None, qty_now, qty_prev, net_fill, PREV)
    return v


# ── 1. cổng KL qua exdate_frame (⇒ daily_nav_snapshot / compute_active_nav) ───────────────────
s = Sandbox()
s.journal("SpaceX", [("28241", "VPB", "sell", 100)])
s.journal("ZaloPay", [])
base_out, base_notes, base_miss = s.net("SpaceX", SPX)
check(base_out.get("SCL", 0) == 0 and residual(base_out.get("SCL", 0), 300) == "qty_unexplained",
      "không có sổ: SCL −800 chặn rc=5 như master (qty_unexplained)")
s.write_ledger([])
o2, n2, m2 = s.net("SpaceX", SPX)
check((o2, n2, m2) == (base_out, base_notes, base_miss), "sổ RỖNG ⇒ kết quả y hệt không có sổ (INERT)")

s.write_ledger([rec()])
out, notes, _ = s.net("SpaceX", SPX)
check(out.get("SCL") == -800 and residual(out["SCL"], 300) == "ok",
      "khai + VERIFIED ⇒ SCL −800 giải thích được ⇒ cổng mở")
check(out.get("VPB") == base_out.get("VPB"), "fill bot khác (VPB) không đổi")
check(residual(out["SCL"], 200) == "qty_unexplained",
      "(a) phần dư KHÁC khai (KL 1100→200, khai −800) vẫn qty_unexplained ⇒ rc=5")
check(residual(out["SCL"], 400) == "qty_unexplained", "(a') bán ÍT hơn khai cũng vẫn chặn")

for name, r in (("UNVERIFIED", rec(status="UNVERIFIED")),
                ("REJECTED", rec(status="REJECTED")),
                ("broker fillQuantity 500 ≠ khai 800", rec(bo=order(fq=500))),
                ("broker side NB ≠ khai sell", rec(bo=order(side="NB"))),
                ("broker symbol khác", rec(bo=order(sym="SHI"))),
                ("broker transDate khác", rec(bo=order(td="2026-10-28"))),
                ("broker order id khác", rec(bo=order(oid="20261029_999"))),
                ("envelope tiểu khoản ZaloPay", rec(env_acct=ZLP))):
    s.write_ledger([r])
    o, n, _ = s.net("SpaceX", SPX)
    check(o.get("SCL", 0) == 0 and any("KHÔNG tính" in x for x in n),
          f"(b) {name} ⇒ không mở cổng + ghi lý do")

s.write_ledger([rec()])
oz, nz, mz = s.net("ZaloPay", ZLP)
s.write_ledger([])
oz0, nz0, mz0 = s.net("ZaloPay", ZLP)
check((oz, nz, mz) == (oz0, nz0, mz0), "(c) khai của SpaceX không ảnh hưởng ZaloPay (§12)")
s.write_ledger([rec(account="SpaceX", acct_no=ZLP, env_acct=ZLP)])
o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL", 0) == 0, "(c') dòng gắn nhãn SpaceX nhưng tiểu khoản ZaloPay ⇒ không tính cho SpaceX")
s.write_ledger([rec(account="ZaloPay", acct_no=ZLP, oid="20261029_346911", qty=500)])
o, _, _ = s.net("ZaloPay", ZLP)
check(o.get("SCL") == -500, "(c'') ZaloPay khai đúng tiểu khoản ⇒ −500 của riêng ZaloPay")

# journal đã có chính lệnh đó (child_oid trùng) ⇒ không đếm đôi
s.journal("SpaceX", [("28241", "VPB", "sell", 100), ("344271", "SCL", "sell", 800)])
s.write_ledger([rec()])
o, _, _ = s.net("SpaceX", SPX)
check(o.get("SCL") == -800, "lệnh khai trùng child_oid journal ⇒ không đếm đôi (−800, không −1600)")
s.journal("SpaceX", [("28241", "VPB", "sell", 100)])

# statement về: statement thắng, sổ chỉ đối chiếu
s.statement([(SPX, "VPB", "BÁN", 100), (SPX, "SCL", "BÁN", 800)])
check(bfc.load_broker_fills(D, "SpaceX", s.root, allow_fetch=False).available,
      "statement giả đọc được (tiền đề cho 2 ca dưới — không vacuous)")
o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL") == -800 and not any("≠ statement" in x for x in n),
      "statement về + khớp khai ⇒ −800 (không cộng đôi), không cảnh báo")
s.statement([(SPX, "VPB", "BÁN", 100), (SPX, "SCL", "BÁN", 500)])
o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL") == -500 and any("≠ statement−journal" in x for x in n),
      "statement về nhưng lệch khai ⇒ statement thắng + CẢNH BÁO lệch")
os.remove(bfc.broker_csv_path(s.root, D))

# sổ hỏng ⇒ fail-closed (raise), không âm thầm bỏ qua
with open(s.ledger, "w") as f:
    f.write("{not json")
try:
    s.net("SpaceX", SPX)
    check(False, "sổ hỏng ⇒ raise ManualActionsError")
except ma.ManualActionsError:
    check(True, "sổ hỏng ⇒ raise ManualActionsError")
s.write_ledger([rec(), rec(account="SpaceX")])
try:
    ma.load_all(s.ledger)
    check(False, "trùng broker_order_id ⇒ raise (chống đếm đôi)")
except ma.ManualActionsError:
    check(True, "trùng broker_order_id ⇒ raise (chống đếm đôi)")

# ── 2. verify (đọc order-history giả) ─────────────────────────────────────────────────────────
s.write_ledger([dict(rec(status="UNVERIFIED"), verification={"status": "UNVERIFIED"})])
env_ok = {"accountNo": SPX, "data": [order(), order(oid="20261029_1", sym="VPB")]}
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: env_ok)
check(res[0][1] == "VERIFIED" and ma.evidence_check(ma.load_all(s.ledger)[0], SPX, s.exec)[0],
      "verify: order-history khớp ⇒ VERIFIED + bằng chứng dùng được")
s.write_ledger([dict(rec(), verification={"status": "UNVERIFIED"})])
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: {"accountNo": ZLP, "data": [order()]})
check(res[0][1] == "REJECTED", "verify: envelope tiểu khoản khác ⇒ REJECTED (§12)")
s.write_ledger([dict(rec(), verification={"status": "UNVERIFIED"})])
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: {"accountNo": SPX, "data": [order(fq=500)]})
check(res[0][1] == "REJECTED", "verify: KL broker 500 ≠ khai 800 ⇒ REJECTED")
s.write_ledger([dict(rec(), verification={"status": "UNVERIFIED"})])
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: {"accountNo": SPX, "data": []})
check(res[0][1] == "REJECTED", "verify: không có lệnh ⇒ REJECTED")


def _boom(a, d):
    raise OSError("mạng")


s.write_ledger([rec()])
res = ma.verify(path=s.ledger, fetch_fn=_boom, recheck=True)
check(res[0][1] == "VERIFIED" and ma.load_all(s.ledger)[0]["verification"]["status"] == "VERIFIED",
      "verify: DNSE lỗi ⇒ giữ nguyên trạng thái (không tự hạ/không tự nâng)")

# ── 3. park_holdings.statement_extra_sells ────────────────────────────────────────────────────
s.write_ledger([])
ev0, nt0 = park_holdings.statement_extra_sells("SpaceX", {}, PREV, D, s.exec)
s.write_ledger([rec(), rec(oid="20261029_2", side="buy", ticker="VPB", qty=100)])
ev, nt = park_holdings.statement_extra_sells("SpaceX", {}, PREV, D, s.exec)
check((ev0, nt0) == ([], []), "park: sổ rỗng ⇒ không event")
check(len(ev) == 1 and ev[0]["ticker"] == "SCL" and ev[0]["qty"] == 800
      and ev[0]["parent_id"] == "manual_action", "park: BÁN tay VERIFIED ⇒ trừ lô FIFO 800")
check(any("MUA" in x and "KHÔNG thêm lô" in x for x in nt), "park: MUA tay ⇒ chỉ ghi chú, không thêm lô")
evz, _ = park_holdings.statement_extra_sells("ZaloPay", {}, PREV, D, s.exec)
check(evz == [], "park (c): ZaloPay không nhận lệnh tay SpaceX")
s.write_ledger([rec(status="UNVERIFIED")])
ev, _ = park_holdings.statement_extra_sells("SpaceX", {}, PREV, D, s.exec)
check(ev == [], "park (b): UNVERIFIED ⇒ không áp")

# ── 4. reconcile_lines (EOD leg 3) ────────────────────────────────────────────────────────────
bk = bfc.BrokerFills(True, "", "", {("SCL", "sell"): {"qty": 800, "value": 0, "fee": 0, "tax": 0}})
plain = bfc.reconcile_lines(bk, {}, {})
check(any("🚨" in x for x in plain), "EOD: không khai ⇒ 🚨 lệnh ngoài kế hoạch (như master)")
check(bfc.reconcile_lines(bk, {}, {}, {}) == plain, "EOD: manual rỗng ⇒ y hệt master")
ok = bfc.reconcile_lines(bk, {}, {}, {("SCL", "sell"): 800})
check(not any("🚨" in x for x in ok), "EOD: lệnh tay đã khai đúng KL ⇒ không 🚨")
bad = bfc.reconcile_lines(bk, {}, {}, {("SCL", "sell"): 500})
check(any("🚨" in x for x in bad) and any("800cp" in x for x in bad),
      "EOD (a): broker 800 ≠ khai 500 ⇒ vẫn 🚨, báo ĐỦ 800cp (không trừ khai lệch)")
bk2 = bfc.BrokerFills(True, "", "", {("VPB", "sell"): {"qty": 600, "value": 0, "fee": 0, "tax": 0}})
mixed = bfc.reconcile_lines(bk2, {("VPB", "sell"): 100}, {("VPB", "sell"): 100}, {("VPB", "sell"): 500})
check(not any("🚨" in x for x in mixed), "EOD: mã trong plan, bot 100 + tay 500 = broker 600 ⇒ không 🚨")
s.write_ledger([rec()])
rl = ma.report_lines("SpaceX", SPX, D, path=s.ledger)
check(rl and rl[0].startswith("ℹ️") and "SCL" in rl[1] and "⚠️" not in rl[1],
      "EOD: mục ℹ️ 'Lệnh tay đã khai (đã xác nhận broker)'")
check(ma.report_lines("ZaloPay", ZLP, D, path=s.ledger) == [], "EOD (c): ZaloPay không thấy khai SpaceX")

# ── 5. plan_position_drift_check ──────────────────────────────────────────────────────────────
os.environ["MIKE_DRIFT_SELFCHECK"] = "1"
os.environ["MIKE_MANUAL_ACTIONS_FILE"] = s.ledger


def drift_res(unexpl):
    return {"notes": [], "items": [{"ticker": "SCL", "qty_flag": True, "qty_unexplained": unexpl,
                                    "px_flag": False, "mixed_frame_now": False, "fills_unsure": True,
                                    "base_ts": f"{D}T04:45:00"}]}


r = drift_res(-800)
ppd._apply_manual_actions(r, "SpaceX", SPX, D)
check(r["items"] == [], "drift: KL −800 = lệnh tay đã khai ⇒ không cờ")
r = drift_res(-900)
ppd._apply_manual_actions(r, "SpaceX", SPX, D)
check(len(r["items"]) == 1, "drift (a): −900 ≠ khai −800 ⇒ vẫn cờ")
r = drift_res(-800)
r["items"][0]["base_ts"] = f"{D}T19:05:00"
ppd._apply_manual_actions(r, "SpaceX", SPX, D)
check(len(r["items"]) == 1, "drift: mốc SAU giờ lệnh tay ⇒ không trừ")
r = drift_res(-800)
ppd._apply_manual_actions(r, "ZaloPay", ZLP, D)
check(len(r["items"]) == 1, "drift (c): ZaloPay không trừ lệnh tay SpaceX")
os.environ.pop("MIKE_MANUAL_ACTIONS_FILE")
r = drift_res(-800)
ppd._apply_manual_actions(r, "SpaceX", SPX, D)
check(len(r["items"]) == 1, "drift: selfcheck không trỏ sổ ⇒ không đọc sổ production")

# ── 6. vòng 2 arch-review: bằng chứng gắn artifact độc lập + 3 mutant ─────────────────────────
print("\n[vòng 2] artifact độc lập dnse_raw + mutant m1/m2/m3")
s.write_ledger([rec()], raw=False)
o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL", 0) == 0 and any("khớp từng byte" in x for x in n),
      "(3) VERIFIED nhưng KHÔNG có bản sao trong dnse_raw ⇒ không mở cổng, nêu lý do")
s.write_ledger([rec()])
rawp = ma.raw_log_path(s.exec, D)
tampered = open(rawp, encoding="utf-8").read().replace('"fillQuantity": 800', '"fillQuantity": 801')
open(rawp, "w", encoding="utf-8").write(tampered)
o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL", 0) == 0, "(3) bản sao thô lệch 1 byte so với broker_order trong sổ ⇒ không mở cổng")
s.write_ledger([rec()])
os.remove(rawp)          # cùng lệnh nhưng dưới tiểu khoản ZaloPay (§12)
with open(rawp, "w", encoding="utf-8") as f:
    f.write(json.dumps({"ts": f"{D}T14:40:00", "kind": "order_history", "account_no": ZLP,
                        "payload": {"accountNo": ZLP, "data": [order()]}}) + "\n")
o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL", 0) == 0, "(3) bản sao thô nằm dưới tiểu khoản KHÁC (ZaloPay) ⇒ không tính cho SpaceX (§12)")
for name, mut in (("method sai", lambda v: v.update(method="manual")),
                  ("orderStatus chưa khớp", lambda v: v["broker_order"].update(orderStatus="Pending")),
                  ("verified_at trước ngày giao dịch", lambda v: v.update(verified_at="2026-10-28T10:00:00+07:00"))):
    r_ = rec()
    mut(r_["verification"])
    s.write_ledger([r_])
    o, n, _ = s.net("SpaceX", SPX)
    check(o.get("SCL", 0) == 0 and any("KHÔNG tính" in x for x in n), f"(3) {name} ⇒ không mở cổng")

# m1: park — ngày ĐÃ có statement ⇒ statement thắng, KHÔNG áp thêm dòng tay (không trừ lô đôi)
s.write_ledger([rec()])
s.statement([(SPX, "SCL", "BÁN", 800)])
ev, nt = park_holdings.statement_extra_sells("SpaceX", {}, PREV, D, s.exec)
check(len(ev) == 1 and ev[0]["parent_id"] == "broker_statement" and sum(e["qty"] for e in ev) == 800,
      "(m1) park: ngày có statement ⇒ chỉ 1 event từ statement, KHÔNG áp thêm dòng tay (800, không 1600)")
os.remove(bfc.broker_csv_path(s.root, D))

# m2: khai < fillQuantity broker ⇒ REJECTED (== không được nới thành >=)
s.write_ledger([dict(rec(qty=500), verification={"status": "UNVERIFIED"})])
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: {"accountNo": SPX, "data": [order(fq=800)]})
check(res[0][1] == "REJECTED" and "KL khớp" in res[0][2],
      "(m2) verify: khai 500 < broker fillQuantity 800 ⇒ REJECTED (lý do nêu KL khớp)")
s.write_ledger([rec(qty=500, bo=order(fq=800))])
check(not ma.evidence_check(ma.load_all(s.ledger)[0], SPX, s.exec)[0],
      "(m2) evidence_check: khai 500 < broker 800 ⇒ KHÔNG ok")

# m3: dòng tay ngày ĐÚNG BẰNG after_date không được đếm (khoảng nửa mở (after, upto])
s.write_ledger([rec()])
check(ma.gate_fills("SpaceX", SPX, D, D, path=s.ledger) == {},
      "(m3) gate_fills(after=D, upto=D) ⇒ rỗng (dòng ngày D nằm NGOÀI (D, D])")
check(list(ma.gate_fills("SpaceX", SPX, PREV, D, path=s.ledger)) == [D],
      "(m3') gate_fills(after=PREV, upto=D) ⇒ có ngày D (không vacuous)")

# phân trang order_history (6): lý do REJECTED nêu số trang đã đọc; _pages lưu vào VERIFIED
s.write_ledger([dict(rec(), verification={"status": "UNVERIFIED"})])
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: {"accountNo": SPX, "data": [], "_pages": 3})
check(res[0][1] == "REJECTED" and "đã đọc 3 trang" in res[0][2],
      "(6) REJECTED nêu rõ số trang đã đọc")
s.write_ledger([dict(rec(), verification={"status": "UNVERIFIED"})], raw=False)
res = ma.verify(path=s.ledger, fetch_fn=lambda a, d: {"accountNo": SPX, "data": [order()], "_pages": 2})
v0 = ma.load_all(s.ledger)[0]["verification"]
check(res[0][1] == "VERIFIED" and v0.get("pages_read") == 2
      and ma.evidence_check(ma.load_all(s.ledger)[0], SPX, s.exec)[0],
      "(3) verify ghi nguyên envelope vào dnse_raw (kind=order_history) ⇒ evidence_check ok + pages_read=2")


class _FakeClient:
    """DNSEClient giả: 250 lệnh, trang 100 ⇒ 3 trang; mode='ignore' = API lờ pageIndex."""
    mode = "ok"
    calls = []

    @classmethod
    def from_credentials_file(cls):
        return cls()

    def order_history(self, account_no, from_date=None, to_date=None, page_size=None, page_index=None):
        _FakeClient.calls.append(page_index)
        allrows = [order(oid=f"20261029_{i}", sym="VPB") for i in range(250)]
        if _FakeClient.mode == "ignore":
            return {"accountNo": account_no, "data": allrows[:page_size]}
        lo = (page_index - 1) * page_size
        return {"accountNo": account_no, "data": allrows[lo:lo + page_size]}


import types as _types
sys.modules["dnse_api"] = _types.SimpleNamespace(DNSEClient=_FakeClient)
env = ma._dnse_fetch(SPX, D)
check(len(env["data"]) == 250 and env["_pages"] == 3 and _FakeClient.calls == [1, 2, 3],
      "(6) _dnse_fetch đọc HẾT 3 trang (250 lệnh), dừng ở trang ngắn")
_FakeClient.mode = "ignore"
try:
    ma._dnse_fetch(SPX, D)
    check(False, "(6) API lờ pageIndex ⇒ raise")
except RuntimeError as e:
    check("lặp trang trước" in str(e), "(6) API lờ pageIndex ⇒ raise (không kết luận từ danh sách cụt)")
sys.modules.pop("dnse_api")

# (1) drift: lệnh tay đã nằm trong sổ lệnh DNSE (explained_fills đã đếm) ⇒ KHÔNG trừ lần 2
s.write_ledger([rec()])
os.environ["MIKE_DRIFT_SELFCHECK"] = "1"
os.environ["MIKE_MANUAL_ACTIONS_FILE"] = s.ledger
r = drift_res(-800)
ppd._apply_manual_actions(r, "SpaceX", SPX, D, known_oids={"20261029_344271"})
check(len(r["items"]) == 1 and r["items"][0]["qty_flag"],
      "(1) lệnh tay đã có trong final_orders + thêm −800 chưa giải thích cùng mã ⇒ cờ PHẢI còn")
r = drift_res(-800)
ppd._apply_manual_actions(r, "SpaceX", SPX, D, known_oids={"20261029_999"})
check(r["items"] == [], "(1') id lệnh khác ⇒ vẫn trừ lệnh tay như cũ (không vacuous)")
os.environ.pop("MIKE_MANUAL_ACTIONS_FILE")

# (5) prompt_note: 1 ca OK + 1 ca UNVERIFIED; (2) emit_warnings ra stderr
import io
import contextlib
s.write_ledger([rec()])
note_ok = ma.prompt_note("SpaceX", D, path=s.ledger, account_no=SPX)
check("LỆNH TAY ĐÃ KHAI" in note_ok and "đã xác nhận broker — 2026-10-29 BÁN SCL 800cp" in note_ok
      and "CHƯA xác nhận" not in note_ok and "KHÔNG coi là drift" in note_ok,
      "(5) prompt_note ca OK: nêu BÁN SCL 800cp đã xác nhận, không có phần CHƯA xác nhận")
s.write_ledger([rec(status="UNVERIFIED")])
note_bad = ma.prompt_note("SpaceX", D, path=s.ledger, account_no=SPX)
check("CHƯA xác nhận broker" in note_bad and "SCL sell 800cp" in note_bad
      and "đã xác nhận broker —" not in note_bad and "KHÔNG coi là drift" not in note_bad,
      "(5) prompt_note ca UNVERIFIED: coi là CHƯA được giải thích, không bảo đừng coi là drift")
check(ma.prompt_note("ZaloPay", D, path=s.ledger, account_no=ZLP) == "",
      "(5) prompt_note: account khác không thấy khai của SpaceX (§12) ⇒ rỗng")
s.write_ledger([])
check(ma.prompt_note("SpaceX", D, path=s.ledger, account_no=SPX) == "", "(5) prompt_note: sổ rỗng ⇒ ''")

# (6) report_lines: tiêu đề "đã xác nhận broker" chỉ khi có ≥1 dòng VERIFIED hợp lệ
s.write_ledger([rec(status="UNVERIFIED")])
rl_bad = ma.report_lines("SpaceX", SPX, D, path=s.ledger)
check(rl_bad and "đã xác nhận broker" not in " ".join(rl_bad) and "CHƯA có dòng nào" in rl_bad[0],
      "(6) toàn UNVERIFIED ⇒ báo cáo KHÔNG chứa cụm 'đã xác nhận broker'")
s.write_ledger([rec(), rec(oid="20261029_7", status="UNVERIFIED", ticker="VPB", qty=100)])
rl_mix = ma.report_lines("SpaceX", SPX, D, path=s.ledger)
check("đã xác nhận broker" in rl_mix[0] and sum("CHƯA được cổng KL chấp nhận" in x for x in rl_mix) == 1,
      "(6) có ≥1 VERIFIED ⇒ tiêu đề có 'đã xác nhận broker'; dòng UNVERIFIED vẫn bị gắn CHƯA chấp nhận")
s.write_ledger([rec()], raw=False)
rl_noraw = ma.report_lines("SpaceX", SPX, D, path=s.ledger)
check("đã xác nhận broker" not in rl_noraw[0] and "✅ broker xác nhận" not in " ".join(rl_noraw),
      "(6) VERIFIED nhưng thiếu bản sao dnse_raw ⇒ không nói 'đã xác nhận' (✅ theo bằng chứng, không theo status)")

# (2) emit_warnings: cảnh báo crosscheck ra stderr cả ở đường thành công
s.write_ledger([rec()])
s.statement([(SPX, "SCL", "BÁN", 500)])
_buf = io.StringIO()
with contextlib.redirect_stderr(_buf):
    o, n, _ = s.net("SpaceX", SPX)
check(o.get("SCL") == -500 and "≠ statement−journal" in _buf.getvalue() and any("≠ statement−journal" in x for x in n),
      "(2) statement lệch khai ⇒ cảnh báo RA STDERR (đường thành công) chứ không chỉ trong notes_out")
_buf = io.StringIO()
with contextlib.redirect_stderr(_buf):
    park_holdings.statement_extra_sells("SpaceX", {}, PREV, D, s.exec)
check("≠ statement−journal" in _buf.getvalue(), "(2) park: cảnh báo crosscheck ra stderr")
os.remove(bfc.broker_csv_path(s.root, D))

print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} ca hỏng" + (f" — {FAILS}" if FAILS else ""))
sys.exit(1 if FAILS else 0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho `nav_sleeve.py` (SPEC §B5) — không broker, không BQ, không ghi `data/` (mọi
file ở thư mục tạm; ca 2 đọc fixture đóng băng `fixtures/nav_sleeve_zalopay_20261013/`). Không import
`Executor` ⇒ không cần MIKE_BOT_TEST_MODE. Chạy dưới `env -u TZ` và một TZ lạ (§16/§19).
"""
import datetime as dt
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nav_sleeve as S  # noqa: E402
from account_cash_flows import NavRow  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "nav_sleeve_zalopay_20261013", "zalopay_dgc_rows.json")
N_OK = 0


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def D(s):
    return dt.date.fromisoformat(s)


def scope(*tks, frm="2026-07-06"):
    return [{"ticker": t, "from": D(frm), "to": None} for t in tks]


def tr(**kw):
    """Bản ghi sleeve_transfers đã parse (giống load_transfers)."""
    base = {"decision": "confirmed", "confirmed_by": "selfcheck", "evidence": "selfcheck",
            "date": None, "ex_date": None, "time_ict": None, "fee_tax_vnd": 0.0}
    base.update(kw)
    for k in ("date", "ex_date"):
        if isinstance(base[k], str):
            base[k] = D(base[k])
    return base


# ───────────────────────────────────────── bộ dữ liệu tổng hợp nhỏ

INC = {"account_no": "A1", "inception_date": "2026-07-06", "starting_capital": 1_000_000.0}
SEED = {"legacy_positions": {"DGC": {"qty": 10, "price": 40000}}}           # ngoài bot 400.000


def nav_rows(navs, dates=("2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10")):
    return [{"date": d, "nav": str(n), "balance_ts": f"{d}T19:00:00", "nav_is_estimate": "",
             "cash": "0", "egg_assets": "", "offbook_assets": "", "margin_debt": "0"}
            for d, n in zip(dates, navs)]


def pos_const(q):
    return lambda d, ts: (dict(q), ts, 0, False)


def px_const(p):
    return lambda d, tk: (p, "test")


def t_no_outside():
    """Ca 1: không mã ngoài bot ⇒ (b) ≡ (a) từng dòng."""
    rows = nav_rows([1_010_000, 990_000, 1_000_000, 1_020_000])
    inc = dict(INC)
    b = S.build_sleeve_rows("A1", rows, inc, scope("ZZZ"), [], pos_const({"AAA": 5}), px_const(1.0),
                            seed={"legacy_positions": {"ZZZ": {"qty": 0, "price": 1}}})
    ok(all(t["nav_b"] == t["nav_a"] and t["outside_mv"] == 0 for t in b["table"]), "ca1 nav_b ≡ nav_a")
    led_b, _ = S.build_sleeve_ledger(b["table"], inc, b["base_b"], [])
    from nav_unit_ledger import build_ledger
    led_a, _ = build_ledger([NavRow(D(r["date"]), float(r["nav"]), balance_ts=r["balance_ts"]) for r in rows],
                            [], D(inc["inception_date"]), inc["starting_capital"])
    ok([x["unit_price"] for x in led_a] == [x["unit_price"] for x in led_b], "ca1 giá đơn vị (b) ≡ (a)")


def t_prototype_fixture():
    """Ca 2: DGC đứng yên ⇒ đúng nguyên mẫu zalopay_bot_series.py (fixture đóng băng từ dữ liệu thật)."""
    with open(FIX, encoding="utf-8") as f:
        fx = json.load(f)
    rows = [{"date": r["date"], "nav": r["nav"], "balance_ts": r["balance_ts"],
             "nav_is_estimate": r["nav_is_estimate"]} for r in fx["rows"]]
    q = {r["date"]: r["dgc_qty"] for r in fx["rows"]}
    p = {r["date"]: r["dgc_price"] for r in fx["rows"]}
    trs = [tr(proposal_id="dividend:DGC:2026-09-14", source="dividend", ticker="DGC", ex_date="2026-09-14",
              gross_vnd=80_000_000.0, fee_tax_vnd=4_000_000.0, amount_vnd=76_000_000.0, date="2026-09-25",
              time_ict="10:00")]
    b = S.build_sleeve_rows("ZaloPay", rows, fx["inception"], scope("DGC"), trs,
                            lambda d, ts: ({"DGC": q[str(d)]}, ts, 0, False),
                            lambda d, tk: (p[str(d)], "fixture"),
                            seed={"legacy_positions": fx["seed_legacy_positions"]})
    ok(b["base_b"] == 525_365_567.0, f"ca2 mốc (b) {b['base_b']}")
    flows = S.transfer_flows(trs)
    ok([f["amount_vnd"] for f in flows] == [76_000_000.0], f"ca2 dòng vào (b) {flows}")
    led, info = S.build_sleeve_ledger(b["table"], fx["inception"], b["base_b"], flows)
    r = led[-1]["unit_price"] / led[0]["unit_price"] - 1
    ok(round(100 * r, 3) == -0.790, f"ca2 từ đầu (b) {100 * r:.4f}% ≠ −0,790%")
    ok(not info["pending"] and not info["dropped"], "ca2 không dòng tiền treo/loại")
    rec = S.reconcile(b, flows, fx["inception"])
    ok(rec["identity_max_abs_vnd"] == 0.0, "ca2 a = b + ngoài")
    ok(rec["pnl_vnd"] == {"a": -61_234_124.0, "b": -3_734_124.0, "outside": -57_500_000.0, "residual": 0.0},
       f"ca2 lãi/lỗ cộng được {rec['pnl_vnd']}")
    t = {x["date"]: x for x in b["table"]}
    ok(t["2026-09-11"]["outside_recv"] == 0 and t["2026-09-14"]["outside_recv"] == 80_000_000.0
       and t["2026-09-24"]["outside_recv"] == 80_000_000.0 and t["2026-09-25"]["outside_recv"] == 0,
       "ca2 recv: 0 trước GDKHQ, 80tr từ 14/09 tới trước 25/09, 0 ngày về")


def t_dividend_rows():
    """Ca 3: trước GDKHQ / giữa / ngày về — recv + dòng tiền từng dòng; lãi/lỗ ngoài ngày về = −thuế."""
    dates = ("2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10")
    # 10 cp × 1.000 đ/cp cổ tức, ex 07-08, về 07-10 (09:00) — giá 40.000 không đổi; NAV_a: tiền phải thu
    # nằm trong cash từ 07-08 (10.000), ngày về cash thật +10.000 − thuế 500, recv thôi tính.
    navs = [1_000_000, 1_010_000, 1_010_000, 1_009_500]
    rows = nav_rows(navs, dates)
    trs = [tr(proposal_id="dividend:DGC:2026-07-08", source="dividend", ticker="DGC", ex_date="2026-07-08",
              gross_vnd=10_000.0, fee_tax_vnd=500.0, amount_vnd=9_500.0, date="2026-07-10", time_ict="09:00")]
    b = S.build_sleeve_rows("A1", rows, INC, scope("DGC"), trs, pos_const({"DGC": 10}), px_const(40000.0),
                            seed=SEED)
    t = {x["date"]: x for x in b["table"]}
    ok([t[d]["outside_recv"] for d in dates] == [0, 10_000.0, 10_000.0, 0], "ca3 recv theo dòng")
    out = [t[d]["outside_mv"] + t[d]["outside_recv"] for d in dates]
    ok(out[3] - out[2] + 9_500 == -500, f"ca3 lãi/lỗ ngoài ngày về = −thuế: {out[3] - out[2] + 9_500}")
    flows = S.transfer_flows(trs)
    led, _ = S.build_sleeve_ledger(b["table"], INC, b["base_b"], flows)
    ok(led[-1]["flow_bod_vnd"] == 9_500.0, f"ca3 dòng vào (b) ngày về là bod 9.500: {led[-1]}")
    ok(abs(led[-1]["unit_price"] - led[-2]["unit_price"]) < 1e-9, "ca3 giá đơn vị (b) không nhảy ngày về")


def t_sale():
    """Ca 4: bán một phần DGC — đề xuất đúng số; chưa xác nhận ⇒ S1; xác nhận ⇒ (b) không nhảy."""
    dates = ("2026-07-07", "2026-07-08", "2026-07-09")
    qrows = [(D("2026-07-06"), {"DGC": 10}), (D(dates[0]), {"DGC": 10}), (D(dates[1]), {"DGC": 4}),
             (D(dates[2]), {"DGC": 4})]
    fills = {"2026-07-08": [{"symbol": "DGC", "side": "NS", "fillQuantity": 6, "averagePrice": 41000},
                            {"symbol": "VPB", "side": "NB", "fillQuantity": 100, "averagePrice": 20000}]}
    props = S.detect_transfers(qrows, scope("DGC"), [], [], fills)
    ok(len(props) == 1 and props[0]["source"] == "sale" and props[0]["qty"] == -6, f"ca4 đề xuất {props}")
    gross = 6 * 41000
    fee = gross * (0.097 / 100 + 0.001)
    ok(props[0]["gross_vnd"] == gross and abs(props[0]["fee_tax_vnd"] - fee) < 1e-9
       and abs(props[0]["amount_vnd"] - (gross - fee)) < 1e-9, f"ca4 số tiền {props[0]}")
    # NAV_a: giá 40.000 cố định, bán 6 cp giá 41.000 ⇒ NAV_a +6.000 − phí/thuế ngày 07-08
    navs = [1_000_000, 1_000_000 + 6 * 1000 - fee, 1_000_000 + 6 * 1000 - fee]
    rows = nav_rows(navs, dates)

    def pos(d, ts):
        return ({"DGC": 10 if str(d) <= "2026-07-07" else 4}, ts, 0, False)
    b = S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [], pos, px_const(40000.0), proposals=props, seed=SEED)
    blocked = [x["date"] for x in b["table"] if x["blocked_reason"]]
    ok(blocked == ["2026-07-08", "2026-07-09"] and "S1" in b["table"][1]["blocked_reason"],
       f"ca4 chưa xác nhận ⇒ S1 từ ngày khớp: {blocked}")
    led, _ = S.build_sleeve_ledger(b["table"], INC, b["base_b"], [])
    ok([x["date"].isoformat() for x in led] == ["2026-07-06", "2026-07-07"], "ca4 ledger (b) dừng trước S1")
    conf = tr(proposal_id=props[0]["proposal_id"], source="sale", ticker="DGC", qty=-6, date="2026-07-08",
              time_ict="15:00", gross_vnd=gross, fee_tax_vnd=fee, amount_vnd=gross - fee)
    b2 = S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [conf], pos, px_const(40000.0), proposals=props,
                             seed=SEED)
    ok(not any(x["blocked_reason"] for x in b2["table"]), "ca4 xác nhận ⇒ hết chặn")
    led2, _ = S.build_sleeve_ledger(b2["table"], INC, b2["base_b"], S.transfer_flows([conf]))
    ok(abs(led2[2]["unit_price"] / led2[1]["unit_price"] - 1) < 1e-12,
       f"ca4 giá đơn vị (b) không nhảy ngày bán: {led2[1]['unit_price']} → {led2[2]['unit_price']}")
    # bản ghi xác nhận sai KL ⇒ S2
    bad = dict(conf, qty=-5)
    b3 = S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [bad], pos, px_const(40000.0), proposals=props,
                             seed=SEED)
    ok("S2" in b3["table"][1]["blocked_reason"] and "-6" in b3["table"][1]["blocked_reason"],
       f"ca4 KL xác nhận không khớp ⇒ S2: {b3['table'][1]['blocked_reason']}")


def t_needs_human():
    """Ca 5: KL đổi không có lệnh khớp ⇒ needs_human, không mang số tiền."""
    qrows = [(D("2026-07-06"), {"DGC": 10}), (D("2026-07-07"), {"DGC": 12})]
    props = S.detect_transfers(qrows, scope("DGC"), [], [], {})
    ok(len(props) == 1 and props[0]["source"] == "needs_human" and "amount_vnd" not in props[0]
       and props[0]["qty"] == 2, f"ca5 {props}")


def _raw(tmp, day, recs):
    p = os.path.join(tmp, f"dnse_raw_{day}.jsonl")
    with open(p, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def pos_rec(acct, ts, lots):
    return {"ts": ts, "kind": "positions", "account_no": acct,
            "payload": {"positions": [{"symbol": s, "openQuantity": q, "loanPackageId": i}
                                      for i, (s, q) in enumerate(lots)]}}


def t_positions(tmp):
    """Ca 6 + 7: hai lô cùng mã ⇒ cộng; lệch > 10 phút ⇒ cờ; hai tài khoản cùng file ⇒ kết quả khác."""
    _raw(tmp, "2026-07-07", [
        pos_rec("B2", "2026-07-07T19:00:00", [("DGC", 99)]),
        pos_rec("A1", "2026-07-07T18:00:00", [("DGC", 1)]),
        pos_rec("A1", "2026-07-07T19:00:30", [("DGC", 10), ("MBB", 100), ("MBB", 50)]),
        pos_rec("B2", "2026-07-07T23:00:00", [("DGC", 7)])])
    qa, ts, gap, stale = S.positions_at("A1", "2026-07-07", "2026-07-07T19:00:00", tmp)
    ok(qa == {"DGC": 10, "MBB": 150} and gap == 30 and not stale, f"ca6 cộng lô: {qa} gap {gap}")
    qa2, _, gap2, stale2 = S.positions_at("A1", "2026-07-07", "2026-07-07T19:11:00", tmp)
    ok(stale2 and gap2 == 630, f"ca6 lệch 10'30\" ⇒ cờ stale: {gap2}")
    qb, _, _, _ = S.positions_at("B2", "2026-07-07", "2026-07-07T19:00:00", tmp)
    ok(qb == {"DGC": 99} and qb != qa, f"ca7 §12 hai tài khoản khác nhau: A1 {qa} B2 {qb}")
    # dò cổ tức bỏ qua bản ghi số dư hỏng (ca thật 24/09: toàn 0 rồi hồi lại)
    recv = [("2026-07-08T04:00:00", 10_000.0), ("2026-07-08T19:07:17", 0.0), ("2026-07-08T19:17:59", 10_000.0),
            ("2026-07-09T04:51:38", 10_000.0), ("2026-07-09T19:07:08", 0.0), ("2026-07-10T04:00:00", 0.0)]
    props = S.detect_transfers([(D("2026-07-06"), {"DGC": 10}), (D("2026-07-07"), {"DGC": 10}),
                                (D("2026-07-09"), {"DGC": 10})], scope("DGC"),
                               [{"ticker": "DGC", "ex_date": "2026-07-07", "per_share": 1000.0}], recv, {})
    ok(props[0]["date"] == "2026-07-09" and props[0]["settle_window"] == ["2026-07-09T04:51:38", "2026-07-09T19:07:08"]
       and props[0]["amount_vnd"] == 9_500.0, f"ca6 dò ngày tiền về bỏ bản ghi hỏng: {props[0]}")


def t_raw_div_recv_two_accounts(tmp):
    """§12 (mutant N9 vòng 1): `raw_div_recv_and_fills` đọc file dnse_raw DÙNG CHUNG ⇒ lọc account ở
    dòng đầu; hai tài khoản cùng file phải ra kết quả KHÁC nhau, không lẫn bản ghi của nhau."""
    d = os.path.join(tmp, "raw2acct")
    os.makedirs(d, exist_ok=True)
    bal = lambda acct, ts, v: {"ts": ts, "kind": "balances", "account_no": acct,           # noqa: E731
                               "payload": {"stock": {"cashDividendReceiving": v}}}
    odr = lambda acct, ts, sym, q: {"ts": ts, "kind": "orders", "account_no": acct,        # noqa: E731
                                    "payload": {"orders": [{"symbol": sym, "fillQuantity": q}]}}
    _raw(d, "2026-07-08", [bal("A1", "2026-07-08T19:00:00", 10_000.0), bal("B2", "2026-07-08T19:00:05", 777.0),
                           odr("A1", "2026-07-08T15:00:00", "DGC", 100), odr("B2", "2026-07-08T15:00:09", "MBB", 5)])
    ra, fa = S.raw_div_recv_and_fills("A1", d)
    rb, fb = S.raw_div_recv_and_fills("B2", d)
    ok(ra == [("2026-07-08T19:00:00", 10_000.0)] and rb == [("2026-07-08T19:00:05", 777.0)],
       f"§12 cổ tức chờ về lẫn tài khoản: A1 {ra} B2 {rb}")
    ok([o["symbol"] for o in fa["2026-07-08"]] == ["DGC"] and [o["symbol"] for o in fb["2026-07-08"]] == ["MBB"],
       f"§12 lệnh khớp lẫn tài khoản: A1 {fa} B2 {fb}")


def t_gates(tmp):
    """S3, S6, S7, freshness của consumer + chống đọc excluded_tickers."""
    rows = nav_rows([1_000_000, 1_000_000])
    try:
        S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [], pos_const({"DGC": 10}), lambda d, tk: None, seed=SEED)
        ok(False, "S3 phải từ chối")
    except S.SleeveError as exc:
        ok("S3" in str(exc) and "DGC" in str(exc), f"S3 thông điệp {exc}")
    try:
        S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [], pos_const({"DGC": 10}), px_const(40000.0),
                            seed={"legacy_positions": {"DGC": {"qty": 10, "price": 96000}}})
        ok(False, "S7 phải từ chối mốc (b) < 5%")
    except S.SleeveError as exc:
        ok("S7" in str(exc) and "40,000" in str(exc), f"S7 thông điệp {exc}")
    b = S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [], pos_const({"DGC": 10}), px_const(40000.0),
                            seed={"legacy_positions": {"DGC": {"qty": 10, "price": 94000}}})
    ok(b["base_b"] == 60_000.0, "S7 sát ngưỡng (6%) không từ chối")
    # S6 + consumer
    ex = os.path.join(tmp, "ex")
    os.makedirs(ex, exist_ok=True)
    sp = os.path.join(tmp, "scope.json")
    with open(sp, "w") as f:
        json.dump({"A1": [{"ticker": "DGC", "from": "2026-07-06", "to": None}]}, f)
    seedp = os.path.join(tmp, "seed.json")
    with open(seedp, "w") as f:
        json.dump({"A1": SEED}, f)
    sc = S.load_scope("A1", sp)
    b = S.build_sleeve_rows("A1", rows, INC, sc, [], pos_const({"DGC": 10}), px_const(40000.0), seed=SEED)
    hp = S.history_path("A1", ex)
    S.write_history(hp, b["table"], sc)
    nr = [NavRow(D(r["date"]), float(r["nav"]), balance_ts=r["balance_ts"]) for r in rows]
    got = S.sleeve_inputs_for_report("A1", "2026-07-08", nr, INC, [], exec_dir=ex, scope_path=sp,
                                     transfers_path=os.path.join(tmp, "none.json"), seed_path=seedp)
    ok(got["nav0"] == 600_000.0 and [r[1] for r in got["rows"]] == [600_000.0, 600_000.0], f"consumer {got}")
    nr_more = nr + [NavRow(D("2026-07-09"), 1_000_000.0)]
    for bad_rows, why in ((nr_more, "thiếu dòng"), ([NavRow(nr[0][0], 1_000_001.0)] + nr[1:], "nav_history nav")):
        try:
            S.sleeve_inputs_for_report("A1", "2026-07-09", bad_rows, INC, [], exec_dir=ex, scope_path=sp,
                                       transfers_path=os.path.join(tmp, "none.json"), seed_path=seedp)
            ok(False, f"consumer phải từ chối: {why}")
        except S.SleeveUnavailable as exc:
            ok(why in str(exc), f"consumer {why}: {exc}")
    # dòng bị chặn (S1: KL đổi chưa ai xác nhận) ⇒ consumer từ chối, nêu lý do
    props = [{"proposal_id": "needs_human:DGC:2026-07-08", "source": "needs_human", "ticker": "DGC",
              "qty": -1, "date": "2026-07-08", "note": "selfcheck"}]
    bb = S.build_sleeve_rows("A1", rows, INC, sc, [], pos_const({"DGC": 10}), px_const(40000.0),
                             proposals=props, seed=SEED)
    hp_b = S.history_path("A1", os.path.join(tmp, "exb"))
    os.makedirs(os.path.dirname(hp_b), exist_ok=True)
    S.write_history(hp_b, bb["table"], sc)
    try:
        S.sleeve_inputs_for_report("A1", "2026-07-08", nr, INC, [], exec_dir=os.path.dirname(hp_b),
                                   scope_path=sp, transfers_path=os.path.join(tmp, "none.json"), seed_path=seedp)
        ok(False, "consumer phải từ chối dòng bị chặn")
    except S.SleeveUnavailable as exc:
        ok("S1" in str(exc) and "2026-07-08" in str(exc), f"consumer dòng bị chặn: {exc}")
    got7 = S.sleeve_inputs_for_report("A1", "2026-07-07", nr, INC, [], exec_dir=os.path.dirname(hp_b),
                                      scope_path=sp, transfers_path=os.path.join(tmp, "none.json"),
                                      seed_path=seedp)
    ok(len(got7["rows"]) == 1, "consumer: kỳ kết thúc TRƯỚC dòng bị chặn vẫn có số")
    with open(sp, "w") as f:
        json.dump({"A1": [{"ticker": "DGC", "from": "2026-07-01", "to": None}]}, f)
    sc2 = S.load_scope("A1", sp)
    try:
        S.sleeve_inputs_for_report("A1", "2026-07-08", nr, INC, [], exec_dir=ex, scope_path=sp,
                                   transfers_path=os.path.join(tmp, "none.json"), seed_path=seedp)
        ok(False, "S6 consumer phải từ chối")
    except S.SleeveUnavailable as exc:
        ok("S6" in str(exc), f"S6 consumer: {exc}")
    before = open(hp, "rb").read()
    try:
        S.write_history(hp, b["table"], sc2)
        ok(False, "S6 ghi phải từ chối")
    except S.SleeveError as exc:
        ok("S6" in str(exc) and open(hp, "rb").read() == before, f"S6 ghi: {exc}")
    # phạm vi chỉ từ sleeve_scope: mã của bot (PNJ, cấm MUA ở excluded_tickers) không bị tách khỏi (b)
    b = S.build_sleeve_rows("A1", rows, INC, scope("DGC"), [], pos_const({"DGC": 10, "PNJ": 5}),
                            px_const(40000.0), seed=SEED)
    ok(all(json.loads(x["outside_qty_json"]) == {"DGC": 10} for x in b["table"]), "PNJ nằm trong (b)")
    src = open(os.path.join(HERE, "nav_sleeve.py"), encoding="utf-8").read()
    code = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    ok("excluded_tickers\"" not in code and "['excluded_tickers']" not in code and
       ".get(\"excluded_tickers\"" not in code, "nav_sleeve không đọc excluded_tickers")


def main() -> int:
    t_no_outside()
    t_prototype_fixture()
    t_dividend_rows()
    t_sale()
    t_needs_human()
    with tempfile.TemporaryDirectory(prefix="nsl_sc_") as tmp:
        t_positions(tmp)
        t_raw_div_recv_two_accounts(tmp)
        t_gates(tmp)
    print(f"OK — {N_OK} assertion PASS (nav_sleeve_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""REPLAY old-vs-new cho bản vá lô lẻ thoát hết (job Taylor_20261002_082525).

Cùng MỘT bộ đầu vào (holdings park_holdings(asof) đọc dnse_raw lịch sử/DNSE, ADV, day-cap, rổ,
share, plan) chạy qua code BASE (mike master, đường dẫn --base-bin) và code MỚI (worktree này):
L1 compute_trim → L2 compute_jit_unpark(l1_result) → merge_park_orders(plan, L1, L2).
In từng lệnh KHÁC nhau (trước/sau) và đếm lệnh byte-identical. Chỉ đọc, không ghi plan/data.

Vòng 3 (job Taylor_20261002_094032) — thêm 2 biến thể ĐƯỜNG LIVE của nguồn broker, cùng bản ghi
`positions` MỚI NHẤT của dnse_raw_{asof}.jsonl, đưa qua nhánh LIVE THẬT của
`read_broker_snapshot` (DNSEBroker.get_positions thật, client giả trả payload thô, không mạng):
  · live_unfixed = park_holdings BASE (sellable lấy từ get_positions ⇒ tradeQuantity=0 → total)
  · live_fixed   = park_holdings MỚI (sellable = Σ tradeQuantity thô, cùng bộ chuẩn hoá jsonl)
rồi chạy pipeline MỚI trên từng biến thể (merge 20:20 trước, auto_exit_inject+cap 20:40 sau).
`--forward-1002`: thêm ca asof=2026-10-02 (bản ghi EOD hôm nay — đúng đầu vào park_trim 19:30 tối
nay), lệnh MUA lấy tạm từ plan 10-02, target từ artifact 10-02; giá = marketPrice của bản ghi
(BQ chưa sync 10-02 — chỉ ảnh hưởng cỡ lô theo giá trị, không ảnh hưởng điều kiện thoát hết).

    $DNA_PYEXE agents/Taylor/oddlot_replay_20261002.py --base-bin /home/trido/thanhdt/WorkingClaude/mike/bin
"""
import argparse
import copy
import functools
import importlib.util
import json
import os
import sys

NEW_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bin"))
sys.path.insert(0, NEW_BIN)
import wc_paths  # noqa: E402
WC = wc_paths.find_wc_root(NEW_BIN + "/x")
sys.path.insert(0, WC)

import compute_park_trim as cpt_new             # noqa: E402  (tên chuẩn = bản MỚI)
import compute_jit_unpark as cju_new            # noqa: E402
import merge_park_orders as mpo_new             # noqa: E402
import auto_exit_inject as aei                  # noqa: E402
import park_holdings as ph_new                  # noqa: E402
from park_holdings import park_holdings         # noqa: E402
import trading_bot.brokers as tbb               # noqa: E402
from trading_bot.plan import _adv_for_gate      # noqa: E402

# artifact (plan_date) → asof đã dùng lúc sinh artifact (đọc từ chính artifact)
DATES = ["2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"]
ACCTS = ["SpaceX", "ZaloPay"]
PLAN_DIR = os.path.join(WC, "data", "trade_plans")


def load_as(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dumps(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, default=str)


def by_tk(orders):
    out = {}
    for o in orders or []:
        out.setdefault(o.get("ticker"), []).append(o)
    return out


def diff_orders(tag, old, new, rows):
    same = changed = 0
    ot, nt = by_tk(old), by_tk(new)
    for tk in sorted(set(ot) | set(nt)):
        a, b = ot.get(tk, []), nt.get(tk, [])
        if dumps(a) == dumps(b):
            same += len(a)
            continue
        changed += 1
        rows.append({"layer": tag, "ticker": tk,
                     "old": [(o.get("side"), o.get("qty")) for o in a],
                     "new": [(o.get("side"), o.get("qty"), o.get("full_exit"), o.get("odd_lot_qty"))
                             for o in b],
                     "old_keys_minus_new": sorted({k for o in a for k in o} - {k for o in b for k in o}),
                     "new_keys_minus_old": sorted({k for o in b for k in o} - {k for o in a for k in o}),
                     "other_fields_identical": _same_except_odd(a, b)})
    return same, changed


ODD_KEYS = {"qty", "value_vnd", "fifo_lots", "reason", "full_exit", "odd_lot_qty", "qty_lot_part",
            "note", "estimated_proceeds_vnd", "fee_est_vnd", "merged_from"}


def _same_except_odd(a, b):
    if len(a) != len(b):
        return False
    return all(dumps({k: v for k, v in x.items() if k not in ODD_KEYS})
               == dumps({k: v for k, v in y.items() if k not in ODD_KEYS}) for x, y in zip(a, b))


def strip_injected(plan):
    """Đưa plan về trạng thái TRƯỚC khi cron inject chạy: merge 20:20 → auto_exit_inject 20:40.
    Trả (plan_trước_inject, [lệnh AUTOEXIT đã inject — qty = số ĐÃ bị cap bởi production cũ])."""
    pl = copy.deepcopy(plan)
    inj = [o for o in pl.get("orders", []) if "-AUTOEXIT-" in str(o.get("id"))]
    pl["orders"] = [o for o in pl["orders"] if "-AUTOEXIT-" not in str(o.get("id"))]
    return pl, inj


def cron_order_outcome(merged_plan, inj, positions):
    """Áp inject SAU merge đúng thứ tự cron: từng lệnh AUTOEXIT qua `_cap_sellable` trên plan đã
    merge (Σ SELL mã đó đã có). Trả {ticker: (qty_AUTOEXIT_cuối, cảnh_báo)} + Σ PARK merge theo mã."""
    pl = copy.deepcopy(merged_plan)
    out = {}
    for o in inj:
        tk = o["ticker"]
        q, warn = aei._cap_sellable(pl, tk, int(o["qty"]), positions, o.get("book", "LAG"))
        out[tk] = (q, warn)
        if q > 0:
            pl["orders"].append({"ticker": tk, "side": "sell", "qty": q})
    park = {}
    for o in merged_plan.get("orders", []):
        if o.get("merge_owner") == mpo_new.OWNER and o.get("side") == "sell":
            park[o["ticker"]] = o["qty"]
    return out, park


EXEC_DIR = os.path.join(WC, "data", "execution_logs")
ACCT_NO = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}


def last_positions_record(acct, asof):
    best = None
    for line in open(os.path.join(EXEC_DIR, f"dnse_raw_{asof}.jsonl"), encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("kind") == "positions" and str(r.get("account_no")) == ACCT_NO[acct] \
                and (best is None or r.get("ts", "") >= best.get("ts", "")):
            best = r
    return best


class _FakeClient:
    def __init__(self, payload):
        self._p = payload

    def positions(self, _acc):
        return json.loads(json.dumps(self._p))

    def balances(self, _acc):
        return {}


def live_broker(module, acct, asof, rec, price_fn):
    """Nhánh LIVE THẬT của `module.read_broker_snapshot` trên payload thô `rec` (không mạng,
    không _log_raw). Tiền mặt LẤY TỪ nhánh jsonl (balances không phải đối tượng audit này)."""
    old_conn, old_today = tbb.DNSEBroker.connect, module.today_ict

    def _connect(self):
        self.client, self._raw_log = _FakeClient(rec["payload"]), None
        return self
    tbb.DNSEBroker.connect, module.today_ict = _connect, (lambda: asof)
    try:
        pos, _c, _m = module.read_broker_snapshot(acct, ACCT_NO[acct], asof, price_fn=price_fn)
    finally:
        tbb.DNSEBroker.connect, module.today_ict = old_conn, old_today
    module.today_ict = lambda: "2099-01-01"          # tiền mặt: nhánh jsonl
    try:
        _p, cash, meta = module.read_broker_snapshot(acct, ACCT_NO[acct], asof, price_fn=price_fn)
    finally:
        module.today_ict = old_today
    return pos, cash, meta


def run_new(acct, asof, target, h, buys, plan, kw, kw2, h_true):
    """`h_true` = holdings nguồn jsonl: auto_exit_inject production LUÔN đọc sellable từ jsonl
    (portfolio_status.broker_positions_with_cost, `or 0`) ⇒ cap 20:40 và kiểm 'vượt sellable THẬT'
    dùng nó cho MỌI biến thể, không dùng sellable của biến thể."""
    l1 = cpt_new.compute_trim(acct, asof, target, holdings=copy.deepcopy(h), **kw)
    l2 = cju_new.compute_jit_unpark(acct, asof, orders=copy.deepcopy(buys),
                                    holdings=copy.deepcopy(h), l1_result=l1, **kw2)
    plan_pre, inj = strip_injected(plan)
    m, rep = mpo_new.merge_park_orders(plan_pre, l1, l2, allow_approved=True, ex_map={})
    positions = {tk: {"sellable": v.get("sellable")}
                 for tk, v in (h_true.get("broker_positions") or {}).items()}
    cron, park = cron_order_outcome(m, inj, positions)
    fe = {o["ticker"]: o["qty"] for o in m.get("orders", [])
          if o.get("merge_owner") == mpo_new.OWNER and o.get("full_exit")}
    sell_over = {tk: (q, positions.get(tk, {}).get("sellable")) for tk, q in park.items()
                 if positions.get(tk, {}).get("sellable") is not None
                 and q > positions[tk]["sellable"]}
    return {"park": park, "full_exit": fe, "status": rep["status"], "cron": cron,
            "over_sellable": sell_over,
            "sellable": {tk: v.get("sellable") for tk, v in h["broker_positions"].items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-bin", required=True)
    ap.add_argument("--out", default="/tmp/oddlot_replay_20261002.json")
    ap.add_argument("--asof-override", action="append", default=[],
                    help="acct:plan_date:asof — vd SpaceX:2026-10-02:2026-10-01 (artifact asof=hôm "
                         "nay chạy 08:42 trước phiên ⇒ sổ = EOD hôm trước; asof hôm nay sẽ đọc DNSE "
                         "LIVE đã gồm lệnh khớp trong ngày)")
    ap.add_argument("--only", default=None, help="acct:plan_date — chỉ chạy 1 cặp")
    ap.add_argument("--forward-1002", action="store_true")
    a = ap.parse_args()
    ph_old = load_as("park_holdings_old", os.path.join(a.base_bin, "park_holdings.py"))
    assert not hasattr(ph_old, "aggregate_position_rows"), "base-bin park_holdings KHÔNG phải base"
    from verify_account_snapshot import bq_close_prices
    variants = []
    cpt_old = load_as("cpt_old", os.path.join(a.base_bin, "compute_park_trim.py"))
    cju_old = load_as("cju_old", os.path.join(a.base_bin, "compute_jit_unpark.py"))
    mpo_old = load_as("mpo_old", os.path.join(a.base_bin, "merge_park_orders.py"))
    assert not hasattr(cpt_old, "full_exit_qty"), "base-bin KHÔNG phải code base"

    rows, summary, cross = [], [], []
    jobs = [(acct, d, False) for acct in ACCTS for d in DATES]
    if a.forward_1002:
        jobs += [(acct, "2026-10-02", True) for acct in ACCTS]
    for acct, d, fwd in jobs:
        if True:
            art_p = os.path.join(PLAN_DIR, f"park_trim_{acct}_{d}.json")
            plan_p = os.path.join(PLAN_DIR, f"plan_{acct}_{d}.json")
            art = json.load(open(art_p, encoding="utf-8"))
            plan = json.load(open(plan_p, encoding="utf-8"))
            if a.only and a.only != f"{acct}:{d}":
                continue
            ovr = {x.rsplit(":", 1)[0]: x.rsplit(":", 1)[1] for x in a.asof_override}
            asof = "2026-10-02" if fwd else ovr.get(f"{acct}:{d}", art["asof"])
            rec = last_positions_record(acct, asof)
            if fwd:                                    # BQ chưa có 10-02 ⇒ marketPrice bản ghi
                _mp = {p["symbol"]: float(p.get("marketPrice") or 0)
                       for p in rec["payload"]["positions"] if p.get("marketPrice")}

                def pxf(tks, _d, _mp=_mp):
                    return {t: _mp.get(t) for t in tks}
            else:
                def pxf(tks, dd):
                    return bq_close_prices(tks, dd)[0]
            old_today = ph_new.today_ict
            ph_new.today_ict = lambda: "2099-01-01"    # nhánh jsonl kể cả khi asof = hôm nay
            try:
                h = park_holdings(acct, asof, price_fn=pxf)
                hv = {"live_unfixed": park_holdings(acct, asof, price_fn=pxf, broker=live_broker(
                          ph_old, acct, asof, rec, pxf)),
                      "live_fixed": park_holdings(acct, asof, price_fn=pxf, broker=live_broker(
                          ph_new, acct, asof, rec, pxf))}
            except SystemExit as e:
                ph_new.today_ict = old_today
                summary.append({"acct": acct, "plan_date": d, "asof": asof, "error": str(e)})
                continue
            ph_new.today_ict = old_today
            adv = functools.lru_cache(None)(lambda tk, s: _adv_for_gate(tk, s))
            basket, rebal, berr = cpt_new.park_target_basket(asof)
            day_cap, _n, cerr = cpt_new.etf_day_cap_live(asof, sorted(basket or {}))
            share = art.get("adv_share") or 0.5
            target = float(art["target_park"])
            kw = dict(share_override=share, adv_fn=adv, day_cap_override=day_cap,
                      basket_override=basket, price_fn=functools.lru_cache(None)(
                          cpt_new.live_price_fn(asof)))
            if fwd:
                kw["price_fn"] = lambda tk, _mp=_mp: (_mp.get(tk), None if _mp.get(tk) else "no px")
            l1o = cpt_old.compute_trim(acct, asof, target, holdings=copy.deepcopy(h), **kw)
            l1n = cpt_new.compute_trim(acct, asof, target, holdings=copy.deepcopy(h), **kw)
            s1 = diff_orders(f"L1 {acct} {d}", l1o.get("orders"), l1n.get("orders"), rows)
            buys = [o for o in plan.get("orders", []) if str(o.get("side")).lower() == "buy"]
            kw2 = dict(share_override=share, adv_fn=adv, day_cap_override=day_cap)
            try:
                l2o = cju_old.compute_jit_unpark(acct, asof, orders=copy.deepcopy(buys),
                                                 holdings=copy.deepcopy(h), l1_result=l1o, **kw2)
                l2n = cju_new.compute_jit_unpark(acct, asof, orders=copy.deepcopy(buys),
                                                 holdings=copy.deepcopy(h), l1_result=l1n, **kw2)
            except SystemExit as e:
                l2o = l2n = None
                summary.append({"acct": acct, "plan_date": d, "l2_error": str(e)})
            s2 = diff_orders(f"L2 {acct} {d}", (l2o or {}).get("orders"),
                             (l2n or {}).get("orders"), rows)
            # ĐÚNG THỨ TỰ CRON (arch-review B2): merge chạy trên plan CHƯA inject; inject sau đó.
            plan_pre, inj = strip_injected(plan)
            mo, ro = mpo_old.merge_park_orders(plan_pre, l1o, l2o, allow_approved=True, ex_map={})
            mn, rn = mpo_new.merge_park_orders(plan_pre, l1n, l2n, allow_approved=True, ex_map={})
            positions = {tk: {"sellable": v.get("sellable")}
                         for tk, v in (h.get("broker_positions") or {}).items()}
            co, park_o = cron_order_outcome(mo, inj, positions)
            cn, park_n = cron_order_outcome(mn, inj, positions)
            for tk in sorted(set(co) | set(park_o) | set(park_n)):
                cross.append({"acct": acct, "plan_date": d, "ticker": tk,
                              "PARK_merge_old_new": [park_o.get(tk), park_n.get(tk)],
                              "AUTOEXIT_after_cap_old_new": [co.get(tk, (None, None))[0],
                                                             cn.get(tk, (None, None))[0]],
                              "CAP_warn_old_new": [bool(co.get(tk, (0, None))[1]),
                                                   bool(cn.get(tk, (0, None))[1])]})
            s3 = diff_orders(f"MERGE {acct} {d}", mo.get("orders"), mn.get("orders"), rows)
            vr = {"base_raw": {"park": park_o, "cron": co}, "new_raw": run_new(
                acct, asof, target, h, buys, plan, kw, kw2, h)}
            for vn, hh in hv.items():
                vr[vn] = run_new(acct, asof, target, hh, buys, plan, kw, kw2, h)
            variants.append({"acct": acct, "plan_date": ("FWD " if fwd else "") + d, "asof": asof,
                             "rec_ts": rec.get("ts"), "res": vr})
            # mọi khoá cấp plan ngoài orders/merge_park_orders/proposal phải byte-identical
            skip = {"orders", "merge_park_orders", "park_trim_proposal", "jit_unpark_proposal"}
            plan_keys_same = dumps({k: v for k, v in mo.items() if k not in skip}) == \
                dumps({k: v for k, v in mn.items() if k not in skip})
            summary.append({"acct": acct, "plan_date": d, "asof": asof, "target": target,
                            "L1_decision": [l1o.get("decision"), l1n.get("decision")],
                            "L1_same_changed": s1, "L2_same_changed": s2,
                            "merge_status": [ro["status"], rn["status"]],
                            "MERGE_same_changed": s3, "plan_other_keys_identical": plan_keys_same,
                            "basket_err": berr, "daycap_err": cerr})
    res = {"summary": summary, "changed": rows, "cron_order": cross, "variants": variants}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    for s in summary:
        print(dumps(s))
    print("--- THỨ TỰ CRON (merge trước, inject+cap sau): chỉ mã PARK đổi hoặc có AUTOEXIT ---")
    for c in cross:
        if c["PARK_merge_old_new"][0] != c["PARK_merge_old_new"][1] or \
                c["AUTOEXIT_after_cap_old_new"][0] is not None:
            print(dumps(c))
    print("--- lệnh ĐỔI ---")
    for r in rows:
        print(dumps(r))
    print("--- BIẾN THỂ NGUỒN BROKER (pipeline MỚI; base_raw = code base, nguồn jsonl) ---")
    print("acct | plan | asof | rec_ts | mã | sellable(jsonl/live_unfixed/live_fixed) | PARK merge "
          "base_raw/new_raw/live_unfixed/live_fixed | full_exit? new_raw/live_unfixed/live_fixed")
    for v in variants:
        r = v["res"]
        tks = set()
        for k in ("new_raw", "live_unfixed", "live_fixed"):
            tks |= set(r[k]["park"]) | set(r[k]["full_exit"])
        tks |= set(r["base_raw"]["park"])
        for tk in sorted(tks):
            sl = [r[k]["sellable"].get(tk) for k in ("new_raw", "live_unfixed", "live_fixed")]
            pk = [r[k]["park"].get(tk) for k in ("base_raw", "new_raw", "live_unfixed", "live_fixed")]
            fe = [tk in r[k]["full_exit"] for k in ("new_raw", "live_unfixed", "live_fixed")]
            if len(set(map(str, pk))) > 1 or any(fe) or len(set(map(str, sl))) > 1:
                print(f"{v['acct']} | {v['plan_date']} | {v['asof']} | {v['rec_ts']} | {tk} | "
                      f"{sl} | {pk} | {fe}")
        for k in ("new_raw", "live_unfixed", "live_fixed"):
            if r[k]["over_sellable"]:
                print(f"  !! {v['acct']} {v['plan_date']} {k}: PARK merge > sellable THẬT (jsonl) "
                      f"{r[k]['over_sellable']} (status {r[k]['status']})")
        eq = all(r["live_fixed"][x] == r["new_raw"][x] for x in ("park", "full_exit", "sellable"))
        print(f"  == {v['acct']} {v['plan_date']}: live_fixed ≡ new_raw (park/full_exit/sellable): "
              f"{eq}; merge status new_raw/live_unfixed/live_fixed = "
              f"{[r[k]['status'] for k in ('new_raw', 'live_unfixed', 'live_fixed')]}")


if __name__ == "__main__":
    main()

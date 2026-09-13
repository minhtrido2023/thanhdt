"""aria-H nhóm B — replay OFFLINE check_plan_funding trên plan JSON thật, phí cũ 0,075% vs mới 0,097%.

KHÔNG gọi broker: sức mua (pp0Buy) lấy từ bằng chứng đã ghi —
  (a) dòng "FUNDING GATE" trong mike/logs/run_bot_<acct>_<date>.log = đúng con số gate đo lúc chạy thật;
  (b) plan chưa chạy (ZaloPay 2026-09-14): pp0Buy ppse MỚI NHẤT của account trong dnse_raw (proxy, ghi rõ).
Log đa nhóm gói vay đều cho CÙNG pp0Buy mọi nhóm (hũ chung) ⇒ stub trả một giá trị cho mọi gói, gộp một
nhóm là tương đương (raw_util = Σneed/bp, pot = bp).

Chạy:  PYTHONPATH=<gốc WorkingClaude chứa trading_bot cần thử> $DNA_PYEXE replay_funding_gate_fee.py
In bảng + ghi replay_funding_gate_fee.json cạnh file này. Read-only với data/.
"""
import json
import os
import re
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
import trading_bot.plan_funding_gate as g          # noqa: E402  (theo PYTHONPATH)
import trading_bot.plan as _plan_mod              # noqa: E402
_plan_mod.PLAN_DIR = f"{WC}/data/trade_plans"      # plan THẬT, kể cả khi trading_bot nạp từ worktree tạm
load_plan = _plan_mod.load_plan

CASES = {"SpaceX": ["2026-08-17", "2026-08-14", "2026-08-13", "2026-08-12", "2026-08-11", "2026-08-10"],
         "ZaloPay": ["2026-09-14", "2026-08-14", "2026-08-13", "2026-08-12", "2026-08-11", "2026-08-10"]}
ACCT_NO = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
OLD, NEW = 0.00075, 0.00097


class StubBroker:
    client = None

    def __init__(self, bp):
        self.bp = bp

    def get_buying_power(self, ticker, price, loan_package_id=None):
        return self.bp

    def get_cash(self):
        return self.bp


def bp_from_log(acct, date):
    # Lần gate chạy ĐẦU TIÊN trong ngày: log sáng → autoheal (theo giờ) → chiều.
    ymd = date.replace("-", "")
    cands = [f"{WC}/mike/logs/run_bot_{acct}_{date}.log"]
    cands += sorted(f"{WC}/mike/logs/{f}" for f in os.listdir(f"{WC}/mike/logs")
                    if f.startswith(f"run_bot_{acct}_autoheal_{ymd}_"))
    cands += [f"{WC}/mike/logs/run_bot_{acct}_{date}_afternoon.log"]
    for path in cands:
        if os.path.exists(path):
            hit = _bp_in(path)
            if hit[0] is not None:
                return hit
    return None, None, None


def _bp_in(path):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for i, ln in enumerate(lines):
        if "FUNDING GATE" in ln:
            txt = ln if "sức mua" in ln else (lines[i + 1] if i + 1 < len(lines) else "")
            m = re.search(r"sức mua (?:thật của broker )?([\d,]+)đ", txt)
            n = re.search(r"Σ lệnh MUA (?:còn lại )?([\d,]+)đ", txt)
            if m:
                return (float(m.group(1).replace(",", "")),
                        float(n.group(1).replace(",", "")) if n else None,
                        f"log:{os.path.basename(path)}")
    return None, None, None


def bp_from_ppse(acct):
    raw = sorted(f for f in os.listdir(f"{WC}/data/execution_logs") if f.startswith("dnse_raw_"))
    for f in reversed(raw):
        last = None
        for ln in open(f"{WC}/data/execution_logs/{f}", encoding="utf-8"):
            r = json.loads(ln)
            if r.get("kind") != "ppse" or str(r.get("account_no")) != ACCT_NO[acct]:
                continue
            last = r
        if last:
            return float(last["payload"]["resp"]["pp0Buy"]), f"ppse:{f}@{last['ts']}"
    return None, None


rows = []
for acct, dates in CASES.items():
    for d in dates:
        plan = load_plan(d, acct)
        bp, log_need, src = bp_from_log(acct, d)
        if bp is None:
            bp, src = bp_from_ppse(acct)
        row = {"account": acct, "plan_date": d, "bp_vnd": bp, "bp_source": src, "log_need_vnd": log_need,
               "n_buy": sum(1 for o in plan.orders if o.side == "buy"),
               "n_sell": sum(1 for o in plan.orders if o.side == "sell")}
        for tag, fee in (("old", OLD), ("new", NEW)):
            g.FEE_RATE = fee
            v = g.check_plan_funding(plan, StubBroker(bp), "live")
            row[f"{tag}_action"] = v["action"]
            row[f"{tag}_need_vnd"] = round(v["need_vnd"])
            row[f"{tag}_util"] = v["utilization"]
        row["flip"] = row["old_action"] != row["new_action"]
        rows.append(row)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_funding_gate_fee.json")
json.dump({"gate_module": g.__file__, "rows": rows}, open(out, "w"), ensure_ascii=False, indent=1)
print(f"gate module: {g.__file__}")
print(f"{'acct':8} {'plan':10} {'buy/sell':8} {'pp0Buy':>13} {'need@0,075':>13} {'need@0,097':>13} "
      f"{'U old':>7} {'U new':>7} old→new  nguồn pp0Buy")
for r in rows:
    print(f"{r['account']:8} {r['plan_date']:10} {r['n_buy']:>3}/{r['n_sell']:<4} {r['bp_vnd']:>13,.0f} "
          f"{r['old_need_vnd']:>13,} {r['new_need_vnd']:>13,} {r['old_util']*100:>6.1f}% {r['new_util']*100:>6.1f}% "
          f"{r['old_action']}→{r['new_action']}{' ⚠FLIP' if r['flip'] else ''}  {r['bp_source']}"
          + (f" (log need {r['log_need_vnd']:,.0f})" if r['log_need_vnd'] else ""))
print("FLIP:", sum(r["flip"] for r in rows), "/", len(rows))

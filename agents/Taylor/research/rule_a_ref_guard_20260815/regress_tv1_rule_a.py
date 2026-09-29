"""HỒI QUY luật A cho book DISCRETIONARY_SPECIAL (TV1) trên NGÀY THẬT.

Việc 2 của job Taylor_20260815_022340. Câu hỏi: đổi `sessions=5` (mean-5 = luật B) sang luật A
(anchor = giá đóng phiên đã hoàn tất gần nhất) thì trần TV1 mỗi phiên thật đổi bao nhiêu?

Không tự viết lại công thức: gọi THẲNG `resolve_price_band()` production cho CẢ HAI chân, chỉ
đổi đúng một khoá state (`ceiling_rule`). Chân đối chứng (mean-5) phải TÁI LẬP ĐÚNG con số
`hard_no_chase_ceiling_vnd` đã ghi trong plan THẬT — nếu không tái lập được thì harness sai,
mọi so sánh phía sau vô nghĩa (đúng tinh thần "self-check + control leg" của skill quant-research).

Giá anchor lấy từ DNSE `ohlc` 1D — CÙNG feed production dùng, không phải BigQuery (§6).
"""
import copy
import datetime as dt
import glob
import json
import sys
from zoneinfo import ZoneInfo

from trading_bot.brokers import DNSEBroker
from trading_bot.discretionary_accumulation import resolve_price_band

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
TICKER = "TV1"
OUT = "mike/agents/Taylor/research/rule_a_ref_guard_20260815/tv1_rule_a_regression.json"


def load_bars():
    """(date_iso → close_vnd) các phiên 1D đã đóng, từ feed DNSE."""
    b = DNSEBroker(quote_only=True).connect()
    to_ts = int(dt.datetime(2026, 8, 15, 20, 0, tzinfo=ICT).timestamp())
    raw = b.client.ohlc(TICKER, resolution="1D", **{"from": to_ts - 120 * 86400, "to": to_ts})
    ts, c = raw.get("t") or [], raw.get("c") or []
    bars = [(dt.datetime.fromtimestamp(int(t), ICT).date().isoformat(), float(v) * 1000.0)
            for t, v in zip(ts, c)]
    bars.sort(key=lambda x: x[0])
    return bars


def real_plan_ceilings():
    """(account, plan_date) → trần TV1 THẬT đã ghi trong plan production."""
    out = {}
    for p in sorted(glob.glob("data/trade_plans/plan_*_2026-*.json")):
        name = p.split("/")[-1][len("plan_"):-len(".json")]
        account, _, pdate = name.rpartition("_")
        try:
            d = json.load(open(p))
        except Exception:
            continue
        for o in d.get("orders", []):
            if o.get("book") == "DISCRETIONARY_SPECIAL" and o.get("ticker") == TICKER:
                out[(account, pdate)] = {
                    "ceiling": o.get("hard_no_chase_ceiling_vnd"),
                    "limit": o.get("limit_price_vnd"), "qty": o.get("qty"),
                    "ref_price": o.get("ref_price")}
    return out


def main():
    bars = load_bars()
    by_date = dict(bars)
    print(f"TV1: {len(bars)} phiên 1D từ feed DNSE "
          f"({bars[0][0]} → {bars[-1][0]})\n")

    states = {a: json.load(open(f"data/trade_plans/discretionary/state_{TICKER}_{a}.json"))
              for a in ("SpaceX", "ZaloPay")}
    real = real_plan_ceilings()
    rows, mismatch = [], 0

    for (account, pdate), got in sorted(real.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        st_old = copy.deepcopy(states[account])
        n = int(st_old["dynamic_ceiling"].get("sessions", 5))
        # Phiên ĐÃ ĐÓNG TRƯỚC ngày thực thi — đúng bất biến production (loại nến hôm nay).
        done = [(d, px) for d, px in bars if d < pdate]
        if len(done) < n:
            continue
        prices = [px for _, px in done[-n:]]
        dates = [d for d, _ in done[-n:]]
        latest = done[-1][1]

        c_old, r_old, i_old = resolve_price_band(st_old, prices, latest)

        st_new = copy.deepcopy(states[account])
        st_new["dynamic_ceiling"]["ceiling_rule"] = "A"
        c_new, r_new, i_new = resolve_price_band(
            st_new, prices, latest, anchor_dates=dates, plan_date=pdate)

        # ĐỦ ĐIỀU KIỆN ĐỐI CHỨNG chỉ khi production THẬT SỰ chạy engine trần động phiên đó.
        # P1 (trần động) landed 2026-08-12 18:38 ICT (commit ec0120c) ⇒ plan đầu tiên ăn luật
        # này là 2026-08-13. Mọi plan trước đó ghi ĐÚNG trần CỐ ĐỊNH 20.000 — so chân mean-5
        # vào đó là so với một luật chưa từng chạy, sẽ ra "lệch" giả và che mất đối chứng thật.
        fixed_c = float(st_old["price_band"]["no_chase_ceiling"])
        eligible = (got["ceiling"] is not None and float(got["ceiling"]) != fixed_c)
        ok = eligible and int(c_old) == int(got["ceiling"])
        if eligible and not ok:
            mismatch += 1
        rows.append({
            "account": account, "plan_date": pdate,
            "anchor_last_date": dates[-1], "anchor_last_close": latest,
            "mean_n_anchor": round(sum(prices) / len(prices), 2),
            "ceiling_old_mean5": int(c_old), "ceiling_new_rule_a": int(c_new),
            "delta_vnd": int(c_new) - int(c_old),
            "delta_pct": round((c_new / c_old - 1) * 100, 3) if c_old else None,
            "resting_old": int(r_old), "resting_new": int(r_new),
            "real_plan_ceiling": got["ceiling"], "control_eligible": eligible,
            "control_reproduced": ok,
            "mode_old": i_old.get("mode"), "mode_new": i_new.get("mode"),
            "rule_a_provenance": i_new.get("rule_a_provenance"),
        })

    hdr = (f"{'account':<8} {'plan_date':<11} {'anchor':<11} {'mean5':>9} {'cũ':>8} "
           f"{'MỚI(A)':>8} {'Δ':>7} {'Δ%':>7}  {'plan thật':>9} ctrl")
    print(hdr); print("-" * len(hdr))
    for r in rows:
        print(f"{r['account']:<8} {r['plan_date']:<11} {r['anchor_last_date']:<11} "
              f"{r['mean_n_anchor']:>9,.0f} {r['ceiling_old_mean5']:>8,} "
              f"{r['ceiling_new_rule_a']:>8,} {r['delta_vnd']:>+7,} "
              f"{r['delta_pct']:>+6.2f}%  {str(r['real_plan_ceiling']):>9} "
              f"{('✓' if r['control_reproduced'] else '✗ SAI') if r['control_eligible'] else '– (band cố định)'}")

    elig = [r for r in rows if r["control_eligible"]]
    deltas = [r["delta_vnd"] for r in rows]
    print(f"\nN = {len(rows)} (phiên-account thật) — trong đó {len(elig)} phiên production "
          f"THẬT SỰ chạy trần động (từ 2026-08-13, sau khi P1 ec0120c landed 08-12 18:38 ICT)")
    if deltas:
        print(f"  Δ trần (toàn bộ {len(rows)}): min {min(deltas):+,} / max {max(deltas):+,} / "
              f"mean {sum(deltas)/len(deltas):+,.0f} VND")
        print(f"  luật A CAO hơn: {sum(1 for d in deltas if d > 0)}  |  "
              f"THẤP hơn: {sum(1 for d in deltas if d < 0)}  |  "
              f"bằng: {sum(1 for d in deltas if d == 0)}")
    print(f"  ĐỐI CHỨNG (chỉ {len(elig)} phiên đủ điều kiện): tái lập ĐÚNG trần plan THẬT "
          f"{len(elig) - mismatch}/{len(elig)}" + ("" if not mismatch else f"  ✗ {mismatch} LỆCH"))
    print("  (các phiên ≤2026-08-12 production ghi trần CỐ ĐỊNH 20.000 — engine động chưa chạy;\n"
          "   dòng của chúng là PHẢN THỰC, không dùng để xác nhận harness)")

    json.dump({"bars": bars, "rows": rows}, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"\n→ {OUT}")
    return 1 if mismatch else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""universe_pit_ab_p2p3.py — A/B TĨNH cho P2 (custom30V) và P3 (banking sector-lens D1).

§4.3 của `ticker_prune_replacement_plan.md`: P1-P3 KHÔNG shadow, thay bằng **A/B tĩnh 1 lần**,
người đọc duyệt diff. Script này CHỈ XUẤT DIFF — nó **không sửa** `custom_basket.py` hay
`golive_recommend_v23.py`, không ghi bảng nào, không đổi hành vi production.

CÁCH LÀM (không đụng file production): `custom_basket.build_pit` nhận hàm `bq` làm tham số.
Ta bọc `bq` bằng một wrapper viết lại đúng mệnh đề universe trong SQL trước khi gửi đi. Đây là
cách duy nhất chạy được ĐÚNG code production với universe khác mà không sửa một dòng nào của nó.

3 NHÁNH (cố ý tách 2 hiệu ứng — nếu gộp thì không đọc được diff đến từ đâu):
  A  = production hôm nay: `ticker IN (SELECT DISTINCT ticker FROM ticker_prune)`
       (DISTINCT-ever ⇒ ĐANG có look-ahead, §2.2 của plan)
  B0 = `universe_pit` DISTINCT-ever  → cô lập hiệu ứng ĐỔI UNIVERSE (universe rộng hơn ~1,7x)
  B  = `universe_pit` per-day EXISTS → thay thế D1 đúng đặc tả §4.1 (đổi universe + BỎ look-ahead)

Chạy:  DNA_PYEXE universe_pit_ab_p2p3.py            (mặc định: 10 mốc lịch sử + rebal mới nhất)
Kết quả: in bảng diff + ghi CSV `universe_pit_ab_p2p3_<date>.csv` cạnh file này.
"""
import os
os.environ.pop("BQ_LOCAL_CACHE", None)          # universe_pit nằm ở tav2_mike, cache local không có
import sys
import datetime as dt

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import pandas as pd  # noqa: E402
from simulate_holistic_nav import bq as _bq_raw  # noqa: E402
import custom_basket as cb  # noqa: E402

PRUNE_PRED = "t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)"
UPIT = "lithe-record-440915-m9.tav2_mike.universe_pit"
PIT_EVER = (f"t.ticker IN (SELECT DISTINCT u2.ticker FROM `{UPIT}` u2 WHERE u2.in_universe)")
PIT_DAY = (f"EXISTS(SELECT 1 FROM `{UPIT}` u2 "
           f"WHERE u2.ticker=t.ticker AND u2.time=t.time AND u2.in_universe)")

ARMS = {"A_prune": None, "B0_pit_ever": PIT_EVER, "B_pit_perday": PIT_DAY}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   f"universe_pit_ab_p2p3_{dt.date.today()}.csv")


def bq_arm(repl):
    """Trả một hàm bq viết lại mệnh đề universe. repl=None ⇒ nhánh production nguyên bản."""
    if repl is None:
        return _bq_raw

    def _bq(sql, *a, **kw):
        if PRUNE_PRED in sql:
            sql = sql.replace(PRUNE_PRED, repl)
        return _bq_raw(sql, *a, **kw)
    return _bq


def p2_members():
    """P2 — rổ custom30V (yieldcombo) theo từng mốc rebalance, 3 nhánh."""
    os.environ["BASKET_SELECT"] = "yieldcombo"      # cấu hình PRODUCTION (custom30_history.py [6b])
    end = __import__("pt_dates").detect_end_date()
    out = {}
    for name, repl in ARMS.items():
        print(f"\n===== P2 arm {name} =====", flush=True)
        _, _, mem, _ = cb.build_pit(bq_arm(repl), "2014-01-02", end, quality="none",
                                    rebal="q2m5", gate_rating=3, weight_scheme="namecap")
        mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])
        out[name] = mem
    return out


def p3_banking(dates):
    """P3 — banking sector-lens D1 (ICB 8633), universe theo từng nhánh, tại từng mốc."""
    rows = []
    for d in dates:
        for name, repl in ARMS.items():
            pred = PRUNE_PRED.replace("t.", "t.") if repl is None else repl
            sql = f"""SELECT DISTINCT t.ticker FROM tav2_bq.ticker t
WHERE t.ICB_Code=8633 AND t.time = DATE '{d}' AND {pred}"""
            tks = sorted(_bq_raw(sql)["ticker"])
            rows.append({"date": str(d), "arm": name, "n": len(tks), "tickers": ",".join(tks)})
    return pd.DataFrame(rows)


def main():
    mem = p2_members()
    rebals = sorted(mem["A_prune"]["rebal_date"].unique())
    # 10 mốc lịch sử rải đều + mốc mới nhất
    idx = sorted(set([int(round(i * (len(rebals) - 1) / 9)) for i in range(10)] + [len(rebals) - 1]))
    picked = [pd.Timestamp(rebals[i]) for i in idx]

    rows = []
    print("\n================ P2 — DIFF RỔ custom30V (30 mã) ================")
    for d in picked:
        sets = {k: set(v[v["rebal_date"] == d]["ticker"]) for k, v in mem.items()}
        a = sets["A_prune"]
        for arm in ("B0_pit_ever", "B_pit_perday"):
            b = sets[arm]
            ins, outs = sorted(b - a), sorted(a - b)
            rows.append({"step": "P2", "date": str(d.date()), "arm": arm, "n_a": len(a), "n_b": len(b),
                         "n_changed": len(ins), "in": ",".join(ins), "out": ",".join(outs)})
            print(f"{d.date()}  {arm:14s}  đổi {len(ins):2d}/30   VÀO: {','.join(ins) or '-'}"
                  f"   RA: {','.join(outs) or '-'}")

    print("\n================ P3 — DIFF banking sector-lens (ICB 8633) ================")
    p3 = p3_banking([str(d.date()) for d in picked])
    for d, g in p3.groupby("date"):
        m = {r["arm"]: set(r["tickers"].split(",")) if r["tickers"] else set()
             for _, r in g.iterrows()}
        a = m["A_prune"]
        for arm in ("B0_pit_ever", "B_pit_perday"):
            ins, outs = sorted(m[arm] - a), sorted(a - m[arm])
            rows.append({"step": "P3", "date": d, "arm": arm, "n_a": len(a), "n_b": len(m[arm]),
                         "n_changed": len(ins) + len(outs), "in": ",".join(ins), "out": ",".join(outs)})
            print(f"{d}  {arm:14s}  A={len(a):2d} B={len(m[arm]):2d}   VÀO: {','.join(ins) or '-'}"
                  f"   RA: {','.join(outs) or '-'}")

    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()

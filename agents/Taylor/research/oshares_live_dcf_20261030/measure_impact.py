#!/usr/bin/env python3
"""Đo ảnh hưởng DCF_OSHARES_SOURCE fin -> live trên universe_pit tại các asof cho trước.

Chạy từ worktree OUTER (để `oshares_dcf` + `dcf_valuation` đã vá được import):
  cd /home/trido/wt-oshares-live-20261030/WorkingClaude && \
  python3 <this> 2026-10-29 2025-10-29
Giá = `Price` (chưa điều chỉnh) phiên asof từ data/bq_cache/ticker — đúng loại giá
`_dcf_check_for_order` nhận (giá khớp sống). Ghi out_impact_<asof>.csv + in tóm tắt.
"""
import os
import sys

import duckdb
import numpy as np
import pandas as pd

OUTER = os.getcwd()
sys.path.insert(0, OUTER)
import dcf_valuation as dv          # noqa: E402  (chdir sang WORKDIR canonical khi import)
import oshares_dcf as osd           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"
assert osd.__file__.startswith(OUTER), osd.__file__


def universe_prices(asof):
    c = duckdb.connect()
    y = asof[:4]
    u = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{C}/universe_pit/{y}.parquet')
                      WHERE in_universe AND time = (SELECT max(time) FROM read_parquet('{C}/universe_pit/{y}.parquet')
                                                    WHERE time <= DATE '{asof}')""").df().ticker
    p = c.execute(f"""SELECT ticker, Price FROM read_parquet('{C}/ticker/{y}.parquet')
                      WHERE time = (SELECT max(time) FROM read_parquet('{C}/ticker/{y}.parquet') WHERE time <= DATE '{asof}')""").df()
    return p[p.ticker.isin(set(u))].dropna().set_index("ticker").Price


def run(asof):
    px = universe_prices(asof)
    fin = dv._load_financials()
    osd.prime(list(px.index), asof)
    rows = []
    for tk, price in px.items():
        dv.OSHARES_SOURCE = "fin"
        a = dv.fair_value(tk, asof, price=float(price), fin=fin)
        dv.OSHARES_SOURCE = "live"
        b = dv.fair_value(tk, asof, price=float(price), fin=fin)
        r = {"ticker": tk, "price": price, "ok_fin": a["ok"], "ok_live": b["ok"],
             "reason": a.get("reason") or ""}
        if a["ok"] and b["ok"]:
            sa, ra = dv.classify_dcf(a.get("margin_of_safety"), a.get("sensitivity", {}), price)
            sb, rb = dv.classify_dcf(b.get("margin_of_safety"), b.get("sensitivity", {}), price)
            r.update(osh_fin=a["oshares"], osh_live=b["oshares"], fv_fin=a["fair_value_ps"],
                     fv_live=b["fair_value_ps"], fv_ratio=b["fair_value_ps"] / a["fair_value_ps"],
                     mos_fin=a.get("margin_of_safety"), mos_live=b.get("margin_of_safety"),
                     st_fin=sa, st_live=sb, rb_fin=ra, rb_live=rb,
                     src=b.get("oshares_source"), method=b.get("oshares_method"),
                     ann_added=";".join(b.get("oshares_announced_added") or []))
        rows.append(r)
    dv.OSHARES_SOURCE = "fin"
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(HERE, f"out_impact_{asof}.csv"), index=False)
    ok = d[d.ok_fin & d.ok_live]
    ch = ok[(ok.fv_ratio - 1).abs() > 1e-9]
    print(f"== asof {asof}: universe có giá {len(d)} | DCF ok {len(ok)} | ok_fin!=ok_live {int((d.ok_fin != d.ok_live).sum())}")
    print(f"   FV đổi: {len(ch)} mã; |ΔFV| >1%: {int(((ch.fv_ratio - 1).abs() > 0.01).sum())}, >5%: {int(((ch.fv_ratio - 1).abs() > 0.05).sum())}")
    if len(ch):
        print(f"   fv_ratio min {ch.fv_ratio.min():.4f} / median {ch.fv_ratio.median():.4f} / max {ch.fv_ratio.max():.4f}")
    print(f"   lật status {int((ok.st_fin != ok.st_live).sum())}; đổi robust {int((ok.rb_fin != ok.rb_live).sum())}")
    print(f"   nguồn live: {ok.src.value_counts().to_dict()}")
    show = ch.reindex(ch.fv_ratio.sub(1).abs().sort_values(ascending=False).index)
    cols = ["ticker", "osh_fin", "osh_live", "fv_ratio", "mos_fin", "mos_live", "st_fin", "st_live",
            "rb_fin", "rb_live", "method", "ann_added"]
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(show[cols].head(40).round(4).to_string(index=False))
    return d


def tcb_probe(asof="2026-10-30"):
    """TCB = BANK ⇒ fair_value loại trước khi đọc OShares; đo riêng hệ số số CP (= hệ số FV/cp nếu
    DCF tính được, vì FV/cp tỉ lệ nghịch số CP) và xác nhận fair_value vẫn NOT_COMPUTED ở cả 2 nguồn."""
    fin = dv._load_financials()
    f = float(fin[(fin.ticker == "TCB") & (fin.time <= pd.to_datetime(asof))].OShares.iloc[-1])
    r = osd.oshares_for("TCB", asof, f)
    print(f"== TCB {asof}: OShares quý {f:,.0f} -> live {r['value']:,.0f} ({r['method']}, ISS announced "
          f"đã thêm {r['announced_added']}); hệ số FV/cp nếu tính được = {f / r['value']:.4f}")
    for s in ("fin", "live"):
        dv.OSHARES_SOURCE = s
        print(f"   fair_value[{s}] ok={dv.fair_value('TCB', asof, price=1.0, fin=fin)['ok']} "
              f"reason={dv.fair_value('TCB', asof, price=1.0, fin=fin)['reason'][:40]}")
    dv.OSHARES_SOURCE = "fin"


if __name__ == "__main__":
    tcb_probe()
    for a in sys.argv[1:] or ["2026-10-29"]:
        run(a)

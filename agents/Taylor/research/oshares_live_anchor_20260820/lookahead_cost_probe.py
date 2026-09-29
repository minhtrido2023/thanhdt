#!/usr/bin/env python3
"""Cái giá look-ahead của nhánh LIVE (`oshares_at(..., live=True)`), đo trên cùng một rổ/asof.

PHÉP ĐO, nói rõ để tái lập được:
  * rổ    = ticker_prune tại PHIÊN CUỐI ≤ `--asof` (point-in-time, không chọn rổ bằng dữ liệu
            tương lai). Mặc định asof=2026-03-01 ⇒ 263 mã. KHÔNG cố tái lập con số "246 mã" của
            phép đo 2026-08-19: định nghĩa rổ của phép đo đó không ghi lại được, và so hai con số
            trên hai rổ khác nhau còn tệ hơn là đo lại cả hai trên MỘT rổ (làm ở đây).
  * mốc   = `live=False` (PIT, y hệt production trước 2026-08-20) trên CHÍNH rổ đó.
  * chữ ký RESTATE = giá trị phục vụ trùng KHÍT (±1 cp) `shares_total_after` của một AIS có
            `effective_date > asof`. Cần dữ liệu tương lai để tính ⇒ chỉ chạy được trong probe,
            không phải cổng.

    ⚠️ CHỮ KÝ THÔ KHÔNG PHẢI LOOK-AHEAD — PHẢI TÁCH THEO NEO. Một mã KHÔNG đổi số CP giữa `asof`
    và AIS kế tiếp sẽ trùng khít một cách hoàn toàn vô tội: AIS sau chỉ đăng ký lại đúng con số
    đã đúng từ trước. Đo được ở đây: 7/11 ca chữ ký thô của nhánh PIT có neo `ANCHOR_ONLY` —
    dòng quý ĐÃ được `_explain_quarterly` đối chiếu xong với chuỗi AIS, tức con số suy ra được
    tại `asof` bằng dữ liệu của `asof`. Không có look-ahead nào ở đó.
    Look-ahead THẬT chỉ vào được qua neo KHÔNG kiểm chứng được: `FIN_FALLBACK` (dòng quý bị cổng
    loại nhưng vẫn phục vụ) và `ANCHOR_UNVERIFIED`. Vì vậy con số phải trích dẫn là
    `n_restate_fin_*`, KHÔNG phải `n_restate_*` thô.
    Kiểm chứng chéo: `n_restate_fin_pit == 3` (ABB/HAH/NVL) khớp ĐÚNG con số 3 đã ghim trong
    docstring `oshares_live._stale_fallback_verdict` (đo 2026-08-19 trên một rổ 246 mã khác) —
    hai phép đo độc lập, hai rổ khác nhau, cùng một tập mã.

Chạy: python3 lookahead_cost_probe.py [--asof 2026-03-01] [--out cost.json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"))
os.environ.pop("BQ_LOCAL_CACHE", None)

from corp_action_lib import bq                                         # noqa: E402
from oshares_live import _fetch, oshares_at                           # noqa: E402

PRUNE = "lithe-record-440915-m9.tav2_bq.ticker_prune"


def universe(asof):
    rows = bq(f"""
        SELECT DISTINCT ticker FROM `{PRUNE}`
        WHERE time = (SELECT MAX(time) FROM `{PRUNE}` WHERE time <= "{asof}")
        ORDER BY ticker""")
    return [r["ticker"] for r in rows]


def restate_hits(corp, tk, asof, value):
    """AIS SAU `asof` mà `shares_total_after` trùng khít `value` — chữ ký look-ahead."""
    if value is None:
        return []
    return sorted(c["effective_date"] for c in corp
                  if c["ticker"] == tk and c["event_code"] == "AIS"
                  and c.get("shares_total_after") and c.get("effective_date")
                  and c["effective_date"] > asof
                  and abs(float(c["shares_total_after"]) - float(value)) < 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default="2026-03-01")
    ap.add_argument("--future-until", default="2026-08-20",
                    help="tới ngày nào thì coi là 'tương lai đã biết' để bắt chữ ký RESTATE")
    ap.add_argument("--out", default="cost.json")
    a = ap.parse_args()

    tks = universe(a.asof)
    print(f"[universe] {len(tks)} mã ticker_prune tại phiên cuối <= {a.asof}", flush=True)

    # MỘT lần fetch tới `future_until`; `oshares_at` tự cắt cache về `asof` nên hai nhánh vẫn
    # point-in-time, còn `corp` giữ lại phần tương lai để chấm chữ ký RESTATE.
    cache = _fetch(tks, a.future_until)
    corp = cache[1]
    print(f"[fetch] {len(cache[0])} dòng quý, {len(corp)} dòng corp-action", flush=True)

    pit = oshares_at(tks, a.asof, _cache=cache, live=False)
    live = oshares_at(tks, a.asof, _cache=cache, live=True)

    changed, rest_pit, rest_live = [], [], []
    for tk in tks:
        p, l = pit[tk], live[tk]
        if (p["value"] is None) != (l["value"] is None) or (
                p["value"] is not None and l["value"] is not None
                and abs(p["value"] - l["value"]) > 1.0):
            changed.append({"ticker": tk,
                            "pit_value": p["value"], "pit_method": p["method"],
                            "live_value": l["value"], "live_method": l["method"],
                            "live_anchor": l.get("anchor_date"),
                            "live_anchor_source": l.get("anchor_source"),
                            "fin_anchor_ais_certified": l.get("fin_anchor_ais_certified"),
                            "ais_age_days": l.get("ais_age_days")})
        for served, bag in ((p, rest_pit), (l, rest_live)):
            hits = restate_hits(corp, tk, a.asof, served["value"])
            if hits:
                bag.append({"ticker": tk, "value": served["value"],
                            "method": served["method"], "future_ais": hits})

    n_none_pit = sum(1 for tk in tks if pit[tk]["value"] is None)
    n_none_live = sum(1 for tk in tks if live[tk]["value"] is None)
    new_restate = sorted({r["ticker"] for r in rest_live} - {r["ticker"] for r in rest_pit})
    # neo KHÔNG kiểm chứng được = con đường DUY NHẤT một số tương lai vào được câu trả lời
    LOOKAHEAD_METHODS = ("FIN_FALLBACK", "ANCHOR_UNVERIFIED")
    fin_pit = sorted(r["ticker"] for r in rest_pit if r["method"] in LOOKAHEAD_METHODS)
    fin_live = sorted(r["ticker"] for r in rest_live if r["method"] in LOOKAHEAD_METHODS)
    out = {"asof": a.asof, "future_until": a.future_until, "n_universe": len(tks),
           "n_none_pit": n_none_pit, "n_none_live": n_none_live,
           "coverage_gain": n_none_pit - n_none_live,
           "n_changed": len(changed), "changed": changed,
           "n_restate_pit": len(rest_pit), "restate_pit": rest_pit,
           "n_restate_live": len(rest_live), "restate_live": rest_live,
           "restate_new_from_live_branch": new_restate,
           "lookahead_methods": list(LOOKAHEAD_METHODS),
           "n_restate_fin_pit": len(fin_pit), "restate_fin_pit": fin_pit,
           "n_restate_fin_live": len(fin_live), "restate_fin_live": fin_live,
           "restate_fin_new_from_live_branch": sorted(set(fin_live) - set(fin_pit))}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print(f"\n[phủ]     PIT từ chối {n_none_pit}/{len(tks)} · LIVE từ chối {n_none_live}/{len(tks)}"
          f" ⇒ nhánh LIVE cứu thêm {n_none_pit - n_none_live} mã")
    print(f"[đổi số]  {len(changed)} mã")
    print(f"[RESTATE thô]  PIT {len(rest_pit)} · LIVE {len(rest_live)} — KHÔNG trích con số này")
    print(f"[LOOK-AHEAD]   neo không kiểm chứng được {LOOKAHEAD_METHODS}: "
          f"PIT {len(fin_pit)} {fin_pit} · LIVE {len(fin_live)} {fin_live} ⇒ "
          f"CÁI GIÁ MỚI của nhánh LIVE = {sorted(set(fin_live) - set(fin_pit))}")
    for c in changed:
        print(f"   {c['ticker']:5s} {c['pit_method']:<17s} -> {c['live_method']:<13s} "
              f"{c['pit_value']} -> {c['live_value']} (AIS cũ {c.get('ais_age_days')}n)")
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()

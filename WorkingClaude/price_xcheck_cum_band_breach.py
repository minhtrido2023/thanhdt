#!/usr/bin/env python3
"""Đo BƯỚC 1 của Việc C (chuỗi paper-report-fpt-double-adjust-fix-20260929, dispatch
Taylor_20260929_050059): tách 681 ca `ffill_cum_band` (từ `price_xcheck_calibration.py`, Việc B)
thành 2 lớp NGUYÊN NHÂN KHÁC NHAU trước khi bàn nới `_band_lifted_suspect`'s tolerance 1e-9:

  (a) CHAINED — `_lift_neighbour`'s `chained=True`: raw Price của phiên cum LẶP LẠI ĐÚNG giá trị
      phiên liền trước. Đây LÀ định nghĩa ffill/đông giá theo cấu trúc — không liên quan làm tròn,
      không phải ứng viên nới ngưỡng.
  (b) BAND MISMATCH — `chained=False` (Price có đổi so với hôm trước, tức có khả năng là phiên
      giao dịch thật) nhưng vẫn bị `_band_lifted_suspect` từ chối vì nằm ngoài band
      [Low,High] đã lift sang khung raw. CHỈ nhóm này mới là ứng viên "chặn oan do làm tròn" theo
      giả thuyết quant-skeptic (AIG 2026-07-30 lệch 2,8đ).

Với nhóm (b), đo GAP thật (VND + %) giữa Price và biên band gần nhất đã lift, rồi so với BƯỚC GIÁ
(`trading_bot.vn_market.tick_size`, quy ước HOSE theo mức giá — không có cột Exchange trong
`tav2_bq.ticker` nên KHÔNG phân biệt được HNX/UPCOM ở đây; nêu rõ như một giới hạn của phép đo,
không giả định).

KHÔNG SỬA `close_repair.py` trong script này — đây là phép đo, sinh input cho quyết định ở Bước 2.

LỆNH TÁI LẬP: source wc_env.sh && python3 price_xcheck_cum_band_breach.py
VINTAGE: đo 2026-09-29, cùng cửa sổ dữ liệu với `price_xcheck_calibration.py`
(events 2025-01-01..2026-09-15, bars 2024-11-15..2026-09-20).
"""
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import close_repair as cr  # noqa: E402
import price_xcheck_calibration as pxc  # noqa: E402
from trading_bot.vn_market import tick_size  # noqa: E402


def main() -> int:
    from google.cloud import bigquery

    client = bigquery.Client(project=pxc.PROJECT)
    print(f"Đang truy vấn corporate_action ({pxc.EVENT_START}..{pxc.EVENT_END})...", file=sys.stderr)
    events_df = client.query(pxc.SQL_EVENTS).to_dataframe()
    print(f"Đang truy vấn ticker bars ({pxc.PRICE_START}..{pxc.PRICE_END})...", file=sys.stderr)
    bars_df = client.query(pxc.SQL_BARS).to_dataframe()
    print(f"  {len(events_df)} events, {len(bars_df)} bars.", file=sys.stderr)

    events_by_ticker = defaultdict(list)
    for row in events_df.itertuples(index=False):
        events_by_ticker[row.ticker].append({
            "ticker": row.ticker, "exright_date": row.exright_date, "event_code": row.event_code,
            "issue_method_name_vi": row.issue_method_name_vi,
            "exercise_ratio": row.exercise_ratio, "value_per_share": row.value_per_share,
        })

    series_by_ticker = defaultdict(list)
    for row in bars_df.itertuples(index=False):
        series_by_ticker[row.ticker].append(
            {"d": row.d, "close": float(row.Close), "price": float(row.Price),
             "high": float(row.High or 0), "low": float(row.Low or 0)})
    for tk in series_by_ticker:
        series_by_ticker[tk].sort(key=lambda b: b["d"])

    all_pairs = set()
    for tk, evs in events_by_ticker.items():
        for ev in evs:
            all_pairs.add((tk, ev["exright_date"]))

    n_candidate = 0
    n_ffill_cum_band = 0
    chained_cases = []
    band_cases = []  # (tk, ex, gap_vnd, gap_rel, tick, gap_in_ticks, bar)

    for tk, ex in sorted(all_pairs):
        series = series_by_ticker.get(tk, [])
        if not series:
            continue
        series_max = series[-1]["d"]
        if ex > series_max:
            continue
        n_candidate += 1

        evs = [e for e in events_by_ticker[tk] if e["exright_date"] == ex]
        kept, _dropped = cr.dedup_same_term(evs)
        f, note_f = cr.group_factor(ex, kept, series)
        if f is not None or "outside the raw-lifted" not in (note_f or ""):
            continue  # not a ffill_cum_band case
        n_ffill_cum_band += 1

        i_cum = cr._last_cum_index(series, ex)
        bar = series[i_cum]
        neighbour, chained = cr._lift_neighbour(series, i_cum)
        if chained:
            chained_cases.append((tk, ex, bar))
            continue
        if not neighbour or not neighbour.get("close") or neighbour["close"] <= 0:
            # `_band_lifted_suspect` would have returned False here (cannot test) — cannot happen
            # for a case classified ffill_cum_band (that requires the band test itself to fire).
            raise AssertionError((tk, ex, "unexpected: no usable neighbour but flagged band-mismatch"))

        lift = neighbour["price"] / neighbour["close"]
        hi, lo = bar["high"], bar["low"]
        hi_lifted, lo_lifted = hi * lift, lo * lift
        price = bar["price"]
        if price < lo_lifted:
            gap_vnd = lo_lifted - price
        elif price > hi_lifted:
            gap_vnd = price - hi_lifted
        else:
            raise AssertionError((tk, ex, "flagged band-mismatch but price is inside lifted band",
                                   price, lo_lifted, hi_lifted))
        gap_rel = gap_vnd / price
        t = tick_size(price, symbol=tk, exchange="HOSE")
        gap_in_ticks = gap_vnd / t
        band_cases.append((tk, ex, gap_vnd, gap_rel, t, gap_in_ticks, bar["d"]))

    # 681 = pre-fix baseline (Việc B). 454 = post-fix (681 − 227 flipped by the tick-tolerance
    # change, Việc C, 2026-09-29) — running this script against the fixed close_repair.py is
    # itself a cross-check that exactly 227 cases left the ffill_cum_band bucket.
    assert n_ffill_cum_band in (681, 454), \
        f"n_ffill_cum_band={n_ffill_cum_band}, kỳ vọng 681 (pre-fix) hoặc 454 (post-fix)"
    assert n_candidate == 1587, f"n_candidate={n_candidate}, kỳ vọng 1587 (khớp Việc B)"

    print()
    print(f"=== Phân rã {n_ffill_cum_band} ca ffill_cum_band ===")
    print(f"  (a) chained (Price lặp đúng phiên liền trước — ffill THẬT, không phải làm tròn): "
          f"{len(chained_cases)}")
    print(f"  (b) band mismatch (Price ĐỔI so với hôm trước, nhưng ngoài band đã lift — ứng viên "
          f"làm tròn): {len(band_cases)}")
    assert len(chained_cases) + len(band_cases) == n_ffill_cum_band

    if band_cases:
        gaps_vnd = sorted(c[2] for c in band_cases)
        gaps_rel = sorted(c[3] for c in band_cases)
        gaps_ticks = sorted(c[5] for c in band_cases)

        def pct(sorted_list, p):
            idx = min(len(sorted_list) - 1, int(round(p * (len(sorted_list) - 1))))
            return sorted_list[idx]

        print()
        print(f"=== Nhóm (b), n={len(band_cases)} — GAP tuyệt đối (VND) ===")
        for p in (0.50, 0.75, 0.90, 0.95, 0.99):
            print(f"  p{int(p*100)}: {pct(gaps_vnd, p):,.2f} đ")
        print(f"  min: {gaps_vnd[0]:,.2f} đ   max: {gaps_vnd[-1]:,.2f} đ")

        print()
        print(f"=== Nhóm (b) — GAP tương đối (%) ===")
        for p in (0.50, 0.75, 0.90, 0.95, 0.99):
            print(f"  p{int(p*100)}: {pct(gaps_rel, p):.4%}")
        print(f"  min: {gaps_rel[0]:.4%}   max: {gaps_rel[-1]:.4%}")

        print()
        print(f"=== Nhóm (b) — GAP tính theo SỐ BƯỚC GIÁ (tick, quy ước HOSE theo mức giá) ===")
        for p in (0.50, 0.75, 0.90, 0.95, 0.99):
            print(f"  p{int(p*100)}: {pct(gaps_ticks, p):.2f} tick")
        print(f"  min: {gaps_ticks[0]:.2f} tick   max: {gaps_ticks[-1]:.2f} tick")

        print()
        print("=== Phân bố theo ngưỡng SỐ TICK (cỡ-mẫu tích lũy <= N tick) ===")
        for n_tick in (0.5, 1, 1.5, 2, 3, 5, 10, 20, 50):
            cnt = sum(1 for g in gaps_ticks if g <= n_tick)
            print(f"  <= {n_tick} tick: {cnt}/{len(band_cases)} = {cnt/len(band_cases):.1%}")

        print()
        print("=== Phân bố theo ngưỡng TƯƠNG ĐỐI (cỡ-mẫu tích lũy <= X%) ===")
        for x in (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20):
            cnt = sum(1 for g in gaps_rel if g <= x)
            print(f"  <= {x:.2%}: {cnt}/{len(band_cases)} = {cnt/len(band_cases):.1%}")

        print()
        print("=== 15 ca gap NHỎ NHẤT theo tick (ứng viên làm-tròn rõ nhất) ===")
        for tk, ex, gap_vnd, gap_rel, t, gap_ticks, d_cum in sorted(band_cases, key=lambda c: c[5])[:15]:
            print(f"  {tk} ex={ex} cum={d_cum}: gap={gap_vnd:,.1f}đ ({gap_rel:.3%}), "
                  f"tick={t}đ → {gap_ticks:.2f} tick")

        print()
        print("=== 15 ca gap LỚN NHẤT theo tick (ứng viên ffill/stale THẬT) ===")
        for tk, ex, gap_vnd, gap_rel, t, gap_ticks, d_cum in sorted(band_cases, key=lambda c: -c[5])[:15]:
            print(f"  {tk} ex={ex} cum={d_cum}: gap={gap_vnd:,.1f}đ ({gap_rel:.3%}), "
                  f"tick={t}đ → {gap_ticks:.2f} tick")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

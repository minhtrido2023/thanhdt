#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Giá tham chiếu phiên của UPCOM = giá ĐÓNG CỬA hay BÌNH QUÂN GIA QUYỀN phiên trước?

CHỈ ĐỌC. Không đặt lệnh, không ghi state production — chỉ `secdef` (endpoint giá, không cần
trading token) + một truy vấn BQ. Ghi kết quả ra CSV cạnh file này.

VÌ SAO test này mạnh hơn test trên ngày GDKHQ: luật tham chiếu áp cho MỌI phiên, không riêng
ngày có sự kiện quyền. Trên ngày GDKHQ, cỡ mẫu là số sự kiện (n=2: VGT lệch −100đ, QNS khớp)
và làm tròn 100đ của UPCOM nuốt mất mọi chênh lệch <50đ nên QNS không phân biệt được hai giả
thuyết. Trên ngày THƯỜNG, mọi mã đang niêm yết đều là một quan sát, và HOSE/HNX làm ĐỐI CHỨNG
trong cùng một lần đo, cùng một feed:

    H0 (đóng cửa)  : ref(phiên T) == close(phiên T−1) trên MỌI sàn.
    H1 (bình quân) : ref == close trên HOSE/HNX, nhưng LỆCH ở một tỉ lệ đáng kể mã UPCOM.

Đối chứng nội bộ là thứ làm test này không thể bị "cả hai đường cùng sai": nếu feed hay cơ sở
giá của ta sai hệ quy chiếu, HOSE/HNX cũng phải lệch. HOSE/HNX khớp mà UPCOM lệch ⇒ khác biệt
nằm ở LUẬT CỦA SÀN, không nằm ở đường dữ liệu.

Chạy lúc 01:04 ICT 2026-08-18 (TRƯỚC giờ mở cửa): bản ghi secdef đã lật sang phiên 08-18 từ
~19:23 ngày 08-17, nên `basicPrice` đọc bây giờ LÀ tham chiếu phiên 08-18, và phiên trước nó
là 08-17 — đã có trong BQ. Chạy lại vào khung giờ khác thì cặp phiên đổi: xem cổng G6.

Loại khỏi mẫu: mã có `exright_date` trong cửa sổ (tham chiếu bị điều chỉnh hợp lệ, không phải
bằng chứng về luật làm tròn) và mã không đọc được sàn (fail-closed, không đoán).
"""
import csv
import os
import subprocess
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

from trading_bot.brokers import (MARKET_ID_TO_EXCHANGE, DNSEBroker, get_dnse_client,  # noqa: E402
                                 qget)
from trading_bot.vn_market import normalize_price_vnd, tick_size  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(HERE, "upcom_ref_basis_probe_20260818.csv")
PREV_SESSION = "2026-08-17"   # phiên cum ngay trước phiên mà secdef đang mô tả
THIS_SESSION = "2026-08-18"
BQ_PROJECT = "lithe-record-440915-m9"


def bq_rows(sql, max_rows=100000):
    """Chạy bq CLI qua wc_env.sh (đừng tự đoán đường dẫn SDK — CLAUDE.md).

    ⚠️ `--max_rows` là BẮT BUỘC: `bq query` mặc định chỉ in **100 dòng đầu** và KHÔNG báo là
    đã cắt. Lần chạy đầu của probe này ăn đúng cái bẫy đó — `LIMIT 700` trả về 100, universe
    tụt còn 95 mã và chỉ 4 UPCOM, y hệt lần chạy trước nên trông như "đã lấy hết".
    """
    cmd = ("source /home/trido/thanhdt/WorkingClaude/wc_env.sh && "
           f"bq query --use_legacy_sql=false --project_id={BQ_PROJECT} --format=csv "
           f"--max_rows={int(max_rows)} {sql!r}")
    out = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError(f"bq lỗi: {out.stderr[-2000:]}")
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    return list(csv.DictReader(lines))


def main():
    excluded = {r["ticker"] for r in bq_rows(
        "SELECT DISTINCT ticker FROM `lithe-record-440915-m9.tav2_bq.corporate_action` "
        f'WHERE exright_date BETWEEN "{PREV_SESSION}" AND "2026-08-21"')}
    print(f"loại {len(excluded)} mã có sự kiện quyền trong cửa sổ: {sorted(excluded)}")

    # Bảng `ticker` (không phải `ticker_1m`) vì `ticker_1m` là ảnh chụp đã lọc — chỉ ra 95 mã,
    # trong đó vỏn vẹn 4 UPCOM. Cần phủ rộng để n(UPCOM) đủ nói được điều gì.
    # `Low`/`High` phiên T−1 là ĐIỀU KIỆN CẦN kiểm chứng được: một giá bình quân gia quyền
    # BẮT BUỘC nằm trong [Low, High] của chính phiên đó. Ref nằm NGOÀI ⇒ bác bỏ H1 cho mã đó.
    universe = bq_rows(
        "SELECT t.ticker, t.Price AS close_prev, t.Low AS low_prev, t.High AS high_prev, "
        "t.Volume "
        "FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t "
        f'WHERE t.time = "{PREV_SESSION}" AND t.Volume >= 3000 '
        'AND t.ticker NOT IN ("VNINDEX","VN30","HNX30","HNXINDEX","UPCOMINDEX") '
        "ORDER BY t.Volume DESC LIMIT 700")
    universe = [r for r in universe if r["ticker"] not in excluded]
    print(f"universe {len(universe)} mã (phiên trước {PREV_SESSION})")

    client = get_dnse_client()
    rows, errors = [], 0
    for i, r in enumerate(universe, 1):
        tk = r["ticker"]
        try:
            # `secdef` trả LIST bản ghi theo board (G1 lô chẵn, G4 lô lẻ, T* thoả thuận) —
            # tái dùng bộ chọn board của production thay vì tự viết, để probe đứng trên ĐÚNG
            # bản ghi mà cổng G1-G6 sẽ đứng lên khi chạy thật.
            sd = DNSEBroker._pick_board(client.secdef(tk), "secdefs") or {}
        except Exception as exc:                                    # noqa: BLE001
            errors += 1
            if errors <= 5:
                print(f"  ! {tk}: {type(exc).__name__}: {exc}")
            continue
        market_id = qget(sd, "marketId", "market_id")
        exchange = MARKET_ID_TO_EXCHANGE.get(str(market_id or "").upper())
        ref = normalize_price_vnd(qget(sd, "basicPrice", "basic_price"))
        prev_close = normalize_price_vnd(float(r["close_prev"]))
        if not exchange or not ref or not prev_close:
            continue          # fail-closed: không đoán sàn, không đoán giá
        dev = ref - prev_close
        tick = tick_size(ref, symbol=tk, exchange=exchange)
        low = normalize_price_vnd(float(r["low_prev"])) if r.get("low_prev") else None
        high = normalize_price_vnd(float(r["high_prev"])) if r.get("high_prev") else None
        # Điều kiện CẦN của giả thuyết "ref = bình quân gia quyền phiên T−1": ref ∈ [Low, High]
        # của phiên T−1 (nới đúng 1 tick cho việc sở làm tròn). Ngoài khoảng ⇒ ref KHÔNG THỂ là
        # một giá bình quân của phiên đó, bất kể trọng số nào.
        in_range = (None if low is None or high is None
                    else (low - tick) <= ref <= (high + tick))
        rows.append({
            "ticker": tk, "exchange": exchange, "market_id": market_id,
            "secdef_time": qget(sd, "time"), "session": THIS_SESSION,
            "ref_live": ref, "prev_close": prev_close,
            "prev_low": low, "prev_high": high, "ref_in_prev_range": in_range,
            "dev_vnd": dev, "dev_ticks": round(dev / tick, 3) if tick else None,
            "tick": tick, "match": abs(dev) < 1e-6,
            "volume_prev": r["Volume"],
        })
        if i % 50 == 0:
            print(f"  … {i}/{len(universe)} (đã thu {len(rows)})")

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\nCSV: {OUT_CSV}  ({len(rows)} mã đo được, {errors} lỗi đọc)\n")
    print(f"{'SÀN':7} {'n':>4} {'khớp':>6} {'lệch':>6} {'% lệch':>8} "
          f"{'|lệch| TB (đ)':>14} {'max |lệch| (tick)':>18}")
    for ex in ("HOSE", "HNX", "UPCOM"):
        grp = [x for x in rows if x["exchange"] == ex]
        if not grp:
            continue
        off = [x for x in grp if not x["match"]]
        mean_abs = sum(abs(x["dev_vnd"]) for x in off) / len(off) if off else 0.0
        max_ticks = max((abs(x["dev_ticks"] or 0) for x in off), default=0.0)
        print(f"{ex:7} {len(grp):4d} {len(grp) - len(off):6d} {len(off):6d} "
              f"{100.0 * len(off) / len(grp):7.1f}% {mean_abs:14,.0f} {max_ticks:18.2f}")

    # Dấu của lệch: giá bình quân nằm hai phía giá đóng cửa với xác suất xấp xỉ nhau, nên H1
    # dự đoán lệch ĐỐI XỨNG. Lệch một chiều tuyệt đối sẽ là chữ ký của cơ chế KHÁC (vd sở tự
    # điều chỉnh xuống), nên phải đếm dấu chứ không chỉ đếm số mã lệch.
    off_up = [x for x in rows if x["exchange"] == "UPCOM" and not x["match"]]
    pos = sum(1 for x in off_up if x["dev_vnd"] > 0)
    print(f"\nDấu lệch UPCOM: {pos} dương / {len(off_up) - pos} âm "
          f"(H1 'bình quân gia quyền' dự đoán xấp xỉ đối xứng)")
    outside = [x for x in off_up if x["ref_in_prev_range"] is False]
    print(f"Ref NẰM NGOÀI [Low,High] phiên T−1: {len(outside)}/{len(off_up)} mã lệch "
          f"⇒ với những mã này ref KHÔNG THỂ là giá bình quân của phiên đó (bác bỏ H1)")
    for x in outside[:15]:
        print(f"    ✗ {x['ticker']:6} ref {x['ref_live']:>9,.0f} ngoài "
              f"[{x['prev_low']:,.0f}; {x['prev_high']:,.0f}]")

    print("\nMã UPCOM LỆCH (bằng chứng trực tiếp cho H1 nếu HOSE/HNX khớp 100%):")
    for x in sorted(off_up, key=lambda x: -abs(x["dev_vnd"]))[:25]:
        rng = ("?" if x["ref_in_prev_range"] is None
               else ("trong dải" if x["ref_in_prev_range"] else "NGOÀI DẢI"))
        print(f"  {x['ticker']:6} ref {x['ref_live']:>10,.0f}  close(T-1) "
              f"{x['prev_close']:>10,.0f}  lệch {x['dev_vnd']:>+8,.0f}đ "
              f"({x['dev_ticks']:+.2f} tick)  [{x['prev_low']:,.0f}–{x['prev_high']:,.0f}] {rng}")


if __name__ == "__main__":
    main()

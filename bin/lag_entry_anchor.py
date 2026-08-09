#!/usr/bin/env python3
"""Tra `entry_anchor_price` — giá NEO của phiên entry chuẩn, cho cửa sổ entry LAG V2.4.

⚠️ CHỈ ĐỌC. Không đặt lệnh, không ghi plan. Gọi BQ (dữ liệu LỊCH SỬ), KHÔNG gọi DNSE.

VÌ SAO CÓ FILE NÀY (gap thật, phát hiện 2026-08-09, job Taylor_20260809_082212): luật V2.4
user duyệt cùng ngày mở cửa sổ entry LAG ra 3 phiên (phiên chuẩn + 2 phiên kế tiếp), nhưng
điều kiện an toàn CỐT LÕI của chính luật đó là "giá live không được vượt `entry_anchor_price`
đã lưu ở phiên chuẩn" — mà KHÔNG nguồn dữ liệu nào sinh ra con số này. Bản vá đầu tiên chỉ đặt
cờ `requires_anchor_price=True` rồi thả mã vào `due_today`: cửa sổ mở ra nhưng cái chốt cửa
không tồn tại. File này sinh ra con số thật đó.

BA QUYẾT ĐỊNH DỮ LIỆU (đừng đảo lại nếu chưa đọc lý do):

1. **Dùng `Price` (giá THÔ), TUYỆT ĐỐI KHÔNG dùng `Close`.** `Close` trong `tav2_bq.ticker` là
   giá ĐÃ ĐIỀU CHỈNH cổ tức/chia tách, hồi tố từ vintage HÔM NAY về quá khứ. Anchor được đem so
   với GIÁ LIVE trên bảng (DNSE) — giá thô. Trộn hai hệ quy chiếu = đúng "Bẫy (2)" trong
   `kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`. Nếu mã chốt quyền
   giữa phiên chuẩn và phiên 2/3, `Close` của phiên chuẩn bị kéo XUỐNG so với giá thật đã khớp
   ⇒ anchor thấp giả tạo ⇒ chặn oan một entry hợp lệ. `Price` không hồi tố nên miễn nhiễm.
   (Với DRI 08-06 hai cột tình cờ bằng nhau = 13.000; sự trùng khớp đó KHÔNG phải lý do để
   dùng `Close` — nó chỉ có nghĩa là DRI chưa có ex-date trong cửa sổ này.)

2. **Đọc thẳng BẢNG BQ, không qua cache local.** `data/bq_cache` chỉ sync 23:45 ICT (sự cố
   2026-07-09, lệch +5,7%). Ở đây gọi `bq` CLI trực tiếp nên không dính cache — và đừng
   "tối ưu" bằng cách đọc parquet cache, đó chính là con đường đã gây lỗi.

3. **BQ hợp lệ ở đây vì đây là giá LỊCH SỬ, không phải giá trong ngày.** Quy tắc cứng
   `coding_guidelines.md §6` (dữ liệu cùng ngày PHẢI lấy DNSE) vẫn nguyên giá trị và KHÔNG bị
   nới ở đây: hàm này TỪ CHỐI tra anchor cho ngày >= `plan_date` (xem `_reject_non_historical`).
   Phiên chuẩn của một ứng viên ngày-2/3 luôn nằm trước `plan_date` theo định nghĩa, nên ràng
   buộc này không bao giờ cản đường đi đúng — nó chỉ chặn đường đi sai.

⚠️ Anchor KHÔNG PHẢI là giá đặt lệnh. Nó là TRẦN để so với giá live tại lúc thực thi; giá live
   đó vẫn phải lấy từ DNSE (§6). File này không biết gì về giá hôm nay và không nên biết.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

BQ_PROJECT = os.environ.get("BQ_PROJECT", "lithe-record-440915-m9")

# `bq query` mặc định chỉ trả 100 DÒNG ĐẦU và cắt ÂM THẦM (đã cắn thật 2026-08-02 ở
# dividend_adjusted_return.py). Cửa sổ này tối đa vài chục mã nên trần rộng là đủ an toàn,
# nhưng vẫn RAISE khi chạm trần thay vì im lặng dùng kết quả có thể thiếu.
BQ_MAX_ROWS = 10_000
BQ_TIMEOUT_S = 120

ANCHOR_SOURCE = "tav2_bq.ticker.Price (giá thô, chưa điều chỉnh cổ tức)"


def _d(x):
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    return dt.date.fromisoformat(str(x)[:10])


def _bq(sql):
    """Chạy BQ, trả list[dict]. Lỗi → raise (caller fail-closed, không đoán mò)."""
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
         f"--max_rows={BQ_MAX_ROWS}", "--format=json", sql],
        capture_output=True, text=True, timeout=BQ_TIMEOUT_S,
    )
    if out.returncode != 0:
        raise RuntimeError(f"bq query failed: {out.stderr.strip()[:400]}")
    body = out.stdout.strip()
    start = body.find("[")          # bq đôi khi in dòng cảnh báo trước JSON
    rows = json.loads(body[start:]) if start >= 0 else []
    if len(rows) >= BQ_MAX_ROWS:
        raise RuntimeError(f"bq chạm trần {BQ_MAX_ROWS} dòng — gần như chắc chắn bị CẮT")
    return rows


def _reject_non_historical(pairs, plan_date):
    """§6: anchor chỉ được tra cho phiên ĐÃ ĐÓNG. Ngày >= plan_date ⇒ đó là giá trong ngày,
    phải lấy DNSE chứ không phải BQ — raise thay vì trả một con số sai hệ quy chiếu."""
    if plan_date is None:
        return
    bad = sorted({f"{t}@{_d(d)}" for t, d in pairs if _d(d) >= _d(plan_date)})
    if bad:
        raise ValueError(
            f"từ chối tra anchor bằng BQ cho ngày >= plan_date ({_d(plan_date)}): {bad}. "
            f"Giá trong ngày PHẢI lấy DNSE (coding_guidelines §6).")


def fetch_anchor_prices(pairs, plan_date=None):
    """[(ticker, entry_date)] → {(ticker, 'YYYY-MM-DD'): giá thô}.

    Cặp nào KHÔNG có dữ liệu thật thì VẮNG MẶT trong dict trả về — caller phải coi "vắng mặt"
    là loại khỏi ứng viên, không được suy diễn giá thay thế."""
    pairs = [(str(t).strip().upper(), _d(d)) for t, d in pairs]
    if not pairs:
        return {}
    _reject_non_historical(pairs, plan_date)

    inlist = ",".join(f"'{t}'" for t in sorted({t for t, _ in pairs}))
    lo, hi = min(d for _, d in pairs), max(d for _, d in pairs)
    rows = _bq(f"""
        SELECT t.ticker AS tk, CAST(t.time AS STRING) AS d, t.Price AS px
        FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
        WHERE t.ticker IN ({inlist})
          AND t.time BETWEEN DATE '{lo}' AND DATE '{hi}'
          AND t.Price > 0
    """)
    px = {(r["tk"], r["d"][:10]): float(r["px"]) for r in rows}
    return {k: v for k, v in px.items() if k in {(t, str(d)) for t, d in pairs}}


def main():
    ap = argparse.ArgumentParser(description="Tra entry_anchor_price (giá thô phiên chuẩn).")
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--entry-date", required=True)
    ap.add_argument("--plan-date")
    a = ap.parse_args()
    try:
        px = fetch_anchor_prices([(a.ticker, a.entry_date)], a.plan_date)
    except Exception as e:                                   # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 1
    v = px.get((a.ticker.strip().upper(), str(_d(a.entry_date))))
    print(json.dumps({"ok": v is not None, "ticker": a.ticker.upper(),
                      "entry_date": str(_d(a.entry_date)), "entry_anchor_price": v,
                      "source": ANCHOR_SOURCE}, ensure_ascii=False, indent=2))
    return 0 if v is not None else 1


if __name__ == "__main__":
    sys.exit(main())

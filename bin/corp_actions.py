#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sổ đăng ký SỰ KIỆN DOANH NGHIỆP làm ĐỔI SỐ LƯỢNG cổ phiếu (chia tách / thưởng / cổ tức CP).

VÌ SAO CÓ FILE NÀY
------------------
`mike/bin/park_holdings.py::LotBook` chỉ có `buy()`/`sell()` theo journal fill. Không có thao
tác nào cho sự kiện doanh nghiệp ⇒ ngày VHM chia cổ tức cổ phiếu 1:1 (broker credit 2026-08-05),
sổ lô đứng ở 500cp trong khi broker nhảy lên 1000cp, `reconcile.ok=False`, L1 park-trim
`BLOCKED_RECONCILE` VĨNH VIỄN cho tới khi có người sửa tay. Đây là khe hở THIẾT KẾ, không phải
lỗi một lần: mỗi corp action sau này lặp lại y hệt.

⚠️ ĐIỀU QUAN TRỌNG NHẤT — **KHÔNG BAO GIỜ tự suy corp action từ việc thấy qty lệch.**
"Sổ 500, broker 1000 ⇒ chắc là chia đôi" là đúng cái lối đoán-rồi-gộp mà §5
`coding_guidelines` cấm: một lệnh bị bỏ sót khỏi journal, một GHOST_ORDER, hay một vụ chuyển
khoản chứng khoán cũng tạo ra ĐÚNG hình dạng lệch đó. Mất khả năng phân biệt "corp action" với
"kế toán sai" là mất luôn giá trị của cái cổng reconcile. Vì vậy sổ này là **file dữ liệu do
người xác nhận**, và `park_holdings` CHỈ áp record có `_status` bắt đầu bằng `CONFIRMED` —
cùng khuôn với `_status: APPROVED` của bootstrap snapshot.

BA CÁI MỐC THỜI GIAN KHÁC NHAU — ĐỪNG GỘP (bài học rút từ chính ca VHM 2026-08)
------------------------------------------------------------------------------
  * `ex_date`               — GDKHQ trên sàn. Quyết định **LÔ NÀO ĐƯỢC CHIA**: chỉ lô có
                              `entry_date < ex_date` (mua từ ex_date trở đi = không hưởng quyền).
  * `record_date`           — ngày đăng ký cuối cùng. Chỉ để tra cứu/đối chiếu công bố.
  * `broker_effective_ts`   — thời điểm BROKER thật sự đổi `openQuantity`. Quyết định **NGÀY SỔ
                              PHẢI NHẢY**, vì bất biến đối soát là `Σ lô == openQuantity` của
                              broker, không phải của sàn.

Ca VHM 2026-08 chứng minh ba mốc này KHÔNG trùng nhau: DNSE credit cổ phiếu thưởng ngày
2026-08-05, TRƯỚC ex-date sàn 2026-08-06 một phiên (BQ vẫn báo Price 153.000 ngày 08-05 và khớp
broker tuyệt đối ở 7 mã khác cùng ngày ⇒ BQ tươi, sàn chưa lăn chốt). Neo sổ theo ex_date thì
hôm nay vẫn lệch; neo entitlement theo broker_effective_ts thì một lô mua ngày 08-05 (vẫn được
hưởng quyền) sẽ bị bỏ sót. Phải giữ cả hai.

XÁC NHẬN ĐỘC LẬP (không phải một nguồn, không phải chính cái lệch)
-----------------------------------------------------------------
`verify_against_bq()` dưới đây kiểm hệ số nhân bằng NGUỒN KHÁC HẲN broker: cú nhảy tỉ số
`Close/Price` của `tav2_bq.ticker` tại ex_date (cùng cơ chế `dividend_adjusted_return
._scan_jumps`, tầng 1). Một sự kiện chia 1:1 phải làm tỉ số nhảy đúng hệ số 2,0.
Ba kết quả có thể: `MATCH` / `MISMATCH` / `PENDING` (BQ chưa có phiên nào từ ex_date trở đi —
tình huống bình thường khi corp action vừa xảy ra hoặc còn ở tương lai). `PENDING` **không phải**
`MATCH`: nó chỉ nói "chưa kiểm được", và đó chính là lý do trường `evidence` bắt buộc phải có ít
nhất 2 nguồn độc lập trước khi người ta ký `CONFIRMED`.

Dùng như thư viện (đường live — CHỈ đọc file, KHÔNG gọi BQ/mạng):
    from corp_actions import load_corp_actions
    for a in load_corp_actions():        # chỉ trả record đã CONFIRMED + hợp lệ
        ...

Dùng như CLI (đường offline — có gọi BQ để lấy bằng chứng):
    python3 mike/bin/corp_actions.py --list
    python3 mike/bin/corp_actions.py --verify VHM-2026-08-06-STOCK-DIV-100
"""
import argparse
import datetime as dt
import json
import os
import sys

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY = os.path.join(WC_ROOT, "data", "corp_actions.json")

# Chỉ các loại sự kiện làm ĐỔI SỐ LƯỢNG. Cổ tức TIỀN MẶT không thuộc file này — nó đi qua
# `mike/bin/dividend_adjusted_return.py` (§21 coding_guidelines) và không đụng vào số lượng lô.
QTY_EVENT_TYPES = {"STOCK_DIVIDEND", "BONUS_ISSUE", "SPLIT"}
CONFIRMED_PREFIX = "CONFIRMED"
RATIO_TOL = 0.02          # sai số cho phép giữa hệ số khai báo và hệ số suy từ tỉ số BQ


class CorpActionError(Exception):
    """Record sai định dạng/thiếu trường. Ném ra thay vì bỏ qua im lặng: một record hỏng nghĩa là
    sổ lô sắp sai, và sai im lặng đúng là dạng lỗi thiết kế này sinh ra để chặn."""


def _require(rec, field, idx):
    if rec.get(field) in (None, ""):
        raise CorpActionError(f"corp_actions[{idx}] thiếu trường bắt buộc '{field}': "
                              f"{json.dumps(rec, ensure_ascii=False)[:200]}")
    return rec[field]


def _date(value, field, idx):
    try:
        return dt.date.fromisoformat(str(value)[:10]).isoformat()
    except ValueError:
        raise CorpActionError(f"corp_actions[{idx}].{field}='{value}' không phải ngày ISO")


def validate(rec, idx=0):
    """Chuẩn hoá + kiểm một record. Trả về dict đã chuẩn hoá; ném `CorpActionError` nếu sai."""
    ticker = str(_require(rec, "ticker", idx)).strip().upper()
    etype = str(_require(rec, "event_type", idx)).strip().upper()
    if etype not in QTY_EVENT_TYPES:
        raise CorpActionError(f"corp_actions[{idx}].event_type='{etype}' không thuộc "
                              f"{sorted(QTY_EVENT_TYPES)} — cổ tức tiền mặt KHÔNG đi qua file này")
    try:
        mult = float(_require(rec, "qty_multiplier", idx))
    except (TypeError, ValueError):
        raise CorpActionError(f"corp_actions[{idx}].qty_multiplier không phải số")
    if mult <= 1.0:
        raise CorpActionError(f"corp_actions[{idx}].qty_multiplier={mult} ≤ 1 — sổ này chỉ mô tả "
                              f"sự kiện LÀM TĂNG số lượng; gộp cổ phiếu (reverse split) chưa được "
                              f"thiết kế, cần bàn riêng vì phát sinh lô lẻ")
    ex_date = _date(_require(rec, "ex_date", idx), "ex_date", idx)
    eff_ts = str(_require(rec, "broker_effective_ts", idx))
    _date(eff_ts, "broker_effective_ts", idx)          # phải parse được phần ngày
    return {
        "id": rec.get("id") or f"{ticker}-{ex_date}-{etype}",
        "ticker": ticker, "event_type": etype, "qty_multiplier": mult,
        "ratio_text": rec.get("ratio_text", ""),
        "ex_date": ex_date, "record_date": rec.get("record_date"),
        "broker_effective_ts": eff_ts,
        "_status": str(rec.get("_status", "")),
        "confirmed_by": rec.get("confirmed_by"), "confirmed_at": rec.get("confirmed_at"),
        "evidence": rec.get("evidence") or [],
        "note": rec.get("note", ""),
    }


def load_all(path=REGISTRY):
    """MỌI record (kể cả chưa duyệt), đã chuẩn hoá. Sổ vắng mặt = danh sách rỗng, KHÔNG lỗi —
    tuyệt đại đa số phiên không có corp action nào, đó là trạng thái bình thường."""
    if not os.path.exists(path):
        return []
    blob = json.load(open(path, encoding="utf-8"))
    return [validate(r, i) for i, r in enumerate(blob.get("actions") or [])]


def load_corp_actions(path=REGISTRY, ticker=None):
    """Chỉ record ĐÃ ĐƯỢC NGƯỜI XÁC NHẬN (`_status` bắt đầu bằng `CONFIRMED`) — đây là hàm mà
    đường live (`park_holdings`) gọi. Fail-closed: record `PROPOSED`/`PENDING` bị bỏ qua, sổ lô
    giữ nguyên số cũ và cổng reconcile tiếp tục chặn — đúng hành vi mong muốn khi chưa ai ký."""
    out = [a for a in load_all(path) if a["_status"].upper().startswith(CONFIRMED_PREFIX)]
    if ticker:
        out = [a for a in out if a["ticker"] == str(ticker).upper()]
    return sorted(out, key=lambda a: (a["broker_effective_ts"], a["ticker"]))


# ───────────────────────────────── xác nhận độc lập bằng BQ (đường OFFLINE, có gọi mạng)

def verify_against_bq(action, window_days=15):
    """So hệ số khai báo với hệ số suy ra từ cú nhảy `Close/Price` tại ex_date.

    KHÔNG được gọi từ đường live: hàm này chạy `bq` (subprocess, mạng) và §6 cấm đường same-day
    đọc BQ. Nó tồn tại để SINH BẰNG CHỨNG cho người ký `CONFIRMED`, chạy tay hoặc theo cron.

    Trả `{"verdict": MATCH|MISMATCH|PENDING|ERROR, ...}`.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ex = action["ex_date"]
    start = (dt.date.fromisoformat(ex) - dt.timedelta(days=window_days)).isoformat()
    end = (dt.date.fromisoformat(ex) + dt.timedelta(days=window_days)).isoformat()
    try:
        from dividend_adjusted_return import detect_adjustments_batch
        events, max_date = detect_adjustments_batch([action["ticker"]], start, end)
    except Exception as e:                                    # bq lỗi/không có quyền
        return {"verdict": "ERROR", "detail": f"{type(e).__name__}: {str(e)[:200]}"}

    # BQ chưa có phiên nào TỪ ex_date trở đi ⇒ cú nhảy chưa thể lộ ra. "Không thấy" ở đây KHÔNG
    # đồng nghĩa "không có" (đúng cảnh báo trong docstring `detect_adjustments_batch`).
    if not max_date or max_date < ex:
        return {"verdict": "PENDING", "bq_max_date": max_date or None,
                "detail": f"BQ mới có tới {max_date or '(rỗng)'} < ex_date {ex} — cú nhảy tỉ số "
                          f"chỉ lộ ra ĐÚNG Ở phiên ex, chưa kiểm được (không phải bằng chứng phủ định)"}

    hits = [e for e in events.get(action["ticker"], []) if e.ex_date == ex]
    if not hits:
        return {"verdict": "MISMATCH", "bq_max_date": max_date,
                "detail": f"BQ đã có dữ liệu tới {max_date} nhưng KHÔNG thấy cú nhảy tỉ số nào tại "
                          f"ex_date {ex} — hoặc ex_date khai sai, hoặc sự kiện không có thật"}
    e = hits[0]
    # `_scan_jumps` cho `last_cum_price` và `per_share` ước lượng; hệ số điều chỉnh giá suy ngược:
    #   factor = P_cum / (P_cum − per_share).  Chia 1:1 ⇒ factor = 2,0.
    denom = e.last_cum_price - e.per_share
    if denom <= 0:
        return {"verdict": "ERROR", "detail": f"suy hệ số ra số không hợp lệ (P_cum="
                                              f"{e.last_cum_price}, est={e.per_share})"}
    factor = e.last_cum_price / denom
    ok = abs(factor - action["qty_multiplier"]) <= RATIO_TOL * action["qty_multiplier"]
    return {"verdict": "MATCH" if ok else "MISMATCH", "bq_max_date": max_date,
            "bq_factor": round(factor, 4), "declared_multiplier": action["qty_multiplier"],
            "last_cum_date": e.last_cum_date, "last_cum_price": e.last_cum_price,
            "detail": f"tỉ số Close/Price nhảy hệ số {factor:.4f} tại {ex} "
                      f"(giá cum {e.last_cum_price:,.0f} ngày {e.last_cum_date}) vs khai báo "
                      f"{action['qty_multiplier']}"}


def main():
    ap = argparse.ArgumentParser(description="Sổ corp action làm đổi số lượng cổ phiếu")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verify", metavar="ID", help="kiểm 1 record với BQ (gọi mạng)")
    ap.add_argument("--registry", default=REGISTRY)
    a = ap.parse_args()
    acts = load_all(a.registry)
    if a.verify:
        hit = [x for x in acts if x["id"] == a.verify]
        if not hit:
            print(f"không có record id='{a.verify}' trong {a.registry}")
            return 2
        r = verify_against_bq(hit[0])
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["verdict"] in ("MATCH", "PENDING") else 1
    print(f"=== {a.registry} — {len(acts)} record ===")
    for x in acts:
        live = x["_status"].upper().startswith(CONFIRMED_PREFIX)
        print(f"  [{'ÁP DỤNG' if live else 'CHƯA ÁP'}] {x['id']}  {x['ticker']} ×"
              f"{x['qty_multiplier']}  ex={x['ex_date']}  broker={x['broker_effective_ts']}")
        print(f"        _status: {x['_status'][:150]}")
        for ev in x["evidence"]:
            print(f"        · {ev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

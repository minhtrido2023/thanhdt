#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh trần giá mua LUẬT A cho lệnh LAG entry-window — CHẠY 1 LẦN LÚC LẬP PLAN.

⚠️ CHỈ ĐỌC. Không đặt lệnh, không ghi plan, không sửa file nào trừ khi có `--apply <plan.json>`
(và ngay cả khi đó cũng chỉ sửa 5 field trần của đúng lệnh trong phạm vi).

Luật A (user chốt 2026-08-15, bus `ceiling-rule-AB-user-decision-CORRECTED`):
    hard_no_chase_ceiling_vnd = Price(phiên đã đóng gần nhất TRƯỚC plan_date) × (1 + 3%)

Đây là **lựa chọn CHÍNH SÁCH** — trả thêm ~16 bps trung bình để cắt rủi ro kẹt hoàn toàn khi
giá chạy — **KHÔNG phải một cải tiến có bằng chứng**. Trên implementation shortfall, chênh lệch
A−B không có ý nghĩa thống kê và đổi dấu theo giả định. Xem `trading_bot/no_chase_ceiling.py`
và `mike/agents/Taylor/research/ceiling_ab_pacing_20260814/README.md`.

BA QUYẾT ĐỊNH DỮ LIỆU (cùng lý do với `mike/bin/lag_entry_anchor.py` — đừng đảo lại):
 1. Dùng `tav2_bq.ticker.Price` (giá THÔ). **TUYỆT ĐỐI không `Close`** — `Close` đã điều chỉnh
    cổ tức/chia tách hồi tố từ vintage hôm nay, trong khi trần được đem so với giá LIVE trên
    bảng (giá thô). Trộn hai hệ quy chiếu = "Bẫy (2)" trong
    `kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`.
 2. Đọc thẳng bảng BQ, KHÔNG qua `data/bq_cache` (cache sync 23:45 ICT, sự cố 2026-07-09).
 3. BQ hợp lệ ở đây vì đây là giá LỊCH SỬ: công cụ TỪ CHỐI mọi phiên >= plan_date. Quy tắc cứng
    §6 (dữ liệu cùng ngày PHẢI lấy DNSE) không bị nới.

CỔNG TƯƠI (mặc định BẬT, `--allow-stale-anchor` để tắt): anchor phải đúng bằng phiên giao dịch
liền trước `plan_date` theo lịch của chính BQ (VNINDEX). Nếu bảng BQ chưa nạp phiên hôm nay lúc
lập plan (~19-21h ICT), công cụ **KHÔNG in trần** thay vì im lặng dùng giá phiên cũ hơn — trần cũ
hơn thì AN TOÀN (chặt hơn) nhưng làm hỏng đúng cái cơ chế này sinh ra để chữa, và không ai thấy.

    python3 lag_rule_a_ceiling.py --plan-date 2026-08-18 --tickers DRI,POW,SCL
    python3 lag_rule_a_ceiling.py --plan-date 2026-08-18 --plan data/trade_plans/plan_SpaceX_2026-08-18.json
    ... thêm --apply để GHI 5 field trần vào chính file plan đó (in diff trước khi ghi).
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.no_chase_ceiling import (  # noqa: E402
    RULE_A_TAU_DEFAULT, RULE_A_TAU_MAX, apply_rule_a, resolve_buy_ceiling)

BQ_PROJECT = os.environ.get("BQ_PROJECT", "lithe-record-440915-m9")
BQ_MAX_ROWS = 10_000
BQ_TIMEOUT_S = 120
ANCHOR_SOURCE = "tav2_bq.ticker.Price (giá thô, chưa điều chỉnh cổ tức)"


def _bq(sql):
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
         f"--max_rows={BQ_MAX_ROWS}", "--format=json", sql],
        capture_output=True, text=True, timeout=BQ_TIMEOUT_S)
    if out.returncode != 0:
        raise RuntimeError(f"bq query failed: {out.stderr.strip()[:400]}")
    body = out.stdout.strip()
    i = body.find("[")
    rows = json.loads(body[i:]) if i >= 0 else []
    if len(rows) >= BQ_MAX_ROWS:
        raise RuntimeError(f"bq chạm trần {BQ_MAX_ROWS} dòng — gần như chắc chắn bị CẮT")
    return rows


def market_last_session_before(plan_date):
    """→ (phiên gần nhất TRƯỚC plan_date, phiên mới nhất BQ có) theo lịch của chính BQ.

    Dùng VNINDEX chứ không dùng mã bất kỳ: một mã lẻ có thể nghỉ giao dịch/bị đình chỉ nên
    "phiên gần nhất của mã" không chứng minh được thị trường đã có phiên đó.

    Trả cả `bq_max` vì nó là thứ DUY NHẤT phân biệt được hai tình huống trông giống hệt nhau
    ở đầu ra: (a) BQ đã nạp đủ, phiên liền trước là thật; (b) BQ CHƯA nạp tới plan_date, nên
    "phiên liền trước" thật ra là một phiên cũ — và lúc đó MỌI mã đều khớp với nó, khiến phép
    so mã-với-thị-trường không phát hiện được gì. Xem cổng tuổi anchor trong main()."""
    rows = _bq(f"""
        SELECT CAST(MAX(IF(t.time < DATE '{plan_date}', t.time, NULL)) AS STRING) AS d_before,
               CAST(MAX(t.time) AS STRING) AS d_max
        FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
        WHERE t.ticker = 'VNINDEX'
    """)
    r = rows[0] if rows else {}
    b, m = r.get("d_before"), r.get("d_max")
    return (b[:10] if b else None), (m[:10] if m else None)


def fetch_prev_session_prices(tickers, plan_date):
    """{ticker: (price_vnd, 'YYYY-MM-DD')} — phiên ĐÃ ĐÓNG gần nhất TRƯỚC plan_date.

    Mã không có dữ liệu thì VẮNG MẶT (caller coi là loại, không suy diễn giá thay thế)."""
    tks = sorted({str(t).strip().upper() for t in tickers if str(t).strip()})
    if not tks:
        return {}
    inlist = ",".join(f"'{t}'" for t in tks)
    rows = _bq(f"""
        WITH last_px AS (
          SELECT t.ticker AS tk, t.time AS d, t.Price AS px,
                 ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) AS rn
          FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
          WHERE t.ticker IN ({inlist})
            AND t.time < DATE '{plan_date}'
            AND t.time >= DATE_SUB(DATE '{plan_date}', INTERVAL 60 DAY)
            AND t.Price > 0
        )
        SELECT tk, CAST(d AS STRING) AS d, px FROM last_px WHERE rn = 1
    """)
    return {r["tk"]: (float(r["px"]), r["d"][:10]) for r in rows}


def main():
    ap = argparse.ArgumentParser(description="Trần giá mua luật A cho lệnh LAG entry-window.")
    ap.add_argument("--plan-date", required=True, help="ngày THỰC THI của plan (YYYY-MM-DD)")
    ap.add_argument("--tickers", help="danh sách mã, phân tách bằng dấu phẩy")
    ap.add_argument("--plan", help="file plan JSON — tự lấy đúng lệnh TRONG PHẠM VI")
    ap.add_argument("--tau", type=float, default=RULE_A_TAU_DEFAULT,
                    help=f"mặc định {RULE_A_TAU_DEFAULT} (user chốt); trần cứng {RULE_A_TAU_MAX}")
    ap.add_argument("--allow-stale-anchor", action="store_true",
                    help="cho phép anchor CŨ HƠN phiên liền trước (mặc định TỪ CHỐI)")
    ap.add_argument("--max-anchor-age-days", type=int, default=4,
                    help="tuổi anchor tối đa tính bằng NGÀY LỊCH so với plan_date (mặc định 4: "
                         "đủ cho T6→T2 = 3 ngày, cộng 1 ngày lễ; nghỉ dài hơn phải khai "
                         "--allow-stale-anchor một cách có ý thức)")
    ap.add_argument("--apply", action="store_true",
                    help="ghi 5 field trần vào chính file --plan (mặc định chỉ IN RA)")
    a = ap.parse_args()

    try:
        dt.date.fromisoformat(a.plan_date)
    except ValueError:
        print(f"plan-date không hợp lệ: {a.plan_date!r}", file=sys.stderr)
        return 2
    if not (0 < a.tau <= RULE_A_TAU_MAX):
        print(f"tau={a.tau} ngoài (0, {RULE_A_TAU_MAX}] — τ lớn hơn thế là bỏ trần, "
              f"không phải 'nới trần'.", file=sys.stderr)
        return 2

    orders, plan_obj = [], None
    if a.plan:
        with open(a.plan, encoding="utf-8") as f:
            plan_obj = json.load(f)
        if plan_obj.get("plan_date") != a.plan_date:
            print(f"plan_date trong file ({plan_obj.get('plan_date')}) ≠ --plan-date "
                  f"({a.plan_date}) — dừng, không đoán.", file=sys.stderr)
            return 2
        orders = plan_obj.get("orders", [])
    elif a.tickers:
        orders = [{"side": "buy", "ticker": t.strip().upper(), "book": "LAG",
                   "entry_anchor_price": 1.0}          # giữ chỗ: chỉ để lọt cổng phạm vi
                  for t in a.tickers.split(",") if t.strip()]
    else:
        print("cần --tickers hoặc --plan", file=sys.stderr)
        return 2

    scope = [o for o in orders
             if str(o.get("side") or "").lower() == "buy" and o.get("entry_anchor_price")
             and str(o.get("book") or "") != "DISCRETIONARY_SPECIAL"]
    if not scope:
        print(json.dumps({"ok": True, "n_in_scope": 0,
                          "note": "không lệnh nào trong phạm vi Rule A (cần side=buy + "
                                  "entry_anchor_price + book ≠ DISCRETIONARY_SPECIAL)"},
                         ensure_ascii=False, indent=2))
        return 0

    try:
        want_date, bq_max = market_last_session_before(a.plan_date)
        px = fetch_prev_session_prices([o["ticker"] for o in scope], a.plan_date)
    except Exception as exc:                                    # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    # CỔNG TUỔI ANCHOR — phải chạy TRƯỚC vòng so từng mã. Nếu BQ chưa nạp tới plan_date thì
    # `want_date` tự nó đã cũ, và mọi mã sẽ khớp với nó ⇒ phép so mã-với-thị-trường mù hoàn
    # toàn. Đây là ca THẬT của giờ lập plan (~19-21h ICT): bảng BQ có thể chưa có phiên hôm nay.
    anchors, skipped = {}, []
    age_days = None
    if want_date:
        age_days = (dt.date.fromisoformat(a.plan_date)
                    - dt.date.fromisoformat(want_date)).days
    if want_date is None or (age_days > a.max_anchor_age_days and not a.allow_stale_anchor):
        print(json.dumps({
            "ok": False, "plan_date": a.plan_date, "n_applied": 0,
            "phien_lien_truoc_theo_BQ": want_date, "bq_max_date": bq_max,
            "anchor_age_days": age_days,
            "error": (f"phiên gần nhất BQ có trước plan_date là {want_date} — cách "
                      f"{age_days} ngày lịch (trần {a.max_anchor_age_days}). Gần như chắc chắn "
                      f"BQ CHƯA nạp xong phiên gần đây. KHÔNG sinh trần Rule A: trần cũ hơn thì "
                      f"AN TOÀN nhưng làm hỏng đúng cơ chế này sinh ra để chữa, và không ai "
                      f"thấy. Dùng --allow-stale-anchor nếu cố ý (vd nghỉ Tết dài)."
                      if want_date else "BQ không có phiên nào trước plan_date"),
        }, ensure_ascii=False, indent=2))
        return 1

    for o in scope:
        tk = o["ticker"]
        got = px.get(tk)
        if not got:
            skipped.append(f"{tk}: không có phiên nào trong 60 ngày trước {a.plan_date}")
            continue
        p, d = got
        if want_date and d != want_date and not a.allow_stale_anchor:
            skipped.append(f"{tk}: anchor {d} KHÔNG phải phiên liền trước ({want_date}) — "
                           f"BQ chưa nạp xong hoặc mã nghỉ giao dịch. TỪ CHỐI (dùng "
                           f"--allow-stale-anchor nếu cố ý chấp nhận trần cũ hơn).")
            continue
        anchors[tk] = (p, d)

    n, notes = apply_rule_a(scope, anchors, tau=a.tau)

    out = []
    for o in scope:
        if o.get("ceiling_rule") != "A":
            continue
        # Đối soát bằng CHÍNH hàm mà load_plan() sẽ chạy — nếu ở đây đã không tái lập được thì
        # plan sẽ fail-safe về luật cũ lúc nạp, và tốt hơn là biết ngay bây giờ.
        ceil, info = resolve_buy_ceiling(o, plan_date=a.plan_date)
        out.append({
            "ticker": o["ticker"],
            "hard_no_chase_ceiling_vnd": o["hard_no_chase_ceiling_vnd"],
            "ceiling_rule": "A",
            "ceiling_anchor_price": o["ceiling_anchor_price"],
            "ceiling_anchor_date": o["ceiling_anchor_date"],
            "ceiling_tau": o["ceiling_tau"],
            "entry_anchor_price_cu": o.get("entry_anchor_price"),
            "load_plan_se_dung": ceil, "load_plan_mode": info.get("mode"),
            # executor tính `cap = ref_price × (1+chase%)` TRƯỚC khi min với trần cứng, mà
            # chase = clamp(2×rvol20d, 1,5%, 4%). Để ref_price cũ (= anchor entry cũ) thì cap
            # đó thành ràng buộc BUỘC và phần lớn tác dụng của Rule A bốc hơi — đúng cơ chế đã
            # ghi trong resolve_price_band() của discretionary_accumulation.py.
            "ref_price_de_xuat": o["hard_no_chase_ceiling_vnd"],
            "ref_price_ghi_chu": ("đặt ref_price = trần để trần đuổi % không cắt trước; qty "
                                  "phải re-derive theo ref_price mới — SIZING là quyết định "
                                  "của DollarBill/user, công cụ này không tự tính lại."),
        })

    if a.apply:
        if plan_obj is None:
            print("[APPLY] bỏ qua — --apply chỉ có nghĩa cùng --plan.", file=sys.stderr)
        elif n == 0:
            print("[APPLY] bỏ qua — 0 lệnh gắn được Rule A, không ghi đè plan.", file=sys.stderr)
        else:
            # `scope` giữ CHÍNH các dict trong plan_obj["orders"] (lọc theo tham chiếu), nên
            # apply_rule_a() đã sửa tại chỗ — ghi lại là đủ. KHÔNG đụng qty/ref_price/
            # approved_by/nav_basis: sizing và duyệt là việc của DollarBill/user.
            with open(a.plan, "w", encoding="utf-8") as f:
                json.dump(plan_obj, f, indent=2, ensure_ascii=False)
            print(f"[APPLY] ghi {n} lệnh vào {a.plan} — chỉ 5 field trần, "
                  f"KHÔNG đụng qty/ref_price/approved_by.", file=sys.stderr)

    print(json.dumps({
        "ok": True, "plan_date": a.plan_date, "tau": a.tau,
        "phien_lien_truoc_theo_BQ": want_date, "bq_max_date": bq_max,
        "anchor_age_days": age_days, "source": ANCHOR_SOURCE,
        "n_in_scope": len(scope), "n_applied": n,
        "orders": out, "skipped": skipped, "notes": notes,
        "canh_bao": ("Đây là lựa chọn CHÍNH SÁCH (chấp nhận trả thêm ~16 bps để cắt rủi ro kẹt "
                     "hoàn toàn), KHÔNG phải edge đã kiểm chứng. Cần user duyệt plan như mọi "
                     "plan LIVE khác."),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

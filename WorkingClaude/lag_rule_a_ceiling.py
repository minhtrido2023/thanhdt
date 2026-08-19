#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh trần giá mua LUẬT A cho lệnh LAG entry-window — CHẠY 1 LẦN LÚC LẬP PLAN.

⚠️ CHỈ ĐỌC. Không đặt lệnh, không ghi plan, không sửa file nào trừ khi có `--apply <plan.json>`
(và ngay cả khi đó cũng chỉ sửa 7 field trần của đúng lệnh trong phạm vi).

Luật A (user chốt 2026-08-15, bus `ceiling-rule-AB-user-decision-CORRECTED`):
    hard_no_chase_ceiling_vnd = GIÁ THAM CHIẾU CHÍNH THỨC của phiên `plan_date` × (1 + 3%)

Đây là **lựa chọn CHÍNH SÁCH** — trả thêm ~16 bps trung bình để cắt rủi ro kẹt hoàn toàn khi
giá chạy — **KHÔNG phải một cải tiến có bằng chứng**. Trên implementation shortfall, chênh lệch
A−B không có ý nghĩa thống kê và đổi dấu theo giả định. Xem `trading_bot/no_chase_ceiling.py`
và `mike/agents/Taylor/research/ceiling_ab_pacing_20260814/README.md`.

🔴 SỬA LỖI 2026-08-15 (job Taylor_20260815_034407) — ANCHOR ĐỔI NGUỒN. Bản trước lấy anchor =
`tav2_bq.ticker.Price` phiên đã đóng gần nhất = **giá đóng cửa**. Đó KHÔNG phải "giá tham
chiếu", và hai thứ chỉ trùng nhau ở HOSE/HNX trong ngày thường:
 · **UPCOM**: giá tham chiếu = BÌNH QUÂN GIA QUYỀN giá khớp lô chẵn phiên trước. Đo 12 tháng,
   N=1.618 phiên-mã: median lệch 0,361%, p90 1,271%, **1,2% số phiên lệch hơn CẢ τ=3%**.
   DRI/SCL/TV1 — 3/5 mã từng dùng cơ chế này — đều là UPCOM.
 · **Mọi sàn, ngày GDKHQ**: giá tham chiếu ĐÃ ĐIỀU CHỈNH theo giá trị quyền. Ca thật SSI
   ex-right 2026-08-17: tham chiếu 19.600đ vs giá đóng 24.500đ ⇒ trần cũ 25.235đ **cao hơn cả
   GIÁ TRẦN hợp lệ của phiên (20.972đ)** ⇒ luật A vô hiệu hoàn toàn, im lặng.
Bằng chứng + cách tái lập: `mike/agents/Taylor/research/upcom_ref_anchor_20260815/`.

BỐN QUYẾT ĐỊNH DỮ LIỆU (nêu tường minh — đừng chọn ngầm, đừng đảo lại):
 1. **Anchor = DNSE live `q.ref`** (secdef `refPrice`/`basicPrice`) cho MỌI sàn. Đây là con số
    do chính sở giao dịch công bố ⇒ đã đúng công thức riêng của từng sàn VÀ đã điều chỉnh
    quyền, không phải tự tính lại. Đã đối soát cơ chế: dựng lại bình quân gia quyền từ bar 1
    phút nguồn VCI (đường dữ liệu độc lập) trùng `q.ref` **6/7 mã UPCOM tới TỪNG TICK**.
 2. **KHÔNG có nguồn thay thế trong BQ** — đã kiểm `INFORMATION_SCHEMA`, không cột nào mang giá
    tham chiếu/sàn/trần-sàn; `Trading_Value / Volume == Close` tuyệt đối 24/24 dòng ⇒ cột phái
    sinh, không phải giá trị khớp thật. Vì `q.ref` chỉ đọc được SỐNG, công cụ này **chỉ chạy
    được cho phiên giao dịch KẾ TIẾP**, không hồi quy lịch sử được (cổng ở `main()`).
 3. BQ giữ vai trò **kiểm chéo, không phải nguồn**: `Low/High` phiên đã đóng gần nhất để khoá
    bất biến "tham chiếu ∈ biên giá phiên trước" (cổng G3), và lịch phiên (VNINDEX) để biết
    phiên liền trước là ngày nào. Đọc thẳng bảng, KHÔNG qua `data/bq_cache` (sự cố 2026-07-09).
 4. **Sàn suy từ DNSE `marketId`** (STO/STX/UPX), KHÔNG từ `Quote.exchange` — trường đó mặc
    định "HOSE" khi feed câm nên fail-OPEN (đo 43/43 mã đều ra "HOSE" trước bản vá).

CỔNG TƯƠI (mặc định BẬT, `--allow-stale-anchor` để tắt): anchor phải đúng bằng phiên giao dịch
liền trước `plan_date` theo lịch của chính BQ (VNINDEX). Nếu bảng BQ chưa nạp phiên hôm nay lúc
lập plan (~19-21h ICT), công cụ **KHÔNG in trần** thay vì im lặng dùng giá phiên cũ hơn — trần cũ
hơn thì AN TOÀN (chặt hơn) nhưng làm hỏng đúng cái cơ chế này sinh ra để chữa, và không ai thấy.

    python3 lag_rule_a_ceiling.py --plan-date 2026-08-18 --tickers DRI,POW,SCL
    python3 lag_rule_a_ceiling.py --plan-date 2026-08-18 --plan data/trade_plans/plan_SpaceX_2026-08-18.json
    ... thêm --apply để GHI 7 field trần vào chính file plan đó (in diff trước khi ghi).
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.brokers import DNSEBroker  # noqa: E402
from trading_bot.no_chase_ceiling import (  # noqa: E402
    RULE_A_TAU_DEFAULT, RULE_A_TAU_MAX, apply_rule_a, check_reference_snapshot,
    resolve_buy_ceiling)
from trading_bot.price_frame import band_tol_one_tick  # noqa: E402

BQ_PROJECT = os.environ.get("BQ_PROJECT", "lithe-record-440915-m9")
BQ_MAX_ROWS = 10_000
BQ_TIMEOUT_S = 120
ANCHOR_SOURCE = "DNSE live q.ref — giá tham chiếu CHÍNH THỨC của phiên plan_date"


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


def fetch_prev_session_range(tickers, plan_date):
    """{ticker: (low, high, close_price, 'YYYY-MM-DD')} — phiên ĐÃ ĐÓNG gần nhất TRƯỚC plan_date.

    KHÔNG phải nguồn anchor (anchor đến từ DNSE `q.ref`). Đây là **vật kiểm chéo**: giá tham
    chiếu của phiên kế tiếp phải nằm trong `[Low, High]` phiên này — bất biến đúng cho CẢ HAI
    công thức (giá đóng cửa hiển nhiên ∈ biên; bình quân gia quyền cũng ∈ biên theo cấu tạo).
    Đây là cổng DUY NHẤT bắt được snapshot `q.ref` CŨ bị phục vụ nhầm cho phiên mới.

    `Price`/`Low`/`High` là giá THÔ chưa điều chỉnh cổ tức — cùng hệ quy chiếu với giá LIVE
    trên bảng. **TUYỆT ĐỐI không `Close`** (đã điều chỉnh hồi tố; "Bẫy (2)" trong
    `kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`).

    Mã không có dữ liệu thì VẮNG MẶT (caller coi là loại, không suy diễn giá thay thế)."""
    tks = sorted({str(t).strip().upper() for t in tickers if str(t).strip()})
    if not tks:
        return {}
    inlist = ",".join(f"'{t}'" for t in tks)
    rows = _bq(f"""
        WITH last_px AS (
          SELECT t.ticker AS tk, t.time AS d, t.Low AS lo, t.High AS hi, t.Price AS px,
                 ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) AS rn
          FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
          WHERE t.ticker IN ({inlist})
            AND t.time < DATE '{plan_date}'
            AND t.time >= DATE_SUB(DATE '{plan_date}', INTERVAL 60 DAY)
            AND t.Price > 0 AND t.Low > 0 AND t.High > 0
        )
        SELECT tk, CAST(d AS STRING) AS d, lo, hi, px FROM last_px WHERE rn = 1
    """)
    return {r["tk"]: (float(r["lo"]), float(r["hi"]), float(r["px"]), r["d"][:10]) for r in rows}


def fetch_exright_on(tickers, plan_date):
    """{ticker: mô tả sự kiện} cho mã có ngày GDKHQ RƠI ĐÚNG `plan_date`.

    Vì sao phải biết: hôm đó giá tham chiếu ĐÃ ĐIỀU CHỈNH theo giá trị quyền nên **cổng G3 (∈
    biên giá phiên trước) sẽ nổ một cách ĐÚNG ĐẮN** — nếu không phân biệt được, ta sẽ đọc một
    ca hợp lệ thành lỗi feed (chính xác là cái nhãn sai mà commit `59f9569` đã gán cho SSI).

    Xử lý: **BỎ QUA luật A cho mã đó** (lệnh giữ nguyên luật trần cũ) + in cảnh báo to. Đây là
    giới hạn phạm vi CÓ CHỦ ĐÍCH chứ không phải bỏ sót: hôm GDKHQ thì `ref_price` và `qty` của
    chính lệnh đó cũng dựng trên giá/khối lượng CHƯA điều chỉnh, tức cả lệnh đáng ngờ chứ không
    riêng cái trần — sửa trần mà để nguyên sizing là vá nửa vời. Việc còn lại: xem README §4.

    Lỗi tra bảng ⇒ ném lên (fail-closed): không biết có sự kiện quyền hay không thì không được
    phép gắn trần."""
    tks = sorted({str(t).strip().upper() for t in tickers if str(t).strip()})
    if not tks:
        return {}
    inlist = ",".join(f"'{t}'" for t in tks)
    rows = _bq(f"""
        SELECT ca.ticker AS tk, ca.event_title_vi AS title
        FROM `{BQ_PROJECT}.tav2_bq.corporate_action` AS ca
        WHERE ca.ticker IN ({inlist}) AND ca.exright_date = DATE '{plan_date}'
    """)
    out = {}
    for r in rows:
        out.setdefault(r["tk"], []).append(str(r.get("title") or "?"))
    return {k: " | ".join(v) for k, v in out.items()}


def fetch_live_reference(tickers):
    """{ticker: dict} — snapshot giá tham chiếu SỐNG từ DNSE, kèm sàn và biên độ.

    `quote_only=True`: chỉ market-data, KHÔNG đăng nhập tài khoản giao dịch, không đặt được
    lệnh. Sàn lấy từ `q.market_id` (STO/STX/UPX) qua `Quote.exchange`/`exchange_known` — KHÔNG
    tin nhánh mặc định "HOSE" (xem docstring đầu file).

    Mã lỗi thì VẮNG MẶT khỏi kết quả (caller fail-closed), không bịa giá trị thay thế."""
    tks = sorted({str(t).strip().upper() for t in tickers if str(t).strip()})
    if not tks:
        return {}, "không có mã nào"
    b = DNSEBroker(quote_only=True).connect()
    out = {}
    for t in tks:
        try:
            q = b.get_quote(t)
        except Exception as exc:                                # noqa: BLE001
            out[t] = {"err": f"{type(exc).__name__}: {exc}"}
            continue
        out[t] = {"ref": q.ref, "ceiling": q.ceiling, "floor": q.floor, "last": q.last,
                  "exchange": q.exchange, "exchange_known": bool(q.exchange_known),
                  "market_id": q.market_id}
    return out, f"DNSE quote-only, {len(out)} mã"


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
                    help="ghi 7 field trần vào chính file --plan (mặc định chỉ IN RA)")
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
        rng = fetch_prev_session_range([o["ticker"] for o in scope], a.plan_date)
        ca = fetch_exright_on([o["ticker"] for o in scope], a.plan_date)
        live, live_note = fetch_live_reference([o["ticker"] for o in scope])
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

    # CỔNG "CHỈ PHIÊN KẾ TIẾP" — mới, và là hệ quả BẮT BUỘC của việc anchor đổi sang nguồn SỐNG.
    # `q.ref` chỉ tồn tại cho phiên giao dịch kế tiếp; không có endpoint lấy lịch sử đại lượng
    # này (đã kiểm, xem docstring đầu file). Chạy công cụ cho một plan_date quá khứ sẽ lấy tham
    # chiếu của HÔM NAY gắn cho một phiên đã qua — sai im lặng, đúng loại lỗi đang sửa.
    if bq_max != want_date and not a.allow_stale_anchor:
        print(json.dumps({
            "ok": False, "plan_date": a.plan_date, "n_applied": 0,
            "phien_lien_truoc_theo_BQ": want_date, "bq_max_date": bq_max,
            "error": (f"BQ đã có phiên {bq_max} SAU phiên liền trước plan_date ({want_date}) ⇒ "
                      f"{a.plan_date} KHÔNG phải phiên giao dịch kế tiếp. Anchor luật A nay là "
                      f"GIÁ THAM CHIẾU SỐNG (DNSE q.ref), chỉ đúng cho phiên kế tiếp — chạy cho "
                      f"ngày quá khứ sẽ gắn tham chiếu hôm nay vào một phiên đã qua."),
        }, ensure_ascii=False, indent=2))
        return 1

    for o in scope:
        tk = o["ticker"]
        got_rng, q = rng.get(tk), live.get(tk) or {}
        if q.get("err"):
            skipped.append(f"{tk}: DNSE không trả quote ({q['err']}) — FAIL-CLOSED, không gắn trần")
            continue
        if not got_rng:
            skipped.append(f"{tk}: không có phiên nào trong 60 ngày trước {a.plan_date}")
            continue
        lo, hi, _px, d = got_rng
        if d != want_date and not a.allow_stale_anchor:
            skipped.append(f"{tk}: phiên đối chiếu {d} KHÔNG phải phiên liền trước ({want_date}) "
                           f"— BQ chưa nạp xong hoặc mã nghỉ giao dịch. TỪ CHỐI.")
            continue
        # Ngày GDKHQ: tham chiếu ĐÃ điều chỉnh nên NẰM NGOÀI [Low, High] phiên trước một cách
        # HỢP LỆ ⇒ cổng G3 mất hiệu lực. Bỏ qua luật A cho mã đó (xem `fetch_exright_on`).
        if tk in ca:
            skipped.append(f"{tk}: ⚠️ GDKHQ ĐÚNG NGÀY {a.plan_date} ({ca[tk]}) — BỎ QUA luật A. "
                           f"Tham chiếu đã điều chỉnh nên không đối chiếu được với biên giá phiên "
                           f"trước, VÀ ref_price/qty của chính lệnh cũng dựng trên giá chưa điều "
                           f"chỉnh ⇒ cả lệnh cần người xem lại, không riêng cái trần.")
            continue
        ok, ginfo = check_reference_snapshot(
            q.get("ref"), q.get("ceiling"), q.get("floor"),
            q.get("exchange"), q.get("exchange_known"), prev_low=lo, prev_high=hi,
            band_tol=band_tol_one_tick(q.get("ref"), exchange=q.get("exchange") or "HOSE"))
        if not ok:
            skipped.append(f"{tk}: [{ginfo.get('gate')}] {ginfo.get('reason')}")
            continue
        # `anchor_date` = phiên SINH RA tham chiếu (phiên đã đóng gần nhất) — giữ nguyên bất
        # biến #4 "trần chỉ neo vào phiên ĐÃ ĐÓNG trước ngày thực thi".
        anchors[tk] = (float(q["ref"]), d, str(q.get("exchange")).strip().upper())

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
            "ceiling_anchor_basis": o["ceiling_anchor_basis"],
            "ceiling_exchange": o["ceiling_exchange"],
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
            print(f"[APPLY] ghi {n} lệnh vào {a.plan} — chỉ 7 field trần, "
                  f"KHÔNG đụng qty/ref_price/approved_by.", file=sys.stderr)

    print(json.dumps({
        "ok": True, "plan_date": a.plan_date, "tau": a.tau,
        "phien_lien_truoc_theo_BQ": want_date, "bq_max_date": bq_max,
        "anchor_age_days": age_days, "source": ANCHOR_SOURCE,
        "n_in_scope": len(scope), "n_applied": n, "live_ref_source": live_note,
        "exright_dung_ngay_plan_date": ca,
        "orders": out, "skipped": skipped, "notes": notes,
        "canh_bao": ("Đây là lựa chọn CHÍNH SÁCH (chấp nhận trả thêm ~16 bps để cắt rủi ro kẹt "
                     "hoàn toàn), KHÔNG phải edge đã kiểm chứng. Cần user duyệt plan như mọi "
                     "plan LIVE khác."),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

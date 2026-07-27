# -*- coding: utf-8 -*-
"""Reconciliation POST-FILL cho netting lệnh ngược chiều cùng mã (`net_offsetting_orders`).

BỐI CẢNH — killer objection của quant-skeptic (job Taylor_20260727_040719):
`net_offsetting_orders()` gộp SELL 800 park + BUY 700 LAG → 1 lệnh NET SELL 100 ra broker.
Broker chỉ thấy −100; câu hỏi: phần chuyển nội bộ (park −700 / LAG +700) có được ghi đúng
vào sổ từng book, và sổ từng book có lệch khỏi broker theo thời gian không?

ĐIỀU MODULE NÀY *KHÔNG* LÀM (và VÌ SAO — đã xác minh trên code hiện có, 2026-07-27):
- KHÔNG đồng bộ một "sổ vị thế từng book" — vì **ở live KHÔNG tồn tại sổ như vậy**:
  * Journal FILL (`executor._journal`) book-agnostic: cột ts/event/parent_id/ticker/side/
    child_oid/qty/price/filled_total/note — không có `book`.
  * Tầng kế toán/NAV (`daily_nav_snapshot.py`, `compute_active_nav.py`, `reconcile_equity.py`)
    book-agnostic: NAV = mtm_stock(TỔNG broker) + cash − margin_debt + offbook. Mọi lần khớp
    chữ "book" trong các file đó thực ra là "off-book" (Trứng vàng), không phải per-book.
  * Vị thế "từng book" chỉ tồn tại dưới 2 dạng, cả 2 KHÔNG tích luỹ từ fill:
      (a) paper-mirror `pt_v22_dt5g_open_positions.csv` — do engine mô phỏng (pt_v4_dt5g.py…)
          ghi, TÁI DỰNG + scale theo NAV MỖI ngày rồi diff vs vị thế TỔNG thật của broker.
      (b) field `book` trên PlannedOrder — chỉ để routing tier sizing, khoá trần %ADV
          (cap_capit/cap_lag), và hiển thị. Vòng đời = 1 plan, không phải sổ bền.
  * DollarBill lập plan T+1 tái dựng từ recommend CSV + vị thế TỔNG thật + active_nav —
    KHÔNG đọc sổ per-book bền nào.
  ⇒ Không có sổ tích-luỹ-từ-fill nào để "lệch". Bất biến bảo toàn của netting
    (net = Σqty_buy − Σqty_sell = TỔNG các Δ per-book dự kiến — đã test case E của
    net_offsetting_orders_selfcheck) đảm bảo vị thế TỔNG broker luôn kết thúc đúng bằng
    tổng-các-book dự kiến; và target per-book ngày mai tái dựng từ (paper-mirror) −
    (vị thế TỔNG broker), tự hấp thụ cả khớp một phần. Netting trong suốt với bước này.
  * Khớp MỘT PHẦN khiến việc "chẻ fill về từng book" không định nghĩa được (một phần của
    NET SELL 100 không tách lại thành park-trim-800 vs LAG-entry-700 riêng) — thêm một lý
    do nữa vì sao sổ per-book-từ-fill vừa không tồn tại vừa không nên bịa ra.

ĐIỀU MODULE NÀY LÀM (phần lõi HỢP LỆ, ĐỊNH NGHĨA ĐƯỢC của objection, chạy SAU khi có FILL
THẬT — không phải lúc sinh plan, vì cần giá/khối lượng khớp thật):
1. Audit-trail: với mỗi mã đã netted, ghi lại HAI leg gốc (buy_legs/sell_legs: book+qty)
   ĐỊNH GIÁ CÙNG MỘT giá — với NET≠0 là giá khớp THẬT của lệnh net; với NET=0 (100% nội bộ,
   KHÔNG có lệnh net nên KHÔNG có giá khớp) là ref_price của plan (một giá nhất quán ⇒ 2 leg
   nội bộ bù trừ nhau, P&L gộp = 0 dù giá là gì). Nhờ đó mọi báo cáo per-book tương lai tái
   dựng được cả 2 leg ở CÙNG một giá thật (objection #1/#2/#3).
2. Conservation guard FAIL-LOUD (objection #4, dạng định nghĩa-được): phần THẬT chạm broker
   (khớp có dấu của lệnh net) PHẢI bằng Σ các Δ book chạm-thị-trường; và nếu caller cấp
   `broker_net_delta` (thay đổi vị thế sở hữu THẬT đọc từ positions API), phải khớp — lệch =
   raise + để caller báo Mike/user, KHÔNG tự suy đoán gộp lại (coding_guidelines §5/§6).

WIRED LIVE (2026-07-27, job Taylor_20260727_063826): `bot_execute.py::_reconcile_net_fills`
gọi hàm này SAU khi `run_session` trả về (phiên đóng, fills đã chốt). Giá khớp thật đọc qua
`get_net_fill_from_journal(executor.journal_file, ...)` — parent `NET-<ticker>-<SIDE>`, lấy
avg_price broker từ cột `price` của dòng FILL journal, KHÔNG từ giá đặt lệnh `c["price"]` (§6).
records → JSONL audit (`netting_recon_<account>_<date>.jsonl`); failures → BÁO LOUD (bus error
NETTING_RECON_FAIL + Discord + Telegram) và exit ≠ 0, KHÔNG tự gộp.
"""

import csv
import json
import os


def get_net_fill_from_journal(journal_file, ticker, net_side):
    """(filled_qty, avg_price) của lệnh net (parent `NET-<ticker>-<SIDE>`) đọc từ journal FILL.

    NGUỒN GIÁ = cột `price` của các dòng FILL trong journal executor — chính là
    `u.avg_price or c["price"]` mà executor._sync_fills ghi, tức GIÁ KHỚP THẬT từ broker
    (avg_price), KHÔNG phải giá đặt lệnh trong plan (coding_guidelines §6). Đây là điểm
    quant-skeptic nhấn mạnh phải chứng minh bằng self-check tích hợp: giá lấy từ journal
    FILL, không phải c["price"] lúc lập plan.

    Journal (executor.py) là CSV có header: ts,event,parent_id,ticker,side,child_oid,qty,
    price,filled_total,note. Mỗi dòng FILL ghi qty = filled TÍCH LUỸ của child đó và price =
    avg_price broker của child đó; một child có thể có nhiều dòng FILL khi khớp tăng dần
    (dòng sau ghi đè cumulative của dòng trước). Vì vậy: gom theo child_oid lấy DÒNG CUỐI
    (append order = thời gian tăng → cumulative lớn nhất), tổng qty các child = filled của
    lệnh net, avg_price = bình quân gia quyền theo qty của giá từng child.

    Trả (0, None) nếu không có journal / không có dòng FILL nào cho parent này.
    """
    net_id = "NET-%s-%s" % (ticker, (net_side or "").upper())
    if not journal_file or not os.path.exists(journal_file):
        return 0, None
    per_child = {}   # child_oid -> (cum_filled, avg_price); append order → dòng cuối thắng
    with open(journal_file, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL" or row.get("parent_id") != net_id:
                continue
            try:
                q = int(round(float(row.get("qty") or 0)))
            except (TypeError, ValueError):
                continue
            raw_px = row.get("price")
            try:
                px = float(raw_px) if raw_px not in (None, "") else None
            except (TypeError, ValueError):
                px = None
            per_child[row.get("child_oid") or ""] = (q, px)
    if not per_child:
        return 0, None
    total = sum(q for q, _ in per_child.values())
    num = sum(q * px for q, px in per_child.values() if px is not None and q > 0)
    den = sum(q for q, px in per_child.values() if px is not None and q > 0)
    avg = (num / den) if den > 0 else None
    return total, avg


def reconcile_netted_fills(adj, get_net_fill, ref_price_of, broker_net_delta=None):
    """Đối soát post-fill cho danh sách `adj` do `net_offsetting_orders` trả về.

    Tham số:
    - adj: list dict (mỗi mã netted) — action INTERNAL_ONLY | NETTED, kèm total_buy/total_sell/
      net_qty/internal_qty/buy_legs/sell_legs/net_side.
    - get_net_fill(ticker, net_side) -> (filled_qty:int, avg_price:float|None): khối lượng &
      GIÁ KHỚP THẬT của lệnh net (parent NET-<ticker>-<SIDE>). Nguồn phải là xác nhận khớp
      broker / journal FILL (avg_price), KHÔNG phải giá đặt lệnh. (0, None) nếu không khớp gì.
    - ref_price_of(ticker) -> float|None: giá tham chiếu plan cho mã (dùng định giá 2 leg khi
      NET=0 — không có lệnh net nên không có giá khớp).
    - broker_net_delta: dict|None {ticker: signed_int} — thay đổi vị thế SỞ HỮU thật của mã
      (đọc positions API, sau − trước). Nếu cấp → cross-check cứng (objection #4 dạng mạnh).

    Trả (records, failures):
    - records: list dict audit (đủ 2 leg @ 1 giá, net_to_broker có dấu, giá dùng, nguồn giá).
    - failures: list dict {ticker, reason} — RỖNG nghĩa là sạch. Caller PHẢI fail-loud khi
      non-empty (raise + bus event + báo Mike/user), không tự gộp.
    """
    records, failures = [], []

    for rec in adj:
        tk = rec["ticker"]
        action = rec.get("action")
        tb, ts = rec["total_buy"], rec["total_sell"]
        net_qty = rec["net_qty"]
        internal = rec["internal_qty"]

        # (i) Internal-consistency của chính adj (chống adj hỏng/bị sửa tay).
        if tb - ts != net_qty:
            failures.append({"ticker": tk, "reason": (
                f"adj hỏng: total_buy({tb}) − total_sell({ts}) = {tb - ts} ≠ net_qty({net_qty})")})
            continue

        bdelta = None if broker_net_delta is None else broker_net_delta.get(tk, 0)

        if action == "INTERNAL_ONLY":
            # NET=0: không có lệnh net → không có giá khớp → định giá 2 leg @ ref_price.
            if net_qty != 0:
                failures.append({"ticker": tk, "reason": (
                    f"INTERNAL_ONLY nhưng net_qty={net_qty}≠0 — adj không nhất quán")})
                continue
            px = ref_price_of(tk)
            if px is None:
                # objection: "FAIL LOUD khi giá khớp không lấy được" — với NET=0 giá đó là ref.
                failures.append({"ticker": tk, "reason": (
                    "NET=0 (100% nội bộ) nhưng KHÔNG lấy được giá tham chiếu để định giá "
                    "chuyển nội bộ — không ghi audit với giá bịa")})
                continue
            # Không lệnh nào ra broker ⇒ vị thế sở hữu KHÔNG được đổi bởi plan này.
            if bdelta not in (None, 0):
                failures.append({"ticker": tk, "reason": (
                    f"NET=0 (0 lệnh ra broker) nhưng vị thế broker đổi {bdelta:+d}cp — "
                    f"bất nhất (ghost/nguồn khác?), cần người kiểm tra")})
                continue
            records.append(_mk_record(rec, price=px, price_src="ref_price (NET=0, no market leg)",
                                      net_to_broker=0))
            continue

        if action == "NETTED":
            filled, px = get_net_fill(tk, rec["net_side"])
            signed = filled if rec["net_side"] == "buy" else -filled
            # (ii) Khớp không được vượt số lượng net đã gửi (bất khả nếu executor đúng).
            if filled < 0 or filled > abs(net_qty):
                failures.append({"ticker": tk, "reason": (
                    f"khớp lệnh net = {filled}cp ngoài [0, |net_qty|={abs(net_qty)}] — bất khả, "
                    f"executor/nguồn fill sai")})
                continue
            # (iv) Có khớp mà không lấy được giá khớp thật → FAIL LOUD (objection #3).
            if filled > 0 and px is None:
                failures.append({"ticker": tk, "reason": (
                    f"lệnh net khớp {filled}cp nhưng KHÔNG lấy được giá khớp thật (avg_price) — "
                    f"không định giá 2 leg bằng giá bịa; kiểm tra xác nhận khớp broker")})
                continue
            # filled==0: lệnh net đặt nhưng chưa khớp cp nào → phần nội bộ vẫn là bút toán hợp
            # lệ (0 chạm thị trường). Định giá @ ref cho nhất quán; net_to_broker=0.
            if filled == 0:
                px = ref_price_of(tk)
                if px is None:
                    failures.append({"ticker": tk, "reason": (
                        "lệnh net khớp 0cp và không có ref_price để định giá chuyển nội bộ")})
                    continue
                price_src = "ref_price (net order 0-filled)"
            else:
                price_src = "avg_price khớp thật của lệnh net"
            # (iii) Cross-check cứng vs vị thế sở hữu thật (objection #4 dạng mạnh).
            if bdelta is not None and bdelta != signed:
                failures.append({"ticker": tk, "reason": (
                    f"phần chạm broker theo fill = {signed:+d}cp ≠ thay đổi vị thế sở hữu thật "
                    f"{bdelta:+d}cp — Σ(book) ≠ broker, cần người kiểm tra (không tự gộp)")})
                continue
            records.append(_mk_record(rec, price=px, price_src=price_src, net_to_broker=signed))
            continue

        failures.append({"ticker": tk, "reason": f"action lạ: {action!r}"})

    return records, failures


def _mk_record(rec, price, price_src, net_to_broker):
    """Dựng 1 record audit: 2 leg gốc @ CÙNG giá `price`, phần net chạm broker có dấu.

    Bất biến audit: Σ(qty buy) − Σ(qty sell) == net_qty (đã assert ở caller); phần nội bộ
    (internal_qty) mua/bán ở CÙNG price ⇒ bù trừ về P&L gộp; chỉ net_to_broker thật chạm TT.
    """
    return {
        "ticker": rec["ticker"],
        "action": rec["action"],
        "price": price,
        "price_source": price_src,
        "internal_qty": rec["internal_qty"],
        "net_to_broker": net_to_broker,       # có dấu: >0 mua, <0 bán, 0 nếu 100% nội bộ
        "net_side": rec.get("net_side"),
        "buy_legs": [{"book": l["book"], "qty": l["qty"], "price": price} for l in rec["buy_legs"]],
        "sell_legs": [{"book": l["book"], "qty": l["qty"], "price": price} for l in rec["sell_legs"]],
    }


def write_recon_log(records, account, plan_date, out_dir):
    """Ghi records ra JSONL audit (atomic: tmp + os.replace, coding_guidelines §5).

    Append-only theo (account, plan_date). Trả path. records rỗng → không ghi, trả None.
    """
    if not records:
        return None
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"netting_recon_{account}_{plan_date}.jsonl")
    existing = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(existing)
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return path

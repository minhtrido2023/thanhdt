#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper_corp_action.py — áp sự kiện quyền (corp-action) vào sổ PaperBroker.

VÌ SAO TỒN TẠI
--------------
`PaperBroker` (`trading_bot/brokers.py`) giữ vị thế là một con số thuần `{mã: KL}` và tiền là
một con số thuần. Nó khớp lệnh trên QUOTE THẬT — nghĩa là sáng ngày GDKHQ, giá nó nhìn thấy đã
rơi về hệ quy chiếu mới, trong khi KL nó đang giữ vẫn là KL hệ CŨ. Không ai bù phần chênh. Đo
trên chính sổ paper `main`: 3 sự kiện thật từ 2026-07-07 làm sổ bỏ lỡ 7.860.455đ = 0,79% NAV
(cổ tức tiền tính RÒNG sau thuế TNCN 5% — xem `DIV_TAX_RATE`; con số GỘP là 7.915.455đ).
Sổ paper là NỀN BẰNG CHỨNG của các chương trình R&D ⇒ đây là CÔNG CỤ ĐO, không chạm tiền thật,
không đi vào đường đặt lệnh.

KHÔNG VIẾT LẠI CÔNG THỨC GIÁ: ngữ nghĩa sự kiện tái dùng `corp_action_lib` (taxonomy + reader
BQ) và `trading_bot.price_frame.adjustment()` (hàm THUẦN, CỘNG tỉ lệ chứ không NHÂN, fail-closed
khi thiếu giá phát hành quyền mua).

⚠️ BẪY ĐÃ CẮN, VÒNG 1 CỦA CHÍNH FILE NÀY: `price_frame.adjustment()` trả `share_factor` — CHỈ
đúng cho MẪU SỐ GIÁ, KHÔNG phải hệ số nhân SỐ LƯỢNG
--------------------------------------------------------------------------------------------
`adjustment()` sinh ra để phục vụ cổng đối soát GIÁ THAM CHIẾU (G5). Mẫu số giá gộp MỌI tỉ lệ
làm tăng CP, kể cả QUYỀN MUA. Nhưng quyền mua **không tự động tăng số lượng** — cổ đông phải
NỘP TIỀN thì CP mới về, và về sau nhiều tuần.

Bằng chứng, 2 nguồn độc lập, đều đã có sẵn trong repo trước khi file này ra đời:
  · `data/execution_logs/dnse_raw_2026-08-1{0,1}.jsonl`, tài khoản SpaceX: MBB `openQuantity`
    1.100 (10/08) → **1.265** (11/08, 00:41:05) = ×1,15 — ĐÚNG phần cổ tức CP 15%, KHÔNG có
    10% quyền mua. Nếu quyền mua cũng tăng KL thì phải là 1.375.
  · `data/corp_actions.json`, `MBB-2026-08-11-STOCK-DIVIDEND`, `_status: CONFIRMED`:
    `qty_multiplier = 1.15`, kèm câu chữ "quyền mua KHÔNG tự động làm tăng số lượng (phải nộp
    tiền thực hiện quyền) … Đợt quyền mua CHỈ ảnh hưởng GIÁ THAM CHIẾU".

Vòng 1 file này dùng thẳng `share_factor` làm hệ số KL ⇒ MBB 1.200 → 1.500 thay vì 1.380, tức
120 CP MA, lại `sellable` ngay sáng đó (`PaperBroker.get_positions()` trả `sellable == total`),
trong khi `paper_main_probe_plan.py` đọc `positions` lúc 08:52 — 7 phút sau — để dựng lệnh.
quant-skeptic bắt được (job Taylor_20260923_005911, verdict REFUTED/high). Vì vậy ở đây TÁCH
BA tỉ lệ, đặt tên khác nhau, không dùng chung một biến:
    price_ratio   — MẪU SỐ GIÁ, gồm cả quyền mua   (của `adjustment()`, giữ nguyên)
    share_ratio   — HỆ SỐ NHÂN KL tại GDKHQ, LOẠI quyền mua
    rights_ratio  — quyền mua, đi vào `pending_rights`, KHÔNG vào `positions`

QUYỀN MUA ĐƯỢC GHI NHẬN NHƯ MỘT KHOẢN CHỜ, KHÔNG PHẢI CỔ PHIẾU
----------------------------------------------------------------
Chính sách user (2026-09-23): mặc định thực hiện 100% quyền. Nhưng "thực hiện 100%" là một
QUYẾT ĐỊNH về kinh tế, không phải về THỜI ĐIỂM: tiền ra và CP về ở ngày nộp tiền/niêm yết bổ
sung, cách GDKHQ nhiều tuần, và lịch đó KHÔNG có trong feed `tav2_bq.corporate_action`. Bịa ra
một ngày quyết toán là tự chế dữ liệu. Vì vậy tại GDKHQ ta ghi `pending_rights` gồm số CP sẽ
mua, giá phát hành, và GIÁ TRỊ NỘI TẠI `n × (P_ref − giá phát hành)` — phần giá trị này KHÔNG
biến mất khỏi sổ, nó nằm ở một trường riêng đọc được. Quyết toán là bước RIÊNG, có chủ đích
(`--settle-rights`), cần ngày thật do người cung cấp.

BẤT BIẾN BẢO TOÀN GIÁ TRỊ (`verify_invariant`):
    KL_cũ × P_cum  ==  KL_mới × P_ref + Δtiền + tiền_lẻ + giá_trị_quyền_chờ
⚠️ ĐÂY LÀ ĐỒNG NHẤT THỨC BẢO TOÀN, KHÔNG PHẢI BẰNG CHỨNG KINH TẾ. Nó đúng bằng đại số với MỌI
bộ (P_cum, tỉ lệ, cổ tức) kể cả bộ SAI — quant-skeptic đã chứng minh bằng cách tiêm cổ tức gấp
5 lần và nó vẫn cho phần dư 0,0. Giữ nó vì nó bắt được lỗi số học GIỮA các nhánh, nhưng thứ
thật sự ràng buộc KINH TẾ là NEO NGOÀI dưới đây — đừng đọc ngược hai vai này.

NEO NGOÀI (không vòng tròn) — `check_p_ref_against_close()`:
`tav2_bq.ticker.Close` của phiên cum cuối là giá đã điều chỉnh hồi tố BỞI VENDOR, tính hoàn toàn
ngoài code này ⇒ so `P_ref` tự tính với nó (dung sai 1 bước giá) là phép kiểm DUY NHẤT ràng buộc
được KINH TẾ. Đo thật 6 ca: MBB 08-11 20.200 / VHM 08-06 76.500 / DGC 09-14 38.750 khớp TUYỆT
ĐỐI; FPT 09-21 và VIB 09-10 lệch đúng 1 tick. Chính neo này bắt được con bọ ×1,25 của vòng 1
(P_ref sẽ ra 19.960đ thay vì 20.200đ).

Hai điều kiện dùng đúng, cả hai ĐO ĐƯỢC chứ không suy đoán:
  · **Chỉ neo khi mã KHÔNG còn sự kiện làm-đổi-giá nào SAU ngày GDKHQ.** `Close` mang điều chỉnh
    của MỌI sự kiện về sau, không riêng sự kiện đang xét. Ca thật: MBB@2026-07-09 có P_ref đúng
    là 25.000đ nhưng `Close(07-08)` = 20.820đ vì đã gánh thêm đợt 08-11 ⇒ neo phải TỰ BỎ QUA
    (`skipped-later-events`), không phải báo lệch.
  · **KHÔNG dùng biến thể "tỉ số hệ số" `(Close/Price)_cum ÷ (Close/Price)_ex`** để né điều kiện
    trên. Nó chạm dòng `Price` của CHÍNH ngày GDKHQ — dòng đã hỏng sẵn: VHM 2026-08-06 mang
    `Price = 153.000` (hệ CŨ, y hệt 08-05) trong khi `Close = 77.100`, và `Price` chỉ lật ở phiên
    08-07. Thử thật: biến thể này cho 151.809đ thay vì 76.500đ, sai gấp đôi. Đây đúng là "bẫy VHM
    08-06" mà docstring `price_frame` đã cảnh báo.

Neo là CỐ VẤN, KHÔNG phải cổng chặn: lệch ⇒ in cảnh báo + rc=1 (cron/escalation thấy), nhưng
bản ghi VẪN được áp. Lý do: sáng ngày GDKHQ ta không kiểm chứng được vendor đã điều chỉnh
`Close(D−1)` trong lần sync 23:45 hôm trước hay chưa, nên một neo CHẶN sẽ chặn oan; và bỏ hẳn
sự kiện chính là lỗi "mất im lặng vĩnh viễn" mà mục WATERMARK dưới đây vừa phải vá.

KHÔNG SAO CHÉP `cum_dividend_double_count` — SẼ LÀ LỖI NẾU LÀM
----------------------------------------------------------------
`daily_nav_snapshot.cum_dividend_double_count` vá một HIỆN VẬT CỦA BROKER DNSE: DNSE ghi
`cashDividendReceiving` vào `totalCash` ngay TỐI NGÀY CUỐI CÒN HƯỞNG QUYỀN trong khi giá đóng
cửa phiên đó vẫn là giá cum ⇒ NAV đếm 2 lần rồi tự triệt tiêu phiên sau. PaperBroker KHÔNG có
trường đó (`state` chỉ có `cash/positions/open_orders/fills/next_id`); tiền chỉ đổi khi có fill.
Ở đây cổ tức vào sổ ĐÚNG MỘT LẦN, tại GDKHQ, CÙNG thao tác với việc KL/giá đổi hệ quy chiếu ⇒
không-đếm-2-lần là tính chất BẰNG CẤU TRÚC. Bê logic TRỪ của live sang sẽ trừ một khoản chưa
bao giờ được cộng. (quant-skeptic đã xác nhận lập luận này đúng.)

LẺ CỔ PHIẾU: KL mới làm tròn XUỐNG; phần lẻ quy tiền theo `P_ref`. XẤP XỈ có chủ đích — thực tế
tổ chức phát hành huỷ phần lẻ hoặc mua lại theo MỆNH GIÁ (10.000đ), nên cách này hơi RỘNG TAY,
lệch một chiều ĐI LÊN, chặn trên bởi 1 giá cổ phiếu mỗi sự kiện (≈ ≤0,07%/năm trên sổ 1B). Ghi
rõ `frac_shares`/`frac_cash_vnd` từng bản ghi để hậu kiểm trừ ra được.

SỔ CÁI BỀN NGOÀI STATE: khoá idempotent nằm ở `data/paper_corp_action_ledger_<label>.jsonl`
(append-only) CHỨ KHÔNG chỉ trong state. Lý do đo được: `PaperBroker._save()` ghi ĐÈ TOÀN BỘ
state không nguyên tử ⇒ một phiên executor chạy chồng sẽ xoá sạch sổ con `corp_actions` trong
state, và lần chạy sau sẽ áp LẠI cùng sự kiện. File ngoài sống sót cú đó.

WATERMARK KHÔNG VƯỢT QUA SỰ KIỆN CÒN TREO: nếu một sự kiện bị TỪ CHỐI (thiếu giá quyền mua, BQ
hỏng, KL lệch…), watermark dừng lại TRƯỚC ngày GDKHQ của nó để lần chạy sau còn gặp lại. Vòng 1
đẩy watermark vô điều kiện ⇒ mọi đợt quyền mua tương lai (vốn LUÔN fail-closed vì
`RIGHTS_ISSUE_PRICE` chỉ có 1 khoá quá khứ) sẽ rơi ra ngoài mọi cửa sổ VĨNH VIỄN.

CHƯA XỬ LÝ (khai báo thẳng, không giấu trong code):
  · `PaperBroker.get_positions()` trả `sellable == total` cho MỌI thứ — kể cả CP thưởng/cổ tức
    CP ngày GDKHQ (broker thật giữ `tradeQuantity` = 1.100 trong khi `openQuantity` = 1.265) và
    kể cả T+2 thường. Đây là giới hạn SẴN CÓ của PaperBroker, không phải do file này gây ra;
    sửa nó là đổi `trading_bot/brokers.py` (module lõi dùng chung, §23) — việc riêng, cần duyệt.
  · Sự kiện `announced` bị HUỶ sau khi đã áp: không có đường đảo ngược tự động.

Usage:
  paper_corp_action.py [--label main] [--date YYYY-MM-DD] [--dry] [--backfill-since YYYY-MM-DD]
  paper_corp_action.py --selfcheck
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Sai số của ĐỒNG NHẤT THỨC bảo toàn, trên TOÀN CỤM. Mọi số hạng là tích số nguyên × giá VND
# nên lệch thật chỉ đến từ lỗi công thức, không từ dấu phẩy động.
INVARIANT_TOL_VND = 1.0

# Thuế TNCN cổ tức TIỀN MẶT, cá nhân cư trú. KHỚP quy ước sổ THẬT: `reconcile_equity.py`
# (`--div-tax-rate`, mặc định 0,05 → `net_cash_dividends()` trả `net = gross − paid×rate`).
# Sổ paper ghi tiền ngay ngày GDKHQ (sổ thật nhận sau vài tuần) ⇒ ở đây mọi cổ tức đều coi như
# ĐÃ CHI TRẢ, tức luôn chịu thuế — khác `net_cash_dividends()` chỗ nó tách phần còn phải thu.
# Không làm tròn: giống hệt `tax = paid * tax_rate` bên sổ thật.
DIV_TAX_RATE = 0.05

# Phương thức phát hành KHÔNG làm tăng KL tại GDKHQ (phải nộp tiền mới có CP). Nguồn chuẩn tắc
# của chuỗi này: `price_frame.RIGHTS_METHOD`, import lại chứ không chép.
def _rights_method() -> str:
    from trading_bot.price_frame import RIGHTS_METHOD
    return RIGHTS_METHOD


def now_ict() -> dt.datetime:
    return dt.datetime.now(_ICT)


def state_path(label: str) -> str:
    """Đường dẫn sổ paper — PHẢI khớp `PaperBroker.__init__`, không đoán lại."""
    from trading_bot import brokers as brk
    if label == "main":
        return brk.PAPER_STATE_FILE
    return os.path.join(brk.DATA_DIR, f"bot_paper_{label}.json")


def ledger_path(label: str) -> str:
    """Sổ cái append-only NGOÀI state — sống sót khi `PaperBroker._save()` ghi đè state."""
    from trading_bot import brokers as brk
    return os.path.join(brk.DATA_DIR, f"paper_corp_action_ledger_{label}.jsonl")


def read_external_ledger(path: str) -> list:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_external_ledger(path: str, rec: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def save_state_atomic(path: str, state: dict) -> None:
    """Ghi nguyên tử (§5): kill giữa chừng không để lại sổ paper viết dở."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def ledger(state: dict) -> dict:
    led = state.setdefault("corp_actions", {})
    led.setdefault("applied", [])
    led.setdefault("pending_rights", [])
    led.setdefault("watermark", None)
    return led


def event_key(ticker: str, ex_date: str) -> str:
    return f"{str(ticker).strip().upper()}|{str(ex_date)[:10]}"


def applied_keys(state: dict, external: list = None) -> set:
    """HỢP của sổ trong state và sổ cái ngoài — state có thể bị `PaperBroker._save()` xoá."""
    keys = {r.get("key") for r in ledger(state).get("applied", [])}
    keys |= {r.get("key") for r in (external or [])}
    return {k for k in keys if k}


# ───────────────────────────────────────────────────────────────── lõi THUẦN (không IO)

def split_ratios(events):
    """Cụm sự kiện → (price_ratio, share_ratio, rights, lý do | None). HÀM THUẦN.

    `price_ratio` = mẫu số giá của sở (gồm quyền mua) — lấy nguyên từ `adjustment()`.
    `share_ratio` = phần LÀM TĂNG KL NGAY tại GDKHQ (cổ tức CP, thưởng, tách) — LOẠI quyền mua.
    `rights`      = [(tỉ lệ, giá phát hành)] của các đợt quyền mua.
    Hai tỉ lệ này khác nhau ở đúng ca MBB 2026-08-11 (0,25 vs 0,15) — xem docstring module.
    """
    from trading_bot.price_frame import adjustment

    adj, info = adjustment(events)
    if adj is None:
        return None, None, None, info.get("reason", "adjustment() từ chối")

    rights_method = _rights_method()
    share_ratio, rights = 0.0, []
    for e in events or []:
        if str(e.get("event_code") or "").strip().upper() != "ISS":
            continue
        r = float(e.get("exercise_ratio"))
        if str(e.get("issue_method_name_vi") or "").strip() == rights_method:
            # giá phát hành: `adjustment()` đã fail-closed nếu thiếu, nên ở đây chắc chắn có
            from trading_bot.price_frame import RIGHTS_ISSUE_PRICE
            tk = str(e.get("ticker") or "").strip().upper()
            d = str(e.get("exright_date") or "")[:10]
            rights.append((r, float(RIGHTS_ISSUE_PRICE[(tk, d)])))
        else:
            share_ratio += r
    return float(adj["ratio"]), share_ratio, rights, None


def build_record(ticker, ex_date, events, qty0, p_cum, close_ref=None):
    """Một cụm sự kiện → (record | None, lý do). HÀM THUẦN — không đọc BQ, không đụng file.

    `p_cum`     = giá THÔ phiên cum cuối (trước GDKHQ).
    `close_ref` = `tav2_bq.ticker.Close` của CHÍNH phiên cum cuối (giá vendor đã điều chỉnh hồi
                  tố) — NEO NGOÀI. `None` ⇒ bỏ qua phép neo và ghi `p_ref_anchor = "skipped"`;
                  caller production PHẢI truyền vào, chỉ selfcheck offline mới được bỏ.
    Mọi nhánh không chắc chắn đều FAIL-CLOSED: trả `None` kèm lý do đọc được.
    """
    from trading_bot.price_frame import adjustment

    tk = str(ticker).strip().upper()
    if qty0 <= 0:
        return None, f"{tk}: KL = {qty0} — không giữ, bỏ qua"

    adj, info = adjustment(events)
    if adj is None:
        return None, f"{tk}@{ex_date}: {info.get('reason', 'adjustment() từ chối')}"
    price_ratio, share_ratio, rights, why = split_ratios(events)
    if price_ratio is None:
        return None, f"{tk}@{ex_date}: {why}"

    try:
        p_cum = float(p_cum)
    except (TypeError, ValueError):
        p_cum = -1.0
    if not (p_cum > 0):
        return None, (f"{tk}@{ex_date}: thiếu giá phiên cum cuối (p_cum={p_cum!r}) — không dựng "
                      f"được P_ref. FAIL-CLOSED")

    cash_ps = float(adj["cash"])              # cổ tức tiền, VND / 1 CP cũ
    rights_ps = float(adj["rights_value"])    # Σ r×giá phát hành, VND / 1 CP cũ (mẫu số giá)
    den = 1.0 + price_ratio
    num = p_cum - cash_ps + rights_ps
    if den <= 0 or num <= 0:
        return None, (f"{tk}@{ex_date}: công thức sở cho giá tham chiếu không hợp lệ "
                      f"(tử {num:,.0f}, mẫu {den})")
    p_ref = num / den

    # NEO NGOÀI = CỐ VẤN, KHÔNG PHẢI CỔNG CHẶN (xem docstring module, mục NEO NGOÀI). Lệch ⇒
    # in to + rc=1 để cron/escalation thấy, nhưng vẫn áp: giá trị được bảo toàn trong cả hai
    # trường hợp, còn BỎ HẲN sự kiện chính là lỗi "mất im lặng vĩnh viễn" vừa phải vá ở vòng 2.
    anchor = check_p_ref_against_close(p_ref, close_ref, tk)

    # ─── SỐ LƯỢNG: chỉ phần TĂNG NGAY (cổ tức CP/thưởng/tách). Quyền mua KHÔNG vào đây.
    raw_new = qty0 * (1.0 + share_ratio)
    qty_new = int(math.floor(raw_new + 1e-9))
    frac = raw_new - qty_new
    frac_cash = frac * p_ref

    # ─── TIỀN: chỉ cổ tức tiền + tiền lẻ. Tiền mua quyền CHƯA ra (nộp ở ngày quyết toán).
    # Cổ tức tiền vào sổ là RÒNG sau thuế TNCN (xem DIV_TAX_RATE). GỘP vẫn được giữ lại vì
    # đồng nhất thức bảo toàn nói về kinh tế của sự kiện (giá rơi theo cổ tức GỘP); thuế là
    # khoản chuyển RA NGOÀI hệ, phải là số hạng RIÊNG chứ không được giấu vào phần dư.
    cash_div_gross = qty0 * cash_ps
    div_tax = cash_div_gross * DIV_TAX_RATE
    cash_div_net = cash_div_gross - div_tax
    cash_delta = cash_div_net + frac_cash

    # ─── QUYỀN MUA: khoản CHỜ, có giá trị nội tại, không phải cổ phiếu.
    rights_ratio = sum(r for r, _ in (rights or []))
    pending = []
    rights_intrinsic = 0.0
    for r, px in (rights or []):
        n = qty0 * r
        intrinsic = n * (p_ref - px)
        rights_intrinsic += intrinsic
        pending.append({
            "key": event_key(tk, ex_date), "ticker": tk, "ex_date": str(ex_date)[:10],
            "shares": n, "issue_price": px, "cost_vnd": n * px,
            "p_ref_at_ex": p_ref, "intrinsic_value_vnd": intrinsic, "settled": False,
        })

    rec = {
        "key": event_key(tk, ex_date), "ticker": tk, "ex_date": str(ex_date)[:10],
        "n_events": len(events or []), "reason": info.get("reason", ""),
        "price_ratio": price_ratio, "share_ratio": share_ratio, "rights_ratio": rights_ratio,
        "cash_per_share": cash_ps, "rights_value_per_share": rights_ps,
        "p_cum": p_cum, "p_ref": p_ref,
        "p_ref_anchor": anchor["verdict"], "p_ref_anchor_close": close_ref,
        "p_ref_anchor_diff": anchor["diff"],
        "qty_before": int(qty0), "qty_after": qty_new,
        "frac_shares": frac, "frac_cash_vnd": frac_cash,
        "cash_dividend_vnd": cash_div_gross,      # GỘP — giữ tên cũ = con số của SỞ
        "cash_dividend_net_vnd": cash_div_net, "div_tax_vnd": div_tax,
        "div_tax_rate": DIV_TAX_RATE,
        "cash_delta_vnd": cash_delta,             # RÒNG + tiền lẻ = đúng số vào sổ
        "pending_rights": pending, "rights_intrinsic_vnd": rights_intrinsic,
        "mv_before_vnd": qty0 * p_cum, "mv_after_vnd": qty_new * p_ref,
    }
    ok, resid = verify_invariant(rec)
    rec["invariant_residual_vnd"] = resid
    if not ok:
        return None, (f"{tk}@{ex_date}: ĐỒNG NHẤT THỨC BẢO TOÀN THẤT BẠI — lệch {resid:,.4f}đ "
                      f"(> {INVARIANT_TOL_VND}đ). Bản ghi bị TỪ CHỐI, sổ paper không đổi")
    return rec, info.get("reason", "")


def check_p_ref_against_close(p_ref, close_ref, symbol="", exchange="HOSE"):
    """NEO NGOÀI: P_ref tự tính vs `ticker.Close` phiên cum (vendor tự điều chỉnh) → dict.

    Đây là phép kiểm DUY NHẤT trong module ràng buộc được KINH TẾ (tỉ lệ / cổ tức / giá phát
    hành). Đồng nhất thức bảo toàn thì không — nó đúng với cả bộ tham số sai.
    """
    from trading_bot.price_frame import tick_size
    if close_ref is None:
        return {"verdict": "skipped-no-data", "diff": None, "tol": None}
    try:
        close_ref = float(close_ref)
    except (TypeError, ValueError):
        return {"verdict": "skipped-no-data", "diff": None, "tol": None}
    if close_ref <= 0:
        return {"verdict": "skipped-no-data", "diff": None, "tol": None}
    tol = float(tick_size(p_ref, symbol=symbol or "", exchange=exchange or "HOSE"))
    diff = p_ref - close_ref
    return {"verdict": "ok" if abs(diff) <= tol + 1e-9 else "mismatch", "diff": diff, "tol": tol}


def verify_invariant(rec) -> tuple:
    """KL_cũ×P_cum == KL_mới×P_ref + Δtiền + thuế TNCN + giá trị quyền chờ → (đạt?, dư VND).

    ⚠️ ĐỒNG NHẤT THỨC BẢO TOÀN, KHÔNG phải bằng chứng kinh tế — xem docstring module. Bắt được
    lỗi số học giữa các nhánh (vd bỏ sót tiền lẻ), KHÔNG bắt được tỉ lệ/cổ tức sai.
    """
    lhs = rec["qty_before"] * rec["p_cum"]
    rhs = (rec["qty_after"] * rec["p_ref"] + rec["cash_delta_vnd"]
           + rec.get("div_tax_vnd", 0.0)          # rời hệ ra thuế, KHÔNG được nuốt vào phần dư
           + rec.get("rights_intrinsic_vnd", 0.0))
    resid = lhs - rhs
    return abs(resid) <= INVARIANT_TOL_VND, resid


def apply_records(state: dict, records, asof: str, external: list = None) -> dict:
    """Áp bản ghi vào state (mutate). Bỏ qua khoá đã áp ⇒ chạy lại là idempotent."""
    led = ledger(state)
    done = applied_keys(state, external)
    summary = {"applied": [], "skipped_duplicate": [], "rejected": [], "cash_delta_total": 0.0}
    for rec in records:
        if rec["key"] in done:
            summary["skipped_duplicate"].append(rec["key"])
            continue
        pos = state.setdefault("positions", {})
        cur = int(pos.get(rec["ticker"], 0))
        # Chốt an toàn: sổ phải KHỚP với "băng fills + phần CP các sự kiện ĐÃ ÁP cộng vào". Lệch
        # = sổ đã trôi (ca thật: `PaperBroker._save()` ghi đè nuốt mất thay đổi) ⇒ TỪ CHỐI TO.
        # KHÔNG so `cur` với `qty_before`: với sự kiện QUÁ KHỨ, sổ hôm nay đã khác KL sáng GDKHQ
        # một cách hợp lệ (mua thêm sau đó) — so như vậy sẽ chặn mọi lần hồi tố.
        expect = qty_at_effective(state, rec["ticker"], "9999-12-31", external=external)
        if cur != expect:
            summary["rejected"].append(
                f"{rec['key']}: KL sổ = {cur} ≠ {expect} (băng fills + sự kiện đã áp) — sổ đã "
                f"trôi, KHÔNG áp")
            continue
        delta = int(rec["qty_after"]) - int(rec["qty_before"])
        if cur + delta < 0:
            summary["rejected"].append(f"{rec['key']}: áp Δ{delta:+d} vào KL {cur} ⇒ âm")
            continue
        # Cộng ĐỘ LỚN thay đổi, không gán `qty_after`: gán sẽ XOÁ mọi lệnh khớp SAU ngày GDKHQ
        # (hồi tố MBB 08-11 lên sổ hôm nay ⇒ 1.500 bị ghi đè thành 1.380, bốc hơi 120 CP).
        pos[rec["ticker"]] = cur + delta
        state["cash"] = float(state.get("cash", 0.0)) + rec["cash_delta_vnd"]
        rec = dict(rec, applied_at=now_ict().isoformat(timespec="seconds"), asof=asof)
        led["applied"].append(rec)
        led["pending_rights"].extend(rec.get("pending_rights") or [])
        done.add(rec["key"])
        summary["applied"].append(rec)
        summary["cash_delta_total"] += rec["cash_delta_vnd"]
    return summary


def qty_at(state: dict, ticker: str, on_date: str) -> int:
    """KL của `ticker` vào SÁNG `on_date`, dựng lại từ băng `fills` — cho đường HỒI TỐ.

    Dùng KL HÔM NAY để áp một sự kiện của QUÁ KHỨ là sai kinh tế (sổ paper churn mỗi phiên:
    MBB giữ 1.100 sáng 09/07 và 1.200 sáng 11/08, nhưng hôm nay là 1.500).
    """
    tk = str(ticker).strip().upper()
    d = str(on_date)[:10]
    q = 0
    for f in state.get("fills") or []:
        if str(f.get("symbol") or "").strip().upper() != tk:
            continue
        if str(f.get("ts") or "")[:10] >= d:
            continue
        q += int(f.get("qty") or 0) * (1 if f.get("side") == "buy" else -1)
    return q


def _fills_on_or_after(state: dict, ticker: str, on_date: str) -> int:
    """Số lệnh khớp của `ticker` có ngày >= `on_date` (dùng để PHÂN BIỆT bằng chứng, §29)."""
    tk = str(ticker).strip().upper()
    d = str(on_date)[:10]
    return sum(1 for f in (state.get("fills") or [])
               if str(f.get("symbol") or "").strip().upper() == tk
               and str(f.get("ts") or "")[:10] >= d)


def applied_records(state: dict, external: list = None) -> list:
    """HỢP các bản ghi đã áp (state + sổ cái ngoài), khử trùng theo `key`."""
    out, seen = [], set()
    for r in list(ledger(state).get("applied", [])) + list(external or []):
        k = r.get("key")
        if k and k not in seen:
            seen.add(k)
            out.append(r)
    return out


def qty_at_effective(state: dict, ticker: str, on_date: str, external: list = None) -> int:
    """KL vào SÁNG `on_date` cho MỌI đường chạy (cron lẫn hồi tố).

    `qty_at()` một mình KHÔNG đủ: băng `fills` chỉ biết lệnh khớp, không biết CP mà các sự kiện
    ĐÃ ÁP trước đó cộng vào sổ ⇒ phải cộng lại phần đó cho các sự kiện có GDKHQ <= `on_date`.
    Ngược lại, đọc thẳng `positions` (vòng 2 làm thế ở nhánh cron) tính cả lệnh mua ĐÚNG NGÀY
    GDKHQ — cổ phiếu mua ngày đó KHÔNG được hưởng quyền. Sổ paper main có thật một lệnh mua
    100 MBB lúc 11:00:06 ngày GDKHQ 2026-08-11 ⇒ nhánh cron ghi dư 2.425.000đ (quant-skeptic
    vòng 2, D1). Cả bất biến bảo toàn lẫn neo ngoài đều MÙ với lỗi này vì cả hai độc lập với KL.
    """
    tk = str(ticker).strip().upper()
    d = str(on_date)[:10]
    q = qty_at(state, tk, d)
    for rec in applied_records(state, external):
        if str(rec.get("ticker") or "").strip().upper() != tk:
            continue
        if str(rec.get("ex_date") or "")[:10] > d:
            continue
        q += int(rec.get("qty_after") or 0) - int(rec.get("qty_before") or 0)
    return q


# ───────────────────────────────────────────────────────────────── đường production (có IO)

def _close_at(ticker, ex_date, bq_query=None):
    """`tav2_bq.ticker.Close` của phiên cum cuối trước `ex_date` → (giá | None, info)."""
    sql = f"""
        SELECT t.Close AS px, CAST(t.time AS STRING) AS d
        FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
        WHERE t.ticker = '{str(ticker).strip().upper()}'
          AND t.time < DATE '{str(ex_date)[:10]}' AND t.Close > 0
        ORDER BY t.time DESC LIMIT 1
    """
    try:
        if bq_query is None:
            import corp_action_lib as cal
            bq_query = cal.bq
        rows = bq_query(sql)
    except Exception as exc:                                        # noqa: BLE001
        return None, {"reason": f"BQ Close lỗi: {type(exc).__name__}: {exc}"}
    if not rows:
        return None, {"reason": "BQ Close không trả dòng nào cho phiên cum"}
    from trading_bot.price_frame import normalize_price_vnd
    px = normalize_price_vnd(rows[0].get("px"))
    return (float(px) if px and float(px) > 0 else None), {"reason": f"Close phiên {rows[0].get('d')}"}


def collect(state, since, until, p_cum_fn=None, events_fn=None, close_fn=None):
    """Tra sự kiện trong (since, until] cho mã ĐANG GIỮ → (records, errors, error_dates).

    Không còn nhánh `backfill`: cron và hồi tố dùng CHUNG một gốc KL (`qty_at_effective`). Hai
    nhánh khác nhau chính là lỗi D1 của quant-skeptic vòng 2 — đường sẽ chạy thật là đường sai.
    """
    from trading_bot.price_frame import events_by_ticker_date, p_cum_from_bq
    from trading_bot.price_frame import pricing_events as pf_pricing_events

    held = {t: int(q) for t, q in (state.get("positions") or {}).items() if int(q or 0) > 0}
    if not held:
        return [], [], []
    evs = (events_fn or pf_pricing_events)(sorted(held), since=since, until=until)
    by = events_by_ticker_date(evs)
    pcf = p_cum_fn or (lambda tk, d: p_cum_from_bq(tk, d))
    clf = close_fn or (lambda tk, d: _close_at(tk, d))

    done = applied_keys(state, read_external_ledger_for(state))
    # KL nối qua từng sự kiện: 2 sự kiện đổi KL trên CÙNG mã trong 1 cửa sổ phải nối nhau, không
    # cùng xuất phát từ ảnh chụp đầu cửa sổ (vòng 1 bị lỗi này — sổ bị áp DỞ DANG).
    back_mult = {}                      # {mã: tích (1+share_ratio) của sự kiện đã hồi tố trước}
    records, errors, error_dates = [], [], []
    for (tk, d), cluster in sorted(by.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if tk not in held or event_key(tk, d) in done:
            continue
        # Gốc KL = băng `fills` cắt theo ngày GDKHQ + phần CP các sự kiện ĐÃ ÁP cộng vào sổ,
        # RỒI nhân tiếp hệ số của các sự kiện áp trong CHÍNH lần chạy này (chưa vào sổ cái).
        qty_base = qty_at_effective(state, tk, d, external=read_external_ledger_for(state))
        qty0 = int(math.floor(qty_base * back_mult.get(tk, 1.0) + 1e-9))
        if qty0 <= 0:
            # Phân biệt bằng CHỨNG CỨ (§29), không đoán: KL=0 vì toàn bộ vị thế mua VÀO/SAU ngày
            # GDKHQ là câu trả lời XÁC ĐỊNH ("không hưởng quyền") ⇒ không chặn watermark. KL=0 mà
            # băng fills cũng không có lệnh nào từ ngày đó trở đi là MÂU THUẪN ⇒ treo, chờ người.
            bought_on_or_after = _fills_on_or_after(state, tk, d)
            errors.append(f"{tk}@{d}: KL vào ngày GDKHQ = {qty0} — không hưởng quyền "
                          f"({bought_on_or_after} lệnh khớp từ ngày đó trở đi)")
            if not bought_on_or_after:
                error_dates.append(d)
            continue
        p_cum, pinfo = pcf(tk, d)
        if p_cum is None:
            errors.append(f"{tk}@{d}: {pinfo.get('reason', 'không lấy được p_cum')}")
            error_dates.append(d)
            continue
        # Neo chỉ hợp lệ khi mã KHÔNG còn sự kiện làm-đổi-giá nào SAU `d`: `Close` gánh điều
        # chỉnh của mọi sự kiện về sau (ca MBB@07-09 gánh thêm đợt 08-11). `by` đã phủ trọn cửa
        # sổ tới `until` nên phép kiểm này không tốn thêm truy vấn nào.
        has_later = any(k[0] == tk and k[1] > d for k in by)
        close_ref = None if has_later else clf(tk, d)[0]
        rec, why = build_record(tk, d, cluster, qty0, p_cum, close_ref=close_ref)
        if rec is not None and has_later:
            rec["p_ref_anchor"] = "skipped-later-events"
        if rec is None:
            errors.append(why)
            error_dates.append(d)
            continue
        back_mult[tk] = back_mult.get(tk, 1.0) * (1.0 + rec["share_ratio"])
        records.append(rec)
    return records, errors, error_dates


def read_external_ledger_for(state):
    return state.get("_external_ledger") or []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--label", default="main")
    ap.add_argument("--date", default=None, help="ngày chạy (mặc định hôm nay ICT)")
    ap.add_argument("--dry", action="store_true", help="in ra, không ghi sổ")
    ap.add_argument("--backfill-since", default=None,
                    help="HỒI TỐ: quét từ ngày này, KL dựng lại từ băng fills (không dùng trong cron)")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        import subprocess
        return subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "paper_corp_action_selfcheck.py")]).returncode

    date = args.date or now_ict().date().isoformat()
    path, lpath = state_path(args.label), ledger_path(args.label)
    if not os.path.exists(path):
        print(f"[paper-ca] sổ paper [{args.label}] chưa tồn tại ({path}) — không có gì để áp")
        return 0

    # Khoá độc quyền suốt đọc→ghi: `PaperBroker._save()` ghi ĐÈ toàn bộ state, chạy chồng sẽ
    # nuốt mất thay đổi (và cả sổ con). Khoá không ngăn được PaperBroker (nó không lấy khoá),
    # nhưng ngăn 2 lần chạy applier chồng nhau và thu hẹp cửa sổ va chạm xuống mức đo được.
    os.makedirs(os.path.dirname(lpath), exist_ok=True)
    with open(lpath + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
        state["_external_ledger"] = read_external_ledger(lpath)
        led = ledger(state)

        if args.backfill_since:
            since = args.backfill_since
            print(f"[paper-ca] ⚠️ HỒI TỐ từ {since} — KL dựng lại từ băng `fills` theo từng ngày "
                  f"GDKHQ (KHÔNG dùng KL hôm nay). Sẽ ĐỔI số liệu lịch sử của sổ paper; mọi "
                  f"verdict đã chốt dựa trên số cũ phải được nêu lại thủ công.")
        elif led["watermark"]:
            since = led["watermark"]
        else:
            since = (dt.date.fromisoformat(date) - dt.timedelta(days=1)).isoformat()
            print(f"[paper-ca] lần chạy đầu trên sổ [{args.label}] — watermark = {since}, KHÔNG "
                  f"hồi tố (số liệu cũ là căn cứ của verdict đã chốt).")

        records, errors, error_dates = collect(state, since, date)

        for e in errors:
            print(f"[paper-ca] ❌ {e}")
        if not records:
            print(f"[paper-ca] [{args.label}] {since} → {date}: không có sự kiện nào cần áp"
                  f"{' (có lỗi ở trên)' if errors else ''}")
        for r in records:
            extra = (f" · quyền mua CHỜ {r['rights_intrinsic_vnd']:+,.0f}đ nội tại "
                     f"({sum(p['shares'] for p in r['pending_rights']):,.0f}cp @ "
                     f"{r['pending_rights'][0]['issue_price']:,.0f}đ)") if r["pending_rights"] else ""
            tax = (f" (cổ tức gộp {r['cash_dividend_vnd']:,.0f}đ − thuế "
                   f"{r['div_tax_vnd']:,.0f}đ @{r['div_tax_rate']:.0%})") if r["div_tax_vnd"] else ""
            print(f"[paper-ca] {r['ticker']}@{r['ex_date']}  KL {r['qty_before']:,} → "
                  f"{r['qty_after']:,} (×{1 + r['share_ratio']:.4f}) · tiền "
                  f"{r['cash_delta_vnd']:+,.0f}đ{tax} · P_cum {r['p_cum']:,.0f} → P_ref "
                  f"{r['p_ref']:,.0f} [neo {r['p_ref_anchor']}]{extra} · dư "
                  f"{r['invariant_residual_vnd']:+.4f}đ  [{r['reason']}]")

        anchor_bad = [r for r in records if r["p_ref_anchor"] == "mismatch"]
        for r in anchor_bad:
            print(f"[paper-ca] ⚠️ NEO NGOÀI LỆCH {r['ticker']}@{r['ex_date']}: P_ref tự tính "
                  f"{r['p_ref']:,.2f}đ vs `ticker.Close` phiên cum "
                  f"{r['p_ref_anchor_close']:,.2f}đ (lệch {r['p_ref_anchor_diff']:+,.2f}đ > 1 "
                  f"bước giá). Tỉ lệ/cổ tức/giá phát hành CÓ THỂ SAI — vẫn áp (giá trị được bảo "
                  f"toàn) nhưng CẦN NGƯỜI ĐỐI CHIẾU.")

        if args.dry:
            print("[paper-ca] --dry: KHÔNG ghi sổ")
            return 1 if (errors or anchor_bad) else 0

        summary = apply_records(state, records, asof=date,
                                external=state.get("_external_ledger"))
        for r in summary["rejected"]:
            print(f"[paper-ca] ❌ TỪ CHỐI {r}")
            error_dates.append(r.split("|")[1].split(":")[0].strip())

        # Watermark DỪNG TRƯỚC sự kiện còn treo — nếu không, một lần fail-closed sẽ đẩy sự kiện
        # ra khỏi MỌI cửa sổ tương lai và biến "từ chối an toàn" thành "mất im lặng vĩnh viễn".
        if not args.backfill_since:
            new_wm = date
            if error_dates:
                stuck = min(error_dates)
                new_wm = min(new_wm, (dt.date.fromisoformat(stuck)
                                      - dt.timedelta(days=1)).isoformat())
                print(f"[paper-ca] ⚠️ watermark DỪNG ở {new_wm} (không vượt qua sự kiện còn treo "
                      f"ngày {stuck}) — lần chạy sau sẽ gặp lại nó.")
            led["watermark"] = new_wm

        # THỨ TỰ CÓ CHỦ ĐÍCH: state TRƯỚC, sổ cái ngoài SAU (quant-skeptic vòng 2, D2).
        # Ghi sổ cái trước rồi chết máy giữa hai bước để lại dấu "đã áp" trên một sự kiện CHƯA
        # áp ⇒ lần chạy sau bỏ qua nó và đẩy watermark qua = mất im lặng VĨNH VIỄN. Đảo lại thì
        # ca xấu nhất (state đã ghi, sổ cái chưa) chỉ dẫn tới một lần áp lại, và chốt
        # `cur != qty_before` (apply_records) TỪ CHỐI TO thay vì im lặng.
        state.pop("_external_ledger", None)
        save_state_atomic(path, state)
        for rec in summary["applied"]:
            append_external_ledger(lpath, {"key": rec["key"], "ticker": rec["ticker"],
                                           "ex_date": rec["ex_date"], "qty_before": rec["qty_before"],
                                           "qty_after": rec["qty_after"],
                                           "cash_delta_vnd": rec["cash_delta_vnd"],
                                           "cash_dividend_gross_vnd": rec["cash_dividend_vnd"],
                                           "div_tax_vnd": rec["div_tax_vnd"],
                                           "applied_at": rec["applied_at"], "asof": rec["asof"]})
        print(f"[paper-ca] đã áp {len(summary['applied'])} sự kiện · tiền "
              f"{summary['cash_delta_total']:+,.0f}đ · quyền mua chờ "
              f"{len(led['pending_rights'])} khoản · watermark = {led['watermark']}")
        return 1 if (errors or summary["rejected"] or anchor_bad) else 0


if __name__ == "__main__":
    sys.exit(main())

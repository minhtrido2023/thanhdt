#!/usr/bin/env python3
"""merge_park_orders.py — GỘP L1 park_trim + L2 jit_unpark vào `orders[]` của plan.

Thay cho các script one-off (`merge_three_in_one_20260807.py`,
`write_park_trim_into_plan_20260807.py`, `approve_plan_with_jit.sh` phần merge). Chạy lặp
được mỗi phiên, KHÔNG cần viết script mới mỗi lần.

════════════════════════════════════════════════════════════════════════════════════════
NGUYÊN LÝ THIẾT KẾ — vì sao là "DỰNG LẠI" chứ không phải "THÊM VÀO"
════════════════════════════════════════════════════════════════════════════════════════

Sự cố 2026-08-07 (bán trùng 1.200cp SpaceX + 400cp ZaloPay, Wags bắt được lúc 05:48 ICT,
cách giờ đặt lệnh 15 phút) KHÔNG phải lỗi số học. Nó là lỗi **hai người viết cùng một khái
niệm bằng hai cái tên khác nhau**:

  · `merge_three_in_one_20260807.py` ghi id  `SELL-{TK}-PARK-{i:02d}`
  · `approve_plan_with_jit.sh`       ghi id  `SELL-JIT-PARK-{TK}-01`
    và dedup bằng `if oid in existing_ids: continue`

Hai namespace id khác nhau ⇒ dedup theo id KHÔNG BAO GIỜ khớp ⇒ cùng một lô cổ phiếu bị
đề xuất bán hai lần. Ca cụ thể: ZaloPay/VHM = 200 (L1) + 100 (L2) + 100 (JIT gốc còn sót)
= **400cp trên 300cp sellable**.

⇒ Bài học: **dedup theo id là sai cơ chế.** Id là thứ do người viết đặt; nó không phải danh
tính kinh tế của lệnh. Danh tính kinh tế là `(ticker, side, nguồn-sinh-ra)`.

Cơ chế ở đây:

  1. **SỞ HỮU MỘT VÙNG.** Mọi lệnh do merge sinh ra mang dấu `merge_owner="park_merge_v1"`.
     Bước ĐẦU TIÊN của mỗi lần chạy là **XOÁ SẠCH** vùng đó rồi dựng lại từ L1/L2 hiện tại.
     Chạy 2 lần ⇒ kết quả y hệt (không cộng dồn). Chạy lại sau khi L1/L2 được tính lại ⇒
     ra số MỚI ĐÚNG, không phải số cũ + số mới.
  2. **NHẬN NUÔI LỆNH DI SẢN.** Vùng sở hữu còn bao gồm lệnh bán PARK do các script CŨ ghi
     (nhận diện theo `play_type ∈ {PARK_TRIM, JIT_UNPARK, PARK_TRIM+JIT_UNPARK}` +
     `book=PARK` + `side=sell`), kể cả khi không có dấu `merge_owner`. Nhờ vậy chạy merge
     mới SAU một script cũ thì HỘI TỤ về một bộ lệnh đúng, thay vì nhân đôi — đúng lớp lỗi
     08-07 bị chặn từ gốc, không phụ thuộc việc ai nhớ xoá tay.
  3. **BẤT BIẾN HẬU KIỂM TRÊN TOÀN BỘ `orders[]`**, không chỉ trên phần mình sinh ra:
     Σ qty bán mỗi mã (mọi book, mọi nguồn) ≤ `sellable`. Bất biến này bắt được bán trùng
     kể cả khi lệnh thừa do một writer KHÁC ghi vào — thứ mà dedup theo id mù hoàn toàn.
     Vi phạm ⇒ TRẢ VỀ PLAN NGUYÊN VẸN, không ghi file (fail-closed).

════════════════════════════════════════════════════════════════════════════════════════
CỔNG ĐỐI SOÁT — KHÔNG kế thừa `assert reconcile_ok is True`
════════════════════════════════════════════════════════════════════════════════════════

`merge_three_in_one_20260807.py:32` hard-assert `l2["reconcile_ok"] is True`. Với bản vá
kế toán 2026-08-10 (`pending_park_trim_partial_reconcile_20260810/`), ngày PARTIAL có
`reconcile_ok=False` NHƯNG vẫn sinh lệnh hợp lệ (mã lệch bị cấm bán riêng, mẫu số đã hiệu
chỉnh) ⇒ assert đó sẽ DỪNG SAI đúng ngày bản vá vừa cứu được. Ở đây:

    chấp nhận  ⇔  reconcile_ok is True  OR  reconcile_partial is True
    từ chối    ⇔  reconcile_ok is False AND reconcile_partial is not True

Và từ chối là **theo TẦNG**, không phải theo tài khoản: L1 hỏng thì L2 vẫn chạy, và ngược
lại. Đây là bài học 2026-08-06 (một mã lệch sổ ⇒ khoá sạch vốn cả 2 tài khoản đúng phiên
entry chuẩn): một cổng thô chặn cả gói là cách mất phiên, không phải cách an toàn.

════════════════════════════════════════════════════════════════════════════════════════
THỨ TỰ CẮT KHI VƯỢT `sellable` — cắt L1 trước, KHÔNG cắt L2 trước
════════════════════════════════════════════════════════════════════════════════════════

L1 = tuân thủ trần PARK (hoãn được 1 phiên, hướng sai là "trim ít hơn" = an toàn).
L2 = cấp vốn cho lệnh MUA cùng plan (cắt ⇒ lệnh mua thiếu tiền ⇒ P0 `check_plan_funding`
chặn ⇒ mất phiên entry). Nên khi phải cắt: **L1 trước, L2 sau**, làm tròn XUỐNG bội 100.
Cắt vào L2 luôn được ghi cờ `jit_underfunded` để người duyệt thấy trước, không để P0 phát
hiện hộ lúc 09:05.

════════════════════════════════════════════════════════════════════════════════════════
KHÔNG BAO GIỜ tự duyệt
════════════════════════════════════════════════════════════════════════════════════════

Hàm này luôn đặt `requires_user_approval=True` và KHÔNG BAO GIỜ ghi `approved_by`. Plan đã
có `approved_by` ⇒ TỪ CHỐI sửa (sửa orders[] sau khi duyệt = vô hiệu hoá chữ ký duyệt);
muốn sửa thật thì phải `--force-clear-approval`, và cờ đó XOÁ `approved_by` để bắt buộc
duyệt lại.

DÙNG:
    python3 mike/bin/merge_park_orders.py --account SpaceX --plan-date 2026-08-11
    python3 mike/bin/merge_park_orders.py --account SpaceX --plan-date 2026-08-11 --write
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

LOT = 100
OWNER = "park_merge_v1"
LEGACY_PLAY_TYPES = {"PARK_TRIM", "JIT_UNPARK", "PARK_TRIM+JIT_UNPARK"}
ID_PREFIX = "PARKMERGE-SELL"

# merge SỞ HỮU TOÀN BỘ KHÔNG GIAN TÊN `jit_*` trên `orders[]`. Bước 5 ghi chú thích lên lệnh
# MUA (lệnh của writer khác, NGOÀI vùng bán) — nằm ngoài vùng bị xoá-và-dựng-lại nên KHÔNG tự
# hết hạn ⇒ bước 0 xoá theo TIỀN TỐ, không theo danh sách liệt kê.
#
# ⚠️ Vì sao tiền tố chứ không phải tuple 3 tên (`jit_status`/`jit_note`/`jit_underfunded`):
# bản trước neo bằng danh sách + một helper bắt buộc gọi + một ca selfcheck grep 3 tên literal.
# quant-skeptic vòng 5 **BÁC BỎ** đúng chỗ đó: helper chỉ nổ khi có người GỌI nó, còn ca grep
# chỉ biết 3 tên đang có ⇒ nhãn thứ 4 gán thẳng `tgt["jit_x"] = …` lọt qua CẢ HAI, không bao
# giờ bị bước 0 xoá, và sống sót vào đúng lần chạy L2 bị từ chối — **tái lập nguyên văn khuyết
# tật #5 với selfcheck vẫn xanh 84/84** (nó đã chứng minh bằng cách vá đúng 1 dòng).
# Xoá theo tiền tố khiến tập XOÁ luôn là tập CHA của mọi tập GHI, **theo cấu trúc** — không còn
# danh sách nào để trôi, không cần ai nhớ gọi hàm nào.
#
# ⚠️ RANH GIỚI CHÍNH XÁC của bất biến này (quant-skeptic vòng 6 — nêu ra để nó là SỰ THẬT ĐÃ
# KIỂM, không phải giả định ngầm): bước 0 quét **khoá CẤP MỘT của từng lệnh**. Khoá `jit_` nằm
# LỒNG trong dict con (`o["meta"]["jit_x"]`) **KHÔNG** bị quét — hôm nay vô hại vì bước 5 chỉ ghi
# khoá cấp một, và ca `S5d` ghim đúng ranh giới đó. Bước 5 tương lai ghi nhãn LỒNG sẽ mở lại
# khuyết tật #5, nên nếu cần thì mở rộng bước 0 chứ đừng ghi lồng.
_JIT_PREFIX = "jit_"

# Mọi tên field mang CHỮ KÝ DUYỆT mà tầng dưới công nhận. Cổng duyệt phải đọc ĐỦ tập này, nếu
# không nó fail-OPEN đúng chỗ nó sinh ra để fail-closed. Nguồn (đã đọc tận nơi, không suy đoán):
#   `trading_bot/plan.py:182-183`  ·  `mike/bin/preflight_check.sh:60`
# Thêm alias mới ở hai nơi đó ⇒ PHẢI thêm vào đây; ca `A5` trong selfcheck canh từng tên.
_APPROVAL_KEYS = ("approved_by", "approved_by_user")

DEFAULT_PLAN_DIR = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"

# Repo root, suy từ vị trí CHÍNH FILE NÀY (mike/bin/x.py → lên 3 cấp) chứ không chép cứng:
# file này chạy từ cron, từ worktree, và từ selfcheck ở các cwd khác nhau.
_WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ngưỡng phân biệt "nhiễu giá thường giữa hai lần chạy L1/L2" với "cú LẬT HỆ QUY CHIẾU" —
# xem khối chú thích ở bước 2b. Chọn 1,0%: nhỏ nhất trong 22 ngày-mã GDKHQ đo được (README §4
# của exdate_order_pipeline_20260815) là **0,8%** (VCB 2026-07-23) và trung vị là 5,46%, nên
# ngưỡng phải nằm DƯỚI phân bố đó; đồng thời 1,0% là đúng con số dung sai
# `RULE_A_REF_TOL_DEFAULT` mà cổng cơ sở giá tầng đặt lệnh đang dùng — một chính sách, một số.
# Ngưỡng CHỈ có hiệu lực khi mã có sự kiện quyền trong cửa sổ; ngoài cửa sổ, mọi mức lệch giữ
# nguyên hành vi cũ (cảnh báo + lấy giá thấp hơn).
REF_PRICE_EXDATE_TOL = 0.01


# ══════════════════════════════════════════════════════════════════════════════════════
# helpers
# ══════════════════════════════════════════════════════════════════════════════════════
def _exdate_map(tickers, plan_date, report=None):
    """Lịch sự kiện quyền quanh `plan_date` → map của `price_frame`, {} khi tra không được.

    FAIL-OPEN có chủ ý (cùng lý lẽ với `exdate_gate.apply_exdate_gate`): nguồn là BigQuery,
    một hệ ngoài đường đặt lệnh; cho nó quyền dừng merge mỗi khi BQ hắt hơi là đổi một rủi ro
    hiếm lấy một rủi ro thường. Map rỗng ⇒ hành vi merge NGUYÊN VẸN như trước bản vá, và lý do
    được ghi vào `report["warnings"]` để không ai nhầm im lặng với "không có sự kiện".
    """
    if not tickers or not plan_date:
        return {}
    try:
        if _WC_ROOT not in sys.path:
            sys.path.insert(0, _WC_ROOT)
        from trading_bot.price_frame import pricing_events, events_by_ticker_date
        import datetime as _dt
        d = _dt.date.fromisoformat(str(plan_date)[:10])
        evs = pricing_events(tickers, since=(d - _dt.timedelta(days=6)).isoformat(),
                             until=(d + _dt.timedelta(days=4)).isoformat())
        return events_by_ticker_date(evs)
    except Exception as exc:                                        # noqa: BLE001
        if report is not None:
            report["warnings"].append(
                f"KHÔNG tra được lịch sự kiện quyền ({type(exc).__name__}: {exc}) — cổng chặn "
                f"lệch-L1/L2-do-lật-hệ-quy-chiếu KHÔNG hoạt động phiên này (hành vi cũ giữ nguyên).")
        return {}


def _has_event_in_window(ex_map, ticker, plan_date):
    """Mã có sự kiện quyền quanh `plan_date` không → (bool, [event]).

    ⚠️ Tự neo repo root vào `sys.path` chứ KHÔNG dựa vào việc `_exdate_map()` đã chạy trước.
    Khi caller TIÊM `ex_map` (selfcheck, hoặc bất kỳ orchestrator nào tra lịch một lần rồi
    truyền xuống) thì `_exdate_map()` không hề chạy ⇒ không ai chèn path ⇒ import này hỏng ⇒
    hàm trả `False` và cổng chặn-lật-hệ-quy-chiếu **tự tắt trong im lặng**, đúng cách hỏng tệ
    nhất mà cả bản vá này sinh ra để tránh (README §0 mục 4). Một dòng path ở đây làm hàm
    đúng độc lập với THỨ TỰ GỌI.
    """
    if not ex_map:
        return False, []
    try:
        if _WC_ROOT not in sys.path:
            sys.path.insert(0, _WC_ROOT)
        from trading_bot.price_frame import has_event_in_window
        return has_event_in_window(ex_map, ticker, str(plan_date)[:10])
    except Exception:                                               # noqa: BLE001
        return False, []


def _i(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _f(v, default=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    return f


def _floor_lot(q):
    return max(0, (int(q) // LOT) * LOT)


def is_owned(o):
    """Lệnh có thuộc vùng merge SỞ HỮU không (⇒ bị dựng lại mỗi lần chạy)?

    Hai nhánh CỐ Ý tách rời:
      · nhánh 1 — dấu sở hữu tường minh của chính cơ chế này;
      · nhánh 2 — NHẬN NUÔI lệnh bán PARK do script one-off cũ ghi (không có dấu).
    Bỏ nhánh 2 là mở lại đúng lỗ hổng 08-07.
    """
    if not isinstance(o, dict):
        return False
    if o.get("merge_owner") == OWNER:
        return True
    return (
        str(o.get("side", "")).lower() == "sell"
        and str(o.get("book", "")).upper() == "PARK"
        and str(o.get("play_type", "")).upper() in LEGACY_PLAY_TYPES
    )


def _layer_state(art, want_decision, layer):
    """(accepted: bool, reason: str) — cổng đối soát + cổng decision cho MỘT tầng."""
    if art is None:
        return False, f"{layer}: không có artifact — bỏ qua tầng này (không phải lỗi)."
    dec = art.get("decision")
    if dec != want_decision:
        return False, f"{layer}: decision={dec!r} ≠ {want_decision!r} — tầng này không sinh lệnh."
    ok = art.get("reconcile_ok")
    partial = art.get("reconcile_partial")
    if ok is True:
        return True, f"{layer}: reconcile_ok=True."
    if partial is True:
        return True, (f"{layer}: reconcile_ok={ok!r} nhưng reconcile_partial=True — CHẤP NHẬN "
                      f"(bản vá 2026-08-10: mã lệch bị cấm bán riêng, mẫu số đã hiệu chỉnh).")
    return False, (f"{layer}: reconcile_ok={ok!r} và KHÔNG có reconcile_partial=True — "
                   f"từ chối RIÊNG tầng này (tầng kia vẫn được xét).")


# ══════════════════════════════════════════════════════════════════════════════════════
# lõi thuần — không I/O, không phụ thuộc file
# ══════════════════════════════════════════════════════════════════════════════════════
def merge_park_orders(plan, l1=None, l2=None, *, allow_approved=False, ex_map=None):
    """Dựng lại phần lệnh bán PARK trong `plan["orders"]` từ artifact L1/L2.

    Trả về `(new_plan, report)`. `plan` đầu vào KHÔNG bị sửa (deep-copy).
    `report["status"]` ∈ {"OK", "REFUSED"}. REFUSED ⇒ `new_plan` là bản SAO NGUYÊN VẸN của
    `plan` (caller không được ghi file).
    """
    # `layers` khởi tạo ĐỦ KHOÁ ngay từ đầu: nhánh `refuse()` ở cổng duyệt trả về TRƯỚC khi
    # cổng từng tầng chạy, mà caller (print_report/báo cáo) đọc thẳng report["layers"]["L1"].
    # Bug thật, chỉ lộ ra khi chạy CLI trên plan đã duyệt — selfcheck hàm thuần 58/58 xanh
    # vẫn không thấy (bài học `verify-before-done`: chạy đường THẬT, đừng chỉ test lõi).
    report = {"status": "OK", "errors": [], "warnings": [], "notes": [],
              "layers": {k: {"accepted": False, "reason": "chưa xét — dừng ở cổng trước đó"}
                         for k in ("L1", "L2")},
              "per_ticker": {}, "dropped_owned": [], "kept_foreign": [],
              "generated": [], "invariants": []}
    p = copy.deepcopy(plan)
    orig_orders = list(p.get("orders") or [])

    # ── 0. XOÁ VÔ ĐIỀU KIỆN mọi khoá `jit_*` trên MỌI lệnh (kể cả ngoài vùng sở hữu) ──
    # Bước 5 ghi `jit_status`/`jit_note`/`jit_underfunded` lên lệnh MUA — lệnh KHÔNG thuộc
    # vùng sở hữu nên không bị bước 1 xoá. Không xoá ở đây thì nhãn sống sót qua mọi lần
    # chạy sau với artifact ĐÃ ĐỔI: chạy 1 với L2 đủ vốn ⇒ jit_status="FUNDED"; L2 sau đó
    # bị TỪ CHỐI (reconcile fail) ⇒ chạy lại vẫn hiện "FUNDED" dù JIT đã bị từ chối thật.
    # Số lượng cổ phiếu vẫn đúng (bất biến I2 không phụ thuộc nhãn), nhưng người duyệt —
    # cơ chế an toàn DUY NHẤT của thiết kế này — đọc trạng thái vốn SAI.
    # (quant-skeptic vòng 3, 2026-08-10, khuyết tật #5.)
    # ⇒ 3 nhãn này theo đúng quy tắc của vùng bán: DỰNG LẠI-HOẶC-VẮNG-MẶT, không bao giờ
    #   "còn sót từ lần trước". Xoá TRƯỚC mọi cổng để nhánh REFUSED cũng không thể để lại
    #   nhãn cũ — refuse() trả `copy.deepcopy(plan)` (bản gốc chưa đụng) nên plan trên đĩa
    #   giữ nguyên; chỉ bản dựng lại mới mang nhãn mới.
    # Writer khác có ghi nhãn `jit_*` không? Có: `agents/DollarBill/merge_three_in_one_
    #   20260807.py` và `fix_slot_sizing_20260809.py` — đều là script one-off mà cơ chế này
    #   THAY THẾ, và nhãn của chúng đến từ một lần chạy L2 KHÁC ⇒ xoá là đúng, không phải
    #   đánh rơi dữ liệu của người khác (qty của lệnh mua không bị đụng: xem I5 + bước 5).
    #   Hệ quả CÓ CHỦ Ý và phải khai báo: **merge sở hữu toàn bộ không gian tên `jit_*` trên
    #   `orders[]`** — writer nào muốn giữ nhãn của mình qua merge thì đừng đặt tên `jit_*`.
    for o in (p.get("orders") or []):
        if isinstance(o, dict):
            for k in [k for k in o if str(k).startswith(_JIT_PREFIX)]:
                o.pop(k, None)

    # ── 0b. CÙNG NGUYÊN TẮC ĐÓ Ở **CẤP PLAN** (mở rộng phạm vi 2026-08-10, user DUYỆT) ──
    # Trước bản này merge chỉ sở hữu ĐÚNG MỘT khoá cấp plan (`jit_unpark_proposal`) và cố ý
    # để mọi khoá `jit_*` cấp plan khác cho writer gốc. Ca THẬT chứng minh ranh giới đó sai:
    # `plan_SpaceX_2026-08-10.json` mang `jit_unpark_note` = "L2 KHÔNG chạy cho plan này …
    # không có gì cần JIT tài trợ" — do writer lập plan ghi. Chạy merge với artifact L2 THẬT
    # sẽ sinh lệnh bán JIT vào `orders[]` **trong khi câu đó vẫn nằm nguyên trong plan**, và
    # người duyệt — cơ chế an toàn DUY NHẤT của thiết kế này — đọc một câu khẳng định ngược
    # hẳn với lệnh thật. Đúng LỚP khuyết tật #5/#6 ("nhãn không bao giờ hết hạn"), chỉ khác
    # tầng: #5 ở nhãn của lệnh, #6 ở khối đề xuất, đây ở khoá tự do cấp plan.
    #
    # Xoá theo KHÔNG GIAN TÊN, **không** theo danh sách tên literal — bài học vòng 5 (REFUTED):
    # liệt kê tên là QUY ƯỚC, không phải bất biến; writer sau đặt `jit_note_v2` là thoát ngay.
    # Ghi lại tập đã xoá để bước 6 còn phân biệt "khối cũ CÓ tồn tại" với "chưa từng có"
    # (pop lần hai luôn trả None ⇒ mất cảnh báo VẮNG MẶT của bản vá #6).
    #
    # ⇒ Phạm vi đầy đủ sau bản này: **merge sở hữu toàn bộ không gian tên `jit_*` ở CẢ hai
    #   tầng — khoá cấp một của mỗi lệnh, và khoá cấp một của plan.** Merge dựng lại đúng
    #   `jit_unpark_proposal` (bước 6); mọi khoá `jit_*` cấp plan khác VẮNG MẶT sau merge.
    #   Writer nào cần ghi chú sống qua merge thì đặt tên NGOÀI `jit_` (ví dụ có thật đang
    #   chạy: `duplicate_jit_fix_note` — có trong CẢ `plan_SpaceX_2026-08-07.json` LẪN
    #   `plan_ZaloPay_2026-08-07.json`; có chữ "jit" nhưng KHÔNG mang tiền tố `jit_` ⇒ ngoài
    #   phạm vi, không bị đụng. Đã chạy merge trên đúng 2 plan đó để ĐO, không phải suy luận).
    #
    # ⚠️ PHẠM VI THỜI GIAN của bản mở rộng này — nói thẳng vì nó là giới hạn thật:
    #   bước 0b chạy TRƯỚC cổng duyệt, nhưng cổng duyệt trả về `copy.deepcopy(plan)` NGUYÊN
    #   VẸN ⇒ trên plan ĐÃ CÓ `approved_by`, merge REFUSED và khoá `jit_*` cũ **SỐNG SÓT**.
    #   Đó là fail-closed đúng (ca S5e(f) canh), nhưng hệ quả phải khai: cơ chế này bảo vệ
    #   **cửa sổ TRƯỚC khi duyệt**, không dọn được plan đã duyệt trừ khi chạy lại với
    #   `--force-clear-approval` (và cờ đó xoá chữ ký, buộc duyệt lại).
    plan_jit_removed = sorted(k for k in p if str(k).startswith(_JIT_PREFIX))
    for k in plan_jit_removed:
        p.pop(k, None)

    def refuse(msg):
        report["status"] = "REFUSED"
        report["errors"].append(msg)
        return copy.deepcopy(plan), report

    # ── cổng duyệt ────────────────────────────────────────────────────────────────────
    # Đọc CẢ HAI tên field, đúng tập mà tầng dưới công nhận (quant-skeptic vòng 8 — lỗ
    # FAIL-OPEN thật, trên chính cái cổng có mục đích duy nhất là fail-closed):
    #   · `trading_bot/plan.py:182-183` — `if not d["approved_by"] and d["approved_by_user"]:
    #     d["approved_by"] = d["approved_by_user"]` ⇒ plan CHỈ có `approved_by_user` vẫn được
    #     `load_plan()` HỒI SINH thành đã-duyệt lúc thực thi;
    #   · `mike/bin/preflight_check.sh:60` — `d.get("approved_by") or d.get("approved_by_user")`.
    # Cổng cũ chỉ đọc `approved_by` ⇒ plan duyệt bằng tên thay thế sẽ KHÔNG bị từ chối, orders[]
    # bị dựng lại, rồi `load_plan()` gắn lại chữ ký ⇒ **lệnh mới chạy dưới chữ ký duyệt của bộ
    # lệnh CŨ**. Hôm nay 0/84 plan mang field đó (đã đo) nên là lỗ TIỀM ẨN, không phải đang chảy
    # máu — nhưng "hôm nay chưa ai dùng" là sự thật CÓ HẠN SỬ DỤNG, đúng lớp nhãn hết hạn mà cả
    # bản vá này đi chữa.
    approved_key = next((k for k in _APPROVAL_KEYS if p.get(k) not in (None, "")), None)
    approved = p.get(approved_key) if approved_key else None
    if approved_key and not allow_approved:
        return refuse(
            f"plan ĐÃ CÓ {approved_key}={approved!r} — từ chối sửa orders[]. Sửa lệnh sau khi "
            f"duyệt là vô hiệu hoá chữ ký duyệt. Muốn sửa thật: chạy lại với "
            f"--force-clear-approval (cờ đó gỡ chữ ký ở MỌI tên field, bắt buộc duyệt lại).")
    if approved_key and allow_approved:
        # Đặt None, KHÔNG `del` — giữ đúng hình dạng file mà consumer đang quen. Cả 2 tầng dưới
        # kiểm bằng GIÁ TRỊ (`not d.get(...)` / `or`), không kiểm sự hiện diện của khoá, nên
        # None là đủ; đã đọc tận nơi để khẳng định, không suy đoán.
        report["warnings"].append(
            f"GỠ chữ ký duyệt ({approved_key}={approved!r} → None, và mọi tên field thay thế) "
            f"vì orders[] bị dựng lại — PHẢI duyệt lại.")
        for k in _APPROVAL_KEYS:
            if k in p:
                p[k] = None
        p["approved_at"] = None

    # ── cổng từng tầng ────────────────────────────────────────────────────────────────
    l1_ok, l1_why = _layer_state(l1, "TRIM", "L1 park_trim")
    l2_ok, l2_why = _layer_state(l2, "JIT", "L2 jit_unpark")
    report["layers"] = {"L1": {"accepted": l1_ok, "reason": l1_why},
                        "L2": {"accepted": l2_ok, "reason": l2_why}}
    for why, ok in ((l1_why, l1_ok), (l2_why, l2_ok)):
        (report["notes"] if ok else report["warnings"]).append(why)

    # ── 1. XOÁ vùng sở hữu (kể cả lệnh di sản) ───────────────────────────────────────
    foreign = []
    for o in orig_orders:
        if is_owned(o):
            report["dropped_owned"].append(
                {"id": o.get("id"), "ticker": o.get("ticker"), "qty": _i(o.get("qty")),
                 "play_type": o.get("play_type"),
                 "tagged": o.get("merge_owner") == OWNER})
        else:
            foreign.append(o)
    report["kept_foreign"] = [o.get("id") for o in foreign]

    # ── 2. gộp L1+L2 theo mã ─────────────────────────────────────────────────────────
    agg = {}
    for src, art, use in (("L1", l1, l1_ok), ("L2", l2, l2_ok)):
        if not use:
            continue
        for o in (art.get("orders") or []):
            if str(o.get("side", "")).lower() != "sell":
                report["warnings"].append(
                    f"{src}/{o.get('ticker')}: side={o.get('side')!r} ≠ 'sell' — bỏ qua.")
                continue
            tk = o.get("ticker")
            px = _f(o.get("ref_price"))
            if not tk or px is None or px <= 0:
                report["warnings"].append(
                    f"{src}/{tk!r}: thiếu ticker hoặc ref_price hợp lệ — bỏ qua lệnh này.")
                continue
            d = agg.setdefault(tk, {"L1": 0, "L2": 0, "px": {}, "sellable": None,
                                    "for_orders": []})
            d[src] += max(0, _i(o.get("qty")))
            d["px"][src] = px
            s = o.get("sellable")
            if s is not None:
                s = _i(s, None)
                # nhiều nguồn báo sellable ⇒ lấy CHẶT NHẤT
                d["sellable"] = s if d["sellable"] is None else min(d["sellable"], s)
            if o.get("for_order_id"):
                d["for_orders"].append(o["for_order_id"])

    # ref_price: L1≠L2 KHÔNG phải lý do dừng cả plan (bài học 08-06) — cảnh báo + lấy giá
    # THẤP HƠN (ước tính tiền bán thận trọng; executor định giá lại từ ref_price+urgency).
    #
    # 🔴 NGOẠI LỆ (README §6.2 + §8-D3 mục 2, job Taylor_20260815_054822): hành vi "cảnh báo
    # rồi lấy giá thấp hơn" ĐÚNG cho nhiễu giá thường và SAI cho ca lật hệ quy chiếu. L1
    # (`park_trim`) chạy ~19:04 và L2 (`jit_unpark`) chạy ~19:40 có thể đứng HAI BÊN cú lật
    # của DNSE — ĐÃ XẢY RA THẬT ngày 2026-08-14 với BID (L1 19:04:15 hệ CŨ 38.850; cú lật
    # 19:10:23; L2 sau đó hệ MỚI 35.800). Hôm đó không thiệt hại vì L1 ra 0 lệnh, nhưng cơ
    # chế đã kích hoạt thật. Lúc ấy chênh L1/L2 KHÔNG phải nhiễu: "lấy giá thấp hơn" chọn
    # đúng giá hệ MỚI (may) trong khi qty vẫn là của L1 hệ CŨ (rủi) — hai hệ quy chiếu trong
    # một lệnh, đúng cách hỏng README §0 mục 4 mô tả.
    # ⇒ lệch VƯỢT NGƯỠNG **VÀ** mã có sự kiện quyền trong cửa sổ ⇒ **CHẶN riêng mã đó** (bỏ
    # khỏi vùng bán merge, không dừng cả plan). Ngoài cửa sổ sự kiện: hành vi cũ NGUYÊN VẸN.
    # `ex_map` tiêm được để selfcheck đóng băng lịch sự kiện (§23: không assert lên trạng thái
    # SỐNG — bảng BQ đổi một dòng là test đổi kết quả). None ⇒ tra thật như đường production.
    ex_map = _exdate_map(sorted(agg), plan.get("plan_date"), report) if ex_map is None else ex_map
    blocked_exdate = []
    for tk in sorted(agg):
        d = agg[tk]
        pxs = d["px"]
        if len(set(pxs.values())) > 1:
            lo, hi = min(pxs.values()), max(pxs.values())
            dev = hi / lo - 1
            has_ev, evs = _has_event_in_window(ex_map, tk, plan.get("plan_date"))
            if dev > REF_PRICE_EXDATE_TOL and has_ev:
                blocked_exdate.append(tk)
                report["errors"].append(
                    f"{tk}: ⛔ CHẶN mã này khỏi vùng bán merge — ref_price L1≠L2 ({pxs}) lệch "
                    f"{dev * 100:.2f}% > {REF_PRICE_EXDATE_TOL * 100:.2f}% VÀ mã có sự kiện "
                    f"quyền trong cửa sổ "
                    f"({', '.join(sorted({str(e.get('exright_date')) for e in evs}))}) — đây là "
                    f"chữ ký của một cú LẬT HỆ QUY CHIẾU giữa hai lần chạy L1/L2, không phải "
                    f"nhiễu giá. Lấy giá thấp hơn sẽ ghép giá hệ MỚI với qty hệ CŨ. Chạy lại "
                    f"CẢ L1 và L2 sau khi broker đã lật xong rồi merge lại.")
                continue
            report["warnings"].append(
                f"{tk}: ref_price L1≠L2 ({pxs}) lệch {dev * 100:.2f}% — dùng giá THẤP "
                f"hơn ({lo:,.0f}) cho ước tính thận trọng, KHÔNG dừng merge.")
        d["ref_price"] = min(pxs.values())
    for tk in blocked_exdate:
        agg.pop(tk, None)              # KHÔNG sinh lệnh bán nào cho mã bị chặn
    if blocked_exdate:
        report["exdate_blocked"] = blocked_exdate

    # ── 3. trần sellable, tính TRÊN TOÀN BỘ orders[] (kể cả lệnh của writer khác) ─────
    foreign_sell_qty = {}
    for o in foreign:
        if str(o.get("side", "")).lower() == "sell":
            tk = o.get("ticker")
            foreign_sell_qty[tk] = foreign_sell_qty.get(tk, 0) + max(0, _i(o.get("qty")))
            if tk in agg and o.get("sellable") is not None:
                s = _i(o.get("sellable"), None)
                if s is not None:
                    agg[tk]["sellable"] = (s if agg[tk]["sellable"] is None
                                           else min(agg[tk]["sellable"], s))

    for tk, d in sorted(agg.items()):
        cap = d["sellable"]
        other = foreign_sell_qty.get(tk, 0)
        want1, want2 = d["L1"], d["L2"]
        cut1 = cut2 = 0
        if cap is not None:
            room = cap - other
            if room < 0:
                return refuse(
                    f"{tk}: lệnh bán KHÔNG do merge sở hữu đã {other}cp > sellable {cap}cp — "
                    f"không phải phần merge sửa được. Dừng, không ghi plan.")
            over = (want1 + want2) - room
            if over > 0:
                # cắt L1 TRƯỚC (hoãn được), làm tròn XUỐNG bội lô
                cut1 = min(want1, over)
                new1 = _floor_lot(want1 - cut1)
                cut1 = want1 - new1
                want1 = new1
                over = (want1 + want2) - room
                if over > 0:
                    cut2 = min(want2, over)
                    new2 = _floor_lot(want2 - cut2)
                    cut2 = want2 - new2
                    want2 = new2
        d["final_L1"], d["final_L2"] = want1, want2
        d["cut_L1"], d["cut_L2"] = cut1, cut2
        d["foreign_sell_qty"] = other
        if cut1 or cut2:
            report["warnings"].append(
                f"{tk}: CẮT theo trần sellable={cap}cp (lệnh khác đã chiếm {other}cp) — "
                f"L1 −{cut1}cp, L2 −{cut2}cp." +
                (" ⚠️ cắt vào L2 ⇒ lệnh MUA được tài trợ có thể THIẾU TIỀN." if cut2 else ""))
        report["per_ticker"][tk] = {
            "L1_proposed": d["L1"], "L2_proposed": d["L2"],
            "L1_final": want1, "L2_final": want2, "qty": want1 + want2,
            "sellable": cap, "foreign_sell_qty": other,
            "cut_L1": cut1, "cut_L2": cut2, "ref_price": d["ref_price"]}

    # ── 4. sinh lệnh ─────────────────────────────────────────────────────────────────
    buy_pri = [_i(o.get("priority"), 5) for o in foreign
               if str(o.get("side", "")).lower() == "buy"]
    # KHÔNG clamp về 0. Kiểm toàn bộ chỗ đọc `priority` trong `trading_bot/` (2026-08-10):
    #   · khoá SẮP XẾP tăng dần — `executor.py:1232`, `plan.py:124`;
    #   · SO SÁNH số học — `plan_funding_gate.py:194-214` (`<` nghiêm ngặt), `plan.py:292`
    #     (`min(...)`);
    #   · và MỘT chỗ định dạng chuỗi — `plan.py:149`: `f"...-{o.get('priority', 0):02d}"`,
    #     dùng dựng id DỰ PHÒNG khi lệnh THIẾU `id`.
    # Không chỗ nào dùng nó làm chỉ số hay giả định không âm ⇒ giá trị ÂM hợp lệ. Riêng chỗ
    # thứ ba: lệnh do merge sinh ra LUÔN có `id` (`{ID_PREFIX}-{tk}`) nên nhánh dự phòng đó
    # không bao giờ chạy với priority của merge ⇒ hệ quả bằng 0 (nếu có chạy, `f"{-1:02d}"`
    # = "-1", vẫn là id hợp lệ). (quant-skeptic vòng 3 sửa câu "không nơi nào" trước đó.)
    # Clamp `max(0, …)` khiến lệnh mua ở priority 0 làm
    # bán và mua BẰNG nhau ⇒ bất biến I3 hỏng ⇒ TỪ CHỐI CẢ PLAN ⇒ 0 lệnh bán PARK ⇒ đúng hình
    # dạng mất-phiên 08-06 mà thiết kế này tuyên bố đã diệt (quant-skeptic bắt được 2026-08-10).
    sell_pri = (min(buy_pri) - 1) if buy_pri else 0

    generated = []
    for tk in sorted(agg):
        d = agg[tk]
        # Làm tròn XUỐNG bội lô VÔ ĐIỀU KIỆN, không chỉ ở nhánh phải cắt. Artifact trả qty lẻ
        # (không phải hôm nay — `compute_park_trim` dùng `round_lot()`, `compute_jit_unpark` cấp
        # theo bội LOT — nhưng đó là bất biến của FILE KHÁC, không phải của file này) sẽ làm bất
        # biến I4 hỏng ⇒ TỪ CHỐI CẢ PLAN ⇒ 0 lệnh bán = đúng hình dạng mất-phiên 08-06.
        # Làm tròn ở đây khiến ca đó không thể xảy ra, thay vì bắt cả plan làm con tin.
        # (quant-skeptic vòng 2, 2026-08-10 — "I4 hostage", phơi nhiễm hiện tại bằng 0.)
        for k in ("final_L1", "final_L2"):
            if d[k] % LOT:
                lo = _floor_lot(d[k])
                report["warnings"].append(
                    f"{tk}: {k}={d[k]}cp không phải bội {LOT} (artifact trả qty lẻ) — làm tròn "
                    f"XUỐNG {lo}cp thay vì từ chối cả plan.")
                d[k] = lo
        qty = d["final_L1"] + d["final_L2"]
        report["per_ticker"][tk].update(
            {"L1_final": d["final_L1"], "L2_final": d["final_L2"], "qty": qty})
        if qty <= 0:
            report["notes"].append(f"{tk}: qty cuối = 0 sau khi áp trần — không sinh lệnh.")
            continue
        px = d["ref_price"]
        val = int(round(qty * px))
        srcs = [s for s in ("L1", "L2") if d[f"final_{s}"] > 0]
        ptype = {("L1",): "PARK_TRIM", ("L2",): "JIT_UNPARK",
                 ("L1", "L2"): "PARK_TRIM+JIT_UNPARK"}[tuple(srcs)]
        generated.append({
            "id": f"{ID_PREFIX}-{tk}",
            "ticker": tk, "side": "sell", "qty": qty, "ref_price": px,
            "order_type": "LO", "book": "PARK", "play_type": ptype,
            "priority": sell_pri, "urgency": "normal",
            "estimated_proceeds_vnd": val,
            "fee_est_vnd": int(round(val * 0.00075)),
            "sellable": d["sellable"],
            # ── dấu SỞ HỮU: mọi lần chạy sau sẽ xoá đúng các lệnh này rồi dựng lại ───
            "merge_owner": OWNER,
            "merged_from": {"L1_park_trim_qty": d["final_L1"],
                            "L2_jit_unpark_qty": d["final_L2"],
                            "L1_proposed_qty": d["L1"], "L2_proposed_qty": d["L2"],
                            "sellable_at_calc": d["sellable"],
                            "foreign_sell_qty": d["foreign_sell_qty"],
                            "for_order_ids": sorted(set(d["for_orders"]))},
            "note": (f"BÁN PARK gộp: L1 {d['final_L1']}cp + L2 {d['final_L2']}cp = {qty}cp × "
                     f"{px:,.0f}đ = {val:,}đ."),
            "reason": ("Gộp 2 nguồn đề xuất bán PARK cùng mã thành 1 lệnh. L2 chạy với --l1-json "
                       "nên phần lô L1 đã giữ chỗ bị trừ trước khi L2 đề xuất thêm ⇒ cộng dồn "
                       "KHÔNG phải bán trùng; merge vẫn tự kiểm lại tổng ≤ sellable."),
            "stop_exempt": False, "slot_exempt": False,
        })
    report["generated"] = [{"id": o["id"], "ticker": o["ticker"], "qty": o["qty"],
                            "play_type": o["play_type"]} for o in generated]

    # ── 4b. CỔNG "ARTIFACT VẮNG MẶT KHÔNG ĐƯỢC LÀM MẤT LỆNH" ─────────────────────────
    # Khuyết tật này CHỈ tồn tại khi cơ chế thành BƯỚC PIPELINE, nên 10 vòng quant-skeptic
    # trước (verify script ĐỨNG RIÊNG) không thể thấy: `main()` đọc artifact bằng
    # `_read_json()`, file THIẾU ⇒ `None` ⇒ `_layer_state` trả "bỏ qua tầng này (không phải
    # lỗi)" ⇒ bước 1 vẫn XOÁ sạch vùng sở hữu (kể cả lệnh NHẬN NUÔI của writer khác) ⇒
    # `status=OK` ⇒ `--write` GHI ĐÈ. Đo thật trước khi vá: plan 1.300cp bán PARK + 1 lệnh
    # mua DRI ⇒ sau merge còn ĐÚNG lệnh mua, 0 lệnh bán, status OK. Đó là đúng hình dạng
    # mất-phiên 08-06 (lệnh mua không còn nguồn tài trợ), và nguy hiểm hơn vì L1/L2 hiện
    # KHÔNG có cron ⇒ artifact vắng mặt là trạng thái THƯỜNG, không phải ngoại lệ.
    #
    # Người chạy tay đọc báo cáo thì thấy dòng "L1: không có artifact"; một bước cron thì
    # KHÔNG AI đọc — cùng một hành vi, hai mức độ nguy hiểm khác hẳn nhau.
    #
    # Phân biệt DỨT KHOÁT hai thứ mà bản cũ gộp làm một:
    #   · artifact CÓ MẶT và nói "không bán" (decision=NO_JIT/BLOCKED_RECONCILE, 0 lệnh) —
    #     phát biểu CÓ THẨM QUYỀN ⇒ xoá là ĐÚNG, không chặn;
    #   · artifact VẮNG MẶT — ta KHÔNG BIẾT gì cả ⇒ không được suy ra "không bán".
    # Chỉ chặn khi sự vắng mặt đó THỰC SỰ làm mất lệnh: so qty TRƯỚC/SAU theo TỪNG MÃ.
    # Nhờ so theo lượng (không phải "có drop hay không"), chạy lại lần 2 với cùng artifact
    # vẫn dựng lại đúng lượng cũ ⇒ KHÔNG mất ⇒ vẫn idempotent (ca A6c).
    absent = [nm for nm, art in (("L1 park_trim", l1), ("L2 jit_unpark", l2)) if art is None]
    if absent:
        before_by_tk = {}
        for dp in report["dropped_owned"]:
            before_by_tk[dp["ticker"]] = before_by_tk.get(dp["ticker"], 0) + _i(dp["qty"])
        after_by_tk = {o["ticker"]: _i(o["qty"]) for o in generated}
        lost = {tk: (b, after_by_tk.get(tk, 0)) for tk, b in before_by_tk.items()
                if after_by_tk.get(tk, 0) < b}
        if lost:
            return refuse(
                "ARTIFACT VẮNG MẶT (" + ", ".join(absent) + ") mà việc dựng lại làm MẤT lệnh "
                "bán đã có: " + ", ".join(f"{tk} {b}cp→{a}cp" for tk, (b, a) in sorted(lost.items()))
                + ". Vắng mặt ≠ 'không cần bán' — không có artifact thì KHÔNG BIẾT, và đoán "
                "theo hướng xoá sẽ bỏ đói lệnh mua đang được tài trợ (hình dạng 08-06). "
                "Cách xử lý ĐÚNG: chạy lại L1/L2 để có artifact thật cho phiên này (kể cả khi "
                "kết quả là decision=NO_JIT/BLOCKED_RECONCILE — artifact CÓ MẶT nói 'không "
                "bán' thì merge chấp nhận xoá). KHÔNG ghi gì.")

    p["orders"] = generated + foreign

    # ── 5. chú thích lệnh MUA từ buy_amendments (KHÔNG đổi qty) ──────────────────────
    if l2_ok:
        by_id = {o.get("id"): o for o in p["orders"]}
        for ja in (l2.get("buy_amendments") or []):
            oid = ja.get("order_id")
            tgt = by_id.get(oid)
            if tgt is None:
                report["warnings"].append(
                    f"L2 buy_amendments trỏ order_id={oid!r} KHÔNG có trong orders[] — bỏ qua "
                    f"(không tạo lệnh mới từ amendment).")
                continue
            # Gán thẳng là ĐƯỢC: bước 0 xoá theo TIỀN TỐ `jit_` nên nhãn nào thêm ở đây cũng
            # nằm sẵn trong tập xoá, không cần ai nhớ khai báo (xem `_JIT_PREFIX`).
            tgt["jit_status"] = ja.get("status")
            tgt["jit_note"] = ja.get("reason", "")
            qf = ja.get("qty_final")
            if qf is not None and _i(qf) != _i(tgt.get("qty")):
                report["warnings"].append(
                    f"{oid}: L2 qty_final={qf} ≠ qty trong plan={tgt.get('qty')} — GIỮ NGUYÊN "
                    f"qty của plan (merge KHÔNG đổi cỡ lệnh mua), chỉ ghi chú.")
            # L2 cấp vốn theo GÓI cho toàn bộ lệnh mua trong plan ⇒ bất kỳ mã nào bị cắt L2
            # cũng làm hụt nguồn của lệnh mua này. Gắn cờ để người duyệt thấy TRƯỚC, không
            # để P0 check_plan_funding phát hiện hộ lúc 09:05.
            if any(v.get("cut_L2") for v in report["per_ticker"].values()):
                tgt["jit_underfunded"] = True

    # ── 6. cổng duyệt + audit trail ──────────────────────────────────────────────────
    p["requires_user_approval"] = True
    for key, art, ok, why in (("park_trim_proposal", l1, l1_ok, l1_why),
                              ("jit_unpark_proposal", l2, l2_ok, l2_why)):
        if art is None:
            # Artifact VẮNG MẶT lần chạy này ⇒ XOÁ khối cũ, không `continue`. Khuyết tật #6
            # (quant-skeptic vòng 4, 2026-08-10 — cùng lớp với #5, ở tầng khối đề xuất thay
            # vì tầng nhãn): chạy 1 có L2 ⇒ ghi `jit_unpark_proposal` dán "✅ ĐÃ MERGE";
            # chạy 2 mất file artifact ⇒ `continue` để khối đó Y NGUYÊN trong khi orders[]
            # chỉ còn phần L1 ⇒ người duyệt đọc một khối kiểm toán KHÔNG khớp lệnh thật.
            # Cùng quy tắc với vùng bán và với 3 nhãn: DỰNG-LẠI-HOẶC-VẮNG-MẶT.
            # Khoá thuộc namespace `jit_` đã bị bước 0b xoá rồi ⇒ HỎI BẢN GHI của bước đó.
            # `p.pop()` lần hai luôn trả None ⇒ cảnh báo VẮNG MẶT (chính bản vá #6) sẽ lặng
            # lẽ biến mất — bản mở rộng phạm vi tự bắn vào chân bản vá trước nếu không có
            # nhánh này. `park_trim_proposal` nằm NGOÀI namespace nên vẫn tự xoá tại đây.
            had_old = (key in plan_jit_removed if str(key).startswith(_JIT_PREFIX)
                       else p.pop(key, None) is not None)
            if had_old:
                report["warnings"].append(
                    f"{key}: artifact VẮNG MẶT lần chạy này — đã XOÁ khối kiểm toán cũ khỏi "
                    f"plan (khối cũ mô tả một lần chạy KHÁC, giữ lại là gây hiểu nhầm).")
            continue
        c = copy.deepcopy(art)
        c["_merged_into_orders"] = (
            "✅ ĐÃ MERGE vào orders[] (merge_owner=park_merge_v1). Giữ làm NGUỒN KIỂM TOÁN — "
            "KHÔNG thực thi riêng." if ok else f"⛔ KHÔNG merge vào orders[] — {why}")
        p[key] = c

    # Khoá `jit_*` cấp plan của writer KHÁC (bước 0b đã xoá): khai ra tên từng khoá, đừng xoá
    # im lặng. Merge KHÔNG dựng lại chúng — đó chính là nội dung của "dựng-lại-HOẶC-VẮNG-MẶT"
    # áp cho một khoá merge không sinh ra: nó vắng mặt.
    for k in plan_jit_removed:
        if k == "jit_unpark_proposal":
            continue
        report["warnings"].append(
            f"{k}: khoá `jit_*` CẤP PLAN do writer khác ghi — đã XOÁ (merge sở hữu toàn bộ "
            f"không gian tên `jit_*`; nội dung cũ mô tả một lần chạy L2 KHÁC). Muốn ghi chú "
            f"sống qua merge thì đặt tên KHÔNG bắt đầu bằng `jit_`.")

    # ── 7. BẤT BIẾN HẬU KIỂM trên TOÀN BỘ orders[] ───────────────────────────────────
    inv = _check_invariants(p["orders"], agg, orig_orders)
    report["invariants"] = inv["checks"]
    if inv["failed"]:
        report["status"] = "REFUSED"
        report["errors"].extend(inv["failed"])
        return copy.deepcopy(plan), report

    p["merge_park_orders"] = {
        "owner": OWNER,
        "layers": report["layers"],
        "n_generated": len(generated),
        "n_dropped_owned": len(report["dropped_owned"]),
        "sell_gross_vnd": sum(o["estimated_proceeds_vnd"] for o in generated),
        "sell_fee_est_vnd": sum(o["fee_est_vnd"] for o in generated),
        "warnings": report["warnings"],
        "note": ("orders[] phần bán PARK được DỰNG LẠI mỗi lần chạy (không cộng dồn). "
                 "Chạy lại merge với artifact mới = kết quả mới đúng, không phải chồng lên."),
    }
    return p, report


def _check_invariants(orders, agg, orig_orders):
    """Bất biến hậu kiểm — chạy trên MỌI lệnh, không riêng lệnh merge sinh ra."""
    failed, checks = [], []

    ids = [o.get("id") for o in orders]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    checks.append(("I1 id duy nhất", not dup, f"trùng: {dup}" if dup else "ok"))
    if dup:
        failed.append(f"I1: id trùng trong orders[]: {dup}")

    # I2 — Σ qty bán mỗi mã ≤ sellable. Đây là bất biến bắt được bán trùng KỂ CẢ khi lệnh
    # thừa do writer khác ghi (dedup theo id mù hoàn toàn với ca này — lỗi 08-07).
    sell_by_tk, cap_by_tk = {}, {}
    for o in orders:
        if str(o.get("side", "")).lower() != "sell":
            continue
        tk = o.get("ticker")
        sell_by_tk[tk] = sell_by_tk.get(tk, 0) + max(0, _i(o.get("qty")))
        s = o.get("sellable")
        if s is not None and _i(s, None) is not None:
            cap_by_tk[tk] = min(cap_by_tk.get(tk, 10**12), _i(s))
    for tk, d in agg.items():
        if d.get("sellable") is not None:
            cap_by_tk[tk] = min(cap_by_tk.get(tk, 10**12), d["sellable"])
    over = {tk: (q, cap_by_tk[tk]) for tk, q in sell_by_tk.items()
            if tk in cap_by_tk and q > cap_by_tk[tk]}
    checks.append(("I2 Σ bán/mã ≤ sellable", not over, f"vượt: {over}" if over else "ok"))
    if over:
        failed.append(f"I2: BÁN VƯỢT SELLABLE {over} — đúng lớp lỗi 2026-08-07, dừng.")

    # I3 — CHỈ ràng buộc lệnh bán DO MERGE SINH RA phải chạy trước mọi lệnh mua. Lệnh bán của
    # writer khác nằm sau lệnh mua là vấn đề CÓ SẴN, không do merge tạo ra: từ chối cả plan vì
    # nó = lấy plan làm con tin cho một lỗi mình không gây ra, đúng hình dạng mất-phiên 08-06.
    # ⇒ cảnh báo, không chặn. (Khác ca S6 "lệnh ngoài vùng đã vượt sellable" — ở đó CHẠY TIẾP
    # làm tình trạng vi phạm NẶNG THÊM, nên mới phải fail-closed.)
    buy_pri = [_i(o.get("priority"), 5) for o in orders
               if str(o.get("side", "")).lower() == "buy"]
    own_sell_pri = [_i(o.get("priority"), 5) for o in orders
                    if str(o.get("side", "")).lower() == "sell" and is_owned(o)]
    ok3 = (not buy_pri) or (not own_sell_pri) or (max(own_sell_pri) < min(buy_pri))
    checks.append(("I3 lệnh bán MERGE chạy trước mua", ok3,
                   f"sell_pri={sorted(set(own_sell_pri))} buy_pri={sorted(set(buy_pri))}"))
    if not ok3:
        failed.append(
            f"I3: priority lệnh bán merge {sorted(set(own_sell_pri))} không < mua "
            f"{sorted(set(buy_pri))}")

    late_foreign = sorted(
        o.get("id") for o in orders
        if str(o.get("side", "")).lower() == "sell" and not is_owned(o) and buy_pri
        and _i(o.get("priority"), 5) >= min(buy_pri))
    checks.append(("I3b lệnh bán NGOÀI vùng merge chạy trước mua", not late_foreign,
                   f"cảnh báo (không chặn): {late_foreign}" if late_foreign else "ok"))

    # I4 — CẢNH BÁO, không chặn. Lệnh do merge sinh ra đã được làm tròn bội lô vô điều kiện ở
    # bước sinh, nên nhánh này chỉ còn bắt lệnh "trông giống của merge" do writer khác ghi. Từ
    # chối cả plan vì một qty lẻ = lại đúng hình dạng mất-phiên 08-06 (quant-skeptic vòng 2).
    bad = [o.get("id") for o in orders if is_owned(o)
           and (_i(o.get("qty")) <= 0 or _i(o.get("qty")) % LOT != 0)]
    checks.append(("I4 qty > 0 và bội lô", not bad,
                   f"cảnh báo (không chặn): {bad}" if bad else "ok"))

    # I5 — không đánh rơi lệnh của người khác
    keep_before = {o.get("id") for o in orig_orders if not is_owned(o)}
    keep_after = {o.get("id") for o in orders if not is_owned(o)}
    lost = sorted(keep_before - keep_after)
    checks.append(("I5 không mất lệnh ngoài vùng sở hữu", not lost,
                   f"mất: {lost}" if lost else "ok"))
    if lost:
        failed.append(f"I5: đánh rơi lệnh không thuộc vùng merge: {lost}")

    return {"failed": failed, "checks": [{"name": n, "ok": bool(k), "detail": d}
                                         for n, k, d in checks]}


# ══════════════════════════════════════════════════════════════════════════════════════
# I/O + CLI
# ══════════════════════════════════════════════════════════════════════════════════════
def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _atomic_write_json(path, obj):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def print_report(rep):
    print(f"status: {rep['status']}")
    for k in ("L1", "L2"):
        print(f"  {k}: {'✔' if rep['layers'][k]['accepted'] else '✘'} {rep['layers'][k]['reason']}")
    if rep["dropped_owned"]:
        print(f"  xoá {len(rep['dropped_owned'])} lệnh thuộc vùng sở hữu (dựng lại):")
        for d in rep["dropped_owned"]:
            print(f"    − {d['id']} {d['ticker']} {d['qty']}cp "
                  f"({'có dấu' if d['tagged'] else 'DI SẢN, không dấu'})")
    for t, d in sorted(rep["per_ticker"].items()):
        if d["qty"]:
            print(f"    {t:<5} {d['qty']:>6}cp  (L1 {d['L1_final']} + L2 {d['L2_final']}) "
                  f"sellable={d['sellable']} khác={d['foreign_sell_qty']}")
    for c in rep.get("invariants", []):
        print(f"  {'✔' if c['ok'] else '✘'} {c['name']}: {c['detail']}")
    for w in rep["warnings"]:
        print(f"  ⚠ {w}")
    for e in rep["errors"]:
        print(f"  ✘ {e}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--plan-date", required=True)
    ap.add_argument("--plan-dir", default=DEFAULT_PLAN_DIR)
    ap.add_argument("--l1-json", default=None, help="mặc định park_trim_{acct}_{date}.json")
    ap.add_argument("--l2-json", default=None, help="mặc định jit_unpark_{acct}_{date}.json")
    ap.add_argument("--write", action="store_true",
                    help="ghi thật (mặc định chỉ in báo cáo, KHÔNG ghi)")
    ap.add_argument("--force-clear-approval", action="store_true",
                    help="plan đã duyệt: XOÁ approved_by và dựng lại (bắt buộc duyệt lại)")
    a = ap.parse_args(argv)

    d = a.plan_dir
    plan_path = os.path.join(d, f"plan_{a.account}_{a.plan_date}.json")
    plan = _read_json(plan_path)
    if plan is None:
        print(f"❌ không có plan: {plan_path}", file=sys.stderr)
        return 2
    l1 = _read_json(a.l1_json or os.path.join(d, f"park_trim_{a.account}_{a.plan_date}.json"))
    l2 = _read_json(a.l2_json or os.path.join(d, f"jit_unpark_{a.account}_{a.plan_date}.json"))

    new_plan, rep = merge_park_orders(plan, l1, l2,
                                      allow_approved=a.force_clear_approval)
    print(f"== {a.account} {a.plan_date} ==")
    print_report(rep)
    if rep["status"] != "OK":
        print("KHÔNG ghi gì (fail-closed).", file=sys.stderr)
        return 1
    if not a.write:
        print("[dry-run] KHÔNG ghi. Thêm --write để ghi thật.")
        return 0
    _atomic_write_json(plan_path, new_plan)
    print(f"✅ đã ghi {plan_path} — {len(new_plan['orders'])} lệnh, "
          f"approved_by={new_plan.get('approved_by')!r} (luôn cần user duyệt).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

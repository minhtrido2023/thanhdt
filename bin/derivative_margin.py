#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tài sản tiểu khoản PHÁI SINH trong NAV — một nguồn công thức cho mọi consumer NAV.

VÌ SAO (job Taylor_20261117_092943): 17/11/2026 user nộp 4.999.059đ ký quỹ phái sinh vào SpaceX
(sleeve ORB, kb/projects/orb-futures-sleeve-20261116.md §7). Tiền đó RỜI `balances.stock.totalCash`
sang `balances.derivative` ⇒ NAV cũ (cổ phiếu + totalCash − totalDebt + egg) tụt đúng bằng số ký
quỹ dù tiền vẫn là của tài khoản.

ĐÃ XÁC MINH (probe read-only 17/11 ~17:00 ICT, agents/Taylor/research/nav_deriv_20261117/probe_1700.json):
  · SpaceX: `derivative.remainSecure` = 4.999.059 = 5.000.000 chuyển vào − 941 còn ở tiền cơ sở
    (`stock.totalCash` 1.640 → 2.581, +941); usedSecure = pendingSecure = holdTaxAndFee =
    totalLoanDebt = pendingDepositWithdraw = 0; positions(marketType=DERIVATIVE) rỗng.
  ⇒ KHI KHÔNG CÓ VỊ THẾ và mọi field khác = 0: tài sản phái sinh = `remainSecure` (khớp tới đồng).

CHƯA XÁC MINH (chưa từng thấy ≠ 0 trên dữ liệu thật): ý nghĩa `usedSecure` (ký quỹ đang dùng —
NẰM TRONG hay NGOÀI remainSecure?), `pendingSecure`, `holdTaxAndFee`, `totalLoanDebt`,
`pendingDepositWithdraw`, và KHÔNG có field lãi/lỗ chưa thực hiện nào trong block này.
⇒ FAIL-CLOSED: bất kỳ field chưa xác minh nào ≠ 0, hoặc có vị thế phái sinh mở, hoặc không đọc được
vị thế khi đang có ký quỹ ⇒ trả LÝ DO từ chối; caller KHÔNG ghi NAV (không đoán công thức cộng).
Xác minh xong field nào thì chuyển nó từ UNVERIFIED_FIELDS sang công thức, kèm bằng chứng probe.

KHÔNG dùng cho mẫu số sizing cổ phiếu (`compute_active_nav.py`) — tiền ký quỹ bị ràng buộc cho
sleeve ORB, không mua được cổ phiếu (xem docstring compute_active_nav §derivative).
"""
import math

VERIFIED_FIELD = "remainSecure"
UNVERIFIED_FIELDS = ("usedSecure", "pendingSecure", "holdTaxAndFee", "totalLoanDebt",
                     "pendingDepositWithdraw")


def _num(block, key):
    v = block.get(key)
    if v is None:
        return 0.0
    try:
        f = float(v)
    except (TypeError, ValueError):
        raise ValueError(f"derivative.{key}={v!r} không phải số")
    if not math.isfinite(f):
        raise ValueError(f"derivative.{key}={v!r} không hữu hạn")
    return f


def derivative_assets(payload, positions=None, positions_required=True):
    """→ (VND, None) nếu tin được; (None, lý_do) nếu phải chặn ghi NAV.

    `payload`: payload bản ghi `balances` (dict có `stock`/`derivative`/`egg`).
    `positions`: list vị thế DERIVATIVE đọc từ broker; None = KHÔNG đọc được/không có.
    `positions_required`: True (đường live) ⇒ đang có ký quỹ mà positions=None là chặn.
      False chỉ dùng cho backfill `--from-raw` (dòng đó đã gắn nav_is_estimate=True) và reconcile
      lịch sử — khi đó dựa vào usedSecure==0 (ký quỹ đang dùng bắt buộc >0 nếu có vị thế — GIẢ
      ĐỊNH chưa kiểm chứng, nên chỉ chấp nhận ở đường đã là ước tính/đối soát).
    Block `derivative` vắng (raw cũ) ⇒ (0, None): đúng hành vi trước khi có sleeve.
    """
    block = (payload or {}).get("derivative")
    if not block:
        return 0.0, None
    if not isinstance(block, dict):
        return None, f"block derivative không phải object: {block!r}"
    try:
        remain = _num(block, VERIFIED_FIELD)
        nonzero = {k: _num(block, k) for k in UNVERIFIED_FIELDS if _num(block, k) != 0}
    except ValueError as e:
        return None, str(e)
    if nonzero:
        return None, ("block derivative có field CHƯA XÁC MINH ý nghĩa ≠ 0: "
                      + ", ".join(f"{k}={v:,.0f}" for k, v in nonzero.items())
                      + f" (remainSecure={remain:,.0f}) — không đoán công thức cộng; probe "
                        "balances+positions DERIVATIVE rồi cập nhật derivative_margin.py")
    if remain < 0:
        return None, f"derivative.remainSecure âm ({remain:,.0f})"
    if positions:
        return None, (f"có {len(positions)} vị thế phái sinh MỞ nhưng chưa có field lãi/lỗ chưa "
                      f"thực hiện đã xác minh — không định giá được NAV phái sinh")
    if positions is None and remain > 0 and positions_required:
        return None, (f"đang có ký quỹ phái sinh {remain:,.0f}đ nhưng KHÔNG đọc được vị thế "
                      f"DERIVATIVE — không chứng minh được tài khoản phái sinh đang phẳng")
    return remain, None


def read_derivative_positions(client, account_no):
    """Vị thế DERIVATIVE từ DNSE (read-only). → list, hoặc None nếu lỗi (caller fail-closed)."""
    try:
        r = client.positions(account_no, market_type="DERIVATIVE")
    except Exception:
        return None
    if isinstance(r, dict) and isinstance(r.get("positions"), list):
        return r["positions"]
    return None

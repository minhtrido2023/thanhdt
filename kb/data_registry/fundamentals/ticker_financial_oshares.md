---
kind: bigquery-column
status: TRAP
source: tav2_bq.ticker_financial.OShares
group: fundamentals
writer: Ingest BCTC quý (cùng đường với `ticker_financial`) — nhưng giá trị bị GHI ĐÈ về sau
---

# `tav2_bq.ticker_financial.OShares` — số cổ phiếu lưu hành theo quý

**Status: TRAP.** Cột này **KHÔNG point-in-time**. Nó bị **RESTATE**: một dòng quý cũ được ghi
đè về sau để mang số cổ phiếu tại thời điểm CÔNG BỐ (hoặc muộn hơn nữa). Đọc nó trong một
backtest / một câu hỏi "ngày D số CP lưu hành là bao nhiêu" là **look-ahead**.

## Là gì
Số cổ phiếu đang lưu hành, một dòng mỗi quý mỗi mã. Là **mẫu số** của vốn hoá, EPS, và mọi chỉ
tiêu per-share.

## Bẫy (1) — RESTATE, không phải "dữ liệu sớm"

Đo thật **2026-08-13** trên toàn bảng (định nghĩa: dòng quý có `OShares` trùng khít — sai số
<1 cổ phiếu — với `shares_total_after` của một `AIS` *executed* có `effective_date` **SAU** ngày
dòng quý đó):

| Lát cắt | Số dòng | Số mã | Sớm nhất |
|---|---:|---:|---:|
| Toàn bảng | **2.667** | **576** | **2.693 ngày** |
| Từ 2024-01-01 | **626** | **247** | **819 ngày** |
| Từ 2024-01-01, **look-ahead CỨNG** (có ít nhất một `ISS` *executed* đi ex SAU dòng quý và trước/bằng AIS đó ⇒ ngày ghi dòng quý sự kiện còn chưa xảy ra) | **145** | **75** | — |

Ca cụ thể để nhớ: **HAH**, dòng quý ngày **2026-02-02** đã mang **185.840.401** — con số chỉ ra
đời cùng `AIS` ngày **2026-05-27** (niêm yết thêm 16.979.189 CP từ chuyển đổi trái phiếu
**2026-03-12** và ESOP **2026-04-17**, cả hai đều SAU 02-02). Sự thật ngày 2026-03-01 là
**168.861.212**.

⚠️ Không được đọc bảng trên thành "cột này nhanh hơn AIS nên dùng được". **Vừa có** restatement
(giả) **vừa có** dữ liệu sớm thật, và nhìn vào một dòng thì không phân biệt được. Ca dữ liệu sớm
THẬT: **FPT** dòng quý **2025-07-22** mang số sau thưởng 1.703.507.121, đúng **một ngày** sau
ex-right 07-21 và **7 tuần** trước AIS — số này có căn cứ. Cách duy nhất tách được hai loại là
**bắt dòng quý tự giải thích**: lăn `AIS` gần nhất TRƯỚC nó qua các `ISS` ở giữa; khớp trong 0,1%
thì nhận, không khớp thì loại.

## Bẫy (2) — không có `shares_delta` để cứu, và `exercise_ratio` rỗng ở đúng nhóm nguy hiểm

Khi phải tự lăn số CP tiến lên từ một mốc, `tav2_bq.corporate_action` cũng có bẫy riêng (đo cùng
ngày): `exercise_ratio` = 0 hoặc NULL ở **3.914/9.297** dòng `ISS` *executed* (**42%**), tập
trung đúng vào nhóm **không** phát sinh quyền cho cổ đông hiện hữu — riêng lẻ 2.187/2.280, ESOP
1.105/1.222, chuyển đổi TP 240/243, đấu giá 140/142, sáp nhập 85/99. Nhân `(1 + 0)` ở đó là một
**no-op** nhưng dễ bị gắn nhãn "đã tính". `shares_delta` **NULL trên 100%** dòng `ISS`
(0/9.297) — nó chỉ có ở `AIS`/`NLIS`/`SUSP`. ⇒ Không có tỉ lệ mà cũng không có delta thì phải
**fail CLOSED**, không được trả số.

## Dùng gì thay

`oshares_live.py` (repo `WorkingClaude`) — neo chính là `AIS.shares_total_after`, chỉ nhận dòng
`ticker_financial` khi nó **tự giải thích được**, và trả `value=None` (`UNKNOWN_RATIO`) khi có
`ISS` không xác định được cỡ. **WIRE** từ 2026-08-13 (3 consumer:
`custom30_core_select_audit.py`, `rating_8l.py::_reconcile_oshares`, `mike/bin/corp_action_daily.py`).

**Neo `AIS` cũng có cổng, từ 2026-08-13 vòng 4** (`Taylor_20260813_154112`): feed vendor có dòng
`AIS` SAI (IDC 2020-05-28 ghi 3.000.000.000 khi AIS liền trước là 300.000.000), nên
`AIS.shares_total_after` chỉ được phục vụ khi **đối chiếu được với AIS liền trước** — qua
`roll(prev, ISS ở giữa)` HOẶC `prev + shares_delta`, khớp 1 trong 2 là đủ. Không đối chiếu được ⇒
`value=None`, nhãn **`AIS_UNCERTIFIED`**, số bị từ chối giữ ở `uncertified_value` để ghi log.
Cổng nằm TRONG `oshares_live` (trước đó ở `oshares_pit`, nên gọi thẳng `oshares_at()` vẫn ăn số
sai) ⇒ **mọi đường gọi đều bị chặn, kể cả gọi thẳng**.

Nhãn `ANCHOR_UNVERIFIED` (mã chưa từng có `AIS` nào, vd DHG) = số vẫn trả nhưng **chưa kiểm
chứng được** — consumer cần số đã kiểm phải coi như miss.

## Giới hạn còn lại (không đóng được từ phía này)

Cổng "tự giải thích" chỉ loại được restatement khi nó **mâu thuẫn với sự kiện feed đã có**. Một
dòng bị restate về con số mà `AIS` hậu thuẫn **chưa được ingest** thì cổng không thấy — điểm mù
chung của mọi tái dựng point-in-time.

## Liên quan
- [`ticker_financial.md`](ticker_financial.md) — bảng chứa cột này (CANONICAL cho các cột khác)
- [`../price-volume/shares_outstanding_live.md`](../price-volume/shares_outstanding_live.md)
- [`../price-volume/ticker_close_vs_price_dividend_adj.md`](../price-volume/ticker_close_vs_price_dividend_adj.md)

## Nguồn
Job `Taylor_20260813_050945` (đo lại + vá sau khi quant-skeptic REFUTED vòng 1 của job
`Taylor_20260813_041648`) · báo cáo `mike/agents/Taylor/research/corp_action_wire_20260813.md`.

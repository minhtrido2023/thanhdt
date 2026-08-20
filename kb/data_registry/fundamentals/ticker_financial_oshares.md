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

## HAI NHÁNH, KHÁC NHAU ĐÚNG MỘT ĐIỀU KIỆN — chọn nhánh theo CÂU HỎI, không theo tiện tay

Từ 2026-08-20 (`oshares_at(..., live=)`, job `Taylor_20260820_015520`) hàm có hai nhánh. Chọn sai
nhánh không báo lỗi — nó chỉ trả một con số của câu hỏi khác.

| Câu hỏi | Gọi | Vì sao |
|---|---|---|
| "**HÔM NAY** có bao nhiêu CP lưu hành?" (publish snapshot, đối soát, sizing) | `live=True` | fail-closed ở đây = câm về một sự thật ĐÃ CÔNG BỐ; look-ahead vô nghĩa vì không có "tương lai" nào để nhìn trộm |
| "Tại ngày T trong quá khứ, người ta BIẾT bao nhiêu?" (backtest, `oshares_pit`) | `live=False` (**mặc định**) | look-ahead đắt hơn fail-closed; giữ nguyên vẹn, KHÔNG đổi một số nào so với trước 2026-08-20 |

**Chính sách nền (2026-08-19, `FIN_FALLBACK`)** — chỉ đạo user: *dữ liệu từ BCTC mới nhất là dữ
liệu tươi nhất, TRỪ KHI có phát sinh sự kiện giữa 2 kỳ báo cáo; BCTC vẫn là CHUẨN re-baseline mỗi
quý*. Khi neo `AIS` đã cũ hơn `FIN_FALLBACK_MAX_AIS_AGE_DAYS` = **90 ngày** và dòng `ticker_financial`
MỚI HƠN ngày neo, dòng quý được phục vụ với nhãn **`FIN_FALLBACK`** (`anchor_verified=False`),
KHÔNG xét chiều tăng/giảm.

**Khác biệt của nhánh LIVE (2026-08-20)** — đúng MỘT điều kiện đảo chiều: neo `AIS`
**chưa chứng nhận** (`AIS_UNCERTIFIED`) không còn chặn được một dòng BCTC MỚI HƠN nó. Lý lẽ: chuỗi
`AIS` gãy là bằng chứng chống lại **chính AIS**, không phải chống lại BCTC — nó làm BCTC đáng tin
hơn một cách tương đối. Bằng chứng sống cùng ngày: **TCB** — dòng quý 2026-07-21 = 7.086.240.414 bị
cổng loại 2 tuần liền (lệch +0,30% so với chuỗi AIS); ngày 08-05 `AIS` mới về và
`shares_total_after` của nó = **đúng con số BCTC đã nói từ 07-21**. BCTC đi TRƯỚC `AIS` và ĐÚNG.

**Ba điều kiện KHÔNG đổi ở cả hai nhánh** (nới thêm là đổi chính sách, không phải sửa lỗi):
2 — neo `AIS` còn tươi ≤90 ngày thì không rơi về BCTC; 3 — dòng quý CŨ hơn neo `AIS` thì rơi về
BCTC là đi LÙI ⇒ từ chối; và **cổng chứng nhận neo `AIS` không bị nới**: không có dòng quý nào để
nhường thì neo uncertified vẫn `AIS_UNCERTIFIED` dưới `live=True`.

### CÁI GIÁ, ĐO ĐƯỢC — 21 ăn 1

Rổ 263 mã `ticker_prune` tại asof=2026-03-01, đối chiếu bằng 5,5 tháng dữ liệu tương lai
(`mike/agents/Taylor/research/oshares_live_anchor_20260820/lookahead_cost_probe.py` →
`cost_20260301.json`). CẢ HAI nhánh đo lại trên CÙNG rổ — rổ "246 mã" của phép đo 08-19 không tái
lập được, và so hai con số trên hai rổ là so hai thứ khác nhau.

- **ĐƯỢC**: PIT từ chối 28/263, LIVE từ chối **7/263** ⇒ nhánh LIVE cứu **21 mã** (+8,0pp phủ). Cả
  21 đều đi đúng một đường `AIS_UNCERTIFIED → FIN_FALLBACK` — nhánh mới không rò sang hành vi khác.
- **MẤT**: chữ ký RESTATE trên neo không kiểm chứng được (`FIN_FALLBACK`/`ANCHOR_UNVERIFIED` — con
  đường DUY NHẤT một số tương lai vào được câu trả lời) đi từ 4 mã (ABB, HAH, NVL, TDC) lên **5**:
  thêm ĐÚNG **1 mã — KBC** (941.754.759 = `AIS` 2026-06-25).
- ⚠️ **KHÔNG trích con số "RESTATE thô" (11 → 12)**: 7/11 ca của nhánh PIT có neo `ANCHOR_ONLY`, tức
  dòng quý ĐÃ đối chiếu xong với chuỗi `AIS` — một mã không đổi số CP thì `AIS` kế tiếp trùng khít
  một cách hoàn toàn vô tội, đó không phải look-ahead.
- Kiểm chứng chéo: `FIN_FALLBACK`-RESTATE của nhánh PIT ra ĐÚNG 3 mã ABB/HAH/NVL — khớp tuyệt đối
  con số 3 đã ghim ở phép đo 08-19, đo độc lập trên một rổ khác.

⇒ Con số phải nhắc lại khi ai đó muốn siết/nới nhánh này là **1 mã**, không phải 12.

### Consumer phải lọc bằng FIELD, không bằng cách đọc `reason`

Bản ghi phục vụ qua nhánh LIVE mang `anchor_verified=False`, `fin_anchor_ais_certified=False`,
`fin_branch_live=True`. Backtest cần số đã kiểm chứng ⇒ coi `method == "FIN_FALLBACK"` là miss.

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

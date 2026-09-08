---
kind: bigquery-table
status: PARTIAL
source: lithe-record-440915-m9.tav2_bq.treasury_news
group: price-volume
scope: tin tức mua/bán cổ phiếu quỹ (treasury buyback) per mã — nguồn NGÀY + HƯỚNG cho lớp lỗi
  ticker_financial.OShares bị restate sớm khi có sự kiện treasury
writer: UNKNOWN — không script/cron nào trong repo Mike ghi bảng này (grep sạch, 2026-09-07)
---

# `tav2_bq.treasury_news`

**Status: PARTIAL.** Bảng mới, chưa từng có trong registry trước job `Taylor_20260907_160333`
(tạo 2026-09-04 theo dispatch — grep xác nhận 2026-09-07: 0 tham chiếu trong repo Mike trước job
này). Đúng chỗ để lấy **ngày hiệu lực thật + hướng** của một sự kiện buyback, nhưng **KHÔNG đủ để
tự đứng một mình** — 2 giới hạn số liệu đo được dưới đây khiến nó phải phối hợp với
[`../fundamentals/ticker_financial_oshares.md`](../fundamentals/ticker_financial_oshares.md) mới
dùng được.

## Là gì

Tin tức per-mã liên quan cổ phiếu quỹ, 2.371 dòng (đo `bq` CLI 2026-09-07, `--max_rows=200000` —
mặc định 100 dòng của `bq` CLI cắt mất dữ liệu, xem CLAUDE.md gốc §BigQuery).

`action_type`: `buy` 833 · `sell` 569 · `buy_done` 369 · `other` 366 · `sell_done` 214 ·
`cancel` 20. **232 mã** có ≥1 dòng `buy_done`/`sell_done`.

## Bẫy (1) — `shares_delta` chỉ populate 23,9%, TẬP TRUNG SAI CHỖ

**567/2.371 dòng (23,9%)** có `shares_delta`. Không phân bố đều theo `action_type`: nhiều dòng
`buy_done`/`sell_done` — chính là loại cần để xác nhận độ lớn — vẫn NULL. ⇒ Khi thiết kế bất kỳ cơ
chế nào dùng bảng này để suy độ lớn thay đổi CP lưu hành, **PHẢI fallback về nguồn khác** (Δ liên-quý
của `ticker_financial.OShares`) cho phần lớn trường hợp — không giả định `shares_delta` luôn có.

## Bẫy (2) — `ref_price` 100% NULL toàn bảng

**0/2.371 dòng** có `ref_price`. Không dùng được để định giá giao dịch cổ phiếu quỹ từ bảng này —
nếu cần giá, phải tra nguồn khác (giá đóng cửa quanh ngày sự kiện, hoặc tính từ số tiền công bố
trong `title`/`short_content` nếu vendor có ghi — CHƯA kiểm chứng độ tin cậy của cách này).

## Bẫy (3) — `action_type` KHÔNG bao trùm hết các sự kiện làm đổi số CP lưu hành

Ca thật **MCH** (job `Taylor_20260907_160333`): sự kiện 2025-12-25 "dùng CP quỹ chia cho cổ đông
hiện hữu **+** phát hành ~227 triệu CP thưởng" (Δ OShares thật = +237.755.604, 22,6% tổng CP) bị
gắn `action_type='other'`, KHÔNG rơi vào `buy`/`sell`/`buy_done`/`sell_done`. Một cơ chế chỉ lọc
theo `buy_done`/`sell_done` sẽ **bỏ sót đúng sự kiện gây ra thay đổi**, và có rủi ro khớp NHẦM vào
một sự kiện `buy_done`/`sell_done` khác không liên quan nằm gần đó về thời gian (đã xảy ra thật
trong job này trước khi vá bằng trần tỉ lệ — xem mục dưới).

⇒ **Trần tỉ lệ bắt buộc khi dùng `action_type IN ('buy_done','sell_done')` làm nguồn ngày/hướng**:
match không có `shares_delta` xác nhận mà |Δ OShares| > ~15% tổng CP trước đó → đáng ngờ là bị gắn
nhầm nguyên nhân (chương trình buyback thật hoàn tất trong 1 quý hiếm khi vượt ngưỡng này). Không
tự tin nhận số khi vượt trần — cần review tay dòng `action_type='other'` quanh cùng thời điểm.

## Bẫy (4) — nhiều dòng trùng `(ticker, public_date, action_type)` = NHIỀU NGUỒN TIN cho 1 sự kiện

Ca CTD 2018-02-06: 2 dòng `sell_done` cùng ngày (1 có `shares_delta=-448.500`, 1 không) — không
phải 2 sự kiện khác nhau. Bất kỳ cơ chế đếm/khớp nào theo dòng phải **gộp theo
`(ticker, public_date, action_type)` trước**, nếu không 2 Δ liên-quý khác nhau của cùng mã có thể
cùng "tiêu thụ" 2 dòng trùng lặp của MỘT sự kiện thật (bắt được bằng self-check trong job trên).

## Cách dùng đã kiểm chứng — overlay OShares point-in-time (job `Taylor_20260907_160333`)

Neo **ngày hiệu lực thật** của một thay đổi OShares vào `public_date` của dòng `buy_done`/`sell_done`
khớp hướng + cửa sổ thời gian với Δ liên-quý trong `ticker_financial.OShares` (không phải ngày dòng
quý — dòng quý đó có thể đã restate SỚM hơn cả ngày công bố Ý ĐỊNH, ca VRE: dòng quý filed
2019-10-29 mang số đã trừ 56,5tr CP trong khi Nghị quyết HĐQT ký 2019-11-04 và hoàn tất mua thật
2019-12-19). **Nguồn hỗn hợp có chủ đích, không giả vờ là 1 nguồn**: độ lớn từ `ticker_financial`
Δ liên-quý, ngày hiệu lực + hướng từ `treasury_news`.

Kết quả chạy trên 232/232 mã candidate: **161 mã xử lý được** (khớp `HIGH`/`MEDIUM`, cửa sổ tìm
kiếm 150 ngày sau ngày filed dòng quý restated, đo thực nghiệm p99≈146 ngày lag thật) · **13 mã
chỉ có match `SUSPECT`** (vượt trần tỉ lệ 15%, nghi cùng lớp lỗi MCH) · **28 mã KHÔNG giải thích
được** (không có dòng `buy_done`/`sell_done` nào rơi vào cửa sổ hợp lý cho bất kỳ Δ nào).

**KHÔNG wire vào `oshares_live.py`/`corp_action_lib.py`/production** — job này CHỈ thiết kế +
chạy thử, chờ quant-skeptic review (đổi diễn giải OShares chạm PIT backtest + report §21).

Chi tiết đầy đủ (thuật toán, self-check, danh sách mã theo 3 nhóm, code):
`mike/agents/Taylor/research/treasury_oshares_overlay_20260907/report.md`.

## Liên quan
- [`../fundamentals/ticker_financial_oshares.md`](../fundamentals/ticker_financial_oshares.md) —
  bảng đích của overlay này (RESTATE, không PIT thật — bẫy chung gốc).
- [`corporate_action_bq.md`](corporate_action_bq.md) — bảng corp-action rộng hơn (ISS/AIS/DIV...),
  không phủ sự kiện treasury buyback dạng tin tức như bảng này.

## ⚠️ Quyết định wire (user chốt 2026-09-08) — KHÔNG wire vào production

Overlay đọc bảng này (`match_overlay.py`) đã CONFIRMED 2 vòng quant-skeptic (162/14/29 mã), nhưng
user quyết **KHÔNG** đưa vào `oshares_live.py`/`corp_action_lib.py`/`corp_action_daily.py`: OShares
chỉ nuôi 1/3 nhánh composite v3 (`ps`/sales_yield, KHÔNG phải PE — trụ chính "1/PE dominant factor"
không phụ thuộc OShares), và lớp lỗi này chỉ nằm ở CỬA SỔ LỊCH SỬ đã tự hết (OShares hôm nay đã
đúng) — không có bằng chứng nó đổi được xếp hạng/backtest nào. Giữ overlay làm **công cụ tra cứu
ad-hoc**. Chi tiết: `kb/projects/treasury-buyback-oshares-overlay-20260907.md`.

## Nguồn
Kiểm tra trực tiếp bằng `bq` CLI 2026-09-07, job `Taylor_20260907_160333` (dispatch data-ops
2026-09-04 → Taylor verify độc lập + thiết kế overlay).

↩ [Về index nhóm](index.md)

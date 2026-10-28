# D — Câu hỏi engine: lô LAG mở lúc BEAR (job Taylor_20261020_113646; chỉ ĐỌC code, không sửa engine)

Không đề xuất đổi luật. Engine = `pt_v23_audit_2014.py` + `simulate_holistic_nav.py` (repo WorkingClaude, HEAD hiện tại).
Dữ liệu thật = 4 ledger pin (4707bcbe/bcd0469f/537e349b/a6ba34d8) + cache giá pin `data/bq_cache_asof20260729_postrestate/ticker`.

## (1) Mô tả có đúng không — ĐÚNG ba vế đầu, SAI vế "xoá sổ"
- **Book LAG chạy liên tục kể cả BEAR:** `pt_v23_audit_2014.py:2059-2069` (LAG_KW: `state_by_date` chỉ dùng cho park/ETF; không có
  `state_exit_map`, không cổng vào lệnh theo state); `:2070-2075` + `:2102` `tier_weights_by_state=None` trừ khi `LAG_DISC_STATE`
  (`:343`, mặc định rỗng; lệnh pin không đặt). `:2103-2105` mô phỏng book LAG một lần, độc lập allocator.
- **BEAR ⇒ w_lag_tgt=0:** `:733` `STATE_LAG_WEIGHT = {1:0.50, 2:0.00, 3..5:0.65}`; `:2148-2153` `w_lag_target`.
- **Phơi nhiễm combined = vị thế trong book × cap_lag/combined:** `:2117-2118` lấy lợi suất ngày `rl` của NAV book ref; `:2161-2175`
  `cl *= (1+rl)`, lệch band >10pp (`:735`) thì reset `cl = w_tgt × P`; `combined = cap_bal + cap_lag`. Vào BEAR ⇒ `cl = 0` và giữ 0
  (0×(1+r)); rời BEAR (w_tgt 0,65 hoặc 0,5) ⇒ lệch band ngay ⇒ `cl` bật lại, lô đang mở trong book ref có trọng số combined khác 0.
- **"Kẹt tới hủy niêm yết bị xoá sổ vào NAV" — engine KHÔNG làm vậy.** Ngày không có giá: mark giữ `last_price` cũ
  (`simulate_holistic_nav.py:615-618`); lệnh bán không có giá Open/Close ⇒ `still_pending`, thử lại hôm sau mãi
  (`:559-563`). Không có nhánh nào xoá sổ. Xoá sổ (kịch bản Z) là giả định kinh tế của replay, không phải hành vi engine.
  Thêm nữa, bảng giá BQ không có dòng nào của mã đã biến mất (survivorship), nên engine không bao giờ gặp ca này.

## (2) Dữ liệu thật — có lô LAG mở lúc BEAR bị xoá sổ/halt không? KHÔNG có ca kẹt/xoá sổ
`d_bear_lag.py` → `d_lots_<leg>.csv`; `d_summary.py` → `d_summary.json`. Lô = holding_id, book LAG, bỏ ETF_PARK.
| Chân | lô LAG | mở lúc BEAR | trong đó cap_lag bật lại khi lô còn mở | còn mở tới cuối | mã ngừng dữ liệu TRONG lúc giữ |
|---|--:|--:|--:|--:|--:|
| p30_pin0 | 1503 | 107 | 42 | 0 | 0 |
| p30_pin1M | 1545 | 109 | 42 | 0 | 0 |
| p0_pin0 | 1516 | 109 | 43 | 0 | 0 |
| p0_pin1M | 1553 | 110 | 43 | 0 | 0 |
- Lô BEAR theo năm (p30_pin0): 2015 7 · 2020 5 · 2022 63 · 2023 32. Lợi suất lô trung vị 0,0%, tệ nhất −24,8% (SMT 2015-05), tốt nhất +51,4%.
- 8 lô BEAR thuộc mã về sau ngừng có dữ liệu (BBC, BED, BST×2, PSN, SAP, VHF, VOC; dòng cuối 2025-08…2026-06), nhưng đều đã bán
  xong 2022-11…2023-03 ⇒ không lô nào kẹt.
- Phơi nhiễm combined tối đa của 1 lô BEAR khi cap bật lại: **7,2% NAV** (CKD 2022-08, lợi suất +0,9%).
- 15–16 lô BEAR có ≥5 phiên liên tiếp KL khớp=0 trong lúc giữ; 22–23 lô BEAR được bán vào ngày KL=0 (giá đứng).

## (3) Hệ quả với pin hiện hành
- **Survivorship (mã mất hẳn):** không đo được từ engine. Bảng giá thiếu mã đã mất, nên "0 ca" ở trên KHÔNG phải bằng chứng là
  không có rủi ro. Cơ chế (1) có nghĩa: nếu panel chứa ROS/FLC/HAI, engine sẽ (a) mở lô LAG lúc BEAR (2022-08-05) ở trọng số combined 0,
  (b) giữ lô ở giá đứng, không xoá sổ, (c) khi cap bật lại thì đóng góp phần lời/lỗ theo giá đứng ⇒ NAV engine **lạc quan hơn** thực tế.
  Độ lớn kinh tế đã đo ở replay ALLOC: 3 lô kẹt góp khoảng −0,45pp (p30_pin0, UB). Chưa đo bằng engine.
- **Lô BEAR thông thường (có dữ liệu):** góp vào NAV qua 42–43 lô/chân sau khi cap bật lại. Đóng góp CAGR ròng của nhóm này **chưa đo**:
  cần chạy lại engine với cổng vào theo state (đổi engine, ngoài phạm vi).
- **Phát hiện phụ (ngoài câu hỏi, đã đo, CHƯA đo tác động CAGR):** engine khớp LAG theo ADV 3M mà không xét KL ngày. Trên p30_pin0 /
  p0_pin0, **500/4267 lệnh mua LAG (31% giá trị mua)** và **263/1503 lệnh bán (27% giá trị bán)** rơi vào ngày BQ `Volume = 0`
  (`d_zerovol.json`; vd PNP 2023-02-01 mua 1,53 triệu CP, VC6 2018-01-29 mua 2,46 triệu CP, cả hai ngày KL=0). BAL: 0 lệnh mua,
  1–2 lệnh bán. Nếu `Volume=0` ở BQ là "không có giao dịch khớp" thì phần fill này không làm được thật. Cần Winston xác nhận ngữ nghĩa
  `Volume` trước khi kết luận; tác động lên R3 chưa đo.

# Mã đầu ngành × nowcast ngành + nowcast KQKD 12 họ — NO-GO (đóng 2026-11-19, user duyệt)

Nguồn: `agents/Taylor/research/arch_8l_dt5g_data_leverage_20261119/REPORT.md` (review kiến trúc, Fable/high) →
`nowcast_kqkd_12fam_20261119/REPORT.md` (A4, job `Taylor_20261119_090443`) và
`sector_leaders_nowcast_20261119/REPORT.md` (việc 5, job `Taylor_20261119_090450`). Quant-skeptic đã phản biện cả hai.

## Phán quyết
- **Mã đầu ngành × nowcast (T2/T6/T9): NO-GO, quant-skeptic REFUTED (cao).** Không DISPLAY, không PREREG-5, không tilt/sleeve.
  Lý do: T9 là hiệu ứng vốn hoá lớn (2 mã ngẫu nhiên top-10 thanh khoản ngoài họ tái tạo ~75%: −2,41 vs −3,19pp; bỏ 2020 → p 0,167);
  T2 chỉ đúng với cao su (bỏ cao su p 0,70); T6 là long-short (không bán khống được ở VN) và trượt khi bỏ HSG/NKG (banned, p 0,133).
  BH q<0,10 phụ thuộc ≥4 trial cùng ở sàn p=1/30 (biên 0,4% so với null max). Giữ phán quyết **LENS not BOOK** (20 sector sweep).
- **Nowcast KQKD 12 họ: chỉ họ 2 (biên heo, DBC) và họ 8 (môi giới) CONFIRMED mức vừa.** Họ 9 sân bay REFUTED (bỏ COVID 2020-22: IC −0,06);
  họ 10 cảng, 11 ô tô INCONCLUSIVE (độ trễ công bố chỉ là giả định, chờ vintage A1; ±5–10 ngày độ trễ họ 11 làm cả 5 họ mất cổng BH);
  họ 1, 3, 5, 6, 7, 12 không đạt (họ 12 ngân hàng ngược dấu −0,29). Họ 8 là quan hệ cơ học/công khai (partial IC sau VNINDEX 0,56) ⇒ giá trị gia tăng cho LAG thấp.
  Tổng trial tích luỹ dòng hàng hoá/ngành = 29 (đầu ngành thêm 9 ⇒ 38); trên 29 trial không họ nào qua BH.
- **Quyết định user 19/11:** PREREG-5 paper forward CHỈ cho họ 2 (DBC; BAF banned); họ 10/11 đóng băng chờ vintage; họ 8, 9 không làm.
- Việc đã LIVE cùng đợt: vintage macro/commodity (cron 23:20 ICT), C1 sổ cảnh báo vĩ mô (display-only); ghi: `cron_registry.md`, `data_registry/market-state/macro_stress_ledger.md`.

## Đừng lặp lại
Đầu ngành theo thanh khoản × nowcast hàng hoá (mọi biến thể T1–T9); nowcast sân bay không loại COVID; spread long-short đầu ngành − phần còn lại.
Muốn mở lại đầu ngành: cần định nghĩa theo quy mô (doanh thu/vốn hoá) làm trial ĐĂNG KÝ RIÊNG + placebo top-decile thanh khoản + bản ex-banned bắt buộc.

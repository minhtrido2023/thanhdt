# A1 — FPT thesis audit (1 trang). Nghiên cứu/đọc-ghi file duy nhất; KHÔNG đặt lệnh, KHÔNG sửa plan/exit rules/sổ giá, KHÔNG đổi định giá.

Bối cảnh: user (22/11/2026) đang cân nhắc MIỄN stop −10%/25 phiên cho FPT (vị thế sleeve discretionary, mua 06/11, giá vốn ~51.160 SpaceX / ~51.180 ZaloPay, 5% NAV; luật: `kb/projects/disc-fpt-nnc-approval-20261105.md` — TARGET +10% / STOP −10% (đề xuất lên plan, user xác nhận) / TIME 25 phiên = 11/12). Plan 20/11 đã hủy lệnh bán. Cần một "thesis card" để user quyết. Đây là bước A1 của `kb/projects/dd-upgrade-final-action-20261122.md`.

Nguồn phải đọc (tự kiểm file/số, đừng tin KB):
- DD: `agents/Taylor/research/dd_redo_20261105/FPT/REPORT_r3.md` (+ calc_r3/LOCK_r3_prerun.txt), `agents/Taylor/research/dd_FPT_20261101/REPORT.md`, `kb/projects/fpt-dd-20261101.md`; sổ giá `kb/dd_price_zones.json` (entry FPT rev3 = hiện hành).
- Luật thoát + vị thế: `kb/projects/disc-fpt-nnc-approval-20261105.md`, `data/discretionary_exit_rules.json`.
- Livermore: `kb/data_registry/market-state/livermore_reads.md` (đọc FPT: WAIT_CONFIRM close≥47.950 & vol≥1,5×v20, cancel 42.990 — kiểm lại nguồn).
- Dữ kiện mới từ 06/11 đến 22/11: giá/khối lượng FPT thực (đọc `data/bq_cache*` hoặc BQ `tav2_bq.ticker` ticker='FPT', dùng alias bảng), CBTT/tin FPT (BCTC, cổ tức 1.000đ chốt 30/11, CK FTEL, thay đổi nhân sự/hợp đồng) từ nguồn công khai nếu tìm được; thị trường chung (VNINDEX).

Đầu ra: `agents/Taylor/research/dd_upgrade_20261122/A1_fpt_thesis_audit/THESIS_CARD.md`, ≤1 trang (≤~400 từ + 1 bảng), tiếng Việt:
1. Luận điểm 3 dòng (vì sao giá trị > giá; tâm/vùng rev3 đang hiệu lực; nhãn/skeptic).
2. Mốc kiểm chứng có ngày (BCTC quý kế, cổ tức, sự kiện).
3. **Điều kiện HUỶ luận điểm** — mỗi điều kiện gắn nguồn đo được (file:dòng / truy vấn / URL) và hiện trạng (đã xảy ra chưa).
4. Dữ kiện MỚI từ 06/11 (giá, khối lượng, tin) và tác động lên từng điều kiện huỷ: không đổi / củng cố / yếu đi.
5. Khoảng cách giá hiện tại tới: giá vốn, −10% stop (giá cụ thể mỗi account nếu đọc được từ state/journal), tâm rev3, đáy vùng 45.270.
6. Câu hỏi để user quyết (không tự khuyến nghị miễn stop; chỉ nêu dữ kiện ủng hộ/chống miễn stop MỘT CÁCH CÂN BẰNG hai chiều).
Mọi con số phải kèm nguồn; số không kiểm được ghi "chưa kiểm". Ghi bus finding khi xong: `bin/append_event.sh Taylor finding "A1 FPT thesis card" '{...}'`.

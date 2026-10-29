# PREREG — chi phí vốn dài hạn cho DCF DGC (job Taylor_20261029_133456)
Viết TRƯỚC khi lấy số rf/ERP/β và TRƯỚC khi chạy bất kỳ FV nào. Commit trước khi chạy `model_ke.py`.
Chỉ nghiên cứu — không wire, không sửa r7, không sửa code production.

## 0. Hiện trạng (đã đo trước PREREG, chỉ đọc code)
- r7 `ke()` = CFG["rf"] 0,074 + 1,0 × 0,075 = **14,9%** (comment ghi "CCTG 12M"; registry mô tả CCTG 6M — kiểm ở REPORT).
- Fleet `dcf_valuation.py`: r = consumer_deposit_rate (7,4% hôm nay) + ERP **6,5%** = 13,9% — ERP khác DGC (7,5%).
- Self-check bắt buộc: tái lập DCF tầng A (CFG_A trong r7) **21.407 / 32.925 / 41.779** đúng từng đồng trước khi thay Ke.

## 1. Nguyên tắc chọn rf (khai trước)
DCF DGC = dòng tiền danh nghĩa VND, terminal Gordon vô hạn ⇒ rf phải:
K1 khớp TIỀN TỆ (VND) · K2 khớp KỲ HẠN (dài nhất quan sát được, ≥10Y) · K3 KHÔNG phản ánh chu kỳ chính sách ngắn hạn
(bình thường hoá trên ≥10 năm hoặc dựng từ lạm phát mục tiêu + lãi thực) · K4 quan sát được/kiểm chứng được ·
K5 không nhìn trước (chỉ dữ liệu ≤ 2026-10-29) · K6 nhất quán với g terminal (g ≤ rf danh nghĩa dài hạn ≤ GDP danh nghĩa dài hạn).
Lãi huy động 12M/CCTG vi phạm K2 (kỳ hạn 1 năm) và K3 (đang ở đỉnh chu kỳ) ⇒ chỉ là đối chứng.

## 2. Ứng viên rf (khai trước, giá trị điền SAU)
(a) TPCP 10Y VN hiện tại · (b) trung vị lợi suất TPCP 10Y VN (TB năm) cửa sổ 10Y và 15Y kết thúc 2026 ·
(c) building-block = lạm phát mục tiêu VN (QH: ~4–4,5%) + lãi thực dài hạn 2–3% · (d) TB ≥10 năm lãi huy động Big-4 12M
(`deposit_rate_vn.py`, step-series, có caveat hindsight b) · (e) GDP danh nghĩa dài hạn (mốc trần g; tham chiếu) ·
(f) 7,4% hiện hành (đối chứng).

## 3. Luật quyết định (khai trước — KHÔNG phụ thuộc FV)
- **rf trung tâm** = trung bình của (b-10Y) và (c-giữa) nếu chênh ≤1,0pp; nếu chênh >1,0pp ⇒ lấy (c-giữa) và báo.
- **ERP phải đo so với CHÍNH rf của nó.** Không được ghép rf trái phiếu với ERP đo trên lãi huy động (6,5%/7,5%) — đó là premia
  trên một rf cao hơn. ERP trung tâm = Damodaran ERP trưởng thành (tháng 1/2026, nếu lấy được) + CRP VN (Damodaran) — dạng bond-based.
  Kiểm ngược bằng ERP thực nghiệm VNINDEX TR so với TPCP 10Y cùng cửa sổ. Không chỉnh ERP để bù rf.
- **β**: β tuần 5 năm DGC vs VNINDEX (BQ, điều chỉnh Blume 2/3·β+1/3) + trung vị β nhóm hoá chất cùng phương pháp; khoảng = [min,max] của hai số, điểm = trung bình. Universe nhóm hoá chất lấy qua universe_pit, KHÔNG ticker_prune.
- **Ke trung tâm** = rf_trung tâm + β × ERP. **Vùng Ke** = tổ hợp (rf ±) × (ERP thấp/cao) × (β khoảng), cắt hai đầu thô thiển.
- Đối chiếu độc lập (không dùng để chọn, chỉ kiểm dải): (i) E/P VNINDEX + g dài hạn; (ii) TR CAGR VNINDEX 10/15 năm; (iii) chi phí nợ DGC/ngành.
  Nếu Ke trung tâm nằm NGOÀI dải đối chiếu ⇒ báo, KHÔNG sửa luật.
- **g terminal**: giữ G_BASE 3% của r7 (không đổi g khi đổi Ke); độ nhạy g 2–5%; ràng buộc g < Ke − 3pp và g ≤ (e).

## 4. Đầu ra & kiểm
`model_ke.py` import r7 model.py (không sửa), thay `ke` qua knob; out_*.csv + md5; chạy 2 lần dưới TZ=UTC và TZ=Pacific/Kiritimati, md5 phải trùng.
N độc lập: đây KHÔNG phải kiểm định thống kê; N năm cho trung vị TPCP = 10/15 quan sát năm, tự tương quan cao ⇒ chỉ mô tả.

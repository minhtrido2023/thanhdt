# Snapshot đóng băng cho lvens2_incremental (DCF-VN V3.1)
Nguồn: wt-dcf-v3-20261125/.../dcf_vn_redesign_20261125c (snapshot VNDirect 2026-11-23). Chốt 25/11/2026 22:4x ICT, user duyệt.
- out/delisted/ (1.341 file, giá+BCTC mã vắng BQ) · out/px_pre2013_d.csv (md5 d01c7aa8…)
- MD5SUMS_delisted.txt (gốc, 1.339 dòng) · MD5SUMS_full_frozen_20261123.txt (toàn bộ 1.342 file + px_pre2013)
- Dùng: LVENS2_FROZEN=/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out (script đọc manifest ở ../MD5SUMS_delisted.txt)
- ⚠️ KHÔNG fetch VND hàng tháng. Mã niêm yết mới / huỷ niêm yết SAU 2026-11-23 và mọi mã chỉ có ở VND (2026-10: DSH, GEL, HPA) sẽ THIẾU giá từ as-of 2026-11 (D 11-30 > 11-23) ⇒ phải ghi cờ/WARN, không điền bù.
- KHÔNG sửa file trong thư mục này.

# PREREG v3 — thay PREREG v2 (và v1) · NGƯỠNG SỰ KIỆN ×2 (phương án A)

Phiên bản: v3 · 2026-11-15 · Taylor (job `Taylor_20261115_162439`, P1-V3). **User chốt 2026-11-15 23:24 ICT (`decided_by: user`): phương án A = nới ngưỡng sự kiện ×2.**
v3 thay v2 **TRƯỚC mọi lần chạy forward** — chưa có sự kiện forward nào được chấm; P0 và dry-run chỉ là hồi tố, không tính vào N. v1/v2 không sửa tại chỗ.
Mọi thứ không nêu dưới đây **giữ nguyên v2** (prompt M1 v2, schema, gói PIT, lọc tin theo ngày nạp, M2 fail-open, T1/T2/T3, ngưỡng kinh tế T1 ≥ 5pp, T2 ≥ 8pp).
Tham số máy đọc: `prereg_v3.json` (nguồn DUY NHẤT; `ai_momentum_daily.py` đọc từ đây và tự từ chối chạy nếu md5 lệch `PREREG_v3.md5`).

## 1. Định nghĩa sự kiện v3 (ngày T, mã trong `universe_pit` ruleset_version=1)
| Tham số | v2 (v1) | **v3** |
|---|---|---|
| mom20 (Close/Close[−20]−1) | ≥ 0,20 | **≥ 0,15** |
| idio20 (mom20 − VNINDEX 20 phiên) | ≥ 0,15 | **≥ 0,10** |
| Volume_1M / Volume_3M_P50 | ≥ 1,5 | **≥ 1,2** |
| liq = Price × Volume_1M (tỷ VND) | ≥ 3 | **≥ 1** |
| Giữ nguyên | Close ≥ HI_3M_T1 · universe_pit rv1 · rating_8l ≤ 4 as-of (`fa_ratings_8l` hiệu lực ≤ T) · cooldown greedy 90 ngày + khác quý (tính từ SỰ KIỆN đã phát) · hàng đợi 10/tuần (nhân quả theo ngày, liq giảm dần trong ngày) |

Đo (build_events trên `qual_days_loose.csv`, R4): **N = 560 sự kiện, 321 mã, 26 tháng (2024-10→2026-11), TB 21,5/tháng** (v2: 13,2/tháng). Lịch sử cooldown = `events_v3.csv` (R4, < T) ∪ sổ JSONL.

## 2. Phụ thuộc trong-mã (mới ở v3; 168/321 mã có > 1 sự kiện, tối đa 4/mã)
- **GIỮ** p-value hoán vị **khối tháng** (10.000 lần, seed 20261115) cho T1/T2; sign-flip theo khối tháng cho T3. Họ BH vẫn **3 phép thử** (T1,T2,T3).
- **THÊM — chỉ MÔ TẢ, KHÔNG vào họ BH, không dùng để tuyên bố kết luận**: `T1_ticker_sensitivity` = (a) bootstrap cụm theo mã (resample mã, giữ mọi sự kiện của mã; 10.000 lần) → CI 95% của chênh T1; (b) chênh T1 chỉ trên sự kiện ĐẦU TIÊN mỗi mã. Nếu CI cụm-mã chứa 0 trong khi p khối-tháng < ngưỡng ⇒ báo là **"không bền vững trước phụ thuộc theo mã"** trong báo cáo look (không đổi quyết định BH). Chỉ được đưa vào họ BH nếu chứng minh được (ngoài phạm vi v3).
- **CẤM** hoán vị trong-năm / trong-tháng (luật 12/11: phá cụm tháng ⇒ p quá lạc quan). Placebo nếu cần = hoán vị khối tháng.

## 3. Look — định nghĩa NHẤT QUÁN theo N_dir (không đổi so với v2; khai báo lại để khoá)
- N_dir_scored = số sự kiện đã chấm (đủ 61 phiên) có `view_20s` cuối là CONT/REV. **L1 = 80, L2 = 150 (N_dir)**; FINAL = `N_scored ≥ 250` (mọi sự kiện) **hoặc** 24 tháng lịch sau sự kiện đầu. Mẫu mỗi look đóng băng = N_dir đầu tiên theo T.
- Giữa các mốc scorer chỉ in N, N_dir, G-proc (không có `effects`). Sự kiện `skipped_capacity` không được chấm.
- Scorer chỉ đếm dòng có `prereg_md5` = md5 PREREG_v3.md hiện hành.

## 4. Thời gian tới look & power (đo bằng `power_sim_directional_v3.py` → `power_sim_directional_v3.out`; phân phối ex20 THẬT của 560 sự kiện R4 v3)
Power T1 ex20 (Δ8pp / Δ12pp; nhóm A = CONT ≈ ½ sự kiện có hướng; α = 0,05/3 một phía; NSIM=150 ⇒ sai số mô phỏng ±~0,04):
| p_dir | N_dir=80 | N_dir=150 |
|---|---|---|
| 0,4 | 0,73 / 0,99 | 0,95 / 1,00 |
| 0,3 | 0,78 / 1,00 | 0,96 / 1,00 |
Tháng tới N_dir (chưa gồm ~3 tháng chờ ex60; "cắt" = hàng đợi 10/tuần bỏ 86/560 = 15,4% sự kiện, đo trên events_v3 R4):
| Nhịp | p_dir | N_dir=80 | N_dir=150 | FINAL N_scored=250 |
|---|---|---|---|---|
| TB 21,5/th | 0,4 | 9,3 (11,0 cắt) | 17,4 (20,6) | 11,6 (13,7) |
| TB 21,5/th | 0,3 | 12,4 (14,7) | 23,3 (27,5) | — |
| 6 tháng gần 12,3/th | 0,4 | 16,3 (19,2) | 30,5 (36,0) | 20,3 (24,0) |
| 6 tháng gần 12,3/th | 0,3 | 21,7 (25,6) | 40,7 (48,0) | — |
**Đọc thẳng**: ở nhịp 6 tháng gần, L2 (N_dir=150) KHÔNG tới được trong trần 24 tháng; L1 tới được (~16–26 tháng gồm cắt, + ~3 tháng ex60 ⇒ sát/vượt trần 24 tháng ở p_dir=0,3). Kết luận khả thi chỉ khi nhịp quay về gần trung bình dài hạn. p_dir mới đo trên mẫu 10 (thô) — **P_dir thực đo ở giai đoạn đầu forward, báo ngay tại 40 sự kiện xử lý (không phải look).**

## 5. Phạm vi
Chỉ PAPER. liq ≥ 1 tỷ gồm mã kém thanh khoản ⇒ **không là tín hiệu thực thi**, không sizing, không plan. Không đổi M1/M2.

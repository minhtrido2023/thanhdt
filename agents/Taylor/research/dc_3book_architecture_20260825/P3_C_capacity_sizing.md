# Giai đoạn 3, Phần C — Capacity sizing cho DC universe (16 mã)

Job `Taylor_20260825_153800`. Script: `exp_dc3book_capacity_20260825.py`.
Output: `exp_dc3book_capacity_sizing.csv`. Nguồn ADV: `data/bq_cache/ticker/2026.parquet`
(2026-01-05→2026-08-24, 158 phiên/mã, 16/16 mã có đủ dữ liệu). ADV_60d = `Trading_Value`
(Price×Volume, derived — CLAUDE.md: không dùng cho VWAP nhưng ĐÚNG chuẩn cho proxy giá trị giao
dịch VND, đây chính là việc capacity sizing cần).

## Quy ước

- Ngưỡng an toàn chính: **≤5% ADV/phiên** (vị thế có thể xây/thoát trong 1 phiên mà không vượt
  5% giá trị giao dịch trung bình phiên đó); tham chiếu thêm 10%.
- Vị thế ngụ ý (implied position) = `cap_per_name (0.20) × w_DC × NAV`, tính ở **2 kịch bản
  w_DC**: `0.333` (3-book tĩnh, đúng kịch bản phase-2 Phần C4 để đối chiếu chéo) và `0.46`
  (C1 BULL-only swap, kịch bản đang được đề xuất theo dõi ở Phần A job này — w_DC lớn hơn khi
  active nên là kịch bản NẶNG HƠN, dùng làm worst-case).
- `recommendation` = worst-case trên CẢ 4 tổ hợp (2 kịch bản × 2 quy mô NAV).

## Bảng đầy đủ (đơn vị tỷ VND trừ khi ghi %)

| ticker | ADV_60d (tỷ) | max_pos_5%ADV (tỷ) | %NAV an toàn @100B | %NAV an toàn @200B | %ADV thực @100B (w=0.46) | %ADV thực @200B (w=0.46) | recommendation |
|---|---:|---:|---:|---:|---:|---:|---|
| ACB | 420.3 | 21.0 | 21.0% | 10.5% | 2.19% | 4.38% | **OK** |
| TCB | 404.9 | 20.3 | 20.3% | 10.1% | 2.27% | 4.54% | **OK** |
| SSI | 457.3 | 22.9 | 22.9% | 11.4% | 2.01% | 4.02% | **OK** |
| FPT | 548.9 | 27.5 | 27.5% | 13.7% | 1.68% | 3.35% | **OK** |
| MBB | 305.7 | 15.3 | 15.3% | 7.6% | 3.01% | 6.02% | CAP_NEEDED |
| HDB | 271.6 | 13.6 | 13.6% | 6.8% | 3.39% | 6.77% | CAP_NEEDED |
| VCB | 255.4 | 12.8 | 12.8% | 6.4% | 3.60% | 7.20% | CAP_NEEDED |
| VCI | 183.5 | 9.2 | 9.2% | 4.6% | 5.01% | 10.03% | CAP_NEEDED |
| VND | 252.6 | 12.6 | 12.6% | 6.3% | 3.64% | 7.29% | CAP_NEEDED |
| HCM | 128.5 | 6.4 | 6.4% | 3.2% | 7.16% | 14.32% | CAP_NEEDED |
| PVT | 64.1 | 3.2 | 3.2% | 1.6% | 14.36% | 28.73% | CAP_NEEDED |
| HAH | 32.4 | 1.6 | 1.6% | 0.8% | 28.43% | 56.87% | CAP_NEEDED |
| CTR | 23.8 | 1.2 | 1.2% | 0.6% | 38.63% | 77.26% | CAP_NEEDED |
| DBC | 27.5 | 1.4 | 1.4% | 0.7% | 33.52% | 67.04% | CAP_NEEDED |
| MSH | 3.2 | 0.16 | 0.16% | 0.08% | 285.6% | 571.3% | **EXCLUDE** |
| DHG | 0.74 | 0.04 | 0.04% | 0.02% | 1241% | 2482% | **EXCLUDE** |

## DHG và MSH — xác nhận, đề xuất loại

Cả 2 vượt xa 100% ADV ở MỌI kịch bản (cap tối đa an toàn 5%-ADV chỉ = 0.02-0.16% NAV — quá nhỏ để
có ý nghĩa thực thi, đúng ngưỡng dispatch nêu <0.5% NAV/mã). Khớp với phase-2 Phần C4 (890%/205%
ở 100B, kịch bản w=1/3) — cache mới cho 899%/207% cùng kịch bản, sai biệt <1.5% do window ADV lệch
vài giờ, không phải mâu thuẫn. **Đề xuất: LOẠI DHG và MSH khỏi DC universe** (còn 14/16 mã), thay
vì giữ với cap cực nhỏ không đáng công thực thi.

## 4 mã Securities (SSI/VCI/VND/HCM) — xác nhận lại ở CẢ 2 quy mô NAV

**Không xác nhận đồng đều như phase-2 mô tả ("cả 4 đều an toàn").** Ở kịch bản nặng hơn (w_DC=0.46,
tương ứng C1 BULL-swap đang theo dõi) và NAV=200B (SpaceX+ZaloPay gộp):
- **SSI: an toàn cả 2 quy mô** (2.01%/4.02% ADV) — duy nhất trong nhóm Securities không cần cap.
- **VCI, VND, HCM: cần CAP** ở NAV=200B (10.03% / 7.29% / 14.32% ADV, đều >5%) — VCI còn cận biên
  vượt cả ở 100B (5.01%, sát ngưỡng). HCM là mã mỏng nhất nhóm (ADV 128.5 tỷ), cần cap chặt nhất.

Đây là khác biệt QUAN TRỌNG so với phase-2 (job trước dùng kịch bản w=1/3, nhẹ hơn, và không tách
theo NAV 200B) — ở quy mô vốn thật khi 2 account gộp lại VÀ book DC chạy full trọng số BULL, 3/4
mã Securities cần giới hạn vị thế, không phải "đều an toàn" như kết luận trước.

## Khuyến nghị cap cụ thể (nếu wire ở quy mô 200B)

Với 10 mã `CAP_NEEDED`, cap per-name an toàn (5% ADV, quy mô 200B) tính bằng cột "%NAV an toàn
@200B" ở bảng trên — vd MBB 7.6%, VCB 6.4%, VCI 4.6%, HCM 3.2%, PVT 1.6%, HAH/CTR/DBC dưới 1%. Nếu
giữ cap cứng 0.20/mã như hiện tại (custom30 convention), CẦN hạ cap riêng cho các mã này xuống mức
ở cột %NAV an toàn — đặc biệt HAH/CTR/DBC/PVT chỉ nên cap ~0.6-1.6% NAV chứ không phải 20%.

## Giới hạn

- ADV tính trên cửa sổ 8 tháng 2026 (158 phiên, 2026-01-05→08-24) — không phải trung bình nhiều
  năm; thanh khoản 2026 có thể khác biệt đáng kể so với lịch sử backtest 2014-2026 dùng ở Phần A/B.
  Nếu wire thật, nên tính lại ADV tại THỜI ĐIỂM wire, không dùng cố định số này.
- Không tính đến price impact phi tuyến (giả định 5%-ADV là ngưỡng an toàn tuyến tính, đúng chuẩn
  ngành nhưng là xấp xỉ, không phải mô hình market-impact đầy đủ).

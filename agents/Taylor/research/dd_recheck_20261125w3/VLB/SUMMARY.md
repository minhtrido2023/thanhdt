# VLB — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032448)

Nguồn: `REPORT_recheck_VLB.md` · mô hình rev4 (CONTROL: `dcf_vlb_r4.py` stdout trùng byte `output_r4.txt`) · skeptic `dd_VLB_20261122/skeptic/r3.json` (KHÔNG chạy vòng mới) · E17 `ADJ_CENTER.md` + `adj.json` · `LEDGER_PROPOSAL_VLB.json` (rev5). Calc không bị TRIM.

**Bước 0:** KHÔNG có tham số nền bị phủ (không holding; r Δ 0 ở 25/11 — 7,40% cctg_12m; không terminal; độ nhạy r tính từ mô hình).

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **47.142 (+4,39%)**. **E16:** nguyên văn **RẺ** — phân vị [fade 0, hold 0], N hiệu dụng 9.7, cờ **⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=2.31)** (asof 2026-11-20).
- D3/D4/V1/V3/V5/V6/V8: rev4 đã đủ. D3: chi đền bù đất trong ranh GP là chi bắt buộc — lịch sử đưa vào E17 I3, phần vượt lịch sử = độ nhạy (chưa có số).
- **Dữ kiện A mới:** LCTT KT25 + 9T/26 (khấu hao 17,09/10,62/8,00; chi TSCĐ 3,62/12,04/1,13; Δ chi phí trả trước +15,60/−70,92/+2,89); KQKD Q3/26 lõi ×4 = 403,0 (không phải 440 như skeptic ước).

## (b) Tâm / vùng / nhãn
| | rev4 (sổ rev4) | recheck (proposal rev5) | Δ |
|---|---|---|---|
| Tâm | 45.161 | 45.161 | 0% |
| Vùng | 34.783–55.983 | 34.783–55.983 | 0 |
| Nhãn @ 48.100 (20/11) | trong vùng, nghiêng đắt nhẹ; luật 4 (38.387) không đạt | như cũ | không đổi |
| skeptic_final | REFUTED_OPEN | REFUTED_OPEN | giữ |

## (c) Phản biện
Không chạy vòng mới: r3 (DD_GENERAL, INCONCLUSIVE medium, 1,09 USD, report_md5 khớp) là vòng cuối trên đúng mô hình/tâm này; §E14 dừng. Tâm 0%, nhãn không đổi ⇒ không cần B2.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**43.626 đ/cp (dải 40.056–45.906; −3,40%)**, tuyến tính (|Σ| 3,4% ≤5%; tổ hợp kiểm tra 43.505). Hạng mục B: I1 neo giữa chu kỳ (p 0,35 × −4,79%), I2 phải trả NLĐ mùa vụ (p 0,5 × −1,96%), I3 chênh dòng tiền đền bù/TSCĐ vs khấu hao-phân bổ (p 0,35 × −3,26%; gộp hai hạng mục r3 ngược chiều vì cùng một dòng tiền), I4 năm 1 theo Q3/26 (p 0,35 × +1,14%).
Điều kiện đổi số chính: lõi Q4/2026 (~20/01/2027) ≈ −1,7…+1,3%; LCTT KT26 ≈ −1,0…+0,7%; CBTT đền bù diện tích còn lại có số ≈ −4…−6% (ước lượng skeptic); văn bản gia hạn GP ≈ +3% (ước lượng).

## (e) Rủi ro / việc mở
1. Đền bù phần diện tích còn lại trong ranh GP: chưa có diện tích/đơn giá (BCTN: "gặp khó") — hạng mục C lớn nhất. 2. Lõi Q3×4 chưa khử mùa vụ. 3. Tiền cấp quyền/bù trừ 329 tỷ: STRESS + HARD ABANDON. 4. Thanh khoản: 5 tỷ ≈ 22 phiên.
5. Giá 48.100 so tâm adj 43.626: 1,10× (chỉ đọc sau khoá; KHÔNG đổi nhãn sổ). Đáy hiệu dụng watch nếu Mike ghi center_adj = min(34.783, 34.783×43.626/45.161, 40.056) = 33.601.
6. `LEDGER_PROPOSAL_VLB.json` = rev5 REFUTED_OPEN, selfcheck `--ledger` bản tạm: lỗi 0 (`MIKE_SRC_ROOT=<worktree>`).

## (f) Khuyến nghị lớp: **MECH** (tâm base 0%, không chạy vòng skeptic mới).

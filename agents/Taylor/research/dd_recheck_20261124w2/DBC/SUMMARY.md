# DBC — rà lại DD đợt 2 (24/11/2026, job Taylor_20261124_131354)

Nguồn: `REPORT_recheck_DBC.md` (md5 `50d69040…`) · mô hình rev4 (CONTROL: `calc_rev4.py` stdout trùng byte `calc_rev4_output.txt`) · skeptic `dd_DBC_20261118/skeptic/r4.json` (KHÔNG chạy vòng mới) · E17 `ADJ_CENTER.md` + `adj.json` · `LEDGER_PROPOSAL_DBC.json`. Calc không bị TRIM.

**Bước 0:** KHÔNG có tham số nền bị phủ (không tầng holding; r Δ 0 ở 24/11; RONIC = Ke; độ nhạy r tính từ mô hình).

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **19.669 (+11,29%)**. **E16:** nguyên văn **KHÔNG CHẮC (rẻ…đắt)**, N hiệu dụng 14.0 (asof 2026-11-20).
- D3/D4/V1/V3/V5/V6/V8: rev4 đã đủ (23/11). Chỉ thiếu 2 dòng E15/E16.
- **Dữ kiện A mới:** KT25 (bản EN, OCR trang 34): lãi vay vốn hoá 9,5 tỷ (2025) / 21,7 tỷ (2024) cho vay ĐẶC THÙ xây TSCĐ; không có lãi vốn hoá cho BĐS.

## (b) Tâm / vùng / nhãn
| | rev4 (sổ rev3) | recheck | Δ |
|---|---|---|---|
| Tâm | 17.673 | 17.673 | 0% |
| Vùng | 10.262–24.835 | 10.262–24.835 | 0 |
| Nhãn @ 16.400 (23/11) | quanh giá trị hợp lý, chưa đạt 0,85×tâm (15.022) | như cũ | không đổi |
| skeptic_final | REFUTED_OPEN | REFUTED_OPEN | giữ |

## (c) Phản biện
Không chạy vòng 5: skeptic r4 (DD_GENERAL, REFUTED medium, 1,17 USD) đã chấm đúng mô hình/tâm này; §E14: vòng cuối không CONFIRMED ⇒ dừng. Hạng mục r4 (tài trợ XDCB+BĐS 100% vốn chủ; BĐS 1,0× sổ; chiều lên: lỗ thuế, quỹ đất) xử lý bằng E17.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**16.439 đ/cp (dải 14.828–17.542; −6,98%)**, tổ hợp chạy lại mô hình (|Σ| 7,1% > 5%). Hạng mục: tài trợ XDCB bằng vay đặc thù B (p 0,5 × −8,95%), haircut thời gian BĐS B (p 0,65 × −5,04%), lỗ thuế B (p 0,5 × +1,25%). Bản leverage-neutral 53% của skeptic (−20,7%) chỉ độ nhạy: trái dữ kiện vốn hoá và đếm hai lần chi phí nợ (cộng lại lãi ⇒ −12,5%).
Điều kiện đổi số chính: thuyết minh vay/XDCB KT26 (~03/2027) ≈ −3,6…+3,2%; BCTC Q4/26 ±8,2% (trọng số kịch bản); bàn giao/trích lập BĐS ±1,3–1,5%.

## (e) Rủi ro / việc mở
1. Lãi vay đặc thù thật (không phải lãi BQ 4,5%) chưa công bố ⇒ f_XDCB còn dải 0,39–0,92. 2. Quỹ đất BĐS (vị trí/giá gốc) chưa có. 3. EPR, thuế, ESOP: độ nhạy. 4. WARNING phải thu NLĐ 237,1 tỷ.
5. Giá 16.400 so với tâm adj 16.439: ngang (chỉ đọc sau khoá; KHÔNG đổi nhãn sổ). Đáy hiệu dụng watch nếu Mike ghi center_adj = min(10.262, 10.262×16.439/17.673, 14.828) = 9.545.
6. `LEDGER_PROPOSAL_DBC.json` = rev4 REFUTED_OPEN, selfcheck lỗi 0 (`MIKE_SRC_ROOT=<worktree>`).

## (f) Khuyến nghị lớp: **MECH** (tâm base 0%, không chạy vòng skeptic mới); muốn đổi tâm base theo dữ kiện vốn hoá ⇒ rev5 + skeptic mới — chờ Mike/user.

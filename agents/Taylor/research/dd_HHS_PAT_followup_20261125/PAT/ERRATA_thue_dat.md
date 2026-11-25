# PAT — Rà nhãn "thuê đất KCN" cho khớp chỉ đạo user 25/11 (job Taylor_20261125_080257)

Chỉ đạo user (25/11, ghi tại `kb/memory/Mike.md`, mục 14:55): *thuê đất hết hạn sẽ được thuê lại, đây không phải rủi ro.*
**Tâm 55.527 và tâm adj 57.872 GIỮ NGUYÊN.** Không bằng chứng nào buộc phải đổi:
- **Base đã giả định gia hạn.** `assumptions_rev6.md:12` (khoá md5 `5207e413…`) ghi: "Chuỗi tường minh tới 2045, hoạt động liên tục (gia hạn thuê đất KCN …)". Base vì vậy đã trùng với chỉ đạo của user.
- **E17 không chứa nhánh này.** Trong `adj.json` (md5 `50ef6729…`), nhánh "hết ~2034 không gia hạn −28,7%" thuộc hạng mục **C**, nằm ngoài Σ. Σ chỉ gồm 2 hạng mục bậc B, đều chiều lên (+6,18% ô O2, +2,27% tồn kho). Bỏ nhãn rủi ro không làm đổi số nào.
- Ngày 2034 là suy luận từ phân bổ GPMB (13,158 tỷ, ~1,63 tỷ/năm, Q3 TM9), không đến từ hợp đồng thuê. Điều này không đổi.

## Kết quả rà: CHƯA nhất quán ở phần CHỮ
Tài liệu đã đúng ở chỗ *không tính vào tâm*. Nhưng ở 5 chỗ, chúng vẫn gọi nhánh này là **"rủi ro xuống lớn nhất"**, trái với chỉ đạo:

| # | Vị trí | Chữ hiện tại (trích) | Đề xuất |
|---|---|---|---|
| 1 | Sổ `kb/dd_price_zones.json` PAT rev4 + rev5 · `verdict_label` | "Rủi ro xuống lớn nhất chưa có xác suất: thuê đất KCN hết ~2034 không gia hạn (−28,7%)." | "Thuê đất KCN: theo dõi (user 25/11: hết hạn sẽ thuê lại, không phải rủi ro; base đã giả định gia hạn) — KHÔNG tính vào tâm/E17; xác nhận hạn + điều khoản gia hạn ở BCTC KT 2026." |
| 2 | Sổ rev4 + rev5 · `notes` | "thuê đất hết 2034/2042 không gia hạn 39.598/49.167 sau CK;" | "thuê đất KCN: theo dõi, không phải rủi ro (user 25/11); độ nhạy giả định không gia hạn 39.598/49.167 chỉ lưu vết ở adj.json đợt 4, không dùng;" |
| 3 | `dd_recheck_20261125w4/PAT/ADJ_CENTER.md:25` | "nhánh thuê đất 2034 (−28,7%) lớn gấp ~7 lần Σ" | bỏ vế này; cảnh báo bất đối xứng vẫn giữ cho các hạng mục C còn lại (bảo đảm chéo −2,76%, đình chỉ lò −2,72%, capex môi trường) |
| 4 | `…w4/PAT/SUMMARY.md:25` ("Rủi ro / việc mở" #1: "Hạn HĐ thuê đất … — lớn nhất") | chuyển xuống mục **Theo dõi** (không đánh số rủi ro): "Hạn/điều khoản gia hạn HĐ thuê đất KCN Tằng Loỏng — xác nhận ở BCTC KT 2026; user 25/11: thuê lại, không phải rủi ro" |
| 5 | `…w4/PAT/ADJ_CENTER.md:17,30` + `adj.json` hạng mục C / dòng trigger "tới −15.900" | đổi nhãn cột thành "theo dõi — không phải rủi ro (user 25/11)"; dòng trigger: "BCTC KT 2026 xác nhận hạn/gia hạn ⇒ đóng mục theo dõi; Δ 0" |

**Giữ nguyên:** `skeptic_status` trong sổ và `skeptic/r1.json`. Đây là bản ghi những gì skeptic đã nói, là provenance, không viết lại.

## Cách áp (đề xuất; KHÔNG tự làm, chờ Mike/user)
Không sửa tại chỗ các file nguồn của đợt 4. Selfcheck sổ khoá md5 của `adj.json` (`center_adj_md5`) và `assumptions_rev6.md`, đồng thời so evidence quote nguyên văn với `REPORT_recheck_PAT.md`. Sửa tại chỗ sẽ làm sổ FAIL (#5 chạm `adj.json` ⇒ FAIL chắc chắn).
- **Cách 1 (đề xuất):** thêm một entry sổ **rev6 chỉ đổi chữ** (`LEDGER_PROPOSAL_PAT_rev6_text.json`, thư mục này), sửa #1 và #2. Mọi số, `center_adj*`, nguồn và khoá md5 giữ nguyên rev5. File này (ERRATA) là bản đính chính chữ cho #3–#5, nằm cạnh tài liệu đợt 4 mà không ghi đè nó. Selfcheck sổ tạm: xem `../selfcheck/`.
- Cách 2: không ghi sổ, chỉ giữ ERRATA này và sửa chữ ở rev kế tiếp có lý do số (BCTC Q4/2026). Rủi ro của cách này: công cụ đọc `verdict_label` (vd `bin/dd_reconfirm_plan.py`) và báo cáo trích sổ sẽ tiếp tục in "rủi ro xuống lớn nhất" cho tới lúc đó.

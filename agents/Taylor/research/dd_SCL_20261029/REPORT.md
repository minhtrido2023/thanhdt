# DD SCL r2 — CTCP Sông Đà Cao Cường · 03/11/2026 · job `Taylor_20261103_152941` (NỘI BỘ)

> Bản r1 (29/10, tâm 25.500 ex-quyền) lưu ở `archive_internal/REPORT_r1_20261029.md` — §2–§7, §11–§13 của r1 (phải thu, chất lượng LN,
> bảng cân đối, quyền mua, pháp lý, đối chiếu BQ, đính chính skeptic) VẪN là nền dữ kiện; r2 chỉ làm lại ĐỊNH GIÁ theo luật user 03/11.
> Mô hình: `r2/calc/model_r2.py` (MÙ GIÁ) → khoá `r2/calc/LOCK_md5_r2.txt` 22:34:41 ICT → MỚI đọc giá/ADV (`compare_r2.py`, `reverse_r2.py`).
> Trung thực: r1 và audit 03/11 đã biết giá (31.100 / 30.000) ⇒ khoá chỉ chứng minh thứ tự chạy, không chứng minh "chưa từng thấy giá".
> Báo cáo NĐT: `investor_report_v2/SCL_DD_investor_report_20261103.{md,pdf,html}` (8 trang, thân ≈1.340 từ, CHƯA gửi email).

## 1. Kết quả (đ/cp; số đo từ `r2/calc/*_out.*`)

| | Trước CK thanh khoản | Sau CK 2,3% @1 tỷ đ |
|---|---|---|
| Tâm SAU quyền (44,84tr cp) | 23.075 | **22.543** |
| Vùng P25–P75 sau quyền | 20.405–25.717 | **19.935–25.125** |
| P10 / P90 sau quyền | 18.377 / 27.343 | 17.954 / 26.712 |
| Tâm TRƯỚC quyền (cum, 38,84tr cp) | 24.709 | **24.139** |
| Vùng P25–P75 cum | 21.626–27.759 | 21.128–27.120 |
| Nhánh sau quyền CYC .50 / ADMIN .30 / STRUCT .20 | 21.297 / 23.837 / 26.377 | 20.806 / 23.288 / 25.769 |

- Giá đóng 03/11 **30.000 cum** (tav2_bq.ticker); TERP 27.659; giá trị quyền theo thị trường 2.341 đ/cp cũ, theo FV sau CK ≈1.551.
- **Nhãn (đăng ký trước trong model_r2_out.json): TRÊN vùng hợp lý** — cả cum (30.000 > P90 cum 28.953) lẫn TERP (27.659 > P90 26.712); trước CK thanh khoản cũng TRÊN.
- Kể cả STRUCTURAL (biên ròng 12,7% vĩnh viễn) 25.769 < TERP.
- Định giá ngược: TERP ngầm định r 11,65% ⇔ lãi huy động 5,55% (−185bp so 7,40%); hoặc E chuẩn hoá 147,7 tỷ (+24% so 118,7).
- Độ nhạy lãi huy động (β=1): −100bp +11,0% · −50bp +5,2% · +50bp −4,7% · +100bp −8,9%; β=0,5 = một nửa.

## 2. Kiểm kê khoản cộng/trừ gắn dự án mới

| Khoản | r1 | r2 (base) | Cơ sở độc lập |
|---|---|---|---|
| Phả Lại đã chi 190,7 tỷ (XDCB 178,0 + 12,7) | Không tính; lãi vay của nợ tài trợ vẫn nằm trong LN 135 ⇒ NPV âm ngầm | Tài sản giá vốn − nợ tài trợ mệnh giá (ròng 0) + cộng lại lãi vay sau thuế tương ứng vào E | BCTC HN Q3: XDCB; LCTT capex 9T 198,1 vs CFO 9,9 ⇒ vay tài trợ |
| Tách tro Vĩnh Tân GĐ2 14,8 tỷ | Không tính | Như trên | BCTC HN Q3 |
| Phả Lại còn ≈72 tỷ (ước lượng) | — | NPV 0 | 262,9 − 190,7 |
| Phả Lại LN tăng thêm +34 tỷ (bull 20%) | Có (PE 10) | **Bỏ** — không có giá/sản lượng/hợp đồng đầu ra kiểm được; chỉ độ nhạy IRR: 15% ⇒ +651, 17% ⇒ +1.520, 12% ⇒ −651, 10% ⇒ −1.520 đ/cp | — |
| Thừa cung vùng do dây chuyền mới | — | Không trừ (chỉ có nhận định ngành chung) | Bobby: không có số công suất toàn quốc |
| Trả trước người bán 86,6 tỷ | — | Không cộng thêm (vốn lưu động, mục đích từng khoản không công bố) | BCTC V.3 |

**Hiệu ứng đo được của sửa Phả Lại+tách tro: +96,1 tỷ = +2.143 đ/cp sau quyền (+9,3% tâm trước CK).** Audit 03/11 ước +4.253 (+16,7%) bằng
cách cộng đủ 190,7 tỷ — đếm dư: ở r1 nợ tài trợ chỉ bị trừ qua lãi vay vốn hoá theo P/E (≈0,4–0,8× mệnh giá), không bị trừ mệnh giá, nên
phần phải "trả lại" là PV lãi vay đó, không phải toàn bộ giá vốn. Lãi suất nợ dự án lấy lưới {4,96% = lãi vay Q3×4/dư nợ 30/9; 9,5% BIDV DH}.

## 3. Cầu r1 → r2 (tổng giá trị, tỷ đ; `reverse_r2_out.json`)

r1 1.143 (E kỳ vọng 123 × P/E bình quân 9,29) → ΔE −40,3 (E r2 118,7: chuẩn hoá chu kỳ thay bear 65 tỷ/30% + bỏ bull Phả Lại + cộng lãi nợ dự án)
→ Δbội số −143,1 (P/E nội tại 8,09 tại r 13,5%, g 3–5%, ROE 15–20% thay P/E 9–10 chủ quan) → +75 tiền quyền (r1 không cộng) = 1.034,6
⇒ /44,84tr = 23.075. **Tâm giảm 9,5% so r1 dù sửa Phả Lại +9,3%: nhân tố chính là bội số (r1 PE 9–10 không có cơ sở r).**
Đối chiếu peer (không làm neo): P/E TTM 8 mã VLXD 28/10 trung vị ≈8,85 (5,1–13,1) — P/E nội tại 7,7–8,8 nằm ở nửa dưới.

## 4. Chuẩn hoá chu kỳ tài sản hiện hữu

- Dữ liệu: biên ròng NP_P0/Revenue_P0 (DT gộp) năm 2020–2025 + TTM: 8,1 / 6,6 / 4,7 / 9,6 / 6,2 / 10,4 / **12,7%** (đỉnh 7 năm). TB 2020–TTM 8,32%; TB 2023–TTM 9,72%;
  phương pháp lệch biên gộp (GPM_P0 TTM 36,6% vs TB 2023–TTM 36,3%, +0,36pp) ⇒ 12,44%.
- Nhánh Bobby (sector read VLXD nhẹ 29/10, đọc mù): CYCLICAL .50 quay về TB 100% · ADMIN_GATED .30 quay 50% · STRUCTURAL .20 giữ nguyên.
- DT cơ sở {TTM 924,9; 2026E 983,1 (Q4=Q3, ước lượng)} — DT gộp; thuế 20,0% (Q3 thực tế).
- Giới hạn: lịch sử trước 2023 là quy mô/cơ cấu khác (DT ~300 tỷ, trước Green SCL) ⇒ cửa sổ 2020–TTM có thể kéo biên xuống quá tay; cả hai cửa sổ vào lưới (luật 12).
- Thiên lệch đã biết của phương pháp vốn chủ: nợ hiện hữu (ngoài nợ dự án) bị "trừ" qua lãi vay vốn hoá ở P/E (< mệnh giá) ⇒ thiên lên nhẹ (ước lượng ≈ −400 đ/cp nếu trừ mệnh giá, chưa đưa vào lưới).

## 5. Thanh khoản (phương pháp đăng ký trước; số từ tav2_bq.ticker 120 phiên đến 03/11)

ADV giá trị trung vị 2,24 tỷ (TB 2,96; trung vị 60 phiên 3,46); σ ngày 2,72%; spread Corwin–Schultz 0,97%; 0 phiên không khớp.
CK = nửa spread + 1,0·σ·√(Q/ADV): 1 tỷ 2,31% (Y=0,5: 1,40%) · 5 tỷ 4,55% (2,52%) · 10 tỷ 6,24% (3,36%); số phiên thoát @20%/10%: 2,2/4,5 · 11/22 · 22/45.
Amihud tuyến tính (chỉ đối chiếu, phóng đại khi Q lớn): 1,8% / 9,2% / 18,5%. Free float: cổ đông lớn đã biết 24,0% (Kiều Văn Mát 11,54% + Cao Cường 12,50%) ⇒ ≤76% (ước lượng).
Không dùng số liệu thực thi nội bộ (SCL fill 26–30/10 quá ít, lẫn chênh giá do tin quyền mua).

## 6. Quyền mua (đúng cơ chế)

V/cp sau quyền = (V_trước + 75 tỷ)/44,84tr; cổ phần cum ≡ 1,154453 cp sau − 0,154453×12.500 ⇒ V_cum ≈ V_trước/38,84tr (khớp do 6,0tr/38,84tr ≈ tỷ lệ).
Người thực hiện đủ: tổng giá trị không đổi; bỏ quyền mất (V_sau − 12.500)×0,154453 ≈ 1.551 đ/cp (theo FV) hoặc 2.341 (theo TERP).
Luật nội bộ LAG/quyền (ack 21/10) KHÔNG đổi — SCL đã thoái khỏi LAG 29–30/10 (kb/projects/scl-dd-20261029.md).

## 7. Pháp lý — WARNING (không vào base)

Pha loãng 2,6× từ 2023; ESOP 0,92tr @10.000; vay cổ đông lớn 26 tỷ @10%; không thấy khởi tố/xử phạt (tra cứu Wendy 29/10, giới hạn). Không làm mới tra cứu trong r2.

## 8. Việc còn mở

- CHƯA chạy fundamental-skeptic trên r2 (Mike gọi). Điểm nên tấn công: P/E nội tại tại r 13,5% vs peer; cửa sổ chuẩn hoá 2020–TTM; lãi nợ dự án 4,96%.
- Email: CHƯA gửi (chờ user nói "gửi email"). Dry-run OK: 11 ảnh, 5,6MB, mọi `<img` có alt.
- `dd_price_zones_selfcheck`: entry SCL rev2 sạch; 4 lỗi tồn tại ở entry NNC #40 / MVC #41 (báo cáo NĐT của job khác đã dựng lại sau khi ghi sổ) — không thuộc job này.

# PAT — Tâm kỳ vọng điều chỉnh (E17/V9) — rev6 (sổ rev4), 25/11/2026, job Taylor_20261125_063651

Phương pháp khoá trước: `dd_adjcenter_20261124/PREREG_adj.md` (md5 ef5157cb…) + `PREREG_adj_v2.md` (md5 835dfc1e…); phân loại hạng mục khoá ở `assumptions_rev6.md` (md5 5207e413…) TRƯỚC khi chạy mô hình. MÙ GIÁ: không đọc giá thị trường khi dựng. Áp vì skeptic r1 = INCONCLUSIVE (`skeptic/r1.json`).

**Tâm kỳ vọng điều chỉnh: 57.872 đ/cp sau CK (dải 56.700–59.045; +4,22% so với tâm base 55.527); căn cứ 2 hạng mục bậc B** (trước CK 64.302).

## Hạng mục vào tâm (A/B)
| # | Hạng mục | Hướng | Bậc | p [dải] | m (% tâm, đo mô hình) | p×m |
|---|---|---|---|---|---|---|
| 1 | Ô (A tắt, B bật) ở mức O2 — Q2/26 LNST% 21,2% (F4:74) | lên | B (1 quan sát) | 0,50 [0,25;0,75] | +6,18% | +3,09% |
| 2 | Giải phóng tồn kho dư 44,44 tỷ (F2:79) | lên | B (1 quan sát) | 0,50 [0,25;0,75] | +2,27% | +1,13% |
Σ = +4,22% (< 5%, nhưng vẫn chạy tổ hợp: 4 ô cell D/O2 × tồn kho 0/44,44 trọng số p; trùng cộng tuyến tính tới đồng). Dải = tổ hợp ở p 0,25 / 0,75 (m là số mô hình trực tiếp, không phải ước lượng ⇒ không có dải m).

## Chỉ độ nhạy (C / LUẬT) — KHÔNG vào tâm
| Hạng mục | Hướng | Δ tâm | Vì sao C |
|---|---|---|---|
| Thuê đất KCN hết ~2034 không gia hạn | xuống | −28,7% (+hoàn nguyên 50 tỷ: −29,9%; hết 2042: −11,5%) | ngày suy từ phân bổ GPMB, không phải HĐ; xác suất không gia hạn không có dữ liệu |
| Bảo đảm chéo Vietinbank 42,6 tỷ bị thực hiện | xuống | −2,76% | dư nợ bên được bảo đảm KHÔNG NÊU |
| Pháp nhân PAT bị truy cứu Đ.235 — đình chỉ lò 6 tháng (2027) | xuống | −2,72% (ước lượng cơ học) | chưa có quyết định đích danh; pháp lý chỉ WARNING |
| Capex môi trường (D3) X tỷ một lần | xuống | −36 đ/cp sau CK mỗi tỷ | không có số (F1) |
| ΔVLĐ phần ngoài tồn kho | lên | chưa đo | — |
| 70 tỷ BIDV hoàn theo mệnh giá | lên | +2,92% | thời hạn bảo lãnh không có dữ liệu |
| [LUẬT] r 13,5% vs Ke 12,3% (E15) | lên | +7,66% | tham số luật |
| [LUẬT] RONIC=Ke cả pha tường minh (g=0) | xuống | −8,47% | V5: NARROW không trừ ở pha dự báo (user 08/11); D4 chỉ cuối kỳ |
**Cảnh báo bất đối xứng (minh bạch):** cả hai hạng mục vào tâm đều chiều LÊN; mọi hạng mục chiều xuống đều C vì thiếu XÁC SUẤT (không thiếu độ lớn). Không được đọc 57.872 là "rủi ro đã giảm": nhánh thuê đất 2034 (−28,7%) lớn gấp ~7 lần Σ. Đọc tâm điều chỉnh CÙNG bảng dưới.

## Bảng điều kiện đổi số
| Sự kiện/dữ kiện | Khi nào | Hướng + độ lớn | Δ tâm sau CK |
|---|---|---|---|
| HĐ thuê đất KCN / thuyết minh BCTC KT 2026 (hạn, quyền gia hạn, hoàn nguyên) | ~Q1–Q2/2027 hoặc CBTT | hết 2034 không quyền gia hạn ⇒ C→A: × (1 − 0,287 p); có quyền gia hạn / hạn ≥2050 ⇒ đóng | tới −15.900 (p=1) / 0 |
| BCTC Q4/2026: tồn kho 31/12 và biên LNST Q4 | cuối 01/2027 | tồn kho về ~75 ⇒ #2 thành A p0,9 (+0,9pp); biên ≤13% ở trạng thái A tắt/B bật ⇒ quan sát ngược, p#1 → 0,35 (−0,9pp) | +505 / −515 |
| Quyết định tố tụng đích danh pháp nhân PAT / đình chỉ lò | theo vụ án | ≈ −2,7% mỗi 6 tháng | ≈ −1.500 / 6 tháng |
| Thuyết minh bảo đảm TM4 Q4/2026 | cuối 01/2027 | gỡ ⇒ đóng; bị thực hiện ⇒ A −2,76% | 0 / −1.530 |
| NQ ĐHĐCĐ 2027/HĐQT: capex môi trường | ~04/2027 | X tỷ ⇒ vào base D3 | −36 đ/cp mỗi tỷ |
| Tờ trình GD bên liên quan DLC–PAT (giá P4) | ĐHĐCĐ 2027 | cập nhật nút T, chạy lại cây | r5 §2: T bi quan ≈ −4,9% |
| Lãi huy động 12T ±50bp (β=1) | hằng tháng | r ±50bp | +3,0% / −2,8% |
Có dữ kiện mới ⇒ chạy lại mô hình (rev mới), không cộng tay.

Cổ tức: không có cổ tức tiền đã công bố chưa GDKHQ trong nguồn đã đọc (cần kiểm chứng CBTT) ⇒ một dòng. Tâm điều chỉnh KHÔNG thay tâm base trong sổ/luật 0,85×tâm/luật 4.

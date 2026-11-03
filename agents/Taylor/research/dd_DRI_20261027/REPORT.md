# DD DRI — r5 (job `Taylor_20261103_160959`, 03/11/2026) — NỘI BỘ

> Sửa theo `SKEPTIC_R4_20261103.md` (REFUTED medium-high, 6 điểm). Đăng ký trước: `r5/PREREG_r5.md` (commit cee65d404, TRƯỚC khi chạy).
> Calc `r5/calc/` — khoá `LOCK_md5_r5.txt` 23:12:56 ICT TRƯỚC bước thanh khoản + so giá (đã biết giá 13.400 và số đo của skeptic ⇒ khoá chỉ chứng minh thứ tự chạy).
> Báo cáo NĐT: `investor_report_v4/DRI_DD_investor_report_20261103.{md,pdf,html}` (ĐÈ; bản r4 lưu `archive_internal/DRI_DD_investor_report_20261103_rev1_r4.md`) — **CHƯA gửi email** (dry-run OK).
> r4 nội bộ: `archive_internal/REPORT_20261103_r4.md`. **Trạng thái nắm giữ:** DRI đã bán hết theo quy tắc cờ (chỉ ở bản nội bộ).
> Không còn vòng skeptic (Mike kiểm cơ học rồi trình user).

## 0. Kết quả (số: `r5/calc/dri_model_r5_out.txt`, `liquidity_r5_out.txt`)
| | Trước CK | Sau CK 5 tỷ (−2,0%, Y=1) |
|---|---|---|
| Tâm base (mid 2,221, L27, r13,5%) | **15.860** | **15.543** |
| Thang P10/P25/P50/P75/P90 (lưới 27 ô đối xứng) | 13.157 / 13.573 / 15.576 / 16.825 / 18.401 | 12.893 / **13.301** / 15.265 / **16.488** / 18.033 |
| TB lưới base | 15.411 | 15.103 |
| Tái canh bị buộc (T1 cũ + XDCB) tâm; P25–P75 | 11.924; 10.307–12.737 | 11.685; 10.101–12.482 |
| Kỳ vọng (1−p)·TB base + p·TB bị buộc, p=20% (nhận định) | 14.654 | **14.360** (p0/10/30: 15.103/14.732/13.989) |
| Diễn giải khác: thanh lý 2029–36 = tài sản hiện hữu, không trồng lại (+XDCB) | 13.454 (P25–P75 11.973–14.046) | 13.184 |
- **Giá 13.400** (đóng cửa 03/11, DNSE ohlc 1D, `../dd_audit_newproject_20261103/close_20261103.md`). Nhãn đăng ký trước (thang sau CK 5 tỷ): **HỢP LÝ, sát cận dưới** (P25 13.301; +0,7%). 1 tỷ: RẺ CÓ ĐIỀU KIỆN (P25 13.451); 10 tỷ: HỢP LÝ (P25 13.189).
- **Luật sổ mức giá (giá < tâm −15%)**: 13.400 = **−13,8%** so tâm base sau CK 15.543 (ngưỡng 13.211) ⇒ **KHÔNG ĐẠT**; −6,7% so kỳ vọng 14.360 ⇒ không đạt. Theo diễn giải thanh lý: nhãn HỢP LÝ (tâm 13.184).
- Cầu nối r4→r5 (trước CK): mid 2,341→2,221 **−1.090** (16.950→15.860). Thang trên đổi chủ yếu do bỏ "TB 2006–26" (P90 23.175→18.401).

## 1. Điểm skeptic → xử lý
1. **Cửa sổ mid**: chọn 2014-01..2026-09 (lý do ghi trong PREREG trước khi chạy: sau siêu chu kỳ 2010–13; dùng toàn bộ 153 tháng hậu siêu chu kỳ, ≥2 chu kỳ trọn). Độ nhạy (tâm trước CK): 10 năm trượt 2,201 → 15.678; năm trọn 2014–25 2,204 → 15.707; r4 2013–26 2,341 → 16.950; đáy–đáy 2016–23 2,142 → 15.141. Q3/26 2,753 = phân vị 89% chuỗi thực 2014–26, +24% so mid.
2. **Lưới mid đối xứng** {P25 1,924 · TB 2,221 · P75 2,432} cùng cửa sổ; bỏ TB 2006–26. (Lệch TB−P25 0,297 vs P75−TB 0,211: đối xứng theo phân vị, không theo khoảng cách.)
3. **L_tập {22,27,32} = GIẢ ĐỊNH** (không tìm thấy định mức chu kỳ khai thác có nguồn trong tài liệu đã tải; BCTN thanh lý theo chất lượng vườn ⇒ đời có thể ngắn hơn). Một trục (trước CK): L22 13.573 · L24 14.677 · L27 15.860 · L32 17.007. Bản NĐT ghi "giả định".
4. **NPV0 tái canh**: base giữ luật 20 (thanh lý 2029–36 coi là một phần chương trình tái canh ⇒ vườn hiện hữu cạo tới hết đời). Ghi tường minh là DIỄN GIẢI; cách đọc khác báo song song (13.454 trước CK; skeptic đo 14.290 ở mid 2,341). p=20% bị buộc = nhận định, có độ nhạy p. Hợp đồng 01616/KĐ/DDT4 vẫn chưa xác minh.
5. **Lỗi nhỏ**: (a) capex: chi chăm sóc 24,655 tr/ha/năm khớp BCTN 2024 tr.57 — chỉ hệ số 7 năm KTCB là giả định (sửa câu "chưa nguồn"); (b) kịch bản bị buộc nay CỘNG XDCB 72,71 tỷ (+993 đ/cp); (c) engine r3 đọc `WorkingClaude/data/rubber_monthly.csv` + `macro_usdvnd.csv` sống ⇒ r5 chuyển hướng `open` sang snapshot `r5/calc/data/` (assert không đọc file sống), md5 trong LOCK. Snapshot rubber trùng md5 file sống lúc khoá (20000b0b…).
6. **Flip-flop**: tâm sau CK 10.500 (30/10) → 16.610 (r4) → **15.543** (r5). Phần hợp lệ = luật 20 (NPV0) + luật 21 (r, CK) + sửa lỗi đơn vị danh nghĩa/thực; phần cửa sổ + đuôi trên bất đối xứng của r4 (−1,1k tâm, −5,1k P90 trước CK) đã gỡ. Không có dữ kiện cơ bản tích cực mới (Q3 trượt).

## 2. Kịch bản trình bày (bản NĐT)
Cơ sở 80% = P25–P75 lưới base sau CK 13.301–16.488; Tái canh bị buộc 20% = P25–P75 lưới bị buộc 10.101–12.482; bình quân 14.360. Bỏ dải "tích cực P75–P90" của r4 (đếm đôi đuôi trên của lưới).

## 3. Giữ nguyên từ r4
r 13,5% neo huy động 7,40%, β1 (±100bp ⇒ +2,9/−2,8%; β0,5 ±1,4%); thanh khoản (ADV trung vị 8,33 tỷ, σ 2,58%; CK 1/5/10 tỷ 0,9/2,0/2,8%); XDCB giá vốn; các cấu phần engine có nguồn BCTC3; pháp lý tái canh (§1 r4).

## 4. Sổ mức giá
`kb/dd_price_zones.json` DRI@2026-11-03 **rev 2** (supersedes #1): vùng 13.300–16.490, tâm kỳ vọng 14.360, center_alt 15.540, price_ref 13.400. Rev 1 trỏ sang bản lưu `archive_internal/…_rev1_r4.md`. `dd_price_zones_selfcheck.py`: 0 lỗi.

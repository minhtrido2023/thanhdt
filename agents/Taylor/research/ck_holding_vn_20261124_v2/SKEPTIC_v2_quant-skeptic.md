# quant-skeptic — CK holding v2 (24/11/2026, 1 vòng) — VERDICT: INCONCLUSIVE / medium

Mike ghi lại từ hand-back của subagent quant-skeptic (agentId a394279672d752212). Read-only; tái tính trong bản sao /tmp.

**Kết luận (b) "không đủ làm BASE HHS, giữ 0% + dải" ĐỨNG VỮNG** — mọi lỗi tìm được đều làm bất định lớn hơn. Nhưng KHÔNG trích 6,5/23/38 ở độ chính xác đã ghi trước khi sửa 3 lỗi dưới.

## Tái lập
- LOCK_md5 19/19 khớp. Chạy lại `calc_ck_v2.py` bằng `python3` hệ thống (pandas 2.3.3): bit-exact (`058b2a14…`, calc_out `3e1421fa…`, panel `45a76614…`).
- Tính lại từ `panel_v2.csv`: N=12, trung vị 6,458%, q25 −19,13%, q75 +38,02% — khớp.
- ⚠️ Bẫy môi trường: dưới `$DNA_PYEXE` (pandas 3) script ra **N=0 không báo lỗi** — `calc_ck_v2.py:102` `if r.nested_via:` (None→NaN truthy).

## Phát hiện
1. **PAN double-count corp-action (đòn 8, cục bộ).** Thưởng 20% ex **29/05/2026**; 29/05 và 30/06 code nhân giá đã ex (24.450 / 22.900) với số CP TRƯỚC sự kiện 208,89 tr ⇒ MV mẹ thấp ~16,7%, CK PAN 11,3% / 17,9% (đúng: −6,5% / +1,5%). 250,67 tr = 208,89×1,2 chính xác. Sửa số CP 05–09/2026 về 250,67 tr: PAN 3,2%→1,5%, **trung vị chung 6,46%→5,63%**, đường tháng 05/2026 đổi dấu +1,4%→−6,5%.
2. **T_eff sai.** 0,50 / 6,9 (`calc_ck_v2.py:195-196`) tính trên 21 tháng gồm 12 tháng chỉ có VIC. Trên 9 tháng cắt ngang thật (n≥11): rho **0,80**, T_eff **≈ 1,0**.
3. **Tiền lọc có thể loại sót.** Prescreen dùng VCSH tổng (gồm NCI) ⇒ độ phủ thấp giả 1,3–2,4× (OGC 0,50→1,20; APH 0,59→1,11; PAN 0,42→0,71). Mã 0,25–0,29 (PVI, PPC, VLC, C32, PET, AAA, VSF) có thể vẫn đạt ≥60%. Prescreen chụp 1 ngày 30/10/2026 (chọn mẫu bằng thông tin tương lai so với tháng 03–09). Ảnh hưởng lên trung vị: chưa đo.
4. **Giá con mỏng vẫn tính là giá thị trường.** Cờ `thin` (`calc_ck_v2.py:70`) tính nhưng không dùng. CMX (68%, đuôi trên) chỉ có con CMM: ADV60 0,045 tỷ, sở hữu 74%. Bản chỉ con thanh khoản: −12,6%.
5. Tỷ lệ sở hữu giữ cố định khi con phát hành riêng lẻ/quyền mua (OCH +65%, LBM, GIC) — thử OCH: không trọng yếu.
6. Bootstrap khối thực chất = bootstrap theo holding trong 1 chế độ thị trường, không mô hình cú sốc chung.
7. VIC/MVN chỉ kéo đuôi dưới; bỏ cả hai trung vị ~10,1%.

## Đã đạt
Không look-ahead ở số chính (PIT gated stake_date+90, Release_Date ≤ D, oshares_at PIT). Bản "fixed" chỉ ở độ nhạy/ghi nhãn. Bước nhảy giá×số CP đúng ở VIC 12/2025, VHM 08/2026, GEX/GEE 05/2026, TCB, SZL, LHC.

## Điểm v1 → v2
Trôi theo ngày/N hiệu dụng: một phần (T_eff sai) · giá con stale: xử lý stale, CHƯA xử lý mỏng · BVPS×OShares quanh ISS: một phần (PAN còn) · VCSH mẹ: ĐÃ · độ nhạy ngưỡng: ĐÃ · mẫu hardcode: một phần (prescreen).

## Hướng lệch của (b)
Nhẹ về phía 0% (có lợi cho định giá HHS): mọi cách cắt không look-ahead (trừ bản con thanh khoản) cho trung vị dương 1,5–10%; tháng gần nhất 23%; nhóm giống HHS (N=2) ở ~30%. **0% là đầu LẠC QUAN của khoảng đo được, không phải điểm trung tính.** Dải chỉ có chiết khấu, không có premium.

## Việc cần sửa (chưa làm — chờ user)
1. PAN dùng 250,67 tr từ ex 29/05/2026 (và 07–09) ⇒ headline ~5,6%.
2. Tính lại T_eff chỉ trên tháng n≥11.
3. Hạ ngưỡng prescreen ~15% hoặc tính độ phủ theo VCSH mẹ cho 116 mã; báo N/trung vị mới.
4. Thêm độ nhạy loại con mỏng (ADV60 < ~0,1 tỷ).
5. Ghi pandas 2.x hoặc sửa dòng 102 thành `isinstance(r.nested_via, str)`.
6. Ghi rõ base 0% là đầu lạc quan.

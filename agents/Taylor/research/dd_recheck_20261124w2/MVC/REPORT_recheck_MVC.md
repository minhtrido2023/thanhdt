# MVC — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, đợt 2, job Taylor_20261124_131351)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/MVC/REPORT_r3.md`, sổ rev9, dd_date 2026-11-03).
- **Không làm lại mô hình.** Tái dùng nguyên `calc_r3/mvc_redo_r3.py` + `assumptions_r3.json` (md5 `6c70fdca…`, không sửa) cùng chuỗi engine MVC r8/r6 + NNC r6/r5/r4/r3.
- **Phạm vi chạy lại:** chỉ đổi **r** trên lưới 157.464 kết cục (E15, dải Ke, ±50/±100bp), và đo 2 hạng mục ở §3/§5.

**Nguồn calc.** Gốc bị TRIM khỏi git ngày 19/11. Khôi phục:

```
git archive 14ad1c925^ dd_redo_20261105/{MVC,NNC,common.py,_shared}
git archive ef7472f56^ dd_NNC_20261030
git archive bffae9c42^ dd_MVC_20261103
```
- Đích: `/tmp/ddrestore_MVCw2`.
- Kiểm md5: 25/26 dòng `LOCK_r3_md5.txt` khớp. Dòng lệch là `data/deposit_rate_vn_events.csv` (thêm dòng sau 06/11); lãi hiệu dụng đọc lại vẫn 7,40%.

**Calc.**
- `calc/calc_recheck.py` (độ nhạy r). **Chân CONTROL:** stdout của mô hình trùng byte r3 (md5 `3b13f061…`) và `mvc_redo_r3_out.json` trùng (md5 `c70f8350…`); tâm/P10/P90 được assert. Chạy 2 lần: `run1.txt` = `run2.txt` (md5 `21099185…`).
- `calc/calc_items.py` (2 hạng mục). Chạy 2 lần: `items_run1.txt` = `items_run2.txt` (md5 `2fc6efa4…`).

**Mù giá.** Phần đổi r không dùng giá. Giá 13.500 (06/11/2026) kế thừa r3, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ): 16.241 đ/cp — vùng 9.940–23.471 (P10–P90). KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 16.761 đ/cp (+3,20% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (proxy lệch DD, k=1.33–2.33)** — phân vị [fade 70, hold 79], 112 tháng, N hiệu dụng ≈ 6.3 ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=2.86)

- **Nhãn** (giá 13.500, BQ 06/11/2026, kế thừa r3): **TRONG vùng**. Luật 4 ĐẠT ở mọi cỡ (5 tỷ: ngưỡng 0,85 × 16.241 = 13.805; biên MỎNG 2,2%).
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ cần soát cơ học (MECH).
- **Hạng mục thiếu (phát hiện trong recheck, chưa vào base):** trích quỹ từ LNST theo NQ ĐHĐCĐ 2026 = **11%** (KTPL 7% + thù lao HĐQT/BKS 2% + thưởng BĐH 2%) chưa trừ. Đo bằng mô hình (§5): **−4,59%** (chỉ trên dòng tiền hoạt động trực tiếp) … **−10,13%** (thêm phần NNC + 11% LNST 9T/26 đang nằm trong tiền ròng).
  - Riêng mức −4,59% đã đủ đẩy luật 4 ở cỡ 5 tỷ về TRƯỢT: 16.241 × (1 − 4,59%) ≈ 15.496 ⇒ ngưỡng 13.172 < giá 13.500 (ước lượng tuyến tính).
  - Không sửa base trong recheck (đúng quy trình: đổi mô hình = rev mới); đưa vào E17 và phạm vi phản biện.
- **Bước 0 (tham số nền bị phủ?): KHÔNG.**
  - (i) **CK holding:** base 0% (r3 §7) = mốc 0% của dải 0…+20% user chốt 24/11 (`kb/projects/ck-hhs-reference-range-20261124.md`) ⇒ không bị phủ. Độ nhạy 6% của r3 tham chiếu mốc +6% nay đã bỏ ⇒ thay bằng +20% (§3).
  - (ii) **r:** neo 03/11 7,40%; đọc lại 24/11 vẫn 7,40% ⇒ Δ = 0, r = 13,5%.
  - (iii) **RONIC terminal:** không áp — mọi mảng có hạn (GP Tân Lập 2035–2045 theo kịch bản, BOT 2–8 năm, NNC tới 2043).
  - (iv) **NNC lồng trong MVC:** dùng NNC r3; tâm base NNC trong sổ (rev5–7 = 61.273) chưa đổi ⇒ không bị phủ.
  - (v) **Độ nhạy r** nay tính trên lưới (§2).
- **Sizing (V8):** đề xuất **2% NAV** (đầu dưới) do thanh khoản rất thấp (ADV60 0,189 tỷ), moat NONE trực tiếp và đỉnh lợi nhuận. Tranche ≤ 20% ADV60 / phiên như r3.

## 1. Thay đổi so với r3
| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 3 | D4 dải Ke + ±50/±100bp | ±100bp chỉ ở tham số trung tâm | Trên lưới (§2) | 0 |
| 4 | CK holding | 6% / 15% | + mốc 20% của dải user chốt (§3) | 0 (độ nhạy) |
| 5 | D3 capex tuân thủ | Chưa soát | §3 | 0 |
| 6 | V6 | Chưa có | §3 (chỉ hiển thị) | 0 |
| 7 | Trích quỹ 11% LNST | Không có | Đo §5, đưa vào E17 | 0 ở base |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r, trên lưới 157.464 kết cục
r neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%), β = 1 (giả định), Δ đến 24/11 = 0. Đổi r cũng đổi r của NNC trong mô hình (`N6.R_ANCHOR`). Số sau CK 5 tỷ (8,55%).

| r | Tâm | P10 | P50 | P90 | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|---|---|
| 12,3% (E15) | 16.761 | 10.036 | 15.801 | 24.515 | +520 | +3,20 |
| 12,5% (−100bp) | 16.671 | 10.018 | 15.723 | 24.322 | +430 | +2,65 |
| 13,0% (−50bp) | 16.451 | 9.982 | 15.539 | 23.867 | +210 | +1,29 |
| 13,4% | 16.283 | 9.948 | 15.395 | 23.546 | +42 | +0,26 |
| **13,5% BASE** | **16.241** | **9.940** | **15.359** | **23.471** | 0 | 0 |
| 14,0% (+50bp) | 16.040 | 9.905 | 15.190 | 23.105 | −201 | −1,24 |
| 14,5% (+100bp) | 15.847 | 9.870 | 15.025 | 22.733 | −394 | −2,43 |

- ±100bp khớp hướng và cỡ với r3 tính ở tham số trung tâm (−2,4% / +2,6%).
- Nhãn TRONG ở mọi r.
- Luật 4 @5 tỷ (giá 13.500): TRƯỢT ở 14,5% (ngưỡng 13.470); ĐẠT ở 14,0% (13.634). Biên mỏng.

## 3. Soát luật B5 (D3/D4/V1–V8)
- **D4:** terminal không áp (§0). Pha dự báo không thưởng moat (NONE trực tiếp; NARROW/LOCATION chỉ qua NNC).
- **D3 capex tuân thủ:**
  - Chi phí phục hồi môi trường/đóng mỏ (Tân Lập + 2 mỏ mới) và tiền cấp quyền khai thác KHÔNG có dòng riêng trong mô hình.
  - Tiền cấp quyền đã chi 6,56 tỷ được tính trong giá sổ mỏ mới (B, NPV 0). Chi phí tiền mặt Tân Lập 130k/m³ suy từ biên gộp thực ⇒ đã gồm các khoản phí tính vào giá vốn. Phần ký quỹ phục hồi môi trường chưa đọc trong thuyết minh ⇒ **cần kiểm chứng**; không có số ⇒ không vào base.
  - Tham chiếu NNC cùng ngành: PHMT 4,50 tỷ, skeptic đánh giá không trọng yếu (chiết khấu tới cuối đời mỏ).
- **CK holding (cập nhật dải):** tại tham số trung tâm, phần NNC:
  - 20% ⇒ **−1.286 đ trước CK (−7,26%)**, ≈ −1.176 sau CK 5 tỷ;
  - 6%: −388; 15%: −967 (r3).
  - Base 0% giữ nguyên (đầu lạc quan của dải user chốt).
- **V1/D4 r:** §2. **E15/E16:** §0.
- **V3 thanh khoản:** đã đủ (r3 §4: CK 8,55% @5 tỷ ngoại suy 11,5× ADV; sleeve 40 tr 0,76%).
- **V5 moat:** đã đủ — 5F 09/11/2026 (`ADDENDUM_5F_r2.md`, <12 tháng): **NONE** vận hành trực tiếp, NARROW/LOCATION chỉ qua NNC. Rủi ro số 1 = giấy phép (hạn GP Tân Lập chưa kiểm chứng; GP 2 mỏ mới chưa cấp; nợ ròng tăng trước doanh thu).
- **V6 (chỉ hiển thị):** từ `dd_blend_20261111/out/apply_dd.csv` (khôi phục `3750ca176^`; fin_time 02/11): V_ngắn **8.108** (LNST chuẩn hoá 129,8 tỷ, ROE 9,0%, g 12,75% > ROE ⇒ tái đầu tư bị chặn ở 80%) / V_dài **13.114** / D = **0,481** < ln2 ⇒ không cờ. Caveat: r riêng của engine. V_ngắn sụp do ROE chuẩn hoá < g. Không trộn vào tâm.
- **V8:** 2% NAV (§0).

### Việc còn mở kế thừa
1. Hạn GP Tân Lập chưa xác minh (trục 2035/2040/2045).
2. Điều 195 Luật DN khi MVC lên 51% NNC — cần legal-vn trước khi mua.
3. Quét pháp lý sau 05/11 chưa làm.
4. Số BCTC đọc từ pdftotext, chưa soát mắt.

## 4. WARNING (giữ r3 §8)
- Sở hữu chéo 44,07% ↔ 10,3%, trùng Chủ tịch.
- Uỷ quyền mua NNC lên 51% (bên liên quan).
- Cụm công nghiệp tới 500 tỷ; nợ ròng tiến tới 1,4–1,5 nghìn tỷ trước doanh thu mỏ.
- Dư nợ BIDV 452 > hạn mức 350.
- Pháp lý chỉ WARNING.

## 5. Hạng mục thiếu đo được + phạm vi đề nghị cho phản biện (§E4)

**Trích quỹ từ LNST 11% (NQ ĐHĐCĐ 2026)**
- Nguồn: `dd_MVC_20261103/txt/VI_BienBanHopDaiHoiDongCoDongThuongNien2026VaNghiQuyet.txt:767-785` — "39% Quỹ đầu tư phát triển · 7% Quỹ khen thưởng – phúc lợi · 2% Quỹ thù lao HĐQT và BKS · 2% Quỹ thưởng Ban quản lý điều hành · 50% Quỹ cổ tức". Năm 2025: 7% + 1,5% + 1,5% = 10%.
- Mô hình chỉ trừ TỒN quỹ KTPL 6,52 tỷ trong tiền ròng; dòng trích hằng năm chưa trừ.
- Đo tại tham số trung tâm (`calc/calc_items_out.json`, trước CK, tâm 17.704); hệ số sở hữu chéo 1/(1 − s·c) = 1,0476:

| Cơ sở áp 11% | Δ % tâm |
|---|---|
| Dòng tiền hoạt động trực tiếp (Tân Lập 521,9 + BOT 92,6 + gạch/xăng 40,8 + Q4 50,0 tỷ, kỳ vọng trọng số) | **−4,59%** |
| + 11% LNST 9T/26 HN 231,77 tỷ (nằm trong tiền ròng, trích năm 2027; gồm lãi LK) | thêm −1,51% |
| + phần NNC (stake 619,5 tỷ) nếu cơ sở trích gồm lãi liên kết | tổng −10,13% |

**Phạm vi đề nghị**
- Thiếu hạng mục: trích quỹ 11% (cơ sở áp: LNST riêng hay hợp nhất?); PHMT/ký quỹ đóng mỏ; truyền dẫn các hạng mục mở của NNC (KTPL NNC, capex > khấu hao) qua 44,07%.
- Cân bằng hai chiều:
  - Lên: Ke đầu dưới +3,2%; trục biên Tân Lập 38%; ADMIN perm05.
  - Xuống: CK holding 20% −7,3%; chỉ CYCLICAL; đỉnh lợi nhuận (E16).
- Moat NONE trực tiếp.
- Kiểm bảng §2.

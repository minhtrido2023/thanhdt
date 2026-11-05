# SCL — DD redo VÒNG 2 · giá 04/11/2026 (CUM-quyền) · job `Taylor_20261105_020018`

> Tài liệu chỉ để nghiên cứu, trung dung. Làm theo `STANDARD_r2.md`.
> - Số liệu: `calc/model_scl_r2_out.txt|json`, chạy bằng `$DNA_PYEXE -I calc/model_scl_r2.py`.
> - Khoá: `calc/LOCK_r2_md5.txt` (có `scl_r3_core.py`). Tính tất định: `_common_g2r2/selfcheck_r2.sh`.
> - Lõi định giá vẫn là r3 03/11, tái lập byte ở vòng 1. Vòng 1 giữ nguyên ở `REPORT.md` và `SUMMARY_r1.json`.

## 0. Kết luận

| CUM 38,84 triệu cp, sau CK 4,50% @5 tỷ | |
|---|---|
| **Tâm** (kỳ vọng lưới) | **22.769** |
| P50 kết cục | 23.312 |
| Giá trị tại tham số trung tâm | 22.360 |
| **P10 / P90 kết cục** | **17.348 / 27.119** (min 15.270, max 30.509; n = 324) |

- Giá cum **30.000**: +31,8% so tâm, +10,6% so P90. **98,4% trọng số kết cục nằm dưới giá** ⇒ **TRÊN vùng (>P90)**.
- Nhãn giữ nguyên so vòng 1. Nhãn không đổi vì đổi định nghĩa vùng: vòng 1 đã dùng P10–P90, và r3 (P25–P75) cũng cho TRÊN.
- Cơ sở sau quyền (44,84 triệu cp): tâm 21.319, P10–P90 16.624–25.087. TERP 27.659 cao hơn tâm +29,7% ⇒ TRÊN vùng.
- P10 do riêng nhánh CYCLICAL quyết định. P90 do nhánh STRUCTURAL (82% trọng số quanh P90; nhánh này chỉ có w 0,2).
- So vòng 1 (tâm 22.855): −0,4%.

## 1. Đổi so vòng 1 — rà theo 12 điều

| Điều | Vòng 1 | Vòng 2 |
|---|---|---|
| 1 | `ddg2.wpct` bậc thang | `_shared/wpct.py`; báo n, % dưới giá, min |
| 2 | phải thu tập trung chỉ ở WARNING; IRR Phả Lại bị loại cả hai chiều, không có bản song song | phải thu thành trục lưới; song song: IRR Phả Lại, nhánh đối xứng TROUGH, khung nợ mệnh giá |
| 5 | WARNING thiếu nguồn/ngày tra | bổ sung (§6) |
| 6 | chỉ ADV120 | ADV250/60 + sleeve (§5) |
| 9, 10 | không có | LOCK; Gordon (§7) |

## 5. Thanh khoản

| Cỡ | ADV trung vị | Q/ADV | Phiên @10% | CK |
|---|---|---|---|---|
| **5 tỷ** | 120 phiên: 2,28 tỷ | 219% | 21,9 | **4,50%** |
| 5 tỷ | 250 phiên: 1,26 tỷ | 396% | 39,6 | 5,88% |
| 5 tỷ | 60 phiên: 3,63 tỷ | 138% | 13,8 | 3,67% |
| **Sleeve 10 / 20 / 40 tr** | 120 phiên | 0,4–1,8% | 0,2 | **0,67% / 0,74% / 0,85%** |

- ⚠️ Cỡ 5 tỷ nằm ngoài vùng hiệu chỉnh của luật căn bậc hai, nên con số 4,50% là ngoại suy.
- Ở cỡ sleeve, tâm ≈ 23.640 (= tâm trước CK 23.842 × (1 − 0,85%)). Giá vẫn cao hơn P90 trước CK (28.397).

## 6. Pháp lý / quản trị — ⚠️ WARNING

Các cờ mang theo từ `dd_SCL_20261029/SKEPTIC_R2_20261103.md` và REPORT vòng 1:

1. **Pha loãng:** 17,3 triệu cp (2023) → 44,84 triệu sau quyền (100:15,4453 @12.500; ĐKCC 10/11/2026), cộng ESOP 0,92 triệu cp @10.000.
   - Báo chí ([doanhnhan.baophapluat.vn](https://doanhnhan.baophapluat.vn/song-da-cao-cuong-scl-chao-ban-6-trieu-co-phieu-du-thu-75-ty-dong-de-tai-co-cau-nguon-von.html), [cafef](https://cafef.vn/song-da-cao-cuong-chao-ban-6-trieu-co-phieu-188261027151900881.chn)) nêu đăng ký mua 17/11–08/12/2026.
   - Hai lịch chuyển nhượng quyền trong báo chí lệch nhau → cần đối chiếu CBTT.
2. **Vay 26 tỷ từ cổ đông lớn**, lãi 10% (bên liên quan).
3. **Phải thu tập trung:** một tập đoàn BĐS chiếm 58,5% phải thu KH. Nay đã thành trục lỗ 0/20/50% (xác suất 0,75/0,20/0,05 [UL]).
4. **Dòng tiền và đòn bẩy:** CFO 9T 9,9 so với LNST 94,4; nợ ròng 321 tỷ. Biên ròng TTM là đỉnh 7 năm.
5. **Chưa thấy tin xử phạt/khởi tố SCL** (WebSearch 05/11/2026). Kết quả xử phạt tìm được đều thuộc công ty khác họ Sông Đà. WebSearch không thay được CBTT sàn.
   - Nghị quyết phát hành quyền đã nằm trong mô hình (cơ sở sau quyền + 75 tỷ trả nợ).

## 7. Định giá

**Khung r3:** LN chuẩn hoá chu kỳ × P/E nội tại (1 − g/ROE)/(r − g) + dự án dở dang theo giá vốn − nợ tài trợ (ròng 0) + lãi vay của nợ dự án cộng lại (lãi P&L thực 4,96%). r = 13,5%.

**Các trục:**

| Trục | Giá trị (xác suất) | Ghi chú |
|---|---|---|
| Chế độ ngành | CYCLICAL 0,5 · ADMIN_GATED 0,3 · STRUCTURAL 0,2 | trọng số lấy từ sector read của Bobby; mức quay về TB 1,0/0,5/0,0 là thiết kế [UL] |
| DT | TTM / 2026E (đều) | |
| Biên chuẩn hoá | TB 2020–TTM / TB 2023–TTM / lệch biên gộp (đều) | TB 2020–TTM là cận dưới |
| g | 3 / 4 / 5% (đều) | hai chiều |
| ROE | 15 / 20% (đều) | hai chiều |
| Lỗ phải thu tập trung | 0% (0,75) · 20% (0,20) · 50% (0,05) | 0% = sổ sách là cận trên (không thu quá gốc) |

**Loại khỏi lưới, có bản song song:**

| Biến thể | Tâm | P10 | P90 | % dưới giá |
|---|---|---|---|---|
| Chính | 22.769 | 17.348 | 27.119 | 98,4% |
| + IRR Phả Lại 10 / 13,5 / 17% (0,25/0,5/0,25) | 22.769 | 17.348 | 27.672 | 98,2% |
| Nhánh đối xứng (+TROUGH 0,2) | 21.648 | 15.987 | 26.942 | — |
| Khung toàn bộ nợ theo mệnh giá (r3) | 21.584 | 16.232 | 25.983 | — |

- IRR Phả Lại loại cả hai chiều theo luật 03/11: chưa có giá/sản lượng/hợp đồng, cũng chưa có số công suất vùng. IRR đối xứng nên tâm không đổi, chỉ đuôi trên rộng ra.
- TROUGH là gương của STRUCTURAL: biên về TB rồi vượt xuống 50% khoảng cách. Sector read không có lớp này nên chỉ đưa vào bản song song.

**`base_adjustments`:**
- Dự án Phả Lại + Vĩnh Tân GĐ2 (205,5 tỷ): giá vốn trừ nợ tài trợ = 0. Nguồn: BCTC Q3 XDCB, LCTT.
- Cộng lại lãi vay của nợ dự án: **+1.698 đ/cp cum** (kỳ vọng lưới r3). Cơ sở là lãi P&L thực 4,96% (SKEPTIC_R2).

**Gordon (g 4%, cum, trước CK):** ROE TTM 22,1% ⇒ **26.143**, vẫn dưới giá.
- Chỉ có một biến thể vì không có lãi tiền gửi đáng kể (tiền 95,1 tỷ so với nợ 416,5 tỷ).
- ROE TTM nằm ở đỉnh chu kỳ, nên đây là cận trên tham chiếu.

**Độ nhạy r (tâm cum sau CK):**

| Thay đổi lãi | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1 | 25.489 (+11,9%) | 24.052 | 22.769 | 21.616 | 20.575 (−9,6%) |

Kể cả ở −100bp, giá vẫn cao hơn tâm 18%.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON

| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Quyền mua 17/11–08/12/2026 | phát hành đủ, nợ ròng −75 tỷ | không phát hành hết |
| BCTC Q4/2026 (~20/01/2027) | LNST ≥ 38 tỷ, CFO ≥ LNST, phải thu giảm | biên gộp < 36%, phải thu tăng tiếp |
| Phả Lại vận hành (2027) | có HĐ/sản lượng/giá ⇒ IRR (≥15%) đưa vào lưới | trễ, vượt dự toán |
| Kiểm toán 2026 | chấp nhận toàn phần | ngoại trừ |

- **Ngưỡng nhãn:** về TRONG vùng khi giá cum ≤ 27.119.
- **HARD ABANDON** (dừng hồ sơ, làm lại) khi có một trong các sự kiện:
  - ngoại trừ kiểm toán về phải thu;
  - lỗ phải thu tập đoàn BĐS > 50%;
  - quyền mua bị huỷ hoặc thay đổi điều khoản.
- **Không đủ điều kiện sleeve fear-buy §2.5:** giá TRÊN vùng, không phải trạng thái sợ hãi.

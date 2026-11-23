# HHS — DD rev6 (23/11/2026, job Taylor_20261123_100926)

rev6 xử lý verdict DD_GENERAL r3 của rev5 (`skeptic/r3_raw.md`, INCONCLUSIVE medium). Phần pha loãng (quyền 5:3 @10.000 + cổ tức CP 7%) **giữ nguyên rev5** (`REPORT_rev5.md` §1–§3, §6–§7; skeptic r3 đã tính lại khớp tới đồng). rev6 làm thêm ba việc: (1) chạy lại lưới r3 và ghim kết quả; (2) tách khối HTK NC-II thành phần thấp tầng và phần cao tầng HH1–HH4, rồi định lượng phần cao tầng; (3) tìm số dư quỹ khen thưởng phúc lợi (KTPL) trên CĐKT.

- **Giả định khoá:** `rev6/calc/assumptions.json`, md5 `c7e6c927e84c010d71d0c28449410b0a`. Lint `bin/dd_assumptions_lint.py` cho 0 vi phạm. Calc ở `rev6/calc/calc_rev6.py` (md5 `64187d776a6cb7416bead2fdfee1ce9e`). Chạy 2 lần, `run1.txt` = `run2.txt` = `4e593e33…`. Output: `rev6/calc/calc_rev6_out.json`.
- **LOCK:** `rev6/calc/LOCK_md5.txt`, ghi lúc 17:14 ICT 23/11/2026. rev6 **không truy vấn giá mới**. Giá so sánh 9.700 (BQ 20/11/2026) kế thừa pha sau khoá của rev5 (`rev5/calc/post_lock_out.json`).
- **Nguồn lưới:** `dd_redo_20261105/HHS/calc_r3/hhs_r3.py` (md5 `cf5420d8…`). calc_rev6 nạp phần lõi của script này (từ đầu file tới dòng `# ---- CONTROL`), chạy `make(HEAD)` trên 405 ô và assert tâm. Chiết khấu thanh khoản `d5` = 1,4097% lấy từ `../calc/dilution_out.json` (md5 `0450ba0a…`).

## 0. Kết luận

**Tâm sổ (CUM, cp hiện tại) giữ 13.969, vùng 12.422–15.564, không đổi so với rev5. Nhãn DƯỚI vùng không đổi** ở giá 9.700. Cơ sở EX (phát hành đủ 100%, k = 1): tâm **11.615**.

| Cơ sở | Tâm | P10 | P50 | P90 | Giá so sánh | Nhãn | Luật 4 (giá ≤ 0,85 × tâm) |
|---|---|---|---|---|---|---|---|
| **CUM — headline (CK holding 0%, base theo V4)** | **13.969** | **12.422** | 13.917 | **15.564** | 9.700 (BQ 20/11/2026) | **DƯỚI vùng** | ĐẠT (ngưỡng 11.874) |
| CUM — song song CK holding 27% [UL, độ nhạy] | 10.761 | 8.624 | 10.559 | 13.207 | 9.700 | TRONG vùng | KHÔNG (9.147) |
| CUM — kịch bản tách HH1–HH4, trọng số xác suất (ước lượng, KHÔNG vào base) | 13.784 | — | — | — | 9.700 | DƯỚI vùng | ĐẠT |
| CUM — stress HH chiếm 30% giá gốc, lỗ 20% | 12.708 | 11.460 | — | 14.011 | 9.700 | DƯỚI vùng | ĐẠT (10.802) |
| EX đủ 100%, k = 1 | 11.615 | 10.711 | 11.584 | 12.546 | TERP sau cổ tức 9.171 | DƯỚI vùng | ĐẠT (9.873) |
| EX song song CK holding 27%, k = 0,73 | 8.808 | 7.560 | 8.690 | 10.237 | 9.171 | TRONG vùng | KHÔNG (7.487) |

- **Hạng mục quyết định của skeptic r3 (biên cao tầng HH1–HH4) đã được định lượng.** Lý do không đổi base:
  - BCTC không công bố cơ cấu HTK thấp tầng / cao tầng.
  - Nguồn độc lập duy nhất có định giá phủ cả HH1–HH4 là **PPA đã kiểm toán** (AASC, BCTC 2025 ý kiến chấp nhận toàn phần). PPA này cao hơn mô hình: thặng dư mô hình chỉ bằng **74,2%** thặng dư PPA còn lại sau thuế (§2.1).
  - Luật V4 yêu cầu mọi điều chỉnh giảm phải có cơ sở độc lập. Vì vậy phần cao tầng đi vào kịch bản có xác suất: **−1,3%** (ước lượng), không vào base.
  - Mức −10…−18% của skeptic đến từ việc hạ s cho **toàn khối**, kể cả phần thấp tầng. Biên thấp tầng (52%) là biên đã quan sát được, nên không có cơ sở để hạ phần này (§2.2).
- **Quy ước CK holding 0% / 27%:** giữ hai bản song song như rev5. **User chưa chốt.** rev6 không tự chọn và không gộp hai bản.
- **Quyết định không đổi:** HHS nằm trong `forensic_flags` EXCLUDE ⇒ không vào candidate plan, bất kể nhãn nào. Sizing V8 (2–4% NAV/mã) **không áp** khi còn EXCLUDE. Nếu user gỡ EXCLUDE, đề xuất trần 2% NAV (giữ như rev5 §0).
- ⚠ WARNING giữ nguyên rev5 §6:
  - Tăng vốn 60%.
  - NQ 10/NQ-HĐQT ngày 20/11/2026: lấy ý kiến cổ đông bằng văn bản 14–25/12/2026, **nội dung chưa công bố**.
  - Chuyển nhượng hợp đồng tiền gửi 852,0 tỷ giữa TCH và CRV/NĐL.

## 1. Đính chính so với rev5 — từng hạng mục skeptic r3

| # | Hạng mục skeptic r3 | Chiều | Xử lý rev6 | Loại | Ảnh hưởng tâm |
|---|---|---|---|---|---|
| 1 | **Killer:** khối NC-II 6.009,8 tỷ được định giá bằng s_obs = 0,70 (biên gộp thấp tầng 52,05%) cho cả khối, gồm 2.494 căn cao tầng HH1–HH4. Skeptic chạy lại: s −0,30 ⇒ 12.750 trước CK (−10%); s −0,54 ⇒ 11.663 (−17,7%) | quá cao | **Tái lập đúng số của skeptic:** 12.750 / 11.663 trước CK, tức 12.571 / 11.499 sau CK. **Tách khối:** phần HH1–HH4 chiếm tỷ trọng w trên giá gốc và nhận thặng dư riêng s_hh; phần còn lại giữ s r3. Thang thử w ∈ {3, 5, 10, 15, 30, 100%}, s_hh ∈ {−0,20; 0; 0,16} (§2.2). **Đối chiếu độc lập:** PPA kiểm toán phủ cả HH1–HH4 cao hơn mô hình (§2.1) ⇒ không có cơ sở giảm trong base. Kịch bản có xác suất (ước lượng): **13.784 (−1,3%)**. Stress w = 30%, lỗ 20%: **12.708 (−9,0%)** | (b) kịch bản | 0 (base); −1,3% kỳ vọng kịch bản |
| 2 | §8.5 và #9 của rev5 nói "lưới r3 không chạy lại được" là **sai** | — | **Đã sửa.** calc_rev6 chạy lại lõi `hhs_r3.py` và assert tâm trước CK **14.169**, sau CK **13.969**, P10 12.422, P50 13.917, P90 15.564 (n = 405). Hai file r3 bị mất chỉ ghi metadata. Bỏ cảnh báo "ba bản ghi của cùng một lần chạy" | (a) | 0 |
| 3 | #11 của rev5 nhắm sai biến: trong mô hình s tính trên tổng giá gốc, chi phí hoàn thiện cũng sinh biên | — | **Đã đổi trục.** Độ nhạy chính chuyển sang biên phần cao tầng (hạng mục #1). Các mức −351 / −702 / −1.403 đ/cp của rev5 chỉ còn để tham khảo cho trường hợp chi phí hoàn thiện không sinh biên, không còn là trục chính | (a) sửa cơ học | 0 |
| 4 | Quỹ KTPL ghi "đã tìm" nhưng thực chất "kế thừa r3" | — | **Đã tìm.** CĐKT HN Q3/2026, mã 323 "Quỹ khen thưởng phúc lợi" = **6.458.303.282 đ** (01/01 bằng đúng số này ⇒ 9T/2026 không trích). Nguồn: `rev6/png/hn_p07.png`, tr.6. Khoản này đã là nợ phải trả, nên đã nằm sẵn trong VCSH mẹ 9.152,94 tỷ của lưới ⇒ không trừ thêm (trừ thêm là trừ hai lần). Nếu coi toàn bộ là khoản giảm trừ thêm thì mức trần là 6,46 tỷ / 431,99 tr cp ≈ 15 đ/cp (0,1%) | (a) | 0 |
| 5 | Phiên lấy ý kiến cổ đông 14–25/12/2026 | — | **Không kiểm chứng được** tại 23/11: nội dung chưa công bố (rev5 §1). Mốc làm lại: khi có tài liệu phiếu lấy ý kiến | (c) | 0; nếu sửa phương án chào bán ⇒ làm lại bản pha loãng |
| 6 | Chiều rẻ: base k = 1 bảo thủ; nhóm tự tài trợ được gần đủ; CK thanh khoản | quá thấp | Giữ k = 1 theo V4 (BV NĐL chưa kiểm toán). Skeptic ước tác động ≤ +1%. Không đổi base | (b) | 0 |

### 1.1 Hạng mục còn lại của rev5 (§8) — trạng thái
CK holding chờ user · nội dung phiếu lấy ý kiến 12/2026 · hạn phân phối (chưa có GCN) · BV NĐL chưa kiểm toán: **không đổi**. "Lưới r3 không chạy lại được": **đóng** (#2). Quỹ KTPL: **đóng** (#4). Chi phí hoàn thiện G10: chuyển thành trục biên HH (#1, #3).

## 2. Định lượng biên cao tầng HH1–HH4

### 2.1 Đối chiếu với PPA đã kiểm toán — cơ sở độc lập duy nhất phủ HH1–HH4
- **Phạm vi PPA.** KT25 HN (EN tr.38 = PDF p.91, `dd_HHS_20261101/img/kt25s_p91.png`) ghi tài sản đảm bảo VietinBank là "Land use rights over 04 land lots HH1, HH2, HH3 and HH4 with a total area of 18,494.00 m²" thuộc dự án Hoang Huy New City – II. Vậy các lô HH nằm trong HTK dở dang NC-II, tức phần đã được định giá lại theo GTHL khi mua CRV (PPA: HTK GTHL 14.857,07 tỷ; `GAPS_FILL.md` G8).
- **Thặng dư PPA còn lại.** Thuế hoãn lại phải trả từ PPA còn **2.020,76 tỷ** tại 30/09/2026 (TM35). Suy ra thặng dư sau thuế còn lại = 2.020,76 / 0,2 × 0,8 = **8.083,0 tỷ**.
- **So với mô hình.** Thặng dư mô hình ở tham số trung tâm, chưa chiết khấu, gồm: HTK cũ 6.009,8 × 0,7016 + backlog 3.099,2 / 1,08 × 0,335 + BĐSĐT 817,0 = **5.994,6 tỷ**. Mức này bằng **74,2%** thặng dư PPA. Ngoài ra mô hình còn chiết khấu thời gian pv(y), y = 2,5–4 năm.
- **So với giá trị sổ.** Giá trị sổ mẹ / cp (theo PPA) = 9.152,94 / 431,99 = **21.188 đ**. Tâm 13.969 thấp hơn mức này **34,1%**.
- **Diễn giải.** GTHL HTK dở dang trong PPA được tính sau khi đã trừ chi phí hoàn thành, chi phí bán và lợi nhuận hợp lý của người hoàn thành. Vì vậy PPA đã chứa sẵn biên phần cao tầng theo giả định của bên định giá. Để mô hình bị định giá cao vì phần cao tầng, PPA phải đang định giá cao hơn khoảng 26% trở lên.
- **Giới hạn của nguồn này.** PPA dựa trên kỳ vọng giá năm 2025. Báo cáo định giá PPA không công bố, không có phân bổ theo dự án (G8). Kiểm toán chấp nhận PPA, nhưng đó không phải một lần định giá lại ở hiện tại. Đây là **cơ sở chống lại việc giảm trong base**, không phải bằng chứng để nâng base. Mô hình không dùng PPA để tăng tâm.

### 2.2 Tách khối: phần HH nhận thặng dư riêng (đầu ra `hh_split`)
Công thức: Δ = −HHS × 6.009,8 × w × (s_kịch bản − s_hh) × pv(y) / 431,99 tr cp. Áp trên toàn bộ 405 ô, sau CK thanh khoản 1,41%.

| w (tỷ trọng giá gốc HH, ước lượng) | s_hh = 0,16 (biên gộp 25%, mức của skeptic) | s_hh = 0 (NPV0 theo sổ) | s_hh = −0,20 (lỗ 20%, stress) |
|---|---|---|---|
| 3% | 13.894 (−0,5%) | 13.871 (−0,7%) | 13.843 (−0,9%) |
| 5% | 13.843 (−0,9%) | 13.806 (−1,2%) | 13.759 (−1,5%) |
| 10% | 13.717 (−1,8%) | 13.642 (−2,3%) | 13.549 (−3,0%) |
| 15% | 13.591 (−2,7%) | 13.479 (−3,5%) | 13.339 (−4,5%) |
| 30% | 13.212 (−5,4%) | 12.988 (−7,0%) | 12.708 (−9,0%) |
| 100% (= cách của skeptic: cả khối) | 11.444 (−18,1%) | 10.698 (−23,4%) | 9.766 (−30,1%) |

- **Neo cho w** (ước lượng, không có số công bố):
  - Diện tích đất các lô HH là 18.494 m² (KT25, đã kiểm toán). Khu NC-II rộng 49,36 ha (nguồn thứ cấp nhadautu.vn; tài liệu khác ghi ~50 ha). Tỷ lệ đất = **3,75%**.
  - HH1–HH4 mới ở giai đoạn làm hầm (SHS 08/2026, thứ cấp), nên giá gốc chủ yếu là tiền đất cộng phần hầm.
  - CPSXDD NC-II tăng từ 14.675,46 lên 15.010,99 tỷ trong 9T/2026 (TM09), trong khi vẫn bàn giao thấp tầng ⇒ chi xây dựng thuần trong kỳ có giới hạn.
  - Từ các điểm trên, w ≈ 3–15% hợp lý hơn nhiều so với w = 100%.
- **Vì sao s_hh = 0,16 tính trên giá gốc còn bảo thủ.** Với dự án cao tầng mà giá gốc hiện chủ yếu là đất, lợi nhuận sau thuế = 0,8 × (biên gộp − 10%) × doanh thu, chia cho một giá gốc nhỏ. Vì vậy thặng dư tính trên giá gốc thường **lớn hơn** 0,16, kể cả khi biên gộp cao tầng chỉ 25%. Chi phí xây dựng chưa chi được giữ NPV0 (V4). Chiều xuống thật chỉ xuất hiện khi biên gộp toàn dự án < ~10%, tức chi phí bán vượt biên. Đó là lý do có cột s_hh = −0,20.
- **Kịch bản có xác suất** (ước lượng, `assumptions.json` hh_split.scenario_probs; KHÔNG vào base):
  - 0,30 × (w 5%, s_hh 0)
  - 0,15 × (w 15%, s_hh 0)
  - 0,05 × (w 30%, s_hh −0,20)
  - 0,50 × base (phần HH đạt thặng dư ≥ s_obs, nhất quán với PPA)
  - Kết quả: **13.784 (−1,3%)**. EX đủ 100%, k = 1: ~11.520 ở (w 5%, s_hh 0), so với 11.615 base.
- **Không đổi nhãn** ở mọi ô có w ≤ 30%: P10 thấp nhất là 11.460 > 9.700. Nhãn chỉ đổi khi w = 100% và s_hh ≤ 0 (P10 9.028–9.874). Kịch bản này trái với biên thấp tầng đã quan sát và với PPA, nên không có cơ sở.

## 3. Cơ chế pha loãng (giữ rev5 §3)
V_final = (V_pre × 431,99 tr + (1 − CK_tk) × [k × 2.591,9 − (1 − c) × 2.591,9] tỷ) / (431,99 tr + c × 259,19 tr) / 1,07. Bảng EX đầy đủ xem rev5 §3. rev6 không đổi V_pre nên các dòng rev5 giữ nguyên tới đồng.

## 4. Luật định giá
- **V1 (r):** r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,50%**. Nguồn: `effective_deposit_rate('2026-11-23')` = 7,40%, cctg_12m 02/11; neo 03/11 = 7,40%.
  - Dải Ke nội địa 12,3–13,4% báo kèm.
  - Độ nhạy: NAV quỹ đất, r chỉ vào chiết khấu thời gian thực hiện. r3 đo trục r ±1pp cho tâm 13.972 (+3 đ/cp) ⇒ ±50/±100bp ≈ 0 đ/cp (< 0,1%). β 0,5/1,0: Δ lãi = 0.
- **V3 (thanh khoản):** trước CK 14.169, sau CK 5 tỷ (1,41%) 13.969. Nhãn tính theo giá trị sau CK.
  - ADV (rev5 sau khoá): trung vị 60 phiên 10,35 tỷ ⇒ 5 tỷ = 48% ADV60, nằm **trên** vùng hiệu chỉnh ⇒ CK có thể thấp.
  - Sleeve 40 tr: CK 0,126%.
  - Vị thế 5 tỷ (nếu có) phải chia tranche ≤ 2,1 tỷ/đợt.
- **V4:** I.14 = dự án tăng trưởng ⇒ NPV0. Không có capex tuân thủ mới. Phần cao tầng HH1–HH4 được giữ ở thặng dư s_obs trong base, vì giảm trừ cần cơ sở độc lập (§2). Kịch bản −1,3% chỉ hiển thị.
- **V5 (5F):** đầy đủ ngày 07–09/11/2026 (`dd_redo_20261105/HHS/ADDENDUM_5F.md`), chưa quá 12 tháng ⇒ tái dùng.
  - Moat NONE / LOCATION (asset-play quỹ đất CRV, Hải Phòng).
  - Rủi ro số 1: thực hiện thặng dư quỹ đất và dòng tiền lên HHS qua 2 tầng holding.
  - Kiểm nhanh 23/11: tách HH1–HH4 không đổi moat. Rủi ro thực hiện phần cao tầng (bán chậm, biên thấp) đã có ở §2.2.
- **V6 (hai nền, chỉ hiển thị):** FCFE ≤ 0 (CFO 9T/2026 −2.110,2 tỷ) ⇒ chỉ có V_ngắn = 4.466 đ/cp (rev5 §4).
  - Chênh với tâm NAV: HHS là asset-play. Giá trị nằm ở thặng dư HTK chưa đi qua lợi nhuận.
  - V_ngắn không phải dự báo giá, không vào tâm/vùng.
- **V7:** không dùng snapshot vĩ mô. **V8:** chuẩn 2–4% NAV/mã; không áp vì EXCLUDE.

## 5. Mốc hai chiều (bổ sung rev5 §7)
- **Xuống:**
  - CRV/HHS công bố cơ cấu HTK hoặc tổng mức đầu tư HH1–HH4 cho thấy w > 30%, kèm biên gộp dự kiến < 10%.
  - Giá mở bán HH1–HH2 dưới giá vốn dự toán.
  - Phiếu lấy ý kiến 12/2026 sửa phương án chào bán.
- **Lên:**
  - Mở bán HH1–HH2 với tiền khách ứng trước xuất hiện trên NMTT.
  - Cổ tức tiền CRV chuyển về HHS (bằng chứng chống CK holding).
- **HARD ABANDON:** giữ như rev5 §7.

## 6. Còn mở (không kiểm chứng được tại 23/11/2026)
1. Quy ước CK holding 0% vs 27% — **chờ user** (quyết định nhãn CUM là DƯỚI hay TRONG).
2. Nội dung phiên lấy ý kiến cổ đông 14–25/12/2026.
3. Cơ cấu HTK NC-II thấp tầng / cao tầng và tổng mức đầu tư HH1–HH4: BCTC HN không công bố. Nguồn web 23/11 (thứ cấp) mâu thuẫn nhau về số căn (1.030 / 1.218 / 2.494) và số tầng (29 / 30 / 33), thậm chí về địa điểm (một số bài ghi HH1–HH4 ở Đồng Quốc Bình, Ngô Quyền) ⇒ không dùng. Ảnh hưởng: kịch bản §2.2, ước lượng −1,3%.
4. BV NĐL 11.210 chưa kiểm toán; hạn phân phối (chưa có GCN).

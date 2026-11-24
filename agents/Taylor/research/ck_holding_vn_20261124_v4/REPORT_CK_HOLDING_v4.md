# CK holding niêm yết VN — v4 (job Taylor_20261124_053704, 24/11/2026)

Chỉ đo tham số (đầu vào DD, hiển thị). KHÔNG dựng rev8 HHS, KHÔNG ghi sổ, KHÔNG wire. Không đọc giá HHS/TCH/CRV. Không email, không commit.
Nguồn mọi số: `run1.txt` = `run2.txt` = `run_dna.txt` (md5 `d1540070a122ee9ea7a5aee173a7233a`). python3 (pandas 2.3.3) và `$DNA_PYEXE` (pandas 3.0.2)
cho kết quả giống hệt: `calc_out_v4.json` `cd4d64db…`, `panel_v4.csv` `21ed5849…`. Khoá: `LOCK_md5.txt` (23 file).
PREREG: `PREREG_v4.md` md5 `f4fd5637…` (`PREREG_v4_md5.txt`), mtime **12:42:12 ICT**, trước lần chạy calc v4 đầu tiên (~12:47 ICT).

## 0. Kết luận

**Sửa OCH/OGC xong, đầu trên dải trung tâm từ +23,0% về +14,4%. Đúng như skeptic ước tính.** Vẫn không có dải nào vừa hẹp vừa trung thực.

| Đại lượng (đặc tả chính, N = 13) | v3 | **v4** | Đo cái gì |
|---|---|---|---|
| Trung vị holding | 1,49% | **1,49%** | trung tâm (điểm) |
| Khoảng trung tâm F5: LOO (chẵn/lẻ N) ∪ bỏ KSF ∪ bỏ KSF&CMX | — | **−4,7% … +5,6%** | trung tâm (khoảng, theo cách chọn mẫu) |
| Bootstrap khối trung vị p25…p75 / p5…p95 | — / −26,9…36,2 | **−10,9…9,8 / −49,4…36,2%** | bất định lấy mẫu của trung tâm |
| (d) đường tháng n ≥ 11: min … max | −11,9 … 23,0% | **−11,9 … 14,4%** | trung tâm trôi theo thời gian (03→11/2026) |
| Tháng gần nhất 20/11/2026 | 23,0% | **14,4%** | "hiện tại", xu hướng chưa đảo |
| **Hull (a)∪(d)** | −11,9 … 23,0 (34,9pp) | **−11,9 … 1,5 … +14,4% (26,3pp)** | trung tâm. **> 20pp ⇒ KHÔNG ĐẠT** |
| Hull theo đúng chữ §C2: (c3)∪(d) | (không áp) | **−88,5 … +30,0% (118,5pp)** | xem §3(iv): c3 là phân tán, không phải trung tâm |
| IQR liên-holding (N = 13) | −38,7 … 36,6% | **−50,0 … 36,6%** | phân tán "một holding bất kỳ" |
| (b) IQR sau loại cấu trúc R1+R2 (N = 7) | −18,6 … 45,9% | **−24,2 … 9,8 … 45,9%** | phân tán |

- **Vị trí của 0%:**
  - Hull (a)∪(d): phân vị **0,45**. v3 là 0,34.
  - Hull theo chữ (c3)∪(d): phân vị 0,75.
  - Khoảng trung tâm F5 (−4,7…5,6%): 0% nằm trong, hơi dưới giữa.
- **N, trung vị, mẫu không đổi so với v3.** OGC và LHC đổi số nhưng đều nằm dưới trung vị, nên trung vị 1,49% giữ nguyên.
  - Sửa chỉ đổi đầu trên của đường tháng (10/2026: 19,7 → 13,7%; 11/2026: 23,0 → 14,4%).
  - Và đuôi dưới phân tán (LHC −38,7 → −50,0%).

### Đề xuất dải tham chiếu cho HHS (phương án A — đề xuất, không phải quyết định)

| Mốc | Giá trị | Là cái gì | Nguồn số |
|---|---|---|---|
| **Base** | **0%** | ≈ trung tâm đo (1,5%). Nhãn **"đầu lạc quan"** vì thấp hơn bản bỏ KSF (5,6%) và thấp hơn hiện tại (14,4%) | `center.median_N`, `center.median_exKSF` |
| Độ nhạy 1 | **+6%** (5,6%) | đầu trên khoảng TRUNG TÂM (bỏ KSF = LOO max, chẵn/lẻ N) | `center.interval_high` |
| Độ nhạy 2 | **+14%** (14,4%) | HIỆN TẠI: trung vị cắt ngang 20/11/2026. Xu hướng 9 tháng chưa đảo (ρ lag-1 0,96, T_eff 0,19) | `hhs_marks.current_month` |
| Stress | **+37%** (36,6%) | PHÂN TÁN riêng một holding: q75 liên-holding N = 13 | `hhs_marks.dispersion_q75` |
| Đầu âm −12% | **bỏ**, trừ khi HHS có cấu trúc R1 (cổ đông lớn ≥ 85%) hoặc R2 (phần theo sổ âm) | −11,9% là trung vị tháng 03/2026, bị kéo bởi nhóm premium cấu trúc. R1/R2 trong N: APH, IPA, MVN, OGC, SNZ, VIC (+ KSF, LHC là premium không cấu trúc) | `hhs_marks.R1R2_parents` |

- **Số ủng hộ gợi ý của skeptic:** +6 / +14 / +37%, base 0% gắn nhãn lạc quan, bỏ −12%. Cả 4 mốc khớp số skeptic trong phạm vi làm tròn.
- **Cần nói thẳng ba điều:**
  1. Dải trung tâm trung thực vẫn rộng 26,3pp (> 20pp).
  2. Mốc +14% là một điểm trong xu hướng ≈ 1 quan sát độc lập. Nó không phải trung tâm dài hạn.
  3. Đầu dưới của "một holding" (q25 −50%, bootstrap p5 −49%) không rỗng.
     - Bỏ −12% chỉ đúng nếu HHS **không** có cấu trúc kiểu R1/R2/premium.
     - Tôi KHÔNG kiểm cấu trúc HHS: brief cấm đọc HHS. Người dựng rev8 phải kiểm trước khi bỏ đầu âm.
- **Độ tin: THẤP.** N = 13, 1 chế độ thị trường, cắt ngang PIT thật chỉ có 9 tháng.

## 1. Đính chính so với v3 (mỗi lỗi: tác động lên N / trung vị / đường tháng / hull)

**1. OCH/OGC — pha loãng do phát hành riêng lẻ (lỗi chính). Tổng quát hoá thành quy tắc F1.**
- **Quy tắc** (PREREG_v4 F1), áp cho mọi PP / Rights / PUBL trong `tav2_bq.corporate_action` (`inputs/cap_events_v4.csv`) của mọi con, chỉ khi ex ≤ D (PIT) và ex > stake_date:
  - s_eff = s × S_pre(1+r_b) / S_post, mặc định mẹ không tham gia.
  - Số CP con = S_post từ ngày ex (`CAP_FIX`).
  - VCSH += total_value cho tới khi CĐKT phản ánh (`paid_in`).
  - Có bản ghi cổ đông lớn KBS sau sự kiện của chính mẹ ⇒ dùng % đó từ ngày niêm yết đợt phát hành.
- **OCH:**
  - Kiểm khớp: S_pre 200 tr = 130 tr / 0,65 (khớp).
  - OGC 55,6% → **33,70%** từ 30/10/2026. VCSH OCH + 1.300 tỷ ở 30/10 và 20/11, vì CĐKT Q3 chưa có tiền.
  - KBS OCH sau sự kiện: Leadvisors 39,39% (130 tr CP, 07/10/2026), không có bản ghi OGC mới ⇒ khớp giả định toàn lô về bên ngoài.
  - CK OGC: 10/2026 **+43,0 → −14,3%**, 11/2026 **+49,2 → +2,6%**. Trung vị OGC −8,1 → **−10,9%**.
  - Skeptic ước −14…−5% và +3…+10%: khớp.
- **Kênh tác động chính là TIỀN THU, không phải tỷ lệ** (biến thể `variants`):
  - Pha loãng mà không cộng tiền: đầu trên vẫn 23,0%. Vì OCH giao dịch gần sổ, phần s × (MV − E) gần như không đổi khi s đổi.
  - Cộng tiền mà không pha loãng: OGC −26,9%.
  - Cả hai (chính): OGC −10,9%.
- **GIC (con VSC; quyền mua 1:1 + cổ tức CP 10% cùng ngày ex 02/03/2026):**
  - Số CP v3 nhảy 25,45 → 13,33 → NaN → 25,45 tr. v4 dùng **25,45 tr** liên tục từ 31/03 (`ISS_FIX` gộp DIV + quyền).
  - Tỷ lệ VSC: mặc định 34,6% cho 03–05/2026. Sau đó **66,34%** (KBS 30/06/2026: 16,88 tr CP, tức VSC đã mua đủ quyền) từ ngày niêm yết 22/06/2026.
  - VSC trung vị 55,3 → **55,1%**.
  - Bản chặt (KBS chỉ dùng từ update_date + 90): 60,4%.
- **LBM (con LHC; quyền 4:1 giá 25.000đ, ex 31/03/2026, 10 tr CP / 250 tỷ):**
  - Số CP 40 → 50 tr khớp sẵn trong dữ liệu. Cộng 250 tỷ VCSH tới khi CĐKT phản ánh.
  - KBS không có bản ghi LHC sau sự kiện. Báo Pháp Luật (bảng `inputs/participation_override.csv`) cho biết LHC bố trí 165 tỷ thực hiện quyền, tức mua đủ phần 64,9%.
  - Tỷ lệ: 51,9% (mặc định) cho 03–06/2026, 64,9% từ 20/07/2026.
  - LHC trung vị −38,7 → **−50,0%**. Không override: −58,2%. Coi như tham gia từ đầu: −45,2%.
  - Kênh: tiền thu 250 tỷ vào VCSH LBM, với LBM giao dịch trên sổ.
- **Tác động tổng:**
  - N 13 → 13. Trung vị 1,49 → 1,49%.
  - Đường tháng: 10/2026 19,7 → 13,65%; 11/2026 23,0 → 14,42%. Các tháng khác không đổi.
  - Hull (a)∪(d) 34,9 → **26,3pp**. 0% ở phân vị 0,34 → **0,45**.
  - q25 liên-holding −38,7 → −50,0% (LHC là phần tử q25).
- **Báo cáo v3 sai ở 2 chỗ:**
  - §2d lấy OGC Δln SOTP +0,97 làm bằng chứng. v4: OGC Δln giá mẹ −0,41 so với Δln SOTP **+0,32**. Vẫn là "mẹ giảm nhanh hơn rổ con", nhưng biên độ nhỏ hơn 3 lần.
  - Đếm lại: 8/11 holding (không tính VIC, KSF) có Δln giá mẹ < Δln SOTP. Số đếm không đổi.
  - Hạn chế 4 của v3 ("trên tập N không có ca nào") là SAI. Có 3 ca: OCH, GIC, LBM.
- **Mọi ca F1, gồm cả ngoài N** (`calc_out_v4.json` → `dilution`, `event_check`, `proceeds`):

  | Mẹ | Con | Ex | Loại | s trước → sau (mặc định) | KBS / bằng chứng sau sự kiện |
  |---|---|---|---|---|---|
  | OGC | OCH | 07/10/2026 | PP | 55,6 → 33,7% | Leadvisors 39,39%; không có OGC mới |
  | VSC | GIC | 02/03/2026 | Rights | 66,0 → 34,6% | VSC 66,34% (30/06/2026) ⇒ dùng từ 22/06 |
  | LHC | LBM | 31/03/2026 | Rights | 64,9 → 51,9% | báo chí: LHC mua đủ ⇒ 64,9% từ 20/07 |
  | HAX | PTM | 09/03/2026 | Rights | 51,6 → 46,9% | HAX 52,06% (22/05/2026) ⇒ dùng từ 16/07 |
  | IMP | AGP | 26/11/2025 | Rights | 31,6 → 27,4% | IMP 30,19% (31/12/2025) ⇒ dùng từ 31/03/2026 |
  | BCM | BWE | 23/07/2026 | Rights | 17,0 → 14,9% | — |
  | MBB | MBS | 02/04/2026 | Rights | 66,8 → 44,3% | KBS MBB 66,4% (30/06/2026) **không khớp tên tự động** ⇒ mặc định (ngoài N) |
  | PLX | PTH | 23/10/2026 | Rights | 51,0 → 34,0% | — |
  | PPH | NTT | 24/07/2026 | PP | 23,9 → 19,7% | PPH 23,89% (23/07, trước ex) |
  | VNE | VE4 | 06/02/2026 | PP | 54,7 → 18,6% | — (chuỗi CP đã neo sau phát hành, trạng thái `post`) |

  Ngoài N, nên không đổi kết quả. MBS là ví dụ quy tắc mặc định "không tham gia" sai khi KBS khớp tên trượt (hạn chế 2).

**2. GAS — dòng corporate_action trùng.**
- Khử trùng theo khoá (mã, ex, method, ratio, volume) trước khi cộng cùng ngày ex (`dedup`). Có 2 ca:
  - **GAS** Bonus 3% 28/08/2025: v3 cộng thành ×1,06 và sửa 16 tháng `ISS_FIX`. v4 dùng ×1,03, khớp số liệu, nên không còn sửa nào.
  - **NVL** EMPL 2,5% 09/10/2025: EMPL không vào công thức nên không có tác động.
- Cả hai ngoài N: N / trung vị / đường tháng / hull không đổi.
- Cặp VIC PP 21/08/2025 và 10/07/2026 (volume ± khác nhau) cùng GEG / HPA PP âm KHÔNG gộp. Chúng bị gắn "mơ hồ, không dùng" (`ambiguous`).

**3. Năm chỗ v3 làm khác PREREG v3:**
- (i) `TREASURY_FIX`: giữ nguyên, ghi là **mở rộng ngoài PREREG v3**.
  - Điều kiện siết: không áp nếu có sự kiện ISS ex ≥ cuối quý BQ, tính cả bằng.
  - Còn lại: MCH (01/2025), PAN (07–09/2026), SP2, SZL.
  - Tác động −0,07pp (số skeptic), không đổi trong v4.
- (ii) Cùng ngày ex: **giữ CỘNG tỷ lệ**, vì Bonus + DIV tính trên cùng gốc CP trước ex (BSR sổ thật ×1,615). Đây là khác chữ Π(1+r) của PREREG v3.
  - Bản Π(1+r): N 13, trung vị 1,49%, hull không đổi. Chỉ GEX đổi (36,6 → 34,4%), vì GEX có thưởng 20% + DIV 25% cùng 05/05/2026.
  - Lỗi GAS là do dòng trùng, không do cộng (mục 2).
- (iii) `ISS_FIX` **hai chiều đúng chữ** (|CP/kỳ vọng − 1| > 2%), trong cửa sổ tới sự kiện CP kế tiếp.
  - Bản một chiều (v3): N / trung vị / đường tháng / hull giống hệt.
  - Sửa hai chiều mới chỉ ở ngoài N: DXG, GLT, SHB, SHE.
- (iv) **§C2 đúng chữ:** (c) đầu tiên đạt N ≥ 8 là **c3 "kiểm soát"** (N = 10), thay cho (a).
  - Hull (c3)∪(d) = **−88,5 … +30,0% (118,5pp)**, 0% ở phân vị 0,75. Kết luận "không có dải hẹp trung thực" **không đổi, chỉ mạnh hơn**.
  - Nhưng chữ quy tắc thiết kế sai: dải (c) khai là IQR (PHÂN TÁN), nên đem thay (a) (bất định TRUNG TÂM) là trộn hai đại lượng.
  - Vì vậy tôi báo cả hai. Đề xuất HHS dùng hull (a)∪(d) và ghi rõ đó là lựa chọn của tôi, không phải chữ §C2.
- (v) LOO của (d) dùng n ≥ 11:
  - Đầu thấp: −16,6 … −9,7%.
  - Đầu cao: **11,4 … 19,1%**. v3 dùng n ≥ 10: 19,1 … 26,9.

**4. GLT / SZL** (ngoài N; chỉ ghi kết luận):
- **GLT:** 9,17% KHÔNG phải cổ phiếu quỹ.
  - 9,327 tr + thưởng 0,606 tr + cổ tức CP 2,378 tr = **12,311 tr**, trùng BQ OShares Q3/2026 (12.311.088).
  - AIS 13,44 tr lệch +1,13 tr, không giải thích được bằng sự kiện nào.
  - v4 dùng 12,311 tr qua `ISS_FIX` (nhãn đúng). Đã gỡ khỏi `TREASURY_FIX`: cuối quý BQ = ngày ex nên điều kiện siết chặn nó.
- **SZL:** 0,76 tr **là cổ phiếu quỹ, đã kiểm.**
  - VCI `paid_in` 291,15 tỷ = 29,115 tr CP phát hành; lưu hành 27,90 tr ⇒ quỹ 1,21 tr trước cổ tức.
  - Cổ tức CP 70% có KL 19,846 tr = 0,7 × 28,35 tr lưu hành (đã bán bớt 0,45 tr CP quỹ trước ngày chốt).
  - Sau sự kiện: phát hành 48,961 tr (= AIS), lưu hành 48,199 tr (= BQ Q3) ⇒ **quỹ 0,763 tr**. `TREASURY_FIX` đúng.

**5. Trình bày TRUNG TÂM là KHOẢNG** (`center`):
- Trung vị N = 13 là 1,49% (PAN). Bộ ba quanh trung vị: −10,9% (OGC) / **1,5%** (PAN) / 9,8% (MSN).
- ⇒ Chỉ cần N chẵn/lẻ đổi (bỏ hoặc thêm 1 holding) là trung vị nhảy trong **−4,7 … 5,6%** (LOO min…max).
- Bỏ KSF: **5,6%** (N = 12). Bỏ KSF & CMX: **1,5%** (N = 11).
- Bootstrap khối (holding × 3 tháng, B = 5.000): p25…p75 −10,9…9,8%; p5…p95 −49,4…36,2%.
- KSF giữ trong đặc tả chính, vì BANNED là luật đầu tư, không phải tiêu chí đo.

## 2. Khác PREREG_v4 (không im lặng)
1. **Thêm kiểm khớp tỷ lệ / khối lượng cho F1, SAU lần chạy thử 1.**
   - Lúc thêm, tôi chỉ xem log số CP / tiền thu, chưa xem CK.
   - Lý do: chữ F1 làm phồng số CP ở các mã có chuỗi số CP trước ex đã neo lùi bằng số SAU phát hành (VE4, INC, ORS, VTD, TAL, BID 2026, NVL 12/2025, PXL).
   - Quy tắc: gốc theo tỷ lệ = volume / ratio.
     - `pre` (S_pre ≈ gốc ±3%): áp như PREREG.
     - `post` (S_pre ≈ gốc(1+r_b) + vol): không `CAP_FIX`, S_post = S_pre, f = (S_pre − vol)/S_pre.
     - `ambig`: không áp, liệt kê. Gồm DXG 09/12/2025, MST, SCI, SGR, SJE, TDC, VPL 23/06/2026.
   - VPL (con VIC) là ca `ambig` duy nhất chạm N. Bản `F1_ambig_applied`: N / trung vị / đường tháng / hull không đổi.
   - Sự kiện không có số CP trước ex (IPO hoặc trước cửa sổ: GEL PUBL 07/01/2026, HPA, TCX, MBS 2024…) bỏ qua, liệt kê ở `event_check`. GEL không có số CP PIT nên không được dùng trong GEX ở cả v3 lẫn v4.
2. **Override tham gia quyền bằng nguồn ngoài KBS (`inputs/participation_override.csv`, chỉ có LBM), thêm SAU lần chạy thử 2, khi tôi ĐÃ thấy LHC −58%.**
   - Tác động chỉ ở LHC (−58,2 → −50,0%). LHC dưới trung vị, nên trung vị / hull / đường tháng không đổi.
   - q25 liên-holding thì đổi: −58,2 → −50,0%.
   - Bản không override được báo ở `variants`.
3. Cửa sổ `ISS_FIX` hai chiều kết thúc ở sự kiện CP kế tiếp **bất kỳ**. PREREG v3/v4 ghi "khác loại Bonus/DIV".
   - Lý do: sự kiện cùng loại sau đó tự sửa lại. Bản theo chữ chỉ để lại log ghi đè trung gian (GEX, GEE, HPG…). Giá trị cuối giống hệt, đã kiểm GEX / GEE.
   - Đổi sau lần chạy thử 3. Kết quả CK không đổi.
4. Khoá khử trùng thêm volume (đã khai trong PREREG_v4 F2, khác chữ dispatch).
5. Tiền thu áp cho mọi mã có sự kiện, cả mẹ (đã khai F1, khác chữ dispatch "VCSH con").
   - Mẹ trong N không có PP / quyền trong cửa sổ, trừ VIC: các dòng PP của VIC mơ hồ nên không dùng.
6. PUBL gộp vào F1 (đã khai). Không ca PUBL nào dùng được trong N.

## 3. Bảng theo holding (v4 chính: PIT, loại stale, độ phủ ≥ 60% ở ≥ 3 tháng)
| Holding | CK trung vị v4 | v3 | min…max tháng | Tháng | Ghi chú |
|---|---|---|---|---|---|
| CMX | 68,1% | 68,1 | 62,2…72,4 | 7 | con mỏng (CMM) |
| VSC | 55,1% | 55,3 | 15,0…62,9 | 6 | GIC F1 |
| IPA | 42,2% | 42,2 | 34,9…46,2 | 9 | R2 |
| GEX | 36,6% | 36,6 | 23,4…49,9 | 9 | |
| SNZ | 10,1% | 10,3 | 6,2…26,7 | 9 | R1; SDV tiền thu F1 |
| MSN | 9,8% | 9,8 | 0,6…14,1 | 9 | |
| PAN | 1,5% | 1,5 | −21,2…19,1 | 9 | ISS / TREASURY_FIX |
| OGC | −10,9% | −8,1 | −101,6…2,6 | 9 | R2; **OCH F1** |
| APH | −12,6% | −12,6 | −33,7…−3,5 | 9 | R2 |
| LHC | −50,0% | −38,7 | −63,3…−38,7 | 9 | **LBM F1** |
| KSF | −101,4% | −101,4 | −170,2…−85,1 | 5 | BANNED, con mỏng |
| VIC | −166,7% | −166,7 | −308,1…−4,6 | 21 | R2 |
| MVN | −167,7% | −167,7 | −201,4…−141,8 | 9 | R1 |

- Lưới (a), 12 đặc tả PIT: **−11,8 … 1,5 … 7,4%** (19,2pp). v3 là −10,3…7,4; đổi do LHC ở ô 70% / con mỏng về sổ.
- (d) theo tháng 03→11/2026: −11,9 / −9,8 / −8,7 / −2,6 / −0,9 / 0,5 / 7,9 / **13,7** / **14,4%**, n = 11–15.
- Độ nhạy khác (`sens`):

  | Biến thể | N | Trung vị |
  |---|---|---|
  | Con mỏng về sổ | 10 | −6,9% |
  | Con mỏng trọng 50% | 11 | 1,2% |
  | Tỷ lệ cố định (look-ahead) | 15 | −4,0% |
  | Bỏ VIC | 12 | 5,6% |
  | Bỏ VIC + MVN | 11 | 9,8% |

- T_eff 0,19 (ρ 0,958, 9 tháng).

## 4. Hạn chế còn lại
1. **1 chế độ, T_eff ≈ 0,2.** Đường tháng tăng gần đơn điệu. Mốc "hiện tại" 14,4% không phải trung tâm dài hạn.
2. **Tham gia quyền mua chủ yếu là MẶC ĐỊNH "không tham gia"**, chỉ đúng với PP cho bên ngoài.
   - Cả 2 ca quyền mua trong N có bằng chứng đều là mẹ tham gia đủ (GIC qua KBS, LBM qua báo chí).
   - Ngoài N, phần lớn ca chưa kiểm. MBS: KBS có MBB 66,4% nhưng khớp tên tự động trượt.
   - Trong khoảng ex → niêm yết, mặc định làm CK nghiêng âm (LHC 03–06/2026, VSC 03–05/2026).
3. Override LBM dựa vào một bài báo, không phải báo cáo kết quả chào bán gốc của HNX/UBCK. Thêm sau khi đã thấy số LHC (mục 2.2).
4. Kiểm khớp F1 thêm sau lần chạy thử 1. Các sự kiện `ambig` (VPL, TDC, SGR…) không được áp.
5. Tỷ lệ sở hữu vẫn từ ảnh chụp BCTC năm (KBS) + sự kiện. Tầng 2 chỉ khớp theo tên; MSN–MCH thiếu ngày.
6. KSF (BANNED) và CMX tựa hoàn toàn vào giá con mỏng.
7. R2 bắt rộng hơn ý định (holdco nợ ròng: IPA / APH / OGC); giữ đúng kết quả khai trước.
   - §C2 viết sai bản chất: thay (a) bằng IQR (c) là trộn phân tán vào trung tâm.
8. Survivorship: chỉ mã còn niêm yết.
9. CK là tổng hợp (quản trị, thuế hai lần, thanh khoản, cảm tính). Bootstrap không mô hình cú sốc chung.
10. Chưa kiểm HHS có cấu trúc R1/R2 hay không (brief cấm đọc HHS). Điều kiện bỏ đầu −12% phải kiểm trước khi dùng.
11. Chưa qua quant-skeptic vòng v4.

## 5. Tái lập
- Đầu vào: `cd WorkingClaude && source wc_env.sh && python3 .../fetch_inputs_v4.py capevents4 kbs4`. Các stage khác tái dùng `inputs/` + `raw/` copy từ v3.
- Tính: `python3 calc_ck_v4.py > run1.txt`, lần 2 vào `run2.txt`, `$DNA_PYEXE calc_ck_v4.py > run_dna.txt`. Tất định, không mạng, khoảng 3 phút.

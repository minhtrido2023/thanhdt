# CK holding niêm yết VN — v5 (job Taylor_20261124_073243, 24/11/2026)

Chỉ đo tham số (đầu vào DD, hiển thị). KHÔNG dựng rev8 HHS, KHÔNG ghi sổ, KHÔNG wire. Không đọc giá HHS/TCH/CRV. Không email, không commit.
Nguồn mọi số: `run1.txt` = `run2.txt` = `run_dna.txt` (md5 `b10c57012788e28e0dabe2c0a1ab2d0e`); python3 (pandas 2.3.3) và
`$DNA_PYEXE` (pandas 3.0.2) giống hệt; `calc_out_v5.json` md5 `d64019b7390a4f16633b59e5ed6275ff`. Khoá: `LOCK_md5.txt` (`md5sum -c` 26/26 OK).
PREREG: `PREREG_v5.md` md5 `82a03f9e4061537055924df0ad84cad8`, mtime **14:44:08 ICT**, trước lần chạy calc v5 đầu tiên (**14:45:31 ICT**, `run_start_first.txt`).
Lần chạy thử 1 (14:55) giữ ở `trial/`; sau đó thêm 1 dòng POSTHOC (xem "Khác PREREG" K1).

## 0. Kết luận

**Sửa MSN (thêm MSR + MML, cập nhật MCH/TCB) đẩy mốc hiện tại 20/11 từ 14,4% lên 19,7% — nằm trong khoảng skeptic ước (18–23%).**
Nhưng trung vị N giảm 1,5% → −3,2%, vì VSC rời N (sửa VGR 74% → 54,35% làm độ phủ < 60%). Hull (a)∪(d) rộng ra 26,3 → 36,5pp. **Vẫn KHÔNG có dải trung tâm < 20pp.**

| Đại lượng (đặc tả chính) | v4 (N=13) | **v5 (N=12)** | Đo cái gì |
|---|---|---|---|
| Trung vị holding | 1,49% | **−3,24%** | trung tâm (điểm) |
| Khoảng trung tâm F5 (LOO ∪ bỏ KSF ∪ bỏ KSF&CMX) | −4,7 … +5,6% | **−8,1 … +1,6%** | trung tâm (khoảng) |
| Bootstrap khối trung vị p25…p75 / p5…p95 | −10,9…9,8 / −49,4…36,2 | **−12,3…8,7 / −50,3…34,2%** | bất định lấy mẫu |
| (a) lưới đặc tả | — | **−10,3 … +10,3% (20,6pp)** | trung tâm qua đặc tả |
| (d) đường tháng n ≥ 11: min … max | −11,9 … 14,4% | **−16,8 … 19,7%** | trung tâm trôi theo thời gian |
| **Mốc hiện tại 20/11/2026** | 14,4% | **19,7%** | trung vị cắt ngang tháng cuối (n=11) |
| **Hull (a)∪(d)** | −11,9…1,5…14,4 (26,3pp) | **−16,8 … −3,2 … +19,7% (36,5pp)** | > 20pp ⇒ KHÔNG ĐẠT |
| Hull đúng chữ §C2 (c3)∪(d) | −88,5 … 30,0 (118,5pp) | **−88,5 … 30,0% (118,6pp)** | phân tán trộn trung tâm (xem v4 §3(iv)) |
| IQR liên-holding | −50,0 … 36,6% | **−62,8 … 37,7%** | phân tán một holding |
| (b) IQR sau loại R1+R2 | N=7: −24,2…45,9 | **N=5: −50,0 … 1,6 … 36,6%** | phân tán (N quá nhỏ) |
| MSN (ck trung vị tháng / tháng 20/11) | 9,8% / 9,8% | **40,8% / 45,7%** | một holding |

- **Vị trí của 0%:** hull (a)∪(d) phân vị **0,46** (v4 0,45); hull đúng chữ phân vị 0,75; khoảng F5 −8,1…+1,6%: 0% nằm trong, gần đầu trên.
- **Mốc hiện tại 19,7% là PAN** (trung vị của 11 holding tháng 11). Thứ tự 20/11: VIC −308, MVN −146, LHC −63, APH −32, OGC +10,3, **PAN +19,7**, SNZ +26,9, GEX +39,0, IPA +41,6, MSN +45,7, CMX +69,3%.
  MSN nhảy từ dưới lên trên trung vị ⇒ trung vị chuyển từ OGC (10,3) sang PAN (19,7). Mốc này **nhạy với một holding** (PAN: độ phủ 0,66, phần con mỏng 0,32).
- **Độ nhạy MSR không đổi mốc hiện tại**: s_MSR ∈ {0; 25; 43,7; 87,46; 94,9%} ⇒ MSN 20/11 = 33,6 / 37,6 / 40,3 / 45,7 / 46,5%; trung vị 20/11 = 19,7% ở cả 5 (MSN luôn trên trung vị). Trung vị N −3,24% ở cả 5.

### Đề xuất dải tham chiếu cho HHS (phương án A — đề xuất, không phải quyết định)

| Mốc | Giá trị | Là cái gì | Nguồn số |
|---|---|---|---|
| **Base** | **0%** | đầu trên khoảng trung tâm F5 là +1,6% ⇒ 0% ≈ trung tâm. Nhãn **"đầu lạc quan"** vì thấp hơn hiện tại 19,7% | `center.interval_high` = `hhs_marks.center_high` |
| Độ nhạy 1 | **+6%**? — **số v5 KHÔNG còn ủng hộ** | v4: đầu trên F5 = 5,6% (bỏ KSF). v5: bỏ KSF = 1,6%. Không có đại lượng trung tâm nào ở ≈6% | `center.median_exKSF` = 0,0157 |
| Độ nhạy 2 | **+20%** (19,7%) | HIỆN TẠI: trung vị cắt ngang 20/11/2026 (= PAN). Xu hướng 9 tháng chưa đảo (ρ lag-1 0,92, T_eff 0,39) | `hhs_marks.current_month` |
| Stress | **+38%** (37,7%) | PHÂN TÁN riêng một holding: q75 liên-holding N = 12 | `hhs_marks.dispersion_q75` |
| Đầu âm −17% | **bỏ**, trừ khi HHS có cấu trúc R1 (cổ đông lớn ≥ 85%) hoặc R2 (phần theo sổ âm) | −16,8% là trung vị tháng 03/2026. R1/R2 trong N: APH, IPA, MSN, MVN, OGC, SNZ, VIC | `hhs_marks.R1R2_parents` |

- **Nói thẳng:**
  1. Mốc +6% của v4 không còn chỗ dựa trong v5 — đề xuất bỏ, hoặc giữ chỉ như "giữa base và hiện tại" (không phải số đo).
  2. Mốc hiện tại 19,7% khớp ước lượng skeptic, nhưng là một holding (PAN) và ≈ 1 quan sát độc lập trong một xu hướng; không phải trung tâm dài hạn.
  3. Dải trung tâm trung thực rộng 36,5pp; hẹp nhất là lưới đặc tả (a) 20,6pp — vẫn trên ngưỡng 20pp.
  4. MSN giờ thuộc R2 (phần theo sổ âm −27.057 tỷ): con niêm yết (MV 213.616 tỷ ở 20/11) > VCSH mẹ.

## 1. Đính chính so với v4

1. **BLOCKING — MSN thiếu MSR/MML (đã sửa, S1).** Chuỗi (BCTN MSN 2024/2025 `raw/msn_ar/`, KBS `raw/kbs_sh/`):
   MSN → ZENITH 100% → Tầm nhìn Masan 100% → **MSR 87,46%** CP phổ thông (KBS 30/10/2026; BCTC hợp nhất ghi lợi ích kinh tế MHT 94,9% không đổi 2024→2025 ⇒ áp từ 31/12/2024);
   MSN → SHERPA 100% → Masan Agri / WinEco 100% → **MML 94,3% (2024) → 91,2% (2025)** (bảng công ty con BCTC hợp nhất);
   **MCH 67,4% → 66,2%**, **TCB 19,8 → 19,7%**; VSN bỏ (liên kết của MML ⇒ đã nằm trong MV MML). PIT: `valid_from` = ngày cuối kỳ + 90 ngày (BCTC năm).
   - MSN: ck 9,8% → **40,8%** (trung vị tháng); 20/11: 9,8% → 45,7%. Độ phủ 20/11: 0,94 (bản stake v4) → 1,15.
   - N: không đổi do mục này (S1_MSN_as_v4: N=12). Trung vị N: không đổi (−3,24%).
   - Đường tháng: 10/2026 11,4 → 16,3%; 11/2026 10,3 → 19,7% (so S1_MSN_as_v4); các tháng 03–09/2026 không đổi.
   - Hull: đầu trên 11,4 → 19,7%. Mốc hiện tại 10,3 → 19,7%.
   - Độ nhạy MSR (bắt buộc): xem §0. Biến thể "chặt" s_MSR=0 (KBS 30/10/2026 + 90 ngày nằm ngoài cửa sổ) vẫn cho MSN 33,6% (do MML + MCH/TCB).
2. **Quét hệ thống con niêm yết thiếu** (`sweep_v5.py` → `inputs/sweep_v5.csv`; quy tắc A = con chưa niêm yết khớp tên, B = cổ đông lớn trùng thương hiệu, C = tỷ lệ KBS ≠ stakes_all):

   | Holding | Con thiếu/lệch | Stake | Xử lý | Đổi số? |
   |---|---|---|---|---|
   | MSN | MSR / MML | 87,46 / 91,2% | thêm (mục 1) | **có** (lớn) |
   | MSN | NET (Masan HPC 52,25%, 2020) | lợi ích MSN 34,6% (BCTN 2025, mục công ty con 28) | NET là con của Masan HPC, HPC thuộc MCH (cùng 66,2%) ⇒ đã nằm trong MV MCH; thêm sẽ đếm hai lần ⇒ không thêm | không |
   | VSC | VGR 74% → **54,35%** | bán 20% 07/2025 (KBS 30/06/2026 + báo chí) | sửa, hiệu lực 28/10/2025 (ngày BCTC Q3/2025 VSC) | **có**: VSC rời N (độ phủ trung vị 0,50; 2 tháng ≥ 60%) |
   | PAN | FMC 50,12% → **37,75%** trực tiếp | 12,37% qua ABT đã nằm trong MV ABT | sửa | nhỏ: PAN 1,49 → 1,57%; trung vị tháng 20/11 19,1 → 19,7% |
   | APH/GEX/KSF/PAN | SJS, ABB, VEC, ODE, AST | 21,3 / 12,1 / 88,0 / 5,0 / 10,0% | chỉ khớp thương hiệu: cổ đông là pháp nhân KHÁC tên holding (An Phát TM-DV ≠ An Phát Holdings, Geleximco ≠ Gelex, Sunshine Sky Villa, quỹ STIC) — không thêm; **chưa kiểm sâu quan hệ sở hữu** (hạn chế 5) | không |
   | 15 ca ngoài N (AAA/NHH, AIG/GCF, BCG/BCR-BGE-TCD, CII/NBB, DXG/DXS, FPT/FOC, GVR/NTC-VRG, KDC/VDS, SAB/SBB, TCD/BCR, TVC/TVB, VNM/MCM) | lệch tỷ lệ | xem csv | không sửa | không (ngoài N; có thể đổi tập ứng viên — hạn chế 5) |

3. **Lãi pha loãng của mẹ khi không tham gia (S2).** Áp tới khi BCTC mẹ có cuối quý ≥ ex.
   - **OGC** (OCH PP 07/10/2026): 10/2026 −14,3 → −0,7%; **11/2026 2,6 → 10,3%** (khớp ước skeptic); ck trung vị tháng −10,95 → −8,06%.
   - **LHC** (LBM 31/03/2026): 03/2026 −58,2 → −50,6%; 04/2026 −60,0 → −52,5%; ck trung vị tháng không đổi (−49,95%).
   - **VSC** (GIC): lãi âm −38,2 tỷ ở 03/2026; VSC ngoài N ở v5 ⇒ không đổi kết quả.
   - Tác động N: trung vị −4,69 → −3,24% (OGC sát giữa). Đường tháng/hull/mốc hiện tại: không đổi.
4. **PROCEEDS_ADD bỏ khi BCTC con cũ > 4 quý (S3)**: SDV (BCTC 2020Q2, 125 tỷ), PTH (2015Q4, 17,5 tỷ). **SNZ** ck 10,10 → 10,30%; N/trung vị/đường tháng/hull/mốc: không đổi.
5. **Quy tắc ambiguous**: giữ quy tắc code (rộng) + khai — xem "Khác PREREG" K2. Bản đúng chữ PREREG_v4 (chỉ VIC) cho kết quả giống hệt.
6. **Hạn chế MSR/MML** khôi phục (hạn chế 1) và **bỏ dòng "4 mốc khớp số skeptic"** (vòng tròn) khỏi đề xuất.
7. **GIC**: v4 chuyển tỷ lệ VSC→GIC sang số KBS **66,34%** từ ngày niêm yết **22/06/2026**, sớm hơn ngày KBS **30/06/2026** (= thông tin tương lai 8 ngày). Bản chặt (KBS + 90 ngày, `F1_part_strict`): kết quả N giống hệt vì VSC đã ra khỏi N. Bản chặt VSC = 60,4% (số skeptic v4, đặc tả VGR 74%) — **chưa đo lại** dưới VGR 54,35%, vì VSC không còn trong N.

## 2. Khác PREREG

- **K1 — POSTHOC (sau lần chạy thử 1, 14:55).** Thêm 1 dòng override MSN→MCH 66,2% hiệu lực 28/07/2025 (thuyết minh BCTN MSN 2025: mua lại CP Consumer Holdings hoàn tất 06/2025, lợi ích MSN trong MCH 66,2%; hiệu lực = ngày công bố BCTC Q2/2025 MSN). Trước đó 04–07/2025 dùng KBS 51,28% (khớp tên trượt).
  Tác động (trial1 vs chính): MSN ck 32,5 → 40,8%, ctrl_share 0,25 → 0,78 (MSN thành "control"), q75 liên-holding 33,5 → 37,7%, bootstrap p95 29,9 → 34,2%.
  **Không đổi**: N, trung vị, đường tháng, hull, mốc hiện tại. Biến thể `POSTHOC_MCH_participation_off` báo kèm. Đây là thay đổi sau khi thấy số — người đọc nên coi q75 = 37,7% là bản có POSTHOC, 33,5% là bản đúng PREREG.
- **K2 — ambiguous (S4, đã khai trong PREREG_v5).** Code giữ quy tắc rộng: mọi dòng PP/Rights/PUBL âm ⇒ cả (mã, ex) mơ hồ ⇒ {GEG 16/12/2025, HPA 28/05/2025, VIC 21/08/2025, VIC 10/07/2026}. PREREG_v4 F1 chỉ bắt cặp âm/dương cùng method ⇒ {VIC ×2}. Tác động đo: 0 (GEG, HPA không vào N hay con của holding trong N).

## 3. Hạn chế còn lại

1. **MSR/MML**: stake MSR dùng 87,46% CP phổ thông từ KBS 30/10/2026, áp ngược từ 31/12/2024 vì BCTC hợp nhất ghi lợi ích kinh tế ổn định — không có chuỗi KBS PIT 2025. Không tính CP ưu đãi MSR (94,9% gồm ưu đãi chỉ là độ nhạy). Không look-through tiếp từ MML/MCH xuống con của chúng (đã nằm trong MV con).
2. **1 chế độ, T_eff ≈ 0,4.** Đường tháng tăng gần đơn điệu 03→11/2026. Mốc hiện tại không phải trung tâm dài hạn, và là một holding (PAN).
3. **N = 12, sát ngưỡng**: một sửa tỷ lệ (VGR) đã đổi N 13→12 và trung vị 1,5 → −3,2%. Trung vị nhạy với tập (LOO −8,1…+1,6%).
4. Tham gia quyền mua phần lớn là MẶC ĐỊNH "không tham gia" (v4 hạn chế 2 giữ nguyên); override LBM từ báo chí.
5. Quét hệ thống chỉ dựa KBS + tên; 15 ca lệch tỷ lệ ngoài N chưa sửa — có thể đổi tập ứng viên ở vòng khác. NET (Masan HPC) loại theo đọc BCTN, chưa kiểm KBS PIT.
6. KSF (BANNED) và CMX tựa vào giá con mỏng. R2 bắt rộng (holdco nợ ròng), nay gồm cả MSN.
7. Survivorship: chỉ mã còn niêm yết. CK là tổng hợp (quản trị, thuế hai lần, thanh khoản, cảm tính).
8. Chưa kiểm HHS có cấu trúc R1/R2 (brief cấm đọc HHS) — điều kiện bỏ đầu âm phải kiểm trước khi dùng.
9. Chưa qua quant-skeptic vòng v5 (chỉ rà phần thay đổi).

## 4. Tái lập
- Đầu vào: `inputs/` + `raw/` copy từ v4; thêm `python3 fetch_inputs_v5.py v5add` (MSR, MML), `python3 sweep_v5.py` → `inputs/sweep_v5.csv`, `inputs/stakes_override_v5.csv` (tay, có cột nguồn).
- Tính: `python3 calc_ck_v5.py > run1.txt`; lần 2 → `run2.txt`; `$DNA_PYEXE calc_ck_v5.py > run_dna.txt`. Tất định, không mạng.
- Kiểm: `md5sum -c LOCK_md5.txt`; `md5sum run*.txt` (cả 3 = `b10c5701…`).

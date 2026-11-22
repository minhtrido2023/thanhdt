# B4 — thử `dd_assumptions_lint.py` trên 5 ca DD cũ (22/11/2026, job Taylor_20261122_131400)

**Cách làm.** Dựng tay `assumptions.json` v1 cho bản VÒNG ĐẦU (bản bị phản biện bắt lỗi) của 5 ca, ánh xạ
từ khoá/mô hình/báo cáo CÓ SẴN. **Chỉ điền khoá có trong nguồn; khoá vắng = khoá gốc không có** (không
bịa để qua). Mỗi file ghi `_mapped_from`. Output thô: `trial/lint_output_raw.txt` (lệnh:
`python3 bin/dd_assumptions_lint.py trial/<f>.json`, chế độ cảnh báo, cả 5 rc=0; `--strict` cả 5 rc=1).

`method_version` vắng ở cả 5 (trường mới) — giá trị lẽ ra phải ghi theo `kb/config/dd_method_versions.json`:
QTP/VCB 17/11 → `M20261111`; PAT 14/11 → `M20261111`; VLB 22/11 → `M20261122`; MVC r4 03/11 → `M20261103A` hoặc
`M20261030` (r4 trước luật 17:06).

## Bảng tổng

| Ca (bản thử) | Nguồn ánh xạ | Số vi phạm | Lỗi phản biện/user từng bắt (sổ `kb/dd_price_zones.json`) | Lint bắt được? |
|---|---|---|---|---|
| **QTP v1** 17/11 | `dd_QTP_20261117/model/qtp_model_v1.py` + `REPORT_v1.md` | 13 | **Bỏ sót dự án xử lý khí thải ~3.485 tỷ; NPV=0 áp sai cho capex tuân thủ** (rev3, tâm −41%) | **CÓ — L7**: "dự án 'Nâng cấp hệ thống xử lý khí thải (QĐ 917)' (3,485 tỷ) là chi tuân thủ/bắt buộc không tạo doanh thu ⇒ treatment phải CASH_OUTFLOW (D3), đang NPV0_BOOK" + S thiếu `classification` |
| | | | Skeptic r1 INCONCLUSIVE: trọng số kịch bản tốt, lịch dừng PDP8 | KHÔNG (phán đoán nội dung; 25/50/25 đối xứng nên L2 không bắn) |
| | | | (chưa từng bị bắt) không khai quỹ KT-PL, bên liên quan (EVN mua điện, nhà nước ~80%), hạn/giá PPA, moat | S: `welfare_fund`, `related_parties`, `sector.ppa_expiry/ppa_price`, `terminal.moat_tier`, lãi huy động neo |
| **PAT rev1** 14/11 | `dd_PAT_20261114/assumptions_PAT.md` mục A–E | 8 | Thiếu trích quỹ KTPL 5,5% LNST trong FCFE | **CÓ — S** `welfare_fund.annual_appropriation_pct_of_npat` thiếu (rev1 chỉ trừ số dư 76,69) |
| | | | Bỏ sót TM4 cầm cố Vietinbank cho công ty thành viên | **CÓ một phần — S** `related_parties` vắng (lint không biết nội dung, chỉ ép phải khai) |
| | | | EBT cơ sở 245 > run-rate Q3; nhánh M1 lệch một chiều | KHÔNG (số liệu/phán đoán; rev1 có `asymmetry_reason` nên L2 đúng là không bắn) |
| | | | Kiểm toán FY25 + soát xét H1 **ngoại trừ** mà khoá không nêu cơ sở (lớp LLM/TV1) | **CÓ — S** `audit_opinion.emphasis_or_basis` |
| | | | Mù giá thủng (A2/A4: ADV, cột PE lỡ hiện) | **CÓ — L9** chuỗi "ADV" (cột PE ở A4 không ánh xạ vào JSON nên không thử) |
| **VLB r1** 22/11 | `dd_VLB_20261122/model/dcf_vlb_r1.py.bak` + `REPORT_r1.md` | 16 | Thiếu trừ trích quỹ ~14,8% LNST | **CÓ — S** `welfare_fund.annual_appropriation_pct_of_npat` |
| | | | Tốc độ cấn trừ tiền cấp quyền 47,6→19,4 tỷ/năm | KHÔNG (tham số mô hình) |
| | | | Thiếu BCTC 2025 kiểm toán (ca D5) | **CÓ — S** `audit_opinion` vắng; v1 buộc ghi `audited_fy_missing` ⇒ GHI CHÚ "không vào Bậc 1, cổng LAG = chưa có DD" |
| | | | Thiếu bảng giấy phép/hạn mỏ | **CÓ — S** `sector.license_expiry` (biến thể `mo_giay_phep`) |
| | | | Cổ tức tạm ứng 2.500đ GDKHQ 19/11 lệch cơ sở tiền ròng 30/9 vs giá (rev2) | **KHÔNG — schema v1 không có khoá này** (đề xuất Q3 dưới) |
| | | | Mô hình khoá đọc `px_vlb.csv` (giá+KL) để tính ADV | **CÓ — L9** |
| **VCB** (khoá r4 hiện hành) 17/11 | `dd_VCB_20261117/assumptions_VCB_20261117.json` (md5 sổ 85d41e08f8 là bản r1; file hiện là r4) | 9 | r1: thuế 20% áp sai lên lãi đánh giá lại 3.171 tỷ | **CÓ một phần — S** `tax` vắng (khoá chỉ có thuế cho khoản một lần) |
| | | | r1: VCSH đầu kỳ hardcode, chưa đọc BCTC KT 2025 | **CÓ một phần — S** `audit_opinion.auditor` vắng (nguồn "chưa render lại từ PDF") |
| | | | r4: cổ tức tiền 2.433đ/cp sau GDKHQ | KHÔNG — cùng lỗ hổng Q3 |
| | | | Tách dự phòng cho vay/TPDN; Gordon ngầm chia 56% vs thực ~10% | KHÔNG (phán đoán mô hình) |
| | | | ADV 175 tỷ nằm trong khoá mù giá | **CÓ — L9** |
| | | | Biến thể ngân hàng CAR/nhóm 2/bao phủ/LDR/CASA | QUA — tỉ số TÍNH được từ số dư trong khoá; CAR chỉ 1 nguồn báo chí (schema nhận vì có nguồn) |
| **MVC r4** 03/11 | `dd_MVC_20261103/REPORT_r4_20261103.md` | 19 | **Chương trình mỏ mới −495…−745 tỷ ở base** (luật 03/11 17:06, rev5) | **CÓ — L7**: "dự án growth … lệch NPV=0 (CASH_OUTFLOW) mà thiếu independent_basis" |
| | | | Holding 15%, vách giá 2028, LK ×0,8 … không cơ sở độc lập (rev5 bỏ) | KHÔNG (khoản giảm trừ tự do — chưa có khoá "mọi khoản giảm trừ base phải có cơ sở") |
| | | | Chưa có chiết khấu thanh khoản/neo lãi huy động (luật 22:27 cùng ngày, rev9) | S `liquidity_discount`, `discount_rate.deposit_rate_*`; L3 không chạy được vì thiếu lãi huy động. Ghi chú: r4 làm TRƯỚC luật 22:27 ⇒ đây là thiếu theo luật mới, không phải lỗi lúc đó |
| | | | Đếm hai lần trần chu kỳ (rev9) | KHÔNG (lỗi số học) |

## Kết luận đo được (5 ca)

- **22 dòng lỗi** (đếm tay theo bảng, không gồm dòng QTP "chưa từng bị bắt" và dòng VCB biến thể): **10 bắt đủ**, **4 bắt một phần** (PAT cầm cố, VCB thuế, VCB VCSH/BCTC KT, MVC thanh khoản — luật ra sau r4), **8 không bắt**: 6 là tham số/số học/phán đoán (QTP trọng số, PAT EBT/M1, VLB cấn trừ, VCB dự phòng/Gordon, MVC holding, MVC đếm đôi) — việc của phản biện, không phải lint; **2 là lỗ hổng schema** (cổ tức sau BCĐKT: VLB, VCB → Q3).
- **QTP: bắt đúng khoản 3.485 tỷ (L7)** — yêu cầu cứng của spec đạt.
- **L9 (mù giá) bắn ở 3/5 ca** (PAT, VLB, VCB): dữ liệu thanh khoản đang lọt vào file/mô hình khoá. Đây là quy
  ước fleet hiện hành ("SCL r3/TTA r3") ⇒ bật chặn L9 = đổi quy trình (tính thanh khoản ở bước riêng).
- **Báo giả**: chưa đo được trên DD THẬT viết theo v1 (chưa có ca nào) — mọi vi phạm ở đây là trên file ánh xạ
  ngược. Số báo giả ≤10% (điều kiện bật chặn) phải đo trên 2 tuần DD mới.

## Lỗ hổng/quyết định thiết kế cần Mike / quant-skeptic soát

1. **L7 dựa vào cờ tự khai** `mandatory`/`generates_revenue`: người lập vẫn có thể khai sai (QTP v1 nếu ghi
   `growth`). Lint chỉ ép PHẢI khai + nhất quán; bắt khai sai cần phản biện "thiếu hạng mục" (P0-3).
2. **L9 regex** (`ADV`, `P/E 6`, `giá thị trường`, khoá `adv*/pe/pb/close/volume`) — có thể báo giả khi chuỗi
   chỉ KỂ việc đã dùng (PAT A2). Giữ hay hạ thành ghi chú?
3. **Thiếu khoá "phân phối sau ngày BCĐKT"** (cổ tức tạm ứng/GDKHQ giữa ngày BCĐKT và ngày định giá — VLB r2,
   VCB r4; QTP v1 đã tự trừ). Đề xuất thêm `post_bs_distributions` bắt buộc ở v1.1.
4. **Không có khoá "mọi khoản giảm trừ ở base phải có cơ sở dữ liệu"** (MVC holding 15%) — luật 03/11 yêu cầu
   nhưng khó cơ học hoá; đề xuất mảng `base_haircuts[]` mỗi mục bắt buộc `independent_basis`.
5. **L3 tolerance 5bp** và β mặc định 1,0 đọc từ `kb/config/dd_ke_bands.json`; điểm neo lãi huy động 7,40%
   lấy từ ghi chú khoá VCB/PAT (không tự gọi `deposit_rate_vn` — lint không chạm mạng/BQ).
6. **L5/L6 chỉ áp từ `M20261122`** (D4) — file cũ không bị bắt hồi tố. L10 (FY kiểm toán < năm−1) áp mọi ngày.
7. **`liquidity_discount.basis=sensitivity_only` mà `pct>0`** (PAT 10% "ước lượng") — schema cho qua; luật 03/11
   nói không có cơ sở ⇒ chỉ độ nhạy. Có ép `pct=null` không?
8. **Mốc M20261122 chưa có trong SKILL.md** (B5 sẽ thêm) — ghi `in_skill:false` trong config.
9. Số tỉ số ngân hàng VCB do tôi TÍNH từ số dư trong khoá (LDR thô, không theo TT22) — biến thể bank có nên
   bắt buộc nguồn thuyết minh trực tiếp thay vì tự tính?


---
## VÒNG 2 (22/11/2026, theo `SKEPTIC_R1_REQUIRED_CHANGES.md`) — ĐIỀU CHỈNH CÁCH ĐỌC KẾT QUẢ Ở TRÊN

**B3 — Giới hạn của "bắt được lỗi cũ".** Bảng trên là **TRONG MẪU và HỒI TỐ**: luật D3 sinh ra từ ca QTP, và L7 áp
hồi tố lên file QTP không có cổng `method_version` thật (vòng 2 đã gate theo mốc nhưng file thiếu `method_version`
nay được coi là mốc MỚI NHẤT, nên QTP vẫn bị bắt); kết quả L7 còn **phụ thuộc cờ tự khai** (`mandatory`,
`generates_revenue`, `classification`) — người lập khai sai cả ba thì lint không biết. Số "10/22 bắt đủ" KHÔNG phải
tỉ lệ bắt ngoài mẫu. Vòng 2 chỉ vá những cách né cơ học đã biết (ràng buộc chéo, file rỗng-ruột), không vá khai sai.

**Tiêu chí bật chặn (sửa).** Bật chặn (đặt `DD_ASSUMPTIONS_LINT_ENFORCE_FROM`) khi **CẢ HAI**:
(a) báo giả ≤ 10% trên DD thật 2 tuần; (b) **tỉ lệ PHỦ**: trong bộ ca né-khoá/rỗng-ruột do người KHÁC (skeptic) dựng,
lint bắt ≥ 90%. Số hiện có (do chính tác giả dựng nên chỉ là sàn, không phải đo độc lập): file rỗng-ruột 1/1 bắt
(≥1 vi phạm; trước vòng 2: 0), 5/5 đột biến QTP bắn L7 (`qtp_mutations_raw.txt`; trước vòng 2: 0/4 lọt).
Đột biến MÃ lint: 15/15 bị selfcheck giết (`mutants_raw.txt`).

**Số liệu chạy lại 5 ca sau vòng 2** (`trial/lint_output_raw.txt`, `/usr/bin/python3`, cảnh báo rc=0 cả 5):
MVC 20 · PAT 9 · QTP 14 · VCB 11 · VLB 16 vi phạm (trước: 19/8/13/9/16 theo skeptic tái lập). Tăng là do luật mới
(S chặt hơn, L7 chéo, L14). Báo giả tiềm năng đã thấy: VCB bank khai 1 `capital_commitments_12m` không có `amount_bn`
(ánh xạ ngược của tôi) + `projects` rỗng ⇒ L7 chéo bắn "0 tỷ" — có thể đúng (cam kết ngoại bảng bị bỏ quên) hoặc
báo giả do ánh xạ; chưa phân xử.

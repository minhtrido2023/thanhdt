# Plan — Funnel 8L hằng ngày tìm candidate cho discretionary sleeve (đề xuất 2026-10-06, CHỜ USER DUYỆT)

## Vì sao bỏ quét tuần
- `fearbuy_weekly_scan.sh` (Taylor, Opus/high), 08-14→10-05: **16 lượt (8 thứ Sáu + 8 thứ Hai), 27 "case mới", 0 QUALIFY**.
  QUALIFY duy nhất còn sống (TV1, HPG-2022 hồi cứu) đều có từ trước khi có cron.
- Gốc rễ: quét bắt đầu từ **TIN XẤU + giá sập** (anomaly_scan: FLOOR2/IDIOCRASH, WebSearch khởi tố) rồi mới
  hỏi "công ty có tốt không". Phần lớn mã sập vì tin xấu là mã xấu ⇒ NON. Cùng kết luận với
  `calculated_fear_state_backstop.md` §12: screen cơ học theo cú sập riêng lẻ = **không có edge** (median excess −7% @12m).
- `discretionary_candidate_funnel.py` (4 lớp: washout + 8L + insider/redflag + marginability) ĐÃ có sẵn nhưng chỉ chạy
  nhờ quét thứ Sáu; ra 18-22 mã FULLY_QUALIFIED mỗi lần nhưng không mã nào thành case vì đều là trôi cả ngành/thị trường.

## Hướng mới: đảo thứ tự — CHẤT LƯỢNG trước, RẺ sau, TIN cuối
8L đã chấm sẵn hằng ngày (19:20, `pt_8l_daily.sh`) mọi thứ cần cho 2 bước đầu. Chỉ khi một mã chất lượng
**mới** rơi vào vùng rẻ bất thường thì mới tốn tiền LLM để đọc tin và làm due diligence.

### Tầng 1 — Funnel cơ học hằng ngày (Python, KHÔNG LLM, ~19:35 sau `pt_8l_daily`)
| Lớp | Điều kiện | Nguồn có sẵn |
|---|---|---|
| Chất lượng | `rating ≤ 2` (đúng cổng sleeve hiện hành), golden floor (ROE_Min3Y≥0 ∧ CF_OA_3Y>0), không BANNED / `forensic_flags` exclude / insider redflag | `data/rating_8l.csv`, `universe_pit_quality`, `insider_flags.json` |
| Rẻ so với CHÍNH NÓ | `pb_z ≤ −1` (ô golden của `cheap_pb_floor.py`) **hoặc** earn_yield ở phân vị cao trong lịch sử 5 năm của chính mã | `rating_8l.csv`, `cheap_pb_floor.py` |
| Lệch giá | dd52 ≤ −20% hoặc `drop_pct` (Close vs đỉnh 3 tháng) ≤ −20% | `rating_8l.csv` |
| Thanh khoản | liq_bn ≥ 3, ≤10% ADV cho size dự kiến | `rating_8l.csv` |
| Nhãn bối cảnh (KHÔNG loại) | **IDIO** (mã giảm sâu hơn trung vị cùng route/ngành ≥ 15pp) vs **NGÀNH** (cả ngành cùng giảm) | tính mới, 1 hàm |

- Tái dùng `discretionary_candidate_funnel.py` làm lõi (sửa ngưỡng theo bảng trên), KHÔNG viết engine mới.
- **Sổ trạng thái** `data/discretionary_candidates_state.json`: chỉ báo mã **MỚI vào** hoặc **xấu đi đáng kể**
  (pb_z giảm thêm ≥0,5); mã đã báo thì cooldown 30 ngày. **Đếm thật trên `rating_8l.csv` 05/10**: rating≤2 ∧ liq≥3 = 42 mã; thêm pb_z≤−1 = 16 (VCB CTG ACB ACV VNM PNJ SCS VGC CTR FPT VHC DGC IDC VRE MBS SSI — phần lớn là rẻ CẢ THỊ TRƯỜNG); thêm drop_pct≤−20% = **2 (PNJ — đã EXCLUDED, MBS)**. ⇒ lớp lệch giá là lớp lọc chính; ngưỡng −20% cho số lượng vừa sức DD.
- Đầu ra: 1 dòng trong topic việc-cần-quyết 08:00 (`daily_decision_topic.py`). Không có mã mới ⇒ "Funnel 8L: 0 mới (N đang theo dõi)" — không im lặng.
- **Snapshot hằng ngày** `rating_8l.csv` → `data/rating_8l_daily/` để có lịch sử PIT `value_score`/`pb_z` (hiện KHÔNG có) cho đo hiệu quả sau này.

### Tầng 2 — Proposal → due diligence (LLM, chỉ khi có mã MỚI)
1. Mã mới ⇒ Mike đề xuất trong topic sáng; **user chọn mã nào đáng làm DD** (mặc định: không làm gì).
2. Duyệt ⇒ `dispatch.sh Taylor` (Opus/high, nghiên cứu): đọc tin 30 ngày + BCTC, phân loại theo backstop §2 (scandal) / §2.5 (chu kỳ/vĩ mô/gián đoạn), DCF, cảnh báo pháp lý theo luật 2026-09-27 ⇒ QUALIFY/NON/AMBIGUOUS.
   Nhãn NGÀNH (§2.5 nhóm c, vĩ mô) ⇒ chạy **Bobby** (macro-strategist) TRƯỚC Taylor, mù forward return.
3. QUALIFY ⇒ `fundamental-skeptic` ⇒ CONFIRMED mới trình user kèm đề xuất size.
4. User duyệt ⇒ ghi `state_<TICKER>_<acct>.json` ⇒ `inject_discretionary_orders.sh` 20:30 ⇒ plan T+1 ⇒ duyệt plan như thường.
- Trần chi phí: tối đa 2 DD/tuần; vượt ⇒ xếp hàng theo (rating, pb_z).

### Tầng 3 — Đo trung thực (vì chưa có bằng chứng screen này có edge)
- ⚠️ Nghiên cứu cũ: deep-discount sleeve (pbz≤−1,5) **PARKED** — edge chỉ ở OOS và chỉ trong CRISIS/BEAR (CAPIT đã phủ);
  composite v3 làm entry-selector = **NO**. ⇒ Funnel là **nguồn ý tưởng cho người quyết**, KHÔNG phải tín hiệu mua tự động.
- Ghi mọi candidate (kể cả không làm DD) + forward excess 6/12 tháng so rổ rating≤2 cùng route (PIT). Checkpoint **2027-04-06**:
  nếu nhóm candidate không hơn rổ so sánh ⇒ siết hoặc bỏ funnel.

## Việc kỹ thuật (sau khi duyệt)
1. Sửa `discretionary_candidate_funnel.py` theo bảng Tầng 1 + nhãn IDIO/NGÀNH + sổ trạng thái + snapshot (Opus/high, 1 dispatch, arch-review 1 lần).
2. Cron 19:35 T2-T6 (§11 cron_registry), đầu ra vào `daily_decision_topic.py`.
3. Cập nhật `fearbuy_weekly_scan.sh` bỏ khối funnel; giữ/bỏ lượt thứ Hai theo quyết định dưới.
4. Bus/KB: đóng mandate quét tuần 2026-07-23, cập nhật `kb/current_ops.md` § R&D pipeline.

## Cần user quyết
1. **Lượt quét thứ Hai 08:00** (bảo vệ phía mua trước phiên): giữ hay bỏ? 8 lượt: 2 case, 0 lệnh phải rút.
   Cảnh báo cú sập giá của mã đang giữ đã có `ops_health_check` 08:20 lo; thứ Hai chỉ thêm phần tin cuối tuần.
2. **Ngưỡng chất lượng**: `rating ≤ 2` (cổng sleeve hiện hành) hay nới `≤ 3`?
3. **Ngành trôi chung** (nhãn NGÀNH): vẫn báo làm candidate hay chỉ báo IDIO? (backstop §0.5 cũ nói case chu kỳ/vĩ mô do user tự đưa)
4. **Size**: backstop §12 nói 0,5-1,5% NAV/mã, sleeve ≤3%; thực tế TV1/DRI đang 5%/mã/TK, margin policy cho sleeve ≤10%. Mã mới theo mức nào?

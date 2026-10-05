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

---

## Bản sửa sau trả lời user 2026-10-06 00:43 ICT

**Đính chính**: con số "lớp 3 còn 2 mã (PNJ, MBS)" ở trên chưa áp golden floor. Áp đủ thì MBS rớt
(CF_OA_3Y âm — công ty chứng khoán), còn PNJ (đang EXCLUDED).

### Q4 — Size: GIỮ 5% NAV/mã/tài khoản (user chốt). Mục "0,5-1,5%" của backstop §12 hết hiệu lực cho sleeve này.

### Q3 — Nhãn NGÀNH: vẫn là candidate, nhưng BẮT BUỘC Bobby đánh giá triển vọng ngành TRƯỚC Taylor (mù forward return).

### Q2 — Ngưỡng chất lượng: hạ về `rating ≤ 3` (= cổng production), thêm làn giá trị sâu
Đo trên `data/rating_8l.csv` 05/10: TV1 rating **1**, DRI **2**, PVT **3** (bản live; lịch sử BQ ghi 2 tới 29/07).
⇒ rating KHÔNG phải thứ chặn 2 mã đã chọn; thứ chặn là **thanh khoản** (TV1 0,47 tỷ/ngày < 3 tỷ) và
**định nghĩa "rẻ"** (DRI pb_z +0,56, không giảm giá — không bao giờ lọt làn "lệch giá").
- **Làn A — Lệch giá** (như trên): rating≤3 ∧ golden floor ∧ pb_z≤−1 ∧ drop_pct≤−20% ∧ liq≥0,3 tỷ. Hôm nay: 11 mã
  (CMG DTD DVM HDG KOS LCG NTL PNJ TCM VGS VSC).
- **Làn B — Giá trị sâu**: rating≤3 ∧ golden floor ∧ liq≥0,3 tỷ, xếp **earn_yield (1/PE) trong CÙNG route**
  (không so ngân hàng với sản xuất), lấy top-3/route; chỉ báo mã MỚI vào top. Dùng 1/PE vì là nhân tố trội
  có bằng chứng (IC +0,125); KHÔNG dùng composite value_score (làm bộ chọn = NO). Hôm nay ra 18 mã, **có TV1
  (#3 COMPOUNDER) và DRI (#2 CYCLICAL)**, DGC. ⚠️ Đây là kiểm tra trong mẫu (2 mã được chọn một phần VÌ PE thấp)
  — xác nhận làn không bỏ sót loại mã đã chọn, KHÔNG chứng minh làn có edge.
- **PVT không lọt làn nào** (PE 8,8, pb_z +0,73, không giảm giá): rating≤3 cho PVT vào vũ trụ nhưng không quy
  tắc rẻ nào ở đây chọn nó. ⇒ cần biết user thấy PVT hấp dẫn vì đâu (tăng trưởng đội tàu? cổ tức? chu kỳ cước?)
  rồi mới quyết có làn thứ 3 hay để PVT-loại là đề xuất tay của user.
- Thanh khoản ≥0,3 tỷ đủ cho size 5% NAV (~50 triệu/TK) với trần 10% ADV/phiên (TV1: ~47 triệu/phiên).

### Q1 — Thay quét thứ Hai bằng cổng giá TRONG PHIÊN cho mã đang giữ/sắp mua
Đối chiếu giá ngày 07→10/2026 (`data/bq_cache/ticker`) với ngày có tin:
| Mã | Tin | Biến động giá | Cổng EOD hiện có (IDIOCRASH ret≤−6 ∧ idio≤−5) |
|---|---|---|---|
| PNJ | công bố DN 25-27/09 (T6-CN) | **24/09 −5,7% (idio −4,2, đáy −5,8%) — TRƯỚC tin 1 ngày**; 28/09→05/10 sàn 6 phiên liền, KL chỉ 0,3-0,6× (không bán được ở sàn) | 24/09 KHÔNG bắt (−5,7 > −6); 28/09 mới bắt |
| DGC | vụ án lan sang ban điều hành 23/07 | **23/07 −6,3% (idio −8,1), KL 7,6×** — cùng ngày tin; 22/07 −5,8% nhưng idio −2,2 (cả thị trường) | 23/07 bắt, nhưng báo lúc 08:20 hôm SAU |
| TV1 | vụ án EVNNPT giữa 07 | **16/07 −5,0% (idio −6,2, đáy −6,4%)**; tin 08/09 (thua phúc thẩm) và 13/09 (khởi tố cựu CT EVNNPT): giá KHÔNG phản ứng | 16/07 KHÔNG bắt (−5,0 > −6) |
- **Bot KHÔNG đặt lệnh MUA trước 11:00**: 40 journal gần nhất, từ khi HYBRID live 26/08 có **0 lệnh BUY đặt trước 11:00**
  (khung 11:00/11:15/13:00/13:15/13:30). ⇒ cổng giá chạy từ 09:15 có ~1h45 để rút lệnh mua của mã gãy luận
  điểm TRƯỚC khi lệnh ra sàn — đúng việc quét thứ Hai 08:00 đang làm, nhưng chạy MỌI phiên chứ không chỉ thứ Hai.
- **Thiết kế** (`intraday_price_watch.py`, Python, không LLM, 15'/lần 09:15→14:30 T2-T6, giá DNSE sống):
  vũ trụ = vị thế đang giữ 2 TK + mã có lệnh MUA trong plan hôm nay + watchlist discretionary.
  Kích hoạt khi **giá ≤ −5% so tham chiếu ∧ idio (so VNINDEX) ≤ −4%**, hoặc chạm sàn. Mỗi mã 1 lần/ngày.
  Kích hoạt ⇒ (1) Trading Daily + @user; (2) dispatch DD: legal-vn đọc tin + Taylor (Opus) kết luận
  luận điểm còn/gãy trong ~30-60'; (3) đề xuất HOLD / không mua thêm / bán phiên sau — user quyết.
  Tuỳ chọn cần user duyệt riêng (chạm logic đặt lệnh): tự hoãn lệnh MUA mã đó trong phiên khi kích hoạt.
- Ngưỡng −5/−4 bắt cả 3 ca đầu tiên (PNJ 24/09, DGC 23/07, TV1 16/07) mà không bắt DGC 22/07 (cả thị trường giảm).
  ⚠️ dùng giá ĐÁY ngày làm proxy cho giá trong phiên ⇒ là cận trên của số lần kích hoạt; chưa đo tỉ lệ báo giả trên
  toàn bộ danh mục — làm khi dựng.
- **Giới hạn thật**: tin không làm giá động (TV1 08/09, 13/09) thì cổng giá không thấy — chấp nhận, vì giá không
  phản ứng tức thị trường không coi là gãy luận điểm; mã kẹt sàn (PNJ 28/09+) không bán được trong phiên, quyết
  định thực tế là ngừng mua và lên kế hoạch phiên sau.
- Tắt quét thứ Hai SAU KHI cổng giá chạy ổn 2 tuần (không để khoảng trống bảo vệ).

---

## Quyết định user 2026-10-06 01:00 ICT + ĐỀ XUẤT chiến lược cutloss (CHỜ DUYỆT trước khi dựng)

User chốt: giữ quét thứ Hai 2 tuần song song; rating≤3; thêm làn B; hạ thanh khoản. Cổng giá trong phiên:
mã ĐANG MUA ⇒ dừng mua nếu còn kịp; mã ĐANG GIỮ ⇒ điều tra ngay, báo Telegram + email, **không trả lời
trong 30 phút ⇒ mặc định bán cutloss**. PVT/DRI: tăng trưởng lợi nhuận nhanh ⇒ Taylor nghiên cứu làn C
(job `Taylor_20261005_180155`). Funnel A+B đang dựng (job `Taylor_20261005_180152`).

### Chiến lược cutloss đề xuất
**Dòng thời gian** (T0 = lúc cổng giá kích hoạt, chỉ trong giờ khớp lệnh liên tục):
| Mốc | Việc |
|---|---|
| T0 | Telegram + email + Discord Trading Daily (@user): mã, KL, %NAV, lãi/lỗ, mức giảm, "đang điều tra". Mã đó có lệnh MUA trong plan phiên này ⇒ hoãn ngay (bot chưa đặt mua trước 11:00). |
| T0 → T0+20' | Điều tra nhanh: legal-vn đọc tin + Taylor (Opus) ⇒ phán quyết **GÃY** (pháp lý dính pháp nhân/tài sản lõi, gian lận, KQKD sụp, mất khả năng thanh toán) / **NHIỄU** (không tìm thấy tin, tin cá nhân không dính lõi, cả ngành) / **CHƯA RÕ**. Quá 20' chưa xong ⇒ coi là CHƯA RÕ. |
| T0+20' | Báo cáo quyết định (Telegram + email + Discord) kèm hành động mặc định và **hạn chót = gửi báo cáo + 30'**. |
| Hạn chót | Anh trả lời "GIỮ <MÃ>" / "BÁN <MÃ>" / "BÁN 50% <MÃ>" ⇒ làm theo. Im lặng ⇒ hành động mặc định. |

**Hành động mặc định khi im lặng** — tôi đề xuất THEO PHÁN QUYẾT, không phải luôn bán:
- **GÃY ⇒ bán toàn bộ.**
- **CHƯA RÕ ⇒ bán 50%**, giữ 50% chờ anh (giảm rủi ro mà không bán hết ở đáy hoảng loạn).
- **NHIỄU ⇒ GIỮ, không bán.** Lý do: bán vì cú giảm không có tin là bán đúng lúc sợ hãi — ngược triết lý fear-buy;
  PNJ 07/2026 có nhiều phiên −7% mà luận điểm khi đó vẫn AMBIGUOUS.
- Nếu anh muốn đúng "im lặng = bán" cho mọi trường hợp thì chọn phương án đó; tôi nêu rủi ro ở trên.

**Cách bán** (không bán thị trường bằng mọi giá):
- Lệnh giới hạn tại giá mua tốt nhất hiện tại, chia lệnh con ≤20% khối lượng trung bình 20 phiên; chỉ bán phần
  KL **bán được** (cổ phiếu mua T+2 chỉ bán được từ phiên chiều ngày T+2).
- **Kẹt sàn** (không có bên mua): đặt sẵn tại giá sàn để xếp hàng; phần không khớp chuyển sang phiên sau 09:15.
- **Giờ**: hạn chót rơi vào nghỉ trưa 11:30-13:00 ⇒ thực hiện lúc 13:00; sau 14:15 ⇒ không đặt cuối phiên, chuyển phiên
  sau 09:15 (anh có thêm thời gian đến sáng). Kích hoạt sau 14:00 ⇒ chỉ báo + điều tra, quyết định cho phiên sau.
- Sau khi bán: cấm mua lại mã đó 10 phiên trừ khi anh duyệt; plan T+1 tự loại.
- Mỗi mã kích hoạt tối đa 1 lần/ngày. `data/BOT_STOP` chặn mọi lệnh bán tự động. Ghi trạng thái trước khi đặt lệnh,
  đối chiếu sổ lệnh broker trước mỗi lần đặt (không bán trùng nếu tiến trình chết giữa chừng).

**Phạm vi** (cần anh xác nhận):
- Áp cho mọi vị thế cổ phiếu 2 tài khoản. ⚠️ Mâu thuẫn với quyết định 2026-07-20 "custom30V không stop-loss" — park
  hiện 0% nên rổ custom30V gần như không có vị thế; đề xuất loại custom30V khỏi auto-cutloss (chỉ báo + điều tra).
- Discretionary sleeve (TV1, DRI…) mua có chủ đích khi giá rẻ/sợ hãi: đề xuất chỉ auto-bán khi phán quyết GÃY;
  TV1 thanh khoản thấp (~0,47 tỷ/ngày) dễ giảm 5% vì lệnh nhỏ.
- Kích hoạt cần cả hai: giảm ≥5% so tham chiếu VÀ giảm hơn VNINDEX ≥4 điểm % (hoặc chạm sàn) ⇒ cả thị trường sập
  không kích hoạt hàng loạt.

**Kênh trả lời**: Discord Trading Daily (tôi đọc được ngay) là kênh chính. Telegram: bot nhận lệnh
`telegram_8l_bot.py` có sẵn nhưng KHÔNG đang chạy — bật lại để nhận "GIỮ/BÁN" là việc riêng. Email chỉ để báo,
không nhận trả lời.

**Dựng**: Opus high, 1 dispatch + arch-review + risk-auditor; chạy shadow (chỉ báo, không đặt lệnh bán) 5 phiên
rồi mới bật auto-bán. Chạm logic đặt lệnh ⇒ cần anh duyệt bản cuối trước khi bật.

---

## User duyệt 2026-10-06 01:12 ICT + KỊCH BẢN BÁN KHI "GÃY" (bản cụ thể)

User chốt: mặc định theo phán quyết (GÃY=bán hết / CHƯA RÕ=bán 50% / NHIỄU=giữ) — "dựa trên nghiên cứu của team, không bán theo tâm lý"; **custom30V cũng theo đúng quy trình này** (thay quyết định 2026-07-20 "không stop-loss" cho trường hợp có sự kiện bất thường); discretionary chỉ tự bán khi GÃY; trả lời qua Discord.

### Dữ liệu dùng mỗi phút khi đang bán (đã có trong `DNSEBroker.get_quote()` + sổ lệnh L2)
`last`, `ref`, `floor`, các mức giá mua (giá, KL), KL khớp trong ngày, KL **bán được** của mình (Q).
- `room` = (last − floor) / ref — khoảng cách tới giá sàn, % theo giá tham chiếu (HOSE sàn −7%, HNX −10%, UPCOM −15%).
- `speed` = % thay đổi giá 5 phút gần nhất.
- `depth2` = tổng KL đặt mua trong khoảng 2% dưới giá khớp gần nhất.

### 4 chế độ — chỉ được LEO thang trong ngày, không lùi về chế độ chậm hơn
| Chế độ | Khi nào | Cách bán |
|---|---|---|
| **1. Bình thường** | room > 3% và speed > −1%/5' | 3 đợt trong ~20': 50% ngay, 25% sau 10', 25% sau 20'. Mỗi lệnh con LO tại giá mua tốt nhất, ≤ 30% `depth2`; 2' chưa khớp ⇒ đặt lại theo giá mua mới. |
| **2. Nhanh** | speed ≤ −1%/5' **hoặc** 1,5% < room ≤ 3% | Bán TOÀN BỘ phần còn lại ngay: tách lệnh con theo KL 2 mức giá mua tốt nhất, đặt lại mỗi 1', chấp nhận giá xuống. |
| **3. Khẩn** | room ≤ 1,5% **hoặc** `depth2` < Q | MỘT lệnh LO cho toàn bộ Q **tại giá sàn**. Lệnh bán LO giá sàn khớp ngay với mọi lệnh mua đang chờ **theo giá của bên mua** (không phải bán ở giá sàn), phần dư nằm xếp hàng ở giá sàn và giữ ưu tiên thời gian. |
| **4. Kẹt sàn** | giá = sàn và không còn bên mua | Giữ nguyên lệnh ở giá sàn cả phiên (thứ tự xếp hàng quý nhất — PNJ sàn 6 phiên liền, KL chỉ 0,3-0,6×). 14:30 ⇒ phần dư vào ATC. Phiên sau: đặt lệnh **ATO** trước 09:15 (ATO được ưu tiên trong phiên mở cửa), không chờ khung bán 09:15 của bot. |

### Bảo vệ khi giá rơi nhanh TRONG lúc đang điều tra (trước phán quyết)
- room ≤ 3% khi chưa có phán quyết ⇒ **rút gọn**: điều tra tối đa 10' (thay 20'), hạn trả lời 15' (thay 30'), báo cáo ghi rõ "chế độ rút gọn vì sát sàn".
- Không bán trước khi có phán quyết (đúng nguyên tắc user: không bán theo tâm lý). Chấp nhận rủi ro kẹt sàn nếu tin đến quá nhanh — khi đó áp chế độ 4.

### Quy tắc chung
- CHƯA RÕ ⇒ cùng 4 chế độ, áp cho 50% KL.
- Chỉ bán phần KL bán được (mua T+2 bán từ phiên chiều ngày T+2); phần còn lại bán khi về.
- Nghỉ trưa 11:30-13:00 ⇒ dừng, 13:00 tiếp tục đúng chế độ đang có. Sau 14:30 ⇒ ATC; ngoài giờ ⇒ ATO phiên sau.
- Tần suất theo dõi: 15' khi bình thường, **1' khi đang bán**.
- Báo Discord + Telegram mỗi lần khớp và khi đổi chế độ. `data/BOT_STOP` chặn mọi lệnh. Ghi trạng thái trước mỗi lệnh, đối chiếu sổ lệnh broker trước khi đặt (không bán trùng).
- Sau bán: không mua lại 10 phiên trừ khi user duyệt; mã thuộc custom30V bị loại khỏi rổ tới khi review.
- ⚠️ Cần xác minh khi dựng: DNSE thật có nhận lệnh ATO/ATC không (code hiện chỉ dùng LO; ATO/ATC mới thấy ở broker giả lập). Không nhận ⇒ thay bằng LO giá sàn đặt lúc 09:00.

### Dựng & kiểm chứng
- 1 dispatch Opus high (Taylor, cùng engine `intraday_price_watch.py`) + arch-review + risk-auditor.
- **Replay** kịch bản trên dữ liệu phút nếu có (PNJ 24/09→05/10, DGC 23/07); không có dữ liệu phút ⇒ mô phỏng bằng OHLC ngày, nói rõ giới hạn.
- Chạy **shadow 5 phiên** (chỉ báo, ghi "đã định bán gì, giá nào"), không đặt lệnh thật; user duyệt bản cuối rồi mới bật.

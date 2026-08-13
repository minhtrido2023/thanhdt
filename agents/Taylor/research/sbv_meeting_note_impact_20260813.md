# Tài liệu định hướng NHNN (họp với các NH) — tác động tới book & hệ thống

job `Taylor_20260813_164933` · 2026-08-13 · Taylor (Quant)

## Trạng thái bằng chứng — đọc trước

| Nhãn | Nghĩa |
|---|---|
| **[VERIFIED]** | Đo được từ BQ / code production / artifact live. Trích dẫn được. |
| **[HYPOTHESIS]** | Suy luận định tính từ tài liệu họp. **CHƯA kiểm chứng, KHÔNG phải finding.** |
| **[GAP]** | Câu hỏi quan trọng mà dữ liệu hiện có KHÔNG trả lời được. |

Nguồn gốc tài liệu: ghi chú họp nội bộ, **không có ngày**, không phải văn bản NHNN chính thức,
không phải dữ liệu BQ. Tôi **không** xác minh được ngày ban hành — mọi kết luận dưới đây giả định
nội dung phản ánh định hướng H2/2026. Nếu tài liệu cũ hơn (ví dụ kỳ 2025), phần §3/§4 đổi nghĩa
đáng kể. **Đề nghị user xác nhận mốc thời gian trước khi dùng làm cơ sở quyết định.**

---

## §0. Tiền đề của dispatch cần sửa: rủi ro lãi suất KHÔNG nằm ở 3 mã [VERIFIED]

Dispatch hỏi về "MBB/ACB/HDB — nhóm ngân hàng đang nắm giữ". Đọc vị thế thật
(`dnse_raw_2026-08-13.jsonl`, bản ghi `positions` 20:30 ICT):

| Account | Active stock MV | **Rổ ngân hàng** | MBB+ACB+HDB |
|---|---|---|---|
| SpaceX | 1.638,0tr | **1.094,0tr = 66,8%** (13 mã) | 268,2tr = **16,3%** |
| ZaloPay | 777,9tr (đã trừ DGC legacy 439,0tr) | **455,5tr = 58,6%** (13 mã) | 55,2tr = **7,1%** |

Top-weight SpaceX: CTG 11,38% · BID 11,15% · VPB 8,82% · MBB 7,71% · VCB 6,54% · HDB 6,03% ·
TCB 4,64% · LPB 3,61% · ACB 2,58%. ZaloPay bị chi phối bởi **VPB 26,72%**.

**⇒ Phân tích chỉ 3 mã sẽ bỏ sót ~3/4 phần chịu tác động.** Toàn bộ §1 dưới đây làm trên cả 13 mã.
Không phải phê bình dispatch — đây là điều chỉnh phạm vi vì số liệu bắt buộc phải vậy.

---

## §1. NIM / lợi nhuận nhóm ngân hàng

### 1a. Cái BQ KHÔNG trả lời được — nói trước, đừng để lẫn vào phần đo được [GAP]

Quét toàn bộ `bigquery_dictionary.json`: **không có một cột nào** về `NIM`, `NII`, `CASA`,
`deposit`, `loan`, `LDR`. `ticker_financial` với ngân hàng còn trả `StLiab_P0 = LtLiab_P0 =
StDebt_P0 = LtDebt_P0 = CR_P0 = FinLev_P0 = 0` (schema doanh nghiệp phi tài chính, không map được
bảng cân đối ngân hàng).

Nghĩa là **đúng ba biến mà tài liệu NHNN nói tới — CASA, LDR, tỷ lệ vốn ngắn hạn cho vay
trung-dài hạn — đều KHÔNG đo được bằng hạ tầng dữ liệu hiện tại.** Câu hỏi "ngân hàng nào có cơ
cấu vốn chịu áp lực hơn" **không trả lời được bằng số** ở thời điểm này.

Muốn trả lời phải: parse thuyết minh BCTC (tiền gửi không kỳ hạn / tổng tiền gửi; dư nợ / tiền
gửi) — việc build nguồn dữ liệu mới, cần dispatch riêng cho Winston (data-ops), không làm trong
job này. **Tôi cố tình KHÔNG dùng CASA "theo trí nhớ/thị trường đồn"** — đó đúng là loại khẳng
định mà `verify-real-facts-dont-self-invent` cấm.

### 1b. Cái BQ TRẢ LỜI được: đệm lợi nhuận trên mỗi đồng dư nợ [VERIFIED]

Đo được **độ nhạy lợi nhuận với một cú cắt lãi suất cho vay** — không cần biết CASA:

> Δ LNTT / LN ròng TTM  =  Δlãi suất × (L × Tổng tài sản) / LN_TTM

`L` = dư nợ / tổng tài sản, quét 0,60–0,75 (dải điển hình NH VN). Nguồn: `ticker_financial`
2025Q3→2026Q2 (TTM), truy vấn trong job. Bỏ qua thuế ⇒ số này **đánh giá THẤP** tác động thật
(~×1,25 nếu quy về sau thuế).

**Mỗi 10bp cắt lãi vay, không bù bằng huy động** (% LN ròng TTM):

| Bank | L=0,60 | **L=0,70** | L=0,75 | w SpaceX | w ZaloPay |
|---|---|---|---|---|---|
| BID | 6,40% | **7,47%** | 8,00% | 11,15% | 4,99% |
| SHB | 4,77% | **5,57%** | 5,96% | 1,80% | 0,46% |
| CTG | 4,42% | **5,16%** | 5,53% | 11,38% | 4,34% |
| TPB | 4,26% | **4,98%** | 5,33% | 1,59% | 0,19% |
| **ACB** | 4,09% | **4,77%** | 5,11% | 2,58% | 0,86% |
| VCB | 3,83% | **4,47%** | 4,79% | 6,54% | 7,65% |
| **MBB** | 3,46% | **4,03%** | 4,32% | 7,71% | 3,97% |
| **HDB** | 3,28% | **3,83%** | 4,10% | 6,03% | 2,26% |
| LPB | 3,27% | **3,82%** | 4,09% | 3,61% | 2,43% |
| VPB | 3,02% | **3,53%** | 3,78% | 8,82% | **26,72%** |
| TCB | 2,82% | **3,29%** | 3,52% | 4,64% | 3,90% |

**Trả lời trực tiếp câu hỏi 1 (trong rổ 3 mã): ACB nhạy nhất (4,77%), MBB giữa (4,03%), HDB ít
nhất (3,83%).** Khoảng cách ACB↔HDB là **~25%**, không phải khác biệt vụn.

Bình quân gia quyền toàn rổ ngân hàng (L=0,70): SpaceX **−4,80%** LN rổ / 10bp · ZaloPay **−4,21%**.

**⚠️ ĐÂY LÀ CẬN TRÊN CÓ CHỦ ĐÍCH, KHÔNG PHẢI DỰ BÁO.** Nó giả định: toàn bộ dư nợ tái định giá
ngay, không bù bằng lãi huy động, không bù bằng tăng trưởng khối lượng, phí/ngoại hối không đổi.
Kịch bản 50bp (SpaceX: LN rổ −24%, NAV −16% nếu PE không đổi) **là stress test, KHÔNG phải base
case** — chỉ thị thực tế thường chỉ chạm lãi suất mới/lĩnh vực ưu tiên, tác động toàn danh mục
nhiều khả năng ở dải 10–25bp.

### 1c. Vì sao cận trên này vẫn đáng đọc [HYPOTHESIS]

Thông thường "cận trên không bù trừ" là kịch bản vô lý vì ngân hàng luôn có 3 van xả. Điểm đáng
chú ý của tài liệu này là **nó mô tả đúng cơ chế bịt cả 3 van cùng lúc**:

| Van xả thông thường | Tài liệu nói gì |
|---|---|
| Hạ lãi huy động để giữ NIM | Huy động đang căng (LDR 107,7%) → hạ là mất vốn |
| Bù bằng tăng trưởng dư nợ | Room 2027 gắn với mức độ tuân thủ giảm lãi vay |
| Chuyển sang cho vay lợi suất cao | "Kiểm soát lĩnh vực tiềm ẩn rủi ro" + thanh tra BĐS/related party |

Đây là **giả thuyết định tính**, không phải kết luận đã kiểm chứng. Kiểm được bằng: theo dõi NIM
công bố (thuyết minh BCTC Q3/2026, ~cuối 10/2026) so với dải suy ra ở §1b.

### 1d. Cảnh báo cách đọc bảng §1b [VERIFIED]

Công thức `L×Asset/NP` về bản chất là **1/ROA** — nó đo **đệm lợi nhuận trên quy mô tài sản**, KHÔNG
đo cơ cấu vốn. Hai ngân hàng cùng ROA nhưng CASA lệch hẳn nhau sẽ **cùng điểm** ở bảng này, và đó
là sai. Bảng trên trả lời "ai mỏng đệm nhất" chứ **không** trả lời "ai có nguồn vốn rẻ nhất". Câu
sau là [GAP] §1a.

Số liệu nền kèm theo (2026Q2, `ticker_financial`): ROA — HDB 2,04% · MBB 1,91% · ACB 1,54%.
Lợi suất TOI/tài sản niên hoá — HDB 9,06% · MBB 7,85% · ACB 7,52%. Tăng trưởng tài sản YoY —
MBB **+34,4%** · HDB **+33,3%** · ACB **+14,4%**. ROE_TTM Q2/2025→Q2/2026 — ACB **20,2%→16,3%**
(giảm mạnh nhất cả nhóm 11 mã), MBB 20,9%→21,2%, HDB 25,2%→24,6%.

⚠️ `Revenue_P0` với ngân hàng là **TOI** (gồm phí + kinh doanh ngoại hối/chứng khoán), **không phải
thu nhập lãi thuần** — mọi con số "lợi suất" ở trên là lợi suất TOI, KHÔNG được đọc là NIM.

**Ghi chú độc lập, đáng chú ý hơn cả câu hỏi được giao:** MBB và HDB đang tăng tài sản ~34%/năm.
Nếu cơ chế room-2027 ở §2 là thật, hai mã **nặng ký nhất trong rổ 3 mã lại là hai mã phụ thuộc
phân bổ room nhiều nhất** — rủi ro của chúng nghiêng về *khối lượng* (bị cắt room), còn ACB
nghiêng về *biên* (đệm mỏng). Đây là hai loại rủi ro khác nhau, không cộng dồn thành một thứ hạng.
[HYPOTHESIS]

---

## §2. Room tín dụng 2027 làm đòn bẩy tuân thủ — có nên theo dõi định kỳ?

**Đề xuất: CÓ, nhưng KHÔNG mở rộng `deposit-rate-autocheck`.** Lý do kỹ thuật, không phải khẩu vị:

`deposit-rate-autocheck` là cơ chế ghi **một con số** vào chuỗi append-only, có delta-guard 1,0pp,
có gate ≥2 owner-group, có consumer live (`current_deposit_rate()`). Toàn bộ kiến trúc phòng thủ
của nó — quant-skeptic 10 vòng — được xây quanh bất biến "output là 1 số có thể kiểm cơ học".
"Ngân hàng X có bị cắt room không" **không phải một con số** và không có nguồn công bố định kỳ
đáng tin. Nhét vào đó sẽ phá đúng bất biến khiến nó an toàn.

**Đề xuất thay thế, rẻ hơn nhiều:** thêm *một* dòng vào recon hàng quý — chỉ tiêu tăng trưởng tài
sản YoY của rổ ngân hàng, đã có sẵn trong `ticker_financial` (§1d). Room bị cắt sẽ **lộ ra trong
số liệu** dưới dạng tăng trưởng tài sản chậm đột ngột, không cần theo dõi tin tức. MBB +34,4% rơi
về ~+15% là tín hiệu mạnh hơn bất kỳ bản tin nào. Cadence quý (khớp BCTC), không phải tháng.

**KHÔNG đề xuất wire vào filter live.** Đây là chỉ báo giám sát, chưa có backtest, N=0 sự kiện
lịch sử của cơ chế "room gắn tuân thủ lãi suất". [HYPOTHESIS]

---

## §3. Tỷ giá / trần lãi suất ↔ macro gate DT5G

### 3a. Củng cố: Pillar A đang ngủ, và tài liệu giải thích ĐÚNG vì sao [VERIFIED]

Đọc `macro_state_live.py` (dòng 174–215) + `sbv_macro_overlay.SBV_REFI_EVENTS`:

- Pillar A dùng `refi_chg6m = refi(t) − refi(t−126 phiên)`, trễ 5 ngày. Cap kích hoạt khi
  **refi_chg6m ≥ +0,5pp → NEUTRAL · ≥ +1,5 → BEAR · ≥ +3,0 → CRISIS**. Tức Pillar A là **máy dò
  THẮT CHẶT**, chỉ phản ứng khi SBV **TĂNG** lãi suất điều hành.
- `refi_cut` (cắt) chỉ dùng cho nhánh `easing`, mà **`EASING_FLOOR_ENABLED = False`** từ
  2026-06-03. Cắt lãi suất **không** làm gì cả.
- Mốc refi cuối cùng: **2023-06-19 @ 4,5%** — phẳng **1.151 ngày**. `refi_chg6m = 0` ⇒ `cap = 9`
  (không cap). Hôm nay `state = 3` (NEUTRAL), khớp `golive_v23_status.json`.

Tài liệu nói "dư địa nới lỏng rất hạn chế", tỷ giá là ràng buộc ⇒ **nhất quán hoàn toàn** với thiết
kế bất đối xứng của gate: không có gì để gate phản ứng khi SBV đứng yên, và nếu SBV buộc phải tăng
vì tỷ giá thì Pillar A đã sẵn sàng đúng ngưỡng đó. **Không mâu thuẫn.**

### 3b. Nhưng có một điểm mù thật, tài liệu này chỉ thẳng vào nó [HYPOTHESIS]

Pillar A chỉ nhìn **lãi suất tái cấp vốn — giá hành chính**. Toàn bộ sự thắt chặt mà tài liệu mô
tả (LDR 107,7% · chênh tín dụng-huy động 2 triệu tỷ · vốn TDH 16% nguồn vs 48,5% dư nợ) là thắt
chặt **lượng và giá thị trường** — nó có thể đẩy lãi suất huy động/cho vay thực tế lên **mà không
bao giờ chạm mốc refi 4,5%**. Trường hợp đó `refi_chg6m` đứng yên ở 0 và **DT5G hoàn toàn mù**.

Đây không phải lỗi thiết kế: DT5G được thiết kế là bảo hiểm dựa trên **GIÁ** (base v3.4b), và
thắt chặt thị trường rốt cuộc sẽ hiện ra trong giá VNINDEX → base bắt được. Điểm mù chỉ ở lớp
*cảnh báo sớm* của macro cap.

**KHÔNG đề xuất đổi gì trong DT5G.** Tham số đang ở vùng bình ổn, CLAUDE.md cấm re-tune theo lịch
sử, và toàn bộ edge ròng của DT5G đến từ một lần siết 2023. Thêm "Pillar A′ theo lãi suất huy
động" đã từng được pre-register (`Taylor_20260713_124803`) và **vướng caveat (b)** của
`deposit_rate_vn`: 26 mốc lịch sử neo hồi tố cùng một ngày 2026-06-19 ⇒ mọi backtest trên đó mang
bias hindsight, **không chứng minh được gì**. Chuỗi point-in-time thật mới có **1 mốc**
(2026-07-20, 6,8%). Kết luận: **chưa đủ dữ liệu để nghiên cứu, chứ không phải đã bác bỏ.**

---

## §4. Funding gap 2 triệu tỷ / LDR 107,7% → hướng lãi suất huy động

### 4a. Hàm ý định tính [HYPOTHESIS]

Chênh tín dụng−huy động 2 triệu tỷ, LDR hệ thống 107,7% (VND 110,6%), vốn TDH 16% nguồn tài trợ
48,5% dư nợ TDH — ba con số cùng chỉ một hướng: **áp lực lãi suất huy động là LÊN, không xuống.**
NHNN tự thừa nhận điều này trong tài liệu. Ràng buộc thanh tra "cạnh tranh huy động không lành
mạnh" chỉ giới hạn *tốc độ*, không đảo *chiều*.

Không kiểm chứng được bằng dữ liệu hiện có: chuỗi point-in-time thật chỉ có 1 mốc (§3b). Đây là
**hypothesis chưa kiểm chứng.**

### 4b. Phát hiện đáng kể — cổng deposit-tilt KHÔNG chạm rổ ngân hàng [VERIFIED]

Truy `rating_8l.py:858-870`: deposit tilt (`±0.03` lên `value_score_v3`, hurdle `1/PE(%) −
deposit(%) ≥ 3pp`) chỉ áp cho `val_route ∈ {COMPOUNDER, CYCLICAL, RETAIL}`.

Đối chiếu artifact production `data/rating_8l_screener.csv`: **cả 8 mã ngân hàng kiểm tra
(CTG/VPB/BID/VCB/MBB/ACB/HDB/TCB) đều mang `val_route = "BANK"`** — không nằm trong danh sách áp
tilt. Khớp comment code dòng 820 ("financials keep v2, never use PS").

**⇒ Nếu lãi suất huy động tăng, kênh truyền dẫn duy nhất đang wire (deposit tilt) siết vào ~33%
danh mục phi ngân hàng, và KHÔNG chạm 67% rổ ngân hàng — đúng chỗ câu chuyện lãi suất thực sự
tác động.** Tilt cũng chỉ sống ở NEUTRAL (hôm nay `state=3`, đang sống).

Đây là **quan sát cơ chế đã verify**, KHÔNG phải đề xuất sửa. Việc banks dùng v2 (không PS) là
quyết định có chủ đích và đúng — PS vô nghĩa với ngân hàng. Vấn đề là hệ quả *phụ*: rổ lớn nhất
book không có kênh phản ứng lãi suất nào ở tầng rating. Có nên có hay không là câu hỏi R&D riêng,
cần backtest + quant-skeptic, **không kết luận trong job này.**

---

## §5. Việc mở / đề xuất bước tiếp (không tự làm)

| # | Việc | Giao ai | Chặn bởi |
|---|---|---|---|
| 1 | Xác nhận **ngày** tài liệu họp | user | — |
| 2 | Nguồn CASA/LDR/vốn TDH từ thuyết minh BCTC — đóng [GAP] §1a | Winston (data-ops) | cần dispatch riêng |
| 3 | Theo dõi tăng trưởng tài sản YoY rổ ngân hàng theo quý (§2) | Taylor, cadence quý | user duyệt cadence |
| 4 | Kiểm dải §1b bằng NIM công bố BCTC Q3/2026 | Taylor | ~cuối 10/2026 |
| 5 | Pillar A′ theo lãi suất huy động | — | **chặn dữ liệu**, PIT thật n=1, đợi ≥12–24 mốc |

## §6. Tuyên bố giới hạn

Đầu vào chính là **ghi chú họp định tính không ngày tháng**. Trong tài liệu này chỉ có §0, §1b,
§1d, §3a, §4b là **[VERIFIED]** (đo từ BQ / code production / artifact live, tái lập được bằng
truy vấn ghi trong job). §1c, §2, §3b, §4a là **[HYPOTHESIS]** — suy luận định tính, chưa kiểm
chứng, **không được trích như finding**. §1a là **[GAP]** đã tuyên bố.

**KHÔNG chạm production. KHÔNG đề xuất đổi config live. Không cần quant-skeptic** (đúng ranh giới
dispatch). Nếu bất kỳ mục nào ở §5 tiến tới đề xuất wire, khi đó mới bắt buộc qua gate đầy đủ.

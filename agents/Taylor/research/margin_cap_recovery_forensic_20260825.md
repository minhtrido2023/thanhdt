# Trần margin sleeve Loại-2 + forensic entry sớm khi DT5G thoát khủng hoảng
> **RESYNC 2026-08-30** (job `Taylor_20260830_045349`, `decided_by: user`): chính sách đơn mã
> (`discretionary-margin-policy-20260823.md`) vừa nâng **sleeve cap TỔNG của sleeve đơn mã** từ
> 5%→10% NAV exposure — số này KHÁC số Loại-2 dưới đây (portfolio-level, ≤5% NAV **vốn tự có** /
> ≤6,5% NAV exposure ở f=1,3). Theo re-sync 08-29 đã ghi trong chính sách gốc, Loại-2 KHÔNG tự
> động kế thừa thay đổi của sleeve đơn mã — số Phần A dưới GIỮ NGUYÊN, cảnh báo lỗi công thức A5
> (equity_cap vs exposure_cap, đã sửa 08-29: max loss thật 1,3% NAV không phải 1,0%) vẫn còn hiệu
> lực nguyên văn. Đổi số Loại-2 cần một vòng risk-auditor + user riêng.
>
> Job `Taylor_20260825_113846` · 2026-08-25 · **RESEARCH-ONLY, KHÔNG wire, KHÔNG sửa code/config.**
> Mandate (anh John): số `≤3%/mã · ≤5%/sleeve` trong `crisis_margin_framework_adaptive_20260825.md`
> Phần 3(c) là **mượn từ chính sách đơn mã** (`discretionary-margin-policy-20260823.md`, N=1-2
> mã discretionary) — chưa có cơ sở riêng cho sleeve washout PORTFOLIO-LEVEL. Job này tìm cơ sở
> đúng (Phần A) + forensic một hướng mở khác: vào muộn hơn, tại điểm DT5G xác nhận thoát khủng
> hoảng thay vì tại đáy (Phần B).

## Nguồn đã dùng
- `crisis_margin_framework_adaptive_20260825.md` (toàn bộ — Phần 1/2/3).
- `kb/projects/margin-valuation-spread-20260823.md` (Phase 1 + đính chính trục CONTAINABLE).
- `kb/projects/discretionary-margin-policy-20260823.md` (chính sách đơn mã, nguồn số cũ bị John chỉ ra).
- `kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` — số margin gói 1840 THẬT,
  verified LIVE 2026-08-23 (job `Mafee_20260823_083327`): `initialRate=0.5, maintenanceRate=0.4,
  liquidRate=0.3, interestRate=0.125`.
- `data/VNINDEX.csv` (registry `kb/data_registry/research-caches/vnindex_csv.md`, RESEARCH, frozen
  2026-06-16 — đủ phủ mọi episode dùng trong job này, 2012→2023).
- `data/vnindex_5state_dt5g_live.csv` (bản local công bố của `tav2_bq.vnindex_5state_dt5g_live`,
  registry `kb/data_registry/market-state/vnindex_5state_dt5g_live.md`, CANONICAL) — state map xác
  nhận từ `dna_report.py:28-29`: `{1:CRISIS, 2:BEAR, 3:NEUTRAL, 4:BULL, 5:EX-BULL}`.
- Không dùng BQ trực tiếp trong job này — cả 2 CSV local đã CANONICAL/đủ phủ, tránh phí BQ không
  cần thiết (đúng §9 coding_guidelines: tra registry trước khi chọn nguồn).
- Không backtest tối ưu hoá, không DSR/PBO — forensic + so sánh mô tả, đúng chỉ đạo (N quá nhỏ).

---

## PHẦN A — Cơ sở trần margin cho sleeve Loại-2

### A1. Thông số RocketX gói 1840 — THẬT, không phải proxy
Đã có sẵn, verified LIVE (không cần đoán ngưỡng VN chuẩn):
`initialRate=0,50 (ký quỹ ban đầu) · maintenanceRate=0,40 (duy trì) · liquidRate=0,30 (xử lý bắt
buộc) · interestRate=0,125 (lãi vay/năm)`.

**Hệ số `f=1,3` của `capit_margin_lever`** (hằng số CỐ ĐỊNH, xác nhận qua
`capit_lever_selfcheck.py`) — vốn tự có = 1/f ≈ **76,9%** giá trị vị thế, thấp hơn NHIỀU mức đòn
bẩy tối đa broker cho phép (`initialRate=0,5` ⇒ f tối đa = 2,0, vốn tự có tối thiểu 50%). Đây là
điểm mấu chốt cho toàn bộ Phần A: **`capit_margin_lever` đã tự chọn đòn bẩy BẢO THỦ hơn nhiều mức
sàn broker cho phép**, trong khi chính sách đơn mã (`discretionary-margin-policy-20260823.md`)
tính exposure từ **f=2,0** ("đòn bẩy gói 1840 (initial 50%) → exposure tối đa ≈2,0% NAV" từ vốn
1,0% NAV). Hai chính sách đang neo vào 2 mức đòn bẩy KHÁC NHAU — số ≤3%/≤5% NAV không chỉ mượn
context (đơn mã vs sleeve), mà còn ngầm mượn **f=2,0** trong khi engine sleeve dùng **f=1,3**.

### A2 + A3. Drawdown thật + margin survival tại 3 điểm vào

Công thức (đúng yêu cầu dispatch, verify khớp bằng nghiệm đảo): tỷ lệ ký quỹ hiện tại (equity/vị
thế) tại drawdown `d` (từ giá lúc arm) với hệ số `f`:
`equity_ratio(d) = [f(1+d) − (f−1)] / [f(1+d)]`. Ngưỡng phá vỡ (đảo công thức):
`d_break = (f−1)/(f·(1−target)) − 1`.

| f | Ngưỡng maintenance (40%) chạm ở | Ngưỡng liquidation (30%) chạm ở |
|---|---|---|
| **1,3 (capit_margin_lever thật)** | **−61,5%** | **−67,0%** |
| 2,0 (giả định ẩn trong số cũ, đơn mã max leverage) | −16,7% | −28,6% |

Đo drawdown thật (VNINDEX, BQ-tương đương từ `data/VNINDEX.csv`, cửa sổ 60 phiên từ ngày vào):

| Episode | Ngày vào | Close ngày vào | max DD 60 phiên | Ngày đáy | equity_ratio tại đáy (f=1,3) | Chạm maintenance? | Chạm liquidation? |
|---|---|---|---|---|---|---|---|
| 2020-03 (arm thật E7) | 2020-03-11 | 811,35 | **−18,75%** | 2020-03-24 (+9 phiên) | 71,6% | KHÔNG | KHÔNG |
| 2022-11 (counterfactual đề xuất) | 2022-11-15 | 911,90 | **0,00%** (đúng đáy) | — | 76,9% | KHÔNG | KHÔNG |
| 2018-05 (arm thật E4, counter-example) | 2018-05-28 | 931,75 | **−4,14%** | 2018-07-11 (+32 phiên) | 75,9% | KHÔNG | KHÔNG |

**Kết luận A2+A3: ở f=1,3, margin call KHÔNG PHẢI ràng buộc thật trong cả 3 episode** — drawdown
tệ nhất quan sát được (−18,75%, COVID) còn cách ngưỡng maintenance tới **~43 điểm phần trăm**. Kể
cả nếu dùng đúng mức đòn bẩy tối đa broker cho phép (f=2,0, KHÔNG phải f thật của engine), −18,75%
vẫn chưa chạm maintenance (−16,7%) — sát nhưng chưa chạm; ở f=1,3 nó không hề gần.

### A4. Correlation load — định tính

Khi Loại-2 fire: V2.4 hệ thống (BAL+LAG) đang ở allocation BEAR/CRISIS (`w_LAG`: CRISIS 50/BEAR 0,
và cả 2 book đã tự giảm equity weight theo state) — tức NAV đã **dưới mức đầu tư bình thường**
trước khi sleeve margin cộng thêm vào. Nhưng sleeve washout basket-wide **tương quan CAO** với
chính book hệ thống (cả hai cùng đặt cược VNIndex hồi phục, không như 2 case đơn mã độc lập của
chính sách cũ — due-diligence 2 mã khác nhau có thể đúng/sai độc lập, còn 1 basket-wide bet chỉ có
1 kết quả: thị trường hồi hay không). **Đây là khác biệt CHẤT về rủi ro, không chỉ về quy mô** — lý
do chính đáng để KHÔNG đơn giản nhân đôi số đơn mã cho sleeve portfolio-level, dù margin math (A2+
A3) không phải điểm nghẽn.

### A5. Đề xuất trần — và vì sao KHÔNG dùng margin-survival làm cơ sở

**Phát hiện quan trọng nhất của Phần A: margin call không phải ràng buộc thật ở f=1,3 (cách xa
episode tệ nhất tới ~43pp) — số cũ `≤5% NAV/sleeve` trong chính sách đơn mã CŨNG không thật sự
được suy từ margin math** (đọc lại `discretionary-margin-policy-20260823.md`: 5% = trực tiếp
"≤2 case song song" × 1% vốn/case đơn mã — một phép nhân cơ học, không phải giới hạn margin-
survival độc lập). Vì vậy câu hỏi đúng KHÔNG PHẢI "margin cho phép bao nhiêu" (câu trả lời: rất
nhiều, ở f=1,3) mà là **"NAV chịu được lỗ bao nhiêu nếu lần escalate này SAI"** — đây mới là ràng
buộc thật, và nó neo được vào kỷ luật thoát đã user duyệt sẵn (−20% từ giá arm, Phần 3(d) framework
+ chính sách đơn mã).

**Neo tính**: lỗ thực nhận tối đa TRƯỚC khi kỷ luật −20% kích hoạt buộc de-lever ≈
`exposure_cap × 20%` (**SỬA 2026-08-29, `decided_by: user`, xem
`agents/Taylor/research/discretionary_margin_sizing_20260829.md` §1** — bản gốc viết nhầm
`equity_cap × 20%`; biến động giá dồn hết vào vốn tự có khi nợ VND tuyệt đối không đổi, nên công
thức đúng luôn nhân theo EXPOSURE bất kể f: `equity_loss(d) = exposure_0 × |d|`, chứng minh bằng
đảo `equity_ratio(d) = [f(1+d)-(f-1)]/[f(1+d)]`). Muốn giới hạn lỗ 1 lần escalate sai ở mức
**≤1,0% NAV tính trên EXPOSURE** (ngưỡng rủi ro đơn sự kiện hợp lý, cùng bậc với trần đơn mã ≤1,0%
NAV vốn tự có đã duyệt) ⇒ với f=1,3: `exposure_cap ≤ 5% NAV` sẽ cho max loss = 5%×20%=1,0% NAV —
NHƯNG cách viết gốc bên dưới lại đặt **equity**_cap=5% NAV (không phải exposure_cap=5%), nên
exposure_cap thật = 5%×1,3=6,5% NAV và max loss thật = 6,5%×20%=**1,3% NAV**, cao hơn 30% so với
số 1,0% công bố gốc. Giữ nguyên số equity_cap=5%/exposure_cap=6,5% NAV (đã đúng, không đổi), chỉ
sửa lại con số MAX LOSS công bố từ 1,0%→1,3% NAV.

- **Trần equity SLEEVE TỔNG: ≤5% NAV vốn tự có** (GIỮ số cũ — không đổi bởi bản sửa này, chỉ sửa
  số max-loss suy ra từ nó).
- **Trần EXPOSURE tương ứng (làm rõ điểm MƠ HỒ trong bản cũ — văn bản cũ không phân biệt equity
  cap và exposure cap)**: ở f=1,3, exposure = 5% × 1,3 = **≤6,5% NAV** (KHÔNG phải ≤5% NAV exposure
  như câu chữ cũ có thể bị đọc nhầm — 5% là VỐN TỰ CÓ, exposure luôn cao hơn theo f).
- **Max loss thật tại exit −20%: 1,3% NAV** (= exposure_cap 6,5%×20% — **SỬA từ 1,0% NAV**, xem
  đính chính công thức trên. 1,0% NAV chỉ đúng nếu equity_cap≡exposure_cap, tức f=1).
- **Trần đơn mã (nếu chọn từng mã trong basket thay vì cả basket)**: giữ nguyên ≤1,0% NAV vốn tự có
  / ≤3% NAV exposure của chính sách đơn mã 08-23 KHÔNG ĐỔI bởi bản sửa này — **⚠️ nhưng chính sách
  đơn mã đã đổi per-name lên ≤5% NAV exposure ngày 2026-08-29** (`kb/projects/discretionary-margin-
  policy-20260823.md`, `decided_by: user`); số 1%/3% ở đây là NEO CŨ giữ nguyên có chủ đích (Loại-2
  chưa được risk-auditor/user duyệt lại theo per-name mới) — KHÔNG suy diễn rằng Loại-2 tự động
  theo per-name 5% mới. John chỉ chất vấn số SLEEVE TỔNG lúc job này chạy (08-25), không chất vấn
  số đơn mã.
- **So với số cũ**: trần equity giữ NGUYÊN giá trị (≤5% NAV) nhưng lý luận đã ĐÚNG bối cảnh; trần
  exposure được làm RÕ (≤6,5% NAV, cao hơn cách đọc cũ ≤5% NAV exposure nếu ai từng hiểu vậy) vì
  f thật của sleeve (1,3) thấp hơn giả định ẩn cũ (2,0) — margin math dư sức, không phải điểm bó buộc.
- Margin call của broker **vẫn KHÔNG phải lưới an toàn** (netting cấp account, đã ghi ở chính sách
  cũ) — kỷ luật −20% vẫn là cơ chế thoát DUY NHẤT, không đổi.

---

## PHẦN B — Forensic: vào muộn hơn tại điểm DT5G thoát khủng hoảng

### B1. Ngày DT5G thoát CRISIS/BEAR — đo trực tiếp `vnindex_5state_dt5g_live` (2014+, state map
`{1:CRISIS,2:BEAR,3:NEUTRAL,4:BULL,5:EX-BULL}`, xác nhận từ `dna_report.py`)

⚠️ **2012 KHÔNG có dữ liệu DT5G** — bảng chỉ bắt đầu 2014-01-02 (đúng giới hạn đã ghi trong Phần 1/2
framework: "cửa sổ audit `engine_p1.py` chỉ từ 2014"). Dùng proxy kỹ thuật thay thế, gắn nhãn RÕ
KHÔNG PHẢI DT5G (§4 dưới).

Các transition CRISIS→BEAR/NEUTRAL và BEAR→NEUTRAL liên quan 3 episode:
- **2020 (COVID)**: `CRISIS → NEUTRAL` ngày **2020-05-27** (nhảy thẳng, bỏ qua BEAR).
- **2022-2023 (SCB)**: `CRISIS → BEAR` ngày **2022-12-14**, rồi `BEAR → NEUTRAL` ngày **2023-04-12**
  (2 bước, đo cả hai).

### B2+B3. So sánh washout entry (Phần A / episode thật) vs recovery entry (DT5G exit)

| Episode | Kiểu vào | Ngày | Close vào | max DD 60 phiên | D+30 | D+60 | D+120 | D+252 |
|---|---|---|---|---|---|---|---|---|
| **2012** | Washout (đáy 2012-11-02, mechanism-classifier) | 2012-11-02 | 375,26 | 0,00% | +4,5% | +29,0% | +30,1% | **+33,2%** |
| 2012 | Recovery **proxy kỹ thuật** (10 phiên liên tục Close>MA50, KHÔNG PHẢI DT5G — bảng chưa phủ) | 2012-12-24 | — | 0,00% | +22,2% | +22,9% | +18,3% | **+26,7%** |
| **2020** | Washout (arm E7) | 2020-03-11 | 811,35 | **−18,75%** | −4,6% | +10,9% | +8,7% | **+45,6%** |
| 2020 | Recovery DT5G (CRISIS→NEUTRAL) | 2020-05-27 | 857,48 | **−8,43%** | +0,8% | −0,7% | +11,9% | **+54,0%** |
| **2022-23** | Washout (counterfactual arm) | 2022-11-15 | 911,90 | 0,00% | +10,2% | +15,0% | +16,9% | **+20,8%** |
| 2022-23 | Recovery DT5G (CRISIS→BEAR) | 2022-12-14 | 1050,43 | −6,21% | +2,6% | −0,3% | +6,9% | **+4,0%** |
| 2022-23 | Recovery DT5G (BEAR→NEUTRAL, xác nhận đầy đủ) | 2023-04-12 | 1069,45 | −3,24% | +0,5% | +7,4% | +5,5% | **+13,8%** |

**Đọc bảng — KHÔNG đồng nhất một chiều, N=3 quá nhỏ để kết luận chung:**
1. **2012 & 2022-23: washout entry THẮNG recovery entry cả về return LẪN drawdown-đã-nhận** (2012:
   +33,2% vs +26,7%; 2022-23 vs BEAR→NEUTRAL: +20,8% vs +13,8%; vs CRISIS→BEAR càng tệ hơn: +4,0%).
   Đợi xác nhận DT5G ở 2 ca này **KHÔNG giảm rủi ro có ý nghĩa** (2012 cả hai đều DD=0% vì đáy đã
   qua; 2022-23 washout DD=0% ngay tại đáy) mà chỉ **BỎ LỠ phần hồi phục sớm nhất, mạnh nhất**.
2. **2020 (COVID) là ngoại lệ — recovery entry KHÔNG hy sinh return (thậm chí D+252 cao hơn: +54,0%
   vs +45,6%) VÀ giảm drawdown-đã-nhận đáng kể (−8,4% vs −18,75%).** Nhưng đây là **so sánh 2 cửa
   sổ 252-phiên bắt đầu KHÁC ngày lịch** (11/3 vs 27/5, cách nhau ~2,5 tháng) — cả hai đều cưỡi
   cùng một sóng tăng 2020-2021, cửa sổ sau kết thúc muộn hơn vào đúng giai đoạn EX-BULL cuối 2020/
   đầu 2021 mạnh hơn. **Đây RẤT có thể là hiệu ứng CỬA SỔ (window effect), không phải bằng chứng
   "đợi xác nhận không mất edge"** — hai con số D+252 không đo cùng một khoảng thời gian lịch, nên
   không phải phép so sánh edge công bằng như nó nhìn có vẻ.
3. **Không có case nào trong 3 case cho thấy đợi DT5G xác nhận làm margin call risk giảm CÓ Ý
   NGHĨA** — Phần A đã chứng minh margin call không phải ràng buộc ở CẢ HAI kiểu vào (equity_ratio
   luôn ở vùng 70-77%, cách maintenance 40% rất xa dù vào ở đáy hay vào muộn).

### B4. Kết luận định hướng

**KHÔNG đề xuất mở job nghiên cứu riêng cho recovery-entry.** Ba lý do:
1. **Động cơ ban đầu của hướng này (Phần A) đã bị bác — margin survival không phải vấn đề ở f=1,3**
   dù vào tại đáy hay vào muộn. Recovery-entry không giải quyết một rủi ro THẬT nào mà washout-entry
   đang gánh (đã đo: cách margin call ~43-58pp ở CẢ HAI kiểu vào).
2. **2/3 episode có bằng chứng cho thấy đợi xác nhận TỐN THẬT** (mất 6,5-16,8pp return D+252, không
   giảm drawdown vì đáy washout-entry vốn đã là DD=0%) — chi phí cơ hội đo được, không giả định.
3. **Case duy nhất "ủng hộ" đợi xác nhận (2020) mang khiếm khuyết đo lường đã tự khai** (window
   effect khác ngày kết thúc) — không đủ tin cậy để làm cơ sở mở nghiên cứu mới, và N=1 case sạch
   (COVID là cú sốc ngoại sinh V-shape, không đại diện cho 2012/2022 kiểu khác cơ chế — đúng tinh
   thần đa cơ chế đã ghi trong `margin-valuation-spread-20260823.md` §đính chính).

**Washout entry (đáy, đúng logic Phần A/framework hiện tại) đã cover phần lớn edge quan sát được**
— không có tín hiệu đủ mạnh để đánh đổi lấy độ phức tạp của một nhánh vào-muộn mới.

---

## Giới hạn phải mang theo
1. N=3 (Phần A) / N=3 (Phần B, thực chất 2012 dùng proxy không phải DT5G) — **forensic mô tả**,
   không phải kiểm định thống kê, đúng chỉ đạo dispatch.
2. Trần A5 là **đề xuất lý luận lại**, chưa qua risk-auditor/user xác nhận chính thức — KHÔNG coi
   là đã chốt, giống hệt tình trạng số cũ nó thay thế.
3. 2012 recovery-entry dùng proxy kỹ thuật (Close>MA50 bền 10 phiên) — KHÔNG PHẢI DT5G thật (bảng
   không phủ trước 2014), chỉ dùng để có 1 điểm tham chiếu định tính, không nên trích dẫn như bằng
   chứng DT5G.
4. `data/VNINDEX.csv` đóng băng 2026-06-16 (đủ phủ mọi episode job này dùng, 2012-2023) — KHÔNG
   dùng file này cho phân tích cần dữ liệu SAU 06-2026.

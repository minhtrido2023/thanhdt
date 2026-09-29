# ORB VN30F — nghiên cứu CHẨN ĐOÁN "vì sao performance suy giảm"
Job `Taylor_20260925_122513` · VIỆC 2 · 2026-09-25 · PAPER-ONLY

Dữ liệu: tape ghép 1.129 trade 2022-02-17→2026-09-25 (FiinProX 389 phiên + vnstock 745 phiên,
`../orb_fiinx_vn30f1m_20260925/orb_trades_extended_20220217_20260925.csv`) + VN30 spot daily
OHLCV từ `tav2_bq.ticker` (2021-06→2026-09). Script: `seg.py`, `diag2..7.py`. Chạy bằng `$DNA_PYEXE`.

---

## KẾT LUẬN CHÍNH — câu hỏi "vì sao suy giảm" có tiền đề SAI

**Không có suy giảm nào phát hiện được về mặt thống kê. Không có gì để giải thích.**

Hai kiểm định, cả hai đều đã hiệu chỉnh cho việc ĐI TÌM (đây là điểm mấu chốt — mọi đoạn xấu đều
"có ý nghĩa" nếu bạn chọn nó VÌ nó xấu):

| Kiểm định | Kết quả | p |
|---|---|---|
| **sup-Wald điểm gãy** (quét mọi breakpoint có ≥100 obs mỗi bên, null bằng hoán vị 5.000 lần) | điểm gãy mạnh nhất là **2025-06-19** (+2,86→+14,81bps, tức CẢI THIỆN), \|t\|max=1,690 vs 95pct null 2,955 | **0,666** |
| **"Đoạn 177 phiên tệ nhất"** — chuỗi iid cùng mean/sd sinh ra đoạn xấu cỡ nào? | null: đoạn tệ nhất TB **−10,32bps** CI[−17,5;−4,5]; quan sát 2023-01..09 = **−12,30bps** | **0,286** |

Một chuỗi 1.129 phiên với mean +6,16bps và sd 110bps **được kỳ vọng** sinh ra một đoạn ~177 phiên
lỗ ~−10bps/phiên. Đoạn 2023-01..09 (−12,30bps, cụm −19,7%, MaxDD −30,47%) nằm gọn trong phân phối
đó. Không cần "regime đổi", không cần sự kiện cấu trúc, không cần cơ chế nào biến mất.

⚠️ Hệ quả về quy trình: đoạn 2023 được CHỌN vì nó là drawdown sâu nhất. Mọi p-value tính TRÊN đoạn
đã chọn (kể cả p=0,013 ở §a dưới) đều KHÔNG hợp lệ như bằng chứng. Chỉ hai con số trong bảng trên
là đã hiệu chỉnh selection.

---

## (a) Đoạn 2023-01..09 KHÁC gì? — mô tả được, nhưng không quy nạp được

Đo trên tape (`segment_stats.csv`) và VN30 spot (độc lập với tape phái sinh):

| | 2022-02..12 | **2023-01..09 (LỖ)** | 2023-10..2024-12 | 2025-01..2026-09 |
|---|---|---|---|---|
| n phiên | 221 | **177** | 310 | 421 |
| net TB (bps) | +10,28 | **−12,30** | +6,08 | +11,83 |
| Sharpe năm | 1,01 | **−1,93** | 1,21 | 1,88 |
| **P(đúng chiều)** | 55,20% | **43,50%** | 53,23% | 53,92% |
| biên độ \|gross\| TB | 1,041% | **0,697%** | 0,569% | 0,706% |
| payoff (lãi TB / lỗ TB) | 1,033 | **0,976** | 1,179 | 1,262 |
| \|OR\| TB (bps) | 29,8 | **18,9** | 17,4 | 27,6 |
| MFE TB | 1,068% | **0,605%** | 0,606% | 0,810% |
| MAE TB | 0,829% | **0,642%** | 0,515% | 0,632% |
| — VN30 spot — realized vol 20p | 24,4% | **16,6%** | 15,3% | 19,1% |
| — biên độ ngày spot | 2,005% | **1,340%** | 1,235% | 1,619% |
| — % ngày TREND (đóng ở cực trị) | 53,5% | **58,2%** | 49,5% | 50,0% |
| — gap qua đêm TB (bps) | 43,6 | **24,8** | 21,2 | 38,4 |
| — basis F−S TB (bps) | −51,1 | **−32,1** | +2,2 | −8,0 |
| — KLGD VN30 (triệu) | 163,7 | **189,8** | 215,6 | 372,7 |
| — VN30 spot lãi trong đoạn | −34,8% | **+11,4%** | +15,2% | +44,3% |

**Phân rã cơ học**: khoản lỗ đến HOÀN TOÀN từ **độ chính xác về CHIỀU**, không từ biên độ.
- P(đúng chiều) 43,50% vs 53,99% phần còn lại — χ² p=0,013 *(p này KHÔNG hợp lệ, đoạn đã bị chọn)*.
- Biên độ \|gross\| 0,697% vs 0,739% — Welch **p=0,491**, KHÔNG khác nhau.
- MAE giữ nguyên (0,642% vs 0,640%) trong khi MFE sụt (0,605% vs 0,803%): lệnh vẫn bị đánh ngược
  y như mọi khi, nhưng khi đúng thì không đi xa nữa.

**Đặc điểm thị trường**: đoạn lỗ là đoạn **vol thấp, biên độ hẹp, gap qua đêm nhỏ nhất mẫu, nhưng
thị trường vẫn TĂNG +11,4%** — tức grind đi lên, không phải khủng hoảng. Thanh khoản KHÔNG cạn
(189,8tr > 163,7tr của 2022). Basis discount thu hẹp so với 2022.

**Nhưng mô tả không phải giải thích.** Mỗi đặc điểm ở trên đều bị bác khi kiểm trên toàn mẫu:
- Vol thấp: toàn mẫu ORB chạy **TỐT HƠN** ở vol thấp (Q1 rv20=9,7% → +9,13bps Sharpe 1,95; Q5
  rv20=33,2% → −0,70bps). Đoạn lỗ lại là đoạn vol thấp ⇒ vol **không** giải thích được nó.
- % ngày TREND: đoạn lỗ có tỷ lệ ngày-trend CAO NHẤT (58,2%) mà vẫn lỗ ⇒ "thiếu ngày trend" sai.
  Ngày vẫn đóng ở cực trị — chỉ là **cực trị NGƯỢC chiều 30 phút đầu**.
- Basis, thanh khoản, gap: không có quan hệ đơn điệu (xem §c).

⇒ Mô tả đúng nhất, không vượt quá dữ liệu: **2023 là giai đoạn "mở một đằng, đóng một nẻo" — thị
trường vẫn trending trong ngày nhưng dấu 30 phút đầu không còn chỉ đúng hướng.** Không phân biệt
được với việc một biến ~50/50 rơi vào chuỗi mặt sấp.

---

## (b) Bộ lọc |OR|≥0,2% "đảo dấu" — đây là NHIỄU, đã đo được

Đo trực tiếp: trượt **mọi cửa sổ 74 phiên liên tiếp** trong 1.129 trade (1.056 cửa sổ), tính
delta = (net TB trong-lọc) − (net TB ngoài-lọc):

- delta TB **−0,75bps**, sd **29,24bps**, min −58,6, max **+117,7** — biên độ khổng lồ.
- Cửa sổ live quan sát delta = −17,29 − 31,06 = **−48,35bps** → nằm ở **phân vị 3,8%**;
  P(\|delta\| ≥ 48,35) = **9,7%**.
- Tỷ lệ cửa sổ có Welch **p≤0,028** = **3,7%**. Dưới giả thuyết KHÔNG có hiệu ứng, kỳ vọng 2,8%.
  Quan sát 3,7%. **Không phân biệt được.**
- Theo năm, delta (trong−ngoài) bps: 2022 **−15,0** · 2023 **+2,5** · 2024 **−5,8** · 2025 **+23,9**
  · 2026 **−21,5** → **đổi dấu 4/4 lần chuyển tiếp năm**, không năm nào p<0,05 (tốt nhất p=0,088).
- Toàn mẫu Spearman(\|OR\|, net) rho=**+0,042 p=0,162**. Ngũ phân vị \|OR\| **không đơn điệu**:
  Q1 +2,0 · Q2 +0,9 · Q3 **+16,2** · Q4 **−0,1** · Q5 +11,9 bps.

**Cơ chế? Không có cơ chế nào cần tới.** Câu "vì sao quan hệ đảo dấu" giả định có một quan hệ để
đảo. Dữ liệu nói: chưa từng có quan hệ nào được thiết lập. p=0,028 trên 74 phiên là **một lần rút
từ phân phối có sd 29bps**, đúng tần suất mà nhiễu sinh ra.

Về độ tin cậy thật của p=0,028: nó là p THÔ, và bộ lọc |OR| là **một trong ~20 cấu hình** đã thử
trong chương trình này (đúng N_trials=20 dùng cho DSR). Hiệu chỉnh Bonferroni thô: 0,028×20=0,56.
Hiệu chỉnh bằng phân phối thực nghiệm ở trên: p≈0,10 (hai phía). **Không có ý nghĩa dưới mọi cách
hiệu chỉnh.**

Nếu VẪN muốn một câu chuyện kinh tế cho |OR| lớn (để biết cái gì cần bác): |OR| lớn = tin qua đêm
mạnh / gap / sổ lệnh mỏng lúc mở cửa. Hai lực NGƯỢC nhau — (i) thông tin thật → giá tiếp tục chạy
(momentum), (ii) mất cân đối lệnh tạm thời trên sổ mỏng → giá hồi (mean reversion). Tỷ lệ 2 lực này
đổi theo bản chất tin ⇒ **kỳ vọng tiên nghiệm cho hệ số là ~0**, và đó đúng là cái đo được. Nói cách
khác: kết quả null ở đây **khớp với lý thuyết**, không phải thất bại của phép đo.

---

## (c) Có cơ chế kinh tế cho edge của dấu OR trên VN30F không? — **KHÔNG TÌM ĐƯỢC. NÓI THẲNG.**

Trước hết, phân rã edge toàn mẫu (n=1.129, `diag5.py`):

```
E[gross] = +8,25bps
  (i) thành phần ĐỐI XỨNG PAYOFF (giả sử P=50%):        +4,82bps   bootstrap CI95 [−0,08; +9,65], P(≤0)=0,027
  (ii) thành phần DỰ BÁO CHIỀU (P−50%)×(W−L):           +3,43bps   P=52,35%, CI95 [49,39%; 55,30%]
  phí:                                                   −2,08bps
E[net] = +6,16bps
```

- **P(đúng chiều) = 52,35%, CI95 [49,39%; 55,30%] — KHÔNG loại được đồng xu (p=0,115).** Sau 4,6 năm
  và 1.129 phiên, giả thuyết "dấu OR không chứa thông tin gì về chiều cả ngày" vẫn đứng vững.
- Nếu P **đúng bằng 50%**, chiến lược vẫn +2,74bps/phiên nhờ payoff bất đối xứng (lãi TB 0,778% vs
  lỗ TB 0,682%, tỷ lệ 1,141) — nhưng bootstrap CI của chính thành phần này **chạm 0** ([−0,08;+9,65]).

Tức là: **cả hai nguồn P&L đều dưới 2 sigma.** Không có một nguồn nào đủ mạnh để làm điểm tựa cho
một câu chuyện cơ chế.

### 5 cơ chế ứng viên — đã KIỂM, tất cả null (`diag7.py`)

Mỗi cơ chế được kiểm bằng một biến quan sát được TRƯỚC hoặc TẠI 09:30 (không look-ahead), ngũ phân vị + Spearman:

| # | Cơ chế giả định | Biến kiểm | Kết quả | Phán |
|---|---|---|---|---|
| 1 | Thông tin qua đêm (US close, futures toàn cầu) chảy qua ATO, mất cân đối lệnh giải toả dần trong ngày | dấu gap qua đêm | không đơn điệu (Q1 +17,5 / Q3 −6,0 / Q5 +1,8), rho −0,041 **p=0,165** | BÁC |
| 1b | — cùng cơ chế, đo bằng ĐỘ LỚN tin | \|gap qua đêm\| | rho +0,054 **p=0,071**, Q5 (+6,5) < Q4 (+16,6) ⇒ không đơn điệu | KHÔNG ĐỦ |
| 2 | Roll/expiry — áp lực chuyển vị thế quanh đáo hạn (thứ 5 tuần 3) | số ngày tới đáo hạn | dte≤2: −3,4bps · 3-7: −6,6 · 8-14: **+12,3** · >14: +11,7; riêng ngày đáo hạn n=54 +23,7bps | GỢI Ý, n nhỏ, 4 rổ = multiple-testing, **chưa kiểm** |
| 3 | Breakout cần biến động — chế độ vol cao thì trend kéo dài | realized vol 20 phiên (lag1) | đơn điệu **NGƯỢC** (vol thấp tốt hơn): Q1 +9,1 → Q5 −0,7; rho −0,042 **p=0,157** | BÁC (và ngược chiều giả thuyết) |
| 4 | Thanh khoản/độ sâu sổ lệnh | KLGD VN30 20 phiên (lag1) | Q1 +9,2 · Q2 −3,9 · Q5 +16,2, rho +0,020 **p=0,507** | BÁC |
| 5 | Retail momentum/herding (VN retail ~dominant) | chưa có biến trực tiếp trong mẫu này | — | **CHƯA KIỂM** (cần FiinX investor-flow theo ngày cho VN30F) |

**Tổng kiểm định đã chạy trong chẩn đoán này: ~12 biến × ngũ phân vị + Spearman. Dưới giả thuyết
null kỳ vọng ~0,6 kết quả p<0,05. Thu được: 0.** Đó không phải "chưa tìm thấy vì thiếu công cụ" —
đó là dữ liệu nói đồng đều là không có gì.

### Một kết quả DƯƠNG duy nhất (nhưng là phủ định của giả thuyết đối thủ)

**Edge KHÔNG phải beta trá hình.** Long (n=557) +5,82bps Sharpe 0,91 · Short (n=572) **+6,49bps**
Sharpe 0,87, trong khi VN30 spot buy&hold +2,91bps/phiên cùng mẫu. Chiều bán kiếm được bằng — thậm
chí hơn — chiều mua trong một thị trường đi lên. Đây là bằng chứng loại trừ "chỉ là mua rồng", KHÔNG
phải bằng chứng có edge.

### Câu trả lời thẳng cho (c)

> **Không có cơ chế vi cấu trúc nào giải thích được vì sao dấu 30 phút đầu phải quyết định chiều cả
> ngày trên VN30F, và 5 ứng viên hợp lý nhất đều đã được kiểm và đều null.** Bản thân độ chính xác
> chiều (52,35%) không loại được đồng xu sau 4,6 năm. Đây là thông tin quan trọng nhất của toàn bộ
> chẩn đoán: chương trình này chưa bao giờ có neo lý thuyết, chỉ có một chuỗi P&L dương yếu.

---

## (d) Sự kiện CẤU TRÚC 2022-2026 ảnh hưởng phái sinh VN30

Tra `kb/structural_break_watch.json` (mở 2026-09-10, owner Mike, next_review 2026-11-26):
**7/7 entry đều `status: "watching"`, `effective_date: null`, `conclusion: null`.** Registry có
`krx_microstructure`, `settlement_cycle`, `margin_regulation`, `new_products`, `ftse_msci_upgrade`,
`foreign_ownership_room` — nhưng **KHÔNG entry nào chuyên cho phái sinh VN30F**, và không entry nào
đã được xác nhận có ngày hiệu lực. Protocol: `kb/projects/amh-structural-break-protocol-20260910.md`.

⇒ **Registry hiện KHÔNG cung cấp được sự kiện cấu trúc nào đã xác nhận trong 2022-2026 để đối chiếu.**

Bằng chứng NỘI SINH bổ sung (mạnh hơn danh sách sự kiện): kiểm định điểm gãy sup-Wald **không tìm
được breakpoint có ý nghĩa nào** trong toàn chuỗi (p=0,666). Nếu một thay đổi cấu trúc thật sự đã
làm hỏng edge, nó phải để lại một điểm gãy — không có.

**5 sự kiện ứng viên cần Winston/Wendy XÁC MINH ngày hiệu lực** (tôi KHÔNG khẳng định — chưa tra
nguồn sơ cấp; đây là danh sách để verify, đúng chuẩn `verify-real-facts-dont-self-invent`):
1. Tỷ lệ ký quỹ phái sinh VSDC (có thay đổi trong 2022 không? mức nào → mức nào, ngày nào)
2. KRX go-live trên HOSE (ngày hiệu lực thật; có đổi cơ chế khớp/biên độ/lô không)
3. Rút ngắn chu kỳ thanh toán cổ phiếu cơ sở (T+3→T+2 và các bước sau)
4. Thuế/phí giao dịch phái sinh (phí VSDC, phí quản lý vị thế) có đổi mốc nào không
5. Số lượng tài khoản phái sinh / giới hạn vị thế nhà đầu tư cá nhân

⚠️ Kể cả khi xác minh được, phải nhớ: sup-Wald nói **không có điểm gãy nào** để gán cho chúng. Một
sự kiện có thật nhưng không để lại dấu trong chuỗi P&L thì không giải thích được gì.

---

## DANH SÁCH GIẢ THUYẾT CÓ THỂ KIỂM CHỨNG (đây là output của VIỆC 2, không phải kết luận)

| # | Giả thuyết | Cần dữ liệu gì | Kiểm thế nào | Ước tính khả thi |
|---|---|---|---|---|
| **H0** | **Không có edge; toàn bộ P&L là nhiễu quanh 0** (giả thuyết mặc định, hiện KHÔNG bị bác) | đã có | P(đúng chiều) CI đã chứa 50%; sup-Wald p=0,67; đoạn xấu nhất p=0,29 | ✅ đã kiểm, **chưa bác được** |
| **H1** | Edge tập trung quanh ĐÁO HẠN (dte 8-14 ngày +12,3bps; ngày đáo hạn +23,7bps n=54) | đã có (tape) | pre-specify 1 định nghĩa cửa sổ dte DUY NHẤT, test 1 lần; N độc lập = **54 kỳ đáo hạn**, không phải 1.129 phiên | ⚠️ N=54 → cần effect ~×3 hiện tại mới đủ power. **Nhiều khả năng vô vọng** |
| **H2** | Edge đến từ payoff bất đối xứng (không stop + exit cố định tạo skew dương), KHÔNG từ dự báo chiều | đã có | test riêng thành phần payoff: bootstrap CI [−0,08;+9,65] hiện **chạm 0**; cần n lớn hơn hoặc design tăng skew | ⚠️ nếu đúng, đây KHÔNG phải "edge dự báo" mà là cấu trúc payoff — có thể tái tạo rẻ hơn bằng option, và đã tính phí thì mỏng |
| **H3** | Retail flow giải thích chiều ngày (VN retail chiếm đa số KLGD) | FiinX `fiinprox_vnindex_investor_flow_daily` + luồng phái sinh theo nhà đầu tư nếu có | conditioning ngũ phân vị net theo net-buy retail hôm trước (lag1) | ✅ **rẻ, chưa kiểm** — nhưng lưu ý flow hiện có là cho VNINDEX cơ sở, không phải VN30F |
| **H4** | Edge có điều kiện theo regime DT5G (CRISIS/BEAR chưa từng được test — power 0,18) | cần ≥1 đoạn ngoài NEUTRAL | chờ dữ liệu; **KHÔNG re-test bằng nhãn backfill** (nhãn DT5G trước 2026-07-24 là full-sample construct, xem registry `notes`) | ❌ chưa có dữ liệu, và theo VIỆC 1 đã dừng cấp R&D cho hướng "chờ N" |
| **H5** | Có sự kiện cấu trúc thật làm đổi cơ chế (ký quỹ/KRX/phí) | ngày hiệu lực sơ cấp từ Winston/Wendy | event-study quanh ngày hiệu lực; nhưng sup-Wald đã nói không có điểm gãy | ⚠️ **kiểm xác nhận ngược**: nếu có sự kiện mà không có gãy ⇒ bác luôn giả thuyết |

**Không giả thuyết nào trong số này đáng đầu tư R&D ở trạng thái hiện tại** — vì tất cả đều chia
nhỏ thêm một mẫu vốn đã không đủ để phân biệt mean=+6bps với mean=0.

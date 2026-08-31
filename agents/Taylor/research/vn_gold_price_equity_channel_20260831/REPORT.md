# Giá vàng SJC vs thế giới — kênh truyền dẫn sang chứng khoán VN?

Job: `Taylor_20260831_151503` (dispatch từ Mike, 2026-08-31). Research-only, KHÔNG wire gì vào
production. Đọc `.claude/skills/quant-research/SKILL.md` trước khi thiết kế — áp dụng đúng tinh
thần: N nhỏ (thực chất **N=1 episode dùng được với dữ liệu tốt**, cộng 3 episode phụ rất yếu/nhiễu)
⇒ đây là **case-study định tính có số liệu hỗ trợ**, KHÔNG phải kiểm định thống kê có p-value.

## Tóm tắt kết luận (đọc trước)

**NO-GO cho việc dùng giá vàng/chênh lệch SJC-thế giới làm tripwire/lead-indicator sản xuất.**
Bằng chứng từ episode dữ liệu tốt nhất (2011-2012) **không ủng hộ** giả thuyết theo đúng chiều đề
xuất — quan hệ timing lỏng lẻo, có ít nhất 1 giai đoạn đảo ngược rõ (Q1/2012 vàng và VNINDEX
CÙNG tăng), và bằng chứng định lượng gợi ý chênh lệch SJC-thế giới **CHƯA THỰC SỰ TỒN TẠI** ở quy mô
đáng kể trong đúng giai đoạn chứng khoán rơi mạnh nhất (2011) — nó là hiện tượng xuất hiện SAU
Nghị định 24/2012 (từ giữa 2012 trở đi), tức sau khi đáy chứng khoán 2011 đã hình thành. Không đủ
cơ sở tách kênh (a) tỷ giá/nhập lậu khỏi kênh (b) cạnh tranh dòng tiền tiết kiệm — dữ liệu để phân
biệt 2 kênh này quá thưa. Giữ ở mức tri thức tham khảo (research-only), không nâng lên
CAP_SIGNAL-style tripwire như `kb/projects/cap-signal-advisory-20260830.md`.

## 1. Dữ liệu đã dựng

| Nguồn | File | Phạm vi | Cách lấy |
|---|---|---|---|
| VNINDEX daily (Close, Volume, RSI, PE) | `vnindex_daily_2008_2013.csv` | 2008-01 → 2013-12 | BQ `tav2_bq.ticker` WHERE `ticker="VNINDEX"` (bẫy trùng tên cột — đã alias `t.`) |
| VNINDEX daily (context episodes gần đây) | `vnindex_daily_2019_2026.csv` | 2019-06 → 2026-08 | BQ, cùng cách |
| USD/VND chính thức | `data/macro_usdvnd.csv` (đã có sẵn trong repo, KHÔNG tự tạo) | 2003-12 → 2026-04 | Local CSV, đã kiểm tra `mike/kb/data_registry/` trước — KHÔNG có entry gold/USDVND riêng, coi file này là nguồn tốt nhất hiện có |
| Giá vàng SJC + thế giới (XAU/USD) + tỷ giá chợ đen + nhập khẩu/buôn lậu vàng + Nghị định 24 mốc thời gian | Không có sẵn trong repo/BQ → dispatch sub-agent WebSearch (general-purpose, 25 tool call, log đầy đủ trong lịch sử job) | rải rác 2007-2026, đậm nhất 2010-2013 | WebSearch/WebFetch, mọi điểm số liệu có URL nguồn (liệt kê ở §5) |

**⚠️ Chất lượng dữ liệu vàng — nói thẳng, không giấu:** KHÔNG tồn tại 1 series SJC hàng
tháng/hàng ngày sạch từ một nguồn duy nhất cho 2010-2013. Mọi con số là **điểm rời rạc neo theo
sự kiện tin tức** từ nhiều báo VN khác nhau (topi.vn, tierra.vn, bartrawealthadvisors, bullionstar),
không phải time series đã kiểm chứng chéo. World gold (XAU/USD) monthly grid chuẩn (FRED
`GOLDAMGBD228NLBM`, LBMA) **không lấy được trực tiếp trong job này** (LBMA archive bị khoá từ
03/2025, macrotrends chặn fetch 403) — chỉ có average theo năm + vài điểm mốc theo tháng/ngày cụ
thể qua search snippet. Tỷ giá USD/VND **chợ đen** (không phải official) cũng chỉ có điểm rời rạc,
nhiều nguồn cho số khác nhau (chênh 500đ tới hàng nghìn đồng tuỳ nguồn) — không đủ tin cậy để dùng
làm chuỗi định lượng, chỉ dùng làm bằng chứng định tính có hướng.

**Vì lý do trên: KHÔNG chạy hồi quy/kiểm định thống kê hình thức nào trên "chuỗi giá vàng".** Theo
đúng §5 skill quant-research ("match statistical tool to N") — với dữ liệu thưa neo sự kiện, công
cụ đúng là xếp timeline sự kiện cạnh nhau và đọc trực tiếp, không phải ép vào N lớn giả.

## 2. Episode tham chiếu: 2011-2012 (Nghị định 24/2012)

### Mốc chính sách
- **11/02/2011**: SBV phá giá VND chính thức ~9,3% (đợt phá giá lớn nhất trong nhiều năm).
- **24/02/2011**: Nghị quyết 11/NQ-CP — thắt chặt tiền tệ/tài khoá chống lạm phát (đã ghi trong
  `mike/kb/data_registry/market-state/vn_macro_regime_history.md` — episode `EP-2009-09`).
- **08/2011**: CPI YoY đỉnh 23% (đỉnh lạm phát chu kỳ 2009-2012).
- **11/2011**: SBV nâng lãi suất tái cấp vốn lên 15% (đỉnh thắt chặt).
- **03/04/2012**: Nghị định 24/2012/NĐ-CP ban hành — Nhà nước độc quyền sản xuất vàng miếng,
  SJC thành thương hiệu vàng miếng quốc gia duy nhất. Hiệu lực **25/05/2012**.
- **03/2013 → hết 2013**: SBV chạy 76 phiên đấu thầu vàng bình ổn giá, bán ~1,82 triệu lượng
  (~70 tấn) — đây là cơ chế "trần" của Nhà nước bắt đầu chủ động can thiệp gap.

### Chuỗi giá (điểm rời rạc, xem §5 cho từng nguồn)

| Thời điểm | SJC (tr đồng/lượng) | Vàng thế giới (USD/oz) | VNINDEX close (tháng, BQ) |
|---|---|---|---|
| 2011-01 | ~35,8 (đầu năm) | ~1.410 (giá đóng 2010) | **510,6** (đỉnh cục bộ) |
| 2011-02 (sau phá giá 11/02) | 35,9-37 | — | **461,4** (−9,6% MoM) |
| 2011-04-20 | 37-38 | vượt $1.500 cùng ngày | 480,1 |
| 2011-05 | — | — | **421,4** (−12,2% MoM) |
| 2011-07 cuối | ~40 | $1.624 | 405,7 |
| 2011-08/09 đầu (đỉnh lịch sử) | **48,9-49,3** (đỉnh) | ATH thế giới ~$1.900-1.920 (06/09) | 425,4 → 427,6 (đi ngang) |
| 2011-11 | — | đã hạ nhiệt | **380,7** (−9,6% MoM) |
| 2011-12 (đáy VNINDEX) | 42,68 (bán ra) | ~$1.600 | **351,55** (đáy chu kỳ, −7,7% MoM) |
| 2012-01→04 (Nghị định 24 ban hành 03/04) | 45,8 → tăng dần trong năm | — | **387,97 → 473,77** (+35% từ đáy T12/2011, RALLY) |
| 2012 cả năm | +7,83% (41-46,3tr range) | +6,6% ($1.669 avg → ~$1.675 cuối năm) | dao động 378-474, kết năm 413,73 |
| 2012 cuối năm | chênh SJC-TG **4-5tr đồng/lượng** — gap bắt đầu nới rõ rệt sau Nghị định 24 | | |
| 2013 cả năm | −24,6% | −25,5% (gần khớp % — gap % không nới thêm nhiều trong 2013) | dao động 475-518, khá ổn định |

### Đọc timing — 3 quan sát chính

**(i) Chứng khoán rơi TRƯỚC khi vàng đạt đỉnh, không phải SAU.** VNINDEX đỉnh Jan/2011 (510,6),
đã giảm liên tục 7 tháng liền (Feb→Jul/2011, −20,5%) TRƯỚC KHI vàng đạt đỉnh lịch sử (Aug-Sep/2011).
Nếu vàng là nguyên nhân dẫn dắt (leading), phải thấy vàng tăng RỒI chứng khoán mới yếu — thực tế
ngược: chứng khoán yếu dần cùng với phá giá VND (Feb/2011) và thắt chặt tiền tệ (Nghị quyết 11),
lúc đó giá vàng còn chưa tăng mạnh (35,9-38tr, mới +6% so đầu năm). Đỉnh vàng chỉ xảy ra ở THÁNG
THỨ 7-8 của downtrend chứng khoán đã có sẵn — đọc tự nhiên nhất là **cả hai cùng phản ứng với gốc
rễ chung** (lạm phát 2 chữ số, phá giá VND, thắt chặt tiền tệ, khủng hoảng NHTM đang ủ bệnh — xem
`EP-2009-09` trong registry) chứ không phải vàng → chứng khoán.

**(ii) Q1/2012: vàng và VNINDEX CÙNG TĂNG — đảo ngược trực tiếp giả thuyết.** Ngay sau Nghị định
24 ban hành (03/04/2012), giá vàng SJC tiếp tục xu hướng tăng trong năm (+7,83% cả 2012) trong khi
VNINDEX cũng tăng mạnh Jan→Apr/2012 (+35% từ đáy). Đây KHÔNG phải nhiễu nhỏ — là một quý dữ liệu
đi ngược hẳn chiều giả thuyết đề xuất trong nhiệm vụ này.

**(iii) Vàng hạ nhiệt cuối 2011 (đỉnh 49tr → 42,68tr, −13%) trong khi VNINDEX vẫn tiếp tục rơi tới
đáy chu kỳ (Nov→Dec/2011, −9,6%→−7,7% MoM liên tiếp).** Nếu channel giá vàng là driver, kỳ vọng
chứng khoán phục hồi khi áp lực vàng giảm — thực tế chứng khoán rơi SÂU NHẤT đúng lúc vàng đang hạ
nhiệt. Đáy VNINDEX thực sự (Dec/2011) trùng với đáy chu kỳ kinh tế (CPI bắt đầu hạ từ đỉnh 23%,
Nghị quyết 11 đã ngấm ~10 tháng) — không trùng đỉnh vàng.

### Kênh (a) — tỷ giá/áp lực nhập lậu: bằng chứng định lượng YẾU trong đúng giai đoạn cần

Dùng tỷ giá USD/VND CHÍNH THỨC có sẵn (`data/macro_usdvnd.csv`, đã kiểm tra trước khi wire theo
§9 coding_guidelines — không có entry gold/FX riêng trong `data_registry`, dùng file local hiện có
làm nguồn tốt nhất):
- 01/03/2011: 19.465 → 15/03/2011: 20.850 (**+7,1% trong 2 tuần** — chính là cú phá giá 11/02 phản
  ánh vào dữ liệu chính thức).
- Sau đó **gần như ĐI NGANG suốt phần còn lại 2011-2012**: dao động hẹp 20.300-21.010 tới hết
  2012, kể cả trong đúng giai đoạn vàng lập đỉnh lịch sử (Aug-Sep/2011) và giai đoạn gap SJC-TG
  nới rộng nhất (cuối 2012, sau Nghị định 24).

**Ước tính back-of-envelope (KHÔNG chính xác ngày-với-ngày, chỉ định hướng — số liệu vàng chỉ có
theo khoảng, không theo ngày cụ thể):** tại đỉnh SJC Aug-Sep/2011 (~49tr/lượng), quy đổi world
gold ATH ~$1.900/oz × tỷ giá chính thức ~20.600đ (bình quân H2/2011) × 1,20556 oz/lượng ≈
**39,1tr đồng/lượng "giá ngang giá"**. So với SJC thực tế 48,9-49,3tr → **chênh lệch chỉ ~3,7-4%**
theo tỷ giá CHÍNH THỨC — thấp hơn nhiều so với mức 30-40%+ (13-20tr/lượng) từng thấy 2022-2024.
Nếu dùng tỷ giá CHỢ ĐEN cao hơn (có nguồn cho ~21.500-22.000đ giai đoạn này, dù không tin cậy cao)
thì giá "ngang giá" quy đổi còn CAO HƠN giá SJC thực bán — tức **premium gần như KHÔNG TỒN TẠI, có
thể âm**, ở đúng thời điểm chứng khoán đang trong downtrend. Điều này khớp với đọc sử: cơ chế
"chênh SJC-thế giới → áp lực tỷ giá" là hiện tượng **hậu Nghị định 24** (từ giữa 2012, khi Nhà
nước độc quyền sản xuất/nhập khẩu vàng miếng cắt đường arbitrage hợp pháp) — CHƯA vận hành ở quy mô
đáng kể trong chính giai đoạn 2011 mà chứng khoán rơi mạnh nhất.

Dữ liệu buôn lậu/nhập khẩu vàng tìm được (xuất khẩu trang sức sang Thụy Sĩ, dòng vàng ra ~2-3 tỷ
USD/năm 2009-2010, dự trữ vàng dân cư ước 300-500 tấn năm 2012) xác nhận QUY MÔ dòng vàng lớn
nhưng KHÔNG có breakdown theo tháng để khớp với timing chứng khoán — không đủ để kết luận thêm.

### Kênh (b) — cạnh tranh dòng tiền tiết kiệm cá nhân: không tìm được dữ liệu đủ tin cậy

Chỉ có 1 số liệu khảo sát hộ gia đình (phân bổ tiết kiệm: 47% giữ tại nhà, 33% gửi ngân hàng, 0,4%
chứng khoán, 0,6% quỹ hưu trí) nhưng **KHÔNG rõ năm khảo sát** — sub-agent tự flag "không dùng khi
chưa xác nhận được nguồn/năm gốc". Không tìm được GSO/VHLSS series theo năm để so dòng tiền
vàng-vs-tiết kiệm ngân hàng-vs-chứng khoán 2010-2012. **Không đủ cơ sở kết luận về kênh (b)** —
đây là khoảng trống dữ liệu thật, không phải "không có quan hệ".

## 3. Episode phụ (2020, 2022, 2024-04, 2025-04) — chỉ đọc định hướng, KHÔNG tính là N độc lập bổ sung có ý nghĩa

Mỗi episode dưới đây đều có 1 sự kiện KHÁC, được xác lập rõ trong sử ký VN, giải thích chứng khoán
yếu tốt hơn nhiều so với "cạnh tranh vàng" — liệt kê để tránh cherry-pick, không phải bằng chứng
ủng hộ giả thuyết:

| Episode | Vàng | VNINDEX cùng kỳ | Driver thực tế đã biết (không phải vàng) |
|---|---|---|---|
| 2022-03 | Gap SJC-TG 17,39tr (03/03) | Đỉnh 1.492 (03/2022) → đáy 1.007-1.028 (10-12/2022), **−32%** | Bắt Trịnh Văn Quyết/FLC (29/03/2022), Tân Hoàng Minh (04/2022), Vạn Thịnh Phát (10/2022) — khủng hoảng trái phiếu BĐS + thao túng CK, cùng lúc Fed tăng lãi suất mạnh toàn cầu |
| 2024-04/05 | Gap kỷ lục lúc đó ~18-20tr, SBV đấu thầu lại từ 04/2024 | Đỉnh 1.284 (03/2024) → 1.209,5 (04/2024, **−5,8% MoM**) → phục hồi ngay 05/2024 (1.261,7) | Điều chỉnh nhẹ, phục hồi nhanh — quy mô quá nhỏ để coi là "chứng khoán yếu" theo đúng nghĩa nhiệm vụ đặt ra |
| 2025-04 | SJC đỉnh kỷ lục 124tr/lượng (22/04) | 1.306,9 (03/2025) → 1.226,3 (04/2025, **−6,2% MoM**) | Cú sốc thuế quan Trump "Liberation Day" (04/2025) — sự kiện toàn cầu, không riêng VN |

Cả 3 episode phụ đều CÙNG THÁNG có driver phi-vàng đã được xác lập rõ trong báo chí/sử ký kinh tế
— không đủ cơ sở tách phần đóng góp của riêng kênh vàng khỏi driver chính. Đưa vào bảng để minh
bạch, không đếm là bằng chứng độc lập bổ sung cho N.

## 4. Kết luận & khuyến nghị

**QUALIFY/NO-GO: NO-GO cho production tripwire.** Lý do:
1. Episode dữ liệu tốt nhất (2011-2012) có **bằng chứng trực tiếp đảo ngược giả thuyết** (Q1/2012
   vàng-VNINDEX cùng tăng) và **timing không khớp** (chứng khoán rơi trước đỉnh vàng 7 tháng, rơi
   sâu nhất khi vàng đang hạ nhiệt).
2. Chênh lệch SJC-thế giới — cơ chế cụ thể của kênh (a) — **gần như không tồn tại đáng kể** ở đúng
   giai đoạn chứng khoán yếu nhất (2011); nó là hiện tượng cấu trúc xuất hiện SAU Nghị định 24
   (giữa 2012 trở đi), lúc chứng khoán đã tạo đáy và đang phục hồi.
3. N thực chất = 1 episode có dữ liệu đủ tin để đọc chi tiết, cộng 3 episode phụ đều bị confound
   nặng bởi driver phi-vàng đã biết rõ — không đủ để tách kênh (a) khỏi kênh (b), và không đủ để
   dùng bất kỳ ngôn ngữ thống kê nào (không N, không p-value).
4. Không tìm được chuỗi dữ liệu đủ chất lượng (SJC monthly sạch, world gold monthly chuẩn, tỷ giá
   chợ đen tin cậy) để nâng cấp phân tích này lên định lượng nghiêm túc trong phạm vi 1 job.

**Đề xuất cụ thể:**
- **Giữ ở research-only.** KHÔNG thêm gold/SJC vào CAP_SIGNAL hay bất kỳ gate macro nào.
- Nếu muốn theo đuổi tiếp: việc đầu tư đáng giá nhất là dựng lại đúng 1 chuỗi world gold monthly
  chuẩn (FRED `GOLDAMGBD228NLBM` — thử lại bằng tool khác, WebFetch bị 403 trên macrotrends/LBMA
  trong job này) + xin/scrape SJC daily archive (nếu tồn tại API/CSV công khai) — nếu vẫn giữ được
  đọc giống báo cáo này ở độ phân giải cao hơn thì kết luận sẽ vững hơn, nhưng dựa trên bức tranh
  hiện tại, khả năng đổi chiều kết luận thấp (timing lệch quá rõ, 1 quý đảo chiều trực tiếp).
- Registry pointer: entry mới nên vào `mike/kb/data_registry/market-state/` (chưa tạo file — đây
  là research job, không phải wiring data source; nếu sau này có ai dùng lại `data/macro_usdvnd.csv`
  cho mục đích liên quan vàng/tỷ giá, nên thêm 1 dòng ghi chú ở đó theo §9 coding_guidelines).

## 5. Nguồn (từ sub-agent WebSearch, chưa kiểm chứng chéo độc lập trong job này)

topi.vn/bieu-do-gia-vang-qua-cac-nam · virtusprosperity.com (VN gold 2000-2023) ·
tierra.vn (gia-vang-nam-2011, gia-vang-nam-2012) · bartrawealthadvisors.com.vn/gia-vang-sjc-nam-2011 ·
bullionstar.com/gold-university/vietnam-gold-market · namvietnews.wordpress.com (Vietnam's gold
habit weighs down the dong, 2011) · thuvienphapluat.vn + luatvietnam.vn + vanban.chinhphu.vn
(Nghị định 24/2012/NĐ-CP) · eastasiaforum.org (VN credit/devaluation spiral, 2011) ·
pca-cs.com (VND vs USD historical) · vneconomy.vn + baochinhphu.vn (điều hành tỷ giá 2011-2013) ·
vov.vn, dantri.com.vn, vietnamnet.vn, thanhnien.vn, nld.com.vn (các mốc giá vàng/gap 2020-2026) ·
metalcharts.org (world gold 2008) · statista.com, benzinga.com (world gold 2024).
Danh sách URL đầy đủ nằm trong output gốc của sub-agent (không lưu file riêng — có thể tái tạo lại
bằng cách chạy lại đúng prompt dispatch, xem lịch sử job `Taylor_20260831_151503`).

**Self-check phạm vi job này:** không có backtest engine chạy (không cash-flow identity 0 VND cần
verify — đây là case-study định tính + BQ pull đơn giản, không phải R&D signal test). Đã verify:
(a) VNINDEX pull dùng đúng bảng/ticker (`t.ticker="VNINDEX"`, alias tránh bẫy trùng cột đã ghi
trong CLAUDE.md), (b) `data/macro_usdvnd.csv` đọc trực tiếp không qua biến đổi, (c) mọi con số vàng
đều có URL nguồn kèm theo, không có số nào tự bịa/suy diễn — chỗ nào thiếu dữ liệu đã ghi rõ "not
found"/"không đủ tin cậy" thay vì nội suy.

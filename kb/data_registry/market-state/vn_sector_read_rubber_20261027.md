---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby) — đọc BLIND, dispatch từ Mike 2026-10-27; KHÔNG được biết/tra giá cổ phiếu, KQKD Q3/2026 của DRI hay khuyến nghị CTCK
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành cao su thiên nhiên VN (nền cho due diligence DRI) — pha chu kỳ, cơ cấu chi phí, so sánh nhóm, rủi ro đuôi, chỉ báo dẫn đầu, FORECAST khoá trước
as_of: 2026-10-27 (dữ liệu giá tới 2026-10-23/26)
---

# SECTOR READ — Cao su thiên nhiên VN, as-of 27/10/2026 (Bobby, real-time BLIND)

Không phải episode VNINDEX, không vào N_effective. Nhãn: **[DK]** = dữ kiện có nguồn/ngày; **[UĐ]** = ước
đoán/suy luận của Bobby; **[NỀN]** = hiểu biết nền chưa kiểm lại trong lượt này.

## 0. Nguồn dữ liệu local đã xác minh
- `tav2_bq.commodity_prices` (source `trading_economics`, key `rubber` = **TSR20 SGX, US¢/kg**; `synthetic_rubber`
  CNY/t; `brent`) — tươi tới 2026-10-23. Registry: `kb/data_registry/feeds/bq_commodity_prices.md` (TE rubber = TSR20, WB = RSS3).
- `data/rubber_monthly.csv` = WB CMO RSS3 tháng, tới 2026-09 (mtime 05/10) — CANONICAL qua `commodity_wb_cmo.md`.
- `data/rubber_weekly.csv` — chuỗi ngày THẬT chỉ từ 2026-06-19 (94 dòng); `regionalert` RSS3/TSR20 tuần + `sunsirs`
  spot TQ ngày (cn_rmb_ton) tới 2026-10-26. Bẫy #2/#4 của file (độ phủ lịch, nghi vấn regionalert) áp dụng.
- KHÔNG mở các file có chữ DRI (đúng yêu cầu caller).

## 1. Pha chu kỳ giá + động lực
**Mức giá [DK]:**
| Chuỗi | Hiện tại | So sánh | Nguồn |
|---|---|---|---|
| TSR20 (TE) | 254,3 ¢/kg (23/10); đỉnh 265,4 (13/10) | Oct-25 TB 172,1 ⇒ **+50% YoY**; **phân vị 99,3% từ 2016**, cao nhất từ 2013 | BQ commodity_prices |
| RSS3 WB tháng | 2,75 $/kg (T9) | đỉnh 2,86 (T6); T9/25 2,11 (+30%); phân vị 10 năm 97,5% | rubber_monthly.csv |
| Spot TQ (sunsirs) | 19.408 CNY/t (26/10) | đáy 16.392 (30/07) → đỉnh 19.992 (12/10), −2,9% từ đỉnh; Oct-25 ~14.750 (+31%) | rubber_weekly.csv; SunSirs 03/11/2025 |
| SHFE | T11 19.215, T1 19.900 CNY/t (17/10) | — | Thời báo TC VN 17/10/2026 |
| TOCOM/OSE RSS3 | 448 JPY/kg (17/10) | — | nt |
| Giá XK VN | T9: 2.323 USD/t (+29,8% YoY, cao nhất ~13 năm); 9T: 2.022 (+14,4%) | lượng 9T 1,08 tr t (−15,8%), sang TQ −31,3% (T9 −38,8%) | TBTCVN 17/10; THCL 22/10/2026 (Hải quan) |
| Mủ nước nội địa | Bình Long 540 đ/TSC (tại NM), Phú Riềng 420, Bà Rịa 420, MangYang 458-463; mủ tạp 16.700-18.000 đ/kg | Bình Long đầu T9/2025 422 ⇒ **+28% YoY**; Phú Riềng/Bà Rịa ~đi ngang | TBTCVN 17/10/2026; THCL (T9/2025) |

**Đa proxy (giá nội địa là giá thu mua "neo" của DN nhà nước) [UĐ]:** 420 đ/TSC ≈ 42.000 đ/kg khô; 540 ≈ 54.000;
XK T9 2.323 USD/t × 25.639 (TTTT 20/10) ≈ 59.600 đ/kg; TSR20 SGX ≈ 65.200 đ/kg. Đồng thuận về HƯỚNG (cao), PHÂN KỲ
về MỨC: giá thu mua niêm yết của Phú Riềng/Bà Rịa trễ và thấp hơn thị trường 20-35%. DN có vườn riêng bán SVR theo
giá XK/FOB hưởng mức cao hơn con số mủ nước báo chí trích. Đừng dùng mủ nước Phú Riềng làm proxy giá bán của DN.

**Động lực:**
1. **Cầu TQ YẾU — phân kỳ với giá [DK]:** NK cao su TQ T9 588 nghìn t (−20,8% YoY); bán lẻ ô tô con T9 ~1,618 tr
   (−28% YoY) (ECHEMI/Business Society 16/10/2026). Công suất lốp bán thép 64,42% (03/09, −2,5pp YoY; T10/2025 ~74%)
   (Ruida/Longzhong 09/2026; SunSirs 03/11/2025). Bernama 21/10: tồn kho Qingdao tiếp tục tăng, lốp chạy dưới
   mức bình thường, nhà máy cắt mua ở giá cao. Lốp xuất khẩu PCR T9 −6,1% MoM (Mysteel); EU AD/CVD lốp TQ dự kiến
   kết luận cuối 2026, Canada mở điều tra TBR T9/2026.
2. **Tồn kho Qingdao CAO [DK]:** 62,77 vạn t (30/08), giảm từ 71,52 (giữa T5); cùng kỳ 2025 ~43,2 (26/10/2025) ⇒
   **~+45% YoY**. Số T10/2026 chưa tìm được — Bernama nói đang tăng lại (định tính).
3. **Dầu/cao su tổng hợp — trụ đỡ chi phí [DK]:** Brent 116,7 USD/thùng (23/10; ~115 Reuters, cao nhất từ 04/05),
   do Hormuz/tấn công tàu chở dầu, Houthi–Ả Rập Xê Út. SR (TE) 16.267 CNY/t, +41% YoY. Tỷ lệ NR/SR TQ ~1,19 (Oct-25
   ~1,27) ⇒ NR rẻ tương đối hơn SR so với năm ngoái → hỗ trợ thay thế [UĐ].
4. **Cung — thắt nhưng là cú sốc thời tiết + nền cấu trúc [DK/UĐ]:** mưa/bão Thái Lan T8-T10 làm gián đoạn cạo,
   mủ chén Thái 73,8 THB/kg (+44,6% YoY, 21/09); SMR20 cao nhất từ 05/2012 ngày 09/10 (TE/Bernama). ANRPC: 2026 thiếu
   hụt ~317 nghìn t (15,039 vs 15,356 tr t, trích THCL 22/10) — nhưng bản T8 trích ~101 nghìn t ⇒ **số không nhất
   quán giữa các bản trích, độ tin thấp**. Năm thứ 6 thiếu hụt liên tiếp (nền cấu trúc: cây già TL, bệnh rụng lá
   Indonesia, VN chuyển đất cao su sang KCN/cây khác — XK VN −15,8% lượng). Cảng Abidjan ùn tắc (Bờ Biển Ngà) —
   không có số sản lượng 2026.
5. **El Niño RẤT MẠNH [DK]:** Niño3.4 tuần +3,3°C (14/10), T9 +2,84°C (IRI 19/10/2026); WMO T8: ~100% duy trì
   tới DJF 2026-27; NOAA: >90% sự kiện rất mạnh, ~69-75% mạnh nhất từ 1950. Tác động [UĐ]: ngắn hạn (T11-T12) khô
   hơn ⇒ cạo thuận lợi, cung mùa cao điểm có thể DỒI DÀO hơn; trung hạn (T2-T5/2027) hạn mùa khô ⇒ rụng lá kéo dài,
   ra lá muộn, cung Q1-Q2/2027 thấp ⇒ đuôi phải 90 ngày+.
6. **Tỷ giá/lãi suất [DK]:** USD/VND trung tâm 25.639 (20/10, TTTCTT) — nhích dần; Fed được kỳ vọng nâng lãi lại
   T12 (Bernama 21/10) ⇒ USD mạnh, gió ngược hàng hoá. CNY: không có số trong lượt này.
7. **EUDR [DK]:** áp dụng 30/12/2026 (DN vừa/lớn), 30/06/2027 (siêu nhỏ/nhỏ) (OJEU 23/12/2025); gói đơn giản hoá
   04/05/2026, Ủy ban không mở lại văn bản (Hogan Lovells/Arendt, T5/2026). Không có cập nhật T10 tìm được. Với VN,
   EU là thị trường nhỏ (TQ ~59% lượng 9T) ⇒ rủi ro là chênh giá/thủ tục cho lô đi EU, không phải cú sốc cầu [UĐ].

## 2. Cơ cấu chi phí, biên, mùa vụ (DN vườn cây cỡ nhỏ-vừa)
- **Mùa vụ [NỀN, sửa giả định caller]:** ở Đông Nam Bộ/Tây Nguyên/Nam Lào, sản lượng tăng từ T6, **đỉnh T9-T12**
  (Q4 là quý cao điểm, KHÔNG phải nghỉ cạo); rụng lá/nghỉ cạo **~T2-T4** (Q1 thấp nhất, Q2 phục hồi). Doanh thu ghi
  khi bán ⇒ có độ trễ tồn kho; Q4 thường gánh tỷ trọng lớn nhất năm.
- **Chi phí [NỀN/UĐ]:** giá thành đầy đủ DN VRG-loại ~32-38 tr đ/t, trong đó nhân công cạo ~40-50% (quỹ lương
  thường gắn đơn giá theo doanh thu/sản lượng ⇒ một phần BIẾN THEO GIÁ), khấu hao vườn ~5-8 tr đ/t (vườn hết khấu hao
  khi già ⇒ biên vườn già cao nhưng năng suất giảm), phân bón/hoá chất, chế biến. Vườn ở Lào/Campuchia: lương rẻ hơn,
  thêm thuê đất và rủi ro tỷ giá LAK/KHR.
- **Thanh lý vườn cây:** thu nhập một lần khi tái canh (bán gỗ cao su), cùng chiều giá gỗ, không theo giá mủ; làm
  LNST nhiễu theo năm — phải tách khi đo độ nhạy.
- **Độ nhạy minh hoạ [UĐ]:** giá bán thực 55 tr đ/t, giá thành tiền 30 + KH 6 ⇒ EBIT 19 tr/t (biên ~35%). Giá ±10%
  ⇒ EBIT mảng mủ **±29%** nếu chi phí cố định; **±19%** nếu ~35% doanh thu tăng thêm chảy vào quỹ lương. Ở giá đáy chu
  kỳ (~38-40 tr đ/t) biên ~0 ⇒ đòn bẩy >5x. Taylor phải thay bằng số thật của DRI (sản lượng, giá bán, giá thành).

## 3. So sánh nhóm [NỀN — cần xác minh từ BCTN]
| Mã | Mô hình | Khác DRI |
|---|---|---|
| GVR | Tập đoàn, quỹ đất rất lớn: mủ + gỗ + **KCN/chuyển đổi đất**, đền bù, cổ tức từ cty con | lợi nhuận đa dạng, định giá theo đất |
| PHR | mủ + **đền bù/chuyển đổi đất KCN (VSIP III)**, góp vốn KCN | thu nhập đột biến từ đất |
| DPR | mủ + KCN Bắc/Nam Đồng Phú | KCN là trụ thứ 2 |
| TRC | mủ VN + vườn Campuchia, thanh lý vườn đáng kể, tiền mặt lớn | gần "thuần mủ" nhất trong nhóm VRG |
| HRC | nhỏ, mủ + vườn Campuchia + chuyển đổi đất | quy mô nhỏ, lãi biến động |
| DRC | **sản xuất LỐP** — cao su là ĐẦU VÀO | phơi nhiễm NGƯỢC chiều; dùng để hedge/đối chứng |
| DRI | vườn cây chủ yếu tại Nam Lào, công ty mẹ Dakruco; không có quỹ đất KCN ở VN | **thuần mủ** ⇒ độ nhạy giá cao nhất nhóm, cộng rủi ro chính sách/tỷ giá Lào; ít "đệm" thu nhập đất |

## 4. Phân loại chế độ ngành
**`CYCLICAL_PEAK` (vùng đỉnh do CUNG đẩy, cầu KHÔNG xác nhận) đặt trên một nền cung `STRUCTURAL` thắt — confidence
`ambiguous`, ~60/40 (PEAK vs MID-tiếp diễn).**
- Vì sao PEAK: giá ở phân vị 99% của 10 năm, +50% YoY, trong khi MỌI chỉ báo cầu đi ngược (NK TQ −21%, ô tô −28%,
  lốp −2,5…−10pp, Qingdao +45% YoY); giá đã quay đầu từ 13/10 (TSR20 −4%, spot TQ −3%) đúng lúc vào mùa cao điểm
  cạo Q4. Mẫu giống đỉnh do thời tiết 2016-17 / Q4-2024 hơn là siêu chu kỳ cầu 2010-11.
- Vì sao chưa clean: dầu >110 USD giữ sàn chi phí SR; El Niño rất mạnh đe doạ cung 2027 H1; 6 năm thiếu hụt +
  diện tích VN co lại ⇒ đáy chu kỳ kế tiếp có thể cao hơn đáy 2023 (TSR20 ~130-140¢).
- **Đổi phán đoán:** → MID/tiếp diễn nếu Qingdao giảm ≥3 tuần liên tiếp + lốp bán thép ≥70% + ô tô TQ YoY dương,
  hoặc mùa khô 2027 cắt sản lượng TL/VN ≥5%. → đi xuống TROUGH nếu Brent về <85 (ngừng bắn vùng Vịnh) + Qingdao
  >70 vạn t + TSR20 <220¢ trong 2 tháng.

## 5. Rủi ro đuôi + chỉ báo dẫn đầu
**Đuôi trái:** gãy cầu TQ (ô tô/BĐS, thuế lốp EU/Canada/Mỹ), xả vị thế đầu cơ SHFE, dầu sụp khi xung đột hạ nhiệt,
Fed nâng lãi + USD mạnh, cung cao điểm Q4 dồi dào do El Niño khô. **Đuôi phải:** Hormuz đóng kéo dài (Brent >125),
lũ Nam Thái T11-T1 (mùa mưa bình thường của Nam TL), hạn El Niño T2-T5/2027, dịch bệnh lá. **Riêng DRI-loại:** chính
sách đất/thuế Lào, LAK, EUDR cho lô đi EU từ 30/12/2026.

| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu xấu ⇔ tốt |
|---|---|---|---|
| 1 | Tồn kho Qingdao tổng (tuần) | Longzhong/Ruida, SunSirs | tăng ≥3 tuần ⇔ giảm ≥3 tuần |
| 2 | Công suất lốp bán thép/toàn thép TQ (tuần) | Longzhong, Mysteel | <62% ⇔ ≥70% |
| 3 | Mủ chén/mủ nước Thái (THB/kg) + chênh VN 3L–Yunbao Qingdao | Bernama, ECHEMI | Thái giảm + chênh co ⇔ ngược lại |
| 4 | Brent + SR CNY/t (ngày) | BQ `commodity_prices` | Brent <90 ⇔ >120 |
| 5 | Niño3.4 + mưa mùa khô TL/VN (tháng) | IRI/NOAA, TMD | — (đuôi phải 2027) |
| 6 | XK cao su VN lượng/giá, sang TQ (tháng) | Hải quan | giá XK giảm 2 tháng ⇔ tăng |
| 7 | Mủ nước Bình Long (giá TT) vs Phú Riềng (neo) | báo giá hằng ngày | Bình Long hạ về ≤480 ⇔ Phú Riềng nâng |

## 6. FORECAST KHOÁ TRƯỚC (lập 2026-10-27, chấm theo dữ liệu quan sát cuối cùng ≤ ngày kiểm)
Mốc gốc: TSR20 TE `rubber` = **254,3¢** (23/10); spot TQ sunsirs `cn_rmb_ton` = **19.408** (26/10); mủ nước
**Bình Long 540 / Phú Riềng 420 đ/TSC** (17/10).
| Chân trời | Chuỗi | Dự báo |
|---|---|---|
| +30 ngày (**2026-11-26**) | TSR20 | P(<254,3) = **0,60**; P(≤234, −8%) = 0,20; P(≥275, +8%) = 0,10 |
| | spot TQ | P(<19.408) = **0,60** |
| | mủ nước nội địa | P(ít nhất một trong hai hạ ≥10 đ) = 0,35; P(cả hai giữ nguyên) = 0,50; P(nâng) = 0,15 |
| +90 ngày (**2027-01-25**) | TSR20 | P(<254,3) = **0,55**; P(≤229, −10%) = 0,28; P(≥280, +10%) = 0,18 |
| | spot TQ | P(<19.408) = 0,55 |
| | mủ nước nội địa | P(thấp hơn) = 0,45; P(không đổi) = 0,35; P(cao hơn) = 0,20 |
**Dự báo sai nếu:** Qingdao giảm liên tục + lốp TQ hồi ≥70%; Brent >125 kéo dài; lũ lớn Nam Thái/VN T11-T12; TQ
tung kích cầu ô tô mới. Chấm điểm: Mike/Bobby đọc BQ `commodity_prices` + `rubber_weekly.csv` tại 2 mốc, ghi kết quả
dưới mục này (Brier). **Không phải khuyến nghị mua/bán DRI.**

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (TE, WB) — truy vấn 27/10/2026; `data/rubber_monthly.csv`, `data/rubber_weekly.csv`.
- Thời báo Tài chính VN, "Ngày 17/10: Giá cao su xuất khẩu của VN liên tục tăng cao", 17/10/2026 — https://thoibaotaichinhvietnam.vn/ngay-17-10-gia-cao-su-xuat-khau-cua-viet-nam-lien-tuc-tang-cao-205525.html
- Thương hiệu & Công luận, "Cao su VN: giá bán tăng nhưng lượng XK vẫn lao dốc", 22/10/2026 — https://thuonghieucongluan.com.vn/cao-su-viet-nam-gia-ban-tang-nhung-luong-xuat-khau-van-lao-doc-a338991.html ; bản tin giá 10/10/2026 — https://thuonghieucongluan.com.vn/gia-cao-su-hom-nay-10-10-tang-tren-san-shfe-sgx-a337478.html
- Bernama, KL rubber, 21/10/2026 — https://bernama.com/en/market/news.php?id=2623598
- ECHEMI/Business Society, 16/10/2026 — https://www.echemi.com/cms/3274744.html
- SunSirs, 03/11/2025 (cơ sở YoY) — https://www.sunsirs.com/uk/detail_news-27612.html ; Ruida/Longzhong nhật báo (09/2026) — https://www.rdqh.com/upload/files/base/b/o/115765.pdf
- Mysteel PCR exports T9/2026 — https://www.mysteel.net/news/5145260-chinas-pcr-tire-exports-fall-6-mom-in-sep
- IRI ENSO 19/10/2026 — https://iri.columbia.edu/?p=31794 ; WMO ENSO Update 08/2026 — https://wmo.int/sites/default/files/2026-08/Factsheet-ENSO-Update-August-2026-en.pdf
- EUDR: Hogan Lovells — https://hlc.com/en/publications/eu-deforestation-regulation-commission-publishes-simplification-package-ahead-of-december-2026 ; Arendt — https://www.arendt.com/news-insights/news/eudr-simplification-review-published-what-the-2026-package-means-for-in-scope-companies/
- Brent 23/10/2026 — https://en.mercopress.com/2026/10/17/brent-touches-us-110-for-the-first-time-since-may-on-middle-east-tensions/comments ; https://ground.news/article/brents-oil-price-was-over-117-a-barrel
- Tỷ giá trung tâm 20/10/2026 — https://thitruongtaichinhtiente.vn/ngay-20-10-ty-gia-trung-tam-tang-6-dong-86422.html
- ANRPC (qua bản trích): https://www.capmad.com/post/anrpc-sees-global-natural-rubber-output-at-153-mt-in-2026-still-trailing-demand ; https://www.european-rubber-journal.com/article/2098880/anrpc-expects-slight-growth-in-natural-rubber-supply-demand-in-26

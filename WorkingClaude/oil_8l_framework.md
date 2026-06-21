# Nhóm Xăng Dầu (Oil & Gas) — Lăng kính thứ cho mô hình 8L

**Nguồn**: `oil_sector_sensitivity.py` + `oil_price_supplement.py` (Brent monthly 2013-2026 từ
`data/brent_monthly_full.csv`, vs `tav2_bq.ticker` / `ticker_financial`). Outputs:
`data/oil_sector_sensitivity.md`, `data/oil_price_supplement.md`, `data/oil_price_beta.csv`,
`data/oil_profit_corr.csv`.

## Universe theo vị trí chuỗi (ICB)
| Nhóm | ICB | Mã | Liquid |
|---|---|---|---|
| Upstream / dịch vụ mỏ | 573 | **PVD**(khoan) **PVS**(EPC/kỹ thuật) PVC(dung dịch khoan) PVB(bọc ống) | PVS PVD |
| Lọc dầu / phân phối | 533 | **BSR**(lọc Dung Quất) **PLX**(Petrolimex) **OIL**(PVOil) | BSR PLX OIL |
| Khí (gas) | 7573 | **GAS**(PV Gas) PGS CNG PGD PGC PVG | GAS |
| Phân bón / hoá chất (khí đầu vào) | 1357 | **DGC**(P-vàng) **DCM** **DPM**(ure) CSV | DGC DCM DPM |
| Vận tải biển dầu/khí | 2773 | **PVT** VIP VTO GSP PVP | PVT |

## PHÁT HIỆN 1 — Ảnh hưởng giá dầu lên LỢI NHUẬN (khác nhau theo vị trí chuỗi)
Corr quý của chỉ tiêu với Brent (level, level trễ 1-2 quý, và ΔNP-YoY vs ΔBrent-YoY).

| Nhóm | NP~lvl | NP~trễ1Q | NP~trễ2Q | ΔNP~ΔOil | Cơ chế |
|---|---|---|---|---|---|
| **Upstream** (PVD/PVC) | +0.30/+0.24 | +0.41/+0.37 | **+0.50/+0.46** | −0.11 | LEVEL + TRỄ: dầu cao bền → E&P capex → cầu khoan (trễ 6-12 th). KHÔNG phải inventory. |
| **Lọc/phân phối** (BSR/OIL) | **+0.68/+0.56** | +0.54/+0.25 | giảm | **+0.24/+0.32** | HƯỚNG giá (tồn kho)+crack: dầu tăng=lãi tồn kho. BSR NPM~oil **+0.72**. Phản ứng NGAY. |
| ⚠️ PLX (ngoại lệ) | −0.13 | −0.20 | −0.19 | −0.01 | Phân phối biên cố định/điều tiết → dầu tăng ÉP biên % + rủi ro tồn kho. **Ngược dấu BSR/OIL.** |
| **Khí** GAS | +0.39 | **+0.58** | +0.55 | +0.33 | Giá bán khí neo theo FO (~6th avg) → lãi theo dầu nhưng TRỄ 1-2 quý. |
| ⚠️ LPG hạ nguồn (PGC/PGD/PVG) | ~0 | ~0 | ~0 | +0.2 | GPM~oil **−0.5..−0.72**: mua khí giá neo dầu, không pass-through hết → ÉP BIÊN khi dầu tăng. |
| **Phân bón/hoá chất** (DCM/DGC/CSV) | **+0.50..+0.70** | +0.61..+0.64 | +0.51..+0.54 | +0.1..+0.24 | Corr cao & BỀN, NHƯNG là **đồng pha với energy-complex** (ure/phosphate toàn cầu), không phải dầu nhân-quả trực tiếp — siêu chu kỳ 2022 chi phối. Dầu thực ra là CHI PHÍ đầu vào. |
| **Vận tải** (PVT…) | +0.07 | +0.05 | +0.05 | +0.15 | **KHÔNG phải oil-profit play** — cước neo theo cung tàu/sản lượng, không theo giá dầu. |

## PHÁT HIỆN 2 — Ảnh hưởng lên BIẾN ĐỘNG GIÁ cổ phiếu
Oil-beta thô theo tháng ≈ 0 (R²<0.04): **beta thị trường VNINDEX lấn át hoàn toàn.**

**(A) Hồi quy 2 nhân tố (lọc market):** beta dầu RIÊNG nhỏ ở mọi nhóm (tối đa ~0.13 PVD/BSR/PVC).
Beta THỊ TRƯỜNG mới là động lực biến động: **Upstream bM 1.45 (PVD 1.48 — top beta cả thị trường)
→ vol năm 52%**. Lọc/phân phối bM ~1.2. Khí/phân bón bM 0.7-0.9 (phòng thủ hơn).
→ Đây là **cyclical beta-cao TRƯỚC, oil-play SAU**.

**(B) Horizon QUÝ** (ít nhiễu hơn tháng): oil-beta MẠNH LÊN ở Upstream (PVD 0.39, PVS 0.36) và
BSR (0.57). Link cơ bản chỉ lộ ở tần suất quý, bị rửa trôi ở tháng.

**(C) Event study — 30 tháng |Brent move|≥10%:** mọi nhóm KHUẾCH ĐẠI biến động và đi CÙNG CHIỀU dầu:
| Nhóm | mean\|r\| sốc | mean\|r\| thường | khuếch đại | cùng chiều dầu |
|---|---|---|---|---|
| Upstream | 15.5% | 9.0% | **1.73×** | 0.66 |
| Phân bón | 11.2% | 7.3% | 1.53× | 0.55 |
| Lọc/phân phối | 12.7% | 8.9% | 1.42× | 0.65 |
| Khí | 8.2% | 6.1% | 1.34× | 0.57 |
| Vận tải | 8.1% | 7.0% | 1.15× | 0.62 |
→ Cú sốc dầu CÓ chi phối biến động — nhưng **theo đợt (episodic), không liên tục**. Upstream khuếch đại mạnh nhất.

**Phân kỳ DẤU theo horizon** (insight quan trọng): phân bón có **oil-beta tháng ÂM** (DCM −0.13: nỗi
sợ chi phí đầu vào) nhưng **profit-corr quý DƯƠNG** (giá ure đầu ra). Cùng cú dầu, phản ứng GIÁ ngắn hạn
và LỢI NHUẬN trung hạn có thể ngược dấu.

## KHUNG ĐỀ XUẤT cho 8L — 4 kênh truyền dẫn dầu (KHÔNG đồng nhất)
1. **UPSTREAM SERVICES** (PVD, PVS, PVC, PVB): tín hiệu = **dầu LEVEL cao BỀN + trễ** (backlog/capex).
   Mua khi dầu cao kéo dài + chu kỳ hồi phục. Beta cao nhất TT → size theo vol. Profit trễ 1-2 quý.
2. **INVENTORY/CRACK** (BSR, OIL): tín hiệu = **HƯỚNG dầu (đang tăng)** → lãi tồn kho/crack ngay;
   dầu giảm = lỗ tồn kho. Đồng pha momentum với dầu. **Loại PLX** (điều tiết, ngược dấu).
3. **OIL-LINKED REVENUE** (GAS): dương nhưng CHẬM (trễ 1-2 quý theo FO). Hạ nguồn LPG (PGC/PGD/PVG)
   = bị ÉP BIÊN khi dầu tăng → KHÔNG phải oil-long.
4. **ENERGY-COMPLEX CO-CYCLICAL** (DPM, DCM, DGC): xử lý bằng **framework cyclical hàng hoá có sẵn**
   (`cyclical_multi.py` — ure/DAP/phosphate), KHÔNG coi là oil-play; dầu là phụ + là chi phí.
   PLX, LPG hạ nguồn, vận tải = oil-NEUTRAL/INVERSE-margin → không xếp vào oil-long.

## Bối cảnh LIVE (06/2026)
Brent vọt **$66→$117 (1→4/2026), nay ~$107** (cú sốc cung ~+75%). Theo độ trễ đã đo:
- **BSR, OIL**: lãi tồn kho/crack NGAY trong Q1-Q2/2026 (kênh phản ứng nhanh nhất).
- **GAS**: hưởng lợi nhưng TRỄ 1-2 quý (giá khí neo FO bình quân).
- **PVD/PVS**: cú hích lợi nhuận đến SAU 1-2 quý NẾU dầu giữ cao → backlog khoan; giá cổ phiếu beta cao = khuếch đại biến động.
- **PLX, LPG hạ nguồn, DCM/DPM (chi phí khí)**: chịu áp lực biên ngắn hạn.
- Regime biến động NÂNG CAO → nhóm này (đặc biệt upstream) sẽ dao động mạnh.

## DEEP-DIVE A — BSR: tách lãi/lỗ tồn kho khỏi crack (`oil_bsr_pvd_deepdive.py`)
⚠️ Fix dữ liệu: `ticker_financial.time` = **Release_Date** (~1 quý sau quý báo cáo) → phải merge giá dầu
theo nhãn `quarter`, không theo Period(time). (Part 1 ở trên lệch +1 quý; lượng-tính dưới đã đúng.)

Lợi nhuận BSR = **biên crack (theo MẶT BẰNG dầu) ± swing tồn kho (theo HƯỚNG dầu trong quý)**:
- Hồi quy `GPM ~ brent_avg + oil_qoq`: **LEVEL/crack giải thích R²=0.56** (động lực chính, bền);
  oil_qoq (tồn kho) chỉ thêm R²≈0.01 lên biên% — NHƯNG chi phối ĐUÔI lợi nhuận:
- Bucket theo hướng dầu trong quý: dầu **GIẢM>10% → 60% quý LỖ** (NP_tb −359 tỷ); đi ngang 6% lỗ;
  **TĂNG>10% → NP_tb +2.074 tỷ** (10% lỗ). Mọi cú dầu sập = trích lập NRV tồn kho → lỗ.
- Bằng chứng cực trị: 2018Q4 (dầu −27%) NP −1.010; 2020Q1 (−52%) NP −2.330; 2020Q2 NP −1.906 (đáy crack);
  2022Q1 NP +2.324; **2026Q1 (dầu +65%) NP +8.265 tỷ** (xác nhận LIVE: lãi tồn kho + crack rộng).
→ **BSR = trade HƯỚNG dầu (momentum)**: mua khi dầu xoay lên, tránh vào lúc dầu sập (rủi ro lỗ). Phản ứng NGAY.

## DEEP-DIVE B — PVD: độ trễ backlog theo chu kỳ giàn khoan
Cross-correlation `corr(metric[t], Brent_avg[t−lag])`, lag 0..8 quý:
| metric | đỉnh lag | corr đỉnh | ghi chú |
|---|---|---|---|
| **GPM** | **6Q** | **0.81** | biên trễ nhất — day-rate reprice chậm nhất |
| NP / NPM / Rev | 4Q | 0.67-0.69 | doanh thu/utilization phản ứng sớm hơn biên |
→ PVD trễ dầu **~4-6 quý (≈1-1.5 năm)** trung bình; điểm xoay cấu trúc còn dài hơn (**8-12 quý** để day-rate
repricing đủ): dầu đỉnh 2014 → GPM sập về ~2% mãi 2017-2018; dầu hồi 2020-2022 → GPM mới bật mạnh 2023Q2,
đỉnh 2024Q1 (24%). **2026Q1 dầu vọt nhưng PVD GPM vẫn 19%, NP 306 — CHƯA phản ánh** → kỳ vọng hích 2026H2-2027 nếu dầu giữ cao.
→ **PVD = trade LEVEL có ĐỘ DẪN**: dầu cao BỀN → mua TRƯỚC điểm uốn lợi nhuận ~2-4 quý (thị trường định giá trước);
đợi dầu spike rồi mới vào thì cổ phiếu đã chạy. Khác hẳn BSR (phản ứng tức thì theo hướng).

Output đầy đủ: `data/oil_bsr_pvd_deepdive.md`.

## DEEP-DIVE C — PVD: thị trường ĐỊNH GIÁ TRƯỚC độ trễ (`oil_pvd_anticip_gas.py`)
So sánh độ trễ theo dầu của **định giá (P/B)** vs **lợi nhuận (GPM)**:
| | đỉnh lag theo dầu | corr tại lag 0 |
|---|---|---|
| GPM (kết quả) | **5Q** (0.80) | 0.23 |
| **P/B (định giá)** | **3Q** (0.70) | **0.63** ← bám dầu gần như tức thì |
→ **P/B dẫn dắt GPM ~4 quý** (corr(GPM[t], PB[t−4])=0.68 đỉnh). Quan sát trực tiếp: 2021Q1→2022Q1 dầu
61→100, **P/B bật 0.50→0.77 trong khi GPM vẫn kẹt 4-9%** — định giá đi trước, lợi nhuận xác nhận sau (2023+ GPM 14→24%).
→ **Hệ quả giao dịch: P/B là tín hiệu DẪN (bám dầu lag 0-3Q, dẫn lợi nhuận 4Q); lợi nhuận chỉ XÁC NHẬN trễ.**
Mua PVD theo luận điểm dầu-cao-bền + P/B, KHÔNG chờ earnings turn (lúc đó cổ phiếu đã chạy). 2026Q1 P/B đã
nhảy 0.92→1.13 theo cú dầu dù GPM còn 19% → thị trường đã bắt đầu định giá trước.

## DEEP-DIVE D — GAS: level-play, trễ ngắn, biên ỔN ĐỊNH
Cross-corr NP/GPM/Rev vs dầu: **NP & Rev đỉnh lag 0Q (0.61)**, **GPM/NPM đỉnh lag 2Q** (giá bán neo FO bình
quân trượt ngắn). Trễ ~0-2Q — NGẮN HƠN HẲN PVD (4-6Q). Theo mặt bằng dầu: NP tăng đơn điệu THẤP→CAO
(2.057→2.935→3.063 tỷ) nhưng **GPM ỔN ĐỊNH ~20-21% bất kể dầu** → dầu chi phối DOANH THU/quy mô NP, không
chi phối biên (khác BSR: không có swing tồn kho; khác PVD: không trễ day-rate). Lưu ý: lợi nhuận GAS còn phụ
thuộc mạnh SẢN LƯỢNG khí (mỏ mới/nhu cầu điện) — dầu chỉ là 1 trong 2 trục.

### Bảng so sánh 3 mã thanh khoản chính (cách dầu truyền vào)
| | BSR | PVD | GAS |
|---|---|---|---|
| Biến tín hiệu | **Hướng**(tồn kho)+**level**(crack) | **Level** dầu cao bền | **Level** dầu |
| Trễ lợi nhuận | ~0 (tức thì) | **4-6Q** (cấu trúc 8-12Q) | **0-2Q** |
| Hành vi biên | swing theo crack, lỗ khi dầu sập | day-rate, trễ 6Q | **ổn định ~20%** |
| Định giá vs earnings | đồng pha | **P/B dẫn 4Q** | đồng pha |
| Cách chơi | momentum theo hướng dầu | mua TRƯỚC uốn (P/B dẫn), kiên nhẫn | beta level, trễ ngắn |
| Trục thứ 2 | công suất lọc | utilization giàn | **sản lượng khí** |
| Live 2026Q1 | đã ăn (+8.265 tỷ) | chưa ăn earnings, P/B đã chạy | NP theo dầu, biên ổn |

## Cảnh báo phương pháp
- Corr profit-oil của **phân bón bị thổi phồng bởi siêu chu kỳ 2022** (dầu+ure cùng tăng) → đồng pha,
  không nhân-quả. Link nhân-quả SẠCH nhất: BSR/OIL (tồn kho+crack), GAS (giá bán neo FO), PVD/PVC (E&P capex).
- R² giá theo tháng rất thấp → dầu KHÔNG dùng làm tín hiệu giá tần suất cao; chỉ giá trị ở (a) profit quý,
  (b) event-study cú sốc, (c) định khung kỳ vọng theo vị trí chuỗi.

---
name: oil_gas_chain_8l_2026
description: "Oil & gas sector added to 8L — Brent transmission differs by chain position (upstream lag, refine inventory, fert co-cyclical)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5f3d817b-c03a-49ee-a6dd-e01f08757a73
---

Nhóm xăng dầu (oil & gas) nghiên cứu cho 8L ([REDACTED]05). Brent monthly 2013-2026
(`data/brent_monthly_full.csv`, tải từ datasets/oil-prices GitHub) vs `tav2_bq.ticker`/`ticker_financial`.
Scripts: `oil_sector_sensitivity.py`, `oil_price_supplement.py`. Doc: `oil_8l_framework.md`.

**Phát hiện cốt lõi: chuỗi dầu KHÔNG đồng nhất — dầu truyền dẫn qua 4 kênh khác dấu/khác trễ:**
- UPSTREAM svc (PVD/PVS/PVC, ICB573): profit theo LEVEL+TRỄ (NP~oil 0.30→0.50 qua 2 quý), E&P capex. KHÔNG inventory (ΔNP~ΔOil âm). Beta market cao nhất TT (PVD bM 1.48, vol 52%).
- LỌC/PHÂN PHỐI (BSR/OIL, ICB533): profit theo HƯỚNG dầu+tồn kho, phản ứng NGAY (BSR NP~oil 0.68, NPM 0.72, ΔNP~ΔOil +0.24/+0.32). ⚠️ PLX NGƯỢC DẤU (−0.13, biên điều tiết → dầu tăng ép biên%).
- KHÍ GAS (ICB7573): dương nhưng TRỄ 1-2 quý (giá bán neo FO ~6th, NP~trễ1Q +0.58). Hạ nguồn LPG (PGC/PGD/PVG) GPM~oil −0.5..−0.72 = BỊ ÉP BIÊN khi dầu tăng.
- PHÂN BÓN/HOÁ CHẤT (DCM/DGC/DPM, ICB1357): profit-corr cao bền (0.5-0.7) NHƯNG = đồng pha energy-complex (siêu chu kỳ 2022), KHÔNG nhân-quả; dầu là CHI PHÍ đầu vào. Dùng framework cyclical_multi (ure/phosphate) thay vì coi là oil-play. Oil-beta THÁNG âm (cost fear) >< profit quý dương = phân kỳ dấu theo horizon.
- VẬN TẢI (PVT…, ICB2773): KHÔNG phải oil-profit play (NP~oil 0.07), cước theo cung tàu.

**Biến động giá**: oil-beta thô tháng ≈0 (R²<0.04, market beta lấn át). Lọc market (2-factor) → oil-beta riêng nhỏ (max 0.13). Horizon QUÝ mạnh hơn (PVD 0.39, BSR 0.57). Event study 30 tháng |Brent|≥10%: mọi nhóm khuếch đại (upstream 1.73×, fert 1.53×, refine 1.42×) + cùng chiều dầu (dir 0.55-0.66) → oil-shock chi phối vol theo ĐỢT không liên tục.

**Live 06/2026**: Brent vọt $66→$117 (1→4/2026) nay ~$107, cú sốc cung +75%. Theo trễ đã đo: BSR/OIL lãi tồn kho NGAY Q1-Q2; GAS hưởng trễ 1-2Q; PVD/PVS hích profit sau 1-2Q nếu dầu giữ cao (backlog); PLX/LPG/DCM-DPM chịu áp lực biên ngắn hạn.

**Deep-dive BSR/PVD** (`oil_bsr_pvd_deepdive.py`, `data/oil_bsr_pvd_deepdive.md`): ⚠️ ticker_financial.time=Release_Date (~1Q sau quý báo cáo) → merge giá dầu theo nhãn `quarter` KHÔNG theo Period(time) (Part-1 lệch +1Q). BSR: lợi nhuận = crack(LEVEL brent_avg, R²0.56 = động lực chính bền) ± tồn kho(HƯỚNG dầu trong quý, chi phối ĐUÔI: dầu giảm>10%→60% quý LỖ NP−359tỷ; tăng>10%→NP+2074tỷ). Cực trị 2020Q1 NP−2330, 2022Q2 +10149, 2026Q1 +8265 (dầu+65%). → BSR trade HƯỚNG dầu, phản ứng NGAY. PVD: cross-corr GPM đỉnh lag 6Q corr0.81, NP/Rev lag 4Q; điểm xoay cấu trúc 8-12Q (day-rate reprice chậm); 2026Q1 dầu vọt nhưng GPM vẫn 19% CHƯA phản ánh → hích 2026H2-2027. → PVD trade LEVEL có ĐỘ DẪN, mua TRƯỚC uốn lợi nhuận 2-4Q.

**PVD anticipation + GAS** (`oil_pvd_anticip_gas.py`, `data/oil_pvd_anticip_gas.md`): PVD — thị trường ĐỊNH GIÁ TRƯỚC: P/B bám dầu lag 0-3Q (corr 0.63-0.70) trong khi GPM trễ 5Q; **P/B dẫn dắt GPM ~4Q** (2021 dầu 61→100 P/B bật 0.50→0.77 dù GPM kẹt 4-9%, earnings xác nhận 2023+). → mua PVD theo dầu+P/B KHÔNG chờ earnings. GAS — level-play trễ NGẮN: NP/Rev đỉnh lag 0Q, GPM lag 2Q (FO trượt ngắn), biên ỔN ĐỊNH ~20% bất kể dầu (dầu chi phối DOANH THU không biên; trục 2 = sản lượng khí). 3 mã: BSR=hướng/tức thì, PVD=level/trễ-dài/PB-dẫn, GAS=level/trễ-ngắn/biên-ổn.

**WIRED vào 8L ([REDACTED]05)**: registry `data/oil_transmission_map.csv` (20 mã, hand-maintained như moat_tags) + loader `oil_transmission.py` (`load_oil_map`/`oil_tag`). unified_screener.py: thêm OIL_SET vào universe + overlay tag `⛽ OIL[chain·signal·lag]` (INVERSE_MARGIN/FREIGHT_NOT_OIL gắn cờ ⛽); dna_card.py: in dòng oil-transmission. Chạy OK (PVD/PVS/OIL/PVT/PVC vào TOP actionable). Additive, không đổi routing/verdict.

**Vận tải biển vs CƯỚC thế giới ([REDACTED]05, `shipping_freight_sensitivity.py`, `data/freight_rates_quarterly.csv`=BDI/SCFI/BDTI tái dựng XẤP XỈ)**: CÓ ảnh hưởng nhưng khác theo segment — DRY BULK (VOS/VNA NP~BDI +0.55-0.59) link MẠNH/SẠCH nhất, lỗ ở đáy cước; CONTAINER (HAH ~SCFI lag2Q +0.61) rõ ở bùng nổ 2021-22 nhưng 2024-25 NỚI do mở rộng đội tàu (NP đỉnh mới dù SCFI tb); TANKER (PVT) đệm bởi charter→ổn định, NP tăng khi BDTI giảm (VTO/PVP~0); CẢNG (GMD~0) sản-lượng-driven. → name lớn (HAH/PVT) fleet+charter tách dần spot. BDI now ~3100 (5/2026, mạnh). NB unified_screener đã có RATE_CYCLICAL (HAH/VOS/VTO/GMD…) = NPM-percentile freight-trap gate.

**WIRED freight lens + REAL feed ([REDACTED]05)**: (c) `data/freight_map.csv` (12 mã segment·index·sens·play) + `freight_map.py` (`load_freight_map`/`freight_tag`/`current_bdi`); overlay `🚢 FREIGHT[segment·index·NP~sens]` vào unified_screener (FREIGHT_SET→universe, 12 tagged) + dna_card; DRY_BULK hiện BDI live. (d) **Route bồi đắp BDI THẬT**: `fetch_bdi_daily.py` scrape handybulk.com (prose "X points", local network OK; investing API 403/stooq JS-gated) → `data/bdi_daily_real.csv` dedup-by-date; ĐÃ wire bước [10] vào `papertrade_daily.bat` (chạy 15:30 daily, forward-accumulate). current_bdi() đọc feed thật, fallback approx. Verified: VOS card hiện "BDI now 3037,real". Feed cước liên tục miễn phí KHÔNG có (paywalled hết) → series quý vẫn approx (validated vs avg năm thật 2022/2023); container cần Freightos CSV (email fbx@freightos.com).

Liên quan [[cyclical_commodity_framework_2026]] (cyclical contrarian buy-trough — phân bón thuộc đây), [[sugar_cyclical_trend_2026]] (cyclical trend). 8L manifest [[moat_5f_8l_bridge_2026]].

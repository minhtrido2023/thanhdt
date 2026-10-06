# Làn C — "rẻ theo tốc độ tăng lợi nhuận" cho funnel discretionary (job Taylor_20261005_180155, 2026-10-06)

Chỉ nghiên cứu. KHÔNG wire gì, không đụng production. Artifact cùng thư mục: `lane_c_backtest.py`,
`robustness.py`, `summary.csv`, `monthly.csv`, `panel.csv`, `dose_grid.csv`, `excess_by_year.csv`,
`known_deadline/summary.csv` (bản stress ngày công bố), `lag_events_prodgate.csv`, `live_20261006.csv`.
Interpreter `/home/trido/thanhdt/wc_venv/bin/python`, dữ liệu `data/bq_cache` (ticker tới 2026-10-05,
ticker_financial release tới 2026-08-21 = đủ Q2/2026; Q3 bắt đầu công bố khoảng 20/10).

## TL;DR
1. **Có edge ở cấp RỔ, sống cả IS lẫn OOS, và gần như không trùng LAG.** C1 "GARP" = rating≤3 ∧ golden floor ∧
   universe_pit ∧ **NP quý YoY ≥30% ∧ NP quý QoQ >0 ∧ 0<PE≤12**, rổ EW tái cân bằng tháng (T+1, phí 0,1%/chiều):
   vượt rổ rating≤3 cùng universe **+1,13%/tháng (t=5,3)**: IS 2014-19 t=3,2, OOS 2020+ t=4,5, OOS bỏ 2020-21 t=4,0;
   dương 12/13 năm (2024 ≈0). So với làn B (top-3/route theo 1/PE): +0,84%/tháng, t=3,1. DSR 0,996 (N=4) /
   0,989 (N=22 tính cả lưới độ nhạy), PBO 0,06.
2. **Nhưng đây là hiệu ứng của RỔ ~20 mã ăn đuôi phải, KHÔNG phải bộ chọn từng mã.** Mã trung vị trong C1
   **không** thắng trung bình cùng route (−0,11%/tháng, t=−0,6); hit-rate từng mã 49% so với 45% của rổ gốc.
   Chọn tay 1-2 mã từ danh sách này thì gần như tung đồng xu so với peer cùng ngành — trừ khi DD thật sự thêm thông tin.
3. **Hôm nay C1 ra 38 mã** (quá nhiều để DD, trần 2 DD/tuần). **PVT LỌT** (YoY +88%, QoQ +73%, PE 8,8).
   **DRI KHÔNG lọt** vì QoQ âm (Q2 63,8 tỷ < Q1 78,4 tỷ; YoY +192%). Bỏ điều kiện QoQ thì DRI lọt (47 mã).
4. **Khuyến nghị: (a) có điều kiện** — thêm làn C vào funnel làm **nguồn ý tưởng theo sự kiện công bố BCTC**,
   chỉ báo mã **MỚI vào** sau mỗi lần công bố, kèm nhãn "edge là của rổ, không phải của mã". Bằng chứng hiện có
   đủ để ĐƯA VÀO FUNNEL (rủi ro thấp: người vẫn quyết), KHÔNG đủ để nói 1 mã chọn tay sẽ thắng.
   Tín hiệu mạnh nhất trong nghiên cứu này thật ra là **một rổ GARP hệ thống** — đó là việc R&D riêng
   (chạy full engine + quant-skeptic + biodiversity so với custom30V/BAL), không thuộc funnel.
5. **PVT**: lãi tăng thật từ hoạt động chính (không phải lãi bất thường), rẻ theo run-rate (PE run-rate ~5,7,
   PEG ~0,3), nhưng đang ở **đỉnh chu kỳ cước do Hormuz** — rủi ro đảo chiều là rủi ro chính. Hợp làm đề xuất
   tay có DD (kịch bản cước bình thường hoá), không hợp làm ví dụ "chất lượng rẻ bị bỏ sót". Không có cảnh báo
   pháp lý mới ở PVT mẹ.

## 1. PVT — due diligence ngắn

**Số liệu** (`ticker_financial`, NP = lãi ròng theo nguồn BQ, nhiều khả năng là phần công ty mẹ — báo chí
ghi LNST Q1/26 387 tỷ (tổng) so với 319 tỷ ở BQ):

| Quý | NP (tỷ) | Doanh thu (tỷ) | GPM | EBIT margin | NPM | YoY NP | QoQ NP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q2/25 | 295 | 4.313 | 17,3% | 13,2% | 10,7% | +2% | +37% |
| Q3/25 | 263 | 4.419 | 15,2% | 11,4% | 8,5% | −28% | −11% |
| Q4/25 | 266 | 4.444 | 14,7% | 11,3% | 8,3% | +27% | +1% |
| Q1/26 | 319 | 4.177 | 14,2% | 10,9% | 8,3% | +48% | +20% |
| **Q2/26** | **553** | **5.714** | 15,1% | 12,1% | 9,4% | **+88%** | **+73%** |

- **Nguồn tăng**: doanh thu +32% YoY / +37% QoQ, biên EBIT nhích lên 12,1%. NPM (9,4%) < EBITM (12,1%) ⇒ không có
  dấu hiệu lãi ngoài hoạt động (cờ `_nonop` của LAG = NPM > 1,2×EBITM: KHÔNG kích hoạt). Theo báo chí: đội tàu
  đầu tư mới từ 2025 + cước cao. H1/2026 đã đạt **89% kế hoạch cả năm** 1.200 tỷ (kế hoạch đặt thấp, đi lùi −10%
  so với 2025) ⇒ khả năng vượt kế hoạch cao.
- **Tăng trưởng doanh thu đi kèm BIÊN GỘP GIẢM** từ ~21% (2024) xuống 14-15% — tăng trưởng 2025 đến từ quy mô
  (đội tàu, mảng biên thấp) nhiều hơn từ giá. Q2/26 là quý đầu biên hồi lại.
- **Định giá** (giá 24.200 ngày 05/10, OShares 517 triệu sau trả cổ tức cổ phiếu ~10%): PE TTM 8,8 (TTM NP 1.401 tỷ,
  tăng 29% so với TTM trước). **PE run-rate (Q2×4) ≈ 5,7. PEG (theo TTM) ≈ 0,30**; theo YoY quý ≈ 0,10.
  PB 1,01, pb_z +0,73 (đắt hơn lịch sử của chính nó — vì thế làn A/B không thấy).
- **Chu kỳ cước**: VLCC Trung Đông–Trung Quốc kỷ lục ~800 nghìn USD/ngày (09/2026) vì gián đoạn Hormuz; dự báo
  Hormuz mở lại dần từ Q3/2026, không bình thường hoá hết trong năm; giới phân tích kỳ vọng cước >100 nghìn
  USD/ngày sang 2027. **Phía cung**: 126 VLCC đặt đóng chỉ trong Q1/2026 (cả 2025: 82), orderbook/đội tàu >30%
  ⇒ áp lực giảm cước khi tàu giao 2027-2028.
  ⚠️ GIẢ ĐỊNH chưa kiểm: PVT chủ yếu chạy tàu dầu/hoá chất/LPG cỡ nhỏ-trung và một phần cho thuê định hạn
  (gồm cho BSR) ⇒ nhạy với cước giao ngay KÉM hơn VLCC — cả chiều lên lẫn chiều xuống. Cần đọc BCTC/thuyết minh
  cơ cấu hợp đồng trước khi dùng con số run-rate.
- **Rủi ro đảo chiều**: (1) Q2/26 có thể là đỉnh — run-rate ×4 phóng đại nếu cước giảm; PE TTM 8,8 mới là mức
  "nếu không tăng nữa"; (2) giá đã từng lên 28.600 (PE 12,9) hồi 03/2026 khi khủng hoảng nổ ra rồi rơi về 20.250
  — thị trường định giá PVT như cổ phiếu chu kỳ sự kiện; (3) capex 3.445 tỷ mở rộng đội tàu (kế hoạch 2026) mua
  tàu ở giá đỉnh chu kỳ; (4) quản trị: Tổng giám đốc từ nhiệm sau hơn 2 tháng nhậm chức (2026).
- **Pháp lý (luật 2026-09-27 — chỉ WARNING)**: không tìm thấy khởi tố/xử phạt mới với PVT mẹ. Có tiền lệ HoSE
  nhắc nhở **PVP** (công ty con PVTrans Pacific) chậm công bố quyết định xử phạt thuế (QĐ 1068/QĐ-CT 04/04/2024)
  — mức nhỏ, cũ. Đây là tra cứu web nhanh, chưa qua legal-vn.
- **LAG**: Q2/26 của PVT **qua gate LAG backtest** (NP_R 87,6 ≥15, prior_n_good 28, pa_HL3 5,0 — sát ngưỡng 5),
  entry lý thuyết 05/08, exit 14/09. Không thấy lệnh LAG mua PVT trong plan SpaceX 08/2026 (chưa tra lý do:
  funding/ADV/forensic live). DRI thì LAG ĐÃ mua (plan 07/08, 10/08).

**Kết luận PVT**: tăng trưởng thật, rẻ theo lợi nhuận hiện tại, nhưng là **cược vào độ bền của cú sốc cước**,
không phải "chất lượng bị định giá sai". Nếu user muốn vào: DD phải có kịch bản cước bình thường hoá
(NP quay về ~300 tỷ/quý ⇒ PE ~10-11 ở giá hiện tại) và điểm thoát khi tín hiệu Hormuz mở lại.

## 2. Thiết kế làn C và kết quả hôm nay

**Nguồn & PIT** (đã tra `kb/data_registry/`): `ticker_financial` (CANONICAL; không dùng `OShares`/`IntCov_P0`),
ngày biết = `Release_Date` (thiếu thì `time`), dùng quý có ngày biết **< ngày tái cân bằng** (assert trong code).
PE = `tav2_bq.ticker.PE` ngày d (cơ sở giá thô ⇒ PIT, registry valuation (4)). Universe = `universe_pit`
(`tav2_mike`, cache) ∩ `pass_golden_floor` ∩ `rating_8l≤3` ∩ không banned — **không dùng ticker_prune**.
Route lấy từ `rating_8l_history.csv` — ⚠️ TRAP: route không PIT trước 2026 (chỉ ảnh hưởng thước đo so cùng route
và làn top-3/route, không ảnh hưởng C1).

**4 cấu hình khai trước (N_trials=4, ngưỡng chốt trước lần chạy đầu):**
| Mã | Định nghĩa |
|---|---|
| C1 GARP | NP_P0/NP_P4−1 ≥ 30% ∧ NP_P0/NP_P1−1 > 0 ∧ 0 < PE ≤ 12, EW mọi mã đạt |
| C2 PEG | tăng trưởng TTM ≥ 15% ∧ 0 < PEG ≤ 0,5 (PEG = PE / (100·g_TTM)), EW |
| C3 RUNRATE3 | top-3/route theo 1/PE_run, PE_run = PE·TTM/(4·NP_P0), cần YoY>0 |
| C4 PEG3 | top-3/route theo g_TTM/PE, cần g_TTM>0 |

**Live 06/10** (`data/rating_8l.csv` 05/10 + quý mới nhất đã công bố; vũ trụ funnel: rating≤3 ∧ golden floor ∧
liq≥0,3 tỷ ∧ không banned/forensic-exclude = 133 mã):
- **C1 = 38 mã**: ngân hàng MBB HDB ABB VPB VCB; COMPOUNDER HII DC4 VGS VLB DHB DXP NNC NCT VTO SAS VGT PAT PGC KSB
  PVP CAP DHC AIG DVP **PVT** NTP KSV MWG SCL; CYCLICAL DCM CSV DPM PHR; POWER QTP; BĐS IDC VRE SIP NTC.
- Thêm nếu bỏ QoQ (C1b, 47 mã): PAN BSR SGP TV2 **DRI** HPG DPR PPC VHM.
- TV1 không lọt (YoY +8%). Lưu ý: các mã có YoY khổng lồ (DHB +1.383%, PPC +1.053%, BSR +782%) thường do nền
  so sánh thấp/lãi một lần — DD phải loại trước.

## 3. Bằng chứng (backtest PIT tháng, 2014-01 → 2026-09, 153 kỳ)

Pre-flight power (`rnd_preflight_power.py`, per-day/12 obs/năm, N_trials=4): **MARGINAL** nếu edge thật ~Sharpe
vượt trội 0,5; chỉ phát hiện được ≥0,77. Kết quả đo được (IR 1,49) vượt ngưỡng đó — nhưng chính vì effect lớn
hơn kỳ vọng nên đã săn rò rỉ trước khi tin (mục "kiểm tra" dưới).

| Leg | CAGR FULL | Sharpe | MaxDD | Vượt BASE /tháng (t) | IS t | OOS t | OOS bỏ 2020-21 t | Số mã TB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE rổ rating≤3 | 13,6% | 0,75 | −37,8% | — | — | — | — | 136 |
| Làn B (1/PE top-3/route) | 17,0% | 0,83 | −37,3% | +0,29% (1,5) | 1,0 | 1,1 | 0,2 | 17 |
| **C1 GARP** | **29,5%** | **1,35** | −31,7% | **+1,13% (5,3)** | **3,2** | **4,5** | **4,0** | 20 |
| C2 PEG | 16,1% | 0,82 | −41,0% | +0,20% (1,9) | 2,3 | 0,4 | 0,2 | 55 |
| C3 RUNRATE3 | 24,0% | 1,13 | −32,2% | +0,76% (3,5) | 2,2 | 2,7 | 2,5 | 16 |
| C4 PEG3 | 14,5% | 0,74 | −39,2% | +0,09% (0,5) | 0,6 | 0,1 | 0,1 | 16 |

So cùng route (mỗi mã trừ trung bình route cùng tháng): C1 +1,19%/tháng t=6,4.
**Bài học thiết kế**: các bản dùng tăng trưởng TTM (C2, C4) KHÔNG có edge; bản dùng **quý gần nhất** (C1, C3) có.
Tín hiệu là "lợi nhuận quý vừa công bố đang tăng tốc", không phải "PEG thấp".

**Kiểm tra rò rỉ / độ bền** (`robustness.py`, `known_deadline/`):
- **Stress ngày công bố** — đặt ngày biết = max(Release_Date, hạn luật: quý +45 ngày, Q4 +90 ngày, TT96/2020):
  C1 vẫn +0,90%/tháng t=4,9 (IS 3,4 / OOS 3,5 / OOS bỏ 2020-21 3,6). **C3 sụp** (OOS t=0,4) ⇒ C3 sống nhờ trôi giá
  ngay sau công bố (= vùng LAG), C1 thì không phụ thuộc thời điểm.
- Winsor lợi nhuận mã 1/99: không đổi (+1,31%, t=6,8).
- **Trung vị mã**: −0,11%/tháng so với route (t=−0,6); hit 49,4% vs 45%. Phân vị p10/p50/p90 của mã C1 so route:
  −9% / 0% / +13% mỗi tháng ⇒ edge = đuôi phải dày hơn + tránh đuôi trái, không phải mã điển hình tốt hơn.
  (Trung vị C1 trừ trung vị BASE: +0,71%/tháng t=4,5 — mã C1 điển hình vẫn tốt hơn mã điển hình của rổ gốc.)
- **Thanh khoản**: chỉ mã liq≥3 tỷ: +0,96% (IS t=1,5 / OOS t=3,5); liq≥10 tỷ: +0,54% (IS −0,18 / OOS t=2,4).
  ⇒ Trước 2020 edge nằm ở mã nhỏ; từ 2020 có cả ở mã thanh khoản cao. 46% mã C1 có liq<3 tỷ.
- **Phân rã**: chỉ tăng trưởng (không trần PE) +0,79% t=5,0; chỉ rẻ (PE≤12) +0,22% t=3,1;
  **rẻ mà lợi nhuận đang giảm (PE≤12 ∧ YoY<0) −0,70%/tháng t=−4,4** ⇒ điều kiện tăng trưởng chủ yếu là
  **bộ lọc bẫy giá trị** — đúng loại mã làn B (1/PE) đang kéo vào.
- **Lưới độ nhạy** (18 ô: YoY 15/30/50% × PE≤8/12/15 × có/không QoQ): **18/18 ô dương cả IS lẫn OOS**, t FULL
  2,3-5,9. Bỏ QoQ giảm lợi nhuận/mã ~0,3%/tháng nhưng tăng số mã. Không có đỉnh nhọn ⇒ không phải overfit ngưỡng.
- **Theo DT5G**: dương ở cả 5 trạng thái (CRISIS +0,84% n=24, BEAR +1,14% n=13, NEUTRAL +1,17% n=92, BULL +1,09%
  n=21, EX-BULL n=3).
- Self-check: lợi nhuận tháng tính lại bằng đường pivot độc lập khớp groupby (|diff| 2,8e-17); assert không quý nào
  có ngày biết ≥ ngày tái cân bằng; mã mất giá giữa kỳ dùng giá cuối cùng (không bỏ mã ⇒ không survivorship).

**Trùng với LAG** (gate production: NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5, forensic; giữ T+5→T+30):
- 43,5% lượt chọn C1 có quý tín hiệu là sự kiện LAG; 17,4% đang được LAG giữ tại ngày vào.
- **Phần KHÔNG trùng LAG mạnh hơn**: +1,67%/tháng t=6,6 (IS 5,4 / OOS 4,0); phần trùng LAG +0,88% t=2,7.
- Tương quan tháng giữa phần vượt trội của C1 và của proxy LAG = **0,02**; trong ¼ số tháng LAG tệ nhất, C1 vẫn
  vượt +0,91%/tháng (bằng các tháng khác). ⇒ C1 thêm thứ LAG không có: LAG chỉ giữ 25 phiên quanh công bố và đòi
  lịch sử phản ứng tốt (prior_n_good≥4); C1 giữ suốt quý và không cần lịch sử đó.
- ⚠️ proxy LAG = rổ EW sự kiện theo tháng vào lệnh, KHÔNG phải NAV LAG thật (LAG thật bị giới hạn tiền ~6×) ⇒
  test biodiversity mới đạt PARTIAL (2/3: trực giao + sống khi LAG chết; chưa đo ΔSharpe/ΔCalmar của sổ ghép).

**Đối chiếu nghiên cứu cũ** (step 12):
- d_NPR (gia tốc YoY) có IC tốt (+0,083, mạnh OOS) nhưng **lọc cứng trong LAG thì hỏng** (−1,44pp FULL, 2026-06-27).
  Không mâu thuẫn: ở đây tăng trưởng là điều kiện VÀO rổ giữ cả quý, không phải bộ lọc cắt sự kiện LAG.
- Top-5 sau mùa BCTC theo value_score (2026-08-18): NO-GO vì edge dồn vào 2020-21. C1 thì dương 12/13 năm và OOS
  bỏ 2020-21 vẫn t=4,0 — khác cơ chế (tăng trưởng + rẻ, không phải chỉ rẻ).
- Làn B / composite value làm bộ chọn = NO: khớp với ở đây (làn B chỉ +0,29%, t=1,5).

## 4. Kết luận

**(a) — thêm làn C vào funnel, tiêu chí:**
- rating≤3 ∧ golden floor ∧ liq≥0,3 tỷ ∧ không banned/forensic (như làn A/B)
- NP quý YoY ≥30% (NP_P4>0) ∧ NP quý QoQ >0 ∧ 0<PE≤12, theo quý **đã công bố** (Release_Date < hôm nay)
- **Chỉ báo mã MỚI vào** (thường dồn vào 4 đợt công bố/năm; backtest: ~5-7 mã mới/tháng trên universe_pit),
  xếp theo PE tăng dần trong từng route; DD loại mã có YoY do nền thấp/lãi một lần (YoY > 300% ⇒ đánh dấu).
- Nhãn bắt buộc trên mỗi dòng: "edge là của RỔ (~20 mã, trung vị mã ≈ peer cùng ngành) — DD phải tự thêm thông tin".
- Đo trung thực như Tầng 3: ghi mọi mã làn C + forward excess 6/12 tháng so rổ rating≤3 cùng route; checkpoint 2027-04-06.

**(b) — PVT-loại vẫn cần đề xuất tay + DD** khi luận điểm là cú sốc chu kỳ (cước, giá hàng hoá): làn C bắt được
PVT bằng số, nhưng không đánh giá được độ bền của cú sốc. DRI không lọt C1 (mùa vụ cao su làm QoQ âm) — nếu user
muốn bắt loại đó, bỏ QoQ (C1b, bằng chứng gần ngang) nhưng thêm ~9 mã/lần.

**Không làm, cần quyết riêng:** một **rổ GARP hệ thống** (giữ cả rổ C1) là tín hiệu mạnh nhất ở đây, nhưng
muốn đi tiếp phải: full-engine với chi phí/ADV thật, biodiversity đủ 3 test so với custom30V/BAL, quant-skeptic.

## 5. Giới hạn
- Kết quả cấp rổ, EW, tái cân bằng tháng, phí 0,1%/chiều; chưa mô hình ADV/slippage; 46% mã liq<3 tỷ.
- Route không PIT trước 2026 (TRAP); rating_8l lịch sử là bản dựng lại.
- `NP_P*` có thể bị nguồn cập nhật lại về sau (chưa kiểm vintage); stress ngày công bố chỉ kiểm thời điểm, không
  kiểm số bị sửa.
- Proxy LAG không phải NAV thật; chưa đo ΔSharpe sổ ghép.
- IR 1,5 lớn hơn kỳ vọng ⇒ cần quant-skeptic trước khi dùng con số này cho bất kỳ quyết định size/wire nào.
- DD PVT là bản ngắn, nguồn web + BQ; cơ cấu hợp đồng thuê tàu chưa kiểm; pháp lý chưa qua legal-vn.

Nguồn web: [mekongasean — kế hoạch 2026](https://mekongasean.vn/pvtrans-dat-ke-hoach-lai-sau-thue-1200-ty-dong-nam-2026-52036.html),
[mekongasean — vận tải biển Q2/2026](https://mekongasean.vn/van-tai-bien-quy-22026-nguoi-thang-lon-ke-hut-hoi-58346.html),
[mekongasean — capex đội tàu](https://mekongasean.vn/pvtrans-len-ke-hoach-loi-nhuan-di-lu-i-du-chi-3445-ty-dong-mo-rong-doi-tau-53181.html),
[mekongasean — TGĐ từ nhiệm](https://mekongasean.vn/tong-giam-doc-pvtrans-tu-nhiem-sau-hon-2-thang-nham-chuc-56903.html),
[Veson — Shipping outlook Q3 2026](https://veson.com/blog/shipping-market-outlook-q3-2026/),
[gCaptain — tanker rates](https://gcaptain.com/surging-tanker-rates-signal-a-deepening-global-energy-crisis/),
[Thời báo Tài chính — HoSE nhắc PVP](https://thoibaotaichinhvietnam.vn/hose-nhac-nho-pvtrans-pacific-cham-cong-bo-thong-tin-bi-xu-phat-ve-thue-151054.html).

## Phụ lục 2026-10-06 (job Taylor_20261006_052500) — tính mùa vụ
Xem `season_20261006/report.md`. Tóm tắt: theo dữ liệu, DRI KHÔNG phải mã mùa vụ (η² log-QoQ 0,10 < 0,6) nên
vẫn bị loại vì QoQ âm. Biến thể mùa vụ đã ship (C1S) không làm xấu edge: +1,14%/tháng, t=5,5. Biến thể cho DRI
lọt (C1A, áp cho mọi mã) có IS/OOS lệch dấu, cần user quyết. "YoY quý trước > 0" thay cho QoQ làm xấu edge
(t=−2,5) nên đã loại.

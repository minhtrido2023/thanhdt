# Factor Gap Audit — hệ thống đang THIẾU chỉ số gì so với quỹ thị trường phát triển?

**Job:** `Taylor_20260720_105222` · **Tác giả:** Taylor (Quant) · **Ngày:** 2026-07-20
**Loại:** KHẢO SÁT / KIỂM KÊ. **KHÔNG backtest candidate nào trong job này.** Mục tiêu duy nhất =
tạo danh sách ưu tiên để Mike/user chọn 2-3 cái cho vòng nghiên cứu thật tiếp theo.

> ⚠️ **Đọc trước khi dùng bảng ưu tiên:** cột "Ưu tiên" ở §3 xếp theo **tiền đề** (có dữ liệu không
> + có hợp đặc thù VN không), **KHÔNG theo edge** — chưa candidate nào được test. Một factor "Ưu
> tiên Cao" chỉ có nghĩa "rẻ để kiểm chứng và có lý do tiên nghiệm hợp lý", không có nghĩa "sẽ có
> alpha". Lịch sử fleet đã có nhiều factor hợp lý về mặt lý thuyết bị REFUTE khi đo thật
> (gq_score, liq-tilt, composite v3 as selector — xem `kb/context_pack.md` mục "Đã thử, BỊ LOẠI").

---

## §1 — Kiểm kê THẬT: hệ thống ĐANG CÓ gì

Nguồn: `INFORMATION_SCHEMA.COLUMNS` thật của `tav2_bq.ticker` / `ticker_financial` / `risk_rating`,
đọc code `signal_v11_sql.py`, `custom_basket.py`, `rating_8l.py`, `pt_v23_audit_2014.py`,
`lag_live_schedule.py`, `macro_state_live.py`, `golive_recommend_v23.py`, `filter.json`.
Phân biệt rõ 3 mức: **PROD** (nằm trong đường tiền thật) · **RESEARCH** (đã prototype, chưa wire) ·
**COLUMN-ONLY** (có cột trong BQ nhưng không ai đọc).

### (a) Fundamental / Value

| Chỉ số | Trạng thái | Nơi dùng |
|---|---|---|
| 1/PE (earnings yield) | **PROD — factor thống trị** | `custom_basket.py` SELECT_MODE=`eyonly`; 8L value_score (0.65·1/PE sector-neutral); IC +0.125 |
| PB / pb_z (relative) | **PROD** | `rating_8l.py` value_score axis-2 (0.35·pb_z); **CAPIT basket chọn theo pb_z cực âm** (`golive_recommend_v23.py:284-322`) |
| 1/PCF (cash-flow yield) | **PROD** | 8L composite v3 (route COMPOUNDER); yieldcombo BAL |
| 1/PS | **PROD** | 8L composite v3 |
| EV/EBITDA (EVEB) + MA/SD 5Y/1Y/3M | **PROD (nhánh riêng)** | route `DA_HEAVY_SET` trong `rating_8l.py` — lens value cho tên nặng khấu hao |
| PE/PB/EVEB vs MA-SD lịch sử (z-score theo chính nó) | **PROD** | SIGNAL_V11 term PE vs `PE_MA5Y±SD` |
| DY (dividend yield) | **PROD, đơn lẻ** | `filter.json` `_CashCowStock` (DY>0.022), `_DividendYield`; Dividend_Min3Y/1Y/3Y có cột |
| PEG | COLUMN-ONLY | có cột, không thấy consumer prod |
| DCF / margin-of-safety | **PROD (phụ trợ)** | `dcf_valuation.py`, `BASKET_DCF_W` tilt; `alt_valuation_lens.py` (lăng kính thay thế khi NOT_COMPUTED) |
| BVPS, EPS_P0, OShares | COLUMN-ONLY / normalizer | OShares chỉ dùng làm nhân market-cap |

### (b) Fundamental / Quality

| Chỉ số | Trạng thái | Nơi dùng |
|---|---|---|
| ROE / ROIC (3Y/5Y/10Y avg + **_Min3Y/5Y/10Y floor**) | **PROD — xương sống** | `rating_8l.py` scorecard; golden floor `ROE_Min3Y≥0 ∧ CF_OA_3Y>0`; TRAP gate ROE_Min3Y<0 |
| FSCORE (Piotroski 0-9) + FSCORE_P1 | **PROD** | SIGNAL_V11 term; CAPIT basket screen |
| CF_OA_P0..P4, CF_OA_3Y/5Y (CFO/assets) | **PROD** | golden floor; "mua khi sợ hãi có tính toán"; 8L CFO-3Y confirm ± |
| Debt_Eq / STLTDebt_Eq / IntCov / FinLev | **PROD** | 8L trough-leverage gate, real_lev fortress test |
| GPM_P0..P7 (gross **margin**) | **PROD (proxy moat)** | `rating_8l.py` `moat_tag()` quant proxy (GPM/ROE) |
| NPM / EBITM / ROA_P0/P4 | **PROD (phụ)** | LAG non-operating filter `NPM_P0>1.2·EBITM_P0` (OFF mặc định) |
| Vòng quay & chu kỳ tiền (AssetTurn, DSO/DIO/DPO, CashCycle, InvTurn) | COLUMN-ONLY | có đủ cột P0/P4, không consumer prod |
| Thanh khoản BS (CR, QuickR, CashR) | COLUMN-ONLY | |
| Moat 5F audit (WIDE/NARROW/NONE) | **PROD — thủ công** | `data/moat_tags.csv`, notch +1 chỉ khi WIDE |
| Forensic / anomaly flags | **PROD** | `data/forensic_flags.csv` (LAG gate ON), `anomaly_scan.py` → `data/anomaly_flags.json` (CAPIT due-diligence gate, wire 2026-07-20) |

### (c) Technical

| Chỉ số | Trạng thái | Nơi dùng |
|---|---|---|
| D_RSI (+ Max/Min 1W/3M, T1, T1W, MinT3) | **PROD** | SIGNAL_V11 (3 bậc điểm); nhiều filter `filter.json` |
| MA10/20/50/200 + _T1 (độ dốc) | **PROD** | SIGNAL_V11: Close>MA50>MA200, Close>MA20, slope MA50 |
| MACD / D_MACDdiff | **PROD** | SIGNAL_V11 (+15 khi >0) |
| Volume thrust (Volume vs Volume_3M_P50×1.3) | **PROD** | SIGNAL_V11 |
| Khoảng cách đỉnh 3M (`Close/HI_3M_T1`), `ID_HI_3Y` | **PROD** | SIGNAL_V11 — đây là **biến thể 52-week-high proximity** (George-Hwang) |
| Thanh khoản (Volume_3M_P50×Price, Trading_Value_1M_P50) | **PROD — sàn + selector** | sàn 1e9 SIGNAL_V11; **custom30V chọn top-30 THUẦN theo thanh khoản quý trước** |
| CMF / MFI / CMB / VAP / Res_1Y-Sup_1Y | COLUMN-ONLY hoặc filter.json legacy | không có trong SIGNAL_V11 |
| Momentum giá (PC1W..PC_6M) | **ĐÃ ĐÓNG có chủ đích** | kênh MOM_N/MOM_S đóng khỏi TIER_BAL 2026-07-12 sau chuỗi R&D đầy đủ |
| Exit kỹ thuật | **KHÔNG CÓ** | exit prod = thời gian + stop cố định (BAL 45d/−20%, LAG 25d/no-stop); không có exit theo indicator |

### (d) Macro / Regime

| Chỉ số | Trạng thái |
|---|---|
| DT5G 5-state (base v3.4b + DT 4-gate + macro cap) | **PROD** — `vnindex_5state_dt5g_live` qua `get_gated_state()` |
| Pillar A: lãi suất điều hành SBV (momentum 6m, lag 5d) | **PROD** (easing FLOOR đã tắt 2026-06-03) |
| Pillar A′: lãi suất huy động | **PROD phần theo dõi** — gate 7.5%, hiện 6.8% (cách 70bps) |
| Pillar B: VIX + SPX drawdown 1Y | **PROD** |
| Breadth: % `ticker_prune` trên MA200 | **PROD** — chỉ dùng cho breadth-decoupling guard (chặn cap US khi VN-US phân kỳ) |
| Breadth: % `ticker_prune` có D_RSI<0.3 (oversold) | **PROD** — trigger washout CAPIT, gate 0.30 |
| % trên MA50 | RESEARCH (`vnindex_5state_v2g_full.py`) |
| VNINDEX_PE, VNINDEX RSI/CMF/MACD | **PROD (một phần)** | |

### (e) LAG book (PEAD) — chi tiết vì hay bị nhầm với "revision"

`surprise_B_MA = (NP_P0 − mean(NP_P1..P4)) / |mean|`, clip ±5. Gate: `NP_R≥15 ∧ prior_n_good≥4 ∧
pa_HL3≥5`. Vào lệnh release+5 phiên, giữ 25 phiên, không stop. Tier nhị phân LAG_HI/LO (9%/8%).
→ Đây là **SUE kiểu random-walk 4 quý**, **KHÔNG có analyst estimate**, không có leg momentum giá.

---

## §2 + §3 — Candidate × khả thi × phù hợp VN × ưu tiên

Ký hiệu dữ liệu: **A** = có sẵn trong BQ, 0 nguồn mới · **B** = tính được từ BQ nhưng cần dựng
lịch sử/thận trọng · **C** = cần nguồn NGOÀI hoàn toàn mới (rào cản lớn).

| # | Candidate | Cơ chế (1 dòng) | Độ phổ biến ngành | Hệ thống đã có? | Dữ liệu VN | Phù hợp VN | **Ưu tiên** |
|---|---|---|---|---|---|---|---|
| 1 | **Gross profitability (Novy-Marx)** GP/Total Assets | Lợi nhuận gộp / tổng tài sản = "quality" ít bị bóp méo nhất trên BCTC | Rất cao — factor quality chuẩn của AQR/DFA/Robeco từ 2013 | **KHÔNG** — chỉ có GPM (biên), chưa scale theo tài sản | **A** (`GPM_P0 × Revenue_P0 / totalAsset_P0`) | Cao — ít phụ thuộc mục kế toán dễ chỉnh (khấu hao, dự phòng, "lợi nhuận khác") | **CAO** |
| 2 | **Accruals (Sloan 1996)** (NI−CFO)/TA | Lợi nhuận kế toán tách khỏi tiền thật → hoàn nhập; dấu IC ÂM | Rất cao — có trong hầu hết mô hình quality/earnings-quality | Prototype RESEARCH (`ic_panel_ext_q3.py:60-62`), **chưa prod**. Prod chỉ so CF_OA vs NP thô | **A** (`NP_P0/totalAsset_P0 − CF_OA_P0`) | **Rất cao** — công bố yếu hơn DM ⇒ dư địa bóp méo lớn hơn ⇒ signal thường MẠNH hơn ở EM | **CAO** |
| 3 | **Breadth sâu hơn** (A/D line, new-high/new-low, % trên MA20/50/100) | Đo độ rộng tham gia; phân kỳ breadth vs index báo trước đảo chiều | Cao ở tầng market-timing (không phải stock-selection) | Chỉ 2 metric: %>MA200 và %RSI<0.3 | **A** — tính thẳng từ `ticker_prune` | Trung-Cao — nhưng đuôi kém thanh khoản làm nhiễu A/D; phải giới hạn universe `ticker_prune` | **CAO** (rẻ nhất, 0 nguồn mới) |
| 4 | **Low-vol / low-beta (BAB, Frazzini-Pedersen)** | Cổ phiếu beta thấp có return điều chỉnh rủi ro cao hơn | Rất cao — cả một dòng sản phẩm "min-vol" của quỹ DM | **Beta/Dev CÓ CỘT nhưng CHƯA BAO GIỜ dùng làm factor chọn cổ phiếu** — chỉ là bin eligibility (`Risk_Rating≤5/6` trong `filter.json` legacy) và metric hiển thị | **A** (`risk_rating.Beta`, nhớ DISTINCT — bảng có dòng trùng) | Trung bình — VN sở hữu tập trung ⇒ beta đo được nhiễu; low-vol dễ trùng lặp với tilt value hiện có | **CAO** (rẻ, và là "lỗ hổng dùng sai mục đích" rõ nhất) |
| 5 | **Asset growth / investment factor (CMA)** ΔTotal Assets YoY | Công ty bành trướng tài sản nhanh → underperform sau đó | Rất cao — là 1 trong 5 nhân tố Fama-French 2015 | **KHÔNG** | **B** — `totalAsset_P0` chỉ có P0, phải dựng chuỗi từ dòng quý trước (point-in-time cẩn thận) | Cao — VN đầy case tăng vốn/bành trướng BĐS rồi sập | **TRUNG-CAO** |
| 6 | **Altman Z-score / distress** | Điểm tổng hợp dự báo phá sản | Cao, nhưng ở DM thường dùng làm **gate loại trừ**, không phải factor return | Prototype RESEARCH (`test_fa_extensions.py:200-205`, biến thể Z″) | **B — KHUYẾT** Retained Earnings không có trong BQ ⇒ chỉ dựng được biến thể rút gọn | Trung bình — VN gần như không có phá sản kiểu Chapter 11; "kiệt quệ" biểu hiện qua hủy niêm yết/đình chỉ. Đã có gate leverage 8L + forensic flags phủ phần lớn | **TRUNG** (overlap cao với cái đã có) |
| 7 | **Net share issuance** ΔOShares YoY | Phát hành ròng nhiều → return kém (dilution + market timing của ban lãnh đạo) | Rất cao | **KHÔNG** — OShares chỉ dùng nhân market-cap | **B** | ⚠️ **CẢNH BÁO VN:** cổ tức cổ phiếu / thưởng cổ phiếu cực phổ biến ở VN ⇒ ΔOShares thô **KHÔNG** = pha loãng kinh tế. Phải tách phát hành-lấy-tiền khỏi chia-tách. Nếu không tách, factor này gần như chắc chắn cho tín hiệu rác | **TRUNG** (điều kiện: tách được corp-action — Winston có pipeline corp-action) |
| 8 | **Shareholder yield tổng hợp** (DY + buyback − issuance) | Tổng tiền trả về cổ đông, đầy đủ hơn DY đơn lẻ | Cao (Cambria/O'Shaughnessy phổ biến hoá) | Chỉ có DY | **C phần buyback** — BQ không có cổ phiếu quỹ (Treasury stock). Cần nguồn mới | Thấp-Trung — **mua cổ phiếu quỹ ở VN hiếm và bị siết** thủ tục; leg này gần như rỗng ⇒ giá trị gia tăng so với DY hiện có là nhỏ | **THẤP** |
| 9 | **Giao dịch nội bộ (insider)** | Nội bộ mua = tín hiệu tích cực | Cao ở DM (Form 4 SEC) | **KHÔNG** — chỉ có proxy giá ("insider leak" pattern, `analyze_earnings_reaction.py`) và method `insider_deals()` chưa dùng của vnstock | **C** (nguồn mới: vnstock `insider_deals()`/`foreign_trade()`, hoặc công bố SSC/HOSE) | **⭐ Rất cao — và VN có lợi thế cấu trúc thật:** Thông tư 96/2020 buộc người nội bộ công bố **TRƯỚC** khi giao dịch (pre-trade intent), rồi mới xác nhận sau — khác với đa số nước chỉ công bố SAU. Ngưỡng: ≥50tr/ngày hoặc ≥200tr/tháng; cổ đông lớn biến động >1% báo trong 5 ngày làm việc. Nghĩa là ở VN tín hiệu tới **trước** giao dịch, không phải sau | **CAO — nhưng là dự án DỮ LIỆU, không phải dự án backtest** (xem §4) |
| 10 | **Room ngoại còn lại / dòng tiền khối ngoại** | Room cạn = khan hiếm cấu trúc; dòng mua/bán ròng NN | Không phải factor DM — **đặc thù EM/VN** | **KHÔNG** — chỉ có field mapping chưa dùng (`vci/const.py:154 foreign_total_room`, `kbs/const.py FB/FS/FO`) | **C** (vnstock `foreign_trade()`) | Cao — nhưng cẩn thận: giai đoạn 2024-25 khối ngoại bán ròng kéo dài khiến factor này dễ chỉ là **proxy của regime**, không phải cross-sectional alpha. Phải test trung tính theo thời gian | **TRUNG-CAO** |
| 11 | **Analyst estimate revision** | Điều chỉnh KỲ VỌNG tương lai (khác PEAD = bất ngờ đã xảy ra) | Rất cao ở DM (IBES/Factset — là factor momentum-earnings chuẩn) | **KHÔNG — và không có bất kỳ dữ liệu consensus nào trong repo** | **C, đắt** — FiinGroup/FiinPro có consensus nhưng **chủ yếu VN30**; Bloomberg đắt | Thấp — universe của ta là top-30 thanh khoản + BAL rộng hơn nhiều VN30; coverage mỏng ⇒ factor chỉ phủ một phần rổ, khó dùng nhất quán. Chi phí/độ phủ tệ nhất bảng | **THẤP** |
| 12 | **Quality-Minus-Junk (AQR QMJ)** | Composite profitability+growth+safety+payout | Rất cao | **Overlap RẤT lớn** — 8L đã là composite quality nhiều trụ (ROE/ROIC _Min floors + FSCORE + leverage + CFO). Điểm QMJ có mà 8L thiếu: (i) leg **growth** của chính các tỷ số quality (xu hướng 5Y của ROE/GP, không chỉ mức & sàn), (ii) leg **payout** | (i)=**A**, (ii)=**B/C** | Trung — 8L đã "through-the-cycle" theo đúng tinh thần QMJ safety. Đề xuất: **KHÔNG** dựng QMJ song song; chỉ cân nhắc bổ sung leg *growth-of-quality* vào 8L | **THẤP** như một factor mới / **TRUNG** như 1 leg bổ sung cho 8L |
| 13 | **Beneish M-score (bóp méo BCTC)** *(Taylor bổ sung)* | 8 biến BCTC dò khả năng xào nấu số liệu | Trung-cao (thiên về forensic/risk hơn alpha) | Một phần — `anomaly_scan.py` + `forensic_flags.csv` giải quyết cùng bài toán bằng đường khác (bất thường giá/cổ) | **B** (thiếu vài biến, dựng gần đúng được) | Cao về mặt lý thuyết ở EM, nhưng **overlap cao với accruals (#2)** — accruals là 1 trong 8 biến của M-score và là biến mạnh nhất | **THẤP** (làm #2 trước; nếu #2 ăn thì mới xét mở rộng) |
| 14 | **Cổ phiếu cầm cố / lãnh đạo thế chấp** *(Taylor bổ sung — đặc thù VN)* | Lãnh đạo cầm cố tỷ lệ lớn → rủi ro giải chấp dây chuyền, sập giá phi tuyến | Không có ở DM; **rủi ro đặc trưng VN** (nhiều case 2022) | **KHÔNG** | **C** (công bố rời rạc, không chuẩn hoá — khó) | Rất cao về mức độ liên quan, rất thấp về tính khả thi dữ liệu | **THẤP** (ghi nhận, không đề xuất theo đuổi) |
| 15 | **Idiosyncratic volatility** *(Taylor bổ sung)* | Vol phần dư sau khi bỏ beta thị trường → IVOL cao thường return kém | Cao | **KHÔNG** (Dev có cột nhưng là total dev, không phải idio) | **A/B** (tính từ chuỗi giá + VNINDEX đã có) | Trung — gần trùng #4 low-beta | **TRUNG-THẤP** (gộp vào cùng vòng nghiên cứu với #4) |

### Đã kiểm tra và LOẠI khỏi danh sách (nêu để không ai đề xuất lại)

- **Short interest / securities lending** — VN không có bán khống thật ở tầng cổ phiếu lẻ. N/A.
- **Momentum giá 12-1** — không phải "thiếu", mà là **đã đóng có chủ đích** 2026-07-12 sau chuỗi R&D
  đầy đủ (MOM_N/MOM_S). Mở lại cần lý do mới, không phải vì "quỹ DM ai cũng dùng".
- **52-week-high proximity** — đã có dưới dạng `Close/HI_3M_T1` + `ID_HI_3Y` trong SIGNAL_V11.
- **Piotroski F-score** — đã có (FSCORE + FSCORE_P1).
- **Size/market-cap factor** — đã ngầm định qua sàn thanh khoản + cap-weight 10% của custom30V.

---

## §4 — Khuyến nghị cho vòng tiếp theo

**Nhóm A — rẻ, 0 nguồn dữ liệu mới, có thể backtest ngay (đề xuất chọn 2-3 từ đây):**
`#1 Gross profitability` · `#2 Accruals` · `#4 Low-beta as factor` · `#3 Breadth sâu hơn`

Cả 4 dùng cột BQ đã có, không phụ thuộc ai, không cần mua gì. **Đề xuất mạnh nhất của tôi: #2
Accruals và #1 Gross profitability** — cùng họ "chất lượng lợi nhuận", cùng nguồn dữ liệu, cùng
khung IC-panel đã có sẵn (`ic_panel_ext_q3.py` đã prototype accruals), và cùng có luận điểm tiên
nghiệm rằng chúng **mạnh hơn ở VN so với DM** vì chất lượng công bố thông tin thấp hơn. #4 rẻ nhất
về công sức (Beta đã nằm sẵn trong bảng, chỉ chưa ai dùng nó làm factor) nên đáng chạy kèm.

**Nhóm B — cần dữ liệu mới, phải coi là DỰ ÁN DỮ LIỆU trước, không phải dự án backtest:**
`#9 Insider` · `#10 Room ngoại`. Đây là hai cái **thú vị nhất về mặt cấu trúc thị trường** (đặc
biệt #9: cơ chế công bố-trước của VN không tồn tại ở DM), nhưng bước 1 phải là Winston xác minh
nguồn thật + dựng lịch sử point-in-time đủ dài. **Không có lịch sử point-in-time thì không
backtest được** — đúng giới hạn đã ghi nhận với due-diligence gate CAPIT (n=1, không backtest được).

**Nhóm C — không đề xuất theo đuổi bây giờ:** `#8 Shareholder yield` (leg buyback rỗng ở VN),
`#11 Analyst revision` (đắt + chỉ phủ VN30), `#12 QMJ` (trùng 8L), `#13 M-score` (trùng #2),
`#14 Cầm cố` (dữ liệu không khả thi).

**Kỷ luật bắt buộc nếu chuyển sang backtest** (theo `kb/context_pack.md` §Quy chuẩn 5): khai báo
**N trials trước**, báo **DSR** (<0.95 = red flag), **PBO** nếu chọn từ họ ≥8 biến thể, walk-forward
IS 2014-19 / OOS 2020+, per-year LOO, rồi quant-skeptic. Với các factor họ quality/value ở đây,
rủi ro lớn nhất **không phải overfit tham số** mà là **trùng lặp với 1/PE** — 1/PE đang là factor
thống trị (IC +0.125, 94% hit); mọi candidate phải chứng minh **IC gia tăng SAU KHI trung tính hoá
theo 1/PE và theo 8L rating**, không phải IC thô.

---

## Nguồn tham khảo (§2 — phần cần xác minh thực tế, không suy đoán)

- [Circular 96/2020/TT-BTC — công bố thông tin TTCK VN (bản tiếng Anh)](https://thuvienphapluat.vn/van-ban/EN/Chung-khoan/Circular-96-2020-TT-BTC-providing-guidelines-on-disclosure-of-information-on-securities-market/460833/tieng-anh.aspx)
- [Vietnam Briefing — Circular 96 disclosure norms](https://www.vietnam-briefing.com/news/vietnam-issues-new-information-disclosure-norms-circular-96.html/)
- [Advance disclosure of insider transactions: Empirical evidence from the Vietnamese stock market (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0144818823000157) — nguồn cho đặc điểm công bố-TRƯỚC-giao-dịch của VN
- [Insider trading rules in Vietnam — Lexology](https://www.lexology.com/library/detail.aspx?g=c0c183e2-b9c5-4e7e-88da-9376c42c9e5d)
- [FiinGroup/FiinPro — consensus VN30](https://www.slideshare.net/slideshow/data-digest-8-vietnam-stock-market-in-the-new-normal-expensive-or-relatively-cheap/251534156)

Factor học thuật (kiến thức chuẩn ngành, không cần trích web): Sloan (1996) accruals ·
Novy-Marx (2013) gross profitability · Fama-French (2015) 5-factor CMA · Frazzini-Pedersen (2014)
BAB · Asness-Frazzini-Pedersen (2019) QMJ · Altman (1968) Z-score · Beneish (1999) M-score ·
George-Hwang (2004) 52-week high · Piotroski (2000) F-score.

---

## §5 — KẾT QUẢ candidate #3 (Breadth sâu hơn) — **NO-GO cả 3 metric**

**Job:** `Taylor_20260720_114042` · **Ngày:** 2026-07-20 · **N trials khai báo trước = 3**
(B1 A/D line · B2 new-high/new-low 3M · B3 %>MA20 + %>MA50). Không sweep tham số; cửa sổ
divergence cố định 60 phiên chọn trước. Artifact: `exp_breadth/{build_breadth_panel,analyze_breadth,
fairness_check}.py`, `exp_breadth/{breadth_panel,ic_divergence}.csv`.

**Điều chỉnh khung test so với §2 dòng #3** (đúng như dispatch yêu cầu): test ở tầng
**market-timing**, KHÔNG ép breadth thành factor xếp hạng từng mã (category error — breadth
không có giá trị per-ticker). Biến mục tiêu = forward VNINDEX return T+5/20/60.

**Sanity check nguồn:** `b_rsi_os` tính được ngày 07-17 = **0,2176**, khớp CHÍNH XÁC
`breadth_oversold` production đang theo dõi cho CAPIT → panel dựng đúng.

### Kết quả

| Bằng chứng | Kết luận |
|---|---|
| **Sign-stability IS→OOS** | **5/18** cặp (metric × horizon) giữ đúng dấu — **thấp hơn cả coin-flip 9/18** |
| IC divergence h=20 | B3_ma50: IS **+0,074** (p=0,005) → OOS **−0,050** (p=0,047) — lật dấu, cả 2 đều "có ý nghĩa" |
| | B1_ad_line h=60: IS **−0,138** → OOS **+0,121** — lật dấu mạnh nhất |
| | B2_nhnl: IS ≈ 0,00 (không tín hiệu) → OOS +0,065 — chỉ có ở OOS, không phải edge bền |
| Tercile H−L (h=20) | Lật dấu ở **6/6** metric giữa IS và OOS |
| Đuôi cực đoan (D1 vs D10) | Không metric nào giữ được thứ tự đơn điệu ở cả IS lẫn OOS |
| Per-year IC | Không metric nào giữ dấu ổn định; IC dương tập trung ở **2025-2026** ở CẢ 6 metric (kể cả 2 PROD) ⇒ artifact chế độ thị trường, không phải tín hiệu |
| Fairness check (dùng LEVEL thay divergence) | **Tệ hơn** — B1 level OOS −0,153/−0,246 (lật dấu từ IS ≈0) ⇒ kết luận không phải do spec divergence làm oan |

### Trùng lặp (mục 3 của dispatch)
Ở mức divergence, 3 metric mới **trùng nhau nặng** (B3_ma20↔B3_ma50 = **0,79**; B2↔B3_ma20 =
**0,75**) và trùng vừa phải với PROD %>MA200 (0,41–0,60; B1↔%>MA200 = **0,60**). Nghĩa là phần
"thông tin mới" vốn đã nhỏ — và phần nhỏ đó không dự báo được gì.

### ⚠️ Điều KHÔNG được suy ra từ kết quả này
2 breadth PROD hiện tại **cũng** trượt cùng bài test (P_ma200 1/3, P_rsi_os 2/3 sign-stable) —
nhưng điều đó **KHÔNG có nghĩa chúng hỏng**. Chúng chưa bao giờ được wire làm **bộ dự báo return**:
%>MA200 là **guard chặn cap fail-safe** (suppress cap US khi VN-US phân kỳ), %RSI<0,3 là
**trigger trạng thái** cho washout CAPIT. Đó là việc khác. Kết quả này thực ra **ủng hộ** quyết
định thiết kế cũ: breadth ở VN dùng làm *cổng điều kiện* thì được, làm *dự báo hướng* thì không.

### Kết luận
**NO-GO cả 3.** Không wire gì vào DT5G/production (đúng phạm vi thăm dò). Không đề xuất vòng
tiếp theo cho breadth — dư địa "mở rộng bộ breadth" đã được đo và rỗng. Nhóm A còn lại đáng làm:
**#4 low-beta as factor** (nhưng đọc trước finding `Taylor_20260720_111429`: `risk_rating.Beta`
là BIN 1–5, phải tự tính beta liên tục trước).

---

## §6 — KẾT QUẢ candidate #4 (Low-beta / BAB) + #15 (Idio-vol) — **NO-GO cả hai**

**Job** `Taylor_20260720_121019` · **N trials khai báo trước = 2** (#4 candidate chính; #15 rider
đã pre-register trong §2 dòng 109 "gộp cùng vòng nghiên cứu với #4"). Không sweep cửa sổ, không
sweep tham số Blume, không thử biến thể daily/monthly rồi chọn cái đẹp. Vòng thăm dò — **không
wire gì**.

### Cách tính (chốt trước, không phải lựa chọn post-hoc)
Beta **liên tục tự tính**: return **tuần**, rolling **260 tuần** vs VNINDEX, **Blume-adjust
0,67b+0,33**. Khung weekly-5Y đã được chốt bởi job `Taylor_20260720_111429` (thắng 8/8 quý khi
reverse-engineer `risk_rating.Beta`) — **không** dùng field bin 1–5 làm input. Idio-vol = độ lệch
chuẩn phần dư của **cùng** hồi quy đó (chi phí ~0, đúng lý do §2 xếp #15 chung vòng).
Script: `ic_panel_lowbeta_q3.py` + `ic_panel_lowbeta_diag.py`.

### Self-check bắt buộc (làm TRƯỚC khi kết luận)
| Kiểm tra | Kết quả |
|---|---|
| Beta tính lại bằng đường code khác hẳn (pandas thuần, từng ticker) @2025Q1 | Khớp: VNM 0,690/0,696 · HPG 1,212/1,241 · FPT 0,907/0,918 · MBB 1,181/1,186 · VIC 0,785/0,763 · SAB 0,807/0,786 |
| Beta vs field bin `risk_rating.Beta` | Spearman **+0,742** (n=12.680) — khớp kỳ vọng ~+0,8 |
| Mức beta hợp lý? | top-30 med **1,12** · top-60 **1,08** · 61-150 **0,90** · 151-400 **0,60** · 401+ **0,23** |

⚠️ **Giới hạn phạm vi phải nêu**: cache giá chỉ có từ 2013-01 ⇒ 8 quý đầu panel (2014Q1–2015Q4)
**không đủ 260 tuần và bị loại**. IS thực tế = **2016–2019** (16 quý), không phải 2014–2019.
OOS 2020+ (25 quý) không bị ảnh hưởng.

### Kết quả — #4 low-beta (`neg_beta`, kỳ vọng IC dương)
| Tầng | ALL | IS (2016-19) | OOS (2020+) |
|---|---|---|---|
| L0 raw | +0,0012 (t=0,04) | **+0,0330** | **−0,0192** (t=−0,41) |
| L1 vs value | +0,0072 | +0,0410 | −0,0144 |
| L2 vs value+rating | +0,0081 | **+0,0449** | **−0,0155** (t=−0,38) |

**Lật dấu IS→OOS ở cả 3 tầng.** Ngũ phân vị không đơn điệu (Q1 3,18 · Q3 2,84 · Q5 3,07). LOO:
không năm nào gánh edge — IC dương/âm đảo liên tục theo năm (2020 −0,213 vs 2022 +0,103).

**Trong pool thanh khoản thật — còn tệ hơn:** L2 OOS IC = **−0,082** (top-60) / **−0,037**
(top-100). Nghĩa là ở đúng universe ta giao dịch, low-beta **sai dấu**, không phải chỉ vô dụng.

### Chẩn đoán — TẠI SAO BAB không dịch được sang VN
Đây là phần có giá trị nhất của vòng này. Beta đo được **giảm đơn điệu theo độ thanh khoản**
(1,12 ở top-30 → 0,23 ở nhóm 401+). Đó là **thiên lệch non-synchronous trading**
(Scholes-Williams): cổ phiếu ít khớp lệnh + biên độ ±7% HOSE ⇒ giá phản ứng trễ với thị trường ⇒
beta đo thấp giả tạo. Hệ quả: **"low beta" trong universe đầy đủ chủ yếu là proxy của ILLIQUIDITY,
không phải tính phòng thủ thật.** Một rổ BAB long-low-beta ở VN sẽ tự động mua đuôi kém thanh
khoản — không giao dịch được ở quy mô của ta, và OOS âm ở top-60/100 xác nhận phần "beta thấp
thật" (không do illiquidity) không mang edge.

### Kết quả — #15 idio-vol (`neg_idiovol`) — sống sót L2 nhưng vẫn NO-GO
| Tầng | ALL | IS | OOS |
|---|---|---|---|
| L0 raw | +0,0481 (t=3,70) | +0,0408 | +0,0528 (t=3,23) |
| L2 vs value+rating | +0,0329 (t=2,04) | +0,0354 | +0,0314 (t=2,48) |

Thoạt nhìn đây là ứng viên duy nhất qua được gate L2 với OOS ổn định và LOO sạch (không năm nào
gánh edge). **Ba lý do vẫn NO-GO:**

1. **Trùng lặp gần như hoàn toàn với `risk_rating.Dev` — ta đã có nó rồi.**
   corr(idio-vol, Dev bin) = **+0,854**. Thêm `neg_dev` vào bộ control: OOS IC **0,0314 → 0,0182**,
   t **2,48 → 1,32** (mất ý nghĩa). Thêm hết dev+liq+beta: OOS t = 1,34. Đây đúng mẫu hình
   accruals-bị-1/PCF-nuốt của vòng trước, chỉ đổi thủ phạm: **Dev**.
2. **Không sống trong pool thanh khoản thật.** L2 OOS: top-60 t=+1,26 · top-100 t=+1,34 ·
   top-200 t=+1,41 — không mức nào có ý nghĩa. Edge L0 lớn (+0,14 top-60) tan khi trung hòa
   value+rating. corr(idio-vol, liq_rank)=+0,386 ⇒ một phần là size/thanh khoản đội lốt.
3. **Là lăng kính RỦI RO, không phải return-factor** (giống hệt gross profitability vòng trước).
   Ngũ phân vị trong-từng-quý (Q5 = idio-vol thấp nhất):

   | Q | idiovol med | fwd_mean | fwd_med | crash% | moon% (>30) |
   |---|---|---|---|---|---|
   | 1 | 0,0959 | 3,59 | 0,00 | **10,46** | 9,20 |
   | 3 | 0,0562 | 2,88 | 0,00 | 5,54 | 6,28 |
   | 5 | 0,0341 | 2,52 | 0,56 | **1,98** | 3,13 |

   crash% giảm đơn điệu 10,5→2,0 **và** moon% cũng giảm đơn điệu 9,2→3,1, trong khi `fwd_mean`
   **không** tăng (Q5 2,52 < Q1 3,59). Đây là **nén phương sai hai đuôi**, không phải alpha. IC
   rank dương chỉ phản ánh trung vị cao hơn (0,56 vs 0,00). Một tilt long-only equal-weight theo
   idio-vol thấp sẽ **KHÔNG** thu được IC này thành lợi nhuận.

### Kết luận §6
**NO-GO cả #4 và #15.** Không wire gì. Cụ thể cho vòng sau:
- **Dừng theo đuổi low-beta ở VN** — rào cản là cấu trúc vi mô thị trường (biên độ + thanh khoản
  mỏng làm hỏng phép đo beta), không phải chọn sai khung/tham số. Không có cách đặc tả lại nào
  cứu được; đừng đề xuất lại với cửa sổ khác.
- **Idio-vol: đã có sẵn dưới tên `risk_rating.Dev`.** Nếu vòng sau muốn dùng, phải dùng đúng vai
  trò **lăng kính rủi ro / gate giảm crash** (không phải return-tilt), test riêng với tiêu chí
  riêng, và **không** tái sử dụng IC ở đây làm bằng chứng.
- Mẫu hình lặp lại 3 vòng liên tiếp (accruals→1/PCF, gross-prof→lăng kính rủi ro + nhiễm nhóm tài
  chính, idio-vol→Dev): **khối quality/risk của ta đã bị 8L + value block phủ kín**. Dư địa factor
  mới không nằm ở đó nữa.

**Artifacts**: `ic_panel_lowbeta_q3.py` · `ic_panel_lowbeta_diag.py` ·
`data/ic_panel_lowbeta_q3.csv` · `data/beta_panel_continuous.csv` ·
`data/ic_panel_lowbeta_diag.csv` · `data/ic_panel_lowbeta_loo_F3_low_beta.csv` ·
`data/ic_panel_lowbeta_loo_F4_neg_idiovol.csv`

---

## §7 — Giải mã hệ thống LEGACY (buy-signal / sell-signal, tiền-V2.4) của user

**Job:** `Taylor_20260721_043256` · **Ngày:** 2026-07-21 · **Loại:** KHẢO SÁT/KIỂM KÊ, KHÔNG backtest.
**Nguồn:** `agents/Taylor/inbox/legacy_v1_filter_20260721.csv` — bộ filter.json của 1 hệ thống user
tự xây trước V2.4, kiến trúc **mua-khi-có-tín-hiệu-mua / bán-khi-có-tín-hiệu-bán** (14 pattern MUA
`_X`, 13 pattern BÁN `~X`, bảng map `$X` gán mỗi pattern mua với 4–9 pattern bán tương ứng). Khác
hẳn kiến trúc BAL/LAG hiện tại (2 book + allocator + time/stop exit).

> **Kết luận đầu tiên, quan trọng nhất:** trên phía MUA, hệ thống legacy **trùng lặp nặng** với cái
> ta đã có (value + quality-floor + growth QoQ/YoY + sàn thanh khoản + Risk_Rating gate). Novelty
> thật nằm gần như HOÀN TOÀN ở **tầng EXIT** — 13 tín hiệu bán kỹ thuật/cơ bản chi tiết. Đây đúng
> khoảng trống §1c đã xác nhận ("Exit kỹ thuật: KHÔNG CÓ — exit prod = thời gian + stop cố định").
> Vì vậy §7 dồn trọng tâm vào exit (Bước 3), không xới lại phần buy đã phủ.

### §7.0 — Ba phát hiện cấu trúc phải nêu trước (không phải suy đoán — đã verify bằng BQ)

1. **`Init` bị đóng băng `time ∈ [2014-01-01, 2025-01-01]`.** Đây là 1 snapshot NGHIÊN CỨU/backtest
   tĩnh, **không phải bộ filter live** (cửa sổ kết thúc 2025-01-01, không tự trượt). Coi như tài
   liệu thiết kế, không phải hệ đang chạy.
2. **`ICB_Code` THỰC TẾ là mã số ICB 4 chữ số** (2353.0, 8633.0…), **KHÔNG** phải chuỗi CT/NH/BH/CK
   như `bigquery_dictionary.json` mô tả — verify bằng `SELECT DISTINCT ICB_Code` trên `tav2_bq.ticker`.
   ⇒ điều kiện `ICB_Code != 2353` / `!= 8633` trong legacy **hợp lệ** với bảng hiện tại (không phải
   lỗi). *(Việc phụ cho Winston: sửa mô tả `ICB_Code` trong dictionary — đang sai/lỗi thời.)*
   - **ICB 2353 = Building Materials & Fixtures** (xi măng/gạch/nhựa: BCC, BTS, CLH, BMP, CVT, DHA…),
     n≈97 mã. `_BuySupport` loại ngành này.
   - **ICB 8633 = Real Estate Holding & Development** (BĐS: DIG, DXG, AGG, CEO, HDC, BCM…), n≈105 mã.
     `~SellBV` loại ngành này.
   - **Lý do loại trừ — user xác nhận 2026-07-21**: *"Tôi loại trừ nhóm tài chính và bất động sản
     khu công nghiệp để tránh nhìn sai PB"* — đúng khớp suy luận cơ học ban đầu cho `~SellBV`/8633
     (tài sản BĐS/tài chính hạch toán khác doanh nghiệp sản xuất thường ⇒ PB không so sánh trực
     tiếp được, cùng bài học "domain-correctness trước khi cross-sectional" đã rút ra ở case PCF-
     ngân hàng trong custom30V, xem [[feedback-finance-domain-grounding-not-pure-statistics]]).
     **`_BuySupport`/2353 (vật liệu xây dựng) — user xác nhận KHÔNG chủ ý loại trừ** (2026-07-21:
     "không chủ ý loại vật liệu xây dựng, không cần quan tâm") — có thể là artifact còn sót lại
     từ quá trình tinh chỉnh cũ, không mang ý nghĩa thiết kế. Không cần điều tra thêm.
3. **`_TradingValueMax` chứa điều kiện CHẾT `D_RSI < 83.0`.** Verify: `D_RSI ∈ [0,1]` (min 0, max 1,
   median 0.49) trên BQ ⇒ `D_RSI < 83.0` **luôn đúng** = no-op. Đây là **lỗi port thang đo** từ hệ
   cũ (RSI 0–100) sang cột `D_RSI` 0–1: trần chống-quá-mua dự kiến (~RSI<83) đã bị **vô hiệu âm thầm**
   ⇒ pattern này KHÔNG có trần RSI, có thể kích hoạt ở vùng quá mua cực đoan. Các pattern khác trong
   CÙNG file lại dùng đúng thang 0–1 (`D_RSI<0.27`, `<0.78`…) ⇒ đây là lỗi cục bộ 1 dòng, không phải
   file khác thang. **Nếu tái sử dụng pattern này phải sửa ngưỡng về 0–1 hoặc bỏ.**

### §7.1 — Giải mã 14 pattern MUA (Bước 1)

Khung chung MỌI pattern mua: `{Init}` + **sàn thanh khoản** `Volume_3M_P50·Price/Inflation_7 > X`
(X = trading-value 3M-median quy về VND thực; X ∈ [0.4B, 3.6B] tùy pattern — **cùng khái niệm** với
sàn `Volume_3M_P50·Price` PROD của SIGNAL_V11, chỉ khác mức) + **`Risk_Rating ≤ 4/5/6`** (bin
Beta+Dev làm cổng eligibility — hiện PROD **KHÔNG** dùng, xem §7.2/#24).

| Pattern | Logic kinh tế/kỹ thuật (1 dòng) | Ngưỡng cốt lõi (ngoài liq/risk) |
|---|---|---|
| `_BKMA200` | Phục hồi sau downtrend dài: đáy 3Y đến rất sau đỉnh 3Y + giá về gần MA200 từ dưới, MA50 cong lên + earnings turn | `(ID_LO_3Y−ID_HI_3Y)>265`; `MA50/MA200>0.92`; `MA10/MA200<1.24`; `NP_P0>1.28·NP_P1`; PE 4–20; ROE_Min3Y>0.02 |
| `_BullDvg` | **Phân kỳ RSI tăng tường minh** (giá đáy sau ≈ đáy trước nhưng RSI đáy sau CAO hơn) | `D_RSI 0.46–0.78`; `D_RSI_Min3M<0.34`; `D_RSI_Min1W/D_RSI_Min3M>1.26`; `D_RSI_Min1W_Close/D_RSI_Min3M_Close<1.85`; FSCORE>4; PE 5.6–13; NP_P0/NP_P4≥1.15 |
| `_BuySupport` | Bật từ hỗ trợ 1Y sau cú đâm thủng ngắn rồi thu hồi | `Close>1.08·Sup_1Y`; `LO_3M_T1<0.99·Sup_1Y`; `Close<1.49·LO_3M_T1`; PE 2–18.5; PB 0.34–1.35; **`ICB_Code≠2353`** |
| `_CashCowStock` | **FCF/EV yield** (CFO+CFI 4Q)/(mktcap+LtDebt) cao + đệm tài sản ròng + cú nổ volume | `(ΣCF_OA_P0..3+ΣCF_Invest_P0..3)/(OShares·Price+LtDebt_P0)>0.055`; `(Cash+LtInvest+AR+Inv−StLiab−LtDebt)/mktcap>0.13`; `Trading_Value/Trading_Value_1M_P50>1.85`; DY>0.022 |
| `_Conservative` | Cùng họ FCF/EV nhưng floor kép: 5Y-avg FCF/EV **và** 4Q FCF/EV; sàn liq thấp nhất (0.4B) | `((CF_OA_5Y+CF_Invest_5Y)/5)/(mktcap+LtDebt)>0.03`; `4Q FCF/EV>0.24`; NP_P0/NP_P1>1.12; PE 3.4–33 |
| `_DividendYield` | Cổ tức bền: **Dividend_Min3Y/Price** (cổ tức năm TỆ nhất 3Y) >2%, khác DY trailing | `abs(Dividend_Min3Y)/Price>0.02`; PCF 2–16; PE 0–14; NP_P0/NP_P1>1.14; Risk≤4 (chặt nhất) |
| `_RSILow30` | Quá bán sâu + rẻ tuyệt đối + **PB dưới dải lịch-sử-của-chính-nó** | `D_RSI<0.27`; PE 1.2–7.4; **`PB < 1.1·PB_MA5Y − 0.3·PB_SD5Y`**; ROE_Min3Y>0.04 |
| `_SuperGrowth` | GARP + **vào NGAY SAU báo cáo tốt** (event-timed entry) | `PE/(YoY%·100)<0.64` (PEG cực thấp); FSCORE≥4; **`ID_Current−ID_Release≤14`**; ROE_Min5Y>0.07 |
| `_SurpriseEarning` | Bất ngờ lợi nhuận YoY **và** QoQ (không neo ngày công bố) | `(NP_P0−NP_P4)/abs(NP_P4)>0.12`; `NP_P0/NP_P1>1.25`; PE 5–18.5; PB 0.47–1.8 |
| `_TL3M` | Nổ volume từ nền tích lũy chặt | `HI_3M_T1/LO_3M_T1<1.5` (nền chặt); `Volume>1.28·Volume_3M_P90`; NP_P0>1.28·NP_P1; PE 2.8–13 |
| `_TradingValueMax` | Đột biến **trading-value tuần chạm max 6M** + volume gần max 1Y (climax mua) | `Trading_Value_Total_1W≥0.93·..._Max6M`; `Volume≥0.96·Volume_Max1Y`; `Close<1.05·Close_2Y_P90`; ⚠️`D_RSI<83.0` CHẾT |
| `_TrendingGrowth` | **Breakout vượt vùng giá tại đỉnh-volume 5Y** (phá cung lịch sử lớn nhất) + earnings tăng tốc | `Close>1.13·Volume_Max5Y_High`; PE≤11.2; NP_P0>1.2·NP_P1; NP_P1>NP_P2 |
| `_UnderBV` | Dưới book (PB<1.14) + tăng trưởng YoY mạnh | PB 0.1–1.14; `NP_P0/NP_P4>1.40`; `(ΣNP 4Q)/OShares>1200`; PE 3.2–15 |
| `_VolMax1Y` | Breakout vượt vùng giá tại **đỉnh-volume 1Y** (mới, T-1W còn dưới) | `Close>1.12·Volume_Max1Y_High`; `Close_T1W<1.07·..High`; `ID_Current−Volume_Max1Y_ID≤205`; FSCORE>3 |

### §7.2 — Kiểm kê THẬT: khái niệm MỚI vs đã có (Bước 2, chỉ khái niệm mới/cách-dùng-mới)

Dùng 3 mức PROD/RESEARCH/COLUMN-ONLY như §1. **Bỏ qua** PE/PB/PCF/PS/ROE/ROIC/FSCORE/CF_OA/
Debt_Eq/RSI-thô/MACD/MA — §1 đã xác định trạng thái. Chỉ liệt kê điểm dispatch đánh dấu:

| Khái niệm legacy | Trạng thái hiện tại | Ghi chú khác biệt |
|---|---|---|
| **Sup_1Y / Res_1Y làm ngưỡng entry/exit** | **COLUMN-ONLY** (§1c liệt "Res_1Y-Sup_1Y" COLUMN-ONLY) | Legacy dùng làm tín hiệu tường minh ở ≥3 pattern (BuySupport bật từ Sup_1Y; SellResistance/1Y bị từ chối tại Res_1Y). Hiện KHÔNG ai đọc 2 cột này làm signal. **Cách dùng mới.** |
| **VAP1W/1M/3M (volume-at-price) làm ngưỡng exit** | **COLUMN-ONLY** | Legacy dùng VAP làm **tham chiếu exit cốt lõi** trong 7/13 pattern bán (giá phá xuống dưới VAP = mất vùng chi phí đám đông). **Ứng viên exit-signal CHÍNH.** |
| **Volume_Max1Y/5Y_High + ID (breakout vượt đỉnh-volume lịch sử)** | **COLUMN-ONLY, chưa ai dùng** | Hoàn toàn MỚI. Ý tưởng: vùng giá nơi volume đạt đỉnh 1Y/5Y = vùng cung/phân phối lớn nhất; phá lên = clear overhead supply. 3 pattern dùng (TrendingGrowth 5Y, VolMax1Y 1Y, SellVolMax top5-2Y). |
| **Phân kỳ RSI STOCK-level tường minh (BullDvg/BearDvg2)** | Cột `D_RSI_Max/Min_1W/3M(+_Close/_MACD)` **PROD-tồn-tại**; divergence-logic chỉ có ở **MARKET-level** (DT5G base v3.4b có BearDvg gate trên VNINDEX) — **CHƯA có ở stock-selection** | SIGNAL_V11 chỉ dùng RSI **thô 3 bậc**. Legacy so RSI hiện tại vs RSI-đỉnh/đáy 1W & 3M + so `_Close`/`_MACD` tại các đỉnh đó ⇒ phát hiện phân kỳ giá-momentum. **Tinh vi hơn hẳn cách dùng RSI hiện tại.** |
| **FCF/EV yield = (CFO+CFI)/(mktcap+LtDebt)** | **KHÔNG có** — 1/PCF chỉ là CFO/giá (bỏ capex + bỏ nợ) | **Công thức MỚI, khác 1/PCF VÀ khác shareholder-yield** (đã đánh THẤP §2#8 vì thiếu buyback). Đây là EV-cash-yield: trừ capex (gồm CF_Invest) + chuẩn hóa theo mktcap+LtDebt. Dữ liệu = **A** (đủ cột). Đáng xét độc lập. |
| **Dividend_Min3Y/Price làm sàn cứng** | DY PROD (đơn); Dividend_Min3Y **COLUMN-ONLY** | Khác DY: Min3Y = cổ tức năm TỆ NHẤT trong 3Y ⇒ lọc payer BỀN, miễn nhiễm cổ tức đặc biệt 1 lần thổi phồng DY. Cải tiến nhỏ nhưng hợp lý. |
| **Giao dịch quanh ngày công bố BCTC** (entry SuperGrowth ≤14d sau; exit SellLowGrowth ≤10d sau) | Entry event-timed **CÓ (PROD qua LAG:** vào release+5, giữ 25) ; **Exit-on-disappointment KHÔNG có** (LAG chỉ time-stop 25d, không exit theo BCTC xấu) | Entry side ≈ đã trùng LAG (SuperGrowth thêm lăng kính low-PEG khác selection nhưng cơ chế event-timed đã có). **Exit side MỚI** — xem #21. |
| **PB vs dải-lịch-sử-của-chính-nó có SD** (RSILow30/SellBV2/SellResistance1Y) | **PE-vs-own-history = PROD** (SIGNAL_V11); **PB-vs-own-history = KHÔNG PROD** (PB_MA5Y/SD5Y cột có). 8L `pb_z` là **cross-sectional sector-relative**, KHÁC time-series | Verify dispatch: PE có (PROD), **PB CHƯA** ở dạng time-series vs chính nó. Legacy dùng `PB < 1.1·PB_MA5Y−0.3·PB_SD5Y` (mua) và `PB>1.23·PB_MA5Y+0.84/0.93·PB_SD5Y` (bán). |
| **Loại trừ ngành theo ICB_Code** | 8L **sector-neutralize** (chuẩn hóa trong ngành); custom30V thuần thanh khoản (không lọc ngành) | Legacy **hard-exclude** ngành cụ thể/pattern (2353, 8633). Cơ chế khác (neutralize ≠ exclude). Lý do loại chưa rõ — §7.0#2. |
| **Risk_Rating ≤ N làm cổng eligibility** | **KHÔNG PROD** (Beta/Dev chưa từng là factor hay gate — §1b/#4; low-beta as *factor* đã NO-GO §6) | Legacy dùng Risk≤4/5/6 làm **gate cứng** mọi pattern. Câu hỏi "Risk-bin làm GATE" **khác** "low-beta làm FACTOR" (đã bác) — chưa test riêng. Xem #24. |

### §7.3 — Cơ hội EXIT-SIGNAL: phân loại 13 pattern BÁN + đề xuất vòng đầu (Bước 3, ưu tiên cao nhất)

Khoảng trống đã XÁC NHẬN (§1c) — không cần chứng minh tồn tại, chỉ đánh giá KHẢ THI. Phân loại theo
dữ liệu cần: **T** = thuần kỹ thuật (dùng ngay) · **T+F** = cần thêm cơ bản (PE/PB/NP — đã có sẵn PROD).

| Pattern bán | Loại | #ĐK | Logic exit (1 dòng) | Cột "lạ" cần validate |
|---|---|---|---|---|
| `~SellResistance` | **T** | **4** | Ngày phân phối: down-day volume cực lớn, bị từ chối dưới Res_1Y, sau cú chạy dài từ đáy 3M | Res_1Y (col-only, đơn giản) |
| `~SellLowGrowth` | **F** | **2** | Thoát NGAY sau BCTC yếu (YoY<20% & ≤10 phiên từ release) | — (NP + release, đều PROD) |
| `~MA41` | T+F | 5 | Quá căng trên MA200 (>1.55×) + earnings quay đầu + volume + phá VAP1M | VAP1M |
| `~S13` | T | 4 | Quá mua ngắn hạn (C_L1W≥1.15, >1.15·MA10) + đỉnh CMB tuần | CMB/D_CMB_XFast (col-only) |
| `~MA21` | T | 6 | Mất động lượng: MA20/MA50 gãy + RSI tuần giảm + dưới VAP1M + MACD<signal | VAP1M |
| `~SellResistance1M` | T | 4 | Phá xuống VAP1M + timing crossdown VAP | VAP1M, ID_XVAP (col-only) |
| `~SellVolMax` | T | 7 | Gãy khỏi vùng phân phối volume-đỉnh top5-2Y gần đây | Volume_MaxTop5_2Y, VAP1W (col-only) |
| `~MA31` | T+F | 8 | Trend gãy (MA10 về dưới MA200) + phá VAP3M + earnings chậm | VAP3M |
| `~BearDvg2` | **T** | **9** | **Phân kỳ RSI/MACD giảm** (giá đỉnh cao hơn, RSI+MACD đỉnh thấp hơn) | — (cột RSI-peak PROD) |
| `~SellPE` | T+F | 5 | PE vượt dải-lịch-sử-của-mình (+1.23SD) + earnings đứng + phá VAP3M | VAP3M, PE_MA5Y/SD5Y (PROD) |
| `~SellBV` | T+F | 6 | Giá>1.85·BVPS + earnings giảm + phá VAP1M; loại BĐS (8633) | VAP1M |
| `~SellBV2` | T+F | 6 | PB vượt dải-lịch-sử (+0.84SD) + earnings sập (QoQ<0.62) + phá VAP1M | VAP1M, PB_MA5Y/SD5Y (PROD) |
| `~SellResistance1Y` | T+F | 6 | PB căng lịch-sử + earnings giảm + bị từ chối dưới Res_1Y | VAP1M, Res_1Y, PB hist |

**Nhận xét chốt:** 10/13 pattern bán **phụ thuộc VAP** (COLUMN-ONLY) làm tham chiếu "giá phá xuống
vùng chi phí đám đông" — nên bước 0 của BẤT KỲ nghiên cứu exit nào là **validate VAP** (dựng lại
đúng định nghĩa "close in the largest trading area", kiểm point-in-time). VAP là trục exit-signal
trung tâm của cả hệ legacy.

**Đề xuất 3 ứng viên vòng đầu (đơn giản nhất, ít tham số nhất, dễ backtest nhất) — để 1 nghiên cứu
"exit theo chỉ báo" RIÊNG sau này (KHÔNG backtest trong job này):**

1. **`~SellResistance` (T, 4 ĐK)** — ứng viên #1. Thuần kỹ thuật, cột chuẩn (Open/Close/Res_1Y/
   LO_3M_T1/Volume_3M_P50), KHÔNG đụng VAP. Ngữ nghĩa sạch: "ngày phân phối volume-lớn từ chối tại
   kháng cự sau cú chạy dài" = exit chốt-lãi động lượng. Chỉ cần validate Res_1Y.
2. **`~SellLowGrowth` (F, 2 ĐK)** — ứng viên #2 (đơn giản TUYỆT ĐỐI). Thuần cơ bản, mọi cột PROD
   (NP_P0/NP_P4, ID_Current−ID_Release). Ngữ nghĩa: "thoát ngay khi BCTC làm thất vọng" — **bổ khuyết
   TRỰC TIẾP** cho LAG book (LAG hiện chỉ time-stop 25d, không có exit theo BCTC xấu). Đây là mảnh
   ghép thiếu tự nhiên nhất của khung PEAD đang chạy.
3. **`~BearDvg2` (T, 9 ĐK)** — ứng viên #3 cho exit ĐẢO-CHIỀU-động-lượng "tinh vi". Thuần kỹ thuật,
   dùng cột RSI-peak/MACD-peak đã PROD-tồn-tại, KHÔNG đụng VAP. Nhiều tham số hơn (9) nhưng là **gương
   đối xứng của BullDvg** và của BearDvg gate market-level đã hiểu rõ. *Nếu muốn ít tham số hơn cho
   vòng đầu, thay bằng `~MA41` (5 ĐK) — nhưng MA41 kéo theo VAP1M nên phải validate VAP trước.*

> Kỷ luật khi chuyển sang backtest exit (nhắc lại §Quy chuẩn 5): exit-signal khó đo hơn entry —
> phải so với **baseline exit hiện tại** (time-stop 45d/25d + hard-stop) trên **cùng tập entry**, đo
> Δ trên NAV path (không phải IC), khai N trials + DSR, và cực kỳ cẩn thận look-ahead ở VAP/Res_1Y
> (2 cột này phải là giá trị point-in-time T-1, không được nhìn tương lai).

### §7.4 — GHÉP vào bảng ưu tiên tổng hợp (candidate #16–#24, nối tiếp #1–#15)

Cùng quy ước dữ liệu **A/B/C** và caveat "Ưu tiên = tiền đề/khả thi, KHÔNG = edge" như §2/§3.

| # | Candidate (từ legacy) | Cơ chế (1 dòng) | Hệ thống đã có? | Dữ liệu VN | Phù hợp VN | **Ưu tiên** |
|---|---|---|---|---|---|---|
| 16 | **Exit theo VAP (volume-at-price)** | Thoát khi giá phá xuống dưới vùng chi phí đám đông (VAP1W/1M/3M) | **KHÔNG** (exit prod = time/stop); VAP COLUMN-ONLY | **A** (cột có) nhưng phải validate point-in-time | Cao — VAP nắm "giá vốn đám đông", hợp thị trường retail-nặng VN | **CAO** (đây là trục exit-signal trung tâm — lấp gap §1c) |
| 17 | **Support/Resistance làm signal (Sup_1Y/Res_1Y)** | Mua bật từ Sup_1Y / bán bị từ chối tại Res_1Y | **KHÔNG** (COLUMN-ONLY) | **A** | Trung-Cao | **CAO** cho exit (`~SellResistance` là ứng viên #1), TRUNG cho entry (trùng nhiều với breakout hiện có) |
| 18 | **Breakout vượt đỉnh-volume lịch sử (Volume_Max1Y/5Y_High + ID)** | Phá lên vùng giá nơi volume đạt đỉnh 1Y/5Y = clear overhead supply | **KHÔNG** (COLUMN-ONLY) | **A** | Trung — khái niệm hợp lý nhưng rủi ro trùng momentum (đã đóng MOM_N/S) | **TRUNG** |
| 19 | **Phân kỳ RSI/MACD stock-level (BullDvg entry / BearDvg2 exit)** | Giá đỉnh/đáy mới nhưng momentum đỉnh/đáy ngược chiều = báo đảo | Chỉ RSI thô (SIGNAL_V11); divergence có ở market-level, **chưa stock-level** | **A** (cột RSI-peak/MACD-peak PROD) | Cao — tinh vi hơn RSI thô, 0 nguồn mới | **CAO** cho exit (`~BearDvg2`), TRUNG cho entry (BullDvg trùng 1 phần đáy-RSI) |
| 20 | **FCF/EV cash yield = (CFO+CFI)/(mktcap+LtDebt)** | Hiệu suất tiền mặt tự do trên giá-trị-doanh-nghiệp; khác 1/PCF (bỏ capex+nợ) và khác shareholder-yield | **KHÔNG** (1/PCF chỉ CFO/giá) | **A** | Cao — trừ capex + tính nợ ⇒ khắt khe hơn 1/PCF, khó bị bóp méo | **TRUNG-CAO** (candidate value MỚI thật, không trùng #8/#12 đã loại) |
| 21 | **Exit-on-earnings-disappointment (SellLowGrowth)** | Thoát ≤10 phiên sau BCTC nếu YoY<20% | Entry event-timed có (LAG); **exit-on-BCTC-xấu KHÔNG** | **A** | Cao — bổ khuyết trực tiếp LAG (đang chỉ time-stop) | **CAO** (đơn giản nhất, gắn thẳng book PEAD đang chạy) |
| 22 | **PB vs dải-lịch-sử-của-chính-nó (time-series z)** | PB thấp/cao so với MA±SD 5Y của CHÍNH nó (khác pb_z cross-sectional của 8L) | PE-hist **PROD**; **PB-hist KHÔNG** (cột có) | **A** | Trung — bổ sung PE-hist đã có; giá trị gia tăng cần đo | **TRUNG** |
| 23 | **Dividend_Min3Y/Price (sàn cổ tức bền)** | Cổ tức năm TỆ nhất 3Y/giá > ngưỡng ⇒ payer bền, miễn nhiễm special-div | DY đơn PROD; Min3Y COLUMN-ONLY | **A** | Trung — cải tiến nhỏ trên DY | **THẤP-TRUNG** |
| 24 | **Risk_Rating (Beta+Dev bin) làm GATE eligibility** | Loại mã Beta/Dev cao trước khi chọn (khác dùng làm return-factor) | **KHÔNG PROD**; low-beta as *factor* đã **NO-GO §6** | **A** (nhớ DISTINCT bảng risk_rating) | Trung — như GATE (không phải factor) chưa test; nhưng §6 cho thấy beta VN nhiễu bởi thanh khoản | **THẤP-TRUNG** (câu hỏi khác §6 nhưng cùng rào cản đo-beta) |

**Tóm tắt ưu tiên §7:** cụm **exit-signal (#16 VAP, #17 Res/Sup, #19 BearDvg2, #21 SellLowGrowth)**
là phần đáng giá nhất — lấp đúng gap §1c đã xác nhận, và 3 ứng viên vòng đầu (`~SellResistance`,
`~SellLowGrowth`, `~BearDvg2`) đều A-data, 0 nguồn mới. **#20 FCF/EV** là candidate ENTRY/value MỚI
thật duy nhất từ hệ legacy không trùng cái đã loại. Phần buy còn lại trùng nặng cái đã có ⇒ không đề
xuất theo đuổi riêng. **Không backtest gì trong job này** (đúng phạm vi khảo sát).

### §7.5 — KẾT QUẢ backtest 3 ứng viên exit (job `Taylor_20260721_045810`, user duyệt) — **cả 3 NO-GO / underpowered**

**Phương pháp (deal-level isolation, auditable).** Lấy CHÍNH tập entry production từ R3 audit CSV
(`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv`): **423 deal
BAL** (SIGNAL_V11, 2015-2026) + **1629 deal LAG** (PEAD, 2014-2026), loại CAPIT. Chạy simulator deal-level
riêng (tự kiểm soát mọi bước, không nhiễu ramp/partial-fill/allocator): mỗi deal vào tại Close ngày fill,
thoát theo baseline **verify trong code** (`pt_v23_audit_2014.py:1704` BAL hold=45d stop=−20% min_hold=2;
`:1756` LAG hold=25d no-stop). Biến thể candidate = baseline HOẶC thoát SỚM hơn nếu exit-signal fire (exec
**T+1 Open**, chống look-ahead). Đo Δ trên **CÙNG entry set**. NAV = **fixed-slot honest** (sau early exit,
slot giữ **cash 0** tới đúng ngày baseline-exit — KHÔNG redeploy) để tránh artifact tái-đầu-tư-ngầm. **N=3
trials khai báo trước, KHÔNG sweep tham số.**

**Look-ahead audit (bắt buộc, §Quy chuẩn 5):** `Res_1Y` **98.5% backward-only** (corr 0.82–0.99 với trailing-
incl 252d-High-max; residual 1.5% = artifact adj/raw price trên mã nhiều corp-action, KHÔNG phải future-leak);
`D_RSI_Max1W/3M` **100% ≥ D_RSI hiện tại** (trailing max thật); `sess_since_rel` tự tính causal (đếm phiên kể
từ khi `ID_Release` đổi bậc — vì `ID_Current/ID_Release` là **counter per-ticker, ID_Current RESET cho ~412/603
mã** ⇒ hiệu số thô KHÔNG dùng được, đây là 1 bug cột nữa cùng họ §7.0; median khoảng-cách release 91 ngày ✓).

| Ứng viên | Entry set | Fire | Δ per-deal | NAV honest (Δ CAGR / Sharpe / MaxDD) | fwd-after-exit | Verdict |
|---|---|---|---|---|---|---|
| `~SellResistance` | BAL 423 | **2 (0.5%)** | +0.10pp | **+0.82pp** / +0.030 / 0 | **2/2 dodged DD** (−13.7%) | **UNDERPOWERED** — đúng hướng nhưng N=2 |
| `~BearDvg2` | BAL 423 | 9 (2.1%) | −0.03pp | −0.03pp / +0.003 / 0 | +1.41% (cắt winner ≈ dodge) | **NO-GO** (flat/âm) |
| `~SellLowGrowth` | LAG 1629 | 97 (6.0%) | −0.12pp | **−0.42pp** / +0.003 / **+2.31pp** | +1.19% med (cắt winner), 42% dodge | **NO-GO** như return play |

**Diễn giải:**
1. **`~SellResistance`** — signal chính xác & bảo vệ THẬT (HPX 2023-08-03 né −23% pump-crash; IDI 2021-10-27
   né −4.2%), honest NAV +0.82pp, MaxDD giữ nguyên. NHƯNG **gần như không bao giờ fire trên BAL** (cần down-day
   >5% + volume >2.47× median + dưới kháng cự sau cú chạy dài — BAL hold ngắn hiếm khi tới trạng thái đó). N=2
   ⇒ **không kết luận edge**. Để dành: test entry set rộng hơn (all-buys / custom30V / market-wide distribution-day)
   để tích N. **KHÔNG WIRE.**
2. **`~BearDvg2`** — phân kỳ 9-ĐK không thêm giá trị làm exit trên momentum entries: thoát winner ≈ ngang dodge
   loss (BMI 2021 cắt winner +29.6→+3.5%, fwd +25%!), net ~0/hơi âm, Sharpe phẳng. **KHÔNG WIRE.**
3. **`~SellLowGrowth`** — **đánh đổi return lấy DD** (−0.42pp CAGR đổi −2.31pp MaxDD), Sharpe phẳng. Cốt lõi:
   LAG = book **DRIFT sau BCTC**; thoát khi YoY<20% (vẫn dương) là **QUÁ SỚM**, đánh vào chính edge của book — đặc
   biệt OOS 2020+ (fwd +4.32%, n=45, cắt winner mạnh). ⚠️ Bẫy đo: NAV renormalized-active ban đầu báo **+0.83pp**
   nhưng đó là **redeploy artifact**; honest fixed-slot = **−0.42pp**. DD-benefit nhỏ, có thể có rẻ hơn qua hard-stop.
   **KHÔNG WIRE.**

**Kết luận §7.5:** 3/3 candidate exit vòng đầu **không đủ tư cách wire**. `~SellResistance` là mảnh duy nhất
đáng theo tiếp (đúng hướng, cần larger-N entry set). Không có candidate nào cần quant-skeptic ở vòng này (chưa
có gì để wire). Scripts: `mike/agents/Taylor/research/exit_signal_backtest_20260721/` (deal-level harness,
đọc R3 audit CSV + BQ-cache panel). **KHÔNG chạm production V2.4.**

### §7.6 — `~SellResistance` mở rộng sang custom30V (job `Taylor_20260721_053305`, user duyệt) — **VẪN UNDERPOWERED / NO-GO**

**Bối cảnh phải nêu rõ (theo yêu cầu dispatch):** custom30V hiện theo đúng thiết kế **KHÔNG stop-loss** —
sizing (cap 0.10/tên) + tái cân bằng quý LÀ cơ chế rủi ro duy nhất (quyết định user chốt gần đây, case
VIX −24%, từ chối thêm cảnh báo/stop-loss). `~SellResistance` KHÔNG phải stop-loss giá đơn thuần (nó là
tín hiệu kỹ thuật cụ thể: phiên phân phối volume-lớn `>2.47×` bị từ chối dưới `0.8×Res_1Y` sau chuỗi
tăng dài từ đáy 3M — `Close/LO_3M_T1>1.58`), nhưng **về bản chất vẫn là "thoát sớm hơn lịch tái cân bằng
dựa trên tín hiệu giá"** — nên kết quả này neo trực tiếp vào quyết định no-stop-loss đó, không tách rời.

**Cấu trúc deal (point-in-time, KHÔNG dùng snapshot hiện tại).** Đọc lịch sử thành phần rổ thật từ BQ-cache
`data/bq_cache/custom30v_8l.parquet` (= published `tav2_bq.custom30v_8l`, 48 rebal q2m5 2014-08→2026-05,
30 tên/rebal, có `effective_from/effective_to`). Mỗi (rebal_date × ticker) giữa 2 lần tái cân bằng liên
tiếp = 1 "deal": entry = Close ngày vào rổ, baseline exit = Close ngày tái cân bằng kế tiếp (**không
stop-loss**, đúng thiết kế). Rebal cuối (window đang mở) bị loại → **1410 deal / 209 tên**, phân bố đều
120 deal/năm 2015-2025 (không dồn regime). Candidate = baseline HOẶC thoát sớm nếu `~SellResistance` fire
trong window (exec **T+1 Open**, chống look-ahead). NAV = **honest fixed-slot** (cash 0 sau early exit tới
đúng baseline-exit, KHÔNG redeploy — cùng bài học "bẫy NAV renormalized" §7.5). **N=1 trial**, không sweep.

**Look-ahead audit (universe khác BAL nên verify lại).** `Res_1Y` vs trailing-252d-max Close: **corr 0.993**,
backward-consistent (PASS — khớp 98.5% audit §7.5). Fire-rate toàn panel **0.047%** (284/603.320 phiên).

| Metric | Baseline (no-stop) | Candidate (SellResistance overlay) | Δ |
|---|---|---|---|
| Deal fire early | — | **15 / 1410 (1.06%)** | — |
| Per-deal return (mean) | +4.65% | +4.68% | **+0.029pp** (t=0.26, 95%CI [−0.23,+0.21] **spans 0**) |
| Honest NAV CAGR | +15.74% | +15.98% | +0.238pp |
| Honest NAV MaxDD | −56.9% | −56.1% | +0.84pp |
| Honest NAV Sharpe | 0.74 | 0.75 | +0.016 |
| IS 2014-19 per-deal Δ | — | — | **−0.174pp** (fire=2) |
| OOS 2020+ per-deal Δ | — | — | +0.207pp (fire=13) |

**Diễn giải:**
1. **Vẫn UNDERPOWERED — 15 fire trên tập RỘNG NHẤT hợp lý.** Dù custom30V hold ~62 ngày (dài gấp ~1.4×
   BAL 45d) và tập entry lớn gấp ~3× (1410 vs 423), signal chỉ fire 15 lần (so N=2 ở BAL §7.5). Signal
   cực hiếm **do cấu trúc** (cần 4 điều kiện đồng thời rất chặt) — mở rộng entry set không cứu được.
2. **Đúng hướng bảo vệ nhưng KHÔNG có ý nghĩa thống kê.** 10/15 fire né được sụt giảm (fwd<0, median
   −6.18%): HSG 2022-08 né −44.8%, HPX 2023-08 né −23.1%, MBG né −20%. NHƯNG per-deal Δ t=0.26, CI qua 0.
3. **Rủi ro bất đối xứng winner-cut là lý do thật.** 10 dodge cộng −160.6pp / 5 winner-cut cộng +136.1pp
   → **gần như triệt tiêu nhau**. Riêng **LDG 2017 cắt mất +110pp** (thoát ở +23% trong khi deal chạy tiếp
   lên +158%) ~ một mình xoá sạch mọi dodge. Trên sleeve KHÔNG tái vào lệnh, một winner-cut nuốt trọn
   nhiều dodge nhỏ — đúng cơ chế vì sao exit kỹ thuật nguy hiểm trên parking basket.
4. **IS âm / OOS dương = split-luck**, không phải edge bền (IS Δ −0.174pp fire=2; toàn bộ Δ dương đến từ
   OOS 13 fire — cùng dấu hiệu underpowered §Quy chuẩn 5 per-year LOO).

⚠️ **Caveat harness:** NAV MaxDD −56.9% là sleeve equal-weight LUÔN đầu tư (mọi tên, không cap, không
cash-park, gồm bear 2018/2022) — **KHÔNG phải DD production custom30V** (cap-weight 0.10, nằm trong book
lớn có allocator + NEUTRAL-only). Đây chỉ là harness cô lập Δ-signal, không đại diện rủi ro thật của sleeve.

**Kết luận §7.6 (neo vào quyết định no-stop-loss):** kết quả **NO-GO/underpowered** → đây là **bằng chứng
CỦNG CỐ quyết định no-stop-loss** của custom30V, không đảo ngược. Thêm 1 điểm dữ liệu (sau BAL §7.5) cho
thấy exit sớm theo tín hiệu kỹ thuật **không tạo giá trị ròng có ý nghĩa** ở đây (Δ CAGR +0.24pp nằm trong
nhiễu, per-deal Δ CI qua 0), và mang rủi ro winner-cut bất đối xứng thật (LDG). **KHÔNG cần quant-skeptic**
(dispatch chỉ route skeptic nếu N đủ lớn ∧ dương có ý nghĩa — cả hai đều KHÔNG đạt). **KHÔNG wire, KHÔNG
chạm production V2.4/custom30V.** Scripts: `exit_c30v.py`, `dealset_c30v.csv`, `result_c30v.csv` cùng thư mục.

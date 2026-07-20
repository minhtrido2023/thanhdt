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

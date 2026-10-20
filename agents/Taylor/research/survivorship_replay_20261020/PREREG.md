# PREREG — Survivorship replay BAL/LAG trên mã lớn đã biến mất (job Taylor_20261020_094204, EXPLORATORY)

Viết TRƯỚC khi tính bất kỳ kết quả phantom nào. md5 + commit trước khi chạy `svr_replay.py`. Không sửa pin/registry/
pin_ledger, không kết luận lại số R3/V2.4, không đề xuất đổi luật.

## 0. Dữ kiện đã kiểm trước khi viết (không phải kết quả)
- 15 mã của Winston KHÔNG có dòng nào trong `tav2_bq.ticker`, `ticker_financial`, `fa_ratings`, `fa_ratings_8l`,
  `tav2_mike.universe_pit_q` (truy vấn 2026-10-20) ⇒ mọi đầu vào phải dựng lại từ VNDirect finfo (Winston).
- Engine R3 (`pt_v23_audit_2014.py`): BAL = SIGNAL_V11, `TIER_BAL = MEGA, MOMENTUM, DEEP_VALUE_RECOVERY, RE_BACKLOG_BUY`,
  hold 45 phiên, stop −20% theo giá đóng cửa, thoát ở Open phiên sau; EX-BULL chặn MEGA/MOMENTUM; overheat chặn mọi
  tier mua. LAG = sự kiện công bố quý: `NP_R=NP_P0/NP_P4−1 ≥ 0,15` ∧ `prior_n_good ≥ 4` ∧ `pa_HL3 ≥ 5` (post_ret
  = Close[+30]/Close[+5]−1, %, half-life 3 năm) ∧ forensic gate; vào Open phiên Release+5, giữ 25 phiên, không stop.
  Khớp lệnh: ≤20% ADV (`Volume_3M_P50 × Price`) mỗi phiên, tối đa 5 phiên, bỏ nếu <30%.
- **R3 backtest KHÔNG có cổng 8L rating ≤3 cho BAL/LAG** (cổng LAG 8L là luật LIVE từ 2026-07-27; cổng 8L trong
  engine chỉ ở rổ custom30). ⇒ "cận dưới có rating" ở dưới được tách làm 2 lớp: LB-R3 (cổng thật của engine) và
  LIVE (thêm golden floor xấp xỉ).

## 1. Phạm vi mã
- **M (chính)** = 15 mã Winston trừ HVG (hạng C) = 14 mã: ROS, FLC, GAB, KLF, ART, HAI, AMD, SJF, PSH, TTB, KSA, TGG,
  DAG, NHP. Hạng: A = ROS HAI AMD TGG TTB KLF SJF PSH NHP; B = FLC ART DAG (+GAB: không dùng GTGD — GAB dùng ADV của
  VNDirect nhưng báo riêng dòng "GAB ADV chưa kiểm"); KSA chưa đối chiếu (độ nhạy: bỏ KSA).
  Kiểm điều chỉnh hạng B: liệt kê ngày `adClose/close` đổi bước (>2%) trong cửa sổ có vị thế phantom, báo trong REPORT.
- **HVG**: chạy cùng cách, báo riêng, KHÔNG vào kết luận chính.
- **E (mở rộng)** = 21 mã còn lại trong 36 mã có đỉnh GTGD trung vị 60 phiên ≥5 tỷ (`stats_all.csv` Winston):
  KSH TNA KHB VIS CAV DPS VMI AVF KSS RDP SIC IBC CEE PPI SPI GTT NDF KSK KPF ASA BGM. Giá `prices_all` chưa đối chiếu
  nguồn thứ hai ⇒ báo riêng. BCTC: tải VNDirect `financial_statements` cùng cách `fin.py` của Winston; mã nào không tải
  được chỉ có UB.

## 2. Đầu vào dựng lại (từ CSV giá VNDirect)
Lịch = các ngày DAILY của ledger pin (2014-01-02 → 2026-06-19); chỉ báo tính trên lịch VNINDEX BQ từ 2013-01-02.
Close (adj, VND) = adClose×1000; Price (thô) = close×1000; Volume = nmVolume; Open adj = open×adClose/close.
- `tv_real = Price×Volume / Inflation_7(d)` (Inflation_7 lấy từ dòng VNINDEX của BQ theo ngày; thiếu ⇒ 1,07^(năm−2026)).
- `liq = Volume_3M_P50 × Price`, Volume_3M_P50 = median Volume 60 phiên.
- Chỉ báo SIGNAL_V11 phần giá: D_RSI, D_MACDdiff, MA20/50/200, MA50_T1, Close_T1, HI_3M_T1, ID_HI_3Y, D_RSI_Max1W —
  công thức chọn theo khớp BQ trên 5 mã còn sống (§4), KHÔNG theo kết quả phantom.
- Ngày khớp cuối `LT` = ngày cuối có nmVolume>0 trên sàn gốc; ngày hủy `DL` = ngày cuối có dòng trên sàn gốc;
  sau DL: dòng UPCOM (nếu có).

## 3. Universe replica (ruleset v1, `build_universe_pit.py`)
B1 coi có ICB · B2 tuổi ≥60 phiên từ dòng đầu VNDirect · B3 vào: median 60 phiên tv_real ≥1e9 · B4 ra: max 20 phiên
tv_real <0,5e9 · B5 Close ≥1.000 · B6 vắng ≥10 phiên liên tiếp trên lịch ⇒ ra · B7 hysteresis bằng LAST_VALUE.
Dòng UPCOM sau DL: coi là dòng của mã (BQ `ticker` có UPCOM), tv thật — thường ⇒ B4 ra.
**Kiểm định (cổng)**: chạy replica trên 5 mã còn sống (HPG, VNM, HQC, ITA, DLG) với giá VNDirect, so `universe_pit_q`
từng ngày 2014-01-02→2026-06-19. Cổng đạt: khớp ≥95% số ngày ở MỖI mã. Không đạt ⇒ nhãn kết luận "không đủ căn cứ"
cho phần BAL (LAG không dùng universe).

## 4. Kiểm định chỉ báo
Cùng 5 mã: so replica với BQ `ticker` cho D_RSI, D_MACDdiff, MA20/50/200, Volume_3M_P50, HI_3M_T1, ID_HI_3Y,
D_RSI_Max1W. Báo tỉ lệ ngày khớp các ĐIỀU KIỆN nhị phân dùng trong ta (vd D_RSI>0,5) và tương quan ta_px replica vs
ta_px tính từ cột BQ. Cổng: ta_px khớp tuyệt đối ≥90% số ngày (gộp 5 mã). Không đạt ⇒ ghi sai số, vẫn chạy.
Cùng 5 mã (ít nhất VNM, HPG): so NPAT quý và CFO quý VNDirect với BQ `ticker_financial` (NP_P0, CF_OA_P0) để xác định
(a) item npat hay npat_parent khớp NP_P0, (b) CFO là đơn quý hay luỹ kế. Dùng kết quả này cho §6.

## 5. BAL phantom
Ngày tín hiệu d: U(d) ∧ liq(d) ≥1e9 ∧ state(d)∈{4,5} (cột `state` ledger) ∧ ¬overheat(d) [VNINDEX Close/MA200>1,30 ∧
(state=5 ∨ VNI D_RSI>0,75)] ∧ điều kiện tier:
- **UB**: ta_px(d) + 56 ≥ 100 (giả định mọi cấu phần BCTC/ngành ở mức tốt nhất: PE+15, FSCORE+10, NP+8, NP_P1+8,
  ngành +5, ngành-8&tier D +10; fa_tier = C, tăng trưởng đạt ⇒ DEEP_VALUE_RECOVERY; ở state 4 mọi ca ta≥155 cũng
  ⊂ điều kiện này).
- **MID (xấp xỉ BCTC)**: ta = ta_px + cấu phần NP tính được (NP_P0/NP_P4, NP_P0/NP_P1 từ NPAT quý VNDirect, as-of
  Release ước lượng §6); PE/FSCORE/fa_tier/ngành = 0 (sai số ±40 điểm ta). Tier: state 4 ∧ ta≥155 (MEGA/MOMENTUM,
  giả định fa C/D) ∨ state∈{4,5} ∧ ta≥100 ∧ (np_yoy>0,2 ∨ rev_yoy>0,2) (DVR).
- **LIVE**: MID ∧ golden floor xấp xỉ (§6).
Vào Open phiên d+1; mỗi mã tối đa 1 vị thế BAL mở; tái vào được ở tín hiệu kế sau khi đã thoát hết.
Thoát: Close/entry−1 ≤ −20% hoặc đủ 45 phiên giữ ⇒ bán từ Open phiên sau. Không tính min_hold/T+3 (≤2 phiên).

## 6. LAG phantom
Sự kiện = mỗi quý có NPAT VNDirect. Release ước lượng = cuối quý + trung vị trễ công bố đo trên
`earnings_surprise_data.pkl` từ 2014 (Q1 27, Q2 32, Q3 26, Q4 27 ngày). Vào = Release+5 phiên (offset_date engine),
sd = vào−1; bỏ nếu `w_lag_tgt(sd)=0` (allocator BEAR).
- **UB**: mọi sự kiện có giá tại sd (không dùng BCTC).
- **LB-R3**: cổng engine: NP_R≥0,15 ∧ prior_n_good≥4 ∧ pa_HL3≥5, dựng từ NPAT VNDirect + giá VNDirect (post_ret cần
  giá từ 2013 ⇒ hist trước 2013 thiếu ⇒ prior_n_good bị đếm THIẾU ⇒ LB-R3 nghiêng về ít vị thế; ghi rõ).
  Forensic gate: không có mã nào trong `data/forensic_flags.csv` ⇒ không loại (kiểm bằng grep).
- **LIVE**: LB-R3 ∧ golden floor xấp xỉ: ROE_Min3Y≥0 ≈ NPAT 4 quý (TTM) tại 3 cuối năm tài chính gần nhất (as-of
  Release) đều ≥0; CF_OA_3Y>0 ≈ tổng CFO 12 quý gần nhất >0. Golden floor là điều kiện CẦN của rating ≤3 ⇒ LIVE vẫn
  là cận TRÊN của tập qua cổng 8L thật (các trục 8L khác không dựng được: PE/PB/PS/PCF cần số CP, percentile toàn
  thị trường cần universe đầy đủ — không dựng).
Thoát: bán từ Open phiên thứ 25 sau vào.

## 7. Kích thước, khớp lệnh, halt
- Trọng số mục tiêu: w_b = median theo book từ v2 `out_summary.json` từng chân (BAL 2,04–2,56%, LAG 2,92–4,07%);
  VND mục tiêu = w_b × combined_nav(ngày vào).
- Khớp vào (engine): mỗi phiên ≤ 0,2×liq, tối đa 5 phiên, bỏ nếu <30%; giá = Open adj phiên đầu (xấp xỉ 1 giá).
- Khớp ra (**chính, X-liq**): từ phiên thoát, mỗi phiên bán ≤ 0,2 × GTGD thực phiên đó (nmValue+ptValue), phiên đầu
  ở Open, phiên sau ở Close; GTGD=0 ⇒ không bán được. Độ nhạy **X-eng**: bán hết ở Open phiên thoát (như engine).
- Halt: vị thế còn tồn ở LT bị kẹt, định giá ở giá khớp cuối đến DL. Tại DL: **Z** = về 0; **U** = bán hết ở Close
  phiên UPCOM đầu tiên có KL>0 sau DL (nếu không có ⇒ như Z). Vị thế còn mở ở 2026-06-19: định giá theo giá cuối.
- Phí 0,1% mỗi chiều trên phần đã khớp.

## 8. Overlay (cùng cách v2) và chỉ số
Mỗi lô phantom k (book b, w_k = VND đã khớp / combined_nav(ngày vào)): hệ số NAV
f_k(t) = 1 − w_k·(1 − V_k(t)/G_k(t)) với V_k = giá trị lô (gồm tiền đã bán ra, sau phí)/vốn bỏ, G_k = NAV(t)/NAV(vào);
sau khi đóng lô f_k cố định. NAV' = NAV × Π f_k. Tức là: vốn của phantom lấy từ danh mục R3 (lẽ ra hưởng lợi suất R3).
Chỉ số `calc_metrics` (bản sao từ engine): ΔCAGR, ΔSharpe_252, ΔMaxDD; 4 chân × {UB, MID/LB-R3, LIVE} × {Z, U} ×
{X-liq, X-eng}; book BAL, LAG, MIX(=cả hai). Tập M (chính), M−KSA, HVG, E.

## 9. Kết quả cần và nhãn
(a) số mã/mã-năm R3 nắm xuyên suốt đến sụp: cửa sổ sụp C_i = [LT_i − 365 ngày, DL_i]. mã-năm = Σ ngày lịch có lô mở
   trong C_i / 365. Theo năm lịch. "Kẹt" = lô còn mở ở LT_i.
(b) ΔCAGR/ΔSharpe/ΔDD như §8.
(c) Nhãn dùng chân X-liq, kịch bản Z (bảo thủ), MIX, tập M, **so |ΔCAGR| với sàn nhiễu 0,46pp ở cả 4 chân**:
   mọi chân <0,46 ở cả UB ⇒ "nhỏ hơn sàn nhiễu"; ≥0,46 ở UB nhưng <0,46 ở LB-R3 ⇒ "vượt sàn nhiễu ở cận trên, dưới
   sàn ở cận dưới"; ≥0,46 ở LB-R3 ⇒ "vượt sàn nhiễu ở cận dưới". Cổng §3 trượt ⇒ phần BAL gắn "không đủ căn cứ".
(d) λ_replay = mã-năm(C) / số năm backtest (12,46) cho UB và LB-R3; so λ* v2 (MIX L−100% 0,11–0,15; L−50%
   0,19–0,25). Đây là so sánh mô tả, không phải kiểm định.

## 10. Control
Chạy lại 4 chân R3 (`run_leg.sh` = bản sao v2, chỉ đổi OUT), md5 phải = 4707bcbe / bcd0469f / 537e349b / a6ba34d8 và
self-check 0 VND BAL+LAG ở cả 4, TRƯỚC khi đọc kết quả phantom. Overlay dùng ledger trích từ kho pin
(`pin_ledger.py extract`), kiểm tái tạo METRIC ≤1e−9.

## 11. Giới hạn đã biết trước
Không mô hình hoá: cạnh tranh slot (max 12 vị thế/book — UB bỏ qua, nên còn bảo thủ hơn), rổ custom30 và nhánh
CAPIT (vanished names có thể vào các nhánh này — ngoài phạm vi), D1 RE_BACKLOG_BUY (cần AdvCust), SV_TIGHT (không áp
cho state 4/5). Release date ước lượng (p10–p90 trễ 18–34 ngày). CFO/NPAT VNDirect chưa đối chiếu BCTC gốc.

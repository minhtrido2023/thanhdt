# PVX 2011 — verify FEARBUY v1 false-positive + rule-fix backtest
> Job `Taylor_20260723_130951` (dispatch Mike ← user). Research-only, KHÔNG wire production.
> Nguồn: BQ `tav2_bq.ticker`/`ticker_financial`; panel `fearbuy_screen/episodes4.csv` (universe_pit, point-in-time).

## 1. User claim — VERIFIED ĐÚNG
PVX = **Tổng CTCP Xây lắp Dầu khí VN** (ICB **2357** Heavy Construction / xây lắp dầu khí).
- **Biên siêu mỏng**: GPM ~10%, NPM_P0 = **3,1%** tại thời điểm screen fire (2011-12).
- **Kế toán POC (percentage-of-completion)** → LN sổ sách KHÔNG đi kèm tiền: CF_OA âm ở ĐA SỐ quý
  dù NP dương (2010Q2 NP +249B / CF_OA **−610B**; 2011Q1 NP +133B / CF_OA **−336B**).
- **TTM CF_OA/NP KHÔNG bao giờ ≥1 khi NP dương**: quý "qualify" duy nhất (2011Q3) TTM = **0,67**
  (tiền chỉ đậy 67% lợi nhuận). Cumulative **3Y CF_OA/NP = −0,31** (âm).
- **Đòn bẩy nổ**: Debt_Eq 2,4→3,6→**3,7**→6,1→8,58→9,11. Vào insolvency: 2013Q2 NP **−1.194B**/quý.
- Screen fire 2011-12-15 (PB 0,63, mkt_dd −33%) ngay TRƯỚC sập 2011Q4 (NP −178B). **r24 = −57%→−70%.**

**Vì sao FEARBUY v1 lọt**: rule dùng `CF_OA_P0>0` **1 quý** → bắt đúng cú lumpy 2011Q3
(CF_OA_P0 +213B >0) trong khi bức tranh nhiều-năm là cash-lag-profit kinh niên.

## 2. User fix #1 (đo CF_OA≥NP liên tục 2-3 năm) — TEST → **REJECT (false-negative nặng)**
Áp trên case library. Cumulative 3Y CF_OA/NP tại fire-quarter:

| Case | 3Y CF_OA/NP | Kết quả thực | Gate CF≥NP |
|---|---|---|---|
| PVX 2011 | **−0,31** | LOSER −57% | reject ✅ đúng |
| **PNJ 2015** | **−0,46** | **WINNER +148%** | reject ❌ SAI |
| **VEA 2019** | **−0,28** | **WINNER (cash-cow cổ tức)** | reject ❌ SAI |
| TV1 2026 | +1,64 | QUALIFY | keep ✅ |
| HPG 2022 | +0,83 | QUALIFY (cyclical) | keep ✅ |

→ **Cash-conversion KHÔNG phân biệt được PVX (xấu) với PNJ/VEA (tốt)** — cả 3 đều âm 3Y.
PNJ ôm vốn lưu động trong **tồn kho vàng**; VEA lợi nhuận là **equity-method JV** (tiền về chậm dạng
cổ tức, nằm ở dòng đầu tư). CF_OA<NP là ĐÚNG cho họ nhưng KHÔNG phải red-flag. **Bỏ fix này.**

## 3. User fix #2 (lọc ngành) — một phần đúng nhưng BLUNT
- PVX ICB **2357** ≠ TV1 ICB **2791** (consulting) → loại nhóm xây lắp 23xx **KHÔNG** đụng TV1. An toàn.
- NHƯNG nhóm construction 2357 là HỖN HỢP: PVX/HBC-2022 lỗ nặng, mà HBC-2020 **+282%**, SCI-2020
  **+723%**, PHC-2020 **+114%** thắng lớn. Loại cả ngành = ném luôn winner. → sector-only quá thô.

## 4. Fix ĐỀ XUẤT — leverage ceiling `Debt_Eq_P0 ≤ 2,5` (solvency = tiền đề FEARBUY)
Backtest trên panel 273 episode (combined rule, dedup 420, universe_pit):

| Config | n | median ex24 | winrate | r24<−50% | sign-test/năm |
|---|---|---|---|---|---|
| Baseline | 273 | +13,2% | 57% | 3,7% | 6/8 (p=0,14) |
| **+ DE≤2,5** | 237 | **+15,0%** | 57% | 3,8% | **6/7 (p=0,06)** |
| + NPM≥0,05 | 163 | +19,2% | 58% | 3,1% | — (drop 41% pool) |
| + DE≤2,5 & NPM≥0,05 | 147 | +17,5% | 56% | 3,4% | 6/7 |

**DE≤2,5**: loại PVX (3,7) + **xoá trọn thảm hoạ năm 2012** (per-year 2012 −67% biến mất → 6/7 năm
dương, p cải thiện 0,14→0,06), median +1,8pp, tail giữ nguyên. Winner đã verify đều SỐNG (DGC/HPG/
SSI/HAH/DBC/DCM/DPM DE≤2,2).

### ⚠️ CAVEAT TRUNG THỰC — KHÔNG phải free lunch (đây là tail-insurance, KHÔNG phải alpha)
37 episode bị DE≤2,5 loại có **median r24 = +43,2%, mean +116%** — gate NÉM LUÔN nhiều V-recovery
đòn-bẩy-cao 2020: **LPB +297%, HDG +566%, SCI +723%, DTD +455%, TDC +303%, TCB +129%, NAB +186%**.
Gate đổi **đuôi phải (upside đòn bẩy)** lấy **cắt đuôi trái (PVX −70%, HBC-2022 −46%)**. Phù hợp mandate
sleeve (asymmetric, downside-protected) nhưng **median chỉ +1,8pp — coi là bảo hiểm tail, đừng bán như
return-enhancer.** NPM floor 1-quý càng mỏng manh (PNJ fire NPM −0,3% sẽ bị loại). Không dùng.

## 5. Kết luận (khớp chính triết lý doc: screen = CANDIDATE GENERATOR, DD thủ công = HARD GATE)
- **KHÔNG filter tự động nào tách sạch PVX khỏi mọi winner** — đây đúng lý do §5-caveat-3 đã ghi.
- Fix tự động đáng thêm nhất = **`Debt_Eq_P0 ≤ 2,5`** (tail-insurance, giải thích được: DN không thể
  "hồi phục" nếu vỡ nợ trước). User quyết ngưỡng (2,5 chặt hơn / 3,0 nhẹ tay hơn, cùng loại PVX+2012).
- Cân nhắc **loại hẳn financials/bank** khỏi sleeve (cần khung riêng: book quality/NPL/CAR).
- **Fix THẬT theo triết lý doc = tăng cường DISCRIMINATOR THỦ CÔNG**: thêm red-flag PVX vào checklist —
  ngành POC (xây lắp/EPC 23xx) + biên mỏng + CF_OA âm nhiều-năm + đòn bẩy tăng = "LN sổ sách là hư
  cấu kế toán, DN đang đi tới vỡ nợ". Con người giết PVX ở bước này, không phải ở screen.

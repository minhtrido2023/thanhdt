# Rà soát due-diligence toàn bộ ứng viên LAG — 2026-07-23

**Job** `Taylor_20260723_125437` (Mike dispatch, user chỉ đạo sau vụ TRC bị DollarBill tự đưa vào plan
bằng DCF override mà không escalate). **Loại:** rà soát/nghiên cứu — KHÔNG sửa production, KHÔNG tự
quyết TRC (đang HOLD chờ chính sách).

## 0. Kết luận nhanh (đọc cái này trước)

- **32 ứng viên LAG** đang chờ entry (signal 2026-07-23, `n_lag_recent=0` → CHƯA có mã nào đã vào, không
  có vị thế cần unwind). Tất cả là "upcoming".
- **Đã CÓ sẵn 1 lớp due-diligence TỰ ĐỘNG** trong `golive_recommend_v23.py` (gọi
  `trading_bot/due_diligence.py::run_due_diligence`) — in vào recommendation MD mỗi ngày: thanh khoản
  ADV3T, in/out `universe_pit`, cờ chất lượng (`quality_flag`), FA thô, cơ học surprise, DCF/lăng kính
  ngành. **Nhưng nó THUẦN THÔNG TIN** (Q-C, user chốt 2026-07-22) — KHÔNG chặn lệnh, KHÔNG buộc escalate.
- **Chỉ 5/32 (16%) đạt `QUALITY_OK`** (không banned ∧ qua golden floor ∧ rating 8L ≤3 ∧ trong universe):
  **CSV, GEE, HT1, NBC, VPB**. → xác nhận đúng nghi ngờ của user: "rất nhiều ứng viên LAG hiện nay không
  đạt chuẩn custom30V/CAPIT".
- Phân bố: **15/32 rating 8L ≥ 4** (fail nếu áp gate rating≤3), **12/32 FLOOR_FAIL**, **13/32 NGOÀI
  universe_pit** (thanh khoản mỏng/~0 hoặc mới niêm yết), **7/32 surprise nghi phồng cơ học** (nền có quý lỗ).
- **Gate LIVE hiện có cho LAG = CHỈ thanh khoản** (`lag_filter_illiquid` lọc ADV≤0/cũ >30d;
  `cap_lag_orders` trần 20%ADV). **KHÔNG có gate rating/quality nào** — đúng thiết kế backtest gốc (PEAD-only).
- **TRC**: RATING_FAIL (8L=4), qua floor, TRONG universe, thanh khoản MỎNG (1.37 tỷ < sàn 2 tỷ nhưng >0
  nên không bị lọc), DCF CHEAP (+40% MoS robust). Đây là câu hỏi CHÍNH SÁCH (mục 3), không tự quyết.

## 1. Bảng tổng hợp 32 ứng viên LAG (dữ liệu THẬT, BQ + universe_pit_q asof 2026-07-23)

Rating 8L: từ `universe_pit_q` (mã trong universe) hoặc panel `tav2_bq.fa_ratings_8l` (mã ngoài universe).
Cột "Cờ": quality_flag (mã trong universe) / OUT = ngoài universe_pit. ADV3T + FA + DCF từ recommendation MD.

| Mã | Book | 8L | Cờ chất lượng | ADV3T | Universe | Surprise | DCF/lăng kính | Ghi chú |
|----|------|----|--------------|-------|----------|----------|---------------|---------|
| **TCI** | LAG_HI | **5** | FLOOR_FAIL | 1.34 tỷ (mỏng) | in | ⚠ quý lỗ P2 | P/B-band RICH | CTCK, ROE_TTM 1.1% |
| **IVS** | LAG_HI | **5** | OUT | 175 tr (mỏng) | OUT | ⚠ quý lỗ P2 | P/B-band RICH | CTCK, ROE_Tr 1.9% — đã loại 07-21 |
| AFX | LAG_LO | 4 | FLOOR_FAIL | 674 tr (mỏng) | in | nền dương | 8L fallback | CF_OA_3Y≤0 |
| AGR | LAG_LO | 4 | FLOOR_FAIL | 4.46 tỷ | in | nền dương | P/B-band RICH | CTCK |
| PSI | LAG_LO | 4 | FLOOR_FAIL | 2.30 tỷ | in | nền dương | P/B-band CHEAP | CTCK |
| PXL | LAG_LO | 4 | FLOOR_FAIL | 397 tr (mỏng) | in | nền dương | 8L fallback | ROE5Y 0.3% |
| **MST** | LAG_LO | **4** | **RATING_FAIL** | 15.30 tỷ | in | nền dương | DCF RICH (không robust) | PE 40, ROE_Min3Y 2% |
| **TRC** | LAG_LO | **4** | **RATING_FAIL** | 1.37 tỷ (mỏng) | in | nền dương | **DCF CHEAP +40% robust** | cao su, PE 7.8, D/E 0.09 |
| DDN | LAG_HI | 4 | OUT | 4 tr (~0) | OUT | nền dương | 8L fallback | ROE_Min3Y 0.5%, D/E 3.87 |
| ITQ | LAG_HI | 4 | OUT | 145 tr (mỏng) | OUT | nền dương | 8L fallback | ROE5Y 0.1% |
| KHS | LAG_HI | 4 | OUT | 36 tr (~0) | OUT | nền dương | DCF CHEAP | ROE_Min3Y −3.7% |
| MCP | LAG_LO | 4 | OUT | 530 tr (mỏng) | OUT | ⚠ quý lỗ P1 | DCF RICH | PE 79 |
| UNI | LAG_HI | 4 | OUT | 3 tr (~0) | OUT | ⚠ quý lỗ P1,P2 | 8L fallback | PE −308, ROE ~0 |
| VLG | LAG_HI | 4 | OUT | 5 tr (~0) | OUT | nền dương | 8L fallback | CF_OA_3Y≤0 |
| VNP | LAG_HI | 4 | OUT | 454 tr (mỏng) | OUT | ⚠ quý lỗ P2 | DCF RICH | ROE_Min3Y −4% |
| BMS | LAG_HI | 3 | FLOOR_FAIL | 1.69 tỷ (mỏng) | in | nền dương | P/B-band RICH | CTCK |
| BSI | LAG_LO | 3 | FLOOR_FAIL | 8.30 tỷ | in | nền dương | P/B-band CHEAP | CTCK |
| EVF | LAG_LO | 3 | FLOOR_FAIL | 35.62 tỷ | in | nền dương | P/B-band CHEAP | tài chính, D/E 7.06 |
| FTS | LAG_LO | 3 | FLOOR_FAIL | 19.59 tỷ | in | nền dương | P/B-band RICH | CTCK |
| HCM | LAG_LO | 3 | FLOOR_FAIL | 117.86 tỷ | in | nền dương | P/B-band RICH | CTCK |
| VCI | LAG_LO | 3 | FLOOR_FAIL | 129.99 tỷ | in | nền dương | P/B-band CHEAP | CTCK |
| VND | LAG_HI | 3 | FLOOR_FAIL | 222.26 tỷ | in | nền dương | P/B-band CHEAP | CTCK |
| HAR | LAG_LO | 3 | OUT | 125 tr (mỏng) | OUT | nền dương | DCF RICH | ROE5Y 0.7% |
| SPM | LAG_HI | 3 | OUT | 1 tr (~0) | OUT | ⚠ quý lỗ P2 | DCF CHEAP | ROE5Y 1.4% |
| VE9 | LAG_LO | 3 | OUT | 2 tr (~0) | OUT | 🔴 PHỒNG CƠ HỌC (NP_P4≤0) | DCF RICH | ROE5Y −16.8% |
| GEE | LAG_LO | 3 | **QUALITY_OK** | 85.10 tỷ | in | nền dương | DCF RICH −245% | ROE5Y 22.9% |
| HT1 | LAG_HI | 3 | **QUALITY_OK** | 1.93 tỷ (mỏng) | in | nền dương | DCF CHEAP +53% | xi măng, FSCORE 8 |
| NBC | LAG_HI | 3 | **QUALITY_OK** | 308 tr (mỏng) | in | nền dương | DCF CHEAP +95% | than, FSCORE 8 |
| VPB | LAG_LO | 3 | **QUALITY_OK** | OK (bank) | in | nền dương | (bank) | ngân hàng |
| CSV | LAG_HI | 2 | **QUALITY_OK** | OK | in | nền dương | — | hoá chất |
| CLC | LAG_LO | 2 | OUT | 28 tr (~0) | OUT | nền dương | DCF RICH −6670% | FSCORE 7 nhưng ADV~0 |
| IDV | LAG_HI | 2 | OUT | 58 tr (~0) | OUT | nền dương | 8L fallback | ROE5Y 22% nhưng ADV~0 |

## 2. Thống kê & quan sát

**Rating 8L:** r5=2 (TCI, IVS) · r4=13 · r3=14 · r2=3 (CSV, CLC, IDV). → **rating≥4: 15/32 (47%)**.

**Cờ chất lượng (mã trong universe, 19 mã):** QUALITY_OK 5 · FLOOR_FAIL 12 · RATING_FAIL 2 (MST, TRC).
**Ngoài universe_pit: 13 mã** (ADV mỏng/~0 hoặc mới niêm yết).

**Thanh khoản:** chỉ ~10/32 có ADV3T ≥ sàn thin 2 tỷ. Phần lớn (thin <2 tỷ hoặc ~0) sẽ bị
**cap_lag_orders trần 20%ADV** siết size rất nhỏ, hoặc `lag_filter_illiquid` lọc thẳng (ADV≤0). Nghĩa là
đa số mã "rác" tự nhiên bị siết ở tầng thanh khoản — **nhưng KHÔNG bị chặn vì rating/floor**.

**Đặc thù mùa vụ quan trọng:** ~12/32 là **công ty chứng khoán / tài chính** (AGR, BMS, BSI, EVF, FTS,
HCM, IVS, PSI, TCI, VCI, VND + bank VPB). Q2/2026 là mùa BCTC CTCK bùng nổ (thị trường hồi) → LAG book
hiện đang **bị chi phối bởi surprise nhóm chứng khoán**. Nhóm này **hệ thống FLOOR_FAIL** vì golden floor
đòi `CF_OA_3Y>0`, mà dòng tiền HĐKD của CTCK (margin/tự doanh) biến động mạnh, âm hợp pháp → FLOOR_FAIL
với CTCK **KHÔNG cùng nghĩa "kém chất lượng"** như với DN sản xuất (giống bài học [[finance-domain-
grounding-not-pure-statistics]]). DCF cũng `financial_sector_excluded` → dùng lăng kính P/B-band. Đây là
lý do phải cẩn thận nếu định biến FLOOR_FAIL thành gate cứng: sẽ chặn nhầm nguyên một nhóm ngành.

**Surprise phồng cơ học (nền có quý lỗ → %YoY méo):** VE9 (🔴 NP_P4≤0, vô nghĩa), IVS, MCP, SPM, TCI,
UNI, VNP. Đây là dạng edge PEAD giả — surprise lớn do nền thấp/âm, không phải earnings power thật.

## 3. CÂU HỎI CHÍNH SÁCH — LAG có nên áp gate rating 8L ≤3 như custom30V/CAPIT? (KHÔNG tự quyết)

**Bối cảnh thiết kế:** LAG book (PEAD) entry gốc CHỈ dựa `NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5` — thuần
earnings-surprise, **cố ý KHÔNG gate rating**. Con số pin chính thức **R3 27.16% CAGR** đo trên chính
thiết kế đó — pool lịch sử ĐÃ bao gồm các mã rating 4/5 khi chúng có surprise. custom30V/CAPIT thì
NGƯỢC LẠI: chúng là rổ "chất lượng" nên golden-floor + rating≤3 là bản chất thiết kế.

### Hướng A — GIỮ NGUYÊN (LAG chỉ PEAD, không gate rating)
**Ưu:**
- Trung thành với backtest đã pin (27.16%). Không đưa gate chưa-đo vào production.
- PEAD là hiện tượng drift SAU tin, độc lập với chất lượng dài hạn — logic học thuật của PEAD không đòi
  chất lượng cao; thậm chí surprise ở mã "tệ" đôi khi drift mạnh hơn (under-reaction lớn hơn).
- Thanh khoản gate + %ADV cap đã tự siết phần lớn rủi ro thực thi. Hold 25td có giới hạn thời gian.

**Nhược:**
- Cho phép mua mã rating 4/5 / FLOOR_FAIL / surprise phồng cơ học — đúng loại "chất lượng kém" mà phần
  còn lại của hệ thống cố tránh. Mâu thuẫn triết lý với mandate due-diligence 07-21.
- Rủi ro giá trị: mua surprise giả (VE9-kiểu nền âm) = mua noise, không phải edge.
- Không có backstop khi PEAD signal trúng đúng mã đang có vấn đề cơ bản (rủi ro đuôi trái).

### Hướng B — ÁP gate rating≤3 (và/hoặc golden floor) cho LAG giống custom30V/CAPIT
**Ưu:**
- Nhất quán chuẩn chất lượng toàn hệ thống; loại surprise-giả và mã rác một cách hệ thống.
- Trực tiếp đóng lỗ hổng "DollarBill tự override" — nếu là gate cứng thì không cần nhớ.

**Nhược (LỚN — lý do phải backtest trước, không tự bật):**
- **THAY ĐỔI CHIẾN LƯỢC ĐÃ PIN** → 27.16% không còn hiệu lực, phải re-backtest self-check 0 VND +
  walk-forward IS/OOS + quant-skeptic. Có thể GIẢM edge (PEAD edge có thể nằm chính ở nhóm rating thấp).
- **Chặn nhầm cả nhóm ngành**: nếu dùng FLOOR_FAIL/golden-floor làm gate → xoá gần hết nhóm CTCK (12 mã)
  vì lý do sector-artifact chứ không phải kém thật. Rating≤3 đỡ hơn floor (giữ được BMS/BSI/EVF/FTS/HCM/
  VCI/VND rating 3) nhưng vẫn chưa đo.
- Mất tính "always-on" của LAG trong các mùa mà surprise tập trung ở mã rating thấp.

**Biến thể trung dung (nếu user muốn khám phá):** không gate cứng, mà **half-size** mã rating≥4 trong LAG
(tương tự cơ chế "weak → half-size trong BEAR/CRISIS" đã có ở BAL, dòng 519-530 golive_recommend). Vẫn
là thay đổi cần backtest, nhưng ít phá vỡ pool hơn gate cứng.

→ **Khuyến nghị quy trình (không phải quyết định):** nếu user/Mike nghiêng về B, việc đúng là Taylor
**backtest gate rating≤3 (và biến thể half-size) trên LAG book 2014→now**, báo Δ CAGR/Sharpe/DD + DSR +
LOO per-year, route quant-skeptic, RỒI mới quyết wire. Không bật gate lên live trước khi có số.

## 4. Đề xuất bước due-diligence TỰ ĐỘNG (sơ bộ — không implement ngay)

**Phát hiện quan trọng:** DD tự động **ĐÃ TỒN TẠI** và chạy mỗi ngày (`run_due_diligence` → recommendation
MD). Nên gap KHÔNG phải "thiếu DD tự động". Gap thực là **2 điểm**:
1. DD thuần thông tin — không có tín hiệu nào buộc DollarBill/Mike DỪNG hoặc ESCALATE khi mã xấu lọt vào.
2. DollarBill có thể override (như TRC dùng DCF CHEAP) mà không escalate — vụ việc gốc.

**Đề xuất (soft-gate escalation, GIỮ human-in-loop — KHÔNG auto-block, KHÔNG đổi backtest):**
- Thêm cột `dd_severity` (OK / WARN / **BLOCK-REVIEW**) vào output recommendation cho mỗi ứng viên, suy
  từ các cờ ĐÃ có (không tính lại gì): **BLOCK-REVIEW** khi rating≥4 **HOẶC** FLOOR_FAIL **HOẶC** ngoài
  universe **HOẶC** surprise phồng cơ học (nền lỗ). WARN khi thanh khoản mỏng / DCF RICH robust.
- Ở tầng **DollarBill lập plan**: nếu 1 ứng viên `dd_severity=BLOCK-REVIEW` được đưa vào plan, DollarBill
  **BẮT BUỘC** ghi `dd_override_reason` + `escalate=true` (event `question` tới Mike), thay vì tự override
  im lặng. Đây là mở rộng đúng của due-diligence HARD gate đã có (forensic_flags/>7%NAV/first-buy/DCF
  RICH-override/anomaly Tier-H) sang thêm điều kiện rating/floor/universe/surprise-cơ-học.
- **Ranh giới giữ nguyên:** đây là gate ESCALATE (buộc con người xem), KHÔNG phải gate CHẶN LỆNH tự động
  → không đụng vào chiến lược đã pin, không cần re-backtest (chỉ là lớp quy trình/quan sát). Khác hoàn
  toàn với Hướng B ở mục 3 (gate chặn = đổi chiến lược, cần backtest).
- Tùy chọn bổ sung: cờ CTCK/tài chính riêng để BLOCK-REVIEW **không** kích hoạt vì FLOOR_FAIL sector-
  artifact (tránh báo động giả cả mùa BCTC chứng khoán) — dùng rating≥4 + surprise-cơ-học làm trigger
  chính cho nhóm này thay vì floor.

Thiết kế này bám sát mandate 07-21 ("due-diligence mặc định cho MỌI candidate, để LỘ điểm hệ thống cần
sửa") mà không phá vỡ tính auditable của backtest LAG. Cần user/Mike duyệt hướng trước khi Taylor
implement + route quant-skeptic.

## Nguồn dữ liệu
- `deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-07-23.md` (DD tự động + FA + DCF)
- `tav2_mike.universe_pit_q` (quality_flag + rating_8l point-in-time, asof 2026-07-23)
- `tav2_bq.fa_ratings_8l` (rating panel cho 13 mã ngoài universe)
- `trading_bot/due_diligence.py` (logic DD), `mike/bin/build_universe_pit_quality.py` (taxonomy cờ)
- `data/golive_v23_status.json` (n_lag_recent=0, n_lag_upcoming=32)

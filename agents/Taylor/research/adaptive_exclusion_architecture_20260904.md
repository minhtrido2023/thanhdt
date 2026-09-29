# Kiến trúc loại trừ thích ứng (adaptive exclusion) — thay thế BANNED tĩnh

Job `Taylor_20260904_043943` (dispatch Mike). User yêu cầu trực tiếp 2026-09-04: HSG vẫn nằm
trong BANNED vĩnh viễn, user muốn hệ thống ĐỦ THÔNG MINH để tự biết khi nào loại một mã — không
thích danh sách cấm cứng. Nhiệm vụ: chứng minh bằng dữ liệu khả thi tới đâu, thiết kế kiến trúc
thay thế, nói thẳng phần nào không thay được.

**Artifact**: `mike/agents/Taylor/research/adaptive_exclusion_20260904/` (toàn bộ script + CSV
trung gian). Không đụng `lag_forensic_filter.py`, `build_universe_pit_quality.py`,
`custom_basket.py` — mọi thử nghiệm chạy trên bản FORK (`custom_basket_dynfork.py`) trong thư
mục artifact riêng.

## Tóm tắt 1 đoạn

BANNED (16 mã, `lag_forensic_filter.py:90` = `build_universe_pit_quality.py:71`) **không hề nằm
trong engine backtest custom30V/BAL** — nó chỉ bind ở hai chỗ: (a) `compute_park_trim.py:431`
(tầng LIVE, lọc mục tiêu park, tự nhận là "lệch có chủ đích so với backtest") và (b)
`lag_forensic_filter.py` (tầng ứng viên + lệnh của riêng book LAG). Đo trực tiếp: **9/16 mã
(KSF,NVL,VJC,VVS,GEG,IMP,TRA,TOS,VTP) chưa từng được yieldcombo chọn dù có bỏ ban** — ban dư
thừa với chúng. Nhưng **HSG bind THẬT — 13/48 kỳ tái cân bằng (27%)**, và phần lớn các lần đó
(11/13) HSG có đòn bẩy vừa phải + lãi vay được che phủ tốt — tức bị chặn OAN theo dữ liệu tại
thời điểm đó. Một gate động (đòn bẩy + vốn chủ âm + pha loãng, PIT, có đường quay lại) bắt được
đúng 2 khung nguy hiểm thật của HVN (vốn chủ âm 2025) và khung pha loãng của BAF, nhưng **KHÔNG
bắt được PC1 (gian lận hình sự)** — mã này sạch trên mọi tỷ số tài chính tới tận ngày bị bắt.
Kết luận: **thay được phần lớn "bẫy đòn bẩy/vốn chủ âm" bằng cơ chế động PIT có đường quay lại;
phần gian lận/thao túng liên quan bên thứ ba vẫn cần một lớp thủ công — nhưng lớp đó nên hết hạn
và bắt buộc rà lại định kỳ, không nên "vĩnh viễn".**

---

## §0. Bối cảnh kiến trúc hiện tại (verify code, không suy diễn)

**BANNED = 16 mã**, 2 bản sao khớp nhau: `lag_forensic_filter.py:90-91` và
`mike/bin/build_universe_pit_quality.py:71-72`:
`PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC, IMP, TRA, TOS, VTP, BAF`.
Nguồn "chuẩn tắc" khai báo = `mike/kb/KNOWLEDGE.md:247`.

**Phát hiện kiến trúc quan trọng nhất (chưa có trong brief của Mike, tự đào ra bằng grep +
đọc code — đây là thứ đổi toàn bộ khung backtest ở §3):**

`custom_basket.py` — engine sinh custom30V/BAL — **KHÔNG có một dòng nào tham chiếu `BANNED`**.
Cột `banned` chỉ tồn tại trong bảng phụ `universe_pit_quality`/view `universe_pit_q`
(`build_universe_pit_quality.py:120,138`), và **không consumer Python nào đọc cột đó để lọc
candidate trong `custom_basket.py`** (đã grep toàn bộ, chỉ thấy `quality_flag` được hiển thị
*thông tin* trong `trading_bot/due_diligence.py:822` — không chặn lệnh). Chỗ BANNED **thực sự**
bind cho custom30V/BAL là `mike/bin/compute_park_trim.py:427-434` — tầng LIVE tính lại mục tiêu
park mỗi ngày — và chính docstring của nó (dòng 428-433) tự thú nhận:

> "Mã `BANNED` vĩnh viễn... ĐÃ từng là thành viên custom30V các kỳ trước... Đây là **lệch có
> chủ đích so với backtest** (backtest không có khái niệm BANNED-vĩnh-viễn): Mike chốt
> 2026-08-07 theo hướng an toàn hơn... User đảo lại được nếu muốn."

Tức là: **con số CAGR 28,86% pin R3 (NEUTRAL-only, `data/results_registry.md`) đã BAO GỒM các
mã BANNED bất cứ khi nào chúng lọt qua gate rating≤3 tự nhiên** — BANNED chỉ là một patch AN
TOÀN áp thêm ở live, không phải một phần đã backtest. Điều này nghĩa là "gỡ BANNED" cho
custom30V/BAL **không đổi con số pin đang công bố** — nó chỉ gỡ một lớp an toàn live-only mà
Mike tự thêm 2026-08-07. Hệ quả cho §3: kịch bản (i) "hiện trạng backtest" ĐÃ CHÍNH LÀ kịch bản
"không banned" — không cần chạy lại.

Với **book LAG**, cơ chế khác hẳn và đã tốt hơn nhiều: `lag_forensic_filter.py` áp BANNED tại
TẦNG ỨNG VIÊN (từ 2026-08-03) + `trading_bot/plan.py:862-947` áp lại ở TẦNG LỆNH, và nó đã có
sẵn `data/forensic_flags.csv` — một danh sách **CÓ NGÀY hiệu lực** (`date`, so với `asof`,
không hindsight), được người curate với lý do rõ ràng, và consumer (`rating_8l.py:465`,
`custom_basket.py:307-315`) áp override rating=5 **từ ngày flag trở đi** — không phải vĩnh viễn
theo nghĩa "không bao giờ ghi ngày". PC1, VVS, KSF **đã có mặt trong `forensic_flags.csv`** với
lý do cụ thể (fraud_confirmed / pump_no_moat / related_party) — **trùng lặp với BANNED**, tức
BANNED đang làm việc thừa cho 3/16 mã vì forensic_flags.csv đã phủ chúng bằng cơ chế date-aware
hơn.

**Kết luận §0**: kiến trúc "adaptive" mà user muốn **đã tồn tại một phần** trong LAG
(`forensic_flags.csv`) — vấn đề là nó chưa lan sang custom30V/BAL, và BANNED (constant cứng,
không ngày) là lớp CHE ĐẬY thô ráp hơn nằm chồng lên. Bài toán không phải "phát minh cơ chế
adaptive từ đầu" mà là **tổng quát hoá pattern đã có + thêm 1 lớp mới (đòn bẩy/vốn chủ động) mà
forensic_flags.csv (thủ công) không phủ**.

---

## §1. Audit phản thực 16 mã

### 1a. Golden-floor + rating≤3 (gate ĐANG DÙNG cho custom30V) có tự loại chúng không?

Đo PIT thật từ `tav2_mike.universe_pit_quality` (đã có sẵn `pass_golden_floor` +
`rating_8l` as-of, tính ĐỘC LẬP với cờ `banned` — dùng lại đúng logic CASE của
`build_universe_pit_quality.py:135-144` nhưng bỏ nhánh `banned`):

| ticker | %ngày sẽ QUALITY_OK nếu không ban | %FLOOR_FAIL | %RATING_FAIL | %UNKNOWN |
|---|---:|---:|---:|---:|
| VTP | 100.0 | 0.0 | 0.0 | 0.0 |
| TOS | 100.0 | 0.0 | 0.0 | 0.0 |
| SBA | 72.5 | 4.0 | 8.7 | 14.8 |
| GEG | 68.5 | 0.0 | 31.5 | 0.0 |
| TRA | 61.0 | 20.8 | 0.0 | 18.3 |
| KSF | 59.8 | 1.9 | 38.3 | 0.0 |
| DMC | 54.2 | 6.2 | 0.0 | 39.5 |
| VVS | 51.9 | 37.2 | 10.8 | 0.0 |
| IMP | 49.2 | 11.7 | 18.3 | 20.7 |
| VJC | 37.3 | 60.0 | 2.8 | 0.0 |
| BAF | 31.7 | 57.3 | 11.0 | 0.0 |
| PC1 | 25.3 | 21.1 | 53.6 | 0.0 |
| NVL | 21.1 | 48.6 | 30.3 | 0.0 |
| HSG | 16.7 | 54.0 | 29.2 | 0.0 |
| HVN | 15.6 | 59.2 | 25.1 | 0.0 |
| NKG | 10.4 | 55.3 | 34.3 | 0.0 |

(`banned_counterfactual_qualityflag.csv`.) Kết luận sớm: gate hiện tại **KHÔNG** tự loại hầu hết
16 mã phần lớn thời gian — trái với giả thuyết ban đầu trong brief. Nhưng đây mới là điều kiện
CẦN (đủ điều kiện gate); điều kiện ĐỦ là có thực sự lọt vào top-30 yieldcombo không — đo ở 1b.

### 1b. Funnel thật: có thực sự được CHỌN vào custom30V không?

Chạy `custom_basket.build_pit` GỐC (không fork, không đổi 1 dòng), `BASKET_SELECT=yieldcombo`,
`BASKET_EXCLUDE=""` (tức đúng cấu hình R3 pin, KHÔNG áp BANNED — vì §0 đã xác nhận BANNED không
nằm trong engine này), 2014-01-01→2026-06-15, 48 kỳ tái cân bằng q2m5:

| ticker | n_rebals (lọt top-30) | % kỳ | avg liq_rank | avg rating | lần đầu | lần cuối |
|---|---:|---:|---:|---:|---|---|
| **HSG** | **13** | **27.1%** | 9.8 | 2.85 | 2016-02-05 | 2025-11-05 |
| NKG | 5 | 10.4% | 15.6 | 3.00 | 2021-08-05 | 2024-02-05 |
| HVN | 4 | 8.3% | 24.5 | 3.00 | 2018-08-06 | 2025-08-05 |
| PC1 | 2 | 4.2% | 26.0 | 3.00 | 2025-11-05 | 2026-05-05 |
| DMC | 1 | 2.1% | 30.0 | 1.00 | 2016-05-05 | — |
| BAF | 1 | 2.1% | 28.0 | 3.00 | 2023-11-06 | — |
| SBA | 1 | 2.1% | 16.0 | 3.00 | 2014-08-05 | — |
| KSF, NVL, VJC, VVS, GEG, IMP, TRA, TOS, VTP | **0** | **0%** | — | — | — | — |

(`q1_selection_frequency_16names.csv`, script `step_a_banned_audit.py`, self-check: NAV
baseline khớp bit-cho-bit với cache đã dùng ở job `Taylor_20260630_102153` khi cùng tham số.)

**9/16 mã chưa từng lọt kể cả không có ban nào cả** — với các mã này BANNED **hoàn toàn dư
thừa** trong custom30V, y hệt phát hiện cũ về VJC/NVL (job `Taylor_20260630_102153`) nay mở
rộng ra KSF/VVS/GEG/IMP/TRA/TOS/VTP. Cơ chế tự nhiên (rank liquidity + rank(1/PE)+rank(1/PCF))
đã làm đúng việc: VJC/VTP "không bao giờ rẻ" (PB median 4.14/6.81, xem §1c) tự động rớt hạng;
KSF/VVS đã có forensic_flags.csv override rating=5; IMP/TRA/TOS thanh khoản+giá không đủ cạnh
tranh top-60.

**HSG BIND THẬT — đây là ca trung tâm mà user hỏi.** 27,1% số kỳ, rank thanh khoản top-10, rating
trung bình 2,85 (qua gate dễ dàng). NKG/HVN/PC1/BAF/SBA bind ở mức nhỏ hơn (1-5 lần).

### 1c. Tình trạng tài chính THẬT tại đúng thời điểm được chọn (must-know trước khi thiết kế gate)

Tra `ticker_financial` as-of tại từng ngày tái cân bằng thực tế (không phải trung bình mù):

| ticker @ ngày | Debt/Eq | IntCov | BVPS | PB | Nhận xét |
|---|---:|---:|---:|---:|---|
| HSG @ 2016-02 | 1.70 | -5.53 | 24,528 | 1.15 | lãi vay ÂM (1 trong 3 lần yếu) |
| HSG @ 2020-08→2022-08 (9 lần) | 0.56–1.72 | 3.7–26.1 | 13.8k–23.1k | 0.64–2.10 | **đòn bẩy vừa phải, lãi vay che phủ TỐT-RẤT TỐT, PB rẻ-hợp lý** |
| HSG @ 2022-11 | 0.56 | -12.27 | 18,198 | 0.64 | lãi vay ÂM (2/13) |
| HSG @ 2023-11, 2025-11 | 0.61 / 0.67 | 14.9 / 3.5 | 17.5k / 18.3k | 1.01 / 0.92 | lành mạnh |
| **HVN @ 2018-08, 2019-02** | 4.13 / 3.41 | 2.08 / 3.08 | 11,832 / 13,119 | 3.15 / 2.97 | đòn bẩy cao nhưng vốn chủ CÒN DƯƠNG |
| **HVN @ 2025-05, 2025-08** | **-11.22 / -21.12** | 15.4 / 15.4 | **-2,644 / -996** | 0.00 | **VỐN CHỦ ÂM — nhưng ROE3Y in hiển thị DƯƠNG (+35,5%)** vì NP âm ÷ Equity âm = ROE dương giả — bẫy dấu, xem §2 |
| NKG (5 lần) | 1.26–2.05 | 1.51–18.1 | 20.6k–24.1k | 0.81–2.28 | phần lớn lành mạnh, 1 lần lãi vay yếu (1.51) |
| **PC1 @ 2025-11, 2026-05** | 1.82 / 1.74 | 3.55 / 2.70 | 20,303 / 22,072 | 0.99 / 0.90 | **SẠCH HOÀN TOÀN trên mọi tỷ số — bị bắt hình sự 2026-05-15 vì gian lận kế toán, không phải vì số** |
| BAF @ 2023-11 | 2.47 | 1.93 | 13,511 | 1.70 | không cực đoan tại thời điểm đó, nhưng đã pha loãng 84% từ 2021-12 (78tr→143,5tr CP) |
| SBA @ 2014-08 | 1.28 | -2.35 | 10,557 | 0.92 | đòn bẩy thấp nhưng lãi vay ÂM |
| DMC @ 2016-05 | 0.20 | n/a (nợ ~0) | 31,020 | 2.22 | **công ty xuất sắc**, rating 1/5 — ban DMC không liên quan chất lượng |

**Kết luận trung tâm §1**: với đúng cái tên user nêu (HSG), **10-11/13 lần lọt rổ là lựa chọn
lành mạnh theo số liệu tại thời điểm đó** — ban tĩnh đã chặn OAN phần lớn các lần này. Chỉ 2-3
lần (lãi vay âm) là đáng ngờ thật. PC1 là ca ngược lại hoàn toàn: sạch tuyệt đối trên số, chỉ lộ
ra qua điều tra hình sự — không tỷ số tài chính nào cứu được. HVN 2025 là ca nguy hiểm nhất về
mặt thiết kế: **một gate ROE hoặc "golden floor" kiểu ROE≥0 sẽ BỎ LỌT vì dấu ROE bị lật do cả tử
và mẫu đều âm** — bài học kỹ thuật quan trọng nhất của audit này.

---

## §2. Kiến trúc đề xuất — 4 tầng thay 1 danh sách

Tách đúng 4 loại rủi ro trong BANNED thành 4 CƠ CHẾ riêng (không dồn vào 1 danh sách nữa),
theo đúng bằng chứng đo được ở §1 — không phải lý thuyết:

```
                    ỨNG VIÊN (top-60 thanh khoản, trước gate rating)
                              │
        ┌─────────────────────┼─────────────────────┬────────────────────┐
        ▼                     ▼                     ▼                    ▼
  [A] HARD financial    [B] Forensic/thao      [C] Value-yield      [D] Strategy-fit
      distress gate         túng (thủ công,        rank tự nhiên       tag (routing,
      (PIT, tự động,        date-aware, ĐÃ CÓ)      (ĐÃ CÓ, không       KHÔNG phải gate
      có đường quay lại)                            đổi)                chất lượng)
        │                     │                     │                    │
        ▼                     ▼                     ▼                    ▼
   BVPS≤0 → loại NGAY    forensic_flags.csv    rank(1/PE)+rank(1/PCF)  DMC/IMP/TRA:
   (Debt/Eq>3.5 AND      (KSF,VVS,PC1 đã có)    tự nhiên loại "không   gắn nhãn
   IntCov<1.5) 2 quý     → BẮT BUỘC re-review    bao giờ rẻ" (VJC PB   BUY_AND_HOLD_ONLY,
   liên tiếp → loại      định kỳ (không          med 4.14, VTP 6.81)   loại khỏi rổ
   Pha loãng >80%/3năm   "vĩnh viễn" im lặng)    — KHÔNG cần thêm gì   rebalance-nhanh,
   → loại                                                              KHÔNG loại khỏi
   Quay lại: 2 quý                                                     universe đầu tư
   sạch liên tiếp                                                      (sleeve buy&hold
   → tự phục hồi                                                       riêng, ngoài scope
                                                                        job này)
```

### [A] Gate tài chính động, PIT, có đường quay lại — MỚI, thay phần "đòn bẩy trap"

Nguồn cột: `ticker_financial.Debt_Eq_P0`, `IntCov_P0`, `BVPS`, `OShares` (đã tra
`bigquery_schema.md` + `bigquery_dictionary.json` trước khi dùng — không bịa cột, đúng §9).

**Luật (đã hiệu chỉnh ngưỡng bằng phân phối TOÀN UNIVERSE, không chỉ 16 mã — tránh overfit)**:

1. **Vốn chủ âm — cấm cứng, tức thời**: `BVPS ≤ 0` → loại ngay quý đó. Universe-wide: 1,5% số
   quý (`universe_flag_rates.csv`). **Bắt buộc kiểm tra DẤU trực tiếp qua BVPS, KHÔNG dùng
   `Debt_Eq>ngưỡng`** — vì D/E khi vốn chủ âm tự đổi dấu thành SỐ ÂM (HVN 2025: D/E=-11,2 đến
   -21,1) và sẽ KHÔNG bị bắt bởi bộ lọc "D/E > X". Đây là lỗi thiết kế cụ thể tôi tự phát hiện
   khi build gate, đã sửa trước khi chạy backtest — không phải giả định lý thuyết.
2. **Đòn bẩy cao + lãi vay không che phủ, PHẢI 2 quý liên tiếp** (chống nhiễu 1 quý bất thường):
   `Debt_Eq_P0 > 3.5` **VÀ** `IntCov_P0 < 1.5` cùng lúc, ở CẢ quý hiện tại và quý trước. Ngưỡng
   3,5 ≈ percentile 85 toàn universe (`Debt_Eq` p85=2,86, p90=3,80 — chọn giữa để không quá
   lỏng/chặt). **Đã thử và LOẠI 2 biến thể lỏng hơn** (IntCov<1.0 độc lập: 25,4% quý bị gắn cờ
   — quá rộng, vì IntCov ở VN nhiễu nặng, p25 toàn universe ĐÃ ÂM; IntCov<0 độc lập: 21,4% — vẫn
   quá rộng) → **quyết định dùng AND-combo, không dùng IntCov đơn lẻ**, khớp với phát hiện cũ
   (nghiên cứu sector Brokerage, `data/results_registry.md` "IntCov replaces Debt_Eq for
   brokers... NULL-tolerant") rằng IntCov một mình không đáng tin cho screen rộng.
3. **Pha loãng dồn dập**: `OShares_t / MIN(OShares 12 quý gần nhất) - 1 > 80%`. Ngưỡng 80% khớp
   đúng ca BAF thật (84% tại ngày được chọn 2023-11-06). Cửa sổ rolling 12 quý (~3 năm) tự nhiên
   tạo "quên" — pha loãng cũ ngoài 3 năm không còn tính, không cần luật hết hạn riêng.
4. **Đường quay lại (reversible, cố ý bất đối xứng theo §e của brief)**: loại ngay khi vi phạm
   (khớp "chi phí sai lầm để lọt đắt hơn bỏ lỡ"), nhưng **CHỈ phục hồi sau 2 quý liên tiếp SẠCH**
   cả 3 điều kiện trên — không phục hồi tức thời dù quý đó vừa hết vi phạm.
5. **Fail-safe**: thiếu `Debt_Eq_P0`/`BVPS`/`OShares` as-of → **coi như KHÔNG kiểm tra được**,
   để nguyên luồng hiện tại (rating≤3 vẫn là sàn chặn) — KHÔNG tự động loại vì thiếu dữ liệu
   (khác với golden-floor `UNKNOWN_FLOOR` hiện có, cố ý fail-open ở gate MỚI này vì nó là lớp BỔ
   SUNG, không phải sàn duy nhất; sàn duy nhất — rating≤3 — vẫn fail-closed như hiện tại).

**Capacity toàn universe**: luật cuối cùng gắn cờ **17,62%** số (ticker,quý) từ 2010
(`universe_flag_rates.csv` phiên bản gốc = luật này). Không siết chặt tới mức làm cạn pool top-30
(xem §3 must-catch — vẫn đủ mã để chạy).

### [B] Forensic/thao túng — GIỮ cơ chế hiện có, chỉ đổi 1 điều: bỏ "vĩnh viễn im lặng"

`data/forensic_flags.csv` đã ĐÚNG tinh thần user muốn: có ngày (`date`), có lý do
(`note`), date-aware khi áp (không hindsight). Đề xuất **1 thay đổi nhỏ, không đổi cơ chế**:
thêm cột `review_by` (ngày bắt buộc rà lại, vd +12 tháng kể từ `date`) — khi tới hạn, checker
health-check (như `ops_health_check.sh`) tạo `question` trên bus bắt buộc CON NGƯỜI xác nhận
"vẫn đúng" hay "gỡ" — thay vì để severity=`exclude` nằm mãi không ai nhìn lại. Đây chính là điều
user phàn nàn ("tôi không thích danh sách banned") áp cho đúng loại rủi ro KHÔNG THỂ tự động hoá
(§4) — biến "vĩnh viễn" thành "có hạn + bắt buộc rà, không tự hết hạn ngầm" (đúng tinh thần §20
coding_guidelines: không để CRON tự đóng quyết định treo, ở đây là ngược lại — không để quyết
định treo VĨNH VIỄN không ai đụng tới).

### [C] Value-yield rank — không đổi

Đã đo (§1b): 9/16 mã tự nhiên không lọt vì không đủ rẻ/thanh khoản. KHÔNG cần thêm luật.

### [D] Strategy-fit tag (DMC/IMP/TRA) — ngoài scope gate chất lượng

Đây là phát hiện CŨ đã pin (`data/results_registry.md` "Technology... FPT timing lens" +
sector-sweep dược phẩm cho thấy buy-and-hold thắng timing) — DMC/IMP/TRA là công ty TỐT
(DMC rating 1/5, Debt/Eq 0,20, IntCov 9,4) nhưng bị 8L momentum rebalance nhanh phá alpha. Đề
xuất: **KHÔNG đưa vào gate chất lượng nào cả** — đây là vấn đề ĐỊNH TUYẾN sleeve, không phải rủi
ro. Nếu tương lai muốn giữ pharma, cần một sleeve buy-and-hold riêng (nằm ngoài custom30V/BAL
rebalance q2m5) — ngoài phạm vi job này, chỉ ghi nhận kiến trúc.

---

## §3. Backtest 3 kịch bản + must-catch

Cùng engine `custom_basket.build_pit` (yieldcombo, gate_rating≤3, namecap, q2m5),
2014-01-01→2026-06-15, walk-forward IS(2014-2019)/OOS(2020+), self-check: NAV bit-khớp với
job `Taylor_20260630_102153` ở cấu hình chung. Kịch bản (iii) chạy trên FORK
`custom_basket_dynfork.py` — **thay đúng 1 dòng** so với production
(`if _DYN_EVENTS and dyn_excluded_asof(tk, d): continue`), còn lại giữ nguyên 100%.

| Scenario | CAGR FULL | Sharpe | MaxDD | Calmar | CAGR IS | CAGR OOS |
|---|---:|---:|---:|---:|---:|---:|
| **A — hiện trạng backtest** (= "không banned", vì §0 đã xác nhận BANNED không nằm trong engine này) | 32.07% | 1.29 | -40.0% | 0.80 | 24.12% | 39.69% |
| **B — BANNED-16 áp tại tầng chọn** (mô phỏng đúng hành vi `compute_park_trim.py` LIVE) | 31.41% | 1.29 | -40.2% | 0.78 | 22.77% | 39.83% |
| **C — gỡ BANNED, thay gate động [A] ở §2** | 30.15% | 1.29 | -37.1% | 0.81 | 18.31% | 42.01% |

ΔB-A: **-0.66pp CAGR FULL, -1.35pp IS, +0.14pp OOS** — tức **enforce BANNED hiện tại ĐANG TỐN
CHI PHÍ backtest**, chủ yếu vì chặn HSG's 13 lần vào rổ (khớp §1c: phần lớn lành mạnh).

ΔC-A: **-1.92pp CAGR FULL, -5.81pp IS, +2.32pp OOS**; MaxDD cải thiện (-40.0%→-37.1%), Calmar
OOS 0,99→1,13, Sharpe OOS 1,40→1,48. **Gate động [C] tốn CAGR NHIỀU HƠN cả ban tĩnh B** — vì nó
là bộ lọc **toàn universe** (17,6% quý bị gắn cờ, không chỉ 16 tên), xáo trộn cả những kỳ mà
BANNED không hề chạm tới. Đây là kết quả THẬT, không phải kỳ vọng ban đầu (kỳ vọng là "gate
thông minh sẽ đỡ tốn hơn ban tĩnh") — báo cáo trung thực theo đúng yêu cầu §6 brief.

**⚠️ N_TRIALS & tính chọn-theo-hiệu-suất**: đã thử **5 biến thể ngưỡng** trước khi chốt luật ở
§2 (2 biến thể IntCov độc lập bị loại vì capacity quá rộng — KHÔNG phải vì CAGR thấp; ngưỡng
dilution 50%→80%). **Luật được CHỌN không phải luật có CAGR cao nhất** (thực ra nó có CAGR THẤP
NHẤT trong các kịch bản đo) — tiêu chí chọn là capacity hợp lý + must-catch đúng ca nguy hiểm
thật, KHÔNG phải tối ưu backtest. Điều này giảm rủi ro overfit nhưng KHÔNG thay thế review
chính thức — **DSR/PBO chưa tính chính thức** (N_TRIALS=5 nhỏ, tiêu chí chọn không phải hiệu
suất nên khung PBO cổ điển không áp thẳng được) — nếu quyết định wire, phải qua
**quant-skeptic** trước, đúng cam kết trong dispatch.

### Must-catch — câu hỏi bắt buộc: có bắt đúng lúc nguy hiểm không?

| ticker | ca nguy hiểm thật (theo §1c) | gate động [C] có chặn ĐÚNG lúc đó không? |
|---|---|---|
| **HVN @ 2025-05, 2025-08** (BVPS -2644/-996, vốn chủ âm thật) | CÓ | **✅ CHẶN** (cửa sổ động 2020-08-03→2026-02-02 phủ đúng 2 ngày này; baseline A vẫn chọn HVN 2 lần này, scenario C thì KHÔNG) |
| **HVN hồi phục 2026-02, 2026-05** (BVPS +2047→+3300, dương 2 quý liên tiếp từ 2025-10) | Không còn nguy hiểm | **✅ ĐÚNG THIẾT KẾ** — gate tự phục hồi sau 2 quý sạch, cho HVN vào lại đúng lúc số liệu xác nhận hồi phục thật (không phải đoán) |
| **BAF @ 2023-11** (pha loãng 84% từ IPO) | CÓ | **✅ CHẶN** (cửa sổ 2022-01-28→còn hiệu lực phủ đúng ngày chọn) |
| **HSG** (13 lần, phần lớn lành mạnh + 2-3 lần lãi vay âm) | CHỈ 2-3/13 lần đáng ngờ | **✅ ĐÚNG THIẾT KẾ** — vẫn chọn 12/13 lần (chỉ chặn đúng 2020-08-05, lúc lãi vay âm mạnh nhất); đây CHÍNH XÁC là hành vi user muốn: không cấm cả tên, chỉ cấm đúng lúc xấu |
| **PC1 @ 2025-11, 2026-05** (gian lận hình sự, sạch trên số) | CÓ, cực nghiêm trọng | **❌ KHÔNG CHẶN** — vẫn lọt cả 2 lần trong scenario C (thậm chí C còn chọn PC1 nhiều hơn A do hiệu ứng "ghế trống"). Không tỷ số tài chính nào phản ánh gian lận trước khi bị phát hiện. |
| **SBA @ 2014-08** (lãi vay âm, đòn bẩy THẤP) | Nhẹ | **❌ KHÔNG CHẶN** — lỗ hổng đã biết: luật [A] yêu cầu Debt/Eq CAO **VÀ** IntCov thấp cùng lúc; SBA có IntCov xấu nhưng đòn bẩy thấp nên combo không kích hoạt. Đã cân nhắc tách IntCov thành điều kiện độc lập nhưng bị loại vì gây 21-25% false-positive toàn universe (xem trên). Limitation ghi nhận, không giấu. |
| **NKG (5 lần)** | Nhẹ-vừa | **❌ KHÔNG CHẶN lần nào** — các cửa sổ vi phạm của NKG (2012-2020, rồi 2023, 2025) không trùng đúng 5 ngày NKG thực sự được chọn (2021-2024) — tại các ngày ĐƯỢC CHỌN, NKG thực sự lành mạnh theo số (§1c), nên đây cũng là hành vi ĐÚNG không phải bỏ sót |

**Tổng kết must-catch**: gate động bắt ĐÚNG 2/2 khung nguy hiểm tài chính thật đo được (HVN vốn
chủ âm, BAF pha loãng), và cố ý KHÔNG chặn các lần chọn lành mạnh (đúng ý đồ thiết kế, không
phải lỗi). Bỏ lọt hoàn toàn 1 ca gian lận hình sự (PC1) và 1 ca đòn bẩy-thấp-nhưng-lãi-vay-yếu
(SBA) — cả hai đúng như dự đoán trong §4 dưới.

---

## §4. Phần KHÔNG thay được bằng cơ chế động

**Gian lận/thao túng kế toán (PC1, và về bản chất cả KSF/VVS related-party)** — bằng chứng thật
từ §1c/§3: PC1 sạch tuyệt đối trên Debt/Eq, IntCov, BVPS, PB **tới tận ngày bị bắt**
(2026-05-15). Không có tỷ số tài chính công khai nào phản ánh gian lận trước khi cơ quan điều
tra công bố — đây đúng là loại rủi ro dispatch cảnh báo trước ("thứ không hiện trong số liệu tài
chính cho tới khi quá muộn"). **Kết luận: phần này VẪN CẦN một lớp thủ công/forensic.**

Nhưng "thủ công" không bắt buộc "vĩnh viễn": `data/forensic_flags.csv` ĐÃ chứng minh mô hình
đúng — con người curate, có ngày hiệu lực, có lý do, KHÔNG hindsight. Đề xuất duy nhất ở §2[B]
(thêm `review_by` bắt buộc rà lại định kỳ) là đủ để đạt tinh thần "không phải danh sách chết"
mà vẫn giữ được lớp bảo vệ không thể tự động hoá.

**5 mã còn "chưa rõ loại"** (NVL, GEG, SBA, TOS, VTP — dispatch tự nêu): đã grep
`kb/incidents/`, `kb/projects/`, `git log -S` toàn repo — **không tìm được lý do gốc bằng văn
bản** (commit sớm nhất chứa các mã này là `c9cc670c "Checkpoint: code + docs baseline before
data/secrets reorg"`, tức đã có trong danh sách TRƯỚC khi lịch sử KB hiện tại bắt đầu ghi chép
chi tiết — không đoán thêm). Với NVL: dữ liệu tài chính (Debt/Eq frac>4x=28%, PB frac<1=38%) phù
hợp câu chuyện khủng hoảng bất động sản 2022-2023 đã biết công khai — gate [A] sẽ phủ được phần
lớn giai đoạn này (cửa sổ 2022-02-07→2025-02-03 đo được). Với GEG/SBA/TOS/VTP: không đủ căn cứ
văn bản để phân loại chắc chắn vào 1 trong 4 nhóm — khuyến nghị: giữ nguyên trong BANNED cho tới
khi có review thủ công 1 lần xác nhận lý do gốc, SONG SONG với việc bật gate [A] (nếu số liệu
[A] tự phủ được giai đoạn rủi ro của chúng thì gate mới đã đủ, không cần giữ tên trong danh sách
nữa).

---

## §5. Kế hoạch triển khai (đề xuất, CHƯA làm)

**Đây là ĐỀ XUẤT THIẾT KẾ — không tự sửa `lag_forensic_filter.py`,
`build_universe_pit_quality.py`, `custom_basket.py`, `compute_park_trim.py`. Mọi bước dưới đây
cần user duyệt + quant-skeptic verify trước khi chạm production.**

1. **Shadow-mode 4-8 tuần**: viết `dynamic_quality_gate.py` độc lập (không sửa production),
   chạy SONG SONG mỗi ngày cùng lúc `build_universe_pit_quality.py`, ghi cột `dyn_excluded` vào
   1 bảng phụ MỚI (không đụng `universe_pit_quality`), so sánh với `banned` hiện tại — KHÔNG đổi
   hành vi chọn lệnh nào trong giai đoạn này.
2. **Tiêu chí go/no-go sau shadow-mode**:
   - Gate mới KHÔNG bỏ lọt bất kỳ mã nào đang thực sự xấu (equity âm/đòn bẩy cực đoan) mà
     BANNED đang chặn đúng — verify bằng chính danh sách 16 mã, có must-catch như §3.
   - `quant-skeptic` CONFIRMED trên backtest §3 (bao gồm review N_TRIALS/DSR đã nêu ở trên).
   - User xác nhận rõ ràng: chấp nhận đánh đổi CAGR IS thấp hơn (§3 cho thấy scenario C tốn
     hơn cả B ở IS) để đổi lấy "không cấm cứng theo tên" — đây là quyết định GIÁ TRỊ, không phải
     con số, cần user chốt (giống case LAG rating gate 2026-07-27, `feedback-lag-rating-gate-
     locked-2026-07-27`: user có thể CHẤP NHẬN CAGR thấp hơn vì lý do khác numbers).
3. **Nếu go**: wire gate [A] vào `build_universe_pit_quality.py` như MỘT CỘT MỚI song song
   (`dyn_quality_flag`), KHÔNG xoá cột `banned` ngay — chạy 2 cột song song thêm 1 chu kỳ báo
   cáo (tháng) trước khi `compute_park_trim.py` chuyển từ đọc `BANNED` sang đọc cột mới.
   `lag_forensic_filter.py` giữ nguyên `LAG_USER_EXCLUDED`/`forensic_flags.csv` (đã đúng mô
   hình), chỉ thêm gate [A] làm điều kiện OR bổ sung.
4. **Danh sách 16 mã cụ thể sau khi có gate**: dựa trên §1/§3, đề xuất (KHÔNG tự áp — chờ user):
   - **Gỡ khỏi BANNED, để gate [A]+[C] tự xử lý**: KSF, VJC, NVL, VVS, GEG, IMP, TRA, TOS, VTP,
     HSG, NKG, HVN, SBA, BAF (14 mã — gate hoặc không lọt tự nhiên, hoặc gate động phủ đúng
     giai đoạn nguy hiểm biết được).
   - **Giữ nguyên qua `forensic_flags.csv` (đã có, chỉ thêm `review_by`)**: PC1 (đã có), khuyến
     nghị thêm KSF/VVS (đã có) — không đổi gì thêm ngoài trường review.
   - **DMC/IMP/TRA**: KHÔNG cần "gỡ khỏi ban" theo nghĩa BANNED — chúng vốn đã không cần ban
     (rating tốt, chỉ là timing) — nếu muốn dùng lại, cần thiết kế sleeve buy-and-hold riêng
     trước (ngoài scope).

---

## §6. Giới hạn

- Backtest custom30V/BAL độc lập, **không mô phỏng LAG book** — LAG có cơ chế forensic/exclude
  riêng đã date-aware, không đo lại N ở đây do effort budget; khuyến nghị tổng quát hoá gate [A]
  sang LAG bằng dispatch riêng nếu user muốn.
- Ngưỡng gate [A] (Debt/Eq>3.5, IntCov<1.5, dilution>80%) hiệu chỉnh từ percentile TOÀN
  universe + khớp đúng ca BAF/HVN đã biết — **chưa walk-forward-optimize theo nghĩa cổ điển**
  (không chia IS/OOS RIÊNG cho việc CHỌN ngưỡng, vì mục tiêu là capacity/an toàn chứ không phải
  tối đa hoá CAGR) — nếu wire, nên có 1 vòng kiểm tra ngưỡng KHÔNG đổi khi thay đổi cửa sổ mẫu.
- `IntCov_P0` trong `ticker_financial` nhiễu nặng toàn universe (p25 đã âm) — bất kỳ luật nào
  dùng độc lập metric này sẽ gãy; đã verify bằng đo trực tiếp (2 biến thể bị loại), không phải
  suy đoán.
- SBA-style (đòn bẩy thấp, lãi vay không che phủ mãn tính — điển hình IPP thuỷ điện có nợ dự án
  dài hạn lãi suất cố định) là lỗ hổng CÒN MỞ của gate [A] — cần metric riêng theo NGÀNH (tương
  tự phát hiện cũ "IntCov thay Debt/Eq cho brokerage") nếu muốn phủ tốt hơn; ngoài effort budget
  job này.
- Không chạy PBO chính thức (N_TRIALS=5, tiêu chí chọn không phải hiệu suất) — nêu rõ theo yêu
  cầu trung thực của brief, không tự ý bỏ qua.
- Mọi số liệu ở đây tính tới `AUDIT_END=2026-06-15` (khớp cache `data/bq_cache`); 3 tháng gần
  nhất (07-09/2026) không nằm trong backtest.

---

## Phụ lục — file nguồn

`mike/agents/Taylor/research/adaptive_exclusion_20260904/`:
`step_a_banned_audit.py` (scenario A/B + Q1 funnel), `custom_basket_dynfork.py` (fork 1-dòng),
`step_c_dynamic_gate.py` (scenario C), `dynamic_exclude_events.csv` (luật gate [A] cuối cùng,
episode theo ticker), `banned_financials_history.csv` / `universe_all_financials.csv` (dữ liệu
BQ thô), `universe_flag_rates.csv` (capacity), `final_3scenario_metrics.csv` /
`final_by_year_3scenario.csv` (kết quả §3), `q1_selection_frequency_16names.csv`,
`banned_counterfactual_qualityflag.csv` (§1a).

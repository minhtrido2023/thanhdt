# Re-pin R3 baseline sau restate DT5G 2026-07-29 (Việc 1)

**Job:** `Taylor_20260729_155142` · **Ngày chạy:** 2026-07-29/30 · **Tác giả:** Taylor
**Bối cảnh:** `mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md` — backfill
`VNINDEX_PE` 2006+ lan qua expanding-window ⇒ `vnindex_5state_dt5g_live` bị viết lại lịch sử.

---

## 1. Thiết kế đo — 3 chân, tách được nguyên nhân

Baseline R3 cũ (27,16%) pin ngày 2026-07-22. Vintage cache 07-22 **đã bị ghi đè, không còn tồn
tại** ⇒ không thể chạy lại. Vì vậy không so trực tiếp "cũ vs mới" được — phải dựng chân điều
khiển mới và tách nguyên nhân bằng vintage có thật.

| Chân | Cache | State DT5G | Giá / universe | Trả lời câu hỏi |
|---|---|---|---|---|
| **A** (control) | `bq_cache_asof20260728` | **trước** restate | 07-28 | mốc trước sự cố |
| **C** (isolation) | `bq_cache_legC_stateonly` | **sau** restate | 07-28 (y hệt A) | **restate thuần** |
| **B** (baseline mới) | `bq_cache` (07-29 full re-sync) | sau restate | 07-29 | baseline thay thế |

Chân C = bản sao hardlink của cache A, **chỉ tráo đúng 1 file**
`vnindex_5state_dt5g_live.parquet` sang bản post-restate (md5 xác nhận: A `823ae0ef7495…`,
C = live `e7290b86d8d0…`). `pt_v23_audit_2014.py` chỉ đọc **một** nguồn state duy nhất
(`STATE_TABLE`, dòng 53 + 680) — đã grep xác nhận không có bảng state thứ hai ⇒ A→C là
so sánh sạch, mọi thứ khác giữ nguyên bit-for-bit.

**Lệnh:** đúng lệnh pin R3 nguyên văn (`data/g7_restate_repin/leg.sh`), `BQ_CACHE_THREADS=1`,
`NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo
PARK_STATES="3:0.7" AUDIT_END=2026-06-19`, `$DNA_PYEXE` (pandas 3, không phải `python3`) —
theo `coding_guidelines` §8. `EXP_TAG` riêng cho từng chân ⇒ không đè CSV canonical.

## 2. Restate đã đổi gì trên chính chuỗi DT5G

| | trước (07-28) | sau (07-29) |
|---|---|---|
| số phiên | 3.134 | 3.136 |
| **transitions** | **51** | **51** |
| CRISIS(1) | 510 | **489** |
| BEAR(2) | 220 | **241** |
| NEUTRAL(3) | 1.939 | 1.924 |
| BULL(4) | 406 | **422** |
| EX-BULL(5) | 59 | 60 |

**101/3.134 phiên (3,22%) đổi nhãn**, lệch tối đa **3 tier**. Tập trung: 2018 (48 phiên),
2023 (34), 2020 (16), 2019 (1), 2022 (2). Số transitions **không đổi** (51) ⇒ tính chất
"gate chậm, ít whipsaw" của DT5G còn nguyên; cái đổi là **nhãn tier của từng ngày**.

## 3. Kết quả

| Chân | CAGR | Sharpe | MaxDD | Calmar | self-check |
|---|---|---|---|---|---|
| Pin cũ 07-22 (không tái lập được) | 27,16% | 1,81 | −18,1% | 1,50 | — |
| **A** — trước restate, vintage 07-28 | 27,63% | 1,84 | −18,1% | 1,53 | 0 VND ✓ |
| **C** — restate thuần | 27,99% | 1,86 | −17,4% | 1,60 | 0 VND ✓ |
| **⭐ B — baseline mới 07-29 (PIN CHÍNH THỨC)** | **27,60%** | **1,84** | **−17,5%** | **1,58** | 0 VND ✓ |

Chân C đã recompute độc lập từ CSV (`extract_peryear.py`): FULL **27,99%**, IS 23,48%,
OOS 32,27% — khớp bản in. Chân B recompute độc lập: FULL **27,60%**, IS 23,45%, OOS 31,51% —
**khớp chính xác** bản in. Final NAV B = 1.041,95B; coverage gate `[universe_pit] coverage OK:
3107 phiên >= ticker 3107 phiên` qua; cache `verified:true` **14/14 bảng**, `verified_at
2026-07-29T19:27:45Z`.

### Phân rã

| bước | ΔCAGR | nguyên nhân |
|---|---|---|
| 27,16 → 27,63 | **+0,47pp** | trôi dữ liệu thường 07-22→07-28 (6 ngày, **chưa** có restate) |
| 27,63 → 27,99 | **+0,36pp** | **restate DT5G thuần** |
| 27,99 → **27,60** | **−0,39pp** | trôi 07-28→07-29 **+ `ticker_prune` TRUNCATE+rebuild (−58 mã)** — hai nguồn này **không tách được** trong chân B |

| **27,16 → 27,60 (tổng)** | **+0,44pp** | pin cũ 07-22 → pin mới 07-29 |

**Đọc phân rã cho đúng:** tổng +0,44pp là **tổng của ba hiệu ứng lớn hơn nó và ngược dấu nhau**
(+0,47 / +0,36 / −0,39). Nếu chỉ chạy một chân "cũ vs mới" thì sẽ kết luận "gần như không đổi"
— sai. Ba nguyên nhân độc lập (trôi corp-action, restate DT5G, co rổ `ticker_prune`) đều ở mức
0,3–0,5pp và tình cờ bù nhau trong kỳ này; không có gì bảo đảm lần sau cũng bù.

⚠️ **Chỉ chân A→C (+0,36pp) là cô lập SẠCH một nguyên nhân.** Chân C→B (−0,39pp) **gộp hai cú
sốc** (trôi dữ liệu 1 ngày + `ticker_prune` mất 58 mã) và job này **không tách được**. Khi trích
dẫn, KHÔNG được viết "−0,39pp = trôi dữ liệu" — đó là overclaim. (Điểm này do quant-skeptic nêu
làm *killer objection*; ghi rõ ở đây thay vì để người đọc sau tự suy.) Muốn tách sạch: chờ
`ticker_prune` ổn định rồi chạy một chân giữ `ticker_prune` cố định, chỉ đẩy cửa sổ ngày.

### Ba điểm cần nhớ

**(a) Restate làm backtest ĐẸP LÊN, không xấu đi** — +0,36pp CAGR, MaxDD cải thiện 0,7pp,
Calmar +0,07. Đây là hướng nguy hiểm: một con số pin **tự tốt lên trong im lặng** mà không ai
đổi dòng code nào. Nếu không có chân A/C thì delta này rất dễ bị đọc nhầm thành alpha của một
thay đổi mô hình nào đó chạy cùng kỳ.

**(b) Ảnh hưởng KHÔNG nằm trong các năm bị restate** — per-year A→C:

| năm | A | C | Δ | có phiên bị restate? |
|---|---|---|---|---|
| 2014–2017 | (y hệt) | (y hệt) | 0,00 | không |
| 2018 | +24,90% | +26,78% | **+1,88** | có (48) |
| 2019 | +10,97% | +10,71% | −0,26 | có (1) |
| 2020 | +23,20% | +25,84% | **+2,64** | có (16) |
| **2021** | +107,17% | +110,63% | **+3,46** | **KHÔNG (0 phiên)** |
| 2022 | −2,12% | −2,19% | −0,07 | có (2) |
| 2023 | +23,58% | +23,32% | −0,26 | có (34) |
| 2024 | +23,81% | +23,42% | −0,39 | không |
| 2025 | +53,49% | +51,84% | **−1,65** | không |
| 2026 | +0,11% | +0,38% | +0,27 | không |

Năm biến động **mạnh nhất (2021, +3,46pp) lại là năm có 0 phiên bị restate**. Lý do: NAV là
mô phỏng **đơn-đường (single-path)** — state đổi năm 2020 làm đổi vị thế/NAV mang sang 2021 rồi
gộp lãi tiếp. Hệ quả thực tế: **không thể khoanh vùng "chỉ rerun mấy năm bị ảnh hưởng"** —
bất kỳ restate nào cũng làm bẩn toàn bộ đường NAV từ điểm chạm trở đi.

Per-year chân B (so C→B = trôi 07-28→07-29 + co rổ `ticker_prune`) — **cùng hiệu ứng
single-path lặp lại**:

| năm | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 38,45 | 19,86 | 14,25 | 32,75 | 26,78 | 10,71 | 25,84 | **110,63** | −2,19 | 23,32 | 23,42 | 51,84 | 0,38 |
| **B** | 38,45 | 19,85 | 14,26 | 32,52 | 26,82 | 10,72 | 24,38 | **102,29** | −2,83 | 23,37 | 24,20 | 54,12 | 0,17 |
| Δ | 0,00 | −0,01 | +0,01 | −0,23 | +0,04 | +0,01 | **−1,46** | **−8,34** | −0,64 | +0,05 | **+0,78** | **+2,28** | −0,21 |

Δ 2021 = **−8,34pp**, lớn gấp ~21 lần Δ headline (−0,39pp), trong khi 2021 không dính restate:
vốn mang sang từ 2020 rồi gộp lãi, không phải "2021 bị ảnh hưởng".

**(c) Δ headline (+0,36pp) nhỏ hơn nhiều so với Δ từng năm (tới ±3,5pp)** — các mức bù trừ nhau.
Đừng dùng "headline chỉ đổi 0,36pp" để kết luận restate là vô hại: phân bố lợi nhuận theo năm
đổi đáng kể, và mọi phân tích **theo năm / theo regime** đều bị ảnh hưởng nặng hơn headline.

## 4. Còn gì cần rerun ngoài R3?

Phân loại theo bản chất con số, không rerun tràn lan:

| loại | ví dụ | có cần rerun? |
|---|---|---|
| **Mức tuyệt đối đã pin** | R3 baseline; mọi CAGR/Sharpe/DD trích dẫn như "số chính thức" | **CÓ** — ĐÃ LÀM (chân B = pin mới 27,60%) |
| **Ablation cùng vintage** (A/B, verdict = dấu của delta) | c4/c5 LAG, depgate D0-D3, adaptive-persistence, Q-sleeve, momentum-deals… | **KHÔNG** — quy tắc registry #3: so sánh cùng vintage vẫn hợp lệ, verdict NO-GO/GO là delta-based, mà các verdict này đều thua/thắng với biên rộng |
| **Thống kê tính TRỰC TIẾP trên chuỗi DT5G** | P(NEUTRAL→BEAR/CRISIS trong N phiên) (registry dòng ~2902); phân bố ngày theo state; audit sự kiện DT5G | **CÓ** — đây là hàm trực tiếp của nhãn ngày, mà 101 ngày vừa đổi tier (CRISIS −21, BEAR +21, BULL +16) |
| **Đặc trưng cấu trúc của gate** | "49–51 transitions", "DT5G = insurance không phải return-enhancer" | **KHÔNG** — transitions không đổi (51), kết luận định tính còn nguyên |

**Ưu tiên rerun tiếp theo (đề xuất, chưa làm):** bộ base-rate P(NEUTRAL→BEAR/CRISIS) — nó được
trích vào `dna_report`/thảo luận sizing, và là hàm trực tiếp của phân bố state vừa đổi. Rẻ
(chỉ đọc 1 bảng, không phải backtest).

## 5. Cảnh báo hạ tầng phát sinh trong lúc chạy (ngoài phạm vi job, cần Winston/Mike)

`sync_bq_cache.py` **không có lock** và ghi `to_parquet` **trực tiếp** (không `tmp`+`os.replace`).
Lúc 23:45 ICT cron `sync_bq_cache_daily.sh --delta` khởi động **đè lên cùng thư mục
`data/bq_cache`** với lần full re-sync của job này. Đánh giá cụ thể lần này: vùng chồng lấn chỉ
là partition 2026 + các bảng nhỏ + `manifest.json`, full re-sync ghi manifest **sau cùng**, và
không consumer nào đọc cache trước preflight 08:45 ⇒ **rủi ro thực tế thấp, đã CHỦ Ý KHÔNG kill
cron production**. Nhưng đây là vi phạm `coding_guidelines` §5 (ghi phải atomic) và là bẫy thật
cho lần sau: hai lần sync chạy chồng có thể để lại cache **trộn vintage nhưng vẫn `verified=true`**.
Đề xuất: thêm `flock` + ghi `tmp`+`os.replace` cho `sync_bq_cache.py`.

## 6. AS-OF DATA VINTAGE

Áp dụng định dạng đề xuất ở Việc 2 (`research/asof_vintage_label_20260729.md`), sinh bằng
`python3 mike/agents/Taylor/bin/cache_vintage_stamp.py <cache_dir> --md`.

### AS-OF DATA VINTAGE — chân B (số pin CHÍNH THỨC mới)

- `run_date`: 2026-07-29T19:28Z → 19:35Z (backtest), resync cache 17:37Z→19:27Z
- `cache_dir`: `data/bq_cache` — full re-sync `ticker` 2026-07-29T17:37Z (các bảng còn lại
  full re-sync cùng ngày, 15:53Z→16:30Z)
- `manifest.verified`: **true** · `verified_at`: `2026-07-29T19:27:45Z` · **14/14 bảng OK**
- `snapshot`: `data/bq_cache_asof20260729_postrestate/` (ĐÓNG CỨNG, bản sao thật — **không**
  hardlink: `sync_bq_cache.py` ghi `to_parquet` đè inode nên hardlink sẽ bị hỏng lặng lẽ)
- `reproducible`: **CHỈ TỪ SNAPSHOT** — BQ time-travel đã tắt, `ticker`/`ticker_prune` bị
  TRUNCATE+rebuild mỗi ngày ⇒ chạy lại trên live BQ ngày khác **KHÔNG** tái lập được con số này.

| bảng | rows | max_time | md5 (16 ký tự đầu) |
|---|---|---|---|
| `vnindex_5state_dt5g_live` | 3.136 | 2026-07-29 | `371b79941d685954` |
| `vnindex_5state_tam_quan_v34b_clean` | 6.333 | 2026-07-29 | `2646553d23b441f4` |
| `ticker` | 3.493.441 | 2026-07-29 | `2de5ec9412f5e3dd` |
| `ticker_prune` | 755.751 | 2026-07-29 | `6849d5557218f475` |
| `universe_pit_q` | 3.494.415 | 2026-07-29 | `edc917d05fce0538` |
| `ticker_financial` | 66.906 | 2026-07-29 | `5d836b11948bbf62` |
| `fa_ratings_8l` | 52.966 | 2026-07-29 | `2ad86b94411e1359` |

**Log:** `data/g7_restate_repin/legB_new0729.log` (resync:
`data/g7_restate_repin/full_resync_ticker_0730.log`). **CSV:**
`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_g7_legB_new0729_univpit.csv`
(18.496 dòng). Canonical `..._wtnamecap.csv` **KHÔNG bị đụng** (`EXP_TAG` riêng, §8 guidelines).

**Chân A (control) — caveat công khai:** manifest của `bq_cache_asof20260728` được **override
thủ công** `verified=true`; verify gốc 07-28 có **`ticker_prune` FAIL count** (767.068 local vs
755.535 BQ) do BQ truncate+rebuild. Chân A/C **chỉ dùng cho attribution**, **không** phải ứng
viên pin. Vì A và C dùng **chung** file `ticker_prune` đó nên delta A→C vẫn sạch.

**Confound của chân B cần nêu rõ:** B dùng `ticker_prune` **mới** (755.751 dòng, sau
TRUNCATE+rebuild 07-29 làm mất 58 mã khỏi toàn bộ lịch sử, membership −17%). Trong cấu hình
MIXED-universe hiện tại `ticker_prune` vẫn cấp **CAPIT pool / breadth / maturity**. Do đó
**C→B KHÔNG phải chỉ là trôi corp-action** — nó gộp cả cú co rổ `ticker_prune`. Không tách
được hai nguồn này trong chân B.

---

## 7. ⭐ KẾT LUẬN — baseline R3 CHÍNH THỨC mới

| | CAGR | Sharpe | MaxDD | Calmar | Final NAV | vintage |
|---|---|---|---|---|---|---|
| Pin cũ (2026-07-22) — **SUPERSEDED** | 27,16% | 1,81 | −18,1% | 1,50 | 998,09B | cache 07-22 (**đã mất**) |
| **⭐ Pin mới (2026-07-29) = chân B** | **27,60%** | **1,84** | **−17,5%** | **1,58** | **1.041,95B** | cache 07-29 (snapshot đóng cứng) |
| Δ | **+0,44pp** | +0,03 | +0,6pp tốt hơn | +0,08 | +43,86B | |

**Lệnh pin KHÔNG đổi** (nguyên văn `data/g7_restate_repin/leg.sh`, `UNIVERSE_SRC` để mặc định
= `pit`). Đây là **re-pin do vintage dữ liệu**, KHÔNG phải thay đổi mô hình/tham số — không có
dòng code chiến lược nào đổi giữa hai lần pin.

**Cái gì KHÔNG đổi khi cập nhật pin:**
- Nhãn **MIXED-universe** giữ nguyên: `universe_pit` cấp *cổng quyết định*, `ticker_prune` vẫn
  cấp *CAPIT pool / maturity*. (Breadth-decoupling guard của DT5G đã cutover sang `universe_pit`
  ngày 07-29 — commit `8f95895`, ảnh hưởng 0 phiên lên state cuối.)
- **Lỗi fidelity `liq<=0` vẫn MỞ** ⇒ 27,60% vẫn là chân **fill-lạc-quan**; khoảng kỳ vọng
  trung thực giữ nguyên **[~27,6%; ~31,3%]** (cận dưới dịch theo pin mới), anchor DD **~−30%**
  (bootstrap 5th-pct), KHÔNG phải −17,5%.
- Kết luận định tính về DT5G (gate bảo hiểm, không phải return-enhancer; 51 transitions) không đổi.

**Bài học lớn nhất của job này** (đã nêu ở §3): một con số pin **tự đổi 0,44pp trong 7 ngày mà
không ai sửa dòng code nào** — và con số đó là *tổng của ba hiệu ứng ±0,4pp bù trừ nhau*. Đây là
lý do khối AS-OF DATA VINTAGE (Việc 2) phải là **bắt buộc** cho mọi số pin, và tại sao re-pin
nên có nhịp định kỳ chứ không chỉ chạy khi có sự cố.

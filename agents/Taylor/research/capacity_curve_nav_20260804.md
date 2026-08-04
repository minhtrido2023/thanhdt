# Đường cong CAPACITY của V2.4 R3 theo quy mô NAV

**Job** `Taylor_20260804_102015` · **Ngày** 2026-08-04 · **Tác giả** Taylor
**Trạng thái** nghiên cứu thuần — KHÔNG đề xuất gate, KHÔNG đụng production (`git diff` sạch trên
`pt_v23_audit_2014.py`, `simulate_holistic_nav.py`).

---

## 0. Kết luận 5 dòng (đọc trước khi dùng cho bất kỳ quyết định vốn nào)

1. **Câu hỏi "CAGR thật vs CAGR lý tưởng lệch bao nhiêu" có câu trả lời NGƯỢC DẤU với giả định của
   dispatch**: chân LÝ TƯỞNG (fill hoàn hảo, bỏ trần thanh khoản) cho CAGR **THẤP HƠN** chân thật ở
   **cả 8/8 mốc NAV**, lệch −2,09 đến −6,37pp. Trần thanh khoản trong engine đang hoạt động như một
   **bộ lọc chọn mã có lợi**, không phải một chi phí.
2. Cơ chế đã đo, không suy đoán: nhóm mã **chỉ giao dịch được khi bỏ trần** hút 11,0% → 33,1% tổng
   vốn quay vòng (theo NAV) nhưng chỉ lãi **+0,6…+2,6%/vòng** so với **+7,0…+7,7%/vòng** của nhóm
   chung — chênh **−4,8 đến −6,8pp mỗi vòng**, nhất quán ở cả 4 mốc NAV kiểm tra.
3. ⇒ **KHÔNG được đọc bảng CAGR-theo-NAV như đường cong capacity.** Đặc biệt: 28,86% @50B >
   25,90% @1B **KHÔNG có nghĩa "bơm vốn lên 50B thì lãi hơn"** — chênh đó là hiện vật của bộ lọc,
   và LOO theo năm cho thấy nó là **reshuffle-luck** (chỉ 5/13 năm cùng dấu).
4. **Tín hiệu capacity SẠCH duy nhất** nằm ở chân lý tưởng (chỉ còn slippage-thoát theo %ADV +
   trần rổ parking): **−0,45pp @5B, −0,63pp @10B, −0,86pp @20B, −1,02pp @50B, −0,98pp @100B**, và
   **13/13 năm cùng dấu** — nhỏ, thật, bão hoà quanh −1pp. Mốc vượt 1pp ≈ **50B**.
5. **Trần capacity thực dụng KHÔNG đọc bằng CAGR mà bằng KHẢ NĂNG THI HÀNH**: %vị thế bỏ dở tăng
   đơn điệu **17,5% → 58,2%** (1B → 100B). Sổ **LAG đã 25,2% bỏ dở ngay ở 1B** — tức tại NAV LIVE
   hôm nay. Đây mới là ràng buộc đang có hiệu lực.

---

## 1. Cơ chế fill-capacity trong engine (đọc code, không giả định)

Nguồn: `simulate_holistic_nav.py` (bản production, `simulate()`), `pt_v23_audit_2014.py`.

| Thành phần | Vị trí | Nội dung |
|---|---|---|
| Trần fill/phiên | `simulate_holistic_nav.py:1202-1210` | `daily_max = liquidity_lookup[(tk,today)] × liquidity_volume_pct` (= **20% ADV/phiên**) |
| Số phiên được phép khớp | `max_fill_days=5` | lệnh chưa xong sau 5 phiên → đóng sổ |
| Ngưỡng chấp nhận | `min_fill_pct=0.30` | `fill_pct ≥ 0.30` → thành vị thế; **< 0.30 → ABANDONED_REFUND** |
| Hoàn tiền | `:1281-1306` | bán lại phần đã khớp theo giá hôm đó, ghi `reason="ABANDONED_REFUND"`, cùng `holding_id` |

**ABANDONED_REFUND áp cho SỔ NÀO — đã kiểm, không giả định:** cả **BA** sổ.
- `LIQ_FULL` (`pt_v23_audit_2014.py:990`, `liquidity_lookup=liq_map`) → truyền vào sim **BAL**
  (`:1952`, `:1983`).
- `LIQ_LAG` (`:1333`, `liquidity_lookup=liq_lag`, cơ sở giá `PxAdv=COALESCE(Price,Close)` theo
  `LAG_ADV_BASIS=price` mặc định production) → truyền vào sim **LAG** (`:2011`, `:2037`).
- **CAPIT không phải sim riêng**: `add_capit_arm()` gộp nhánh CAPIT vào chính 2 sim trên
  (`CAPITB_*` nằm trong sim BAL ⇒ chịu `LIQ_FULL`; `CAPITL_*` trong sim LAG ⇒ chịu `LIQ_LAG`).
  Vì vậy tách được CAPIT ra khỏi BAL/LAG bằng `play_type`, và **cả 3 sổ đều mô phỏng capacity**.

**`NAV_TOTAL_B` là gì**: `pt_v23_audit_2014.py:55-57` — `TOTAL_NAV = NAV_TOTAL_B × 1e9`, chia đôi
cứng `BAL_NAV = LAG_NAV = TOTAL_NAV/2`. Có `_NAV_TAG` riêng trong tên CSV ⇒ các mốc không đè nhau.

⚠️ **Giới hạn đã biết của phép đo %bỏ dở**: lệnh khớp được **0 cổ** (`filled_shares == 0`) KHÔNG
sinh dòng log nào (chỉ `skipped_for_liquidity += 1`). Vậy mọi con số %bỏ dở dưới đây là **CẬN DƯỚI**
của tỷ lệ thật.

---

## 2. Thiết kế thí nghiệm

- **Chân THẬT (`real`)** = lệnh pin R3 nguyên văn, mặc định production.
- **Chân LÝ TƯỞNG (`ideal`)** = y hệt, **chỉ đổi 1 thứ**: `liquidity_volume_pct = None` cho cả
  `LIQ_FULL` và `LIQ_LAG` ⇒ mỗi lệnh khớp trọn size ngay T+1, **không bao giờ** ABANDONED_REFUND
  vì thanh khoản. **Cố ý GIỮ NGUYÊN** `exit_slippage_tiered` và trần ADV của rổ parking, để hiệu
  số cô lập **đúng một** cơ chế: trần fill ở tầng vào lệnh.
- **Không sửa production**: knob `LIQ_UNCAP` chỉ tồn tại trong bản sao nghiên cứu
  `mike/agents/Taylor/exp_capacity_20260804/pt_v23_capacity.py` (diff với bản production = đúng 3
  hunk, in ra ở §7). Engine `simulate_holistic_nav.py` **không sửa 1 dòng**.
- **Cổng chống no-op im lặng** (bài học `run_jit.sh` 2026-08-03): mỗi lần chạy tự in
  `[CAPACITY] LIQ_UNCAP=… | BAL cap=… | LAG cap=… | NAV_TOTAL_B=…` + `assert`. **16/16 chân đã
  xác nhận đúng cấu hình** — không chân nào là no-op.
- **Môi trường ghim**: snapshot `data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`,
  `$DNA_PYEXE` (pandas 3), `AUDIT_END=2026-06-19`, `ETF_LIQ=custompitg BASKET_WT=namecap
  BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"`, `universe_pit`, `LAG_ADV_BASIS=price`.
- **`EXP_TAG` set trên MỌI chân** ⇒ không chân nào ghi đè CSV canonical (coding_guidelines §8).
- **Chân control tái lập chính xác**: `cap1b_real` = **17,64B / 25,90% / 1,67 / −17,7% / 1,46**,
  trùng tuyệt đối `n1_ctrl` của job `Taylor_20260804_085248`; `cap50b_real` = **1.178,01B / 28,86%
  / 1,90 / −17,8% / 1,62**, trùng tuyệt đối pin R3 chính thức. ⇒ bản sao trung thực.
- **Self-check 0 VND: 16/16 chân, cả 2 sổ** (cash-flow identity + final NAV identity đều 0 VND).
- **N (số sự kiện độc lập)**: N = **16 lần chạy** (8 mốc NAV × 2 chân), báo cáo **toàn bộ**, không
  chọn lọc. N của phép đo cơ chế = 4 cặp NAV × ~900–930 vòng round-trip mỗi cặp.

---

## 3. BẢNG 1 — Đường cong chính

| NAV | CAGR **thật** | CAGR **lý tưởng** | lệch (lt−thật) | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20+ | **%bỏ dở TỔNG** | sc 0 VND |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| 1B | 25,90% | 23,81% | **−2,09** | 1,67 | −17,7% | 1,46 | 24,19% | 27,38% | 17,5% | OK |
| 5B | 29,50% | 23,36% | **−6,14** | 1,86 | −17,9% | 1,65 | 28,37% | 30,42% | 28,6% | OK |
| 10B | 28,57% | 23,18% | **−5,39** | 1,81 | −17,3% | 1,65 | 26,47% | 30,42% | 33,0% | OK |
| 20B | 28,14% | 22,95% | **−5,19** | 1,83 | −17,4% | 1,61 | 25,80% | 30,25% | 40,7% | OK |
| 30B | 29,26% | 22,89% | **−6,37** | 1,91 | −18,0% | 1,63 | 25,64% | 32,64% | 44,2% | OK |
| **50B** | **28,86%** | 22,79% | **−6,07** | 1,90 | −17,8% | 1,62 | 27,09% | 30,48% | 50,8% | OK |
| 75B | 28,05% | 22,86% | **−5,19** | 1,87 | −18,3% | 1,53 | 26,23% | 29,73% | 54,6% | OK |
| 100B | 27,17% | 22,83% | **−4,34** | 1,83 | −18,9% | 1,43 | 25,02% | 29,16% | 58,2% | OK |

**Đọc bảng này thế nào:** cột "lệch" âm ở **mọi** mốc ⇒ **không có "chi phí capacity" nào đo được
theo hướng dispatch giả định**. Câu hỏi "điểm NAV mà độ lệch vượt 1pp" **không áp dụng được** —
độ lệch đã vượt 2pp ngay từ 1B, nhưng theo chiều ngược lại.

---

## 4. BẢNG 2 — Khả năng thi hành, tách theo sổ (chân THẬT)

| NAV | BAL mở | **BAL %bỏ** | LAG mở | **LAG %bỏ** | CAPIT mở | **CAPIT %bỏ** | vốn kẹt B (BAL/LAG/CAPIT) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1B | 254 | 0,4% | 795 | **25,2%** | 97 | 0,0% | 0,3 / 5,0 / 0,0 |
| 5B | 278 | 6,1% | 1015 | 37,3% | 97 | 1,0% | 13,2 / 51,3 / 1,4 |
| 10B | 307 | **14,0%** | 1112 | 41,0% | 98 | 2,0% | 59,3 / 95,9 / 2,6 |
| 20B | 354 | 25,4% | 1230 | 48,0% | 98 | 4,1% | 190,4 / 230,7 / 9,4 |
| 30B | 393 | 32,1% | 1331 | 50,6% | 98 | 6,1% | 325,4 / 354,3 / 15,0 |
| 50B | 452 | 40,7% | 1498 | 56,6% | 106 | **11,3%** | 616,8 / 773,7 / 36,1 |
| 75B | 482 | 44,6% | 1636 | 59,8% | 101 | 16,8% | 803,5 / 1278,7 / 82,7 |
| 100B | 546 | 53,3% | 1752 | 62,0% | 110 | 22,7% | 1407,8 / 1764,7 / 113,0 |

Đơn điệu tăng ở **cả 3 sổ**, không có ngoại lệ. Ngưỡng vượt 10% bỏ dở:
- **LAG**: đã vượt từ **trước 1B** (25,2% tại 1B) — sổ này capacity-bound ở MỌI quy mô đang xét.
- **BAL**: vượt 10% giữa **5B và 10B** (6,1% → 14,0%).
- **CAPIT**: vượt 10% giữa **30B và 50B** (6,1% → 11,3%).
- (`LAG 56,6% @50B` khớp con số 56,6% của job `Taylor_20260804_085248` ⇒ hai job đối chiếu được.)

---

## 5. Cơ chế: vì sao "lý tưởng" lại TỆ hơn (đo, không lập luận)

Với mỗi cặp cùng NAV, chia mã theo: `ONLY_IDEAL` = mã **chỉ** chân lý tưởng mở xong được vị thế;
`BOTH` = mã cả 2 chân đều hoàn tất. Rồi đo lợi suất vòng **trong chính chân lý tưởng** (nên không
lẫn hiệu ứng giá giữa 2 chân).

| NAV | ONLY_IDEAL: %vốn quay vòng | ONLY_IDEAL ret/vòng | BOTH ret/vòng | chênh | P&L nhóm ONLY_IDEAL |
|---:|---:|---:|---:|---:|---:|
| 1B | 11,0% | +1,55% | +7,02% | **−5,48pp** | −0,2B |
| 10B | 17,9% | +0,63% | +7,41% | **−6,78pp** | −1,5B |
| 50B | 27,9% | +2,60% | +7,42% | **−4,82pp** | +5,0B |
| 100B | 33,1% | +2,24% | +7,65% | **−5,41pp** | −20,6B |

**Dose-response rõ**: NAV càng lớn → trần càng siết → nhóm ONLY_IDEAL (mã mỏng thanh khoản, chủ
yếu sổ LAG: 175/206 vòng @50B, 187/239 @100B) càng bị loại nhiều → CAGR chân thật càng được "nâng"
một cách nhân tạo. Đây **cùng một hiện vật** đã đo độc lập ngày 2026-07-21 (nhóm microcap
`liq<=0`: −1,11%/vòng vs +4,82%/vòng phần còn lại).

⚠️ **Bộ lọc này rẻ một cách phi thực tế**: ABANDONED_REFUND bán lại phần đã khớp **ngay trong ngày,
theo giá hôm đó, chỉ mất phí**. Ngoài đời, một lệnh mua dở không tự hoàn tiền — bạn ôm phần đã mua,
hoặc phải đuổi giá. Nên "lợi ích" của bộ lọc trong backtest **không chuyển thành tiền thật được**.

---

## 6. Kiểm định robustness — cái nào là thật, cái nào là reshuffle-luck

**Per-year LOO, Δpp so với mốc 1B, khi tăng NAV 1B → 100B:**

| Chân | Số năm cùng dấu (giảm) | Kết luận |
|---|---:|---|
| **LÝ TƯỞNG** | **13/13** | hiệu ứng THẬT, ổn định, dose-responsive |
| **THẬT** | **5/13** | **reshuffle-luck**, không phải quan hệ bền |

Chân THẬT: mức "50B > 1B" (+2,96pp) là **hiệu số ròng của những dao động lớn ngược chiều nhau** —
2014 **+11,45pp**, 2021 **+25,93pp**, 2015 +8,65pp, 2025 +8,65pp, bù trừ bởi 2024 **−10,39pp**,
2019 −5,40pp, 2022 −6,71pp. Đúng chữ ký reshuffle-luck mà `kb/KNOWLEDGE.md` §8 mô tả.

Chân LÝ TƯỞNG: âm ở **mọi năm** (2014 −1,49 … 2026 −0,26 khi 1B→100B), biên độ nhỏ và tăng dần
theo NAV. Đây là **chi phí capacity thật**, kênh còn lại sau khi bỏ trần vào lệnh:
`exit_slippage_tiered` (vị thế vs %ADV: >5% +0,1%, >10% +0,3%, >20% +0,5% khi thoát) + trần ADV rổ
parking + ngưỡng lệnh tối thiểu. **Không bao gồm** chi phí capacity ở tầng VÀO lệnh — tầng đó
chính là cái bị vướng vào chọn mã nên không tách được.

**Chi phí capacity SẠCH (chân lý tưởng, CAGR toàn kỳ, so với 1B):**
`−0,45pp @5B · −0,63pp @10B · −0,86pp @20B · −0,92pp @30B · −1,02pp @50B · −0,95pp @75B ·
−0,98pp @100B` → **vượt ngưỡng 1pp ở ≈50B, rồi bão hoà** (không tiếp tục xấu đi tới 100B).

*Caveat:* trong chân lý tưởng có một đảo chỗ 2020↔2021 ở mốc 75/100B (2020 từ −2,92 @50B lên −0,47
@75B, 2021 từ −0,40 xuống −2,08) — tổng vẫn ~−1pp, nhưng phân bổ theo năm ở đuôi 75-100B kém ổn
định hơn khoảng 1-50B.

**Về DSR/PBO**: **không áp dụng và cố ý không tính** — DSR/PBO đo rủi ro overfit khi **CHỌN** một
cấu hình tốt nhất trong một họ để wire. Ở đây **không có lựa chọn nào được đưa ra**, không có gì
được đề xuất wire, và toàn bộ 16/16 chân đều báo cáo. Thay vào đó, kiểm định phù hợp với câu hỏi
này là **per-year LOO** (bảng trên) — và nó đã bác bỏ chân THẬT, giữ chân LÝ TƯỞNG.
⚠️ Hệ quả: **đừng đọc "5B = 29,50% là mốc NAV tối ưu"** — đỉnh đó nằm gọn trong biên độ hiện vật.

---

## 7. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
# 1 chân: $1 = NAV_TOTAL_B, $2 = LIQ_UNCAP (0=thật, 1=lý tưởng)
mike/agents/Taylor/exp_capacity_20260804/run_cap.sh 50 0
# toàn bộ bảng:
"$DNA_PYEXE" mike/agents/Taylor/exp_capacity_20260804/collect.py
"$DNA_PYEXE" mike/agents/Taylor/exp_capacity_20260804/decomp.py 1 10 50 100
```

Diff bản sao nghiên cứu vs production = **đúng 3 hunk** (khai báo `LIQ_UNCAP` + 2 dòng áp vào
`LIQ_FULL`/`LIQ_LAG` + cổng in/assert):
`diff pt_v23_audit_2014.py mike/agents/Taylor/exp_capacity_20260804/pt_v23_capacity.py`

Artefact: `capacity_curve_raw.csv`, `cap{NAV}b_{real|ideal}.log` (16 file),
`data/v23_golive_audit_..._exp_cap{NAV}b_{real|ideal}_univpit_nav{NAV}B.csv` (16 file TX).

---

## 8. Giới hạn — phải đọc cùng mọi con số ở trên

1. **Toàn bộ đường cong treo trên MỘT tham số chưa được neo**: trần **20% ADV/phiên**. Fill THẬT
   của DNSE mới xác nhận tới **~3,86% ADV/phiên** (`kb/projects/lag-adv-filter-tracking.md`), và
   90-96% số phiên-fill trong mô phỏng đang nằm **Ở TRẦN**. Nếu trần thật thấp hơn 5×, %bỏ dở ở
   mọi mốc NAV sẽ **cao hơn đáng kể** so với Bảng 2 — Bảng 2 là **cận dưới của cận dưới**.
2. **Không tách được chi phí capacity ở tầng VÀO lệnh** khỏi hiệu ứng chọn mã. Đó không phải thiếu
   sót của lần đo này mà là **thuộc tính cấu trúc của engine**: bỏ trần fill đồng thời đổi cả tập
   mã giao dịch được. Muốn tách phải lọc thanh khoản ở **tầng TÍN HIỆU** (trước khi sinh lệnh) —
   một thí nghiệm khác, chưa chạy.
3. `NAV_TOTAL_B` chia đôi cứng BAL/LAG 50/50; đường cong này **không** trả lời "nếu đổi tỷ lệ 2 sổ
   theo quy mô thì sao".
4. Vintage dữ liệu: snapshot `asof20260729_postrestate`, `AUDIT_END=2026-06-19`. So sánh với số
   pin khác vintage phải cẩn trọng (chân control đã trùng tuyệt đối nên A/B nội bộ hợp lệ).
5. `%bỏ dở` là cận dưới (lệnh khớp 0 cổ không để lại log) — xem §1.

---

## 9. Trả lời trực tiếp câu hỏi "khi nào thì đừng bơm thêm vốn nữa"

| Trục | Ngưỡng đo được | Độ tin cậy |
|---|---|---|
| **Lợi nhuận** (chi phí capacity sạch) | ~1pp mất đi ở **≈50B**, bão hoà sau đó | cao (13/13 năm) |
| **Khả năng thi hành sổ LAG** | **đã vượt** — 25,2% lệnh bỏ dở ngay ở **1B** | cao (đơn điệu, 2 job khớp nhau) |
| **Khả năng thi hành sổ BAL** | vượt 10% giữa **5B–10B**; 25% ở **20B** | cao (đơn điệu) |
| **Khả năng thi hành CAPIT** | vượt 10% giữa **30B–50B** | cao (đơn điệu) |
| "CAGR tăng theo NAV" | **KHÔNG dùng** — reshuffle-luck (5/13 năm) | đã bác bỏ |

**Khuyến nghị diễn giải cho user (không phải khuyến nghị vốn):** ràng buộc đang cắn **không phải**
lợi nhuận mà là **thi hành**, và nó cắn **ngay ở quy mô hiện tại** ở sổ LAG. Chi phí lợi nhuận đo
được của việc bơm vốn tới 50B là **~1pp CAGR** — nhỏ. Nhưng con số đó **chỉ đúng nếu chấp nhận
giả định fill 20% ADV/phiên**, và mọi thứ ở tầng vào lệnh vẫn chưa tách được. **Không có con số
nào trong báo cáo này đủ tư cách làm căn cứ duy nhất cho một quyết định bơm vốn thật.**

---

## 10. BỔ SUNG attempt-2 (2026-08-04, sau quant-skeptic) — ĐỘ NHẠY THEO TRẦN FILL

**Vì sao có mục này.** quant-skeptic **CONFIRMED (high)** toàn bộ §0–§9 nhưng nêu một
`killer_objection` + `recommended_reruns`: mọi con số ở trên treo trên trần **20% ADV/phiên** —
gấp ~5× fill THẬT đã xác nhận của DNSE (~3,86%/phiên) — và **chưa có chân nào chạy ở trần chặt hơn**
để kiểm kết luận ĐỊNH TÍNH có sống sót không. Mục này chạy đúng phép thử đó: chân THẬT ở
**`LIQ_PCT=0.04`** (nằm trong khoảng 0,04–0,06 quant-skeptic đề xuất, neo sát fill thật) tại
**cả 8 mốc NAV**. Chân LÝ TƯỞNG (`cap=None`) **không** chịu ảnh hưởng của `LIQ_PCT` nên dùng lại
8 chân ideal đã có. **Tổng cộng 24 chân (8 NAV × 3 biến thể), self-check 0 VND 24/24.**

> ⚠️ **Lỗi đã bắt được trong chính hạ tầng này** (ghi lại vì đúng loại bẫy `run_jit.sh` 2026-08-03):
> knob `LIQ_PCT` được **khai báo** ở đầu file và **có gắn hậu tố tên file** (`_liqpct0p04`), nhưng
> **KHÔNG được áp** vào `LIQ_FULL`/`LIQ_LAG` (2 dict vẫn hardcode `0.20`). Chạy nguyên trạng sẽ cho
> một chân **mang tên khác nhưng trùng byte** với chân 20% — **no-op im lặng**. Đã wire + thêm
> `assert` thứ 2 (`LIQ_PCT không áp được vào LIQ_FULL/LIQ_LAG`); cổng `[CAPACITY]` nay in
> `LIQ_PCT=0.04 | BAL cap=0.04 | LAG cap=0.04` xác nhận trần thật sự đổi (24/24 chân khớp).
> **Regression:** chạy lại `cap50b_real` ở mặc định `0.20` cho kết quả **byte-identical** với log
> gốc (trừ dòng đồng hồ "cache verified 135h→136h") ⇒ sửa này là **no-op tuyệt đối ở mặc định**,
> 16 chân gốc **không bị ảnh hưởng**.

### BẢNG S1 — chân THẬT: trần 20% (chưa neo) vs 4% (neo theo fill thật)

| NAV | CAGR @20% | CAGR @4% | Δpp | Calmar @20% | Calmar @4% | MaxDD @20% | MaxDD @4% |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1B | 25,90% | 29,22% | **+3,32** | 1,46 | 1,63 | −17,7% | −17,9% |
| 5B | 29,50% | 29,08% | −0,42 | 1,65 | 1,61 | −17,9% | −18,1% |
| **10B** | 28,57% | **29,70%** ← đỉnh | +1,13 | 1,65 | **1,69** | −17,3% | −17,6% |
| 20B | 28,14% | 28,04% | −0,10 | 1,61 | 1,50 | −17,4% | −18,7% |
| 30B | 29,26% | 26,87% | −2,39 | 1,63 | 1,37 | −18,0% | −19,6% |
| 50B | 28,86% | 24,50% | **−4,36** | 1,62 | **1,11** | −17,8% | **−22,1%** |
| 75B | 28,05% | 23,55% | −4,50 | 1,53 | 1,13 | −18,3% | −20,8% |
| 100B | 27,17% | **21,92%** | **−5,25** | 1,43 | **1,02** | −18,9% | −21,6% |

**Ở trần neo theo fill thật, đường cong capacity CÓ HÌNH DẠNG KINH ĐIỂN mà trần 20% che mất**:
tăng nhẹ tới **đỉnh 10B (29,70%)** rồi **giảm ĐƠN ĐIỆU** 20B→100B (28,04 → 26,87 → 24,50 → 23,55 →
21,92). Ở trần 20% thì đường này gần như **phẳng** (25,90…29,50, không có đỉnh rõ) — tức **chính
tham số chưa neo đã xoá mất tín hiệu capacity.**

### BẢNG S2 — kết luận ĐỊNH TÍNH có sống sót không? (độ lệch = lý tưởng − thật)

| NAV | ideal | thật @20% | lệch @20% | thật @4% | lệch @4% | **giữ dấu?** |
|---:|---:|---:|---:|---:|---:|:--:|
| 1B | 23,81% | 25,90% | −2,09 | 29,22% | −5,41 | **CÓ** |
| 5B | 23,36% | 29,50% | −6,14 | 29,08% | −5,72 | **CÓ** |
| 10B | 23,18% | 28,57% | −5,39 | 29,70% | −6,52 | **CÓ** |
| 20B | 22,95% | 28,14% | −5,19 | 28,04% | −5,09 | **CÓ** |
| 30B | 22,89% | 29,26% | −6,37 | 26,87% | −3,98 | **CÓ** |
| 50B | 22,79% | 28,86% | −6,07 | 24,50% | −1,71 | **CÓ** |
| 75B | 22,86% | 28,05% | −5,19 | 23,55% | −0,69 | **CÓ** |
| **100B** | 22,83% | 27,17% | −4,34 | **21,92%** | **+0,91** | **KHÔNG** |

⇒ **Kết luận trung tâm SỐNG SÓT ở 7/8 mốc**: chân LÝ TƯỞNG vẫn thấp hơn chân thật ở cả hai trần.
Cơ chế "trần thanh khoản = bộ lọc chọn mã có lợi" **không phải hiện vật của tham số 20%**.
**Nhưng ở 100B nó ĐỔI DẤU** (lệch **+0,91**): đây là mốc đầu tiên mà **ràng buộc capacity thật
thắng hẳn lợi ích bộ lọc** — tức tồn tại một điểm mà "không fill nổi" tốn nhiều hơn cái nó lọc bỏ.

### BẢNG S3 — %vị thế bỏ dở @4% (trong ngoặc: @20%)

| NAV | BAL | LAG | CAPIT | TỔNG |
|---:|---:|---:|---:|---:|
| 1B | 4,8% (0,4%) | **35,6%** (25,2%) | 1,1% (0,0%) | **27,0%** (17,5%) |
| 5B | 27,6% (6,1%) | 47,6% (37,3%) | 5,7% (1,0%) | 40,8% (28,6%) |
| 10B | 40,8% (14,0%) | 55,5% (41,0%) | 13,6% (2,0%) | 50,1% (33,0%) |
| 20B | 53,6% (25,4%) | 60,6% (48,0%) | 24,8% (4,1%) | 57,4% (40,7%) |
| 30B | 58,9% (32,1%) | 64,4% (50,6%) | 33,6% (6,1%) | 61,7% (44,2%) |
| 50B | 69,4% (40,7%) | 67,1% (56,6%) | 40,3% (11,3%) | 66,6% (50,8%) |
| 75B | 76,8% (44,6%) | 69,4% (59,8%) | 49,2% (16,8%) | 70,7% (54,6%) |
| 100B | 77,6% (53,3%) | 70,8% (62,0%) | 52,7% (22,7%) | 72,1% (58,2%) |

### BẢNG S5 — per-year: sụt giảm 10B→50B có bền không?

| Chân | Số năm GIẢM khi 10B→50B | Đọc |
|---|---:|---|
| thật @20% | **8/13** | yếu — nhất quán với chẩn đoán reshuffle-luck ở §6 |
| **thật @4%** | **11/13** | **bền rõ rệt hơn** — sụt giảm theo NAV là THẬT ở trần hiện thực |
| lý tưởng | 13/13 | (chi phí capacity sạch, biên độ nhỏ) |

### Điều PHẢI SỬA so với §9

1. **Cơ chế (§5) và cảnh báo "đừng đọc CAGR-theo-NAV như đường cong capacity" (§0.3): GIỮ NGUYÊN**,
   nay mạnh hơn vì đã sống sót một tham số bị đổi 5× (7/8 mốc; mốc 100B đổi dấu, xem S2).
2. **"Trần capacity ≈50B, chi phí ~1pp" KHÔNG ổn định và đọc là CẬN DƯỚI LẠC QUAN.** Con số ~1pp
   đến từ chân LÝ TƯỞNG, vốn **chỉ còn** slippage-thoát ⇒ **không phải** chi phí nhà đầu tư thật gánh.
3. **TRẦN CAPACITY THỰC DỤNG ĐÃ ĐỊNH VỊ ĐƯỢC (không còn chỉ "bracket"): đỉnh ở ~10B, và mất >1pp
   so với đỉnh ngay ở 20B** (29,70 → 28,04 = **−1,66pp**). Sau đó xấu nhanh và đơn điệu:
   **−2,83pp @30B · −5,20pp @50B · −6,15pp @75B · −7,78pp @100B**, kèm Calmar **1,69 → 1,02**.
   ⇒ **vùng an toàn ≈ 10–20B, KHÔNG phải ≈50B.**
4. Ràng buộc **THI HÀNH** vẫn cắn trước và mạnh nhất: ở trần hiện thực, sổ LAG bỏ dở **35,6% ngay
   tại 1B** (≈ NAV live hôm nay), tổng bỏ dở **27,0%**.

### Vẫn chưa đóng được
`LIQ_PCT=0.04` là **một** giá trị thay thế hợp lý, **không phải giá trị đúng đã đo**. Sự thật nằm
đâu đó giữa 4% và 20%, và **chiều dịch chuyển của kết luận theo tham số này là lớn** (50B: 28,86% ↔
24,50%) — nên **vị trí đỉnh 10B cũng sẽ trôi lên** nếu fill thật hội tụ về 8–10% thay vì 4%.
Chỉ **tích luỹ fill THẬT** mới đóng được — đúng 2 mốc cứng **2026-12-15 / 2027-03-31** trong
`kb/projects/lag-adv-filter-tracking.md`. Việc còn thiếu (quant-skeptic `recommended_reruns` #3,
CHƯA chạy): quét `LIQ_PCT ∈ {0.04…0.20}` ở NAV cố định để biết **độ dốc** của chỗ sụp, thay vì 2
đầu mút. **Không con số nào ở §10 đủ tư cách làm căn cứ duy nhất cho quyết định bơm vốn thật.**

**Tái lập:** `run_cap.sh <NAV> 0 0.04` (tham số thứ 3 tuỳ chọn, bỏ trống = 0.20 = y hệt 16 chân
gốc) · bảng: `"$DNA_PYEXE" sens.py` · hiện vật: `cap{1,5,10,20,30,50,75,100}b_real_liqpct0p04.log`,
`sens_liqpct_raw.csv`, `cap50b_real.log.orig` (bản gốc giữ để đối chứng regression).

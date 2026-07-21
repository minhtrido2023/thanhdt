# `ticker_prune` — điều tra thực nghiệm + đề xuất bộ quy tắc quản trị universe

Job `Taylor_20260721_162005` · 2026-07-21 · Taylor (Quant)
**Trạng thái: RESEARCH + PROPOSAL. KHÔNG sửa bảng/code production trong job này.**

---

## 0. TL;DR — 3 câu

1. **Nỗi lo của user ĐÚNG nhưng chưa đủ mạnh.** Danh sách có bị đóng băng thật (không có mã mới nào
   vào giữa **2026-03-13 → 2026-07-06**, đúng khung "3-4 tháng"), và đã được ai đó **mở băng bằng 1
   lô thủ công 41 mã ngày 2026-07-06**. Nhưng độ trễ kết nạp mã mới niêm yết thì tệ hơn user nghĩ:
   nhanh nhất ~85 ngày, chậm nhất **948 ngày**, và **20+ mã niêm yết 2023-2026 tới nay vẫn chưa từng
   vào bảng** (kể cả VPL/Vinpearl — trễ 419 ngày).
2. **Rủi ro LỚN HƠN cái user hỏi, và chưa ai biết: `ticker_prune` đang bị GHI ĐÈ LỊCH SỬ.** Đối chiếu
   bảng hiện tại với backup `ticker_prune_ttbackup_fresh_20260713` cho thấy **10.850 dòng lịch sử
   2014-2025 được THÊM VÀO chỉ trong 8 ngày qua** (IVS, PXL, TIS, FRT… toàn bộ history mới xuất hiện).
   → **Mọi backtest pin (kể cả R3 27,84%) chạy hôm nay KHÁC với chính nó chạy tuần trước, dù không
   đổi 1 dòng code nào.** Đây là silent drift của baseline, không phải rủi ro stale.
3. **Và cách đội đang DÙNG bảng còn tạo look-ahead riêng:** 496 chỗ trong repo (gồm cả `pt_v23_audit_
   2014.py` pin R3 và `custom_basket.py` custom30V) viết `ticker IN (SELECT DISTINCT ticker FROM
   ticker_prune)` — **không có điều kiện thời gian**. Universe hợp-nhất-toàn-lịch-sử này lớn gấp
   **1,63×–2,55×** universe point-in-time tại mọi mốc lịch sử → backtest được phép mua "mã mà sau này
   mới đủ chất lượng/thanh khoản".

Thứ tự ưu tiên sửa (ngược với trực giác ban đầu): **(3) look-ahead trong code → (2) drift lịch sử →
(1) độ trễ kết nạp mã mới.** Mục (3) và (2) làm hỏng con số ta đang tin; mục (1) chỉ làm mất cơ hội.

---

## 1. Xác minh claim bq_admin bằng dữ liệu thật

### 1.1 Bảng KHÔNG đứng yên ở mức membership ngày — nhưng pool thì có bị đóng băng

Số mã distinct theo tháng vẫn dao động sau tháng 3 (2026-01: 269 → 2026-06: 245 → 2026-07: 274), nên
"danh sách fix cứng" **không đúng theo nghĩa membership ngày**. Nhưng nhìn **ngày xuất hiện LẦN ĐẦU**
của mỗi mã thì lộ ra sự thật:

| Tháng xuất hiện lần đầu | Số mã | Mã |
|---|---|---|
| 2025-09 | 1 | VVS |
| 2026-01 | 1 | TCX |
| 2026-03 | 2 | GCF, VPX |
| **2026-04 → 2026-06** | **0** | — (đóng băng 4 tháng) |
| **2026-07-06** | **41** | AAS AAV ASP BAF BIG C69 CDC CTF DSE DST DXS FOX HNG KOS L40 MSR NRC NVB ORS PCH PIV PPT PSI SBG SBS SCG SGR STH TAL TDP THD TIN TLD TSA TTF VCK VGI VIW VJC VPL VTD |
| 2026-07-08 | 2 | AIG, + 1 |

41 mã vào **cùng đúng 1 ngày** = can thiệp lô thủ công, không phải rule chạy đều. Và 41 mã này **có
lịch sử rất dài trong `ticker`** (ASP từ 2008, TTF 2008, NVB/ORS/PSI/SBS 2010) — tức không phải mã
mới, mà là mã **đáng lẽ phải có từ lâu nhưng bị bỏ sót**.

→ **Kết luận: pool bị đóng băng 2026-03-13 → 2026-07-06 (đúng khung user nghe được), và đã được
mở băng thủ công 2 tuần trước.** 45 mã "thêm vào" trong spot-check của Mike **không phải** mã tạm
ngừng quay lại — chúng là mã bổ sung thật vào pool.

### 1.2 Độ trễ kết nạp mã niêm yết mới — có 2 chế độ, chế độ tự động KHÔNG đáng tin

Mã niêm yết lần đầu từ 2023 (ngày đầu có trong `ticker`) vs ngày đầu vào `ticker_prune`:

| Chế độ | Mã | Trễ (ngày) |
|---|---|---|
| **Tự động (~3 tháng)** | ABW 83 · GDA 83 · TCX 85 · VPX 92 · MZG 94 · CCC 315 | 83–94 (một số 315) |
| **Chỉ vào nhờ lô thủ công 07-06** | VCK 202 · **VPL 419** · AIG 604 · DSE 735 · TSA 741 · TAL 909 · SBG 948 | 202–948 |
| **Tới nay CHƯA BAO GIỜ vào** | VNZ GPC BHI THM HIO NCG BCR SBB AAH QNP ING BGE TT6 AVG ECO RYG DDB TNV DKG SLD RGG DCV STD UPS (24 mã) | ∞ |

Chế độ tự động ~85 ngày khớp với việc cần đủ cửa sổ `Volume_3M` (≈60 phiên) — hợp lý. Nhưng nó
**bỏ sót phần lớn**: VPL (Vinpearl, IPO 05/2025, ADV ~783k cp/ngày) vô hình với universe 14 tháng.
Không có cách nào giải thích VPL trượt rule tự động bằng thanh khoản → **rule tự động không phủ hết,
hoặc có 1 danh sách curated ở giữa mà rule phải "được cho phép" mới xét.**

### 1.3 ETL ĐANG GHI ĐÈ LỊCH SỬ — phát hiện quan trọng nhất của job này

So `tav2_bq.ticker_prune` (hôm nay) vs `tav2_bq.ticker_prune_ttbackup_fresh_20260713`, cửa sổ
2014-01-01 → 2026-07-10 (loại hẳn phần append hằng ngày mới):

```
n_now = 736.353   n_bak = 725.562   chỉ-có-ở-NAY = 10.850   chỉ-có-ở-BACKUP = 59
```

Phân bố 10.850 dòng thêm mới theo năm — **rải đều khắp lịch sử, không phải chỉ phần đuôi**:

| Năm | Dòng thêm | Số mã | Mẫu |
|---|---|---|---|
| 2014 | 533 | 3 | GGG, IVS, PXL |
| 2015 | 867 | 16 | AGR BID BVS C32 HAH HKB HTI IVS MWG NHA NNC PPC |
| 2016 | 898 | 15 | BID BMP BVS C32 HCM HTI IVS NHA PPC PTC PVD TIS |
| 2017-2020 | 2.353 | 4-7/năm | ATS FRT HTT NTC PXL TIS VIT VNA VRG |
| 2021 | 1.429 | 14 | FRT IVS KSV PXL RTB SGI SVT TID TIS TNS TRA VIT |
| 2022 | 1.542 | 11 | … |
| 2023-2025 | 2.651 | 8-9/năm | BTH FRT HTG IVS KGM KSV MZG PTC PXL TID TIS VNA VPD VRG |
| 2026 | 577 | 47 | (lô 07-06 + backfill) |

Kiểm chứng ở mức từng mã:

| Mã | Backup 07-13 | Hiện tại |
|---|---|---|
| IVS | **0 dòng** | 1.622 dòng, từ **2012-03-20** |
| PXL | **0 dòng** | 2.631 dòng, từ 2011-03-11 |
| TIS | **0 dòng** | 682 dòng, từ 2016-12-30 |
| FRT | 5 dòng (2026-07-07→07-13) | 1.963 dòng, từ **2018-07-20** |
| BID / MWG | 2.989 / 2.879 | 3.054 / 2.944 (chênh = append thường + vài dòng 2015-16) |

→ Cơ chế: mã được thêm vào pool trước (forward-only), rồi **một lượt ETL sau đó backfill TOÀN BỘ
lịch sử của nó**. FRT đã được backfill; 41 mã lô 07-06 thì **chưa** (min time vẫn 2026-07-06). Nghĩa
là **quá trình backfill đang chạy dở, bảng vẫn là mục tiêu di động ngay lúc này.**

**Hệ quả trực tiếp cho đội:** IVS — đúng mã đang tranh cãi trong book LAG tuần này — **toàn bộ lịch
sử của nó vừa được thêm vào universe backtest trong 8 ngày qua.** Mọi kết luận backtest có dính IVS
trước 07-13 chạy trên universe khác với hôm nay.

### 1.4 Rule membership: KHÔNG phải ngưỡng thanh khoản thuần — có curation

Tại 2026-06-15, so `Volume_3M_P50` giữa trong/ngoài prune:

| | n | v3 min | p5 | p50 | max |
|---|---|---|---|---|---|
| trong prune | 233 | 12.450 | 43.150 | 598.700 | 782.759.023 |
| ngoài prune | 1.011 | 0 | 0 | 250 | 3.755.750 |

Có **chồng lấn rõ**: 28 mã thanh khoản >200k cp/ngày bị loại, 12 mã <50k được giữ. Không có ngưỡng
đơn nào tách sạch → **có một danh sách curated (đúng như user mô tả: "legacy product selection") nằm
trên ngưỡng thanh khoản.** Membership KHÔNG liên tục theo mã (SAV: 1.460 dòng prune trong khoảng
thời gian có 5.571 dòng `ticker`) → **có filter theo ngày chạy trên lịch sử**, tức hình dạng lịch sử
là time-varying (điểm tốt), nhưng tiêu chí chính xác không reverse-engineer được từ dữ liệu.
**→ Phải hỏi bq_admin, không đoán (§6).**

---

## 2. Khảo sát consumer — và một look-ahead ta tự gây ra

### 2.1 Hai nhóm nhu cầu

| Nhóm | File | Cần gì |
|---|---|---|
| **LIVE / production** | `custom_basket.py` (custom30V), `pt_v23_audit_2014.py` §5 (CAPIT breadth + basket), `trading_bot/due_diligence.py` (cờ "ngoài universe"), `trading_bot/executor.py`, `macro_state_live.py` (breadth Pillar B guard), `mike/bin/preflight_check.sh` + `bq_freshness_check.sh` (depth gate ≥ ~225 mã) | **TƯƠI**: mã mới đủ thanh khoản phải vào sớm; mã delist/cạn thanh khoản phải ra ngay |
| **BACKTEST / pin** | `pt_v23_audit_2014.py` (R3 pin), ~330 script research/experiment | **ỔN ĐỊNH + POINT-IN-TIME**: universe tại ngày d chỉ được dùng thông tin ≤ d, và không được đổi giữa 2 lần chạy |

Hai nhu cầu này **mâu thuẫn nhau** và hiện đang dùng **cùng một bảng, cùng một cách gọi** — đó là gốc
của toàn bộ vấn đề.

### 2.2 Look-ahead do cách gọi (nghiêm trọng, độc lập với ETL)

496 vị trí trong repo (không tính `archive/`) dùng dạng:

```sql
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)   -- KHÔNG có điều kiện time
```

gồm `pt_v23_audit_2014.py` (dòng 663, 729, 758, 841 — pin R3) và `custom_basket.py` (dòng 114, 202,
656 — custom30V production). Đây là **hợp của mọi mã từng có mặt trong prune bất kỳ lúc nào**, áp cho
mọi ngày lịch sử. Đo độ phồng:

| Ngày | Universe point-in-time | Universe dạng-hợp | Tỷ lệ |
|---|---|---|---|
| 2014-06-30 | 140 | 316 | **2,26×** |
| 2016-06-30 | 167 | 367 | 2,20× |
| 2018-06-29 | 180 | 459 | **2,55×** |
| 2020-06-30 | 226 | 494 | 2,19× |
| 2022-06-30 | 321 | 523 | 1,63× |
| 2024-06-28 | 310 | 535 | 1,73× |
| 2026-06-15 | 233 | 540 | 2,32× |

**Đây chính xác là cái bẫy user nêu trong dispatch** ("biết trước năm 2015 rằng mã X sẽ thanh khoản
tốt năm 2026") — và nó **đã nằm sẵn trong pin R3 từ trước**, không phải rủi ro tương lai.

⚠️ Cần nói cho công bằng về mức độ: backtest còn áp **filter thanh khoản/chất lượng point-in-time
riêng** ở tầng dòng (`adv_yoy`, `ta>=120`, `Volume_3M_P50`…). Nên bias còn lại là dạng mềm — "mã về
sau mới trở thành mã chất lượng" — chứ không phải mua thẳng mã chết. **Độ lớn thật CHƯA ĐO ĐƯỢC,
phải chạy A/B mới biết (§4.1).** Không kết luận R3 sai trước khi đo.

Và điều nối §1.3 với §2.2: vì universe backtest = `DISTINCT` toàn lịch sử, **mỗi lần ETL thêm 1 mã
vào pool là universe lịch sử của MỌI backtest phồng lên ngay lập tức** — 41 mã lô 07-06 đã đủ tư
cách giao dịch từ 2014 trong bất kỳ lần chạy lại nào từ 07-06 trở đi.

---

## 3. ĐỀ XUẤT — bộ quy tắc quản trị universe

Nguyên tắc nền: **tách hẳn 2 vai trò.** Bảng của bq_admin là *nguồn dữ liệu thô*; universe là *quyết
định của đội Mike* và phải do đội sở hữu, đúng tinh thần `coding_guidelines.md` §9/§11.

### 3.1 Tầng do đội Mike sở hữu — `universe_pit` (khuyến nghị chính)

Xây 1 bảng/parquet **append-only, bất biến** do ta tự tính, **chỉ từ cột thô point-in-time của
`tav2_bq.ticker`** (giá/khối lượng/ICB — dữ liệu sự kiện, không phải danh sách curated):

```
universe_pit(time DATE, ticker STRING, in_universe BOOL, reason STRING,
             ruleset_version INT, backfilled BOOL, computed_at TIMESTAMP)
```

- Ghi bởi `bin/build_universe_pit.py`, chạy hằng ngày, **CHỈ APPEND ngày mới — không bao giờ sửa
  dòng quá khứ.**
- Backfill 1 lần lúc tạo (2000→nay), gắn `backfilled=true`, `ruleset_version=1`.
- **Phân biệt bắt buộc, cần nói rõ với user:** *tính lại* universe quá khứ bằng dữ liệu trailing
  (chỉ dùng thông tin ≤ ngày đó) **KHÔNG phải look-ahead** — hoàn toàn hợp lệ. *Sửa* membership quá
  khứ theo danh sách curated của hôm nay **LÀ look-ahead** — đó là cái đang xảy ra ở §1.3.
- Vì rule chỉ ăn dữ liệu thô, universe **tái lập được bit-for-bit** cho mọi ngày lịch sử, cho mọi
  version rule → giải quyết dứt điểm yêu cầu point-in-time trong dispatch.

### 3.2 Tiêu chí thành viên đề xuất (v1 — đo được, có hysteresis)

| # | Điều kiện | Giá trị đề xuất | Lý do |
|---|---|---|---|
| B1 | Có dòng trong `ticker` ngày d **và** `ICB_Code IS NOT NULL` | — | loại pseudo-ticker chỉ số; đúng rule `custom_basket.py` đang dùng |
| B2 | Tuổi niêm yết ≥ 60 phiên kể từ dòng đầu trong `ticker` | 60 phiên | cần đủ cửa sổ `Volume_3M`; **khớp đúng chế độ tự động ~85 ngày đang chạy** → không đổi hành vi các mã đang OK |
| B3 | **VÀO**: median giá trị giao dịch 60 phiên gần nhất ≥ **1,0 tỷ VND/ngày**, khử lạm phát bằng `Inflation_7` (giá trị thực, neo 2026) | 1,0 tỷ | `Inflation_7` có sẵn trong bảng đúng cho mục đích này; ngưỡng danh nghĩa cố định sẽ làm universe 2014 phồng giả |
| B4 | **RA**: chỉ loại khi cùng thước đo < **0,5 tỷ** trong **20 phiên LIÊN TIẾP** | 0,5×, 20 phiên | băng vào/ra bất đối xứng chống whipsaw — cùng triết lý DT5G 4-gate (`enC=25`/`exC=10`), nhất quán house style |
| B5 | Giá sàn `Close ≥ 1.000 VND` | 1.000đ | quan sát: min Close trong prune = 1.799đ, ngoài = 10đ |
| B6 | **Loại cứng ngay** (bỏ qua B4): không có dòng trong `ticker` 10 phiên liên tiếp (delist/đình chỉ) | 10 phiên | giữ mã delist trong universe nguy hiểm hơn nhiều so với chi phí churn |
| B7 | Mã bị loại phải **đủ điều kiện lại từ đầu** (B2-B5) mới quay lại | — | chặn nhấp nháy quanh ngưỡng |

⚠️ Ngưỡng 1,0/0,5 tỷ là **đề xuất khởi điểm, chưa hiệu chuẩn**. Trước khi chốt phải sweep để bộ tiêu
chí này tái tạo gần đúng universe hiện hành (mục tiêu: overlap ≥85% với prune tại vài mốc lịch sử) —
nếu lệch quá xa thì hoặc rule sai, hoặc curation của bq_admin mang thông tin ta chưa nắm (§6).

### 3.3 Cadence refresh

| Loại thay đổi | Đánh giá | Có hiệu lực |
|---|---|---|
| Kết nạp mới (B2-B5) | **hằng ngày** | **thứ Hai kế tiếp** |
| Loại do thanh khoản (B4) | hằng ngày | thứ Hai kế tiếp |
| Loại cứng delist/đình chỉ (B6) | hằng ngày | **NGAY trong ngày** |

Đánh giá hằng ngày ⇒ mã mới vào trong ≤ 7 ngày sau khi đủ 60 phiên (thay vì 83–948 ngày như hiện
nay). Commit theo tuần ⇒ production rebalance không bị nhiễu trong tuần. Không xung đột với nhịp
q2m5 của custom30V hay CAPIT (chọn rổ tại thời điểm fire).

### 3.4 Tách consumer theo 2 nhu cầu

- **LIVE** (custom30V, CAPIT, BAL/LAG, due-diligence, breadth, preflight depth gate) → đọc
  `universe_pit` với `time = ngày giao dịch gần nhất`. Tươi, có hysteresis, không whipsaw.
- **BACKTEST** → đọc `universe_pit` **join theo NGÀY**:
  ```sql
  AND EXISTS (SELECT 1 FROM universe_pit u
              WHERE u.ticker=t.ticker AND u.time=t.time AND u.in_universe)
  ```
  **Cấm tuyệt đối dạng `IN (SELECT DISTINCT ticker …)` không có điều kiện thời gian** — thêm dòng
  cấm này vào `coding_guidelines.md` cạnh §9.
- **Fail-safe**: nếu `universe_pit` thiếu ngày cần dùng → **dừng có lỗi**, không âm thầm fallback về
  `ticker_prune` (nếu không, ta lại thừa hưởng đúng cái drift đang muốn tránh).

### 3.5 Versioning khi đổi rule (yêu cầu 3.d của dispatch)

1. Mọi lần đổi tiêu chí → **`ruleset_version` tăng**, không bao giờ sửa tại chỗ. Bảng giữ cả 2
   version song song (một mã có thể có 2 dòng cùng ngày, khác version).
2. Changelog `mike/kb/universe_ruleset.md`: version · ngày · đổi gì · vì sao · ai duyệt.
3. Mọi backtest **in ra** `ruleset_version` + **hash SHA của tập membership** trong log; `data/
   results_registry.md` pin cả 2 cùng với CAGR. → Hai lần chạy khác universe không thể nhầm là như
   nhau nữa. Đây là thứ lẽ ra đã bắt được sự cố §1.3 ngay lập tức.
4. Đổi version = thay đổi production ⇒ theo chuẩn hiện hành: A/B đo tác động → quant-skeptic →
   user duyệt.
5. `mike/kb/data_registry.md`: thêm entry `universe_pit` = **CANONICAL**, và sửa entry
   `ticker_prune` thành **TRAP** với 3 bẫy đã đo (ghi đè lịch sử · pool đóng băng từng đợt · dạng
   `DISTINCT` gây look-ahead 1,6-2,6×).

---

## 4. Lộ trình + trade-off để Mike/user quyết

### 4.1 Việc nên làm trước tiên (rẻ, không đổi production)

**A/B đo độ lớn thật của look-ahead** trước khi quyết bất cứ điều gì: chạy `pt_v23_audit_2014.py` 2
lần, chỉ đổi mệnh đề universe (dạng-hợp hiện tại vs join theo ngày), ghi ra file experiment riêng
theo `coding_guidelines.md` §8 (**tuyệt đối không ghi đè CSV pin R3**). Kết quả quyết định mọi thứ:

- Lệch nhỏ (≲1pp CAGR) → look-ahead vô hại trên thực tế; vẫn sửa cho đúng nhưng không khẩn, không
  phải re-pin gấp.
- Lệch lớn → **pin R3 27,84% đang được thổi lên bởi survivorship**, phải re-pin và xem lại mọi kết
  luận N-trial tuần qua chạy trên cùng universe.

Chi phí: 2 lần chạy backtest. Chưa làm trong job này vì dispatch giới hạn ở research + proposal.

### 4.2 Trade-off cần user cân nhắc

| Quyết định | Được | Mất |
|---|---|---|
| Chuyển sang `universe_pit` (§3.1) | Point-in-time thật, tái lập được, ta kiểm soát, hết drift | Phải xây + bảo trì 1 lớp nữa; universe lịch sử **co lại 1,6-2,6×** ⇒ mọi số pin đổi, phải chạy lại toàn bộ; rule của ta có thể **thua** curation của bq_admin (họ có thể lọc cả thứ ta không nhìn thấy: mã bị cảnh báo/kiểm soát, cổ đông cô đặc, BCTC ngoại trừ) |
| Giữ `ticker_prune`, chỉ sửa dạng gọi thành join-theo-ngày | Rẻ nhất, diệt look-ahead §2.2 ngay, giữ nguyên curation của bq_admin | **Không chữa được §1.3** — lịch sử vẫn bị ghi đè sau lưng, pin vẫn drift; vẫn phụ thuộc cadence kết nạp không kiểm soát được |
| Snapshot đóng băng `ticker_prune` mỗi ngày vào parquet ta giữ | Rẻ, chặn drift ngay từ mai, giữ curation | Đóng băng luôn cả look-ahead đã có sẵn trong lịch sử; không sửa được quá khứ (chỉ còn backup 07-13 làm mốc so) |

**Khuyến nghị của tôi (Taylor): làm cả 3 theo thứ tự thời gian.** (i) snapshot đóng băng hằng ngày
**ngay** — 1 script, chặn drift từ mai; (ii) sửa dạng gọi trong 2 file production + `pt_v23` sau khi
có số A/B; (iii) `universe_pit` là đích đến, nhưng chỉ khởi công sau khi bq_admin trả lời §6 — nếu
curation của họ mang thông tin thật, ta muốn **tái tạo** nó chứ không phải vứt đi.

### 4.3 Ranh giới team Mike vs bq_admin

Đội Mike **không** sở hữu ETL gốc → không tự sửa được cadence kết nạp, không chặn được ghi đè lịch
sử ở nguồn. Nhưng **toàn bộ §3 nằm ở tầng consumer và team Mike làm được 100%** mà không cần
bq_admin đổi gì. Cái duy nhất phải xin bq_admin là **thông tin** (§6), không phải quyền sửa.

### 4.4 Không làm trong job này

Không sửa bảng, không sửa code, không đụng pin R3, không mass-edit 496 site (`coding_guidelines.md`
§3 — phần lớn là script research đã chết; chỉ sửa production + backtest canonical).

---

## 5. Rủi ro/hạn chế của chính đề xuất này (nói thẳng)

- Ngưỡng 1,0/0,5 tỷ VND **chưa hiệu chuẩn** — số khởi điểm, không phải kết quả tối ưu hoá. Đừng
  trích như đã kiểm chứng.
- Chưa đo tác động của việc chuyển sang PIT lên bất kỳ metric nào (§4.1 chưa chạy). Mọi phát biểu
  "R3 bị thổi phồng" hiện là **giả thuyết chưa kiểm chứng**.
- Bằng chứng ghi-đè-lịch-sử dựa trên **1 backup duy nhất** (`ttbackup_fresh_20260713`). Đã kiểm tra
  loại trừ khả năng backup lỗi/chép dở: BID/MWG có cùng `MIN(time)` ở 2 bảng và chỉ chênh phần
  append cuối, trong khi IVS/PXL/TIS thiếu **toàn bộ** — không khớp mẫu "backup chép thiếu ngẫu
  nhiên". Nhưng n=1 snapshot; nên xin bq_admin xác nhận thay vì coi là đã đóng (§6 câu 4).
- Rule curated của bq_admin có thể mang thông tin thật (mã diện cảnh báo/kiểm soát, ý kiến kiểm toán
  ngoại trừ) mà rule thanh khoản thuần của ta **không** có. Thay thế mù có thể **làm xấu** universe.

---

## 6. Câu hỏi cụ thể nên hỏi bq_admin (đừng đoán)

1. **Rule chính xác** để một mã vào/ra `ticker_prune` là gì? Ngưỡng nào, cửa sổ bao nhiêu phiên,
   đánh giá theo cadence nào?
2. Có **danh sách curated thủ công** ("legacy product selection") nằm trên rule thanh khoản không?
   Ai sửa, sửa khi nào, theo trigger gì?
3. Có phải pool bị **đóng băng 2026-03-13 → 2026-07-06** không? Lô 41 mã ngày 2026-07-06 là gì —
   sửa lỗi thủ công, hay đổi rule?
4. **ETL có ghi đè dòng lịch sử không?** Chúng tôi đo được **10.850 dòng của 2014-2025 được thêm mới
   trong 8 ngày (07-13 → 07-21)**, gồm toàn bộ lịch sử của IVS/PXL/TIS/FRT. Đây là backfill có chủ
   ý? Đang chạy dở? Còn bao nhiêu đợt nữa? **Có lịch để đội chúng tôi biết khi nào bảng ổn định lại?**
5. Khi thêm 1 mã, lịch sử của nó có được backfill **toàn bộ** không? (FRT: đã backfill; 41 mã 07-06:
   chưa — vì sao khác nhau?)
6. Membership lịch sử được tính **point-in-time** (chỉ dùng dữ liệu ≤ ngày đó) hay **áp tiêu chí hôm
   nay ngược lại quá khứ**? Đây là câu quan trọng nhất với backtest của chúng tôi.
7. Có **versioning/changelog** của tiêu chí không? Bảng hiện đang chạy version nào, đổi lần cuối khi nào?
8. Mã niêm yết mới có **đường tự động** không? Chúng tôi thấy ~85 ngày cho ABW/GDA/MZG/TCX/VPX,
   nhưng **24 mã niêm yết 2023-2026 tới nay chưa từng vào** (VNZ, QNP, AAH, DKG, SLD…) và VPL
   (Vinpearl) phải chờ 419 ngày. Vì sao trượt?
9. Có thể cung cấp **snapshot/`as_of`** (bảng giữ membership từng ngày, bất biến) không, hay đội
   chúng tôi tự dựng lớp đó?
10. Mã **delist** thì lịch sử được giữ hay xoá khỏi bảng?

---

## 7. Việc kế tiếp nếu được duyệt

1. Hỏi bq_admin 10 câu §6 (qua user) — không blocking cho việc 2.
2. Chạy A/B look-ahead §4.1 → biết độ lớn thật → quyết có phải re-pin R3 không.
3. Script snapshot đóng băng `ticker_prune` hằng ngày (chặn drift từ mai, rẻ, không phá gì).
4. Sau khi có §6: quyết `universe_pit` (tự dựng) vs mirror curation của bq_admin.
5. Cập nhật `data_registry.md` (`ticker_prune` → TRAP) + `coding_guidelines.md` (cấm dạng `DISTINCT`
   không có điều kiện thời gian).

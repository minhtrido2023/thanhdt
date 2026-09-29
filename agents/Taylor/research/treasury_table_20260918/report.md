# `tav2_mike.treasury_share_events` — loader one-time + dry-run
*(job Taylor_20260918_103820; vá B1 + dọn N1–N4 ở job Taylor_20260918_110145)*

**CHƯA ghi BigQuery, CHƯA tạo bảng.** Dừng ở worktree `mike/agents/wt-treasury-table`
(branch `feat/treasury-share-events-table`). Chờ arch-reviewer + quyết định của Mike/user.

Tái lập từ `WorkingClaude/`:
```
$DNA_PYEXE mike/agents/.../treasury_table_20260918/build_treasury_share_events.py   # đọc BQ read-only -> CSV
$DNA_PYEXE .../treasury_share_events_selfcheck.py                                   # hermetic, 0 lần chạm BQ
$DNA_PYEXE .../mutation_test.py
```

## Kết quả một dòng
577 dòng dựng xong, **164 SIZED / 413 UNSIZED**, 3 tier tách bạch bằng cột riêng, **2 nhóm trùng
được đánh dấu** (§1b — `SUM` thô phồng 3.008.900 CP nếu không lọc `is_canonical`).
**GIÁ TRỊ của 33 ca suy luận được recompute ĐỘC LẬP từ `ticker_financial.OShares` — 33/33 khớp
chính xác**, không ca nào bị từ chối; *cửa sổ quý* và *bộ lọc confounder* thì vẫn kế thừa nguyên
của Winston, **chưa** verify độc lập (§2). Selfcheck 110/110 PASS trên 3 TZ, mutation 32/32 killed.

## 1 — Phân rã nguồn (không trộn lẫn)

| `source` | n | `confidence` | `confirmed_asof` | `outstanding_delta` |
|---|---:|---|---|---|
| `VENDOR_PUBLISHED` | 128 | high | NULL | vendor công bố, lật dấu |
| `SIBLING_ROW` | 3 | high | NULL | vendor công bố (chỉ bị dedup che) |
| `OSHARES_DELTA_INFERRED` | 33 | **medium** | **có** | suy từ ΔOShares |
| *(UNSIZED)* | 413 | NULL | NULL | **NULL** |
| | **577** | | | |

`SIBLING_ROW` = CTD 2018-02-06 (+448.500), HVG 2020-01-13 (+5.000.000), KHW 2018-02-22 (+24.000)
— đây là **số vendor công bố**, không phải suy luận ⇒ `confidence=high`, nhưng vẫn để `source`
riêng vì đường lấy số khác (dòng anh em cùng sự kiện, không phải dòng chính).

**Quy ước dấu — đo trên toàn bộ 577 sự kiện, 0 vi phạm**: `treasury_news.shares_delta` = Δ lượng
CP **quỹ nắm giữ** (buy_done ≥0 / sell_done ≤0) ⇒ `outstanding_delta` = Δ lượng CP **lưu hành** =
`-shares_delta`, một phép lật dấu duy nhất. Loader `raise` nếu gặp dòng ngược dấu, không tự sửa.

**3 sự kiện vendor công bố size = 0** (CKV 2018-10-17, SWC 2018-11-27, VSA 2017-06-20 — đăng ký
nhưng không khớp gì): xếp **SIZED với `outstanding_delta = 0`**, KHÔNG phải UNSIZED. Đây là con số
vendor thật sự công bố; đúng lý do ngược lại là vì sao 413 ca UNSIZED phải để **NULL** chứ không
phải 0.

## 1b — Bẫy đếm 2 lần: một giao dịch, hai ngày công bố (B1, arch-reviewer phát hiện)

Khoá gộp `(ticker, public_date, action_type)` là **điều kiện cần nhưng chưa đủ**. Vendor có thể
đăng cùng một đợt mua ở hai ngày khác nhau (thông báo chính thức + tin báo chí), hoặc một dòng
vendor chồng lên một dòng suy từ OShares. Hai ca đo thật trên chính 577 dòng:

| Ca | Hai dòng | Mỗi dòng | `SUM` thô | Thật |
|---|---|---|---|---|
| NDN `buy_done` | 2018-05-17 + 2018-05-18, cả hai `VENDOR_PUBLISHED` | −1.000.000 | −2.000.000 (+2,5% trên ~39,6tr CP lưu hành) | −1.000.000 |
| CTD `buy_done` | 2021-02-01 `OSHARES_DELTA_INFERRED` + 2021-02-03 `VENDOR_PUBLISHED` | −2.008.900 / −2.000.000 | −4.008.900 (+2,7%) | −2.000.000 |

Ca CTD là ca khó: hai dòng **khác tier** nhưng là cùng một giao dịch thật (mua hơn 2 triệu CP giá
76.764đ). Guard `MULTI_EVENT` của Winston chỉ đếm trong `(lo, hi]` nên bỏ lọt sự kiện "vọng lại"
ngay sau `hi`.

**Ba cột mới**: `dup_group_id` (NULL khi dòng đứng một mình) · `is_canonical` BOOL NOT NULL ·
`duplicate_of` (id dòng canonical). Luật xác định trong `mark_duplicates()`: cùng `ticker` +
`action_type`, cách dòng **NEO của nhóm ≤14 ngày**, `|outstanding_delta|` lệch **≤5%** ⇒ cùng một
giao dịch. Canonical = tier tin nhất (`VENDOR_PUBLISHED` > `SIBLING_ROW` > `OSHARES_DELTA_INFERRED`),
rồi `public_date` sớm nhất, rồi `id` nhỏ nhất — nên CTD giữ dòng **vendor** (−2.000.000), không giữ
dòng suy luận. Dòng bị loại **ở lại trong bảng** để audit.

Trên lô hiện tại: **2 nhóm, 2 dòng `is_canonical=FALSE`**.
`SUM` thô **−247.899.980** vs lọc canonical **−244.891.080** — chênh **3.008.900 CP** (1,2%).

### Ngưỡng chọn từ phân phối thật, không cảm tính
Quét mọi cặp `SIZED` cùng `ticker`+`action_type`:

| gap | lệch giá trị | cặp |
|---:|---:|---|
| 1 | 0,00% | NDN (ứng viên trùng) |
| 2 | 0,44% | CTD (ứng viên trùng) |
| 53 | 65,61% | GDT — sự kiện KHÁC |
| 56 | 69,80% | PVI — sự kiện KHÁC |
| 64 | 50,00% | TW3 — sự kiện KHÁC |
| 78 | 25,09% / 38,92% | GIL, FOC — sự kiện KHÁC |

Và mọi cặp **cùng giá trị** (lệch ≤5%) còn lại đều cách nhau ≥**244 ngày**: HWS −58.500 hai lần
cách 274 ngày, VND −5.000.000 cách 244 ngày, TW3 −2.000 cách 266 ngày, CDP/HWS lệch 1,6–2,4% cách
283/321 ngày — **đợt mua THẬT thứ hai đúng lô cũ**, gộp lại là mất dữ liệu. ⇒ Mọi N trong
**[2, 52]** cho y hệt 2 nhóm; chọn **14** (thận trọng, gần đầu thấp) để hai đợt mua thật cách nhau
3 tuần không bao giờ bị gộp. **Neo theo dòng ĐẦU nhóm, không chain truyền tiếp** — chain sẽ nuốt
một chuỗi đợt mua thật liên tiếp thành một nhóm (selfcheck có fixture `CHN` 3 dòng cách nhau 10
ngày mỗi bước để chốt điều này; mutation M28 đổi sang chain và bị giết).

⚠️ **Giới hạn: dedup chỉ phủ dòng SIZED.** 413 dòng UNSIZED có delta NULL nên không so được theo
giá trị (và không cộng vào `SUM`). Đo được **6 cặp SIZED–UNSIZED + 18 cặp UNSIZED–UNSIZED** trong
vòng 14 ngày (HDB, SFI, STB, VJC…) — **nghi** trùng nhưng không chứng minh được, nên để nguyên
`is_canonical=TRUE` thay vì đoán. Hệ quả cần nói rõ: `COUNT(*)` số sự kiện có thể phồng tối đa 24;
`SUM(outstanding_delta)` thì không.

## 2 — 33 ca suy luận: recompute GIÁ TRỊ độc lập, không tin chuỗi mô tả (§28)
Winston trả kết quả trong cột `why` dạng chuỗi (`dOSh=6,222,000 (0.38%) q2019-10-22..2020-01-21`).
Loader **không tin chuỗi đó**: nó parse ra cặp ngày quý, rồi tự query `ticker_financial`, tự tính
`OShares(sau) − OShares(trước)`, và chỉ nạp khi con số tự tính **bằng đúng** số Winston suy ra,
đúng dấu kỳ vọng, và ≠ 0. Ca nào lệch → vào danh sách `rejected`, không nạp.

Kết quả: **33/33 khớp chính xác, 0 ca bị từ chối.** (Cơ chế từ chối có thật — mutation M11/M15
chứng minh: bỏ recompute hoặc bỏ nhánh từ chối đều bị selfcheck giết.)

### Nói rõ mức verify: **chỉ GIÁ TRỊ là độc lập** (N2)
Diễn đạt "recompute độc lập 33/33" ở bản trước dễ bị đọc thành "đã verify độc lập toàn bộ suy
luận" — không đúng. Cái được recompute là **con số**, với cửa sổ quý mà Winston đã chọn. Hai thứ
vẫn **kế thừa nguyên** của Winston (job `Winston_20260918_052425`) và CHƯA verify độc lập:
1. **Cửa sổ quý nào được chọn** — loader parse cặp ngày từ chuỗi `why` rồi dùng đúng cặp đó.
2. **Bộ lọc confounder** (`CA_CONFOUNDED` / `NO_MOVE` / `MULTI_EVENT` / `ISSUANCE_MATCH` /
   `SIGN_MISMATCH` / `OVER_CAP`) — quyết định ca nào *được phép* suy.

Tức là đã kiểm "cho cửa sổ này, số đúng"; **chưa** kiểm "cửa sổ này là cửa sổ đúng".

### `inferred_window_days` — nhóm control KHÔNG đại diện cho 5/33 dòng (N1)
Cột mới, lưu **bề rộng THẬT** của cửa sổ OShares dùng để suy (số đo, không phải nhãn `k`):
28 dòng **76–115 ngày** (~1 quý) và **5 dòng 176–188 ngày** — TSJ 2019-01-23 (176), SGP 2018-06-04
(182), LSS 2021-04-09 (182), DRH 2020-04-06 (184), SMN 2023-06-27 (188) — phải nới ra 2 quý vì quý
kế tiếp bị confounder. Khoảng trống 115→176 ngày tách hai nhóm rất sạch.

⚠️ Nhóm control gốc của Winston gần như chỉ gồm ca 1 quý (**12 ca k=0 / 1 ca k=1**) ⇒ ba con số
**77% / 85% / 92%** là thống kê của **cửa sổ 1 quý**, KHÔNG đo được cho 5 dòng cửa sổ dài này.
Consumer cần chắc hơn thì lọc `inferred_window_days <= 120`.

### `confirmed_asof` — cột PIT bắt buộc cho 33 dòng này
`= MAX(time, Release_Date)` của dòng BCTC quý SAU. Lý do lấy `MAX`: trên `ticker_financial` từ
2014, `Release_Date` NULL **11,7%** và lệch `time` **0,7%** (375/54.952) ⇒ lấy ngày muộn hơn để
không bao giờ lạc quan hơn thực tế.

Lag `confirmed_asof − public_date`: min 0 / trung vị **45** / max 149 ngày.
⚠️ **3 ca lag ≤3 ngày** — CTD 2021-02-01 (lag 0), VCI 2017-10-31 (1), VLB 2023-04-17 (3). Với
chúng `confirmed_asof` gần như không tách khỏi `public_date`; rủi ro không phải PIT leak (lag luôn
≥0) mà là **độ chính xác**: dòng BCTC phát hành gần như cùng ngày có thể chưa phản ánh sự kiện,
nên ΔOShares đo được có thể là chuyện khác. Đã nằm trong sai số control 77%, ghi ra để người dùng
sau nhìn thấy.

**Join theo `public_date` mà bỏ qua `confirmed_asof` là PIT leak** cho đúng 33 dòng này (trung vị
45 ngày nhìn trước). Đã ghi vào `OPTIONS(description=...)` của cột trong `schema.sql`.

## 3 — 413 ca UNSIZED: giữ NULL + cờ, giữ luôn LÝ DO
`outstanding_delta = NULL`, `source = NULL`, `confidence = NULL`, và `unsized_reason` giữ nguyên
chẩn đoán của Winston:

| `unsized_reason` | n |
|---|---:|
| `CA_CONFOUNDED` | 143 |
| `NO_MOVE` | 134 |
| `MULTI_EVENT` | 94 |
| `NO_DATA` | 26 |
| `ISSUANCE_MATCH` | 8 |
| `SIGN_MISMATCH` | 6 |
| `OVER_CAP` | 2 |

⚠️ `NO_MOVE` **không** nghĩa là size = 0: trong control có 62 sự kiện size thật >0 mà OShares không
nhúc nhích (lớn nhất PVI 2020-05-06 = 7.590.400 CP). Đây là lý do cột để NULL và cơ chế
`TREASURY_UNSIZED` (report 09-17) phải giữ nguyên — nhóm này không thu nhỏ đủ để bỏ cờ đi.

## 4 — Vá lỗ hổng `SHARE_CODES` trong `final3.py`
`SHARE_CODES={ISS,DIV,AIS,MA}` bỏ sót `SUSP`/`NLIS`/`MOVE`. Trên tập ticker này, `SUSP` có **54
dòng** và `NLIS` **1 dòng** mang `shares_delta` ⇒ đúng cùng lớp confounder đã từng quy nhầm phát
hành thành "bán CP quỹ" (ca VPB 1,19 tỷ CP / TPB 100tr CP).

Bản vá nằm ở `patch/final3.py` (bản sao — **không sửa file trong thư mục của Winston**).
Chạy lại toàn bộ: **33 ca suy được không đổi một ca nào** (diff tập kết quả = ∅), control vẫn
13/131 suy được, 76,9% khớp chính xác. ⇒ Vá này là **no-op trên batch hiện tại**, giá trị của nó
là bịt lỗ cho batch tương lai — đúng như dispatch dự đoán.

## 5 — Kiểm chứng
- **Selfcheck hermetic** `treasury_share_events_selfcheck.py`: **110/110 PASS**, 0 lần chạm BQ
  (mọi fixture bịa trong file). Chạy lại dưới `env -u TZ`, `TZ=America/New_York`, `TZ=UTC`:
  110/110 cả 3. Fixture tái tạo đúng hai ca thật của B1 — `NDN` (2 dòng vendor giống hệt cách 1
  ngày) và `CTD` (inferred + vendor cách 2 ngày, khác tier) — assert `SUM` trên dòng canonical
  bằng đúng quy mô một giao dịch (−1.000.000 và −2.000.000), cộng 3 fixture **âm tính**: `HWS`
  (cùng số lượng cách 274 ngày → KHÔNG gộp), `GDT` (gần ngày nhưng lệch 65,6% → KHÔNG gộp), `CHN`
  (chain guard 3 dòng ×10 ngày).
- **Mutation test** `mutation_test.py`: **32/32 killed**, gồm đúng những lỗi đắt nhất —
  không lật dấu (M01/M02), UNSIZED nội suy thành 0 (M04), trộn SIBLING vào VENDOR (M05), nâng tier
  suy luận lên `high` (M06/M07), `confirmed_asof = public_date` tức PIT leak (M08), bỏ recompute và
  tin thẳng số Winston (M11), nạp cả ca đã bị từ chối (M15), id bỏ `action_type` (M16). **9 mutation
  mới của B1/N1**: M24 tắt hẳn luật dedup · M25 canonical chọn tier ít tin nhất · M26 bỏ ngưỡng
  ngày · M27 bỏ ngưỡng lệch giá trị · M28 chain thay vì neo · M29 đánh dấu cả nhóm là canonical ·
  M30 kéo UNSIZED (delta NULL) vào dedup · M31 mất `inferred_window_days` · M32 hardcode window
  1 quý. Cả 9 đều bị giết.
- **Đối soát số**: 128+3+33+413 = 577 = số sự kiện đo thẳng bằng `GROUP BY` trên BQ. id duy nhất
  577/577. Bất biến `UNSIZED ⟺ delta NULL` và `confirmed_asof chỉ trên OSHARES_DELTA_INFERRED`
  được assert trên chính output dry-run, không chỉ trên fixture.

## 6 — Còn lại trước khi ghi BQ thật (KHÔNG tự quyết)
1. **Duyệt DDL** `schema.sql` (chưa chạy). Không partition (577 dòng / ~500 ngày ⇒ partition DAY
   sinh ~500 phân vùng 1 dòng); cluster `ticker`.
2. **Entry `kb/data_registry/`** — §9 bắt buộc trước khi bất kỳ code nào wire vào. Đã đặt ĐÚNG
   vị trí nhóm: `kb/data_registry/price-volume/treasury_share_events.md.proposed`
   (**`price-volume/`**, cạnh `treasury_news_buyback.md` — bản nháp trước ghi sai là
   `corporate-actions/`, thư mục đó không tồn tại). §13 ⇒ 4 file `kb/` cần sửa đều để dạng
   `.proposed`, chờ Mike `diff` rồi `mv`:
   `price-volume/treasury_share_events.md.proposed` (entry mới) ·
   `price-volume/index.md.proposed` (thêm 1 dòng điều hướng) ·
   `price-volume/treasury_news_buyback.md.proposed` (link chéo ngược + bổ sung bẫy "một giao dịch,
   hai ngày công bố" mà entry đó chưa ghi) · `CHANGELOG.md.proposed` (1 mục biên tập).
3. **Freshness check (§14)** — chỉ cần nếu sau này chuyển sang recurring. One-time thì cặp
   producer→consumer chưa tồn tại; nếu `oshares_live` đọc bảng này thì phải có gate `loaded_at`.
4. **2 dòng MANUAL_FILL VRE/SRF trong `corporate_action`: không đụng** (theo chỉ đạo). Ghi nhận cả
   2 đều rơi vào nhóm Winston không resolve được ⇒ bảng này **không** tái tạo được chúng.
5. Chưa có consumer nào đọc bảng. Tiêu thụ trong `oshares_live` là việc riêng, điều kiện mở lại của
   quyết định 09-08 vẫn đứng (chưa có case đổi quyết định đầu tư).

## Artifact
`build_treasury_share_events.py` (loader) · `treasury_share_events_dryrun.csv` (577 dòng) ·
`schema.sql` (DDL đề xuất, chưa chạy) · `treasury_share_events_selfcheck.py` · `mutation_test.py` ·
`patch/final3.py` (+ output `*_patched.csv`) ·
`inputs/` (snapshot artifact của Winston job _052425 để tái lập độc lập).
4 file `.proposed` nằm trong `kb/data_registry/` (xem §6 mục 2), không còn ở
thư mục research này.

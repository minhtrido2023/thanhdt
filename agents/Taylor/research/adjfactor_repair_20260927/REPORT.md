# Corp-action back-adjust: sửa 3 report đang bị chặn + Layer 2 lâu dài

**Job** `Taylor_20260927_131827` · 2026-09-27 · Taylor (Quant)
Tiếp nối prototype `../self_computed_adjfactor_20260927/` (Layer 1 detect, user duyệt 11:14 ICT).
Chỉ đạo user 20:15 ICT: *"corp action đều có đủ thông tin sự kiện nên hệ thống có thể tự kiểm tra
không phụ thuộc bq admin… nếu không chắc chắn, để Winston làm 1 vòng tìm kiếm dữ liệu để xác định"*.

Artifact: `verify_repair.py` + `confirmed.json` (nhân chứng `ticker_1m`) ·
`verify_fiinx.py` + `confirmed_fiinx.json` + `fiinx_witness.csv` (nhân chứng FiinX/FiinGroup).
Code Layer 2: branch `wire/close-repair-layer2-20260927`, commit `fb71a08d` (repo NGOÀI).

---

## TL;DR

1. **Điểm chặn THẬT hẹp hơn nhiều so với 15 mã**: `report_return_gate.paper_entry_gate` chỉ chặn
   vì **FPT**, ở 2 vị thế sổ paper (`alphalens` asof 06-30, `converge` asof 06-26). GAS/VPB không
   nằm trong sổ paper nào ⇒ không chặn gì. Cổng chặn 3 phiên: 09-23, 09-24, 09-25.
2. **FPT đã được XÁC NHẬN bởi HAI nguồn độc lập**: hệ số đúng là **1,100000**. `ticker_1m` lệch
   0,0055%; FiinX (FiinGroup) lệch 0,0010%.
3. **12/15 mã được xác nhận trong biên 0,15%**; 2 mã thêm (E29, V12) xác nhận riêng bởi FiinX;
   **1 mã KHÔNG xác nhận được** (VFR — cả ba nguồn lệch nhau) ⇒ item cho Winston.
4. **KHÔNG có cách backfill 1-lần nào an toàn.** Nguồn cổng đọc là `data/bq_cache/ticker/2026.parquet`
   (bản gương của BQ, `sync_bq_cache_daily.sh` ghi lại mỗi 23:45). Ghi đè nó ⇒ (a) bị xoá ở lần
   sync kế tiếp, (b) đổi dữ liệu âm thầm cho MỌI consumer khác, (c) bản gương không còn là bản
   gương. Ghi thẳng `tav2_bq.ticker` ⇒ tranh chấp với ETL ngoài. Cả hai đều là đúng thứ §8/§9 cấm.
   ⇒ Đường duy nhất đúng là **Layer 2** (Phần B) — đã code xong, đo xong, **chưa wire**.
5. **Vendor KHÔNG tự lành qua cuối tuần.** Chạy lại `audit_week.py` 20:30 ICT 27-09: y nguyên
   15 BROKEN / 0 OK / 9 UNCOMPUTABLE, không đổi một mã nào so với 03:49 sáng cùng ngày.

---

## PHẦN A — xác nhận độc lập, từng mã

### A.1 Tại sao cần nhân chứng thứ hai, và tại sao `ticker_1m` MỘT MÌNH là không đủ

`ticker_1m` do **cùng ETL** ghi trên một cửa sổ khác, nên nó chỉ là nhân chứng **một phần**: đo
được rằng nó mang **đúng cùng lỗi** trên phần đầu cửa sổ của chính nó. FPT trong `ticker_1m`
(08-26 → 09-25): đã điều chỉnh ở 09-08..09-18 (r≈1,0999) nhưng **CHƯA** ở 08-26..09-07 (r=1,0).

Vòng đo đầu tiên của tôi đã trộn hai loại row đó vào một phép so ⇒ báo **14/15 WITNESS_DISAGREES**
với dev đúng bằng cả hệ số (FPT −9,09%). Đó là **lỗi của phép đo, không phải kết quả**: một row
còn ở hệ tiền-sự-kiện không phải ý kiến thứ hai, nó là bản sao của row đang bị xét. Sau khi chỉ
tính những row mà `Price/Close` của CHÍNH nhân chứng đã bằng `r_pred`: **12 CONFIRMED / 0 DISAGREE
/ 3 NO_SECOND_SOURCE**. (Hệ số là HẰNG SỐ giữa 2 ex-date, nên 3-5 phiên được chứng kiến là đủ để
ghim nó — không cần chứng kiến toàn bộ 73 phiên hỏng.)

### A.2 Nhân chứng thứ ba: FiinX (FiinGroup) — thực sự độc lập

FiinX **không** thuộc chuỗi cafef/VCI nuôi `tav2_bq`, nên đây là nguồn độc lập theo nghĩa quan
trọng. Hai điều kiện tiên quyết được cưỡng chế trước khi một row FiinX được phép xác nhận hay
phản bác (nếu không, artifact của FiinX bị đọc thành phán quyết về công thức của ta):

- **P1** — `close` thô của FiinX phải TRÙNG `tav2_bq.ticker.Price`. Đo: đúng **44/44 row**, không
  row nào bị loại vì P1. Ghi lại vì một lần chạy sau mà P1 vỡ thì không được so tiếp.
- **P2** — hệ số ngụ ý của chính FiinX (`raw/adj`) phải là một back-adjustment hợp lệ: ≥ 1 và
  **không tăng** theo thời gian. 5 row bị loại: `BTD 09-17` có adj 14.550,95 **cao hơn** raw
  14.500 (r=0,9965 < 1, bất khả); `AMS 09-18` hệ số **tăng** 1,05254 → 1,05962 trên raw phẳng
  7.400; `VFR 09-16/17/18` tăng tới 1,111111.

### A.3 Kết quả — 15 mã BROKEN, cohort ex-date 2026-09-19…09-25

| mã | hệ số đúng (`r_pred`) | `ticker_1m` (n phiên) | FiinX (n row) | kết luận |
|---|---:|---|---|---|
| **FPT** | **1,100000** | ✅ 0,0055% (5) | ✅ 0,0010% (3) | **XÁC NHẬN ×2** |
| GAS | 1,029036 | ✅ 0,0035% (5) | ✅ 0,0017% (2) | XÁC NHẬN ×2 |
| VPB | 1,260410 | ✅ 0,0164% (5) | ✅ 0,0010% (2) | XÁC NHẬN ×2 |
| HTL | 1,096618 | ✅ 0,0234% (5) | ✅ 0,0006% (2) | XÁC NHẬN ×2 |
| PGD | 1,046083 | ✅ 0,0169% (3) | ✅ 0,0049% (2) | XÁC NHẬN ×2 |
| PHC | 1,135135 | ✅ 0,1421% (5) | ✅ 0,0054% (2) | XÁC NHẬN ×2 |
| VCC | 1,111111 | ✅ 0,0000% (4) | ✅ 0,0000% (2) | XÁC NHẬN ×2 |
| VTB | 1,084746 | ✅ 0,0377% (4) | ✅ 0,0027% (2) | XÁC NHẬN ×2 |
| BTD | 1,062500 | ✅ 0,0259% (3) | ✅ 0,0025% (1) | XÁC NHẬN ×2 |
| E29 | 1,059524 | — không phủ | ✅ 0,0021% (1) | XÁC NHẬN ×1 (FiinX) |
| V12 | 1,060606 | — không phủ | ✅ 0,0045% (1) | XÁC NHẬN ×1 (FiinX) |
| AMS | 1,042254 | ✅ 0,0000% (4) | ✗ P2 / +0,99% | **1 nguồn — xem A.4** |
| DRI | 1,072464 | ✅ 0,0524% (5) | ✗ +0,34% | **1 nguồn — xem A.4** |
| TVN | 1,034091 | ✅ 0,0396% (5) | ✗ +0,27% / −0,40% | **1 nguồn — xem A.4** |
| **VFR** | 1,063830 *(nghi)* | ✗ không có row dùng được | ✗ không nhất quán | **KHÔNG XÁC NHẬN** |

Ngưỡng 0,3% là sàn chính xác đã đo của phương pháp (prototype §5.4: DXG mang dư −0,17% không giải
thích được trên 95 phiên) — không phải 0,1%.

### A.4 Ba mã một-nguồn (AMS, DRI, TVN) — không chặn gì, nhưng KHÔNG tự chốt

`ticker_1m` khớp rất chặt (0,000% / 0,052% / 0,040% trên 4-5 phiên) trong khi FiinX lệch
0,27%-0,99%. Bằng chứng nghiêng về ta: chuỗi adjusted của FiinX cho đúng nhóm mã mỏng này **tự
mâu thuẫn** — AMS hệ số ngụ ý TĂNG theo thời gian trên một raw phẳng, điều không back-adjustment
nào làm được. Nhưng "nguồn kia có vẻ tệ hơn" không phải xác nhận. Ba mã này **không nằm trong sổ
paper nào và không chặn report nào**, nên không cần chốt hôm nay ⇒ chuyển thành item Winston
(mức thấp), KHÔNG đoán.

### A.5 VFR — ca "không chắc chắn" đúng nghĩa, cần Winston

Sự kiện: `DIV` 600đ/cp, ex-date 2026-09-21, `executed`. Ba nguồn cho ba đáp số:

| nguồn | hệ số | ghi chú |
|---|---:|---|
| ta (`r_pred`) | 1,063830 | = 10.000 / 9.400; raw phiên cum cuối 09-18 = 10.000 |
| BQ vendor (`r_obs`) | 1,066253 (09-15..17) · 1,066098 (09-18) | vendor CÓ điều chỉnh, nhưng khác ta |
| FiinX | 1,073519 → 1,065219 → 1,066667 → 1,111111 | **tăng** theo thời gian ⇒ không hợp lệ |

Thêm một dấu hiệu dữ liệu hỏng: `tav2_bq.ticker` VFR **2026-09-22** có `Close`=9.000 > `Price`=8.900
(r = 0,988889) — hệ số back-adjust không thể < 1.

### A.6 Vì sao KHÔNG backfill tay được (và đó là câu trả lời, không phải sự né tránh)

Chuỗi đọc của cổng: `report_return_gate.paper_entry_gate` → `paper_entry_adjust.adjust_entries`
→ `_fetch_rows` → **duckdb trên `data/bq_cache/ticker/*.parquet`**. Ba đường và lý do bác từng đường:

| đường | vì sao KHÔNG |
|---|---|
| sửa `bq_cache/ticker/2026.parquet` | bản gương của BQ, bị ghi lại lúc 23:45 mỗi đêm ⇒ sửa sống được <1 ngày; và đổi âm thầm dữ liệu cho mọi consumer khác của cache |
| ghi `tav2_bq.ticker` | bảng do ETL NGOÀI upsert (registry: `corporate_action_bq.md`, `ticker`), ta tranh chấp writer |
| nới cổng cho FPT | đổi logic cổng — đúng thứ dispatch cấm, và mất luôn phép kiểm cho mọi ca sau |
| **bảng/kênh bên cạnh + consumer LEFT JOIN** | ✅ đúng tiền lệ `update_shares_live.py` → `tav2_bq.shares_outstanding_live` ("writes ONLY to a NEW table. NEVER mutates ticker") — nhưng consumer ở đây đọc parquet cục bộ, nên "kênh bên cạnh" = một lớp code ⇒ **chính là Layer 2** |

Nên Phần A không kết thúc bằng một lần ghi tay; nó kết thúc bằng **giá trị đã xác nhận** để
Layer 2 (hoặc bq_admin) dùng, và bằng kết luận rằng đường an toàn duy nhất là Layer 2.

---

## PHẦN B — Layer 2 REPAIR (code xong, đo xong, **CHƯA WIRE**)

Branch `wire/close-repair-layer2-20260927`, commit **`fb71a08d`** (repo ngoài `/home/trido/thanhdt`).
File: `close_repair.py` (mới), `close_repair_selfcheck.py` (mới), `paper_entry_adjust.py` (nối).

### B.1 Điểm nối — đọc code để xác định, không đoán

`paper_entry_adjust._fetch_rows` là **nơi duy nhất** một `Close` của vendor đi vào module, và
`factor_terp = Close/Price` — thứ mà phép kiểm T1 của cổng và `entry_adj` của báo cáo đều dựng
trên đó — được tính ngay sau nó. `dividend_adjusted_return.py` KHÔNG phải điểm nối: nó chỉ đọc
bước tỉ số CỤC BỘ tại ex-date và bước đó vẫn đúng (prototype đã verify).

### B.2 Hành vi đo thật trên 13 vị thế sổ paper (2026-09-27, BQ tới 09-25)

| cờ | kết quả cổng | FPT | 11 vị thế còn lại |
|---|---|---|---|
| **OFF** (mặc định) | **2 CHẶN** | terp=1,000000 `[UNCHANGED]` src=vendor | — |
| **ON** (`MIKE_CLOSE_REPAIR=1`) | **0 CHẶN** | terp=**0,909091** `[ADJUSTED]` src=**self_computed** | **byte-identical** với lần OFF, src=vendor |

Control âm (11 vị thế không đổi, gồm MBB có quyền mua) là phần quan trọng nhất của phép đo: một
lớp sửa mà "sửa" cả những mã đang đúng thì vô giá trị.

### B.3 Ba quy tắc load-bearing, mỗi cái có mutation guard riêng

- **Sự kiện CÙNG NGÀY cộng trong công thức giá tham chiếu của sở, không nhân rời.**
  `f = (1+q_total)·P_cum/(P_cum − D_total)`. GEX 2026-05-05 (thưởng 20% + cổ tức CP 25%): 1,450
  khớp vendor 1,450191, còn 1,20×1,25 = 1,500 sai −3,32%. DGC 2026-09-14 (3.000 + 5.000 trên raw
  46.750): 1,206452 khớp 6 chữ số, product cho 1,196544 sai +0,83%.
- **Band guard NÂNG band vào hệ thô bằng row láng giềng** — `High`/`Low` ở hệ đã điều chỉnh,
  `Price` thì không; so trực tiếp sẽ gắn cờ mọi row lành trước sự kiện. Và không được nâng bằng
  chính row đang nghi, vì ở đó `Price/Close` đúng là đại lượng đã hỏng.
- **Cửa sổ ex-date kết thúc ở CHUỖI GIÁ (`series_max`), không ở hôm nay** — một ex-date mà chuỗi
  giá chưa chạm tới thì không thể có trong `Close` của vendor; tính nó vào sẽ **bịa ra lỗi** trên
  một row lành.

### B.4 Fail-closed ở đâu (đúng README mục 6: "emit nothing")

Một ex-date trong cửa sổ không tính được hệ số ⇒ **không phát sinh gì**, `adj_source` giữ
`"vendor"`, cổng hiện hành tiếp tục chặn. Các ca: quyền mua (subscription price không phải một
cột; `ref_price` NULL trên cả 2.418 dòng từ 2025-01-01) · `exercise_ratio`/`value_per_share` không
parse được hoặc ≤ 0 · `Price` phiên cum cuối trượt band ffill · không có phiên cum trong cửa sổ.
Thêm hai lối từ chối chủ động: vendor khớp trong 0,3% ⇒ giữ nguyên; `r_obs > r_pred` (vendor điều
chỉnh NHIỀU hơn sự kiện ta có) ⇒ nghi **bảng của ta** thiếu sự kiện ⇒ không sửa giá.

### B.5 Selfcheck

`close_repair_selfcheck.py`: **48 assertion × 15 lần chạy = 720, 0 fail; 14/14 mutation bị giết.**
PASS đồng nhất dưới `python3` 3.10, `$DNA_PYEXE` 3.12, `env -u TZ`, `TZ=America/New_York`, và khi
`MIKE_CLOSE_REPAIR=1` đã có sẵn trong env. Offline hoàn toàn (không cần BQ, không cần parquet).
`paper_entry_adjust.py --selfcheck` 21/21 PASS khi cờ TẮT ⇒ mặc định là trơ.

Hai lỗi phép đo tự bắt trong lúc code: `Repair()` nhận trùng kwarg `close`; và một chỗ
`except Exception as e: continue` nuốt mất thông điệp parser (đúng lớp lỗi §29) — đã sửa thành
mang nguyên văn lỗi lên `repair_note`. Đã GỠ một nhánh `r_pred < 1` **không thể với tới** (mọi
`f` do `group_factor` trả đều đã được chứng minh > 1) — nó sống sót mọi mutation đúng vì không gì
chạm được vào nó (§2).

### B.6 ⚠️ CHẶN TRƯỚC KHI WIRE — một selfcheck CŨ đang xanh vì chính lỗi vendor

`paper_entry_adjust._selfcheck` **case 8** (dòng 593) hardcode FPT/ACB/HDB là *"không có
corp-action sau entry"*. **FPT đã GDKHQ 2026-09-21 ⇒ tiền đề đó SAI từ ngày đó.** Case 8 hiện xanh
chỉ vì vendor chưa điều chỉnh (nên `entry_adj == entry_price`); nó sẽ ĐỎ **cả khi vendor backfill
đúng**, không riêng khi bật cờ này.
Đo thật: `MIKE_CLOSE_REPAIR=1 python3 paper_entry_adjust.py --selfcheck` → `FAILED 1/21` ở đúng
case 8. **Tôi KHÔNG tự sửa** — sửa một test để bản vá của mình xanh là đúng thứ reviewer phải
nghi. Đề xuất: case 8 phải tự kiểm TIỀN ĐỀ (mã này thực sự không có sự kiện điều-chỉnh-giá sau
`asof`) rồi mới khẳng định hệ quả, thay vì hardcode danh sách mã.

### B.7 Cổng để bật

1. **quant-skeptic CONFIRMED** trên Layer 2 (đang chạy, xem bus).
2. Vá case 8 (B.6).
3. User duyệt — mọi con số nó đổi là tỉ suất hướng nhà đầu tư (§21).
4. Bật bằng `MIKE_CLOSE_REPAIR=1` trong env của cron `newdeals_daily_report`, KHÔNG bật toàn hệ.

---

## Item đề xuất cho Winston (KHÔNG tự dispatch — để Mike/user quyết)

| # | mã | câu hỏi cụ thể cần xác định | mức |
|---|---|---|---|
| W1 | **VFR** | Giá tham chiếu (giá điều chỉnh) do sở công bố cho VFR ngày GDKHQ **2026-09-21** là bao nhiêu, và cổ tức thực trả có đúng **600đ/cp** hay còn cấu phần thứ hai? Ta ra 1,063830 (raw cum 09-18 = 10.000), BQ vendor ra 1,066253, FiinX không nhất quán. Kèm: VFR niêm yết sàn nào (biên độ khác nhau)? | **cao** — mã duy nhất không xác nhận được |
| W2 | VFR | `tav2_bq.ticker` VFR **2026-09-22**: `Close`=9.000 > `Price`=8.900 (r=0,988889 < 1, bất khả). Là lỗi ghi của ETL hay `Price` bị ffill? | cao |
| W3 | AMS, DRI, TVN | Chuỗi **adjusted** của FiinX cho mã mỏng có dùng làm nhân chứng được không? Bằng chứng nghi ngờ: AMS hệ số ngụ ý TĂNG 1,05254 (09-17) → 1,05962 (09-18) trên raw phẳng 7.400; BTD 09-17 có adj > raw. Nếu không, cần nguồn thứ ba nào cho nhóm mã dưới ngưỡng thanh khoản? | thấp — không chặn gì |
| W4 | 9 mã UNCOMPUTABLE (BVB, DWS, HC1, LPT, PDB, SEA, TMS, TNC, XHC) | Có nguồn nào lấy được **giá phát hành quyền mua** (subscription price) không? Đây là lỗ lớn nhất: `ref_price` NULL trên cả 2.418 dòng `corporate_action` từ 2025-01-01, nên Layer 2 **không bao giờ** sửa được nhóm này. | cấu trúc |
| W5 | 15 mã BROKEN | Vendor **không** tự lành qua cuối tuần (đo lại 20:30 ICT 27-09: y nguyên 15/0/9). bq_admin có kế hoạch rewrite toàn cửa sổ không, và khi nào? | cao — quyết định bật Layer 2 hay chờ |

## Tái lập

```bash
cd mike/agents/Taylor/research/adjfactor_repair_20260927
python3 verify_repair.py          # nhân chứng ticker_1m  -> confirmed.json
python3 verify_fiinx.py           # nhân chứng FiinX      -> confirmed_fiinx.json
cd ../self_computed_adjfactor_20260927 && python3 audit_week.py --ex0 2026-09-19 --ex1 2026-09-25

# Layer 2 (worktree repo NGOÀI)
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-closerepair-2709/WorkingClaude
python3 close_repair_selfcheck.py                        # 720 assertion, 14/14 mutation
python3 paper_entry_adjust.py --selfcheck                # 21/21 (cờ TẮT)
MIKE_CLOSE_REPAIR=1 python3 paper_entry_adjust.py --selfcheck   # FAILED 1/21 — case 8, xem B.6
```

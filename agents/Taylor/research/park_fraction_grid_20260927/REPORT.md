# Park-fraction custom30V (NEUTRAL) — lưới 12 mức trên bản CANONICAL đã sửa 2 chân

Job `Taylor_20260927_064747` · cây đo **main @`f2cfb124`** · **paper-only, `trading_rules.json`
KHÔNG bị đụng** · PREREG (+2 amendment) ở `PREREG.md`, viết trước khi chạy.

---

## KẾT LUẬN — MỘT SỐ: **30 %**

> **`neutral_parking.default_park_of_idle_pct` = 0,30** (hiện LIVE 0,80).
>
> **Lý do, đúng theo hàm mục tiêu đã khai báo trước:** 30% là mức **tối đa Calmar (1,630)** trong
> tập ứng viên còn lại sau ràng buộc rủi ro — và ràng buộc đó (bootstrap 5th-pct MaxDD không xấu
> hơn park=0 quá 2,0pp, tức không dưới **−26,0%**) **loại toàn bộ mọi mức ≥ 40%**, gồm cả 80% đang
> chạy (5th-pct MaxDD **−32,0%** = xấu hơn park=0 **8,0pp**).
>
> **Khoảng không phân biệt được:** ở ngưỡng phân giải đã khai báo trước (0,03 Calmar) **không mức
> nào khác không-phân-biệt-được với 30%** (gần nhất là 40% với 1,530, cách 0,10 — và 40% cũng đã bị
> ràng buộc DD loại). Nhưng **leave-one-year-out** cho biết khoảng thực tế là **20–30%**: 30% thắng
> **12/13** lần bỏ-một-năm, lần duy nhất đổi là bỏ **2020** → thắng thành 20%. Không lần nào thắng
> ở mức ≥ 40%. Vậy con số đề xuất là **30%**, dải hợp lý **20–30%**, và **≥ 40% bị loại có căn cứ**.

**Điều phải nói thẳng, vì nó ngược hẳn dự đoán vào job này:** bis §7 (4 điểm: 0/70/80/85%) gợi ý
Calmar **đơn điệu giảm** ⇒ "tối ưu risk-adjusted = không park". Làm dày lưới cho thấy điều đó **SAI**:
có **ĐỈNH NỘI THẬT ở 30%**, và ở dải 0→30% parking **tốt hơn trên CẢ HAI chiều cùng lúc** (CAGR
22,37→23,43% *và* MaxDD −16,1→**−14,4%**). Tức câu trả lời không phải "bỏ parking", mà **"parking
đúng, nhưng đang đặt to gấp ~2,7 lần mức tối ưu"**.

---

## 1. Bảng tổng — 12 mức, cùng một lệnh pin, đổi ĐÚNG một biến `PARK_STATES`

`self-check BAL+LAG = 0 VND` **12/12 leg** (+2 control) · `EXIT=0` 14/14 · dòng log
`parking policy (cash_etf_states) {3: x}` khớp `x` ở **12/12** (assert trong `summary.py`, không
đọc bằng mắt — chống lại đúng cái no-op im lặng đã cắn job `_043541`).

| park % | CAGR | Sharpe | MaxDD | **Calmar** | Final NAV | IS 14-19 | OOS 20+ | boot CAGR 5th | **boot MaxDD 5th** | boot SR 5th | park %NAV thật | drag thuế CT | CAGR sau haircut | cổng DD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--|
| **0** | 22,37% | **1,95** | −16,1% | 1,390 | 618,35B | 20,30% | 24,23% | 15,2% | **−24,0%** | 1,34 | 0,00% | 0,000pp | 22,370% | ✅ |
| 10 | 22,75% | 1,94 | −15,7% | 1,450 | 642,68B | 20,11% | 25,16% | 15,3% | −24,3% | 1,33 | 3,49% | 0,008pp | 22,742% | ✅ |
| 20 | 22,76% | 1,90 | −15,2% | 1,500 | 643,55B | 20,11% | 25,19% | 15,1% | −24,9% | 1,29 | 6,99% | 0,015pp | 22,744% | ✅ |
| **30 ← ĐỀ XUẤT** | **23,43%** | 1,88 | **−14,4%** | **1,630** | 688,77B | 20,07% | 26,56% | **15,6%** | **−25,1%** | 1,27 | 10,48% | 0,023pp | **23,407%** | ✅ |
| 40 | 23,03% | 1,80 | −15,1% | 1,530 | 661,56B | 19,86% | 25,97% | 14,9% | −26,4% | 1,18 | 13,95% | 0,031pp | 22,999% | ❌ |
| 50 | 24,15% | 1,81 | −16,6% | 1,450 | 740,30B | 19,73% | 28,32% | 15,8% | −27,4% | 1,19 | 17,44% | 0,039pp | 24,111% | ❌ |
| 60 | 24,32% | 1,75 | −17,7% | 1,370 | 753,06B | 19,54% | 28,84% | 15,6% | −28,9% | 1,13 | 21,06% | 0,047pp | 24,273% | ❌ |
| 70 | 24,42% | 1,69 | −18,8% | 1,300 | 761,11B | 19,31% | 29,29% | 15,5% | −30,3% | 1,07 | 24,50% | 0,055pp | 24,365% | ❌ |
| 75 | 24,66% | 1,68 | −19,3% | 1,280 | 778,96B | 19,24% | 29,83% | 15,5% | −31,1% | 1,05 | 26,18% | 0,059pp | 24,601% | ❌ |
| **80 ← LIVE** | **24,95%** | 1,66 | −19,8% | **1,260** | 802,27B | 19,04% | 30,62% | 15,6% | **−32,0%** | 1,03 | 28,06% | 0,064pp | 24,887% | ❌ |
| 90 | 24,81% | 1,58 | −20,8% | 1,190 | 790,76B | 18,79% | 30,59% | 15,0% | −34,7% | 0,94 | 31,55% | 0,071pp | 24,739% | ❌ |
| 100 | 24,93% | 1,52 | −20,8% | 1,200 | 800,67B | 18,04% | 31,63% | 15,0% | −36,1% | 0,89 | 36,72% | 0,083pp | 24,847% | ❌ |

Đường cong: `park_grid_curves.png` (Calmar theo x · MaxDD thực + 5th-pct theo x + đường trần ràng
buộc). Bảng máy đọc: `grid_summary.csv`. Bản in gốc: `grid_summary.txt`.

**Cổng NEO (PREREG §6) — cả 3 mốc đều giải quyết được, có md5:**
- `x=0` → **22,37% / 1,95 / −16,1% / 1,39**, khớp KHÍT bis §7.
- `x=0,7` → CSV md5 **`2f9c3702…`**, **trùng byte** với leg `wexd2_new_exdate` của ticket 1.
- `x=0,8` ban đầu **FAIL** cổng (24,95% vs bis §7 24,66% = **+0,29pp** > trần 0,05pp). Đã phân tách
  bằng **control, không bằng suy luận** (AMENDMENT 2): chạy `BASKET_OSHARES_STEP=quarter` →
  `parkgrid_070q` md5 **`3f836927…`** = **byte-identical** `c30vmain`, `parkgrid_080q` md5
  **`a90e87c0…`** = **byte-identical** `c30vpark80`. ⇒ **+0,29pp là biên THẬT của ticket 1 tại
  x=0,8**, không phải biến lạ. Biên ticket 1 **không hằng số theo x** (+0,04pp @70%, +0,29pp @80%) —
  hợp lý vì nó chỉ tác động qua chân weight của rổ, mà tỷ trọng rổ tăng theo x.

## 2. Ràng buộc rủi ro — cái thực sự quyết định

Bootstrap (`bootstrap_nav.py`, circular block L=21, B=4000, seed 12345, quy ước LỊCH sau FAIL-F):
5th-pct MaxDD tại park=0 = **−24,0%** ⇒ trần cho phép **−26,0%**.

| park % | 0 | 10 | 20 | **30** | 40 | 50 | 60 | 70 | 75 | **80** | 90 | 100 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| boot MaxDD 5th | −24,0 | −24,3 | −24,9 | **−25,1** | −26,4 | −27,4 | −28,9 | −30,3 | −31,1 | **−32,0** | −34,7 | −36,1 |
| qua cổng 2,0pp | ✅ | ✅ | ✅ | **✅ (1,1pp)** | ❌ 2,4 | ❌ 3,4 | ❌ 4,9 | ❌ 6,3 | ❌ 7,1 | **❌ 8,0** | ❌ 10,7 | ❌ 12,1 |

**5th-pct MaxDD là đại lượng đơn điệu và nhạy nhất của cả lưới** (−24% → −36%, dải 12pp), trong khi
5th-pct CAGR gần như PHẲNG (14,9–15,8%, dải 0,9pp trên cả lưới). Đọc thẳng: **tăng park gần như
không mua thêm được gì ở chân CAGR khi đã tính bất định lấy mẫu, nhưng mua thêm rất nhiều đuôi DD.**

## 3. "CAGR mua được mỗi 1pp DD" — biên giữa các mức kề nhau

| bước | ΔCAGR | Δ\|MaxDD\| | đọc |
|---|--:|--:|---|
| 0 → 10% | +0,38pp | −0,40pp | **MIỄN PHÍ** (CAGR tăng *và* DD tốt hơn) |
| 10 → 20% | +0,01pp | −0,50pp | **MIỄN PHÍ** |
| 20 → 30% | +0,67pp | −0,80pp | **MIỄN PHÍ** |
| 30 → 40% | −0,40pp | +0,70pp | **XẤU HAI CHIỀU** |
| 40 → 50% | +1,12pp | +1,50pp | 0,75pp CAGR / 1pp DD |
| 50 → 60% | +0,17pp | +1,10pp | 0,15 |
| 60 → 70% | +0,10pp | +1,10pp | **0,09** (rẻ nhất cả lưới — mua DD gần như không lấy gì) |
| 70 → 75% | +0,24pp | +0,50pp | 0,48 |
| 75 → 80% | +0,29pp | +0,50pp | 0,58 |
| 80 → 90% | −0,14pp | +1,00pp | **XẤU HAI CHIỀU** |
| 90 → 100% | +0,12pp | 0,00pp | (DD bằng nhau) |

Tổng hợp 30% → 80% (chính là thay đổi đang đề xuất, đọc ngược): **giá của 80% so với 30%** =
+1,52pp CAGR, đổi bằng **5,4pp MaxDD thực** và **6,9pp đuôi DD 5th-pct**, **−0,37 Calmar**,
**−0,22 Sharpe** ⇒ **0,28pp CAGR cho mỗi 1pp MaxDD**.

## 4. Đỉnh 30% là THẬT hay NHIỄU — 3 kiểm tra đặt trước

**(a) Đơn điệu:** KHÔNG đơn điệu. Calmar 1,390 → 1,450 → 1,500 → **1,630** → 1,530 → 1,450 → …
→ 1,200. Có đỉnh nội ⇒ kích hoạt LOYO (§4c prereg).

**(b) Phân giải 0,03 Calmar:** khoảng cách 30% tới mức kề gần nhất = **0,100** (tới 40%) và
**0,130** (tới 20%) ⇒ **> 3× ngưỡng phân giải**, phân biệt được. Để so sánh: biên mà quyết định
08-04 dựa vào là **0,01** — nhỏ hơn 10 lần.

**(c) Leave-one-year-out** (bỏ toàn bộ phiên của từng năm lịch, nối chuỗi return, tính lại):
`loyo_020_030_040.log` (3 mức quanh đỉnh, đúng prereg) + `loyo_000_030_080.log` (bối cảnh 0/30/80).

| | thắng Calmar | số lần đổi so với full-sample |
|---|---|---|
| bộ {20, 30, 40}% | **30% thắng 12/13**, 20% thắng 1/13 (bỏ **2020**) | **1/13** ⇒ **≤1 ⇒ ĐỈNH ROBUST** (prereg: >1 = reshuffle-luck) |
| bộ {0, 30, 80}% | **30% thắng 12/13**, 0% thắng 1/13 (bỏ **2020**) | 1/13; **80% KHÔNG thắng lần nào** |

Cả 13 lần bỏ năm, mức thắng **luôn nằm ở 0–30%**, không lần nào ≥40%.

**(d) Cơ chế — vì sao đỉnh nằm đúng ở 30% (bổ sung, không nằm trong prereg nhưng phải công bố):**
`dd_episodes.txt` cho thấy **danh tính của MaxDD ĐỔI đợt tại 30→40%**:
- park ≤ 30%: đợt ràng buộc là **2019→24/03/2020** (Covid): −16,1% → −15,7 → −15,2 → **−14,4%**.
  Parking **cải thiện** đợt này vì suốt 2019 tiền nhàn rỗi ăn 0%/năm, park ăn return rổ ⇒ NAV đỉnh
  cao hơn, %DD nhỏ hơn.
- park ≥ 40%: đợt ràng buộc chuyển sang **05/04/2018→05/07/2018**: −13,9% (@30%) → −15,1 → −16,6 →
  −18,8 → **−19,8% (@80%)**. Đợt này parking **làm xấu** đơn điệu vì rổ bị phơi hoàn toàn.

⇒ 30% chính là **điểm giao của hai đợt cạnh tranh** = `argmin max(DD_2018, DD_2020)`. Đây là điểm
mạnh (giải thích được bằng cơ chế, không phải trùng hợp số) **và** là điểm yếu phải nói rõ: vị trí
chính xác của nó do **HAI sự kiện lịch sử đơn lẻ** định ra, nên **N hiệu dụng ≈ 2**, không phải một
đỉnh thống kê trơn. Đúng cái đó là lý do LOYO đổi thắng khi bỏ 2020, và là lý do **dải 20–30% mới
là kết luận, không phải riêng con số 30,0%**.

## 5. Haircut thuế cổ tức FAIL-D — áp số học, không đảo gì

`k = 5% thuế + 0,1% phí×(1−thuế) = 5,095%`; `drag = 1 − Π(1 − k·DY_kỳ·park_share_kỳ)^(1/yrs)`, với
`DY_kỳ` lấy nguyên 49 kỳ từ `part2/dy_by_rebal.csv` và **`park_share_kỳ` đo THẬT trên CSV của chính
leg đó** (`(bal_etf_ref+lag_etf_ref)/combined_nav`) — không giả định tỷ lệ tuyến tính theo x.
Script `park_haircut.py`, log `haircut_all.log`.
**Neo tính đúng đắn:** tại x=0,7 script cho `park_share` **0,2450** và drag **0,0552pp/năm**, khớp
`part2/nav_drag.txt` (0,2453 / 0,0552pp) ⇒ bản dựng lại độc lập trùng bản gốc.
Drag đơn điệu theo x (0,000 → 0,083pp/năm) nên **nó chỉ làm mức park cao XẤU THÊM một chút**; ở mức
đề xuất 30% drag chỉ **0,023pp/năm**. **Không mức nào đổi thứ hạng vì haircut.**
`park_share` thực tế: park knob 30% ⇒ rổ chỉ chiếm **10,5% NAV** trung bình toàn kỳ (knob 80% ⇒
28,1%) — knob là "phần TIỀN NHÀN RỖI", không phải phần NAV.

## 6. Walk-forward — cảnh báo ngược chiều, phải đọc kèm

IS(2014-19) **giảm đơn điệu** theo park (20,30% @0 → 19,04% @80 → 18,04% @100), OOS(2020+) **tăng
đơn điệu** (24,23% → 30,62% → 31,63%). Nghĩa là: **toàn bộ lợi ích CAGR của việc park NHIỀU chỉ nằm
ở OOS 2020+**, còn IS thì park nhiều luôn tệ hơn. Đây **không** phải "edge rớt OOS" (không có mức
nào rớt) nhưng là dấu hiệu đóng góp CAGR của park **tập trung vào một chế độ** (hậu-2020, trong đó
2021 +116% chi phối — xem LOYO: bỏ 2021 kéo CAGR mọi mức xuống ~17,5-17,8%). Mức 30% có **IS
20,07%** — gần như bằng park=0 (20,30%) — nên nó KHÔNG phụ thuộc vào chế độ hậu-2020 để đứng vững.

## 7. Giới hạn (bắt buộc công bố, PREREG §8)
- 12 leg **cùng một vintage** `bq_cache_asof20260729_postrestate`, cùng snapshot corp-action ghim
  `data/snapshots/corp_action_share_20260927.parquet`, cùng tham số fill chưa neo (trần 20%
  ADV/phiên — `kb/projects/lag-adv-filter-tracking.md`).
- **Một đường đi lịch sử duy nhất.** Bootstrap chỉ đo bất định LẤY MẪU trên chính phân phối đó,
  không mô hình hoá đổi chế độ ⇒ CI là **biên DƯỚI** của bất định thật.
- Vị trí đỉnh do 2 episode DD đơn lẻ định ra (§4d) ⇒ đọc là **dải 20–30%**, không phải điểm 30,0%.
- **Không đảo quyết định của user.** Đây là khuyến nghị paper-only; áp vào LIVE cần **user duyệt** +
  **quant-skeptic** (Mike chạy sau). `trading_rules.json` vẫn `0.8`, không đụng một byte.

## 8. Hai phương án trình user (theo yêu cầu dispatch)
Dispatch dự phòng cho trường hợp "Calmar đơn điệu giảm từ 0%" — **trường hợp đó KHÔNG xảy ra**, nên
hai phương án là:

**(a) Tối ưu risk-adjusted = 30%** (khuyến nghị): Calmar **1,630** (+0,37 so với LIVE), Sharpe 1,88
(+0,22), MaxDD **−14,4%** (tốt hơn 5,4pp), đuôi DD 5th-pct **−25,1%** (tốt hơn 6,9pp), CAGR
**23,43%** (mất 1,52pp so với LIVE 24,95%). Quy đổi thực tế (CLAUDE.md: −1,5%) ⇒ **≈21,9%/năm**.
Lưu ý: 30% **vượt** park=0 trên CẢ HAI chiều ⇒ không phải "bỏ parking", mà là "park nhỏ".

**(b) Mức park thấp nhất vẫn giữ CAGR ≥ 24,0%** (nếu user coi CAGR tuyệt đối là mục tiêu):
= **50%** (CAGR 24,15%; 40% chỉ được 23,03%). Giá phải trả so với (a): DD thực −16,6% (xấu thêm
2,2pp), đuôi DD 5th-pct **−27,4%** (xấu thêm 2,3pp, **vi phạm** ràng buộc prereg 2,0pp), Calmar
1,450 (−0,18). Nếu muốn giữ đúng ràng buộc rủi ro thì trần khả thi là **30%**, và mức cao nhất còn
qua cổng cũng là **30%** — tức (b) chỉ tồn tại khi user chủ động nới ràng buộc DD.

**Giữ 80% như hiện tại** vẫn là một lựa chọn hợp lệ của user, nhưng phải gọi đúng tên: nó mua
+1,52pp CAGR bằng +5,4pp MaxDD và +6,9pp đuôi DD, và **không thắng Calmar ở bất kỳ lần nào trong
13 lần leave-one-year-out**.

## 9. Artifact
- `PREREG.md` (+ AMENDMENT 1, 2) · `run_leg.sh` · `summary.py` · `park_haircut.py` · `loyo.py`
- 14 log leg `parkgrid_*.log` · 12 `bootstrap_parkgrid_*.log` · `haircut_all.log` · `isoos.txt`
- `grid_summary.csv` / `grid_summary.txt` · `park_grid_curves.png` · `dd_episodes.txt`
- `loyo_020_030_040.log` · `loyo_000_030_080.log`
- CSV: `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-*_wtnamecap_advprice_exp_parkgrid_*_univpit.csv` (14 file, tên non-canonical theo §8)

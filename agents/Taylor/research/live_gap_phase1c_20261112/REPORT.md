# GĐ1 vòng 3 — áp required_change lần 2 của quant-skeptic (job `Taylor_20261112_122855`, 12/11/2026)

> Thay §0.5–0.7 của `../live_gap_phase1b_20261112/REPORT.md` (bị REFUTED: mọi chân engine chạy park = 0 trong khi live chạy
> rổ custom30V park). Nhánh cô lập `research/live-gap-p1c-20261112` (worktree `wt-livegap-p1c-1112`, commit `c27fe6823` =
> `5512bfe3d` [vá mergesort] + 2 hook research mặc định TẮT: `PARK_SCHEDULE`, `TIEBREAK_SEED`). KHÔNG merge, không đổi
> production/cron/data canonical (`WorkingClaude/data/` có 0 file `exp_gap_c3`).
> **Số lần chạy engine: 24** = 20 chạy trọn hợp lệ (self-check cash-flow + NAV identity = 0 VND cả BAL lẫn LAG, mọi chân) +
> 4 chân cold đầu tiên BỎ (lỗi cấu hình của tôi: `BQ_LOCAL_CACHE` tương đối bị resolve theo `WORKDIR_8L` ⇒ engine rơi về BQ
> sống; log giữ ở `logs/bad_nocache/`). Không cấu hình nào được chọn theo kết quả ⇒ không có DSR/PBO.
> **N = MỘT cửa sổ 4 tháng, MỘT đường đi. Mọi kết luận dưới đây là kế toán của đường đi đó, không phải bằng chứng edge.**

## 0. Kết luận (chỉ phần đã đo)

1. **Khi engine nhận đúng lịch park live, DẤU GAP ĐẢO: live THẮNG engine 4,4–4,7pp** (trước đó, park = 0: live thua 2,1–3,9pp).
   | TK | LIVE | engine park=0 (cold … warm-live) | engine + lịch park live (cold … warm-live) | live − engine (park live) |
   |---|---|---|---|---|
   | SpaceX 01/07→11/11 | −3,862% | +0,016% … −0,818% | **−8,216% … −8,387%** | **+4,35 … +4,52pp** |
   | ZaloPay bot 06/07→11/11 | −2,609% | +0,029% … −0,490% | **−7,257% … −7,231%** | **+4,65 … +4,62pp** |
   So hurdle tiết kiệm PIT (GĐ0: 2,548% SpaceX, 2,455% ZaloPay): live −6,41 / −5,06pp; engine-park-live −10,76…−10,93 / −9,69…−9,71pp.
   Độ nhạy over-buy (chân `SXcold_psOB`: park 1,0 tới 06/07 thay 0,70): engine −8,44% ⇒ gap +4,58pp. Engine park bị chặn bởi
   tiền mặt (≤100% gross) nên KHÔNG mô hình hoá được 141% gross/margin 02–03/07; ước tính số học phần vượt 100%:
   0,41 × VNI(02/07→06/07, −1,22%) ≈ **−0,50pp (ước lượng)** thêm cho engine — cùng chiều, không đổi dấu.
2. **Lịch park dùng (đã xác minh, `data/trading_rules.json` + git):** 0,70 của idle pool (v2.1, từ go-live) → **0,80 từ 04/08**
   (đổi BUY rail 11:34 ICT, `neutral_parking.pending_engine_consistency`) → **0,30 từ 27/09** (commit `ae81bd47b`, CN ⇒ áp từ
   phiên 28/09) → **0,0 từ 01/10** 10:26 ICT (commit `b0e2c8110`). Engine: `PARK_SCHEDULE=2026-07-01:0.7,2026-08-04:0.8,
   2026-09-28:0.3,2026-10-01:0.0`, chỉ áp ở **state 3 = NEUTRAL** (`PARK_SCHEDULE_STATES=3`); DT5G = NEUTRAL cả 93/93 phiên
   của cửa sổ (đọc cột `state` ledger). Trước 01/07 chân warm vẫn park = 0 (đúng pin park0). Ngữ nghĩa engine: phân số của
   (tiền nhàn rỗi + rổ), mua sau khi deal BAL/LAG đã khớp, JIT bán rổ khi deal cần tiền — giống `_principle` của rule live.
3. **§0.6 viết lại — T7 là NEUTRAL_park + over-buy, KHÔNG phải "thời điểm vào vị thế".** Plan SpaceX 01/07 = rule
   `custom30V_parking_full_deploy` (23/23 lệnh park, ~938M, đích 93,8%), 02/07 thêm 11 lệnh park ~456M ⇒ `mtm_stock`
   1,40 tỷ / NAV 0,99 tỷ = **141% gross** (nav_history 02–03/07); 06/07 bán về 69,6%; tới 20/07 live 100% là park
   (CAPIT đầu tiên 21/07). Phân rã có park HAI PHÍA (`exposure_decomp3.md`, kỳ, phiên đầu bfill … zero):
   | | gap | β park | β tín hiệu | β disc | **β tổng** | **α-dư** |
   |---|---|---|---|---|---|---|
   | SpaceX vs engine park=0 (cold/warm) | −3,88 / −3,04 | −4,01…−4,49 | +1,24…+1,42 | −0,06 | −2,65…−3,30 | −1,06…+0,08 |
   | **SpaceX vs engine park live (cold/warm)** | **+4,35 / +4,52** | +2,51…+3,05 | −3,36…−3,98 | −0,06 | **−0,36…−1,53** | **+4,72…+6,06** |
   | ZaloPay vs engine park=0 | −2,64 / −2,12 | −3,63…−3,89 | +1,56…+1,66 | −0,07 | −2,05…−2,39 | −0,50…+0,18 |
   | **ZaloPay vs engine park live** | **+4,65 / +4,62** | +2,24…+2,66 | −2,96…−3,78 | −0,07 | **−0,54…−1,45** | **+5,18…+6,07** |
   Khi park khớp hai phía, phần **β (phơi nhiễm × thị trường) gần như cân** (−0,4…−1,5pp); toàn bộ gap còn lại là **α-dư**,
   và nó nghiêng về LIVE. T7 riêng (SpaceX cold): gap β tổng +0,18 (bfill) / −0,31 (zero) — "−5,42/−5,90 do T7" của vòng 2
   biến mất khi engine cũng park.
4. **α-dư tách được ở phía engine** (`alpha_split.md`; chỉ số rổ `CUSTOM_VN30EXVIC_PITG` lấy từ chính ledger):
   rổ park engine thua VNI **−3,10pp** cả kỳ (T7 −0,89, T8 −0,36, T9 −0,69, T10 −1,01, T11 −0,31) ⇒ α park engine −0,97…−1,17pp.
   Phần lớn là **α tín hiệu + chi phí của engine: −2,72…−3,78pp khi có park, so với +1,22…+1,89pp khi park = 0** trên CÙNG cửa
   sổ. Cơ chế: park ăn tiền nhàn rỗi ⇒ CAPIT (định cỡ trên idle) nhỏ lại (mua 230M vs 988M), LAG được cấp tiền qua JIT unpark
   (mua 350M vs 5M, chủ yếu 21–27/07 ngay trước pha giảm). ⇒ α tín hiệu của engine trong cửa sổ này **phụ thuộc đường đi tới
   mức đổi dấu** khi chỉ đổi park — không đọc được thành "edge BAL/LAG". Phía live chỉ có α TỔNG (+0,82pp SpaceX, +1,39pp
   ZaloPay), CHƯA tách theo sleeve (không có chuỗi lợi suất rổ park live sạch giao dịch).
5. **Câu hỏi gốc BAL/LAG — trả lời thẳng: cửa sổ live KHÔNG phải phép thử BAL/LAG.** Sổ theo book (park_holdings, 70 phiên từ
   04/08), mv TB: SpaceX **BAL 13M + LAG 38M ≈ 5% NAV**, CAPIT 221M, PARK 226M, DISC 81M; ZaloPay BAL 6M + LAG 50M, CAPIT 132M,
   PARK 94M, DISC 44M (+ DGC loại trừ 350M). Kết quả live chủ yếu = **park (β park −4,0/−3,6pp) + CAPIT**; BAL/LAG gần như
   không được triển khai nên không gánh được phần thua hurdle. Phía engine-park-live, BAL/LAG chiếm e TB 14%/19% (cold) và α tín
   hiệu âm như mục 4 — cũng KHÔNG đọc được thành edge vì đổi dấu theo park.
6. **Egg (W5, VẪN MỞ):** egg/NAV TB **24,0%** SpaceX, **15,2%** ZaloPay (cả TK, không phải sleeve) cửa sổ (nav_history,
   >0 từ 19/08; cuối kỳ 79,6% / 48,6%). Engine tiền nhàn rỗi 0%/năm; lãi egg ~8,5%/năm (**số của brief, chưa xác minh**) ⇒
   phần α live do egg ≈ 0,240 × 8,5% × 134/365 ≈ **+0,75pp SpaceX (ước lượng)** — tức gần trọn α tổng +0,82pp của live.
   Chưa tách thành bậc waterfall.

## 1. Waterfall (`waterfall.csv`, `waterfall.png`) — cold / warm-live-scale tách riêng, mọi chân trên code vá + sandbox đóng băng

| TK | regime | bậc | lợi suất kỳ | vs hurdle PIT | live − engine | md5 ledger |
|---|---|---|---|---|---|---|
| SpaceX | cold | W1 1B park=0 | +0,016% | −2,53 | −3,88 | `82f73258…` (= vòng 2, byte) |
| | cold | **W1P 1B + lịch park live** | **−8,216%** | −10,76 | **+4,35** | `0746de33…` |
| | cold | (độ nhạy) W1P, park 1,0 tới 06/07 | −8,442% | −10,99 | +4,58 | `9edc2b1f…` |
| | warm | W1 995M park=0 | −0,818% | −3,37 | −3,04 | `df8969f7…` (= vòng 2, byte) |
| | warm | **W1P 995M + lịch park live** | **−8,387%** | −10,93 | **+4,52** | `1ac895ce…` |
| | live | LIVE | −3,862% | −6,41 | | GĐ0 |
| ZaloPay | cold | W1 525M park=0 | +0,029% | −2,43 | −2,64 | `ef0674b1…` (= vòng 2, byte) |
| | cold | **W1P 525M + lịch park live** | **−7,257%** | −9,71 | **+4,65** | `d3e55cc4…` |
| | warm | W1 538M park=0 | −0,490% | −2,95 | −2,12 | `df99ba97…` (= vòng 2, byte) |
| | warm | **W1P 538M + lịch park live** | **−7,231%** | −9,69 | **+4,62** | `746eb5b2…` |
| | live | LIVE bot | −2,609% | −5,06 | | GĐ0 |

Bậc W1P đặt TRƯỚC W2b. Bốn chân park=0 tái lập byte-identical ledger vòng 2 ⇒ (a) hook tắt = byte-identical, (b) chân warm
vòng 2 ĐÃ chạy trên code vá, (c) sandbox chép đóng băng cho cùng kết quả với sandbox symlink vòng 2.

## 2. Độ nhạy backfill ngày 1 (phiên đầu chưa có e_{t−1})

| | T7 gap β tổng bfill / zero | kỳ gap β tổng bfill / zero |
|---|---|---|
| SpaceX vs park=0 cold | −5,42 / −5,90 | −2,82 / −3,30 |
| SpaceX vs park live cold | +0,18 / −0,31 | −0,36 / −0,85 |
| ZaloPay vs park=0 cold | −4,71 / −4,97 | −2,14 / −2,39 |
| ZaloPay vs park live cold | +0,01 / −0,25 | −0,54 / −0,79 |
Lựa chọn ngày 1 dịch β ~0,25–0,5pp, chuyển sang α; không đổi kết luận nào ở §0.

## 3. Đính chính vòng 2 theo skeptic

- **Rút câu "không dùng dữ liệu sau ngày vào ở bất kỳ đâu"** (§0.1 vòng 2). Có một phụ thuộc dữ liệu tương lai nhỏ ở NHÁNH
  TRỌNG SỐ RỔ: `custom_basket.oshares_pit_grid` (`custom_basket.py:433–478`, đã đọc code) lấy OShares của dòng `ticker_financial`
  theo QUÝ (công bố sau) rồi **re-date bước thay đổi số CP lùi về ngày GDKHQ** khớp được trong `_corp_action_share_events` —
  nên trọng số rổ tại ngày GDKHQ dùng số CP chỉ biết khi báo cáo quý ra. Số đo của skeptic (CHƯA đo lại): ACB bước GDKHQ 15/06
  lấy từ dòng Q2 công bố 22/07; 806 bước re-dated, trung vị 42 ngày. Ảnh hưởng quan sát được: phần dư 4 phiên cuối của
  determinism (44,6M / 763,9B = 0,006% NAV). A/B bản strict `Release_Date ≤ t`: **KHÔNG làm** (tuỳ chọn; cần sửa đường trọng
  số rổ, không rẻ).
- **Relabel 7a:** "LAG adj INERT" đổi thành **"hai bản LAG adjusted khớp nhau"** (`sandbox_ctrl` vs `sandbox_adj` đều là bản
  adjusted ⇒ byte-identical `a63b2000…` không nói gì về raw-vs-adjusted). Hiệu ứng thật đo được là **vintage dữ liệu LAG**:
  −1,34pp trên cửa sổ (W0 warm @50B), −68,21B trên lịch sử tới 19/06 (`4707bcbe` vs `d7091b4b`).
- **Thay "±0,2pp" bằng phân phối tie-break thật** (`TIEBREAK_SEED` = xáo thứ tự trong ngày có seed trước mergesort trong
  `regime_size_overlay.apply_regime_size`). Cấu hình pin (park 3:0.3, AUDIT_END 19/06, cache `0729_postrestate`,
  `IDLE_CARRY_TIER=off`) trên dữ liệu LAG đóng băng 12/11, 10 seed: **CAGR 23,94–25,05% (trung vị 24,34, sd 0,35pp)**, NAV
  725,3–810,2B (sd 26,7B), Sharpe 1,94–2,02, Calmar 1,64–1,72, MaxDD −14,6% mọi seed. Mergesort (24,46%, `89e96ba6` = C1fix_v3
  byte) và quicksort main (24,31%) đều nằm trong phân phối. ⇒ chênh pin 23,37% vs vá 23,60% (0,23pp, vintage 10-29) **nhỏ hơn
  1 sd tie-break**; số pin R3 là MỘT lần rút từ phân phối có sd ≈ 0,35pp CAGR (đo trên dữ liệu 12/11, chưa đo trên vintage 10-29).
- **Đóng băng data (việc 6):** sandbox `sb/` — code = symlink worktree p1c, `data/` = **bản chép** (cp, chỉ đọc) của đúng các
  file engine mở (open-trace chân `SXcold_p0`: 4 file LAG/forensic + snapshot CA + 2 bq cache; không có file nào ngoài sandbox),
  gồm `earnings_surprise_data.pkl` đóng băng `952ac926…` (bản canonical đã đổi lúc 19:02 hôm nay → `3e7f3801…`, KHÔNG dùng).
  md5 toàn bộ data trước chạy `sandbox_data_md5.txt` = sau 20 chân `sandbox_data_md5_after.txt` (diff rỗng). Mọi chân cold/warm/
  tie-break chạy trên code vá `c27fe6823`.

## 4. Hạn chế

- Engine park ≤ tiền mặt: không mô hình được 141% gross + nợ margin 02–03/07 (ước lượng số học §0.1).
- Tách live park/tín hiệu: từ 04/08 = sổ book `park_holdings.py` (2 phiên reconcile ≠ ok: 10/08 mỗi TK); trước 04/08 (23 phiên
  SpaceX, 20 ZaloPay) = lô non-PARK của bootstrap 04/08 có `entry_date ≤ t` × Price BQ, park := phần dư `mtm_stock − tín hiệu`
  (bỏ sót lô non-PARK đã bán trước 04/08 — plan tháng 7 chỉ có 1 cặp lệnh book trống 15/07). |Σbook − mtm_stock|/NAV TB
  1,6–1,8%, max ~10% (chưa truy). Book `CORP_ACTION` (TB 2M) tính vào disc.
- α live chưa tách theo sleeve; α engine tách park vs (tín hiệu + chi phí) qua chỉ số rổ.
- Lãi egg 8,5%/năm lấy từ brief, chưa xác minh.

## 5. CHƯA đo
W2b (sàn ADV 2 tỷ / mã cờ / LAG DD-zone / excluded_tickers) · W3 lệnh tay (DISC TB 81M SpaceX) · W4 fill thật · W5 egg ·
A/B strict Release_Date ≤ t cho trọng số rổ · tie-break trên vintage 10-29.

## 6. Tái lập
`make_sandbox.sh` (dựng `sb/` đóng băng) · `run_leg.sh <TAG> KEY=VAL…` (trần RAM 5G/chân) · `run_tiebreak.sh` ·
`live_books/run.sh` (park_holdings mỗi phiên) · `decompose3.py exposure_decomp3` · `alpha_split.py alpha_split.md` ·
`waterfall3.py`. Lệnh + env đầy đủ ở dòng `EXIT=` cuối mỗi `logs/*.log`; md5 ledger ở `ledgers/MD5SUMS`.

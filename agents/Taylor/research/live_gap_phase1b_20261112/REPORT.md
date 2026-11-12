# GĐ1 vòng 2 — áp required_change quant-skeptic (job `Taylor_20261112_112708`, 12/11/2026)

> Thay thế các kết luận bị REFUTED trong `../live_gap_phase1_20261112/REPORT.md`. Nhánh cô lập: code vá ở worktree
> `wt-livegap-p1-1112` (commit `5512bfe3d`, KHÔNG merge); code pin-era ở `wt-livegap-pincode-1112b` (`f66dab189`).
> Không đổi production/cron/data canonical. Mọi ledger `_exp_gap_*` ở `ledgers/` (1 ledger chân pincode lạc vào
> `WorkingClaude/data/` đã chuyển về `ledgers/`; `data/` canonical hiện 0 file `exp_gap`).
> **Số lần chạy engine vòng này: 22** = 18 chạy trọn (self-check 0 VND cả BAL + LAG, mọi chân) + 4 chân v2 bị kill
> (EXIT=143 sau 80–95s, bỏ, thay bằng v3). W0warm_unadj1029 chạy 2 lần (lần 1 log cụt) → 2 ledger md5 trùng `ae506bd1…`.
> Không có cấu hình nào được chọn theo kết quả ⇒ không có DSR/PBO để tính. **N = MỘT cửa sổ 4 tháng, MỘT đường đi.**

## 0. Kết luận (chỉ phần đã đo)

1. **D1 — vá sort THẬT SỰ có tác dụng; lệch AUDIT_END là do sort không ổn định, không phải look-ahead thông tin.**
   Chạy lại với code + workdir cùng sandbox (`sb_main`/`sb_fix`, không còn cảnh báo VO NGHIA; `.opened` trace xác nhận
   `sb_fix/regime_size_overlay.py` được nạp). `determinism_check` AUDIT_END 06-19 vs 07-29, so trên 3.107 phiên chung:
   | code | phiên lệch >1 VND | lệch đầu tiên | max ΔNAV | NAV 06-19 (06-19 / 07-29) |
   |---|---|---|---|---|
   | main (chưa vá) | 1.986 | 2018-07-06 | 16,50 tỷ | 752,73B / 738,83B |
   | fix (mergesort) | **4** | **2026-06-16** | 44,6 triệu | 763,89B / 763,86B |
   Nguyên nhân gốc: `regime_size_overlay.apply_regime_size` gọi `s.sort_values("time")` (quicksort, không ổn định) ⇒ thứ tự
   ưu tiên tín hiệu TRONG CÙNG NGÀY phụ thuộc độ dài toàn mảng (tức phụ thuộc số dòng SAU ngày đó). Đây là phụ thuộc
   tie-break vào kích thước mẫu, **không dùng giá trị tương lai nào** (không chuẩn hoá toàn mẫu, không dùng dữ liệu sau ngày vào).
   Phần dư 4 phiên cuối: chỉ số rổ `CUSTOM_VN30EXVIC_PITG` lệch 0,012% từ 06-16 (3 phiên trước AUDIT_END) + thanh lý cuối
   kỳ 06-19 — hiệu ứng biên, 44,6M/763,9B = 0,006% NAV; **chưa bisect** nguồn lệch chỉ số rổ (mở, nhỏ).
2. **Số pin cũ ĐỔI dưới vá**: dữ liệu pin-era (vintage 10-29 của 3 file LAG, tái lập byte `4707bcbe`) + code vá ⇒
   **700,76B / CAGR 23,60% / Sharpe 1,89 / MaxDD −14,6% / Calmar 1,61** (ledger `c95b4158…`), so pin **684,52B / 23,37% /
   1,88 / −14,6% / 1,60**. Lệch bắt đầu đúng 2018-07-06; theo năm khác ở 2018/2020/2021/2022/2024/2025/2026 (lớn nhất 2025
   +30,58% → +33,60%). ⇒ Số pin R3 23,37% (đầu sàn) là MỘT tie-break tuỳ ý trong dải ≈ ±0,2pp CAGR; cả hai đều là chiến lược
   hợp lệ, chỉ bản vá là tái lập được khi đổi AUDIT_END. **Không re-pin trong lượt này** (cần user/Mike duyệt + quant-skeptic).
3. **D6/việc 4 — drift control `4707bcbe → d7091b4b` là DỮ LIỆU, không phải code**: code pin-era (`f66dab189`) trên dữ liệu
   hôm nay ⇒ `d7091b4b` byte-identical code main. Hoán từng file pin-era (vintage 10-29) vào control (AUDIT_END 06-19, code main):
   | file hoán | NAV 06-19 | Δ vs control 752,73B | ledger md5 |
   |---|---|---|---|
   | không (control, frozen 11-12) | 752,73B | — | `d7091b4b…` |
   | `earnings_surprise_data.pkl` | 752,73B | 0 (byte-identical) | `d7091b4b…` |
   | `lag_edge_health.csv` | 741,66B | −11,07B | `af80f966…` |
   | `earnings_events_classified.csv` | 695,94B | **−56,79B** | `28120b9f…` |
   | cả 3 | **684,52B** | −68,21B (tương tác −0,35B) | **`4707bcbe…` = pin, byte-identical** |
   **Point-in-time: KHÔNG.** `earnings_events_classified.csv` frozen 11-12 vs vintage 10-29, chỉ dòng Release_Date < 06-19
   (51.219 dòng chung): `Release_Date`/`NP_R`/`Rev_YoY` 0 khác; `pre_ret` 18.938, `rel_ret` 16.993, `post_ret` 18.881 dòng khác
   (rải đều MỌI năm 2011–2026), `pattern` 288 dòng đổi nhãn, +8 sự kiện 2015–2017 mới xuất hiện ⇒ lịch sử giá-lợi suất bị dựng
   lại (đúng dạng dựng lại với giá điều chỉnh mới), không phải nối thêm. `lag_edge_health.csv` (so bak 09-27): thêm cột
   `known_date`, 5.391 → 5.412 dòng trước 06-19. Chi tiết: `restate_check.txt`, `restate_check_events.txt`.
   Ghi chú phụ (chưa kiểm sâu): engine dùng `post_ret` (= p_{+30}/p_{+5}) của sự kiện TRƯỚC cho `pa_HL3`; chỉ an toàn khi 2 lần
   công bố cách nhau > 30 phiên.
4. **D5 — LAG adj INERT trên toàn lịch sử warm**: W0warm @50B 2014→11-12, `sandbox_ctrl` (LAG canonical) vs `sandbox_adj`
   ⇒ **byte-identical** `a63b2000…`. Nhưng **vintage file LAG thì KHÔNG inert**: cùng chân với 3 file vintage 10-29 ⇒ cửa sổ
   SpaceX +1,62% (vs +2,96%), ZaloPay +1,76% (vs +3,10%) — **−1,34pp** chỉ do vintage dữ liệu LAG.
5. **Việc 2 — warm ở quy mô live** (chạy lại với hệ số hiệu chỉnh vì lượt đầu lệch quy mô 5–13%):
   SpaceX `NAV_TOTAL_B=0,079958` ⇒ NAV(30/06) = **995,5M** (đích 1B), lợi suất 30/06→11/11 **−0,818%**;
   ZaloPay `NAV_TOTAL_B=0,046052` ⇒ NAV(06/07) = **537,6M** (live 525,4M, +2,3%), lợi suất **−0,490%**.
   (Lượt đầu 946M/455M cho −0,818%/−0,488% ⇒ ở dải < 1B lợi suất gần như không nhạy quy mô.)
6. **D3 đã sửa — live phơi nhiễm CAO hơn engine, không thấp hơn.** Phân rã số học theo tháng (`exposure_decomp.md`):
   gap = Δ(Σ e_{t−1}·r_VNI) [phơi nhiễm × thị trường] + Δ(dư) [chọn mã + thực thi + lãi phần không-cổ-phiếu]. Kỳ (gộp lãi kép):
   | TK | engine so sánh | e TB live / eng | r live / eng | gap | phần β | phần α-dư |
   |---|---|---|---|---|---|---|
   | SpaceX 01/07→11/11 | cold 1B | 70% / 66% | −3,86% / +0,02% | −3,88pp | **−2,87** | −1,01 |
   | SpaceX | warm-live 995M | 70% / 60% | −3,86% / −0,82% | −3,04pp | **−2,69** | −0,35 |
   | ZaloPay bot 06/07→11/11 | cold 525M | 69% / 69% | −2,61% / +0,03% | −2,64pp | **−2,15** | −0,48 |
   | ZaloPay bot | warm-live 538M | 69% / 63% | −2,61% / −0,49% | −2,12pp | **−2,06** | −0,06 |
   Phần β dồn ở **T7**: live 91% (SpaceX) / 87% (ZaloPay) cổ phiếu vs engine 34–42% trong tháng VNI −6,68% (ZaloPay −5,84%
   từ 06/07) ⇒ gap β T7 −5,07..−5,42pp (SpaceX), −4,45..−4,71pp (ZaloPay). T8 ngược lại: phơi nhiễm ngang (89–91%) nhưng
   α-dư live thua 2,9–3,5pp; T9 live thắng α-dư +2,6..+3,4pp. ⇒ Gap kỳ chủ yếu là **thời điểm phơi nhiễm lúc go-live**
   (bot vào đủ tỷ trọng ngay khi engine còn ngồi tiền), α-dư cả kỳ nhỏ (−0,06..−1,01pp) nhưng dao động lớn từng tháng.
7. **Khoảng gap đã sửa (một hurdle PIT duy nhất — D7)**: hurdle tiết kiệm PIT **2,548%** (SpaceX 01/07→11/11), **2,455%**
   (ZaloPay 06/07→11/11), nguồn GĐ0 `vs_savings_table.csv`.
   | | LIVE | vs hurdle | live − engine (cold … warm-live) | engine vs hurdle (cold … warm-live) |
   |---|---|---|---|---|
   | SpaceX | −3,862% | −6,41pp | **−3,04 … −3,88pp** | −2,53 … −3,37pp |
   | ZaloPay bot | −2,609% | −5,06pp | **−2,12 … −2,64pp** | −2,43 … −2,94pp |
   Nếu tính cả W0 @50B gốc 2014 (+2,96% / +3,10%, quy mô KHÔNG phải live) thì dải live−engine mở rộng tới −6,82pp (SpaceX),
   −5,71pp (ZaloPay) — đó là dải D4 của skeptic (1,6–5,7pp); dải ở **quy mô live** hẹp hơn: ZaloPay 2,1–2,6pp.
   D2 ghi nhận: warm W1(live scale) − W0 @50B = −3,78pp (SpaceX), −3,59pp (ZaloPay) — "gap không ở W1" chỉ đúng cold.
   Nhưng bậc warm W0→W1 trộn 2 trục (quy mô 575B→1B VÀ toàn bộ đường đi 2014–06/2026 khác nhau) ⇒ không đọc là "chi phí quy mô".

## 1. Waterfall (`waterfall.csv`, `waterfall.png`) — cold / warm-live-scale tách riêng

| TK | regime | bậc | lợi suất kỳ | vs hurdle PIT | live − engine | md5 |
|---|---|---|---|---|---|---|
| SpaceX | cold | W0 pin park0 @50B | −0,499% | −3,05 | −3,36 | `7895ddef…` |
| | cold | W1 1B (= W2a LIQ_ZERO_BLOCK, byte) | +0,016% | −2,53 | −3,88 | `82f73258…` |
| | warm | W0 @50B gốc 2014 (adj = ctrl, byte) | +2,961% | +0,41 | −6,82 | `a63b2000…` |
| | warm-D5 | W0 @50B, LAG vintage 10-29 | +1,625% | −0,92 | −5,49 | `ae506bd1…` |
| | warm | **W1 quy mô live 995M** | **−0,818%** | −3,37 | **−3,04** | `df8969f7…` |
| | live | LIVE account | −3,862% | −6,41 | | GĐ0 |
| ZaloPay | cold | W0 @50B | −0,499% | −2,95 | −2,11 | `78412d15…` |
| | cold | W1 525M | +0,028% | −2,43 | −2,64 | `ef0674b1…` |
| | warm | W0 @50B gốc 2014 | +3,103% | +0,65 | −5,71 | `a63b2000…` |
| | warm-D5 | W0 @50B, LAG vintage 10-29 | +1,764% | −0,69 | −4,37 | `ae506bd1…` |
| | warm | **W1 quy mô live 538M** | **−0,490%** | −2,94 | **−2,12** | `df99ba97…` |
| | live | LIVE bot | −2,609% | −5,06 | | GĐ0 |

## 2. CHƯA đo (không làm trong lượt này, theo brief)
W2b (sàn ADV 2 tỷ / mã cờ / LAG DD-zone / excluded_tickers) · W3 lệnh tay · W4 fill thật · W5 egg (Trứng vàng — phơi nhiễm
cổ phiếu/NAV của live ở trên tính trên NAV có egg; egg ~79% NAV tháng 11 theo D3, chưa tách thành bậc).
Phần dư 4 phiên cuối của determinism (chỉ số rổ từ 06-16) chưa bisect.

## 3. Tái lập
`run_leg.sh <TAG> <code> <wd> KEY=VAL…` (PT_WORKDIR = wd, OUT `logs/`); sandbox `make_sandbox.sh <name> <code>` (+`SWAP=`);
`determinism_check.py` (phase1); `waterfall.py`; `decompose.py exposure_decomp`. Lệnh + env đầy đủ ở dòng `EXIT=` cuối mỗi log.

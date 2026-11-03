# CAPIT flag gate — có nên loại mã có cờ khỏi candidate CAPIT? (job Taylor_20261103_024121)

**PAPER-ONLY. Không đụng code production, không ghi file pin.** Engine = bản sao
`pt_v23_capitflag_exp_.py` (patch `patch_exp_.py`, thêm env `CAPIT_FLAG_GATE`, mặc định off).

## Kết luận: **KHÔNG PHÂN BIỆT ĐƯỢC** về mặt thông tin của cờ — nhưng cổng có CHI PHÍ CƠ HỌC đo được

- Cổng chỉ chạm **6 lượt tên / 4 mã / 5 sự kiện** trong 16 sự kiện CAPIT 2014–2026 (FMC×2 2018,
  NHH 2022, RAL 2024-08, DGW×2 2025). N độc lập ≈ 6 → không đủ để kết luận gì về chất lượng tín hiệu.
- Ở cấp TÊN, mã có cờ **kém** các mã cùng rổ trung bình **−10,0pp** (trung vị −10,8pp, 4/6 âm),
  exact sign-flip p = **0,31** (6 sự kiện) / **0,25** (gộp 4 mã) ⇒ hướng ủng hộ cổng, KHÔNG có ý nghĩa.
- Nhưng ở cấp NAV cổng floor làm **CAGR 22,12% → 20,35% (−1,77pp)**, Calmar 1,36 → 1,22. Lý do
  KHÔNG phải mã có cờ là mã thắng, mà là **cơ học rổ**:
  1. **2018-07-05: rổ còn 2 tên < tối thiểu 3 ⇒ CẢ SỰ KIỆN bị bỏ** (mất 9,07B lãi CAPIT; bản
     thân FMC chỉ −1,7%, 2 tên còn lại +30%). Đây là toàn bộ phần IS −1,14pp.
  2. **2025-04/2025-10 (DGW)**: bỏ DGW làm rổ rơi khỏi tầng pb_z<−1 hoặc co lại ⇒ deploy nhỏ hơn
     (102→79B, 150→99B) đúng lúc thị trường hồi. Mất 11,2B + 8,3B. Đây là phần OOS −2,4pp.
  - Tổng lãi CAPIT 130,3B → 102,1B (−28,1B); phần còn lại của −100B NAV cuối là lãi kép + đường đi BAL/LAG.
- ⇒ Số −1,8pp phản ánh **2–3 tập** và tương tác với luật "≥3 tên" + fallback tầng pb_z, không
  phải giá trị/phản-giá-trị của cờ. Paired block bootstrap ngày cho P(CAGR tốt hơn)=0,00 nhưng
  **không dùng được làm bằng chứng**: chênh lệch tập trung ở vài tập, bootstrap theo thời gian
  không mô phỏng được "may/rủi chọn tên" — trích để đầy đủ, KHÔNG phải p-value.

## Bảng A/B (một trục: gate tại lúc chọn rổ CAPIT)

Cửa sổ 2014-01-02 → 2026-06-19, NAV 50B, park 0 (`PARK_STATES=3:0.0`), tiền nhàn rỗi 0% (**pin0% = SÀN**),
threads=1, `AUDIT_END=2026-06-19`. Số Final NAV/CAGR/Sharpe/DD/Calmar = dòng engine in ra; IS/OOS tính
lại từ ledger (`analyze_exp_.py`, annualize theo lịch).

| Chân | Cờ loại | Final NAV | CAGR | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20+ | md5 |
|---|---|---|---|---|---|---|---|---|---|
| control main (code canonical) | — | 603,06B | 22,12% | 1,93 | −16,2% | 1,36 | 20,06% | 24,06% | `537e349b` = PIN ✅ |
| control bản vá, gate=off | — | 603,06B | 22,12% | 1,93 | −16,2% | 1,36 | 20,06% | 24,06% | `537e349b` = PIN ✅ |
| **all** (theo dispatch) | FLOOR/RATING/BANNED/UNKNOWN_FLOOR + đỏ PIT | 500,68B | 20,31% | 1,80 | −16,6% | 1,22 | 18,92% | 21,62% | `3735c809` |
| floor | FLOOR_FAIL/UNKNOWN_FLOOR/BANNED | 502,80B | 20,35% | 1,80 | −16,6% | 1,22 | 18,92% | 21,70% | `e73c3905` |
| rating | RATING_FAIL | 602,62B | 22,11% | 1,93 | −16,2% | 1,36 | 20,06% | 24,04% | `80b92713` |
| strict (độ nhạy) | all + UNKNOWN_RATING | 441,09B | 19,09% | 1,69 | −17,5% | 1,09 | 16,07% | 21,97% | `6091bd19` |

Self-check: **0 VND** (BAL + LAG, cash-flow + final-NAV identity) ở cả 6 chân.
`strict` KHÔNG có ý nghĩa cho live: rating 8L chỉ có từ 2014-07 ⇒ sự kiện 2014-05 bị loại do thiếu
dữ liệu backfill, không phải do cờ. Live luôn có rating ⇒ bỏ qua chân này.

## Phân tách cờ

- **FLOOR_FAIL gây ra toàn bộ thay đổi** (FMC 2018: CF_OA_3Y < 0; RAL 2024: CF_OA_3Y < 0; DGW 2025:
  CF_OA_3Y < 0). Cả 3 đều qua cổng golden của CAPIT (ROE_Min5Y≥12%, ROIC5Y≥10%, FSCORE≥6) — tức
  chỉ trượt vế **dòng tiền HĐKD 3 năm**, đặc thù phân phối/vốn lưu động (DGW, RAL), không phải lỗ.
- **RATING_FAIL gần như trơ**: chỉ NHH 2022 → ΔCAGR −0,01pp. Golden floor của CAPIT đã chồng lên rating.
- **BANNED: no-op trong backtest** (VTP/TOS có trong pool 5 lần nhưng không bao giờ được chọn: pb_z
  NaN hoặc > 0, bị xếp hạng loại). ⚠️ Nhưng engine CAPIT KHÔNG có lọc BANNED cứng — một rổ mỏng có
  thể mua TOS/VTP. Cổng BANNED là bảo hiểm đúng, chi phí 0.
- **CTCK: KHÔNG bị loại cấu trúc BỞI CỔNG CỜ** — vì 0/128 dòng pool là CTCK (ICB 8777): cổng golden
  CAPIT đã loại CTCK từ trước. Cho tham chiếu: trên 18 ngày sự kiện, 362/417 (86,8%) dòng CTCK trong
  universe_pit là FLOOR_FAIL, 91,4% trong đó do CF_OA_3Y ≤ 0 (cho vay margin ghi vào CF HĐKD) ⇒ nếu
  CTCK vào được pool thì cổng floor SẼ loại cấu trúc.
- Tỷ lệ pool bị tỉa (cờ thật, không tính UNKNOWN_RATING) theo năm: 2014 0%, 2015 0%, 2016 0%,
  2018 28,6% (2/7), 2020 3,4% (1/29, BANNED no-op), 2022 9,1% (1/11), 2023 0%, 2024 10,5% (2/19),
  2025 20,0% (5/25), 2026 0%. File: `capit_pool_flags_exp_.csv`.

## RED_FLAG_CODES — cái nào tái lập PIT được

| Mã | PIT? | Kết quả |
|---|---|---|
| THANH_KHOAN_CHET (ADV3T ≤ 100tr) | Có (Volume_3M_P50×Price) | 0 lần — pool CAPIT đã đòi GTGD ≥ 2 tỷ |
| NGOAI_UNIVERSE | Có | 0 lần — engine đã chạy trên universe_pit |
| LENH_QUA_LON_VS_ADV (> 25% ADV) | Chỉ hậu kiểm, KHÔNG phải cổng chọn mã (phụ thuộc size) | @50B: 64/243 ngày mua CAPIT (26%) > 25% ADV, max 47% (engine chia lệnh nhiều phiên). Là vấn đề SIZE, không phải chọn mã |
| SURPRISE_PHONG_CO_HOC | N/A (chỉ LAG/PEAD) | — |
| DD_KHONG_CHAY_DUOC | Không (sự cố vận hành) | — |

## Hệ quả cho live

- CAPIT hiện **ngủ/rỗng** ⇒ cổng không đổi gì hôm nay. Nó chỉ tác động ở lần washout kế tiếp, và
  backtest nói tác động chính sẽ đến từ **cơ học rổ mỏng** (bỏ cả sự kiện khi < 3 tên; co deploy).
- Không có bằng chứng cổng làm HỎNG chọn mã (mã có cờ hơi kém, n=6) cũng không có bằng chứng nó
  GIÚP. User đã chốt áp ⇒ áp được, nhưng nên biết cái giá đo được là cơ học, ~−1,8pp CAGR trên
  2 tập lịch sử, IS và OOS cùng âm.
- **Đề xuất (CHƯA ĐO, chỉ là đề xuất):** áp cổng theo kiểu `CAPIT_DIV_MINN` đã có — nếu cổng làm
  rổ < 3 tên thì giữ rổ không gate (hoặc bỏ đúng mã có cờ nhưng không huỷ sự kiện), và giữ nguyên
  tổng tỷ trọng deploy thay vì co lại. Sẽ gỡ được phần 2018-07 (IS); phần 2025 (deploy co) cần đo riêng.
  Muốn biết thì chạy thêm 1 chân — chưa chạy để tránh rẽ nhánh hậu nghiệm.

## Caveat
- Cờ đọc từ BQ `tav2_mike.universe_pit_quality` HÔM NAY (vintage 2026-11-03), engine đọc cache
  snapshot `bq_cache_asof20260729_postrestate` ⇒ lệch vintage chỉ ở chân treatment. Không kiểm được
  universe_pit_quality có bị restate sau 07-29 hay không.
- rating_8l backfill: `rating_asof` một số năm cũ (2022-23 min 2021-03-18) — RATING_FAIL có thể
  thiếu/thừa, nhưng chân rating trơ nên không đổi kết luận.
- N sự kiện CAPIT = 16 (size>0), nhóm thành ít episode hơn; DSR/PBO không chạy (không chọn cấu
  hình trên dữ liệu; 4 biến thể đều định trước).
- CAGR thật ≈ backtest − 1,5pp.

## Tái lập
```bash
cd /home/trido/thanhdt/WorkingClaude; RD=mike/agents/Taylor/research/capit_flag_gate_20261103
$RD/run_leg_exp_.sh ctrlmain_exp $PWD/pt_v23_audit_2014.py            # md5 537e349b
for g in off all floor rating strict; do $RD/run_leg_exp_.sh g_${g}_exp $RD/pt_v23_capitflag_exp_.py CAPIT_FLAG_GATE=$g; done
# (control off leg chạy với tag ctrloff_exp)
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python $RD/analyze_exp_.py   # -> ab_results_exp_.json
```
Ledger nằm ở `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_capflag<g>_exp__..._exp_<TAG>_univpit.csv` (tên exp, không phải pin).

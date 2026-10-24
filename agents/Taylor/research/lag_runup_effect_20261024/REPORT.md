# LAG: giá đã chạy xa trước công bố có làm drift yếu đi không? — job Taylor_20261024_040927

R&D/paper, KHÔNG wire, KHÔNG sửa production/registry. 24/10/2026.

## Kết luận

1. **Nhìn chung là SAI: giá chạy xa (theo 120 phiên hoặc YTD) không làm drift LAG yếu đi.** Ở cả tập
   (5.419 sự kiện, 51 quý), chênh lệch quintile Q5−Q1 trong từng quý đều có CI chứa 0:
   r120 +0,19pp [−1,98; +2,21], YTD −1,29pp [−3,45; +0,71], cách đỉnh 250 phiên −1,68pp [−4,22; +0,65].
   Ngưỡng cứng r120>+50% còn cho excess cao hơn phần còn lại (+1,94pp [−0,09; +3,66]). Riêng
   ytd>+100% thì −0,50pp [−3,90; +1,90] (n=285).
   - Có một hiệu ứng **ngắn hạn, nhỏ**: run-up 30 phiên trước công bố (`pre_ret`) Q5−Q1 −1,93pp
     [−4,02; −0,06], tập trung ở **LAG_LO** (−2,55pp [−5,23; −0,14]). Hiệu ứng này đến từ nhóm cổ phiếu
     bị bán trước công bố drift TỐT HƠN (Q1), chứ không phải nhóm chạy mạnh drift xấu đi. Nó cũng
     **biến mất trong universe_pit** (+0,14pp [−1,99; +2,31]). Book live có sàn ADV 2 tỷ nên gần
     universe_pit hơn.
2. **Ngoại lệ đáng chú ý, nhưng chưa đủ để thành luật: nhóm hàng hóa/chu kỳ (ICB<2000) có YTD>+100%
   trước công bố.** Excess trung bình −2,92% so với +3,39% của phần còn lại trong nhóm hàng hóa, tức
   chênh −6,32pp [−13,24; −0,94]. Mẫu là n=52 sự kiện, 17 quý, 37 mã. Hiệu ứng tăng dần theo ngưỡng
   YTD: >50% −0,6 · >80% −3,1 · >100% −6,3 · >150% −6,5pp. Tuy vậy:
   - CI **chứa 0** khi tách OOS (−5,71 [−14,79; +2,13]), trong universe_pit (−5,86 [−11,50; +1,36]) và
     trong **LAG_HI** (−6,08 [−12,39; +3,97]). LAG_HI chính là nhóm của MSR.
   - Ô này được chọn hậu nghiệm từ khoảng 180 phép thử. 24/180 ô có ý nghĩa thống kê, trong khi nếu
     không có hiệu ứng gì thì kỳ vọng khoảng 9 ô (các ô tương quan nhau). Vì vậy đây là **giả thuyết
     cần pre-register**, chưa phải phát hiện.
   - Ở nhóm phi hàng hóa, ytd>+100% thì +0,69pp [−3,43; +3,74], tức không có tác dụng gì.
3. **Không nên thêm bộ lọc hay hạ tier theo run-up vào LAG.** Họ 11 biến thể "loại sự kiện run-up"
   (N_trials=11, T=51 quý): **DSR 0,561 (<0,95 = RED FLAG), PBO 0,829 (≥0,5 = overfit)**. Biến thể tốt
   nhất (ytd>100) chỉ cải thiện trung bình +0,09pp mỗi quý. Theo leave-one-out từng năm, mức cải thiện
   dương nhưng chỉ 0,01–0,10pp.
4. **"Surprise bị thổi phồng trong xu hướng dốc" không làm xếp hạng sai.** Biến `sur_gap` =
   surprise_B_MA − surprise so với quý liền trước. Q5−Q1 = +1,05pp [−0,38; +2,48] trên toàn tập và
   +1,42 [−0,90; +4,14] trong HI. Dấu còn ngược với giả thuyết của skeptic: surprise "phồng" drift
   không kém hơn.
5. **Lợi nhuận tăng >100% yoy liên tiếp 2+ quý (kiểu MSR): drift vẫn còn.** n=882, excess +2,66% so
   với +1,87% của phần còn lại (+0,79pp [−1,06; +2,58]). HI +2,11 [−0,16; +4,30]; LO −1,30
   [−3,08; +0,94]. Không kết luận được, nhưng không có dấu hiệu drift chết.

## Ca MSR (1 ca, không suy rộng)
- 2026Q3 công bố 2026-10-22: tier LAG_HI, qualify=True, prior_n_good=13, **pa_HL3 = 8,19**. Ở các quý
  trước pa_HL3 là 3,03, tức dưới ngưỡng 5. Mức nhảy qua ngưỡng hoàn toàn nhờ một sự kiện 2026Q2
  (post_ret +27,6%), nên skeptic nói đúng. 13 sự kiện tốt trước đó có post_ret trung bình +3,56%, với
  8/13 sự kiện dương.
- Giá đến phiên 21/10: **YTD +160,3%** (VNINDEX −2,6%), r60 +91,2%, r120 +65,9%, 30 phiên trước công bố
  +32,8%, cách đỉnh 250 phiên −8,1%. MSR thuộc ICB 1775 (hàng hóa) ⇒ rơi đúng vào ô "hàng hóa YTD>150%":
  n=21, 8 quý, excess TB −3,39%, trung vị −7,37%, chênh −6,52pp [−13,27; +0,60]. CI chứa 0.
- NP_R = 41.510% và 29.415% là hiệu ứng nền (các quý trước lỗ, NP_R âm), không phải tăng trưởng
  thật; surprise_B_MA bị kẹp ở mức 5 hoặc 2,54.
- Ý nghĩa thực tế: đây không phải lý do thống kê để LOẠI MSR. Nếu DollarBill muốn giảm tỷ trọng thì
  phải ghi rõ là **đề xuất tùy nghi**, không phải luật production. Đây chính là ô giả thuyết ở mục 2
  cần pre-register và theo dõi.

## Code pin hiện đã có gì (đọc code)
- Gate LAG pin (`pt_v23_audit_2014.py` §4, `lag_live_schedule.py`): NP_R≥15 ∧ prior_n_good≥4 ∧
  pa_HL3≥5, cộng forensic gate. **KHÔNG có bộ lọc run-up hay chase-cap ở khâu chọn sự kiện.**
  `LAG_NONOP_FILTER` mặc định tắt. Overheat/AVOID chỉ áp cho BAL (`golive_recommend_v23.py:732`).
  Live còn có gate rating 8L≤3 và sàn ADV 2 tỷ.
- Nhãn `LEAK_RUNUP_POS` trong `earnings_events_classified.csv` (pre≥10 ∧ rel≤−2) chỉ dùng để mô tả,
  gate không đọc nhãn này. Phân tích ở đây có thử `pre>20 & rel<0`: +1,14pp [−2,63; +4,92], tức không
  phải tín hiệu xấu.

## Phương pháp
- **Sự kiện:** dựng lại gate verbatim từ classified CSV + pkl (`build.py`). Kết quả dùng post_ret =
  Close[R+30]/Close[R+5]−1, tức vào sau công bố 5 phiên và giữ 25 phiên. Excess = post_ret trừ VNINDEX
  cùng cửa sổ. Dữ liệu từ 2014-01 đến 2026-08-07, là giới hạn độ chín của CSV.
- **Control:** giai đoạn 2014-01 → 2026-05-15 có n=5.322, post_ret TB 4,23%; riêng 2026 có n=290, TB
  −0,81%. Bản pin (`research/lag_regime_gate`, 07-23) là 5.389 sự kiện, 2026 có n=287 / −0,82%. Năm
  2026 khớp, tổng lệch −1,2%, có thể do CSV đã refresh và cách khai cửa sổ (chưa truy cụ thể). Tính lại
  post_ret từ bq_cache cho TB 4,23 so với 4,16; 109/5.419 sự kiện lệch >0,5pp.
- **Biến (PIT, giá đến phiên trước ngày công bố):** r60, r120, YTD, các biến đó trừ VNINDEX (`_x`),
  dist_hi250, pos250, pre_ret (30 phiên), rel_ret (R−1→R+5, vẫn trước lúc vào), pre−rel, sur_gap.
- **Thống kê:** quintile trong từng quý, bootstrap cụm theo quý (B=2000), IC Spearman theo quý. DSR
  (Bailey–López de Prado) và PBO (CSCV S=8) cho họ bộ lọc.

## Giới hạn
- Phân tích ở mức sự kiện, không chạy NAV. Book LAG bị giới hạn vốn (oversubscribed), nên loại sự kiện
  ≠ tăng NAV.
- Ô hàng hóa nhỏ: 25/52 sự kiện ytd>100 rơi vào năm 2021, vài mã lặp lại (VGS 4, BKC/DHM/NKG 3), trong
  đó NKG đã bị BANNED.
- ICB lấy theo mã hiện tại, không PIT; mã đổi ngành sẽ bị gán sai.
- `profit_*` không dùng ở đâu.

## Files
`build.py` → `panel.csv` (md5 5d76ab7b…) + `gate_events.csv` · `analyze.py` → `quintiles.csv`,
`thresholds.csv`, `summary.json` (DSR/PBO/LOO) · `robust.py` → `commod_ytd_robust.csv` · `msr_case.py`
→ `msr_case.log`. Chạy bằng `$DNA_PYEXE`.

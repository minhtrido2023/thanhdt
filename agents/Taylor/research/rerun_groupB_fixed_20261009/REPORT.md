# Nhánh 4 — chạy lại "nhóm B" trên engine đã sửa bug custom30V double-count

Job `Taylor_20261008_172556` · 2026-10-09 · PAPER-ONLY. Live đang park = 0 ⇒ **không đổi tiền live**.
Không pin vào kho, không sửa registry (đề xuất ở `results_registry_groupB.proposed.md`), không đụng
`trading_rules.json`/config/knob production.
PREREG `PREREG.md` (md5 `4d73b7e825b841225eacb188e7ec86da`, commit `b0fe4df4`), viết trước số treatment.

## 0. Tóm tắt

1. **Q8/Q12 hết thua.** Hai rổ nhỏ chất lượng thay custom30V từng thua 2,9pp. Trên engine đã sửa,
   chênh lệch chỉ còn **+0,20 / +0,18pp ở pin0%** và **−0,63 / −0,36pp ở pin1M**, cả 4 số đều nằm
   trong sàn nhiễu. Verdict cũ NO-GO **hết ý nghĩa**. Mức thua dịch lên **≈ +3,1pp**, đúng chiều bug
   dự báo (rổ Q nhẹ ngân hàng hơn 12-14pp tỷ trọng).
2. **QF8 vẫn NO-GO** nhưng mức thua co từ −3,08pp về **−0,46 / −0,57pp**.
3. **Sector-cap và fincap: verdict cũ đa số không còn ý nghĩa.**
   - Sector-cap: Δ chỉ còn ±0,1pp ⇒ hết ý nghĩa.
   - fincap 0,45 / 0,55: hết ý nghĩa. Riêng fc45 hai quy ước còn trái dấu.
   - fincap 0,30 vẫn NO-GO (−0,43 / −1,59pp).
   - Không biến thể cắt ngân hàng nào **thắng** control. Cắt bank không còn bị phạt, nhưng cũng không
     được thưởng.
4. **L1 nới pool vẫn "chưa chứng minh", nhưng chắc hơn.**
   - L1b: **+2,86pp (pin0%) / +2,66pp (pin1M)**. LOO dương mọi năm. CI95 bootstrap **loại 0 ở pin0%**
     [+0,24; +4,29], còn ở pin1M sát mép [−0,06; +4,17].
   - **DSR 0,86 / 0,67 < 0,95** ⇒ vẫn trượt cổng.
   - Dự báo "edge thật lớn hơn số đã đo" chỉ đúng nhẹ (+0,24pp ở pin0%).
5. **Nhận định canonical "custom30V thắng nhờ BREADTH" KHÔNG còn đứng như đã viết** (H2 = False).
   - Trên toàn kỳ, rổ 8-12 tên chất lượng **ngang** custom30V.
   - Breadth chỉ thắng ở **IS 2014-19** (Q8/Q12 kém 2,1-3,9pp). Ngoài mẫu **2020+** thì đảo dấu
     (+1,4…+4,4pp), phần lớn đến từ 2020-21 và 2023.
   - Lý do cũ "MaxDD xấu hơn 3,9-6,5pp" cũng không còn: nay chỉ xấu hơn 0,4-0,9pp.
   - Đề xuất sửa câu canonical ở §5.
6. **H1 (bug có hướng) được ủng hộ về chiều.** Tương quan giữa (Δ mới − Δ cũ) và Δ tỷ trọng ngân hàng là
   **−0,52**: chân nào cắt bank nhiều thì được "trả lại" nhiều. Caveat: Δ cũ đo trên cache vintage khác,
   nên chỉ đọc chiều, không đọc biên độ.
7. **Có nên bật park lại không — so với leg park=0 đã pin (§4).**
   - Ở pin1M, park 0,7 control chỉ hơn park 0 **+0,69pp** CAGR, nhưng MaxDD xấu hơn **4,6pp**
     (Calmar 1,41 vs 1,84).
   - Không biến thể nào ở knob 0,7 vượt Calmar của park 0 tại pin1M.
   - Ứng viên duy nhất đáng xét khi lãi hạ: **L1b** (+3,35pp, DD −17,1% vs −13,9%), và phải đo lại ở knob
     ≤0,3 (mức ≥40% đã bị loại ở registry 09-27 ter-bis).

## 1. Control — tái lập pin, md5

| Chân | Lệnh (ngoài env chung `run_leg.sh`) | md5 | Pin | Kết quả |
|---|---|---|---|---|
| `n4_c30_off` | `BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off` | `4707bcbeb7e801d49a4a851ffd91d5e7` | `R3-anchor-pin0pct-sexies` | **BYTE-IDENTICAL** |
| `n4_c30_1m` | như trên, `IDLE_CARRY_TIER=dep1m` | `bcd0469f42c2f76937a6ebb10aae9b40` | `R3-pin1M-dau-TRAN-dai` | **BYTE-IDENTICAL** |
| `n4_c70_off` | như `c30_off`, `PARK_STATES=3:0.7` | `f524c1a086a80518f159daf3ae4740dd` | — (không có pin ở 0,7) | control của mọi chân |
| `n4_c70_1m` | như trên, dep1m | `c0084fae5027dfbe89d1d365247f1e77` | — | control của mọi chân |

- Engine: worktree `wt-repin-dep1m-2809` @ `03b12e46`, tức `f66dab18` + knob `BASKET_WDUMP` (env mặc định
  OFF, chỉ ghi file trọng số phụ). Control 0,3 byte-identical với pin ⇒ knob dump **không đổi một byte**
  output.
- Self-check 0 VND (BAL+LAG): **28/28 chân PASS**.
- Thanh khoản/dữ liệu: snapshot `bq_cache_asof20260729_postrestate`, threads=1, `$DNA_PYEXE`.
- Sự cố trong lúc chạy: 3 chân fincap lần đầu EXIT=1. Nguyên nhân là worktree thiếu `data/value_panel_2014.csv`
  (file gitignored, pinned PIT). Đã symlink về bản canonical rồi chạy lại. Log lỗi giữ ở
  `logs/n4_fc*_off.FAIL1.log`.
- Bank share control **49,2% trọng số toàn kỳ / 67,6% OOS**, khớp số đo độc lập ở Phần 0 vòng 4
  (49,1 / 67,5) ⇒ dump trọng số đáng tin.

## 2. Bảng đầy đủ — knob park 0,7

Δ tính so với **neo chấm verdict** (PREREG §4): mọi chân so với `c70`, riêng fc* so với `eyonly`.
Cột LOO = [min; max] của Δ CAGR khi bỏ từng năm. CI = bootstrap khối L=63, B=4000 trên chuỗi Δ log-return.
DSRx = DSR trên chuỗi excess, N=12. Bank = tỷ trọng TRỌNG SỐ ngân hàng trung bình ngày của rổ park.

### pin0% (SÀN — tiền nhàn rỗi 0%/năm) · PBO(13 cấu hình, CSCV S=16) = **0,039**

| Chân | CAGR | Sharpe | MaxDD | Calmar | ΔFULL | ΔIS 14-19 | ΔOOS 20+ | CI95 Δ | DSRx | LOO | Bank % (Δ) | vs park0 22,12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **c70 control** | 24,47 | 1,63 | −18,7 | 1,31 | — | IS 19,43 | OOS 29,27 | — | — | — | 49,2 | +2,35 |
| q8 | 24,67 | 1,56 | −19,1 | 1,29 | +0,20 | −3,87 | +4,41 | [−2,57; +2,82] | 0,153 | [−0,60; +0,90] | 36,8 (−12,4) | +2,55 |
| q12 | 24,65 | 1,61 | −18,1 | 1,36 | +0,18 | −2,13 | +2,53 | [−2,00; +2,18] | 0,156 | [−0,56; +0,65] | 35,6 (−13,6) | +2,53 |
| qf8 | 24,01 | 1,53 | −19,6 | 1,22 | −0,46 | −1,76 | +0,85 | [−3,53; +2,49] | 0,077 | [−1,24; +0,37] | 12,8 (−36,4) | +1,89 |
| secA | 24,41 | 1,62 | −18,5 | 1,32 | −0,06 | +0,29 | −0,41 | [−1,00; +0,80] | 0,101 | [−0,35; +0,35] | 36,8 (−12,4) | +2,29 |
| secB | 24,43 | 1,63 | −18,4 | 1,33 | −0,05 | +0,33 | −0,42 | [−0,88; +0,72] | 0,104 | [−0,29; +0,34] | 37,9 (−11,3) | +2,31 |
| secBx | 24,52 | 1,63 | −18,7 | 1,31 | +0,05 | +0,02 | +0,07 | [−0,31; +0,41] | 0,158 | [−0,13; +0,16] | 47,1 (−2,1) | +2,40 |
| eyonly | 24,70 | 1,66 | −17,5 | 1,41 | +0,23 | +0,53 | −0,07 | [−0,75; +1,21] | 0,214 | [−0,02; +0,45] | 45,8 (−3,4) | +2,58 |
| fc30 (vs eyonly) | 24,28 | 1,62 | −17,8 | 1,37 | −0,43 | +0,35 | −1,19 | [−1,63; +0,82] | 0,032 | [−0,80; +0,25] | 25,1 (−20,7) | +2,16 |
| fc45 (vs eyonly) | 24,90 | 1,65 | −17,3 | 1,44 | +0,19 | +1,92 | −1,50 | [−1,06; +1,34] | 0,192 | [−0,28; +0,56] | 35,0 (−10,8) | +2,78 |
| fc55 (vs eyonly) | 24,51 | 1,65 | −18,1 | 1,35 | −0,19 | +0,85 | −1,22 | [−1,15; +0,90] | 0,071 | [−0,74; +0,21] | 40,5 (−5,3) | +2,39 |
| l1a | 25,35 | 1,70 | −18,1 | 1,40 | +0,87 | +1,40 | +0,36 | [−0,60; +1,98] | 0,410 | [+0,40; +1,24] | 45,6 (−3,6) | +3,23 |
| l1b | 27,33 | 1,86 | −19,2 | 1,42 | **+2,86** | +2,51 | +3,21 | **[+0,24; +4,29]** | 0,863 | [+2,10; +3,49] | 37,2 (−12,1) | +5,21 |

### pin1M (TRẦN — dep1m Big-4 PIT) · PBO = **0,044**

| Chân | CAGR | Sharpe | MaxDD | Calmar | ΔFULL | ΔIS | ΔOOS | CI95 Δ | DSRx | LOO | vs park0 25,42 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **c70 control** | 26,11 | 1,73 | −18,5 | 1,41 | — | IS 21,09 | OOS 30,88 | — | — | — | +0,69 |
| q8 | 25,48 | 1,61 | −18,9 | 1,35 | −0,63 | −3,84 | +2,68 | [−3,02; +2,07] | 0,026 | [−1,40; −0,02] | +0,06 |
| q12 | 25,75 | 1,69 | −18,4 | 1,40 | −0,36 | −2,14 | +1,44 | [−2,34; +1,69] | 0,034 | [−1,00; +0,06] | +0,33 |
| qf8 | 25,54 | 1,63 | −19,3 | 1,32 | −0,57 | −1,27 | +0,14 | [−3,67; +2,61] | 0,031 | [−1,48; +0,28] | +0,12 |
| secA | 26,17 | 1,73 | −18,3 | 1,43 | +0,06 | +0,23 | −0,10 | [−0,90; +0,95] | 0,076 | [−0,24; +0,54] | +0,76 |
| secB | 26,21 | 1,73 | −18,3 | 1,43 | +0,10 | +0,27 | −0,08 | [−0,77; +0,88] | 0,086 | [−0,20; +0,53] | +0,79 |
| secBx | 26,04 | 1,72 | −18,5 | 1,41 | −0,07 | +0,04 | −0,19 | [−0,31; +0,16] | 0,021 | [−0,14; +0,11] | +0,62 |
| eyonly | 27,10 | 1,81 | −16,2 | 1,67 | +0,99 | +1,35 | +0,63 | [−0,41; +2,06] | 0,451 | [+0,62; +1,29] | +1,68 |
| fc30 (vs eyonly) | 25,51 | 1,70 | −17,5 | 1,46 | −1,59 | −0,68 | −2,49 | [−2,62; −0,01] | 0,000 | [−2,08; −1,25] | +0,09 |
| fc45 (vs eyonly) | 26,20 | 1,75 | −16,3 | 1,61 | −0,91 | +1,12 | −2,89 | [−2,02; +0,51] | 0,002 | [−1,47; −0,52] | +0,78 |
| fc55 (vs eyonly) | 26,82 | 1,80 | −17,9 | 1,50 | −0,29 | +0,59 | −1,15 | [−1,16; +0,68] | 0,019 | [−0,82; −0,02] | +1,40 |
| l1a | 28,00 | 1,89 | −16,3 | 1,72 | +1,89 | +2,22 | +1,57 | [−0,28; +3,30] | 0,598 | [+1,00; +2,27] | +2,58 |
| l1b | 28,77 | 1,95 | −17,1 | 1,68 | **+2,66** | +2,72 | +2,61 | [−0,06; +4,17] | 0,666 | [+1,72; +3,27] | +3,35 |

DSR kiểu vòng 4 (raw, null = SR control), để đối chiếu L1 cũ (0,656 / 0,778):

| Chân | pin0% | pin1M |
|---|---|---|
| l1a | 0,599 | 0,713 |
| l1b | 0,780 | 0,781 |

Δ per-year đầy đủ + LOO từng năm của mọi chân: `results.json`.
Chữ ký Q8/Q12 không đổi so với 07-12: âm hầu hết các năm 2014-19, dương mạnh 2020/2021/2023.
Ví dụ Q8 pin0% năm 2021 = +17,3pp. Chỉ có cả mức cộng lên ~3pp.

## 3. So 1 trục — `pin_ledger.py compare` trên kho SANDBOX

Kho sandbox: `PIN_STORE_WC_ROOT=/tmp/n4_pinstore.*`, không đụng `data/pinned_ledgers`.
Output ở `logs/compare_{off,1m,idle}.txt`. Tổng **33 rc=0 / 6 rc=2**, không có ca "cùng cấu hình, md5 khác"
⇒ **không có trục ẩn ngoài lệnh**.

- **rc=0 (đúng 1 trục), cả 2 quy ước:**
  - q8→q12 (`TOPN`)
  - c70→secA (`WT`), secA→secB (`SECCAP_MODE`), secB→secBx (`SECCAP_MODE`)
  - c70→eyonly (`SELECT`), eyonly→fc30 (`WT`), fc30→fc45 (`FIN_CAP`), fc45→fc55 (`FIN_CAP`)
  - c70→l1a (`CFO_POOL`), l1a→l1b (`CFO_POOL`)
  - 13 cặp off→1m (`IDLE_CARRY_TIER`)
- **rc=2, đã tìm ra trục, không ép:**
  - **c70→q8** khác 4 trục (`WT ew`, `TOPN 8`, `GATE_RATING 2`, `LIQ_FLOOR_B 5`). c70→qf8 khác 5 trục
    (thêm `QFLOOR`).
  - Đây là **một vehicle khai trước** (plan 07-12 định nghĩa Q-sleeve là bó 4-5 knob). Δ của chúng là Δ
    của **cả bó**, không tách được về knob nào. Câu hỏi gốc ("rổ nhỏ chất lượng thay custom30V") vốn
    là câu hỏi cấp bó, nên vẫn trả lời được, nhưng không được đọc thành "do TOPN" hay "do gate".
  - **q8→qf8** khác 2 trục (`GATE_RATING 2→none` + `QFLOOR`): cặp thay thế khai trước (floor Đ2 thay
    gate). Tương tự, chỉ đọc như bó.
- Neo verdict fc45/fc55 vs eyonly khác 2 trục (`WT` + `FIN_CAP`). Chuỗi eyonly→fc30→fc45→fc55 đều 1 trục,
  và verdict giữ đúng neo của 07-14.

## 4. Bảng verdict cũ → verdict trên engine sửa

| Nhánh | Δ cũ (registry) | Verdict cũ | Δ mới pin0% / pin1M | Dịch (pin0%) | ΔBank | Verdict mới |
|---|---|---|---|---|---|---|
| Q8 | −2,89 | NO-GO | +0,20 / −0,63 | **+3,09** | −12,4 | **HẾT Ý NGHĨA** |
| Q12 | −2,93 | NO-GO | +0,18 / −0,36 | **+3,11** | −13,6 | **HẾT Ý NGHĨA** |
| QF8 | −3,08 | NO-GO | −0,46 / −0,57 | +2,62 | −36,4 | ĐỨNG (NO-GO, biên nhỏ) |
| secA fix50 | −0,21 | NO-GO | −0,06 / +0,06 | +0,15 | −12,4 | HẾT Ý NGHĨA |
| secB mktcap | −0,16 | NO-GO | −0,05 / +0,10 | +0,11 | −11,3 | HẾT Ý NGHĨA |
| secB×1,5 | −0,04 | NO-GO | +0,05 / −0,07 | +0,09 | −2,1 | HẾT Ý NGHĨA |
| eyonly (neo fincap) | −0,05 | trung tính | +0,23 / +0,99 | +0,28 | −3,4 | HẾT Ý NGHĨA (pin1M dương, chưa chứng minh) |
| fincap 0,30 | −0,64 | NO-GO | −0,43 / −1,59 | +0,21 | −20,7 | **ĐỨNG (NO-GO)** |
| fincap 0,45 | −0,84 | NO-GO | +0,19 / −0,91 | +1,03 | −10,8 | HẾT Ý NGHĨA (2 quy ước trái dấu) |
| fincap 0,55 | −0,32 | NO-GO | −0,19 / −0,29 | +0,13 | −5,3 | HẾT Ý NGHĨA |
| L1a pool 90 | +1,07 | chưa chứng minh | +0,87 / +1,89 | −0,20 | −3,6 | ĐỨNG (dương, chưa chứng minh) |
| L1b pool 120 | +2,62 | chưa chứng minh | +2,86 / +2,66 | +0,24 | −12,1 | ĐỨNG (dương, chưa chứng minh — CI loại 0 ở pin0%, DSR 0,86) |

Nguồn Δ cũ (theo TÊN MỤC trong registry):
- "2026-07-12 — Q-SLEEVE"
- "Sector-cap cho custom30V"
- "`v4final` — thiết kế tổng hợp" và "`v4final` A4 (DY tie-break) + quét cap theo ĐỈNH"
- "KẾT QUẢ THAM CHIẾU phiên 2026-09-09 (d)"

Đọc H1:
- Ba chân Q dịch +2,6…+3,1pp, trong khi seccap dịch chỉ +0,1pp dù cũng cắt ~12pp bank. Lý do: seccap đổi
  **trọng số trên cùng tập tên**, còn Q đổi **tập tên**.
- Gợi ý rút ra: bug phạt theo **tên phát CP thưởng** (bước OShares) hơn là theo tỷ trọng ngành thuần.
  Đây là suy luận, chưa đo trực tiếp.

## 5. Kết luận — nhận định canonical "custom30V thắng nhờ breadth"

**Không còn đứng như đã viết ở registry 07-12.** Theo luật PREREG §4: Q8 và Q12 đều HẾT Ý NGHĨA ⇒ claim
phải sửa. Đề xuất thay bằng câu sau (chờ Mike/user duyệt):

> Trên engine đã sửa (2026-10-09), rổ nhỏ 8-12 tên chất lượng (gate≤2, ew, sàn thanh khoản 5B) **ngang**
> custom30V trên toàn kỳ 2014-2026 ở knob park 0,7 (Δ +0,2 / −0,6pp, trong nhiễu). Breadth chỉ thắng ở
> IS 2014-19 (−2,1…−3,9pp — thị trường mỏng). Ngoài mẫu 2020+ thì đảo (+1,4…+4,4pp, tập trung 2020-21/2023).
> Không có lý do đổi vehicle; cũng không còn lý do nói breadth là nguồn edge của custom30V.

Những điều KHÔNG đổi:
- QF8 vẫn NO-GO.
- fincap 0,30 vẫn NO-GO, và ở pin1M CI loại 0 về phía âm.
- Không biến thể de-bank theo trọng số nào thắng.
- Kết luận cấu trúc 07-14 "DD không đến từ thứ nằm trong selector" vẫn khớp: seccap/fincap đổi MaxDD
  ≤ ±0,6pp.
- L1 vẫn là đòn bẩy duy nhất có dấu nhất quán (LOO dương 13/13 năm, cả 2 quy ước). Nhưng DSR < 0,95, nên
  vẫn **chưa chứng minh**.
- Cái giá thanh khoản của L1b (−71% ADV rổ, đo ở 09-09) không đổi.

## 6. Hàm ý cho câu hỏi "bật park lại khi trigger lãi hạ"

Mọi dòng "vs park0" ở §2 khác **≥2 trục** so với leg park=0 (knob park + biến thể rổ) ⇒ đây là
**tham khảo, không phải A/B**.

| Ở pin1M (lãi huy động 1T Big-4) | CAGR | MaxDD | Calmar |
|---|---|---|---|
| park 0 (pin `a6ba34d8`) | 25,42 | −13,9 | 1,84 |
| c70 custom30V park 0,7 | 26,11 | −18,5 | 1,41 |
| l1a park 0,7 | 28,00 | −16,3 | 1,72 |
| l1b park 0,7 | 28,77 | −17,1 | 1,68 |

- Không biến thể nào ở knob 0,7 vượt Calmar của park 0 tại pin1M.
- Lãi Trứng vàng hôm nay (~8,5% net, tầng 3) còn cao hơn dep1m ⇒ mẫu số thật còn khó hơn pin1M.
  **Giữ park=0 là nhất quán với số.**
- Nếu trigger lãi hạ kích hoạt, đề xuất:
  1. Đo lại ở **knob ≤0,3** (mức ≥40% bị loại ở registry 09-27 ter-bis).
  2. Chỉ với 2 chân **c30 và l1b@0,3** — 1 trục, tiền đăng ký mới.
  3. Không quét thêm pool (sẽ chết ở DSR).

## 7. Tái lập

```bash
D=mike/agents/Taylor/research/rerun_groupB_fixed_20261009
# code: worktree wt-repin-dep1m-2809 @ 03b12e46 (+ symlink data/value_panel_2014.csv -> canonical)
$D/run_leg.sh n4_c30_off BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off   # phải ra 4707bcbe
$D/run_leg.sh n4_c30_1m  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m # phải ra bcd0469f
$D/run_leg.sh n4_c70_off BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 IDLE_CARRY_TIER=off
$D/run_leg.sh n4_c70_1m  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7 IDLE_CARRY_TIER=dep1m
xargs -P 8 -L 1 $D/run_leg.sh < $D/legs.txt          # 24 chân treatment
$DNA_PYEXE $D/analyze.py > $D/logs/analyze.txt      # verify manifest md5 + mọi bảng ở trên
$D/compare_sandbox.sh                                # luật 1 trục, kho sandbox
```

Artifact:
- `results.json` (md5 `7231e75a…`)
- `dsr_family_manifest_n4.json` (26 ledger, md5 `f765b125…`)
- `logs/analyze.txt`, `logs/compare_*.txt`, `logs/n4_*.log`
- `w/n4_*.csv` (trọng số ngày)
- Ledger CSV `data/v23_golive_audit_2014_now_*_exp_n4_*_univpit*.csv` (tên không canonical)

Giới hạn:
- Chỉ đo ở knob 0,7. Treatment ở 0,3 chưa chạy.
- Q12-BULLEXT ngoài phạm vi (nhóm A).
- Δ cũ đo trên vintage cache khác, nên cột "dịch" lẫn bug + vintage.
- DSR của chân fc* dùng SR0 của họ excess-vs-c70 (gần đúng).

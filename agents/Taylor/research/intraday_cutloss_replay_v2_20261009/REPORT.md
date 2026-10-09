# REPLAY v2 — cổng giá trong phiên sau khi sửa 3 lỗ hổng + chia theo thanh khoản (SHADOW)

Job `Taylor_20261009_110243` · 09/10/2026 · PAPER-ONLY. Tiếp nối v1 (`../intraday_cutloss_replay_20261009/REPORT.md`)
và phản biện quant-skeptic REFUTED medium (`logs/verify_20261009_104604_2121601.log`). Watcher vẫn SHADOW, ngưỡng
kích hoạt không đổi, crontab không đổi. **Mọi đề xuất chỉ là đề xuất — không wire.** Giả thuyết ghi trước ở
`PREREG.md` (commit cùng lượt, viết trước khi chạy replay v2).

## TL;DR

1. **PHẦN 1 đã merge** `9a1eeede` vào master mike (feature `e770f446` + `5197f182` + `b727daa1`).
   - arch-review vòng 1: NEEDS_CHANGES. Lỗi chặn: ca kích hoạt sau 14:00 mà phán quyết được xử lý ở phiên sau vẫn tự bán.
   - Vòng 2: APPROVED_WITH_NITS; các nit đã sửa.
   - Selfcheck 341/341 dưới `env -u TZ`, `TZ=America/New_York` và `python3`. 13/13 đột biến trên nhánh mới bị bắt.
   - Shadow chạy code mới từ phiên **Thứ Hai 12/10**.
2. **H1 (pre-register) = SUPPORTED, tức là KHÔNG KÉM HƠN; chưa đạt mức "tốt hơn".**
   - Phạm vi: mã có ADV20 ≥ 10 tỷ, kịch bản agent kết luận GÃY ⇒ bán hết.
   - T+5: cutloss hơn giữ **+1,06%**, CI[−0,61; +2,68]; N = 104 ca / 85 ngày.
   - T+1: +0,17% [−0,90; +1,26]. T+20: +1,19% [−2,06; +4,47].
   - Kết quả bền: cùng dấu qua cả 6 cấu hình sổ lệnh và cả 2 nửa thời gian.
   - CI vẫn chứa 0 ⇒ **không có edge dương có ý nghĩa**. Bán tự động trên mã thanh khoản cao chỉ ngang giữ, không thua.
3. **Thanh khoản đúng là trục quyết định**, như skeptic chỉ ra. Riêng nhóm ADV < 1 tỷ:
   - T+5 **−4,49%** CI[−6,52; −2,74] (12 ca, universe v2); −3,64% (55 ca, universe v1).
   - Nhưng **lỗ ở mã nhỏ KHÔNG phải do giả định sổ lệnh**: mã giá < 5.000đ lỗ −5,3% đến −5,4% ở T+1 trong CẢ 6 cấu hình (khớp 100%, kể cả 1 bước giá/1× KL). Lỗ đến từ hành vi giá: giảm sâu trong phiên rồi hồi.
   - N nhỏ (8 ca) ⇒ chỉ mang tính mô tả.
4. **3 luật mới loại đúng các nhóm ca tệ nhất.** Trên 298 ca riêng của code cũ (universe v2):
   - (C) ca hoãn sang phiên sau ⇒ GIỮ: 53 ca. Với code cũ T+20 là **−2,99%**.
   - (B) chạm sàn khi VNI ≤ −2% ⇒ gộp: 11 ca. Với code cũ T+20 là **−9,81%**.
   - (A) chuyển sang gộp theo cửa sổ 60', hoặc mở riêng rồi bị gắn nhãn sau: 25 + 37 ca.
   - Tác động cấp chính sách, tính trên mọi ca cũ (ca code mới không bán = 0): T+5 −0,38% → **+0,06%**; T+20 −2,01% → **−0,82%**.
5. **Control PNJ 06–09/10 chạy lại độc lập**: 3/3 kích hoạt tái tạo trên cả code mới lẫn cũ, đúng ngày (live quét lúc 11:10/11:00/11:00, replay lúc 11:00). Ngày 09/10 không kích hoạt, khớp với live.
6. **Khuyến nghị: vẫn CHƯA live, tiếp tục SHADOW.**
   - Nếu sau này cho tự bán, cổng tự nhiên là **ADV20 ≥ 10 tỷ** và **tuyệt đối không tự bán mã ADV < 1 tỷ**.
   - Cần quant-skeptic + user duyệt trước khi wire.
   - Bộ OOS thật nay tích luỹ tự động (EOD_OOS) để kiểm H1 trên dữ liệu chưa thấy.

## 1. PHẦN 1 — sửa code (đã merge `9a1eeede`)

| Luật | Hành vi mới | Chỗ code |
|---|---|---|
| (A) gộp cửa sổ | Đếm số mã PHÂN BIỆT kích hoạt trong **60 phút GIAO DỊCH** (trừ nghỉ trưa 11:30–13:00); ≥3 mã, hoặc ≥2 mã chạm sàn ⇒ gộp cả thị trường. Ca riêng mở trong cửa sổ được gắn nhãn `market_wide`: mặc định ⇒ GIỮ; bán mô phỏng đang chạy THEO MẶC ĐỊNH dừng (`STOPPED_MARKET_WIDE`). Lệnh của user vẫn được tôn trọng. Ghi log `MARKET_WIDE_RELABEL` + gửi tin. | engine `window_market_wide_reason`/`in_window`; driver `_scan`, `_relabel_market_wide` |
| (B) chạm sàn | Chỉ mở ca riêng khi idio đạt −4%. Chạm sàn ∧ VNINDEX ≤ −2% ⇒ nhánh gộp, kể cả khi idio đạt (đúng nguyên văn đề bài). | `trigger_check` → `individual`/`floor_mw` |
| (C) ca hoãn | **Mọi** ca được quyết ở phiên sau ⇒ không tự bán qua ATO; mặc định GIỮ, phán quyết chỉ còn là gợi ý (`actions_suggested`); xét lại lúc mở phiên. "Ca hoãn" gồm: T0 ≥ 14:00, hạn trả lời > 14:15 (T0 khoảng 13:45 trở đi), hoặc phán quyết được xử lý ở phiên sau. Tin 08:30 nhắc kèm gợi ý. | `_hold_override_reason`, `process_case` |
| (D) OOS | 14:55: ghi dòng `EOD_OOS` gồm `vni_day`, `ret_close` (+ `close_final`; UPCOM = False vì khớp tới 15:00) cho mọi ca và mã gộp. Đến ≥14:58 vẫn chưa ghi được ⇒ health_alert. | `_eod_oos` |

Diễn giải và giới hạn cần user biết:
- (C) rộng hơn chữ "sau 14:00": phủ cả ca có hạn trả lời rơi sau 14:15. Đây chính là nhóm "hoãn" có kết quả tệ trong v1.
- **Gộp "dính"**: khi còn ≥3 mã đang giảm, mọi kích hoạt mới trong ngày đều bị gộp, không mở ca điều tra. Thiết kế này nghiêng về an toàn.
- `EOD_OOS` ghi kiểu at-least-once ⇒ reader sau này phải dedupe theo (ngày, mã).
- Replay arch-reviewer trên code mới:
  - 26/10/2023: 11 ca riêng → còn 2 ca, cả 2 bị gắn nhãn GIỮ.
  - VHM 22/07/2026 → gộp.
  - SHS/VIX/VND 20/07/2026 → gộp lúc 13:30, nhưng 2 lệnh bán theo mặc định đã khớp xong trước đó.

## 2. Thiết kế replay v2 (theo `PREREG.md`)

- **Code**: bản chụp `new_bin/` = `9a1eeede`, `old_bin/` = `5050f6fa`. Không đọc `mike/bin` sống ⇒ tái lập được.
- **Driver**: `replay_v2.py` tái dùng nguyên `replay.py` v1 (HistMarket, nguồn bar, `run_tick` thật, tiêm phán quyết), chỉ thay universe, tham số sổ lệnh và ghi thêm `bar_t`.
- **Universe v2**:
  - Ledger R3 point-in-time (BAL/LAG/CUSTOM30V), **lọc ADV20 ≥ 1 tỷ**.
  - ∪ 14 mã SpaceX/ZaloPay đang giữ ngày 09/10 (PVT DRI SCL SIP VPB MSB VIB TPB MBB VNM TV1 SAB NCT VPI), giữ giả định suốt kỳ, mỗi mã 5% NAV.
  - NAV mô phỏng **50 tỷ**, thay cho 1 tỷ của v1.
  - Từ 2026-07-09 dùng vị thế THẬT, như v1.
- **Universe v1** (ledger nguyên, NAV 1 tỷ) chạy lại trên cả code cũ và mới để so. Bù thêm bar 15' vnstock cho 39 mã thiếu (vd SSI trước đây chỉ có từ 06/2025) ⇒ số v1 chạy lại khác nhẹ REPORT v1: T+1 −1,22% thay vì −1,45%.
- **Lọc dữ liệu lỗi** (khai trước):
  - P1 == TC (ngày không giao dịch);
  - Vol(D) = 0 hoặc Vol(D+1) = 0;
  - quote cũ: bar mới nhất nhìn thấy tại T0 cũ hơn 60'.
  - Số ca bị loại: v2 = 17/162 (3 P1==TC, 14 quote cũ); v1 chạy lại = 64/357 (15 P1==TC, 38 Vol=0, 19 quote cũ).
- **Công thức chấm** giữ nguyên v1 (`analyze.score_exec`):
  - E_k = giá bán ròng / giá nếu giữ tại D+k − 1, **dương = cutloss thắng**.
  - Phí 0,097%×2 + impact 0,5·σ20·√(KL/ADV20).
  - Không dùng cột `profit_*`.
  - CI bootstrap theo cụm ngày, 2000 lần, seed 7.
- **Tự kiểm**: tính lại H1 trực tiếp từ `out/v2_new_exec.csv` (không qua hàm tóm tắt): N 104 / 85 ngày, E5 = +1,0643%, khớp bảng.

## 3. H1 — kết quả (code mới, universe v2, BROKEN, ADV20 ≥ 10 tỷ, đã loại ca lỗi)

| h | N ca/ngày | mean | CI95 | trung vị | thắng | bán oan |
|---|---|---|---|---|---|---|
| T+0 | 104/85 | −0,88 | [−1,39; −0,38] | −0,34 | 37% | 47% |
| T+1 | 104/85 | +0,17 | [−0,90; +1,26] | +0,10 | 51% | 48% |
| **T+5** | **104/85** | **+1,06** | **[−0,61; +2,68]** | +0,96 | 56% | 43% |
| T+20 | 104/85 | +1,19 | [−2,06; +4,47] | +1,56 | 54% | 45% |

- **Luật PREREG**: N ≥ 30 ngày ✓; mean ≥ 0 ✓; CI dưới −0,61 > −1,0 ✓; CI dưới ≤ 0 ⇒ **SUPPORTED** (không kém hơn, biên 1 điểm %), không phải STRONG.
- **Độ bền, sổ lệnh**: T+5 lần lượt +1,10 / +1,04 / +1,08 / +1,06 / +1,10 / +1,08 ở 0,25×·1 bước, 0,25×·3, 0,5×·1, 0,5×·3, 1×·1, 1×·3. Cùng dấu ✓. Mã thanh khoản cao gần như không nhạy với giả định sổ lệnh.
- **Độ bền, 2 nửa thời gian**: 2023-09→2024-12 +2,48 (24 ca); 2025-01→2026-10 +0,64 (80 ca). Cùng dấu ✓.
- **Bán ngay tại T0** (bỏ 10–20' điều tra + chờ trả lời): T+5 +0,98, gần như y hệt ⇒ trễ quy trình không phải yếu tố chính.
- **UNCLEAR** (bán 50%, tính trên toàn vị thế, ADV ≥ 10 tỷ): T+1 −0,01 · T+5 +0,21 [−0,59; +0,97] · T+20 −0,47. Trung tính.

## 4. Theo thanh khoản / mức giá / book (BROKEN, bỏ ca lỗi)

| Nhóm | v2 code mới (N ca/ngày) · T+1 · T+5 · T+20 | v1 code cũ (N) · T+1 · T+5 · T+20 |
|---|---|---|
| ADV < 1 tỷ | 12/11 · −2,31 · **−4,49** · −6,14 | 55/50 · −4,45 · **−3,64** · −5,10 |
| ADV 1–10 tỷ | 28/25 · +0,63 · +2,43 · +1,90 | 36/27 · +0,21 · +1,95 · +0,49 |
| ADV ≥ 10 tỷ | 104/85 · +0,17 · +1,06 · +1,19 | 199/126 · +0,14 · +0,77 · +0,69 |
| giá < 5.000đ | 0 (universe lọc ADV) | 12/10 · **−5,41** · −4,43 · −6,23 |
| book LAG | 35/29 · −0,21 · +1,32 · −1,17 | 117/80 · −2,43 · −1,68 · −4,51 |
| book BAL / CUSTOM30V | +1,00 / +0,15 · +1,07 / **+2,69** [+0,16; +5,24] | +0,70 / +0,16 · +1,55 / +0,96 |
| LIVESET (14 mã đang giữ, giả định) | 17/17 · −1,00 · −2,99 · −0,52 | — |

Đọc bảng:
- Khi đã lọc thanh khoản, book LAG không còn thua rõ (v2 T+5 +1,32). Phân nhóm book/sàn của đề xuất A cũ chủ yếu là thanh khoản trá hình, đúng như skeptic nói.
- CUSTOM30V T+5 có CI dương nhưng là phân nhóm hậu nghiệm ⇒ không kết luận.
- Nhóm LIVESET (mã CÒN giữ hôm nay, gán giữ suốt 2023–26) cho kết quả bất lợi cho cutloss. Khớp thiên lệch survivorship đã khai trước: mã sống sót tới nay là mã đã hồi.

**Độ nhạy sổ lệnh trên mã nhỏ** (universe v1, code mới, T+1):

| Nhóm | Kết quả qua 6 cấu hình | Tỷ lệ khớp |
|---|---|---|
| giá < 5k | −5,26 đến −5,36 | 100% |
| ADV < 1 tỷ | −3,83 đến −5,03 | 83–94% |

Skeptic giả thuyết rằng lỗ ở mã nhỏ do "sổ 3 bước giá ăn 5–20%". Dữ liệu **không ủng hộ** điều đó: 1 bước giá + 1× KL vẫn lỗ như cũ. Lỗ đến từ giá — bán gần đáy trong phiên rồi giá hồi — hoặc từ bar 15' thô của mã ít giao dịch. Kết luận thực hành vẫn vậy: **không tự bán mã kém thanh khoản**.

## 5. Luật mới vs cũ — ca riêng của code cũ đi đâu (BROKEN, cấu hình gốc)

| Số phận dưới code mới | universe v2 | universe v1 | B T+5 cũ → mới (v2) | B T+20 cũ → mới (v2) |
|---|---|---|---|---|
| vẫn ca riêng | 139 | 180 | −0,41 → −0,41 | −1,75 → −1,75 |
| (C) ca hoãn ⇒ GIỮ | 53 | 82 | −1,81 → 0 | **−2,99** [−5,93; −0,33] → 0 |
| (A) ca riêng → gắn nhãn gộp sau | 37 | 45 | +1,25 → +2,13 | −2,46 → −0,37 |
| (A) gộp theo cửa sổ 60' | 25 | 22 | +0,21 → 0 | −0,39 → 0 |
| (A) hệ quả: gộp ngay trong 1 lượt* | 33 | 21 | +0,44 → 0 | +0,57 → 0 |
| (B) chạm sàn ∧ VNI ≤ −2% ⇒ gộp | 11 | 12 | −1,43 → 0 | **−9,81** [−18,8; −0,5] → 0 |
| (B) chạm sàn, idio chưa đạt ⇒ gộp | 0 | 2 | — | — |
| **Chính sách, mọi ca cũ** | 270/161 | 291/177 | **−0,38 → +0,06** | **−2,01 → −0,82** |

Ghi chú bảng:
- B = % giá trị vị thế theo TC, dương = cutloss hơn giữ. Ca code mới không bán tính = 0. Đã loại ca lỗi dữ liệu.
- \* Mã đã chuyển sang gộp không chiếm "1 ca/ngày", nên được quét lại ở các lượt sau và làm đủ 3 mã trong 1 lượt.
- Universe v1, cấp chính sách: T+1 −0,79 → −0,44; T+5 −0,45 → +0,02; T+20 −2,29 → −0,89.
- Số ca riêng code mới / cũ: v2 237 / 298, v1 315 / 364.

## 6. Kết luận & đề xuất (CHỈ ĐỀ XUẤT)

- **Live: CHƯA.** H1 không kém hơn nhưng không có edge dương có ý nghĩa. Tự bán không đem lại lợi rõ ràng; giá trị thực của cổng là **báo + điều tra**, không phải bán.
- **Nếu user muốn mở tự bán** (sau khi bộ OOS live xác nhận):
  - Chỉ áp cho mã **ADV20 ≥ 10 tỷ**, với phán quyết GÃY của agent.
  - Mã **ADV < 1 tỷ: KHÔNG BAO GIỜ tự bán**: lỗ nhất quán −3,6% đến −4,5% ở T+5, qua cả 2 universe và mọi giả định sổ lệnh.
  - Nhóm 1–10 tỷ: chưa đủ N để kết luận.
- 3 luật (A)(B)(C) đã merge ở dạng shadow. Replay cho thấy chúng loại đúng các nhóm ca tệ nhất. **Không có thay đổi ngưỡng nào.**
- **Việc tiếp theo**: tích luỹ `EOD_OOS` từ 12/10. Khi có ≥30 ngày ca live ADV ≥ 10 tỷ, kiểm lại H1 out-of-sample bằng đúng luật PREREG này.

## 7. Giới hạn

- Phán quyết agent là giả định (luôn GÃY, hoặc luôn CHƯA RÕ). Agent thật có thể phân biệt tốt hơn.
- Trước 07/2026 dùng bar 15': kích hoạt có thể trễ tới 15'. Sàn giao dịch không point-in-time. 7,8% (ngày, mã) không có bar (v1); v2 đã bù 39 mã.
- LIVESET là tập mã chọn hôm nay ⇒ thiên lệch survivorship (đã khai trước).
- "Giữ tới T+20" bỏ qua việc chiến lược cũng tự thoát vị thế. Bỏ qua ràng buộc T+2.
- Biên không-kém-hơn 1 điểm % do Taylor chọn trong PREREG, chưa qua user.
- H1 là giả thuyết duy nhất được đánh giá theo luật quyết định; mọi phân nhóm khác chỉ mô tả, chưa hiệu chỉnh kiểm định bội.

## Tái lập

```bash
cd agents/Taylor/research/intraday_cutloss_replay_v2_20261009
PY=/home/trido/thanhdt/wc_venv/bin/python
# cache dùng chung với v1 (../intraday_cutloss_replay_20261009/cache, + vn15 bù: fetch_vnstock.py <file mã>)
./run_stage1.sh    # v2 universe, code new+old, BROKEN gốc, mọi ngày (days/hist_*.txt, days/live.txt)
./run_stage2.sh    # casedays.py → độ nhạy sổ lệnh + UNCLEAR (case days) + v1 universe new/old (mọi ngày)
./run_stage3.sh    # độ nhạy sổ lệnh universe v1 (mã <5k / ADV<1 tỷ)
$PY replay_v2.py --code new --scenario NONE --days days/pnj.txt --tail 0 --out runs/pnj_new   # control PNJ (+ --code old)
$PY final_v2.py    # → out/final_v2.txt + out/*_exec.csv, fate_*.csv, policy_*.csv
```

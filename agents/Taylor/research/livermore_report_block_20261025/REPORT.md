# Livermore REPORT_BLOCK: khối Kỹ thuật cho weekly/monthly (job Taylor_20261025_092234)

**Trạng thái:** đã dựng trên nhánh `feat/livermore-report-block-20261025`, worktree `/home/trido/thanhdt/WorkingClaude/wt-livermore-report-block-20261025`. Hai commit: `0dbcc1334` (bản dựng) và `323e39b21` (sửa theo arch-review vòng 1). **Chưa merge, chưa cài cron.**
**Arch-review:** vòng 1 NEEDS_CHANGES (4 lỗi, đã sửa hết). Vòng 2 APPROVED, không còn thay đổi bắt buộc.
Diffstat (`git diff --numstat fe2af8d30 323e39b21`):

| File | Thêm | Bớt |
|---|---|---|
| `livermore_report_block.py` | 543 | 0 |
| `livermore_report_block_selfcheck.py` | 392 | 0 |
| `report_delivery_gate.py` | 18 | 0 |
| `check_report_cadence.sh` | 11 | 2 |
| `check_report_cadence_selfcheck.py` | 10 | 1 |
| `livermore_reads.md` (đầu sổ) | 2 | 1 |

## Thiết kế

**Lệnh chính:** `bin/livermore_report_block.py ensure --kind weekly|monthly --period-end D`. Lệnh có khoá và idempotent: chạy lại thì trả ngay khối đã có.

1. **Xác định as_of.** as_of là phiên cuối cùng ≤ `period_end`. Bắt buộc ba điều kiện:
   - kỳ đã đóng (as_of ≤ `expected_last_session`);
   - có bar đúng ngày as_of;
   - với monthly, `period_end` phải là ngày cuối tháng.
2. **SỐ LIỆU (FACTS) do script tính, Livermore không tự sinh số nào.**
   - Nguồn: VNINDEX OHLCV và các cột chỉ báo của bảng `ticker` (MA20/50/200, D_RSI, D_MACDdiff, D_CMF).
   - MA của BQ được đối chiếu với SMA tự tính từ bar; lệch quá 0,1% thì FAIL.
   - Độ rộng tính theo `universe_pit` point-in-time. Không có dữ liệu thì khối ghi một câu cố định, không chặn cả khối.
3. **Dự báo** (tính trên các lần đọc có `as_of` ≤ as_of của kỳ, tức là mù với mọi thứ sau đó):
   - **Lần đọc gần nhất cách dưới 20 phiên** (tính MỌI loại, kể cả LIVE-BASELINE và MANUAL): khối chỉ NHẮC LẠI dự báo nguyên văn từ sổ.
   - **Cách từ 20 phiên trở lên:** gọi `livermore_run.sh --triggers REPORT_BLOCK_WEEKLY|MONTHLY`, ghi sổ như mọi lần đọc khác.
   - **Không lập dự báo lùi ngày.** Hai trường hợp sau cho chế độ NONE, khối ghi "không có dự báo được lập cho kỳ này":
     - báo cáo soạn trễ hơn 5 phiên;
     - sổ đã có một lần đọc nằm sau as_of trong vòng 20 phiên.
4. **Lời bình của Livermore.** Gọi agent `livermore` với cwd ở `/tmp` và cùng bộ cờ như `livermore_run.sh`. Prompt chỉ chứa FACTS, không có DT5G. Kết quả là đúng 5 dòng: Xu hướng, Hỗ trợ/kháng cự, Động lượng, Thanh khoản, Độ rộng.
5. **Kiểm cơ học, sai thì fail-closed.** Thử lại tối đa 2 lần, lần sau có kèm danh sách lỗi.
   - Đúng khung nhãn.
   - Mọi số và mọi ngày phải có trong FACTS. Số có dấu phải khớp cả dấu. Chỉ bỏ qua các định danh MA20/MA50/MA200/RSI(14).
   - Không có từ cấm: DT5G, tên trạng thái, tên hệ thống nội bộ, lời khuyến nghị mua/bán. Từ cấm cũng được kiểm trên dòng dự báo chép từ sổ.
6. **Ghi kết quả.** Ghi `data/livermore/report_block_<as_of>_<kind>.md` trước, rồi đến `.json` (status, sha256, forecast, facts). File `.json` là dấu commit. Khi FAIL thì ghi `.FAILED.json` kèm lý do; mọi exception đều đi vào nhánh này.
7. **Cổng giao báo cáo** `report_delivery_gate.py::_check_livermore_block` (fail-closed, chạy trước Discord/email):
   - kỳ có khối PASS mà báo cáo không chứa khối đó NGUYÊN VĂN ⇒ CHẶN;
   - không có khối PASS mà báo cáo vẫn gắn tên Livermore ⇒ CHẶN;
   - không có PASS, không gắn tên (khối do người soạn tự viết, tức đường fallback) ⇒ QUA.
8. **Chỗ gắn vào quy trình soạn.** Thêm `LIVERMORE_STEP` vào prompt weekly và monthly trong `check_report_cadence.sh`; đây là nơi soạn duy nhất (đã grep "Toàn cảnh thị trường"). Hướng dẫn cho người soạn:
   - chạy `ensure` ở chế độ nền;
   - PASS thì dán nguyên văn khối rồi chạy `verify-report`;
   - FAIL thì tự viết khối, không ghi Livermore là nguồn. File ZaloPay có dòng cờ ⚠️ kèm lý do; file SpaceX không nhắc gì tới sự cố.
   - Mục Cơ bản/định giá (Value Radar, DT gate) giữ nguyên.
9. **Ghi rõ nguồn và giới hạn.** Tiêu đề khối có "nhận định độc lập của Livermore". Có dòng dự báo đang mở (ngày lập, ngày chấm, điều kiện vô hiệu nguyên văn). Có dòng nói số dự báo đã chấm điểm hiện là 0, nên chưa đủ để đánh giá, và kiểm thử lịch sử chưa cho thấy dự báo này tốt hơn giả định "thị trường tăng". Không có lời hứa nào về độ chính xác.

**Lệch so với spec:** tên file có thêm `_<kind>`. Lý do: thứ Sáu 30/10/2026 vừa là ngày cuối tuần vừa là ngày cuối tháng, weekly và monthly sẽ trùng tên.

## Selfcheck (đã chạy thật trong phiên này)

| Bộ kiểm | Kết quả |
|---|---|
| `livermore_report_block_selfcheck.py` | 47/47 assertion dưới cả 3 TZ (bỏ TZ, America/New_York, UTC); 15/15 mutant bị bắt bằng assertion (crash không được tính là bắt) |
| `check_report_cadence_selfcheck.py` | 64/64 (thêm #25g, #28, #28b) |
| `report_delivery_gate_selfcheck.py` | 7/7 delivery + 5/5 period-return |

- Không selfcheck nào gọi claude thật: dùng `LIVERMORE_CLAUDE_BIN` giả.
- Có test cho: số lạ, ngày lạ, làm tròn, sai dấu, `EMA 1800`, `RSI(70)`, as-of lệch, kỳ chưa đóng, MA lệch, biên khoảng cách 19 và 20 phiên, mù về sau, báo cáo trễ, từ cấm trong sổ, cổng nguyên văn.

## Chạy thử (dry-run)

Dùng Livermore thật, nhưng sổ là BẢN SAO `dryrun/livermore_reads_COPY.md`, dữ liệu ghi vào `dryrun/data/`. Sổ thật và `mike/data/livermore` không bị chạm. Không gửi gì ra ngoài.

| Kỳ | Kết quả | Dự báo |
|---|---|---|
| weekly 19–23/10/2026 | PASS lần 1 | REPEAT: nhắc lại LVR-2026-10-21 (cách 2 phiên) |
| monthly 09/2026 | PASS lần 1 | NEW: GIẢM, P_UP 0.42, mức 1763.62 BREAK, chấm 28/10 (chỉ nằm trong sổ bản sao) |

Cả hai khối PASS lại khi chạy validator vòng 2.

### Khác biệt so với khối cũ đã phát hành: weekly 19–23/10

So với `reports/SpaceX_weekly_report_2026-10-19_to_2026-10-23.md`.

**Số giống nhau:** đóng cửa 1.774,15 (+4,00%); MA20, MA50, MA200; RSI 32,9→57,2; MACD −6,06→+5,86; CMF −0,20→+0,01; khối lượng 716 vs 584 triệu (+22,7%); phiên 948 triệu; độ rộng 46,5% (342 mã) vs 31,6% (345 mã); độ rộng cao nhất/thấp nhất trong kỳ 48,7% / 32,9%.

**Số khác nhau:**

| Mục | Khối cũ | Khối mới | Ghi chú |
|---|---|---|---|
| Chuỗi phiên tăng | "3 phiên tăng liên tiếp từ 21/10" | 4 phiên | Khối cũ SAI: 20/10 đóng 1.691,97, cao hơn 1.689,84 của 19/10 |
| Đáy 3 tháng | 1.651,2 (cột `LO_3M_T1`, 3 tháng lịch, đáy 28/07) | 1.675,19 ngày 29/07 | Khối mới dùng đáy 60 phiên, khác cửa sổ |
| Độ chính xác MA | 1.737,9 | 1.737,93 | 2 chữ số thập phân |

**Nhận định khác nhau:**
- Khối cũ: "MA20 đã ngừng dốc xuống". Livermore: "MA20 vẫn đi xuống" (1.754,09 → 1.737,93), gọi đây là nhịp hồi trong một vùng đi ngang dài hạn.
- Khối cũ dùng ngưỡng tự đặt "40% / 50%". Khối mới không có ngưỡng tự đặt; thay vào đó chỉ ra độ rộng đã hạ nhiệt sau 21/10 trong khi chỉ số vẫn tăng (đà hồi dồn vào ít mã hơn).
- Livermore thêm vùng người mua bị kẹt ở đỉnh 1.874,48 và 1.933,11.

**Nội dung mới:** dòng dự báo đang mở, dòng nguồn và giới hạn.

### Khác biệt so với khối cũ đã phát hành: monthly 09/2026

So với `reports/SpaceX_monthly_report_2026-09.md`.
- Báo cáo cũ KHÔNG có khối Kỹ thuật 5 gạch đầu dòng. Chỉ có đoạn văn mục 6.1, trộn lẫn diễn biến giá với trạng thái mô hình nội bộ.
- Đỉnh tháng:
  - Khối cũ ghi "đỉnh tháng 1.853,08 ngày 04/09". Đây là giá ĐÓNG CỬA (BQ: Close 04/09 = 1853.08).
  - Khối mới ghi 1.874,48 ngày 07/09. Đây là giá cao nhất TRONG PHIÊN (BQ: High 07/09 = 1874.48, Close 07/09 = 1821.64).
  - Hai số đều đúng, chỉ khác định nghĩa. Khối mới ghi rõ "(giá trong phiên)".
- Khối mới có thêm:
  - RSI 64,6→42,4;
  - MACD +11,73→−6,37, đổi dấu ngày 14/09;
  - khối lượng 644 vs 675 triệu (−4,6%);
  - độ rộng 41,2%→32,3%, độ rộng đạt đỉnh (03/09) TRƯỚC khi chỉ số lập đỉnh (07/09);
  - dự báo mới.
- Khối mới không nhắc gì tới mô hình trạng thái, đúng thiết kế đọc mù.
- **Lưu ý trình bày:** điều kiện vô hiệu của monthly được chép nguyên văn từ sổ. Trong đó có "1841.2 (đỉnh 9/18)": số viết theo dấu chấm thập phân, ngày viết kiểu Mỹ. Câu này lại tham chiếu một đỉnh không nằm trong FACTS (chưa đối chiếu). Dòng dự báo chỉ qua lọc từ cấm, KHÔNG qua kiểm số.

## Rủi ro tồn dư (arch-review vòng 2 + tự ghi)

1. **Kiểm số chỉ chứng minh nguồn gốc, không chứng minh nghĩa.** Mỗi số trong khối là bản chép của một số đã tính, nhưng có thể gắn sai nghĩa. Ví dụ: "MA20 tại <giá trị MA200>", hoặc số "20" lấy từ nhãn khối lượng. Các trường hợp sau cũng lọt: số viết bằng chữ, dấu viết bằng chữ ("âm 3,20"), dấu dính liền chữ.
2. **Dòng dự báo chép nguyên văn sổ** (cả điều kiện vô hiệu do LLM viết) không qua kiểm số. "Đang mở" không kiểm xem điều kiện vô hiệu đã kích hoạt chưa. P_UP in kiểu `0.56`.
3. **Có thể chặn nhầm báo cáo fallback.** Nếu người soạn không chờ `ensure` mà tự viết khối, rồi `ensure` PASS trước lúc giao, cổng sẽ CHẶN báo cáo. An toàn được giữ, nhưng việc gửi bị trễ, phải soạn lại. Trường hợp xấu nhất `ensure` chạy khoảng 55 phút, trong khi job soạn có timeout 3600s.
4. **Bản chất mẫu chấm điểm thay đổi.** Lần đọc REPORT_BLOCK_* tính vào khoảng cách của cò trigger. Vì vậy đọc theo lịch mỗi khoảng 4 tuần sẽ gần như thay hẳn đọc tại điểm chuyển trạng thái (trừ `DT_ENTER_*`). Mẫu của cổng giải thể (≥12 lần đọc) sẽ chủ yếu là đọc theo lịch. **Cần user chấp nhận.**
5. **Dự báo LIVE-BASELINE 21/10 sẽ được nhắc lại cho nhà đầu tư.** Khoảng 4 báo cáo tới (tuần 30/10, 06/11, 13/11 và tháng 10) sẽ nhắc lại LVR-2026-10-21 dưới tên Livermore. Đó là bản đọc tay trong phiên Mike. **Cần xác nhận bản đọc đó thật sự mù trước khi merge.**
6. **Commit vòng 2 dùng `SKIP=tz-anchor-gate`.** `report_delivery_gate.py:509` có sẵn `datetime.now()` từ trước (baseline của `mike/bin` = 1), còn đường dẫn worktree lệch baseline. Khi merge vào canonical cần chạy lại cổng này.
7. Kỹ năng và settings cấp user vẫn được nạp vào phiên đọc mù. Rủi ro này có từ trước, giống hệt `livermore_run.sh`.

## Việc tiếp theo (cần Mike/user)

- Duyệt merge.
- Quyết định về rủi ro 4 và 5.
- Tuỳ chọn: chuẩn hoá cách in P_UP và điều kiện vô hiệu (đây là văn bản sổ, nên cần quyết định có được "định dạng lại" hay không).

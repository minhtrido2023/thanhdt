# Lỗi tỉ suất per-position LẦN 2 — khoảng trống phạm vi cổ tức, và cổng chặn cứng

**Job:** `Taylor_20260810_030558` (attempt 2/2) · **Ngày:** 2026-08-10
**Đối tượng:** `mike/reports/SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md` Mục 3.2 / 4.2 / 5.3
**Loại:** sửa báo cáo ĐÃ GỬI nhà đầu tư + vá quy trình. Không đụng tiền thật, không đổi production trading.

---

## 1. Kết luận một dòng

Báo cáo tuần công bố tỉ suất từng mã **chưa cộng cổ tức tiền mặt đã nhận từ các tuần TRƯỚC**, vì
người soạn dùng `cum_dividend_excl` (cổ tức phát sinh **trong tuần**) làm tín hiệu — chỉ báo đó
**đúng nhưng trả lời sai câu hỏi**. Sáu sự kiện cổ tức có ex-date trước kỳ báo cáo vẫn nằm nguyên
trong giá vốn của vị thế đang giữ. SpaceX công bố **−3,28%** thay vì **−1,94%**; SAB và ZaloPay
**bị đảo dấu**. Đã sửa báo cáo + dựng cổng chặn cứng `bin/report_return_gate.py` chạy trong
`send_report_email.py`.

## 2. Root cause — là (a), KHÔNG phải (b) hay (c)

Dispatch nêu 3 giả thuyết. Kết luận: **(a) khoảng trống phạm vi**, xác định bằng dữ liệu:

| Giả thuyết | Phán quyết | Căn cứ |
|---|---|---|
| (a) scope gap của lần fix 02/08 | ✅ **ĐÚNG** | lần 02/08 chỉ phủ cổ tức **trong cửa sổ báo cáo**; 6 sự kiện ex-date 09/07–28/07 nằm ngoài cửa sổ 03–07/08 nhưng vẫn trong giá vốn vị thế đang giữ |
| (b) `dividend_adjusted_return.py` chạy sai | ❌ SAI | công cụ chạy đúng: cả 6 sự kiện ra `CASH_CONFIRMED`, khớp `cashDividendReceiving` broker **từng đồng** |
| (c) tự viết lại công thức, không gọi hàm | ❌ SAI (nhưng gần) | không có dấu vết tính sai công thức; người soạn **không gọi hàm** vì đã kết luận "không cần gọi" từ tín hiệu `cum_dividend_excl`=0 |

**Cơ chế hỏng thật sự:** `cum_dividend_excl` đo *cổ tức chưa settle trong tuần* (đúng cho kế toán
NAV/tiền của tuần). Câu hỏi cần trả lời là *"giá vốn của vị thế ĐANG GIỮ đã trừ cổ tức nhận từ
trước chưa"* — câu hỏi về **lịch sử vị thế**, không phải về tuần. Hai câu hỏi khác nhau, một con số.

## 3. Bằng chứng độc lập — 3 nguồn, không tự kiểm chứng chính mình

**Nguồn 1 — `costPrice` sổ vị thế DNSE (07/08).** DNSE tự trừ cổ tức GỘP khỏi giá vốn:

| Mã | Báo cáo (cũ) | `costPrice` broker | Chênh | = cổ tức GỘP? |
|---|---:|---:|---:|---|
| MBB | 25.850,00 | 24.850,00 | 1.000 | ✅ 1.000 |
| NCT | 94.360,00 | 86.360,00 | 8.000 | ✅ 8.000 |
| SAB | 47.368,18 | 44.368,18 | 3.000 | ✅ 3.000 |
| BID / CTG / VCB | — | — | 450 mỗi mã | ✅ 450 |
| PVT | 17.100,00 | 17.100,00 | 0 | ✅ không cổ tức |
| **LPB** | 52.583,33 | 51.466,67 | 1.116,67 | ❗ **KHÔNG** — lỗi thứ 2 (xem §5) |
| 13 mã còn lại | — | — | 0 | khớp tuyệt đối |

Chênh lệch **bằng đúng** cổ tức gộp ở đúng 6 mã có cổ tức, và **bằng 0** ở 13 mã không có. Đây là
nhân chứng độc lập với cả báo cáo lẫn `dividend_adjusted_return.py`.

**Nguồn 2 — `cashDividendReceiving` broker tại 07/08.** SpaceX **9.775.000đ**, ZaloPay
**6.453.500đ** — khớp từng đồng với tổng cổ tức tính lại (hệ 2 phương trình 2 tài khoản; ZaloPay
**không** hưởng cổ tức MBB vì chưa nắm giữ tại ngày chốt quyền).

**Nguồn 3 — ảnh chụp app DNSE của nhà đầu tư (10/08).** Giải ngược từ lãi/lỗ hiển thị:

| Mã | `costPrice` | KL | Giá app | Lãi/lỗ app | Giá vốn giải ngược | Hoà vốn app | Dư |
|---|---:|---:|---:|---:|---:|---:|---:|
| MBB | 24.850 | 1.100 | 24.100 | −933.592 | 24.948,7 | 24.950 | +98,7 |
| NCT | 86.360 | 500 | 83.100 | −1.757.276 | 86.614,6 | 86.622 | +254,6 |
| PVT | 17.100 | 3.500 | 18.350 | +4.189.371 | 17.153,0 | 17.151 | +53,0 |

Phần dư **+53…+255đ/cp (0,30–0,40% giá vốn)** là quy ước `breakEvenPrice` của app (phí mua +
phí/thuế bán ước tính) — **không phải cổ tức**: cùng dấu, cùng bậc ở cả mã CÓ cổ tức (MBB, NCT) lẫn
mã KHÔNG có (PVT), trong khi chênh cổ tức là 1.000–8.000đ/cp (lớn hơn 20–150×). *Không cố dựng lại
chính xác công thức `breakEvenPrice` của DNSE — không cần cho kết luận, và không có tài liệu để
xác nhận; nêu là phần dư đã khoanh vùng, không phải phần dư đã giải thích hết.*

**Hai câu hỏi khối lượng trong dispatch — kiểm bằng dữ liệu, không đoán:**
- **MBB 1.500 (báo cáo) vs 1.100 (app):** nhật ký `exec_SpaceX_2026-08-10_journal.csv` — bán **400
  MBB** lúc `09:15:30` ngày 10/08 (`SELL-MBB-PARK-06`, JIT_UNPARK), cùng đợt LPB −300. Sổ vị thế
  broker: 07/08 = 1.500 → 10/08 = 1.100. ⇒ **Báo cáo ĐÚNG** tại ngày chốt 07/08; chênh là giao dịch
  thật sau kỳ.
- **PVT (ảnh bị cắt KL):** giải ngược với KL 3.500 cho giá vốn 17.153,0, khớp hoà vốn app 17.151
  trong 2đ ⇒ **KL 3.500 của báo cáo ĐÚNG**.

## 4. Tác động đã sửa

| Chỉ tiêu | Số CŨ (sai) | Số ĐÚNG | Chênh |
|---|---:|---:|---:|
| SpaceX — lãi/lỗ chưa thực hiện (4.2) | −25.723.600 (−3,28%) | **−15.180.766 (−1,94%)** | +10.542.834 / +1,34pp |
| SpaceX — lỗ đã thực hiện 13 lệnh bán (3.2) | −13.911.850 | **−11.883.426** | +2.028.424 |
| ZaloPay — 14 mã bot (5.3) | −3.401.800 (−0,75%) | **+2.729.025 (+0,60%)** | **đảo dấu** |
| SAB (SpaceX) | −5,53% | **+0,49%** | **đảo dấu** |
| NCT (SpaceX) | −12,46% | **−4,41%** | +8,05pp |

**NAV, tiền mặt, KL cổ phiếu, danh sách lệnh: KHÔNG đổi** — cổ tức luôn nằm sẵn trong NAV; sai sót
chỉ ở cách quy tỉ suất về từng mã.

## 5. Lỗi thứ hai, không liên quan cổ tức — LPB (còn mở)

`verify_account_snapshot.py` tính bình quân gia quyền **không reset khi vị thế về 0**. LPB (SpaceX)
mua 900cp 01/07 → **bán sạch 06/07** → mua lại 900cp 15/07; lô đã tất toán vẫn bị trộn vào giá vốn
lô mới ⇒ 52.583,33 thay vì 51.466,67. Chỉ LPB dính; 19 mã còn lại + toàn bộ ZaloPay khớp broker
tuyệt đối.

→ **VIỆC CÒN MỞ (Taylor, chưa chốt hạn):** sửa `verify_account_snapshot.py` reset cơ sở giá vốn khi
vị thế về 0. Cổng đã chặn được triệu chứng (bắt LPB qua `costPrice`), **nhưng nguồn sinh số vẫn sai**
— cổng là lưới an toàn, không phải bản vá.

## 6. Chống tái diễn — `bin/report_return_gate.py` (§22: luật văn xuôi → code chặn được)

§21 đã là **văn xuôi** và vẫn bị áp sai **hai lần**. Theo §22 phải thành code chặn.

- Chạy **trong `send_report_email.py`** trước khi gửi; lệch > **0,15pp** ⇒ `exit 3`, **KHÔNG gửi**.
  Bỏ qua phải khai lý do (`--skip-return-gate "<lý do>"`), có in log. **Fail-closed**: cổng lỗi hoặc
  thiếu `dnse_raw` ⇒ không gửi (đã test: ném `FileNotFoundError`, không im lặng bỏ qua).
- Dựng kỳ vọng từ **2 nguồn độc lập với báo cáo**: `costPrice` broker + cổ tức `CASH_CONFIRMED`.
  **Không** đọc `verified_snapshot_*.json` (chính là nguồn sinh ra số sai) — tránh tự kiểm chứng
  chính mình. Nhờ neo vào `costPrice`, cổng bắt được **cả lỗi cổ tức lẫn lỗi giá vốn kiểu LPB**.
- Quyền hưởng cổ tức tính **riêng từng tài khoản** (`_qty_at()`; ca thật: ZaloPay không hưởng MBB).
- Kiểm cả tỉ suất trong **văn xuôi**, không chỉ trong bảng (lỗi ZaloPay tuần này nằm trong một câu văn).
- **Phạm vi (nói thẳng):** chỉ phủ **vị thế đang giữ cuối kỳ**. Bảng lãi/lỗ ĐÃ THỰC HIỆN (3.2) nằm
  ngoài — cổng **in rõ** số dòng không phủ + dòng TỔNG kỳ vọng để người soạn đối chiếu tay.

### 6.1 Kiểm chứng cổng (không tin lời tự khai)

| Phép thử | Kết quả |
|---|---|
| Selfcheck (offline) | **24/24 PASS** |
| Selfcheck dưới `env -u TZ` + `TZ=America/New_York` (§16) | **PASS** — không phụ thuộc TZ |
| **Chứng minh ngược**: dựng lại bản báo cáo với đúng 3 số SAI đã phát hành | **CHẶN 3/3**, exit 1, nêu đúng SAB −6,02pp · NCT −8,05pp · MBB −3,68pp |
| Chạy trên bản đã sửa | **PASS**, exit 0 |

### 6.2 Bản thân cổng đã bị bắt lỗi trước khi được tin

Bản đầu của cổng **chặn oan chính báo cáo đã sửa đúng** (SAB −5,53%, NCT −12,46%). Nguyên nhân:
bảng tóm tắt mục ĐÍNH CHÍNH nằm trong **blockquote** (`> | … |`); bộ đọc chỉ bỏ qua dòng bảng bắt
đầu bằng `|` nên phân loại nhầm thành văn xuôi, rồi bắt lỗi đúng các con số **CŨ (sai)** mà một mục
đính chính **buộc phải nhắc lại**.

Vá hai lớp:
1. `_strip_quote()` — bóc dấu trích dẫn (kể cả lồng `>>`) **trước khi** phân loại bảng/văn xuôi.
2. Luật **"cũ → đúng" theo từng DÒNG** — một dòng có ít nhất một tỉ suất khớp kỳ vọng thì các số
   còn lại của mã đó trên chính dòng ấy là số đối chiếu lịch sử.

Luật 2 **không tạo lỗ hổng**: muốn lách phải in số ĐÚNG ngay cạnh — tức là đã công bố đúng. Nếu
không vá, cổng sẽ chặn **vĩnh viễn** mọi báo cáo có mục đính chính, và nhanh chóng bị bỏ qua như
báo động giả — nguy hiểm hơn không có cổng. *Bài học: một cổng chặn cứng phải được thử trên chính
artifact nó sẽ gác, không chỉ trên fixture tự dựng.*

Đã ghi 4 ca hồi quy vào selfcheck (ca 19–24) để không tái diễn.

## 7. Việc còn mở

1. **`verify_account_snapshot.py` reset giá vốn khi vị thế về 0** (§5) — nguồn sinh số vẫn sai.
2. Cổng **chưa phủ bảng lãi/lỗ ĐÃ THỰC HIỆN** (Mục 3.2) — đã công bố rõ, chưa vá.
3. Cân nhắc đưa §21 + cổng này vào `coding_guidelines.md` §21 dưới dạng con trỏ tới code (không
   thêm văn xuôi mới).

## 8. Nguồn

- Báo cáo đã sửa: `mike/reports/SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md` (mục
  ĐÍNH CHÍNH đầu file + Mục 11 phụ lục bằng chứng)
- Cổng: `mike/bin/report_return_gate.py` · wiring: `mike/bin/send_report_email.py`
- Script tính lại: `mike/agents/Taylor/exp_div_scope_20260810/recompute_42.py`
- Dữ liệu: `data/execution_logs/dnse_raw_2026-08-07.jsonl`, `dnse_raw_2026-08-10.jsonl`,
  `exec_SpaceX_2026-08-10_journal.csv`
- Nền: `mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md` (lần 1, 02/08)

# DCF — lãi suất chiết khấu: "rf chậm" cho trần g_T (đo) + sửa hướng fallback (code)

Job `Taylor_20261013_163831` · user duyệt 13/10/2026 23:37 ICT · viết 14/10/2026.
Hai việc tách nhau: **Việc 1 chỉ là nghiên cứu** (không sửa `dcf_valuation.py`), **Việc 2 là code trên nhánh, CHƯA merge**.

## Kết luận

1. **Việc 2 — xong, nằm trên nhánh `fix/dcf-fallback-direction-20261013` @ `0b29d2d1`** (repo ngoài,
   worktree `mike/agents/Taylor/wt-dcffb-1013`). Khi CCTG cũ quá 45 ngày hoặc đọc lỗi, 5 consumer
   nay **giữ giá trị CCTG gần nhất đã biết** kèm WARNING, không còn tụt về Big-4. Lịch sử không đổi
   một byte. Cần arch-review rồi mới merge.
2. **Việc 1 — dữ liệu KHÔNG phân biệt được các phương án.** IC của biên an toàn gần như trùng nhau
   (chênh tối đa 0,0008; tương quan hạng trong tháng ≥ 0,9987). Thứ duy nhất thay đổi là MỨC giá trị
   hợp lý: hôm nay "rf chậm 12 tháng" hạ FV **−15,3%** và làm **10 mã** đổi cờ CHEAP → RICH.
3. **Khuyến nghị: giữ `cap_rf` làm mặc định; nếu muốn thấy rủi ro thắt chặt thì hiển thị THÊM một
   dòng FV theo `min(spot, MA12)`, không thay cờ CHEAP/RICH.** Mức tin cậy: trung bình cho vế "đừng
   thay mặc định", thấp cho vế "biến thể nào đúng" — xem mục *Lập luận*.

## Câu hỏi gốc: lãi suất tăng do thắt chặt thì DCF có lạc quan không?

Có, theo một nghĩa cụ thể và đo được. Trần `g_T ≤ rf` **bó 100% số lần công bố BCTC từ 2014**
(`cpi + gdp` hôm nay 9,66% so với rf 7,40%), nên `r − g_T` luôn đúng bằng ERP 6,5%. Mô hình thực
chất là một bội số cuối kỳ cố định, gần như không nhạy với lãi suất:

| Lãi suất tăng | `cap_rf` (hiện hành) | Gordon với g_T cố định 7,4% |
|---|---|---|
| +1pp | FV −1,3% | FV −13,7% |
| +2pp | FV −2,5% | FV −24,1% |

Đợt tăng hiện tại nghiêng về thắt chặt hơn là tăng trưởng danh nghĩa: lãi huy động hiệu dụng đi từ
5,2% lên 7,4% trong 13 tháng, trong khi CPI YoY đi từ 5,5–5,6% (04–05/2026) xuống 4,5–4,9%
(07–08/2026, nguồn FiinPro, không phải NSO). Nếu coi toàn bộ phần tăng vượt trung bình 12 tháng là
thắt chặt, FV hiện hành đang cao hơn khoảng 15%.

Nhưng lịch sử không ủng hộ việc bi quan hơn trong các đợt tăng: xem mục B2.

## Việc 1 — số đo

Script `rf_slow_measure.py`, log `out_rf_slow_measure.txt`, số máy đọc `results.json`.
Interpreter `$DNA_PYEXE`, duckdb `threads=1`. Dữ liệu: `data/bq_cache` (ticker tới 2026-10-13,
ticker_financial tới 2026-10-12), universe = `universe_pit` ruleset_version 1 (không dùng
`ticker_prune`). Giá hôm nay lấy từ BQ cache sau lượt sync 23:45 — dùng cho nghiên cứu.

**Biến thể — khai trước khi xem số, N = 4 mới + 1 đối chứng + 1 đối chứng lãi suất hằng:**

| Mã | Trần g_T dùng rf nào | Ghi chú |
|---|---|---|
| V0 `cap_rf` | spot | production, chân đối chứng |
| V1 `ma12` | trung bình 12 tháng của chuỗi lãi hiệu dụng | |
| V2 `min_spot_ma12` | min(spot, MA12) | chỉ chậm khi lãi TĂNG; đây là cách tôi hiểu chữ "sàn": `r − g_T` không bao giờ dưới ERP |
| V3 `ma36` | trung bình 36 tháng | |
| V4 `min_spot_ma36` | min(spot, MA36) | |
| `const` | lãi suất hằng 5,97% cho mọi ngày | khử hoàn toàn hindsight của chuỗi anchor; mọi biến thể trùng nhau ở đây |

Không chọn theo IS-best — không chọn gì cả. Dưới 8 biến thể và không có phép chọn nên DSR/PBO không
áp dụng. Ngoài tập khai trước, tôi có tính thêm 1 số tham chiếu hậu kiểm (mode `cpi_gdp_half` có sẵn
trong production), ghi rõ ở mục riêng.

**Self-check chân đối chứng (cả ba = 0):**
- chuỗi spot trùng `discount_rate − ERP` của production trên 26.439 lần công bố: lệch tối đa 2,8e-17
- V0 tính lại bằng công thức trùng `D.fair_value` production: lệch tương đối tối đa 1,6e-15
- V0 qua đường monkeypatch trùng production trên rổ hôm nay: lệch 0

### (a) Hôm nay — 2026-10-13

spot 7,40% · MA12 6,15% · MA36 5,29% · r 13,90%. Rổ: 344 mã thuộc `universe_pit`, **151 mã tính được
DCF** (193 không: 74 CF_OA_3Y ≤ 0, 59 FCFE âm, 59 tài chính, 1 thiếu lịch sử).

| Biến thể | r − g_T | % CHEAP | Số CHEAP | CHEAP "robust" | MoS trung vị | ΔFV trung vị (dải) | CHEAP → RICH |
|---|---|---|---|---|---|---|---|
| V0 `cap_rf` | 6,50pp | 64,2% | 97 | 88 | +31,1% | — | — |
| V1 `ma12` = V2 | 7,75pp | 57,6% | 87 | 81 | +18,7% | −15,3% (−17,1 … −14,7) | 10 |
| V3 `ma36` = V4 | 8,61pp | 55,0% | 83 | 76 | +10,4% | −23,1% (−26,0 … −22,3) | 14 |

Hôm nay V1 = V2 và V3 = V4 vì spot đang cao hơn cả hai trung bình. Không mã nào đổi RICH → CHEAP.

**Mã đổi cờ CHEAP → RICH** (MoS V0 → MoS biến thể; đầy đủ ở `out_posthoc_reference.txt`):

| Mã | Giá | FV V0 | MoS V0 | MoS `ma12` | MoS `ma36` |
|---|---|---|---|---|---|
| VGI | 77.300 | 77.490 | +0,2% | −17,7% | −29,8% |
| PPC | 8.760 | 8.916 | +1,7% | −15,2% | −26,5% |
| VNM | 58.000 | 60.549 | +4,2% | −12,8% | −24,2% |
| TNI | 4.170 | 4.388 | +5,0% | −11,4% | −22,4% |
| MWG | 74.800 | 78.779 | +5,1% | −12,0% | −23,5% |
| MST | 9.300 | 9.881 | +5,9% | −10,4% | −21,2% |
| CSV | 21.900 | 23.481 | +6,7% | −9,5% | −20,4% |
| CLX | 13.000 | 14.301 | +9,1% | −6,9% | −17,7% |
| SGP | 20.500 | 22.693 | +9,7% | −6,6% | −17,5% |
| AIG | 46.000 | 54.096 | +15,0% | −0,3% | −10,6% |
| VGT | 11.600 | 13.691 | +15,3% | (còn CHEAP) | −10,2% |
| SAS | 35.700 | 42.731 | +16,5% | (còn CHEAP) | −8,7% |
| PCH | 18.000 | 21.803 | +17,4% | (còn CHEAP) | −7,4% |
| DRI | 16.100 | 20.725 | +22,3% | (còn CHEAP) | −1,1% |

Trong 16 mã có MoS V0 từ 0 đến 25%, còn CHEAP 6 mã dưới `ma12` và 2 mã dưới `ma36`. Số CHEAP
"robust" mất đi: 7 (`ma12`), 12 (`ma36`). Chưa đối chiếu danh sách này với vị thế đang giữ.

### (b) IC của biên an toàn — khuôn Study B

FV tính một lần mỗi kỳ công bố, ghép as-of lên bảng giá đầu tháng (FV không quá 460 ngày tuổi),
IC Spearman cắt ngang từng tháng. 146 tháng (IS 65, OOS 81). t là Newey-West với lag = kỳ hạn − 1.
Cột Δ = chênh ghép cặp theo tháng so với V0.

**Khung 1 — Study B gốc** (từng xếp hạng ≤ 3, rating ≤ 3 as-of; trung vị 390 mã/tháng):

| | IS 1M | IS 2M | IS 3M | OOS 1M | OOS 2M | OOS 3M |
|---|---|---|---|---|---|---|
| V0 `cap_rf` | +0,0419 (t 4,6) | +0,0517 (4,8) | +0,0697 (5,4) | +0,0460 (5,5) | +0,0602 (6,2) | +0,0671 (6,3) |
| Δ `ma12` | −0,0001 | −0,0001 | −0,0001 | −0,0003 | −0,0005 | −0,0002 |
| Δ `min_spot_ma12` | −0,0001 | −0,0001 | −0,0001 | −0,0001 | −0,0002 | −0,0002 |
| Δ `ma36` | −0,0004 | −0,0008 | −0,0008 | −0,0000 | −0,0004 | −0,0004 |
| Δ `min_spot_ma36` | −0,0002 | −0,0003 | −0,0003 | +0,0000 | −0,0001 | −0,0000 |
| Δ `const` | +0,0001 | +0,0001 | +0,0001 | −0,0000 | +0,0000 | +0,0000 |

**Khung 2 — `universe_pit` as-of ∩ rating ≤ 3** (khung quyết định; trung vị 113 mã/tháng):

| | IS 1M | IS 2M | IS 3M | OOS 1M | OOS 2M | OOS 3M |
|---|---|---|---|---|---|---|
| V0 `cap_rf` | +0,0187 (t 1,2) | +0,0176 (1,1) | +0,0189 (0,9) | +0,0310 (2,7) | +0,0478 (3,0) | +0,0600 (3,6) |
| Δ `ma12` | −0,0001 | −0,0003 | −0,0003 | −0,0002 | −0,0003 | −0,0002 |
| Δ `min_spot_ma12` | −0,0000 | −0,0000 | −0,0001 | −0,0003 | −0,0003 | −0,0002 |
| Δ `ma36` | +0,0004 | −0,0005 | −0,0007 | −0,0001 | −0,0006 | −0,0003 |
| Δ `min_spot_ma36` | −0,0003 | −0,0004 | −0,0005 | −0,0000 | −0,0001 | −0,0000 |
| Δ `const` | +0,0001 | −0,0000 | −0,0001 | −0,0000 | +0,0001 | +0,0001 |

Đọc bảng:
- **Không phân biệt được.** |Δ| lớn nhất 0,0008, tức dưới 2% của chính IC. Tương quan hạng trong
  tháng giữa MoS biến thể và MoS V0: 0,9987–0,9999. Lý do cơ học: g_T và r giống nhau cho mọi mã
  trong cùng ngày nên đổi cơ chế chỉ co giãn FV gần như đều, không đổi thứ hạng.
- Vài ô có |t| quanh 2 (ví dụ `ma36` ALL 3M khung 1: −0,0006, t −2,6). Tổng cộng 72 ô so sánh
  (4 biến thể × 3 kỳ hạn × 3 cửa sổ × 2 khung); phần lớn mang dấu âm, tức các biến thể chậm **kém**
  V0 một chút, nhưng cỡ hiệu ứng không có ý nghĩa kinh tế và không ô nào đáng để chọn theo.
- **Hindsight của chuỗi lãi suất không ảnh hưởng IC**: chân `const` lệch tối đa 0,0001.
- So với số pin cũ của Study B (07-14: 0,0444 / 0,0584 / 0,0690, mode `cpi`, vintage dữ liệu khác):
  V0 ALL ra 0,0442 / 0,0564 / 0,0683 — cùng cỡ, không phải tái lập cùng vintage.

**Phát hiện phụ, không nằm trong câu hỏi nhưng đáng biết:** ở khung đầu tư được (`universe_pit`),
IC của MoS trong IS chỉ 0,018–0,019 với t ≈ 1 — không có ý nghĩa thống kê; chỉ OOS mới có (t 2,7–3,6).
IC đẹp của Study B gốc (IS t 4,6–5,4) đến phần lớn từ nhóm mã ngoài universe thanh khoản.

### (B2) Các đợt lãi tăng nhanh — mô tả, không phải kiểm định

Tháng có `spot − MA12 > 0,5pp`: 24 tháng thuộc **3 đợt** (2017-01…06, 2022-10…2023-05,
2026-01…10). Chỉ **2 đợt đã có kết quả 12 tháng sau**.

| Đợt | % CHEAP V0 | % CHEAP `ma12` | Lợi nhuận trung vị 12 tháng sau |
|---|---|---|---|
| 2017-01…06 | 52,6–55,8% | 47,9–53,7% | −3,5% … +10,6% (dương 5/6 tháng) |
| 2022-10…2023-05 | 55,1–68,9% | 50,8–62,9% | +6,4% … +28,1% (dương 8/8 tháng) |
| 2026-01…10 | 51,9–66,9% | 50,0–62,8% | chưa có |

Ở cả hai đợt đã xong, giá cổ phiếu tăng trong 12 tháng sau, tức phương án bi quan hơn lúc lãi tăng
đã sai chiều về mức. N = 2 đợt — không kết luận được gì về mặt thống kê. Pre-flight power
(`rnd_preflight_power.py`, per-episode, N có sẵn 2, 5 cấu hình): **NO-GO**, cần 36 quan sát độc lập,
toàn bộ lịch sử có thể tồn tại không đủ. Câu hỏi "mức nào đúng" **sẽ không bao giờ trả lời được
bằng backtest**.

Chiều ngược lại: 29 tháng lãi GIẢM nhanh (`spot − MA12 < −0,5pp`), `ma12` thuần cho g_T **cao hơn**
rf hiện hành nên % CHEAP tăng từ 57,6% lên 60,8% — lạc quan hơn production đúng lúc nới lỏng.
`min_spot_ma12` không bị (57,4%).

### (c) Kịch bản lãi suất — FV trung vị rổ hôm nay, chỉ số 100 = FV production hôm nay

Lãi suất nhảy một bậc từ ngày mai rồi đứng yên; lợi nhuận, dòng tiền và giá giữ nguyên.

| Cơ chế | Lãi suất | Ngay | Sau 6 tháng | Sau 12 tháng |
|---|---|---|---|---|
| `cap_rf` | giữ nguyên | 100,0 (64,2% CHEAP) | 100,0 | 100,0 |
| | +1pp | 98,7 (63,6%) | 98,7 | 98,7 |
| | +2pp | 97,5 (62,9%) | 97,5 | 97,5 |
| `ma12` = `min_spot_ma12` | giữ nguyên | 84,7 (57,6%) | 94,8 (60,9%) | 100,0 (64,2%) |
| | +1pp | 74,7 (53,6%) | 87,6 (58,3%) | 98,7 (63,6%) |
| | +2pp | 66,8 (49,7%) | 81,4 (55,6%) | 97,5 (62,9%) |
| `ma36` = `min_spot_ma36` | giữ nguyên | 76,9 (55,0%) | 80,2 | 84,5 (57,0%) |
| | +1pp | 68,6 (50,3%) | 72,4 | 77,3 (55,0%) |
| | +2pp | 61,8 (47,7%) | 65,9 | 71,2 (51,7%) |

**Điểm quan trọng nhất của bảng này:** "rf chậm" là hình phạt TẠM THỜI. Sau đúng 12 tháng lãi suất
đứng yên ở mức cao, `ma12` cho FV **giống hệt** `cap_rf`. Nó nói "thắt chặt làm giảm giá trị trong
một năm, sau đó không còn ảnh hưởng gì" — kể cả khi lãi suất ở lại mức cao mãi mãi.

### Số tham chiếu hậu kiểm (NGOÀI tập khai trước)

Mode `cpi_gdp_half` có sẵn trong `dcf_valuation.py` (g_T = CPI + nửa GDP = 6,55%, hôm nay thấp hơn
rf nên không bị trần): `r − g_T` = 7,35pp, FV trung vị −10,9%, 58,3% CHEAP, 9 mã đổi cờ (như danh
sách `ma12` trừ AIG). Khác "rf chậm" ở chỗ nó nhạy lãi suất **lâu dài** chừng nào rf còn trên 6,55%.
Chỉ tính cho rổ hôm nay, chưa chạy IC cho job này.

### Cảnh báo phụ — CPI thiếu nguồn 2026-09…12

`cpi_vn` điền 4 tháng 09–12/2026 bằng forward-fill 3,40% (không phải số công bố); 07–08/2026 là
FiinPro đã đóng băng, không phải NSO. **Ảnh hưởng tới FV hôm nay: bằng 0, dưới mọi biến thể.**
- g_T: trần đang bó với khoảng dư 2,26pp (so với spot) và 3,52pp (so với MA12). Để trần hết bó,
  trung bình CPI 5 năm phải giảm 2,26pp, tức 4 tháng thiếu nguồn mỗi tháng phải sai 34pp.
- g_explicit = g_T + 0,5 × (tăng trưởng lợi nhuận quá khứ − g_T): không chứa CPI trực tiếp.
- Lỗ hổng chỉ lộ ra nếu đổi sang mode `cpi` hoặc `cpi_gdp_*`, hoặc nếu rf lên trên ~9,7%.

## Lập luận và khuyến nghị

Dữ liệu không chọn hộ được, nên đây là lập luận kinh tế:

1. **Lý do muốn "rf chậm" là đúng.** Tăng trưởng danh nghĩa dài hạn không nhảy 1,25pp chỉ vì lãi
   huy động 12 tháng tăng trong một năm. Khi lãi tăng do thắt chặt, để g_T tăng theo là sai.
2. **Nhưng "rf chậm" không sửa đúng chỗ đó.** Vấn đề gốc là trần luôn bó nên `r − g_T` bị ghim ở
   ERP. Trung bình trượt chỉ làm trễ 12 tháng rồi quay về đúng trạng thái cũ (bảng c). Nếu lãi cao
   là vĩnh viễn thì hoặc nó phải ảnh hưởng vĩnh viễn, hoặc không ảnh hưởng — không phải "một năm".
3. **`ma12`/`ma36` thuần còn vi phạm chính nguyên tắc Damodaran khi lãi giảm** (g_T > rf hiện hành,
   29 tháng trong lịch sử). Nếu có dùng thì chỉ nên là bản `min(spot, MA)`.
4. **Hai đợt tăng đã xong đều đi ngược** phương án bi quan hơn (N = 2, chỉ là dữ kiện).
5. **Chi phí của việc thay mặc định là thật**: 10 mã đổi cờ, 7 mã mất nhãn robust, FV −15%, dựa
   trên một quy tắc không đo được lợi ích và tự hết tác dụng sau một năm.

**Khuyến nghị (một phương án):** giữ `cap_rf` làm mặc định và giữ nguyên cờ CHEAP/RICH. Thêm vào
dòng hiển thị DCF một con số phụ "FV nếu thắt chặt kéo dài" tính theo `min(spot, MA12)` — hôm nay
là −15%. Người đọc thấy được độ nhạy mà cờ không nhảy.

Mức tin cậy:
- "Không thay mặc định bằng rf chậm": **trung bình** — dựa trên điểm 2, 3, 5; không dựa trên IC.
- "`min(spot, MA12)` là thước đo đúng cho rủi ro thắt chặt": **thấp** — MA12 hay MA36 là tuỳ chọn,
  không có dữ liệu nào chọn giữa chúng (−15% hay −23%).
- "Đổi cơ chế không làm IC tốt lên hay xấu đi": **cao**.

**Rủi ro và giới hạn của phép đo:**
- 26 anchor lãi suất được hiệu chỉnh hồi tố một lần (2026-06-19). Chân `const` cho thấy điều này
  không ảnh hưởng IC, nhưng nó ảnh hưởng trực tiếp tới MA12/MA36 trong lịch sử và bảng B2.
- MA36 trước 2014 dùng giá trị anchor đầu (14%) kéo ngược về 2008 — chỉ chạm các kỳ công bố
  2012–2013 dùng cho đầu năm 2014.
- Khuôn Study B chỉ cập nhật FV tại kỳ công bố, nên tháng đầu mỗi đợt tăng các biến thể trùng nhau.
- Đợt 2026 chưa có lợi nhuận 12 tháng sau.
- DCF là lăng kính tham khảo, không chặn lệnh; đổi cờ ảnh hưởng báo cáo và cảnh báo, không đổi lệnh.

**Trước khi wire bất kỳ phương án nào: cần quant-skeptic phản biện.** Job này không wire gì.

---

## Việc 2 — sửa hướng fallback

### Đã xác minh bằng đọc code (không tin KB)

`deposit_rate_vn.effective_deposit_rate()` tại `cce3699d` có hai nhánh hạ số về Big-4:
- CCTG đọc lỗi (`cctg_err`): `rate_source = "big4_12m(cctg_unavailable: …)"`, số = Big-4.
- CCTG cũ quá 45 ngày tính theo `asof`: `rate_source = "big4_12m(cctg_stale: Nd)"`, số = Big-4.

KB mô tả đúng. Cả 5 consumer đi qua `consumer_deposit_rate_detail()` → hàm này. Với cả 5, lãi suất
thấp hơn là hướng **dễ dãi hơn** (r thấp hơn, sàn yield thấp hơn).

Hai điểm KB/bối cảnh **không còn đúng**:
- **Mốc stale không phải ~20/10 và 15/11.** Job tuần (thứ Hai 08:05) đã ghi thêm dòng ngày 03/10,
  05/10 và 12/10. Anchor mới nhất của cả hai chuỗi là 2026-10-12, nên mốc stale của cả hai là
  **2026-11-27** (12/10 + 46 ngày), và lùi thêm một tuần mỗi lần job tuần ghi thành công.
- **Big-4 không có khái niệm stale trên đường consumer.** `current_deposit_rate()` forward-fill vô
  hạn, không cảnh báo. Chỉ kill-switch A mới kiểm độ tươi của Big-4.

### Đã đổi gì

| File | Thay đổi |
|---|---|
| `deposit_rate_vn.py` | Hai nhánh trên nay giữ CCTG gần nhất đã biết. `rate = max(Big-4, CCTG đã biết)`. WARNING + nhãn `cctg_held(<ngày>; cctg_stale: Nd)` hoặc `cctg_held(<ngày>; cctg_unavailable: <lỗi>)` |
| `cctg_rate_vn.py` | Thêm `last_known_good_cctg()`: đọc khoan dung từng dòng CSV cho RIÊNG nhánh lỗi; bỏ qua dòng hỏng, không đoán. File không mở được thì dùng anchor đông cứng trong code |
| `dcf_valuation.py` | Chỉ docstring của `discount_rate()` |
| `deposit_fallback_direction_selfcheck.py` | Mới |
| `cctg_deposit_wiring_selfcheck.py`, `cctg_overlay_selfcheck.py` | Sửa các kỳ vọng mô tả hướng cũ (§7/§8, T18) |

Không đổi: `macro_killswitch_a_status` (vẫn fail-closed ARMED), knob `DEPOSIT_RATE_CCTG_OVERLAY=0`,
`merge_deposit` và cổng CAPIT margin PIT của `golive_recommend_v23.py`, mặc định của `dcf_valuation`.
Không sửa crontab, không chạm `trading_bot/`.

Việc giữ **không có hạn**. Lối ra duy nhất là một dòng CCTG mới được xác nhận — dòng đó có thể thấp
hơn, kể cả thấp hơn Big-4.

### Hành vi theo từng mốc (CSV sống hôm nay: Big-4 6,8% và CCTG 7,4%, cùng anchor 12/10)

| Mốc | Trước (main) | Sau (nhánh) |
|---|---|---|
| Nay → 26/11/2026 | 7,4%, r 13,9% | Giống hệt |
| 27/11/2026, nếu 6 tuần liền không có dòng CCTG mới | **6,8%**, r 13,3% | **7,4% giữ nguyên**, WARNING, nhãn `cctg_held(2026-10-12; cctg_stale: 46d)` |
| Cùng ngày, Big-4 cũng quá 45 ngày | Consumer: không gì xảy ra, không cảnh báo. Kill-switch A: ARMED | Không đổi |
| Bất kỳ ngày nào CSV CCTG có dòng hỏng | 6,8% | Giữ dòng tốt gần nhất (7,4%) |
| CSV CCTG không đọc được / sai header | 6,8% | Giữ anchor đông cứng 7,5% (30/09) |
| Chính lookup "đã biết" lỗi (đã vá 14/10 sau arch-review) | 6,8% | Giữ anchor đông cứng 7,5% (30/09), nhãn nêu lỗi lookup; chỉ khi chưa biết gì mới 6,8% |
| `DEPOSIT_RATE_CCTG_OVERLAY=0` | 6,8% | 6,8% |

**Cỡ ảnh hưởng của hướng cũ, đo trên rổ hôm nay:** lãi 7,4% → 6,8% làm FV DCF trung vị **+0,77%**
và không mã nào đổi cờ — nhỏ, chính vì `cap_rf` làm mô hình ít nhạy lãi suất. Ảnh hưởng lớn hơn
nằm ở các consumer dùng lãi suất làm mẫu số: "sàn giá cổ tức" của `due_diligence` và
`custom30_yield_labels` tăng **8,8%**, ngưỡng EY của `rating_8l` NEUTRAL dễ hơn 0,6pp.

### Chứng minh lịch sử không đổi

`deposit_fallback_direction_selfcheck.py` nạp mã nguồn `cce3699d` (qua `git show`) và mã nguồn
nhánh vào hai thư mục tạm riêng, rồi so **mọi đầu ra đường consumer** (`consumer_deposit_rate_detail`
knob 1 và 0, `effective_deposit_rate` với `check_freshness` True và False, `current_deposit_rate`)
bằng sha256:

| Kiểm | Phạm vi | Kết quả |
|---|---|---|
| H1 | fixture đông cứng, 646 asof ≤ 2026-10-13 | fingerprint trùng |
| H2 | bản sao CSV sống, cùng lưới | fingerprint trùng |
| H1/H2 `--full-daily` | **từng ngày** 2011-01-01 → 2026-10-13: 5.765 asof × 5 đầu ra | fingerprint trùng cả fixture (`51ad7252…`) lẫn bản sao CSV sống (`c8f518f6…`) — `selfcheck_branch/fallback_dir_FULLDAILY.txt` |
| H3/H3b | kill-switch A, lưới kéo tới 2027-06-30, thêm fixture Big-4 luôn tươi | fingerprint trùng |
| H4 | mã nguồn 9 hàm không được đụng + 2 bảng anchor | trùng từng ký tự |
| H5 | 2026-11-15 (fixture) | cũ 6,8 → mới 7,5 — thay đổi là có thật, chỉ sau lịch sử |

Pin R3 không đọc đường này: `pt_v23_audit_2014.py` chỉ import HẰNG `DEPOSIT_EVENTS`
(dòng 64, dùng ở 1614–1615), không gọi hàm nào của `deposit_rate_vn`; bảng anchor đó và các hàm
lịch sử (`deposit_events_df`, `merge_deposit`) không đổi một ký tự (H4). Tôi **không** chạy lại R3 —
kết luận "pin không đổi" dựa trên việc input của nó không đổi, không dựa trên một lượt chạy lại.

### Selfcheck và mutation

65 kiểm tra, PASS ở `env -u TZ`, `America/New_York`, `Pacific/Kiritimati` và ICT
(`selfcheck_branch/fallback_dir_TZ*.txt`). 11 mutant mức mã nguồn, cả 11 bị bắt:

| Mutant | Bị bắt bởi |
|---|---|
| M1 **đảo hướng fallback, nhánh stale** | S1, S3 |
| M2 **đảo hướng fallback, nhánh lỗi** | 9 kiểm tra S5 |
| M3 giữ im lặng (bỏ WARNING) | S1 |
| M4 gắn nhãn "tươi" cho giá trị đang giữ | S1 |
| M5 bỏ qua knob rollback | S7 |
| M6 salvage nhận dòng ngoài khoảng | S5a |
| M7 salvage dùng dòng tương lai | S5j |
| M8 salvage lấy dòng CŨ nhất | 12 kiểm tra S5 |
| M9 việc giữ lan ngược vào lịch sử | H1 |
| M10 làm yếu kill-switch A | H3 |
| M11 cho CCTG thấp hơn Big-4 làm driver | S4 |

**Mutation đã bắt được một lỗ trong chính selfcheck:** ở bản đầu, M10 SỐNG SÓT. Trên fixture mặc
định Big-4 và CCTG cùng stale một ngày, `big4_stale` tự ép ARMED nên che mọi thay đổi ở nhánh CCTG.
Đã thêm fixture "Big-4 luôn tươi" vào H3; M10 nay bị bắt.

### Quét selfcheck theo phạm vi (§23 — lõi dùng chung)

14 selfcheck của consumer chạy trong worktree, mỗi cái ở ICT và America/New_York
(`selfcheck_baseline/` so với `selfcheck_branch/`): **13/14 xanh ở cả hai TZ**. Cái còn lại,
`due_diligence_selfcheck.py`, đỏ 5 test Integration **giống hệt trước khi tôi sửa** — worktree không
có `data/` (gitignore) nên DD trả `DD_KHONG_CHAY_DUOC`; cùng file đó trên checkout chính xanh 49/49.

Để kiểm các selfcheck cần dữ liệu thật với mã nhánh, `preload_branch_rates.py` nạp trước
`deposit_rate_vn`/`cctg_rate_vn` của nhánh (trỏ vào CSV sống) rồi chạy selfcheck từ checkout chính.
10 selfcheck, mỗi cái chạy hai lần — mã main và mã nhánh — **cả 20 lượt rc=0**
(`selfcheck_broad/`): `due_diligence_selfcheck` (49/49 ở cả hai), `capit_lever_selfcheck`,
`failopen_failclosed_selfcheck`, `cpi_vn_tier15_selfcheck`, và 6 file trong `mike/bin`
(`sector_valuation_lens`, `discretionary_candidate_funnel`, `discretionary_margin_gate`,
`due_diligence_corp_flags`, `strategy_fit_dashboard`, `filter_lag_entry_window`). Mỗi lượt nhánh in
đường dẫn module đang dùng lúc thoát — cả 10 đều là file trong `wt-dcffb-1013`. Giới hạn: selfcheck
nào tự nạp lại module theo đường dẫn file hoặc gọi tiến trình con thì không đi qua bản nhánh.

Cổng `tz-anchor-gate` không chạy được trong worktree (repo lồng `mike/` vắng mặt), nên tôi chạy tay
`mike/bin/tz_anchor_gate.py` trên 6 file đã commit: rc=0.

### Việc CÙNG LOẠI tôi thấy nhưng KHÔNG sửa — cần quyết

1. **`deposit_events_df()` nuốt `ValueError` rồi lặng lẽ về anchor đông cứng** (CSV Big-4 sai cột).
   Hôm nay vô hại vì CSV và anchor đông cứng cùng 6,8%. Ngày Big-4 lên trên 6,8% qua CSV, một lỗi
   header sẽ hạ số về 6,8% không cảnh báo. Không sửa vì hàm này nuôi cả kill-switch A lẫn lịch sử.
2. **`trading_bot/due_diligence.py::_deposit_rate_pct` rơi về 5,5%** khi `deposit_rate_vn` import
   hoặc đọc hỏng (`YIELD_FLOOR_DEPOSIT_FALLBACK_PCT`). So với 7,4% hiện tại, "sàn giá cổ tức" tăng
   34,5%. Khối này tự ghi là DISPLAY_ONLY. Không sửa vì nằm trong `trading_bot/`.
3. **Big-4 cũ không sinh cảnh báo nào trên đường consumer** — chỉ kill-switch A báo.
4. Nhãn `cctg_6m(<ngày>)` sai tên từ khi chuỗi chuyển sang 12 tháng (05/10). Chỉ là nhãn.
5. Docstring `_deposit_rate_pct` trong `trading_bot/due_diligence.py` còn liệt kê nhãn cũ.

### KB cần cập nhật khi merge

`mike/kb/data_registry/macro/cctg_rate_vn.md` mục "Cơ chế kết hợp" và bẫy #7 đang mô tả hướng cũ.
Bản đề xuất: `mike/kb/data_registry/macro/cctg_rate_vn.md.proposed` (§13, chờ Mike duyệt).

## Cập nhật 14/10/2026 sau arch-review
NEEDS_CHANGES đã vá (commit `024f4a15`, merge `b1b8db83`): salvage CCTG nay total + ISO strict (dòng có múi giờ `Z`/`+07:00` hoặc ngày kiểu ngày-trước bị bỏ), lookup lỗi giữ anchor 7,5%; thêm S5k–n, mutant M12–M14; 14/14 mutant bị bắt, selfcheck xanh ở 3 TZ.

## Việc cần user quyết

1. **Việc 1:** (A) giữ nguyên, không làm gì · (B) thêm dòng hiển thị phụ `min(spot, MA12)`, cờ không
   đổi — **khuyến nghị** · (C) thay mặc định bằng `min(spot, MA12)`, chấp nhận 10 mã đổi cờ.
   B và C đều phải qua quant-skeptic trước khi wire.
2. **Việc 2:** merge nhánh sau arch-review?
3. **Việc 2, mở rộng:** có sửa tiếp mục 1 và 2 ở danh sách "cùng loại" không? Mục 2 chạm `trading_bot/`.
4. Việc giữ CCTG không có hạn — có cần một mốc leo thang (ví dụ quá 90 ngày thì báo Trading Daily)?

## Tệp trong thư mục này

| Tệp | Nội dung |
|---|---|
| `rf_slow_measure.py` · `out_rf_slow_measure.txt` · `results.json` | Việc 1: script, log, số máy đọc |
| `today_basket_by_variant.csv` | 151 mã × 5 biến thể: FV, MoS, cờ, robust |
| `monthly_cheap_share_by_variant.csv` | % CHEAP theo tháng, gap spot − MA12, lợi nhuận về sau |
| `base_inputs_releases.parquet` | 26.439 kỳ công bố: FCFE, g, r, FV production |
| `out_posthoc_reference.txt` | Danh sách mã đổi cờ, số tham chiếu `cpi_gdp_half` |
| `selfcheck_baseline/` · `selfcheck_branch/` · `selfcheck_broad/` | Việc 2: log selfcheck trước / sau / quét rộng |
| `preload_branch_rates.py` | Chạy selfcheck của checkout chính với mã nhánh |

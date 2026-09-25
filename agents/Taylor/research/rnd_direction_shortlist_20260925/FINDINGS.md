# Hướng R&D mới — sàng bằng tiêu chí KHẢ THI ĐO ĐƯỢC trước khi đầu tư
Job `Taylor_20260925_122513` · VIỆC 3 · 2026-09-25 · **Danh sách để Mike/user CHỌN — Taylor không tự bắt đầu hướng nào.**

---

## (a) Bài học quy trình → công cụ, không phải thêm một đoạn văn

**Sự cố:** chương trình ORB VN30F chạy 4 tháng R&D, ~20 cấu hình, 5 job dispatch. Phép tính
"DSR 0,95 cần 4.075 phiên = 16,2 năm > cả đời hợp đồng 9,13 năm" mất **30 giây** và đáng lẽ
phải là bước ĐẦU TIÊN, không phải bước cuối.

### Đã làm — công cụ chạy được, không phải lời khuyên

**`mike/bin/rnd_preflight_power.py`** (mới) — selfcheck `rnd_preflight_power_selfcheck.py`
**21/21 PASS**, ổn định qua 3 môi trường TZ, và **tái lập đúng các con số đã pin của ORB**
(DSR@1129 = 0,491 vs pin 0,4914 · N cho DSR 0,95 = 4.029 vs pin 4.075 · power80 = 2.513 vs pin
2.510 · DSR tại trần 9,13 năm = 0,782 vs pin 0,779). Công thức PSR/DSR dùng NGUYÊN quy ước của
`recalc.py` (job _120926) để số liệu so sánh được giữa các job.

```bash
$DNA_PYEXE mike/bin/rnd_preflight_power.py \
    --sharpe-ann 0.888 --obs-per-year 252 \
    --n-available 1129 --n-trials 20 --n-rule per-day --max-history-years 9.13
# >>> PHÁN: NO-GO — N cần (4.029) > TOÀN BỘ dữ liệu có thể tồn tại (2.301)
```

Ba thiết kế có chủ đích:
1. **`--n-rule` BẮT BUỘC** (`per-day` / `per-episode` / `per-event` / `per-bet`) — không khai
   cách đếm N thì script từ chối chạy. Đếm sai N chính là lỗi đã mắc (744 phiên ORB thực ra là
   13 episode). `--help-rules` in bảng đầy đủ.
2. **`--max-history-years`** — trần cứng "tổng dữ liệu có thể TỒN TẠI". Đây là biến phân biệt
   MARGINAL với NO-GO: bỏ cờ này thì ORB ra MARGINAL ("chờ 11,5 năm"), có nó thì ra NO-GO
   ("chờ bao lâu cũng không đạt"). Selfcheck mục 2 kiểm đúng việc bỏ cờ làm ĐỔI phán — để cờ
   này không trở thành đồ trang trí.
3. **Chiều ngược — "Sharpe tối thiểu phát hiện được với N có sẵn"** — thường hữu ích hơn "N cần",
   vì N ở VN là đại lượng CỐ ĐỊNH, không phải biến điều chỉnh được.

### Đề xuất chờ duyệt

**`.claude/skills/quant-research/SKILL.md.proposed`** — thêm **Step 0 — PRE-FLIGHT KHẢ THI**
đặt TRƯỚC step 1 hiện tại (step 1 được đánh dấu "chỉ tới đây sau khi Step 0 phán GO/MARGINAL").
Gồm: lệnh chạy, bảng quy tắc đếm N theo LOẠI chiến lược, mô tả sự cố ORB, và 2 cái bẫy
(`--n-trials` phải là số cấu hình SẼ thử chứ không phải số báo cáo; effect size giả định phải
đến từ NGOÀI mẫu sắp test). **Chưa áp vào file live** — chờ Mike/user duyệt (skill dùng chung
cho cả fleet).

---

## ⚠️ Con số quan trọng nhất của VIỆC 3 — trần cứng của dữ liệu VN

Chạy pre-flight ngược trên 3.176 phiên (toàn bộ dữ liệu cổ phiếu VN từ 2014, `universe_pit`):

> **Với N_trials 15-25, Sharpe năm TỐI THIỂU phát hiện được ở DSR 0,95 là ≈ 0,96–1,03.**

Tức: **bất kỳ tín hiệu độc lập nào có Sharpe kỳ vọng dưới ~1,0 đều KHÔNG thể xác nhận được ở
ngưỡng fleet trên dữ liệu VN — bất kể hướng nào, bất kể chờ bao lâu** (thêm 1 năm chỉ thêm 8%
số quan sát). Đây không phải tính chất của ORB; đây là tính chất của thị trường VN + ngưỡng DSR
0,95 mà fleet đã chọn.

**Hệ quả xếp hạng — quy tắc chọn hướng:**

| | SNR mỗi quan sát | Ví dụ | Xác nhận được không? |
|---|---|---|---|
| Nghiên cứu **ĐO MỘT CHI PHÍ** bạn kiểm soát | cao (SR/obs ~0,1–0,3) | slippage, phí, thuế, thời điểm đặt lệnh | ✅ vài trăm quan sát là đủ |
| Nghiên cứu **DỰ BÁO MỘT LỢI NHUẬN** | thấp (SR/obs ~0,02–0,06) | tín hiệu alpha mới, factor mới | ❌ cần Sharpe ≥1,0 mới qua được |

Lý do: khi đo chi phí, bạn so sánh hai cách làm trên **CÙNG một biến động thị trường** — biến
động đó triệt tiêu. Khi dự báo lợi nhuận, biến động thị trường CHÍNH LÀ mẫu số.

---

## (b) 5 hướng ứng viên — đã chạy pre-flight

### ① Execution alpha — thu hẹp khoảng cách 1,5pp giữa backtest và thực tế ✅ **GO**

| | |
|---|---|
| **Cơ chế kinh tế** | Không phải "thị trường sai" mà là **chi phí mình đang trả**. `CLAUDE.md`: *CAGR thật ≈ CAGR backtest − 1,5%* (phí + slippage + thuế) — backtest không mô hình hoá slippage lẫn thuế. Cắt được một nửa khoản đó = **+0,75pp/năm**, lớn hơn phần lớn edge tín hiệu mới, và **dấu của nó chắc chắn** (giảm chi phí luôn tốt, không cần đoán đúng tương lai). |
| **N độc lập có sẵn** | **327 lệnh đã khớp** (unique order id, 32 phiên có fill, SpaceX+ZaloPay từ 2026-07-01, đếm từ `data/execution_logs/dnse_raw_*.jsonl` 84 file). Tích luỹ ~5,5 lệnh khớp/phiên ⇒ **~1.300/năm**. |
| **Effect size cần** | pre-flight `--mean-bps 10 --sd-bps 40 --obs-per-year 1300 --n-trials 10 --n-rule per-event`: DSR@327 = **0,998**, N cần chỉ **169** quan sát. Với N có sẵn, effect tối thiểu phát hiện được = **×0,72** mức giả định ⇒ **dư power**. |
| **Hạ tầng mới?** | **KHÔNG.** Cash-equity, dữ liệu đã có (`dnse_raw`, `quote_l2` 2.803 bản ghi, `ppse`, `place_order` 774). |
| **Trùng V2.4?** | **KHÔNG** — tầng trực giao. BAL/LAG chọn MÃ; hướng này quyết định GIÁ và THỜI ĐIỂM của cùng mã đó. |
| **Cảnh báo** | (i) `--sd-bps 40` là **giả định, phải ĐO trước** trên chính 327 lệnh — đúng luật "effect size từ ngoài mẫu": bước 1 là đo sd, bước 2 mới thiết kế test. (ii) N thật < 327: nhiều lệnh cùng phiên + cùng mã chia sẻ một cú sốc ⇒ đếm theo (phiên × mã) mới đúng. (iii) Chạm đường thực thi ⇒ **Mafee + user duyệt** trước khi áp; R&D trên dữ liệu lịch sử thì không. |

### ② Trục CHẤT LƯỢNG DÒNG TIỀN (accrual) cho custom30V ⚠️ **MARGINAL**

| | |
|---|---|
| **Cơ chế kinh tế** | Accrual anomaly (Sloan 1996): lợi nhuận kế toán chứa phần dồn tích dễ điều chỉnh; phần tiền mặt bền hơn. Ở VN kiểm toán yếu hơn ⇒ tiên nghiệm khoảng cách tiền-mặt-vs-lợi-nhuận **rộng hơn** thị trường phát triển. Đúng roadmap user đã nêu: *custom30V cần trục cash-flow-quality kháng thao túng*. |
| **N độc lập có sẵn** | 3.176 phiên (2014+) · 54.901 ticker-quý · 1.292 mã · breadth ~200 mã × 4 lần/năm = **~800 quyết định/năm**. |
| **Effect size cần** | bảo thủ Sharpe 0,5 → DSR@3176 = **0,412**, N cần 13.374 phiên = **53 năm** ⇒ hỏng. Lạc quan Sharpe 0,8 → DSR **0,800**, N cần 5.227 = 20,7 năm ⇒ vẫn hỏng. **Phải đạt Sharpe ≥1,03 standalone** mới qua. |
| **Hạ tầng mới?** | KHÔNG. `CF_OA_P0–P4`, `CF_OA_3Y/5Y`, `NP_P0–P7` đã có sẵn trong `ticker_financial`. |
| **Trùng V2.4?** | **Một phần — phải tách bạch.** `yieldcombo` đang dùng `1/PCF` = **cash-flow YIELD** (định giá). Accrual = **cash-flow QUALITY** (NP vs CF_OA). Khác nhau, nhưng tương quan không tầm thường ⇒ phải test **incremental** trên nền V2.4, không test standalone. |
| **Đường đi khả thi duy nhất** | **KHÔNG theo đuổi như tín hiệu độc lập.** Chỉ có ý nghĩa nếu đo như một **golden-floor / binary gate** giống 8L rating (gate loại bỏ, không phải return-tilt) — ở đó câu hỏi là "gate này có loại đúng các ca thao túng không", N tính theo **số ca bị loại**, và tiêu chí không phải DSR. Nếu định test như factor tilt → pre-flight nói NO-GO. |

### ③ Lăng kính chất lượng tài sản NGÂN HÀNG ⚠️ **MARGINAL — nhưng là sửa LỖI, không phải săn alpha**

| | |
|---|---|
| **Cơ chế kinh tế** | PCF/PE của ngân hàng **không so sánh được** với doanh nghiệp sản xuất (memory `finance-domain-grounding-not-pure-statistics`). Xếp hạng chéo dùng chung thang ⇒ **lỗi xếp hạng đã biết**, không phải cơ hội alpha. Trục đúng cho bank: NPL, bao phủ dự phòng, CAR, tăng trưởng tín dụng. |
| **N độc lập có sẵn** | Thấp. VN có ~20-27 NH niêm yết ⇒ breadth nhỏ, và ngành đồng pha mạnh ⇒ N hiệu dụng ≈ **số chu kỳ tín dụng**, không phải số mã × quý. `ICB_Code` trong BQ là **mã SỐ** (2357, 8633, 2353…) không phải nhãn `NH` như `bigquery_schema.md` mô tả ⇒ **cần bản đồ ngành trước khi làm gì** (một phát hiện phụ của job này). |
| **Effect size cần** | Sharpe 0,4 → DSR@3176 = **0,363**, N cần 18.378 phiên = **72,9 năm** ⇒ NO-GO nếu đo như alpha. |
| **Hạ tầng mới?** | KHÔNG cho dữ liệu BQ; **CÓ** nếu cần NPL/CAR chi tiết → FiinX (`fiinprox_bank_ratios_quarterly_20260914.csv` đã có sẵn 53KB). |
| **Trùng V2.4?** | Trùng **vùng ảnh hưởng** với 8L composite (bank nằm trong pool BAL). |
| **Đóng khung đúng** | Đây là **kiểm tra tính đúng đắn**, không phải nghiên cứu edge: "composite hiện tại có xếp sai bank không?" — trả lời bằng **kiểm tra tính nhất quán của thang đo** (bank vs phi-bank có cùng phân phối điểm không?), KHÔNG bằng backtest lợi nhuận. Rẻ, nhanh, và **không cần DSR** vì không tuyên bố edge nào. |

### ④ Hiệu ứng NGÀY GDKHQ / cổ tức trong khung thuế VN ❓ **CHƯA ĐỦ DỮ LIỆU ĐỂ PHÁN**

| | |
|---|---|
| **Cơ chế kinh tế** | Thuế TNCN cổ tức tiền mặt VN ⇒ giá rơi ngày GDKHQ về lý thuyết ≠ đúng bằng cổ tức gộp. Nếu lệch có hệ thống thì đó là hiệu ứng **cơ học** (thuế), không phải dự báo. |
| **N độc lập** | **KHÔNG đếm được bằng dữ liệu hiện có.** Thử suy ex-date từ bước nhảy tỷ lệ `Close/Price`: ngưỡng >1% cho 77.000 "sự kiện" trên 3.156/3.176 phiên (≈24 sự kiện/phiên) — **phi lý**. Đây chính là điều `coding_guidelines §21` đã cảnh báo: `Close/Price` không phân biệt được cổ tức tiền mặt với chia tách, và nhiễu làm tròn áp đảo. |
| **Việc cần làm TRƯỚC** | Xin Winston (data-ops) một **nguồn corp-action chuẩn** có ngày GDKHQ + loại + tỷ lệ. Không có nó thì không đếm được N ⇒ **không chạy được pre-flight** ⇒ **không được bắt đầu**. |
| **Hạ tầng mới?** | Có thể — tuỳ nguồn corp-action. **Trùng V2.4?** Không. |

### ⑤ Dòng vốn nâng hạng FTSE (khối ngoại) 🔶 **NO-GO theo thống kê — nhưng có thể đúng theo khung khác**

| | |
|---|---|
| **Cơ chế kinh tế** | **Mạnh nhất trong 5 hướng**: nâng hạng FTSE Advanced Emerging ⇒ quỹ thụ động **BẮT BUỘC** mua đúng danh mục, đúng tỷ trọng, đúng ngày. Đó là một **đẳng thức kế toán**, không phải một edge thống kê. Đã có trong `kb/structural_break_watch.json` (`ftse_msci_upgrade`, status `watching`). |
| **N độc lập** | **N = 1.** Tiền lệ thị trường khác (Kuwait/Saudi/Qatar-UAE/Pakistan) cho N ≈ 5-8, mỗi cái một chế độ khác nhau. |
| **Pre-flight** | **NO-GO theo định nghĩa** — N=1 không bao giờ đạt DSR. |
| **Nhưng** | Pre-flight trả lời "có xác nhận được bằng thống kê không", KHÔNG phải "có nên hành động không". Với sự kiện cơ học N=1, khung đúng là **kịch bản + sizing + quản trị rủi ro**, không phải backtest. **Nếu theo đuổi, phải nói thẳng là quyết định phi-thống kê và định cỡ tương ứng** — đây chính xác là cái bẫy mà `feedback-plan-must-follow-production-rule-not-opinion` cảnh báo. |
| **Hạ tầng?** | Không. `fiinprox_foreign_flow_index_daily_20260914.csv` đã có. **Trùng V2.4?** Không. |

---

## (c) Xếp ưu tiên — và câu trả lời thẳng

**Tiêu chí: (1) cơ chế kinh tế rõ, (2) đủ quan sát độc lập, (3) không cần hạ tầng mới.**

| Hạng | Hướng | (1) cơ chế | (2) đủ N | (3) không cần hạ tầng | Phán |
|---|---|---|---|---|---|
| **1** | ① Execution alpha | ✅ chi phí, dấu chắc chắn | ✅ 327 → ~1.300/năm, DSR 0,998 | ✅ | **GO** |
| **2** | ③ Lăng kính bank *(đóng khung là kiểm tra đúng đắn)* | ✅ khả so sánh thang đo | ✅ (không tuyên bố edge ⇒ không cần DSR) | ✅ | **GO có điều kiện** |
| 3 | ② Accrual *(chỉ dạng binary gate)* | ✅ | ⚠️ chỉ khi đo như gate, không phải tilt | ✅ | **MARGINAL** |
| 4 | ⑤ FTSE flow | ✅ mạnh nhất | ❌ N=1 | ✅ | **NO-GO thống kê** |
| 5 | ④ Cổ tức/GDKHQ | ⚠️ | ❓ chưa đếm được | ❓ | **CHẶN — thiếu nguồn corp-action** |

### Trả lời thẳng câu (c)

> **Có đúng MỘT hướng đạt cả ba tiêu chí: ① Execution alpha.** Và nó đạt được **chính vì nó
> không dự báo lợi nhuận** — nó đo một chi phí mình đang trả, nên tỷ lệ tín hiệu/nhiễu mỗi quan
> sát cao gấp ~5× bất kỳ tín hiệu alpha nào, và vài trăm lệnh là đủ thay vì hàng chục nghìn phiên.
>
> **Không hướng SĂN ALPHA nào đạt cả ba, và đó không phải vì danh sách này kém.** Trần cứng đã đo:
> 3.176 phiên dữ liệu VN + ngưỡng DSR 0,95 ⇒ chỉ xác nhận được tín hiệu có **Sharpe ≥ ~1,0**.
> Rất ít tín hiệu đơn lẻ đạt mức đó. V2.4 R3 đạt (Sharpe 1,90) — đó là lý do nó qua được, và cũng
> là lý do **cải thiện V2.4 hiện có gần như luôn đáng giá hơn đi tìm tín hiệu thứ hai độc lập.**

### (d) Taylor KHÔNG bắt đầu hướng nào

Không dòng code nghiên cứu nào được viết cho 5 hướng trên. Danh sách này để Mike/user chọn.
Nếu chọn ①, bước đầu tiên **không phải** backtest mà là: **đo `sd` thật của slippage mỗi lệnh
trên 327 lệnh đã khớp** — vì chính pre-flight cấm lấy effect size từ mẫu sắp test, và
`--sd-bps 40` ở trên mới chỉ là giả định.

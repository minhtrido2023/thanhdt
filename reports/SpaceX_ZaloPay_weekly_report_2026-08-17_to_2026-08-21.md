# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: 17/08/2026 – 21/08/2026

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live từ 01/07/2026 (có margin)
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live từ 06/07/2026 (cash-only, không margin)
**Chiến lược:** V2.4 (2 book BAL/LAG + parking custom30V tại NEUTRAL + rổ CAPIT bear-washout, hiện chưa kích hoạt)
**Ngày lập báo cáo:** 22/08/2026 · **Người lập:** Taylor (Quant) — số liệu đối soát qua pipeline xác minh chuẩn (Mục 7)
**Đối tượng:** Báo cáo hiệu suất & vận hành — có thể chia sẻ với nhà đầu tư

> ⚠️ **Báo cáo này phát sinh TỰ ĐỘNG do bị bỏ sót cadence tuần** (`check_report_cadence.sh` phát
> hiện, dispatch job `Taylor_20260822_020003`). Kỳ đã đóng đầy đủ (17-21/08, dữ liệu 5 phiên trọn
> vẹn, không có ngày nào thiếu trong dữ liệu nguồn) — không phải rescue dữ liệu gap như tuần trước.
>
> ✅ **Nguồn số liệu chính:** `verify_account_snapshot.py` chạy có `--account-no` cho **cả 2** tài
> khoản, dùng ĐẦY ĐỦ lịch sử ngày có fill (16 ngày SpaceX, 19 ngày ZaloPay tính tới 21/08 — không
> chỉ 5 ngày trong tuần, theo đúng cách script yêu cầu để tránh lỗi "legacy-majority guard"), asof
> 21/08/2026 — cả 2 **Verified = True**, 0 lệch khối lượng so với broker. NAV chuỗi từ
> `nav_history_{account}.csv` (đầy đủ cả 5 ngày trong kỳ, không có gap).
>
> ⚠️ **Journal thực thi (`exec_{account}_{date}_journal.csv`) THIẾU cho phần lớn kỳ này** — SpaceX
> chỉ có 17/08, ZaloPay không có ngày nào trong kỳ. Xem giải trình + cách bù bằng nguồn khác ở
> **Mục 3** và **Mục 7.1**.

---

## 1. TÓM TẮT ĐIỀU HÀNH

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (chốt 14/08) | 958.940.908 | 939.887.091 |
| NAV cuối kỳ (chốt 21/08) | **977.129.844** | **948.266.511** |
| Thay đổi trong kỳ | **+18.188.936 (+1,90%)** | **+8.379.420 (+0,89%)** |
| VN-Index cùng kỳ (14/08 → 21/08) | 1.729,08 → 1.768,12 (**+2,26%**) | (cùng chỉ số) |
| **Chênh so với chỉ số** | **−0,36 điểm %** (kém hơn chỉ số) | **−1,37 điểm %** (kém hơn chỉ số) |
| Đáy trong tuần (19/08) | 958.099.132 (−0,09% so đầu kỳ) | 919.774.803 (−2,14% so đầu kỳ, đáy 17/08) |
| Cổ phiếu cuối kỳ | 867.117.750 (88,7% NAV) | 903.040.650 (95,2% NAV, gồm DGC legacy ~432tr = 45,6%) |
| Tiền mặt tại công ty CK | 9.741.252 (1,0% NAV) | 6.439.105 (0,7% NAV) |
| **Tiền gửi "Trứng vàng" (off-book)** | **100.270.842** (10,3% NAV) | **38.786.756** (4,1% NAV) |
| Nợ margin cuối kỳ | 0 | 0 (cash-only) |
| Số mã nắm giữ cuối kỳ | 27 (đều có fill-history đầy đủ) | 26 (24 tracked + DGC/VPB legacy) |

**Cả hai tài khoản TĂNG tuyệt đối nhưng KÉM HƠN VN-Index tương đối** (SpaceX +1,90% vs chỉ số
+2,26%; ZaloPay +0,89% vs +2,26%). Đây là một tuần **gần như không có giao dịch chủ động** — không
có đợt tái cân bằng PARK/BAL/LAG nào (khác hẳn tuần 10-14/08 trước đó); NAV di chuyển gần như thuần
theo biến động giá của rổ đang nắm giữ. Nguyên nhân kém hơn chỉ số: (a) tỷ trọng tiền mặt/Trứng vàng
lớn hơn thị trường tăng làm giảm tốc độ bắt nhịp hồi phục cuối tuần (VN-Index tăng mạnh phiên 21/08);
(b) ZaloPay chịu thêm lực cản riêng từ DGC (45,6% NAV, legacy, ngoài phạm vi quản lý bot, HOSE vẫn
đang hạn chế giao dịch). Sự kiện đáng chú ý nhất trong tuần là khoản chuyển **~100,2tr (SpaceX)** và
**~38,8tr (ZaloPay)** từ tiền mặt sang tiền gửi "Trứng vàng" ngày 19/08 — **không ảnh hưởng NAV**
(Mục 2). DT5G giữ nguyên **NEUTRAL** suốt tuần, không cap phòng thủ nào kích hoạt.

---

## 2. GIẢI TRÌNH — CHUYỂN TIỀN VÀO "TRỨNG VÀNG" NGÀY 19/08 (KHÔNG PHẢI RÚT VỐN, KHÔNG PHẢI LỖ)

Giữa kỳ báo cáo, cả 2 tài khoản ghi nhận tiền mặt giảm mạnh trong một ngày (18/08 → 19/08) và đồng
thời cột `egg_assets` trong `nav_history_{account}.csv` xuất hiện lần đầu với giá trị tương ứng:

| Tài khoản | Tiền mặt 18/08 | Tiền mặt 19/08 | Egg xuất hiện 19/08 | Chênh lệch |
|---|---:|---:|---:|---:|
| SpaceX | 109.984.412 | 9.783.984 | 100.223.898 | khớp (100.200.428 vs giảm 100.200.428) |
| ZaloPay | 45.218.865 | 6.459.346 | 38.768.598 | khớp (38.759.519 vs giảm 38.759.519) |

**Đối soát NAV = Cổ phiếu + Tiền mặt − Nợ vay + Trứng vàng khớp từng đồng mọi ngày trong kỳ** (ví dụ
cuối kỳ SpaceX: 867.117.750 + 9.741.252 + 0 + 100.270.842 = 977.129.844 ✓; ZaloPay:
903.040.650 + 6.439.105 + 0 + 38.786.756 = 948.266.511 ✓) — cơ chế NAV cộng Trứng vàng đã được wire
từ tuần 07/2026 (xem báo cáo tuần 13-17/07), tuần này chỉ là một đợt bổ sung tiền gửi mới, không
phải cơ chế mới. **Hạn chế cần nhắc lại**: số dư Trứng vàng vẫn là số **không đọc được qua API DNSE**
(ngoài phạm vi 19 nhóm endpoint đã kiểm tra) — dựa trên cột `egg_assets` do `daily_nav_snapshot.py`
ghi lại từ nguồn nội bộ đã đối soát trước đó; nếu nhà đầu tư nạp/rút thêm mà không cập nhật, NAV có
thể lệch cho tới lần đối soát tiếp theo.

---

## 3. HOẠT ĐỘNG GIAO DỊCH TRONG KỲ

**Tuần gần như không có giao dịch ở các book chủ động (BAL/LAG/PARK).** Đối chiếu vị thế broker
thật (`dnse_raw`) giữa 14/08 và 21/08 cho thấy chỉ có 2 thay đổi số lượng nắm giữ ở mỗi tài khoản:

- **SpaceX**: TV1 (discretionary, sleeve "mua tích lũy khi sợ hãi có tính toán", theo dõi ngoài
  book chính) tăng từ 1.800 → 2.300cp (+500cp) — khớp với lệnh mua 500cp ngày 17/08 lúc 09:15
  (`exec_SpaceX_2026-08-17_journal.csv`, giá 20.100đ, chiến thuật TWAP). VIX tăng 400 → 420cp
  (+20cp, **+5,0%** — đúng tỷ lệ cổ tức cổ phiếu, KHÔNG phải lệnh mua; xác nhận là hành động doanh
  nghiệp, không phải giao dịch bot).
- **ZaloPay**: chỉ VIX tăng 100 → 105cp (+5cp, +5,0%) — cùng đợt cổ tức cổ phiếu VIX, không có
  giao dịch chủ động nào khác.
- `capit_fired=false`, `capit_size=0` suốt kỳ — rổ CAPIT bear-washout không giải ngân.
- Không có sự kiện PARK/LAG rebalance nào trong `data/trade_plans/plan_{account}_2026-08-{17..21}.json`
  ngoài giữ nguyên rổ đã thiết lập từ đợt tái cân bằng tuần trước (10-11/08).

**Vì sao khẳng định được "không giao dịch" dù thiếu journal 4/5 ngày**: kết luận trên dựa vào
**đối chiếu vị thế broker thật** (`dnse_raw_{date}.jsonl`, nguồn độc lập với journal nội bộ, đã
verify qua `verify_account_snapshot.py` cho asof 21/08 = Verified True), không dựa vào journal —
xem giới hạn đầy đủ ở Mục 7.1.

---

## 4. BỐI CẢNH THỊ TRƯỜNG TRONG TUẦN

| Ngày | VN-Index | Δ ngày |
|---|---:|---:|
| 14/08 (đầu kỳ) | 1.729,08 | — |
| 17/08 | 1.727,46 | −0,09% |
| 18/08 | 1.732,02 | +0,26% |
| 19/08 | 1.726,69 | −0,31% |
| 20/08 | 1.734,24 | +0,44% |
| 21/08 | 1.768,12 | **+1,95%** |

### 4.1 Technical

| Chỉ tiêu | Giá trị (21/08/2026) | Ghi chú |
|---|---:|---|
| Đóng cửa | **1.768,12** | +2,26% so với 14/08; phần lớn mức tăng đến từ 1 phiên bùng nổ 21/08 (+1,95%) |
| MA20 | 1.745,54 | Giá đóng cửa **trên** MA20 |
| MA50 | 1.787,07 | Giá đóng cửa **dưới** MA50 |
| MA200 | 1.777,33 | Giá đóng cửa **dưới** MA200 |
| RSI(14) | 52,4 | Vùng trung tính, không quá mua/quá bán |
| Breadth (%mã > MA50, rổ `ticker_prune` 210 mã) | **35,2%** (74/210) | Cải thiện so với tuần trước (25,4%) nhưng vẫn dưới 50% — đà tăng chưa lan tỏa toàn thị trường |

*Nguồn: `tav2_bq.ticker` với `ticker='VNINDEX'` (cột `Close/MA20/MA50/MA200/D_RSI` tự có sẵn cho
dòng VNINDEX, KHÔNG cần tự tính lại như tuần trước) + `tav2_bq.ticker_prune` cho breadth.*

**Đọc vị**: tuần đi ngang-giảm nhẹ 4 phiên đầu (biên độ hẹp ±0,3-0,4%) rồi bùng nổ phiên cuối
(21/08, +1,95%) đưa giá vượt lại MA20 nhưng vẫn dưới MA50/MA200. Breadth cải thiện nhưng còn thấp
(35,2%) — mức tăng vẫn tập trung ở một nhóm mã lớn hơn là lan tỏa toàn thị trường. Đây là mẫu hình
**hồi phục kỹ thuật một phiên trên nền breadth còn yếu**, chưa đủ để xác nhận đảo chiều xu hướng.

### 4.2 Fundamental — Định giá & vĩ mô

| Chỉ tiêu | Giá trị | Ghi chú |
|---|---|---|
| Value Radar (canonical, `value_radar.py`) | 🟢 **24,5 — RẺ** (phân vị 10 năm) | P/E 11,58 (phân vị 9) · P/B 1,96 (phân vị 33) · spread lợi suất E/P − tiết kiệm +1,83pp (phân vị 32) — **display-only, chưa qua kiểm định đa giả thuyết (0/17 lăng kính), KHÔNG dùng làm tín hiệu mua/bán** |
| DT5G — trạng thái vĩ mô sống | **NEUTRAL** (state 3/5), ổn định, không có candidate đang tích luỹ | `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`, cập nhật 21/08 — NEUTRAL đã 128 phiên liên tục |
| Base-rate lịch sử NEUTRAL → BEAR/CRISIS | 11,5% / 20,9% / 30,6% trong 20/40/60 phiên tới | Base-rate DT5G 2014+, KHÔNG phải dự báo |
| w_LAG mục tiêu / thực tế | 0,50 / 0,4965 | Trong band ±10pp, không breach |
| Drawdown 52 tuần (dd52w) | **−8,3%** | Cách xa ngưỡng kích hoạt CAPIT bear-washout (gate `dd52 ≤ −20%`) |
| CAPIT (bear-washout) | **Chưa kích hoạt** (`capit_fired=false`, `capit_size=0`) | Không có rổ CAPIT nào giải ngân tuần này |

*Nguồn: `dna_report.build_dt_gate_line()` / `build_value_radar_line()` / `build_neutral_base_line()`
(bắt buộc theo `kb/coding_guidelines.md` §6b — tái dùng module canonical, không tự tính lại
percentile P/E ad-hoc) + `data/golive_v23_status.json` (snapshot 21/08, do `macro_state_live.py`
ghi).*

**Đọc vị**: định giá RẺ theo Value Radar canonical (24,5, phân vị 10 năm — đọc bổ sung, không phải
tín hiệu timing) nhưng DT5G — cơ chế phòng thủ chính thức — vẫn NEUTRAL, không có tín hiệu chủ động
nào đòi hỏi thay đổi tỷ trọng. Hệ thống tiếp tục vận hành đúng thiết kế: phản ứng chậm, có chủ đích,
không đoán đáy/đỉnh theo định giá.

---

## 5. EXPOSURE & RỦI RO CUỐI KỲ (21/08/2026)

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| Tỷ trọng cổ phiếu/NAV | 88,7% | 95,2% (45,6% là DGC legacy ngoài phạm vi quản lý bot) |
| Tỷ trọng ngành ngân hàng (trong sổ có fill-history) | **36,1%** (312.997.945 / 867.127.945) | **27,4%** (120.554.126 / 439.150.676) |
| Nợ margin | 0 | 0 (cash-only, đúng thiết kế) |
| CAPIT (bear-washout) đang giữ | 0 mã | 0 mã |
| DT5G regime | NEUTRAL | NEUTRAL |

**Rủi ro tập trung không đổi so với các kỳ trước**: ZaloPay vẫn có ~45,6% NAV nằm ở DGC (legacy,
HOSE hạn chế giao dịch từ vụ khởi tố lãnh đạo 17/03/2026, ước gỡ hạn chế ~11-12/2026) — đã công bố
nhiều kỳ, nhắc lại vì là cấu phần lớn nhất ngoài tầm kiểm soát chủ động của bot. Tỷ trọng ngân hàng
ở cả 2 tài khoản gần như không đổi so với tuần trước (36,9%→36,1% SpaceX; 27,3%→27,4% ZaloPay),
nhất quán với việc không có tái cân bằng trong kỳ.

---

## 6. QUẢN LÝ RỦI RO / DT5G TRONG KỲ

Không có sự kiện phòng thủ nào được kích hoạt: DT5G duy trì NEUTRAL suốt kỳ (đã 128 phiên liên
tục, không có candidate BEAR/EX-BULL nào đang tích luỹ), w_LAG trong band mục tiêu, CAPIT
bear-washout chưa fired (dd52w −8,3%, còn cách xa ngưỡng gate −20%), capit_lever ở trạng thái tắt
(`enabled=false`). Biến động trong tuần (biên độ VN-Index ±2,4% đỉnh-đáy) nằm trong dao động bình
thường của trạng thái NEUTRAL — đúng thiết kế, DT5G là chốt rủi ro fail-safe cho khủng hoảng, không
phải công cụ phản ứng với mọi nhịp dao động thông thường.

---

## 7. GHI CHÚ QUAN TRỌNG VỀ NGUỒN SỐ LIỆU — GAP & GIỚI HẠN

### 7.1 Journal thực thi thiếu cho phần lớn kỳ báo cáo

`exec_SpaceX_{date}_journal.csv` chỉ tồn tại cho **17/08** trong kỳ này (18-21/08 không có file);
`exec_ZaloPay_{date}_journal.csv` **không tồn tại cho bất kỳ ngày nào** trong kỳ (10-14/08 là lần
cuối có journal ZaloPay). `verify_account_snapshot.py` tự cảnh báo (`WARN: missing exec_*_journal.csv`)
cho từng ngày thiếu — không bị bỏ qua âm thầm.

**Tác động lên báo cáo này**: KHÔNG ảnh hưởng đến NAV/tỷ suất tổng (Mục 1) — số liệu đó đến từ
`nav_history_{account}.csv` (đầy đủ, ghi trực tiếp từ balance broker thật mỗi tối) và
`verify_account_snapshot.py` (dùng `dnse_raw` — log API broker thô, độc lập với journal — làm nguồn
chính, cross-check journal chỉ là lớp phụ). Journal chỉ dùng để mô tả CHI TIẾT lệnh nào khớp giờ
nào giá nào; thiếu nó, Mục 3 dùng cách thay thế **đối chiếu vị thế broker giữa đầu kỳ và cuối kỳ**
(same-effect, độ chi tiết thấp hơn — biết ĐƯỢC "có/không đổi vị thế" và đổi bao nhiêu, KHÔNG biết
giờ khớp lệnh chính xác từng lệnh nhỏ nếu có nhiều lệnh cùng mã trong ngày rồi khớp về cùng 1 số).

**Việc cần làm (báo bus, chưa tự sửa)**: cần Winston/Taylor kiểm tra vì sao `run_bot.sh` không ghi
journal cho SpaceX 18-21/08 và ZaloPay toàn bộ kỳ — nghi vấn hợp lý nhất là **không có lệnh nào
được đặt** những ngày đó (khớp với kết luận "không giao dịch" ở Mục 3, dựng độc lập từ `dnse_raw`)
nên journal trống theo đúng thiết kế (chỉ ghi khi có sự kiện PLACE/FILL) — nhưng đây là SUY LUẬN,
chưa xác nhận bằng log cron trực tiếp; nêu rõ để không tự nhận là đã xác minh.

### 7.2 Số dư "Trứng vàng" là số không qua API broker

Xem Mục 2 — hạn chế giống các kỳ trước (không đổi), nhắc lại vì có giao dịch mới trong kỳ này.

---

## 8. PIPELINE XÁC MINH (tuân thủ `kb/coding_guidelines.md` §6)

1. `verify_account_snapshot.py --account SpaceX --account-no 0002023347` và
   `--account ZaloPay --account-no 0001743768`, cả hai `--asof 2026-08-21`, dùng đầy đủ lịch sử
   ngày có fill (không giới hạn 5 ngày trong tuần — tránh false "legacy-majority guard").
   **Verified = True cho cả 2 account**, 0 lệch khối lượng broker vs journal.
2. `nav_history_SpaceX.csv` / `nav_history_ZaloPay.csv` — đầy đủ 5/5 ngày trong kỳ, không có gap
   (khác tuần trước).
3. Đối chiếu NAV = mtm_stock + cash − margin_debt + offbook + egg khớp **từng đồng** mọi ngày
   trong kỳ, cả 2 tài khoản (Mục 2).
4. VN-Index, MA/RSI/breadth: `tav2_bq.ticker` (dòng `ticker='VNINDEX'`) + `tav2_bq.ticker_prune`.
5. DT5G/Value Radar: `dna_report.build_dt_gate_line()` / `build_value_radar_line()` /
   `build_neutral_base_line()` — canonical, không tự tính lại (§6b).

---

*Báo cáo tự động do `check_report_cadence.sh` phát hiện thiếu cadence tuần, dispatch job
`Taylor_20260822_020003`. Toàn bộ số liệu đối soát qua pipeline trên; phần nào không trace được đã
nêu rõ ở Mục 7, không suy đoán.*

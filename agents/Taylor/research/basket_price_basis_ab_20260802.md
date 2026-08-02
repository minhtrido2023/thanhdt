# custom30V — tách vai cơ sở giá (Price vs Close): A/B NAV đầy đủ + tác động LIVE

**Job:** `Taylor_20260802_141725` (attempt 2) · **Ngày:** 2026-08-02
**Tiền đề:** job `Taylor_20260802_083624` (`pe_pb_basis_broad_audit_20260802.md` §3) phát hiện
`custom_basket.py` ghép `Close` (đã điều chỉnh hồi tố) với đại lượng PIT thô (`Volume_3M_P50`,
`OShares`) ở 2 vai cross-sectional, trong khi chính file đó đã dùng đúng `COALESCE(Price,Close)`
cho ADV — tự mâu thuẫn. User đã duyệt sửa.

**Kết luận 1 dòng:** bản sửa làm số backtest **XẤU ĐI −0,36pp CAGR** (27,60% → **27,24%**). Đây là
bằng chứng lỗi cũ **đang thổi phồng số pin R3**, không phải lý do để bỏ bản sửa.

---

## 0. Trạng thái 8 bước

| Bước | Nội dung | Trạng thái |
|---|---|---|
| 1 | Bản đồ mọi chỗ dùng Close/Price/OShares/Volume, phân nhóm (a) lợi suất / (b) chọn-rổ-trọng-số | ✅ commit `ebeacad` |
| 2 | Sửa CHỈ nhóm (b) | ✅ commit `ebeacad` |
| 3 | Self-check 2 chiều (parity + positive control) | ✅ commit `2c098c1`, 4/4 PASS |
| 4 | A/B backtest NAV đầy đủ | ✅ dưới đây |
| 5 | Tác động lên rổ đang giữ THẬT | ✅ dưới đây — **phát hiện lỗi MỚI, đã sửa** (`be6b976`) |
| 6 | DSR | ✅ dưới đây |
| 7 | quant-skeptic | ⏳ đang chạy |
| 8 | Cập nhật tài liệu | ⏳ chỉ sau khi bước 7 CONFIRMED |

---

## 1. Bước 4 — A/B NAV (chân đối chứng tái lập ĐÚNG số pin)

Runner `data/basis_ab_20260802/run_leg.sh`. **Đúng 1 biến** giữa 2 chân (`BASKET_PRICE_BASIS`),
snapshot đóng cứng `data/bq_cache_asof20260729_postrestate` (= đúng vintage số pin được đo),
`BQ_CACHE_THREADS=1`, `$DNA_PYEXE`, lệnh pin R3 nguyên văn.

| | CAGR | Sharpe | MaxDD | Calmar | Final NAV | self-check |
|---|---|---|---|---|---|---|
| **legA `legacy`** (tiền-sửa) | **27,60%** | **1,84** | **−17,5%** | **1,58** | **1.041,95B** | 0 VND (BAL+LAG) |
| **legB `split`** (bản sửa) | **27,24%** | 1,81 | −18,4% | 1,48 | 1.006,33B | 0 VND (BAL+LAG) |
| **Δ (fix − cũ)** | **−0,36pp** | −0,03 | −0,9pp | −0,10 | −35,6B | |

**legA khớp số pin R3 tuyệt đối cả 5 chỉ tiêu** (27,60 / 1,84 / −17,5 / 1,58 / 1.041,95B — so với
`results_registry.md` mục "2026-07-29 RE-PIN R3"). ⇒ A/B **hợp lệ**, engine tất định, và −0,36pp là
chênh lệch thật do bản sửa, không phải nhiễu vintage/threads.

Recompute độc lập từ CSV (`extract_peryear.py`) khớp bản in cả 2 chân:

| | FULL | IS 2014-19 | OOS 2020-26 |
|---|---|---|---|
| legA legacy | 27,60% | 23,45% | 31,51% |
| legB split | 27,24% | **23,81%** (+0,36) | **30,46%** (−1,05) |

### Per-year (LOO) — và vì sao KHÔNG được quy kết theo năm

Δ per-year (legB − legA), pp: 2014 0 · 2015 +4 · 2016 +2 · 2017 −3 · 2018 −1 · 2019 0 · 2020 +4 ·
2021 +6 · 2022 −4 · 2023 −1 · 2024 +1 · 2025 −6 · 2026 −1.

Kiểm **dose-response** (mức lỗi mỗi năm = median |Close/Price − 1| trên toàn panel):

| năm | 2014 | 2016 | 2018 | 2020 | 2022 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| mức lỗi | 0,552 | 0,470 | 0,355 | 0,269 | 0,166 | 0,067 | **0,025** | **0,000** |
| Δ (pp) | 0 | +2 | −1 | +4 | −4 | +1 | **−6** | **−1** |

`corr = +0,347` (n=13, **không có ý nghĩa**). Quan trọng hơn: **năm có Δ âm lớn nhất (2025, −6pp)
lại là năm lỗi gần như BẰNG KHÔNG** (Close≈Price ⇒ 2 chân chọn rổ gần như y hệt). Về mặt cơ chế,
Δ đó **không thể** do cơ sở giá.

⇒ Đây đúng hiện tượng **single-path carry** mà chính bản re-pin 07-29 đã ghi (Δ per-year lớn gấp
~21 lần Δ headline và rơi vào năm KHÔNG bị tác động). **Kết luận bắt buộc: KHÔNG quy kết Δ theo
năm.** Headline −0,36pp là hợp lệ (A/B contemporaneous, 1 biến); phân rã theo năm thì không.

Ngược lại, dose-response ở **tầng CƠ CHẾ** thì CÓ và sạch (self-check T3, commit `2c098c1`):
**4,60 mã/rebal đổi ở cửa sổ cũ vs 1,50 ở cửa sổ gần đây**.

---

## 2. Bước 5 — tác động LIVE: phát hiện lỗi MỚI cùng họ, nằm trên đường LIVE

Rổ parking LIVE **không** do `custom_basket.py` tính lúc chạy — `golive_recommend_v23.py` đọc bảng
dựng sẵn `tav2_bq.custom30v_8l`. Truy ngược publisher: **`custom30_history.py`**, chạy MỖI PHIÊN
trong `papertrade_daily.sh` bước [6b].

**Lỗi:** `custom30_history.py:42` dựng trọng số công bố từ `bx["mcap"]` = **Close đã điều chỉnh ×
OShares** — tức chân RETURN của `build_pit` — đem dùng làm **TRỌNG SỐ CROSS-SECTIONAL**. Đúng họ lỗi
với `ebeacad`, nhưng cao hơn một tầng và **nằm trên đường LIVE**. Bước 1 không bắt được vì bản đồ
bước 1 chỉ quét trong `custom_basket.py`.

**Vì sao lỗi này cắn mạnh ở đây:** publisher chạy lại **mỗi phiên**, nhưng `rebal_date` chỉ đổi
**mỗi quý**. `Close` bị viết lại hồi tố ⇒ trọng số công bố của MỘT rebal cố định **trôi dần** mỗi
lần có mã chốt quyền. Đo trên rebal LIVE 2026-05-05, vintage 2026-07-29:

- **18/30 mã** đã có `Close/Price ≠ 1,00` (ACB 0,862 · IDC 0,873 · DBC 0,882 · PVT 0,909).
- Chính ngày 2026-05-05 thì hệ số = 1,00 cho **cả 30 mã** ⇒ **trọng số ĐÚNG đúng hôm công bố, rồi
  hỏng dần từ đó.** `Price` không bao giờ bị viết lại ⇒ bản sửa ổn định theo thiết kế.

**Δ trọng số LIVE tại rebal hiện hành:** Σ|Δw| = **1,653pp**, lớn nhất **ACB +0,478pp**, 5 mã đổi
>0,1pp, 4 mã ghim trần 10% (CTG/BID/VCB/VHM) không đổi. **Thành viên KHÔNG đổi (0/30)** ⇒ **không
phát sinh mã mua/bán mới**; chỉ là chênh trọng số.

> **Sự kiện vận hành, báo cho Mike/user quyết:** rổ 30 mã đang giữ ở SpaceX/ZaloPay **không đổi
> thành viên**. Chỉ trọng số tham chiếu lệch tối đa 0,478pp/mã. **Tôi KHÔNG đề xuất giao dịch nào.**
> Lưu ý lịch: rebal kế tiếp **2026-08-05** (q2m5) — chỉ còn 3 phiên, rổ sẽ được dựng lại toàn bộ
> trên cơ sở đã sửa, nên phương án "không làm gì tới 08-05" là khả thi.

**Self-check** `custom30_publish_weight_selfcheck.py` — 5/5 PASS, cố ý **KHÔNG** chạy
`custom30_history.py` (file đó kết thúc bằng `bq load --replace` ghi đè bảng production):

- **T1** chân tiền-sửa tái lập **bảng đang publish** tới `4,91e-07` ⇒ chẩn đoán neo vào artifact
  THẬT, không phải bản giống-giống.
- **T3** bất biến đại số: với mã không chạm trần, `w_new/w_old == (1/factor) × k` với **k dùng
  chung**, spread **1,1e-15**, Pearson **+1,000000**.
- **T5** trung thực tự khai **KHÔNG phân giải được** (2 snapshot cách nhau 1 ngày, chân cũ cũng
  trôi 0) — đạt tầm thường, không tính là bằng chứng.
- Chạy lại dưới `env -u TZ` và `TZ=America/New_York`: PASS cả 3 (coding_guidelines §16/§19).

> **T3 bản ĐẦU đã SAI và self-check bắt được:** giả thiết "factor<1 ⇒ trọng số phải TĂNG" sai, vì
> trọng số là đại lượng **tương đối** — VPB/TCB/VND có factor<1 nhưng vẫn TỤT do cả rổ bị chiết
> khấu sâu hơn. Lỗi ở TEST, không ở code; đã thay bằng bất biến đại số mạnh hơn ở trên.

---

## 3. Bước 6 — DSR

`N_trials = 1`: đây là **khôi phục tính đúng đắn** (một bản sửa), không phải dò tham số — cùng lý
luận quant-skeptic đã dùng cho PE. Với N=1 thì `expected_max_sr` suy biến (`norm_ppf(0)`), đúng về
mặt toán: **không có lạm phát do chọn lọc**, nên mốc so là `SR0 = 0` và DSR quy về PSR.

| | SR (ann) | skew | kurt | DSR (N=1) | stress N=10 | N=50 | N=199 |
|---|---|---|---|---|---|---|---|
| legA legacy | 1,775 | +0,07 | 8,8 | 1,000000 | 0,999998 | 0,999956 | 0,999708 |
| **legB split** | 1,740 | +0,14 | 9,5 | **1,000000** | 0,999997 | 0,999931 | **0,999561** |

DSR ≥ 0,9995 kể cả khi ép N=199 (toàn bộ họ tìm kiếm V2.4). **Không có vấn đề multiple-testing.**
Và về bản chất câu hỏi data-mining ở đây là **moot**: bản sửa làm số **XẤU ĐI** — ta đang chấp nhận
số thấp hơn để đổi lấy tính đúng đắn, đó là hướng ngược với data-mining. Không báo PBO (đúng
brief: 1 bản sửa, không phải chọn giữa nhiều biến thể).

---

## 4. Giới hạn phải công bố (KHÔNG được lờ đi)

1. **legB CHƯA phủ hết tác động của bản sửa.** `pt_v23_audit_2014.py:124` (`_c30v_asof`) đọc
   **THÀNH VIÊN** từ bảng đã publish `tav2_bq.custom30v_8l` cho nhánh **CAPIT**. Trong lần chạy A/B,
   bảng đó lấy từ snapshot ⇒ **vẫn là thành viên dựng bằng cơ sở CŨ**. Bản sửa có đổi thành viên ở
   các năm cũ (4,60 mã/rebal ở 2014-2016) ⇒ **−0,36pp là CẬN DƯỚI về độ phủ**, chưa gồm phần CAPIT.
   Đo đầy đủ đòi hỏi republish bảng rồi chạy lại — chưa làm (sẽ ghi đè bảng production).
   Backtest **không** đọc trọng số đã publish (chỉ thành viên) ⇒ bản sửa publisher `be6b976` tự nó
   **không** đổi số backtest.
2. Δ per-year **không quy kết được** (§1) — single-path carry.
3. Lỗi fidelity `liq<=0` **vẫn MỞ** như trước ⇒ khoảng kỳ vọng trung thực vẫn phải đọc kèm, anchor
   DD ~−30% (bootstrap 5th-pct), không phải −18,4%.
4. **KHÔNG đụng** `lag_liquidity_filter.py:100` (dù brief bước 2 có nêu): `Volume_3M_P50*Close` ở đó
   là 1 trong **5 điểm** giữ một bất biến parity đã ghi tài liệu (`due_diligence.py` adv_vnd,
   `plan.py` cap_lag_orders, `pt_v23_audit_2014.py:1303`) mà docstring nói rõ cơ sở `Close` là lựa
   chọn **thận trọng có chủ đích** để trần live == trần mô phỏng. Sửa 1/5 sẽ phá bất biến đó trong
   im lặng ⇒ tách thành job riêng. (Đã ghi trong `ebeacad`.)
5. Cùng họ lỗi nhưng **CHƯA sửa vì là script audit/nghiên cứu, không phải production**:
   `basket_concentration.py:28`, `basket_scheme_concentration.py:23`,
   `custom30_core_select_audit.py:101`, `v4final_lib.py:103` (file tự khai "research/audit only;
   nothing in production imports this"). Nêu ra để không ai tưởng đã quét sạch.

---

## 5. Đề xuất

1. **Giữ bản sửa** (`ebeacad` + `be6b976`). Số backtest xấu đi là **hệ quả đúng** của việc gỡ
   look-ahead: cơ sở cũ để sự kiện quyền XẢY RA SAU ngày t sắp lại thứ tự cross-section.
2. **Re-pin R3: 27,60% → 27,24% / 1,81 / −18,4% / 1,48** — và ghi rõ 27,60% là số **có lỗi
   look-ahead trong rổ parking**, giữ lại làm lịch sử (§8 coding_guidelines), không xoá.
3. Rổ LIVE: **không có hành động giao dịch nào được đề xuất** (thành viên không đổi; rebal 08-05
   sẽ dựng lại toàn bộ trên cơ sở đúng).
4. Việc treo: đo phần CAPIT-membership còn thiếu (§4.1) sau khi bảng được republish bằng cơ sở đã sửa.

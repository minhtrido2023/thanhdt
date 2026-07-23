# Fear-Buy Pattern — Systematic Historical Screen (N lớn, thay N=2)

> Taylor (Quant/Algo), job `Taylor_20260723_123927`, 2026-07-23. **RESEARCH-ONLY.**
> Mandate user: *"tự nghiên cứu... tổng quát hoá từng trường hợp để tìm quy tắc đầu tư của pattern này."*
> Case seed: **DGC 3/2020** (COVID, về dưới book, LN vẫn tốt, 2 năm sau ~10 lần).
> Nối tiếp `calculated_fear_state_backstop.md` (khung 4-trigger) — đây là phần ĐỊNH LƯỢNG N-lớn.

---

## 0. TL;DR — quy tắc rút ra được

Thay vì bám vài case nổi tiếng (bẫy chọn-case-đã-biết-kết-quả, N=2 → "edge" 100% từ 1 mã PNJ), tôi
quét CÓ HỆ THỐNG toàn bộ lịch sử VN 2008–2026 trên `universe_pit` (point-in-time, không look-ahead).

**Bộ tiêu chí SÀNG LỌC định lượng (FEARBUY v1)** — tất cả point-in-time:
1. **Thị trường panic SÂU**: VNINDEX ≤ **−30%** so đỉnh 1 năm (`mkt_dd < −0.30`).
2. **Chiết khấu sổ sách sâu**: **PB < 0.7** (càng sâu càng mạnh — gradient đơn điệu).
3. **Lõi vẫn tạo tiền**: `NP_P0 > 0` (LN quý gần nhất dương) **VÀ** `CF_OA_P0 > 0` (dòng tiền HĐKD dương).
4. **Sàn chất lượng (chống tail)**: `ROE_Min3Y ≥ 0` (golden floor của đội).
5. Nằm trong `universe_pit` (in_universe=TRUE) tại thời điểm đó.

**Kết quả lịch sử (2008–2023, N=237 episode sau dedup >14 tháng/mã):**
- Median **excess return 12m vs VNINDEX = +37.8%**, winrate **77%**, mean +71.6% (winsor +62.1%).
- Median **excess 24m = +45.3%**, mean +119%.
- **8/8 năm-khủng-hoảng có median excess DƯƠNG** (sign-test p = **0.0039**).
- **Tail sạch**: chỉ **0.8%** episode mất >50% sau 24m (so base screen 7.1%).

**Đây là nâng cấp thật so với N=2**: edge KHÔNG còn phụ thuộc 1 mã, mà dương ở MỌI khủng hoảng
độc lập trong 16 năm. Nhưng vẫn là **CANDIDATE GENERATOR + playbook**, KHÔNG auto-buy (xem §5 caveat).

---

## 1. Verify case DGC 3/2020 (BQ thật)

| Mốc | Ngày | Close(adj) | PB | PE | NP_P0 quý | CF_OA_P0 quý |
|---|---|---|---|---|---|---|
| Trước | 2019-12-31 | 6.860 | 0.93 | 4.8 | 118 tỷ | 244 tỷ |
| **ĐÁY COVID** | **2020-03-31** | **5.450** | **0.73** | **4.43** | **168 tỷ** | **197 tỷ** |
| +21 tháng | 2021-11-30 | 63.340 | 5.45 | 21.2 | 478 tỷ | 938 tỷ |
| +24 tháng | 2022-03-31 | 88.930 | 6.16 | 16.3 | **1.304 tỷ** | 1.253 tỷ |
| ~đỉnh | 2022-06-15 | 106.690 | 6.15 | 13.6 | 1.336 tỷ | 1.464 tỷ |

- **Xác nhận "về dưới book, LN vẫn tốt"**: đáy PB **0.73** (dưới sổ sách 27%), PE 4.4 (rẻ cả 2 chiều),
  LN quý DƯƠNG 168 tỷ, dòng tiền HĐKD DƯƠNG 197 tỷ. Lõi tạo tiền nguyên vẹn giữa panic.
- **Xác nhận "~10 lần"**: adjusted 5.450 → 88.930 (24m) = **+16,3 lần**; đỉnh mid-2022 = **+19,6 lần**.
  *Trí nhớ user ("10 lần") CONSERVATIVE — thực tế cao hơn.*
- **★ TÁCH CƠ CHẾ (yêu cầu dispatch #4):** phân rã 16,3× = **PE 3,7× × EPS 4,4×**.
  - ~½ multi-bagger = **de-rate reversal** (PB 0.73→6.15, PE 4.4→16.3): thị trường trả lại giá trị khi
    hết panic — phần này là **VALUE THẬT**, lặp lại được.
  - ~½ còn lại = **EPS nổ 8×** (168→1.336 tỷ/quý) = **SIÊU CHU KỲ PHOTPHO/hoá chất 2021-22** (TQ siết
    xuất khẩu photpho + Nga-Ukraine đứt gãy phân bón) — phần này là **TRÚNG CHU KỲ HÀNG HOÁ**, KHÔNG
    đếm được ex-ante.
  - → Entry PB 0.73/PE 4.4 đủ đảm bảo **cú de-rate 3–5×** kể cả không có super-cycle; cái đuôi "16×" là
    may siêu chu kỳ. **Đừng dùng "16×/10×" làm base case** — dùng median +38–45% excess (§0) làm kỳ vọng.

---

## 2. Phương pháp screen (auditable)

- **Nguồn**: `tav2_bq.ticker` (OHLCV/PB/PE/NP/CF, adjusted Close) JOIN `tav2_mike.universe_pit`
  (point-in-time in_universe, backfilled 2000–2026 — CANONICAL theo `data_registry.md`, KHÔNG dùng
  `ticker_prune`). VNINDEX từ hàng `ticker='VNINDEX'` gốc (né cột mirror corrupt 04/2026).
- **Panel**: mọi ticker-day PB∈(0,1), NP_P0>0, CF_OA_P0>0, in_universe, mkt_dd<−0.20.
- **Forward return**: LEAD(Close,250)=12m, LEAD(Close,500)=24m; **excess = r_stock − r_VNINDEX** cùng
  cửa sổ (khử beta thị trường chung — cô lập edge chọn-mã cross-sectional).
- **Dedup episode**: 1 episode/(ticker, crisis) — giữ ngày PB thấp nhất, cách nhau >14 tháng/mã
  (chống double-count cùng 1 khủng hoảng). 1.315 → 954 episode.
- Script: `fearbuy_screen/screen2.sql` + `analyze2.py`/`analyze3.py` (tái lập được).

---

## 3. Kết quả tầng-tầng (vì sao từng gate cần thiết)

**Base screen (PB<1, NP>0, CF>0, mkt_dd<−20%), N=953 realized-12m:**
- ex12 median +11.2%, winrate 61%, mean +31.7%. **Dương nhưng có 1 năm THẢM: 2010** (median −27%,
  winrate 15%, N=113).

**★ Bài học value-trap ở TẦNG THỊ TRƯỜNG (2010):** gate −20% dd bắn LIÊN TỤC suốt bear cấu-trúc
2010–2012 (lạm phát ~20%, khủng hoảng ngân hàng/BĐS). Mua "rẻ trong khủng hoảng" khi khủng hoảng
CHƯA QUA / là CẤU TRÚC → giá tiếp tục rơi vào crash 2011. **Discriminator "khủng hoảng sẽ qua" cần
chiều THỊ TRƯỜNG, không chỉ chiều doanh nghiệp.**

**Fix = yêu cầu panic SÂU (mkt_dd < −30%)** — phân biệt crash cấp tính (mean-revert) vs grind chậm:

| Gate | N | median ex12 | winrate |
|---|---|---|---|
| base (dd<−20%) | 953 | +11.2% | 61% |
| dd<−30% | 398 | **+35.7%** | 79% |
| dd<−35% | 243 | +51.7% | 87% |

Deep-DD gate gần như XOÁ SẠCH bẫy 2010. (DGC đáy dd=−35.4%, HPG COVID −32.1% → threshold −30% được
chính case thật xác nhận.)

**Gradient PB (đơn điệu — bằng chứng signal thật, không nhiễu):** PB<0.5 → ex +50%/wr65%;
0.5-0.7 → +30%/61%; 0.7-0.85 → +21%/60%; 0.85-1.0 → +13%/52%.

**Golden floor ROE_Min3Y≥0 — KHÔNG tăng mean nhưng CẮT TAIL:** trong slice (dd<−30% & PB<0.7),
bỏ nhánh ROE_Min3Y<0 (N=31) làm tỷ lệ blow-up (r24<−50%) từ **6.5% → ~1%**. Đúng vai trò đội đã
định: **binary tail-guard, không phải return-tilt.**

---

## 4. Combined rule FEARBUY v1 — thống kê tổng hợp

**(mkt_dd<−0.30) ∧ (PB<0.7) ∧ (NP_P0>0 ∧ CF_OA_P0>0) ∧ (ROE_Min3Y≥0)**, dedup, N=237:

| | median | mean | winsor mean | winrate |
|---|---|---|---|---|
| excess 12m | **+37.8%** | +71.6% | +62.1% | **77%** |
| excess 24m | **+45.3%** | +119.4% | +97.8% | 68% |

**Robustness cấp-khủng-hoảng (N_eff thật = số regime, KHÔNG phải 237):**
median excess 12m mỗi năm: 2008 +43% · 2009 +52% · 2010 +28% · 2011 +11% · 2012 +54% · 2020 +140% ·
2022 +31% · 2023 +39%. → **8/8 năm DƯƠNG, sign-test p=0.0039.** Yếu nhất 2011 (+11%, đúng bear cấu
trúc khó nhất). Mạnh nhất 2020 (+140%, cú V COVID).

**Tail (r24 tuyệt đối, N=236):** chỉ **0.8%** mất >50%; 15.3% âm; **47% hơn gấp đôi (>+100%)**.
Worst survivors: CYC −60%, **PVX −57%** (đúng mã value-trap trong case library — lọt lưới vì ROE_Min3Y
tạm ≥0 nhưng lõi PVC/xây lắp đang phá sản). → **không filter nào hoàn hảo.**

**Commodity KHÔNG phải động lực (dispatch #4):** dưới combined rule, **non-commodity median +47.5%
(N=184) > commodity +12.5% (N=53)**. DGC/HPG là cái đuôi nổi bật nhưng là subset MEDIAN THẤP HƠN +
phụ thuộc chu kỳ. **Edge lõi = deep-value-trong-panic DIỆN RỘNG mọi ngành, KHÔNG cần siêu chu kỳ
hàng hoá.** Salience bias: user nhớ commodity 10-bagger, nhưng screen cho thấy value phi-hàng-hoá
đáng tin hơn.

---

## 5. Caveat trung thực (KHÔNG được bỏ qua khi trích dẫn)

1. **N_eff ≈ 8 regime, KHÔNG phải 237.** Episode trong cùng 1 khủng hoảng tương quan chéo (chung beta).
   Excess-vs-VNINDEX đã khử phần lớn factor chung, nhưng residual sector/beta còn. → Độ tin cậy nằm ở
   **"dương MỌI khủng hoảng" (p=0.0039)**, KHÔNG ở con số điểm +38% (band rộng). Vì lý do này KHÔNG
   tính DSR daily (giả định iid → thổi phồng); sign-test cấp-crisis là thống kê trung thực.
2. **Edge dồn về cửa sổ hồi phục nhanh** (2020 +140%). Ngoài đó vẫn dương nhưng khiêm tốn (2011 +11%).
3. **Không filter nào hoàn hảo** — PVX 2011 qua rule vẫn mất 57%. → Screen là **CANDIDATE GENERATOR**;
   discriminator due-diligence §2/§2.5 của `calculated_fear_state_backstop.md` (chu-kỳ-vs-cấu-trúc,
   scandal-chạm-lõi-chưa, CF_OA≥NP) vẫn là **HARD GATE thủ công** trên mỗi tên, user duyệt riêng.
4. **PB neo vào TÀI SẢN, không phải PE** ở đáy chu kỳ (bài học HPG §8 library): dùng PB làm sàn định
   giá; PE thấp/EPS sập ở đáy là LÝ DO rẻ, không phải cảnh báo.
5. Chưa mô hình chi phí thanh khoản/impact khi gom mã PB<0.7 ở đáy panic (nhiều mã kém thanh khoản lúc
   đó) — số excess là lý thuyết mid-price, thực thi sẽ hao.

---

## 6. Đề xuất dùng (không wire production — chờ user)

- **Biến `fearbuy_weekly_scan.sh` thành CÓ ĐỊNH LƯỢNG**: chạy FEARBUY v1 screen mỗi tuần trên dữ liệu
  hiện tại (mkt_dd<−30% là gate BẬT/TẮT toàn cục — hiện 2026 chưa −30% nên screen "ngủ"; khi thị trường
  crash sâu nó tự bật ra danh sách ứng viên PB<0.7 lõi-còn-tốt). Kết hợp với anomaly gate hiện có.
- **Sizing**: đây là sleeve special-situation ≤0.5–1.0% NAV/tên như TV1/DGC discretionary, NGOÀI book
  V2.4. Vào chậm ở đáy, giữ 12–24 tháng, chốt theo PB normalize ~1.5–2.0×.
- Mỗi tên vẫn PHẢI qua due-diligence §2/§2.5 + user duyệt. Screen chỉ thu hẹp vũ trụ tìm kiếm.

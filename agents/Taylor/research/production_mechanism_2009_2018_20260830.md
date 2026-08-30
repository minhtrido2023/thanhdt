# Cơ chế production cho 2 điểm mù đã xác nhận: 2009 rally bị bỏ lỡ + 2018 phân kỳ EM

Job `Taylor_20260830_121551`. Đề xuất nghiên cứu — **KHÔNG wire, KHÔNG sửa `macro_state_live.py`
/ production**. Dùng lại (không chạy lại) Phase A/B đã verify hôm nay
(`crisis_stress_dt5g_2007_2012_20260830.md`, `v2p4_survival_backtest_2007_2009start_20260830.md`)
+ Bobby's BLIND phase-map (`vn_macro_regime_history_2009_2018_phases.md`) làm nền, cộng 1 backtest
chỉ báo mới (Q B) chạy hôm nay.

---

## CÂU HỎI A — 2009: tách nguyên nhân

### A.1 — Kết luận: KHÔNG phải (a) state-gate cap, cũng KHÔNG chủ yếu (b) data artifact — mà là NGUYÊN NHÂN THỨ BA: thiết kế tier của chiến lược đòi state 4/5

Bằng chứng trực tiếp (đã có sẵn, không suy đoán):
- **DT5G cap CRISIS chỉ khoá tới 2009-05-18** (Phase A). Sau đó DT4 base tự chuyển **NEUTRAL
  2009-06-02, giữ ~6 tháng** tới 2009-12-07. Tức: **quá nửa 2009 (H2) đã ở NEUTRAL, KHÔNG bị macro
  cap giữ ở CRISIS.** → giả thuyết (a) "state gate giữ exposure thấp suốt năm" bị bác bỏ trực tiếp.
- Nhưng `invested_bal`/`invested_lag` = **0,000 TUYỆT ĐỐI cả 2009**, kể cả 133/251 phiên NEUTRAL
  (backtest 08-25, đã quant-skeptic CONFIRMED). Nếu nguyên nhân thuần là (b) data artifact (PCF/PS
  coverage 0%), ta kỳ vọng MỘT SỐ mã vẫn lọt qua nhánh 1/PE hoặc LAG PEAD (dù thưa) — nhưng số liệu
  cho thấy KHÔNG một phiên nào có >1% invested trong cả năm, ở CẢ base lẫn lever scenario.
- Nguyên nhân thật, đã xác nhận trực tiếp trong `backtest_2008_v24_20260825.md`: **`signal_v11_sql.py`
  gate CỨNG mọi tier momentum mạnh nhất (MEGA/S_PRO/MOMENTUM/MOMENTUM_QUALITY/MOMENTUM_S/MOMENTUM_A)
  vào `state5 IN (4,5)`** — tức BULL/EXBULL. Và: **DT5G (= DT4 base ở giai đoạn này, macro cap không
  còn hoạt động sau 05/2009) KHÔNG BAO GIỜ đạt state=4 hay 5 trong toàn bộ 2008-2013** — kể cả suốt
  con sóng hồi +57,9% của 2009. Chỉ còn 2 lối hẹp ở NEUTRAL (`MOMENTUM_N`/`MOMENTUM_S_N`, điều kiện
  rất chặt; `COMPOUNDER_BUY` cần `fa_tier IN('A','B')`) — cả hai **hiếm khi fire** vì (i) bản thân
  điều kiện chặt VÀ (ii) coverage cơ bản mỏng (b) làm giảm thêm xác suất fire của 2 lối hẹp đó.

**Kết luận:** đây là gate 2 TẦNG cộng hưởng, không phải một nguyên nhân đơn: **tầng 1 (chiếm ưu
thế) = thiết kế chiến lược** (SIGNAL_V11 cố ý không đuổi giá ngoài BULL/EXBULL, và DT5G/DT4 base
chưa từng gọi 2008-2013 là BULL vì bản thân giá VNI dù hồi mạnh về % vẫn không thoả tiêu chí trend
đủ dài/đủ sạch của v3.4b sau một crash sâu); **tầng 2 (thứ yếu, chỉ tác động 2 lối hẹp còn lại) =
data artifact** (b). "Hệ ngày nay với data đầy đủ" **VẪN sẽ bỏ lỡ 2009** nếu không đổi gì ở tầng
1 — vá riêng data coverage (PCF/PS) sẽ KHÔNG unlock được các tier chính, vì chúng bị khoá bởi state
chứ không phải bởi thiếu ứng viên.

### A.2 — "Vào lại lúc nào, lỡ bao nhiêu pp": không áp dụng theo khung 25/10-phiên như dự kiến

Không có "thời điểm vào lại trong 2009" để đo — hệ **không tham gia một phiên nào cả năm** (đã dẫn
ở A.1), nên số pp bỏ lỡ ≈ toàn bộ +57,9% (thước đo tham chiếu VNINDEX, không phải target trực tiếp
của hệ). Cam kết bất đối xứng 25-phiên-vào/10-phiên-ra **không phải nút thắt** ở đây — ngay cả nếu
tune nhanh hơn, DT4/v3.4b base tự nó (không có macro cap sau 05/2009) vẫn không đạt ngưỡng BULL
trong suốt 6 năm 2008-2013 (fact đã verify, không phải suy đoán). Nút thắt nằm ở NGƯỠNG BULL của
base + tier-gate của chiến lược, không phải tốc độ chuyển state.

### A.3 — Cơ chế ứng viên: KHÔNG revive EASING_FLOOR; hướng khả dĩ hơn là valuation-gated tier
unlock, nhưng CHƯA kiểm chứng được cho 2009 vì thiếu warm-up dữ liệu

**Vì sao KHÔNG đề xuất lại EASING_FLOOR (rate-cut based):** đã tắt có chủ đích 2026-06-03, và 2
nghiên cứu độc lập trước đó (2026-06-22, KB `archive/2026-W26-W27-raw-events.md`) đã bác bỏ họ
chỉ báo dựa trên lãi suất:
- Tín hiệu lãi suất **HIKE** sạch/bearish nhưng **CUT** mơ hồ (context-dependent, sự kiện đối
  chứng 06/2022: xuống -25% từ đỉnh nhưng KHÔNG rẻ so với lịch sử riêng → nếu dùng easing floor sẽ
  bị false bounce đúng lúc đó).
- Chỉ báo THẬT phân biệt được đáy thật/giả là **valuation vs LỊCH SỬ RIÊNG (pb_z)**, không phải
  hướng lãi suất: cheap (pb_z≤-0,3) → fwd6M mean +19,8% win100% (n=3) so với naive deploy coinflip
  (n=39, +0,2%); rate-easing-only vô nghĩa (n=34, +0,0%).
- Combo rate+RE+gold+cheap bị REFUTED làm early-bottom signal riêng (fires 5-8 tháng SAU đáy thật,
  single-episode carry) — thêm bằng chứng không nên quay lại rate-based trigger.

**Hướng ứng viên hợp lý hơn (CHƯA test, đề xuất R&D):** thay vì phục hồi EASING_FLOOR (rate), mở
rộng ý tưởng đã validate — "cheap-vs-own-history + exiting CRISIS" — từ chỗ đang dùng như một
ALLOCATION-CURVE concept sang **mở khoá có điều kiện các tier SIGNAL_V11 hiện đang khoá cứng
`state5 IN (4,5)`**, tức: cho phép tier mạnh fire ở NEUTRAL(3) **NẾU ĐỒNG THỜI** (i) vừa thoát
CRISIS và (ii) định giá rẻ so với lịch sử riêng (pb_z). Đây khác EASING_FLOOR ở chỗ tín hiệu neo
vào GIÁ/ĐỊNH GIÁ (đã chứng minh có tính phân biệt thật), không neo vào hướng chính sách lãi suất
(đã chứng minh mơ hồ).

**Vì sao CHƯA kiểm chứng được cho đúng 2009 — bẫy dữ liệu cụ thể, đo trực tiếp hôm nay:**
`data/value_radar_series.csv` (nguồn PE/PB cấp-index CANONICAL) floor **2008-01-02** — chỉ có
~250 phiên trước khi bước vào 2009. Phương pháp CHÍNH THỨC của Value Radar là **percentile rolling
10 năm (2500 phiên, min 500)** — 2009 hụt warm-up NGHIÊM TRỌNG (thiếu ~2250 phiên so với yêu cầu
tối thiểu), nên KHÔNG thể tính `pb_z`/percentile hợp lệ cho 2009 bằng đúng phương pháp canonical.
Số tuyệt đối đo được (không qua percentile): PE cap10 = 7,4-9,1x, PB cap10 = 1,2-1,5x trong Q1 2009
— rẻ rõ rệt về mặt tuyệt đối — nhưng dùng ngưỡng tuyệt đối cho MỘT episode duy nhất là đúng loại
overfit-vào-1-sự-kiện mà §29/§28 coding_guidelines cảnh báo, không phải bằng chứng percentile thật.

**Đề xuất cụ thể (chưa làm, cần job riêng):** (1) xây percentile pb_z dùng cửa sổ warm-up NGẮN HƠN
khả thi cho 2008-2009 (vd 3-năm hoặc expanding-từ-2000 nếu có dữ liệu PB xa hơn ở BQ `ticker` thô,
KHÔNG phải value_radar_series.csv) — phải tự thấy rõ đây là phương pháp KHÁC canonical, gắn nhãn
"thử nghiệm, không phải Value Radar chính thức"; (2) backtest valuation-gated tier-unlock đầy đủ
IS/OOS + self-check + DSR/PBO trước khi coi là ứng viên thật; (3) quant-skeptic review bắt buộc
trước khi trình user — đúng ranh giới dispatch, không tự tiến thêm hôm nay.

---

## CÂU HỎI B — 2018: chỉ báo vá điểm mù

### B.1 — Khả thi dữ liệu: 2/4 chỉ báo Bobby đề xuất DÙNG ĐƯỢC, 1/4 KHÔNG dùng được cho chính episode nó nhắm vá

| Chỉ báo | Nguồn | Khả thi? |
|---|---|---|
| **MSCI EM proxy (EEM ETF)** | `data/tier2_macro_panel.csv`, cột `EEM`, 2011-01-04→2026-05-15 | ✅ Khả thi |
| **DXY** | cùng file, cột `DXY` | ✅ Khả thi (cũng có ở `data/macro_features.csv` từ 2011) |
| **UST 10Y** | cùng file, cột `TNX` (đơn vị %, đã verify: 2018-04 quanh 2,78-2,94, cắt 3% cuối 04/2018 — khớp mốc Bobby 24/04/2018) | ✅ Khả thi |
| **Bán ròng khối ngoại KHỚP LỆNH HOSE** | `mike/kb/data_registry/feeds/foreign_flow_vndirect.md` (VNDirect finfo) | ❌ **KHÔNG khả thi cho chính 2018** — nguồn chỉ sâu từ **2018-08-30**, tức SAU khi đợt bán tháo chính (04-07/2018, VNI -11% riêng tháng 4) đã xảy ra xong. Không có cách nào backtest được đúng episode Bobby chỉ ra bằng nguồn dữ liệu hiện có. |

Đã kiểm cả `foreign_room`/snapshot vnstock (từ job Winston 2026-07-06) — chỉ có PIT snapshot, KHÔNG
có chuỗi lịch sử. **Kết luận B.1: chỉ báo dòng vốn ngoại khớp lệnh — dù có căn cứ nhân quả tốt nhất
theo Bobby — hiện KHÔNG có dữ liệu lịch sử để test hay wire.** 2 chỉ báo còn lại (EEM, DXY/TNX) khả
thi và đã test dưới đây.

### B.2 — PRE-REGISTERED test: EM-VN divergence + DXY/UST10Y confirm, toàn lịch sử 2011-2026

**Tiêu chí khoá TRƯỚC khi chạy** (chọn số tròn từ mô tả định tính của Bobby, không tune theo kết
quả): cửa sổ rolling 60 phiên (~3 tháng, khớp "MSCI EM đỉnh trước VN 2 tháng"); `EM_dd60 ≤ -8%`
(EM đã rớt ≥8% từ đỉnh 60-phiên) **AND** `VNI_dd60 ≥ -3%` (VN vẫn quanh đỉnh riêng, chưa xác nhận)
= tín hiệu `DIVERGE`. Bộ lọc xác nhận: `DXY 60-phiên ≥ +5%` HOẶC `TNX ≥ 3,0%` = `CAP_SIGNAL`
(DIVERGE AND xác nhận). Đếm episode (gộp các phiên liên tiếp cách nhau ≤10 phiên thành 1 sự kiện),
đo forward VNI return.

**Kết quả — `DIVERGE`-only (27 episode, 2011-2026):**
- **Bắt đúng 2018:** fire **2018-03-22** — đúng tuần VNI đạt đỉnh riêng (VNI_dd60=0,0%, tức đang
  ở đỉnh 60-phiên) trong khi EM đã rớt 8,1% từ đỉnh riêng. Forward 60d = **-17,9%**, forward 120d
  = **-15,8%**. Đây là tín hiệu SỚM đúng nghĩa — fire ngay trước cú sập tháng 4, không phải sau.
- **False-positive rate cao:** trong 27 episode, có **10 lần (37%)** forward-60d VNI **dương rõ
  rệt** (>+3%), tập trung 2016 (5 lần: +3,9% đến +8,1%, Brexit-era EM wobble không lan sang VN) và
  2021 (3 lần: +5,2% đến +14,5%, noise thị trường bull). Nếu dùng riêng lẻ làm cap sizing, hệ sẽ
  bị cắt giảm exposure sai **hơn 1/3 số lần fire** — đúng loại chi phí §28 cảnh báo (mỗi false
  positive trong giai đoạn bull thật = mất pp thật).

**Kết quả — `CAP_SIGNAL` (composite, thêm xác nhận DXY/TNX, 8 episode):**
- False-positive rate tương tự về TỶ LỆ (3/8 = 37,5%: 2016-11, 2016-12, 2024-12 đều fwd60 dương
  +4,9% đến +6,2%) nhưng **số episode tuyệt đối giảm mạnh** (27→8) nên tổng chi phí cơ hội thấp
  hơn nhiều.
- **Nhưng đánh đổi đúng thứ mình cần:** composite **KHÔNG fire tháng 3/2018** — DXY chưa rally đủ
  5% và TNX chưa chạm 3% tại thời điểm đó (TNX mới 2,88-2,94, DXY mom60 chỉ ~1-3%). Composite chỉ
  fire lần đầu ở episode **2018-10-04** (fwd60=-12,0%) — SAU KHI phần lớn thiệt hại (đợt sập tháng
  4, VN "tệ nhất thế giới trong tháng" theo Bobby) đã xảy ra. Tức: **siết false-positive bằng
  cách thêm bộ lọc xác nhận đã xoá đúng giá trị early-warning mà tín hiệu thô (DIVERGE-only) có
  cho chính episode 2018.**

**Ước lượng chi phí false-positive (nếu wire DIVERGE-only làm cap thật, ước thô cấp index, KHÔNG
phải backtest chiến lược):** 10 lần fire sai trên 27 lần trong 15,4 năm dữ liệu (2011-2026) ≈ 1
lần fire sai mỗi ~1,5 năm, mỗi lần cap sizing đúng lúc thị trường tăng ~+4% đến +19% trong 3 tháng
kế tiếp — đây là ĐÁNH ĐỔI CÓ THẬT, không nhỏ, phải cân với lợi ích tránh được cú sập -17,9%/-15,8%
đúng một lần (2018).

### B.3 — N=1 thật sự cho 2018, đọc thẳng theo yêu cầu dispatch

- **DIVERGE-only** có nền tảng nhân quả từ Bobby (EM outflow cycle dẫn trước VN idiosyncratic —
  đúng episode 2018 macro gate đã xác nhận mù ở Phase A hôm nay) VÀ historical false-positive rate
  đo được (37%, N=27, không phải N=1) — đây là mức độ bằng chứng CAO HƠN một chỉ báo fit-1-sự-kiện
  thuần túy, vì false-positive rate được đo trên toàn 15 năm không chỉ trên chính 2018.
- Nhưng **việc tín hiệu "bắt đúng 2018 với timing tốt" vẫn chỉ là N=1 hit trong nhóm confirmed-
  true-positive** (11/27 episode có fwd60 âm rõ, 2018-03-22 là một trong số đó) — không có cách
  tách "may mắn cụ thể cho 2018" khỏi "cơ chế đúng nói chung" chỉ bằng dữ liệu này. Kết luận trung
  thực: **DIVERGE-only là ứng viên ĐÁNG theo đuổi tiếp (căn cứ nhân quả + false-positive đo được
  không quá cao so với lợi ích), nhưng CHƯA đủ điều kiện wire** — cần ít nhất (i) test ở cấp chiến
  lược thật (không chỉ index VNINDEX) để đo pp thật bị mất mỗi false positive, (ii) DSR/PBO nếu
  định tham số hoá thêm, (iii) quant-skeptic pass riêng.

---

## Tổng kết cho user quyết

**2009:** không phải "chỉnh tốc độ commit state" hay "vá coverage dữ liệu đơn thuần" sẽ giải quyết
được — nút thắt chính là **thiết kế tier chiến lược khoá vào BULL/EXBULL mà DT5G/DT4 base chưa
từng gọi tên trong khủng hoảng cơ cấu 6 năm 2008-2013**. Hướng khả dĩ nhất (valuation-gated tier
unlock, KHÔNG phải rate-based) hiện **CHƯA kiểm chứng được cho chính 2009** vì thiếu warm-up dữ
liệu percentile — cần job riêng chấp nhận phương pháp non-canonical + gắn nhãn rõ.

**2018:** 2/4 chỉ báo Bobby đề xuất khả thi dữ liệu; chỉ báo mạnh nhất về căn cứ nhân quả (dòng
vốn ngoại khớp lệnh) **không có dữ liệu lịch sử để test**. EM-VN divergence (EEM vs VNI) khả thi,
bắt đúng 2018 với timing tốt, nhưng false-positive rate ~37% trên 15 năm — thêm bộ lọc xác nhận
giảm false-positive nhưng lại xoá đúng giá trị early-warning cho 2018. **Không có phiên bản nào
"miễn phí"** — mọi lựa chọn đều là đánh đổi định lượng được, không phải free lunch.

**Nếu kết luận hợp lệ là "chưa có cơ chế nào đủ chín để wire"** — đó CHÍNH LÀ kết quả hợp lệ theo
đúng ràng buộc dispatch. Không đề xuất sửa `macro_state_live.py` hay bất kỳ production code nào
hôm nay.

## File liên quan
- `mike/kb/data_registry/market-state/vn_macro_regime_history_2009_2018_phases.md` (Bobby, BLIND)
- `mike/kb/data_registry/market-state/vn_macro_regime_history.md` (EP-2008-09/2009-09/2018-01)
- `research/crisis_stress_dt5g_2007_2012_20260830.md` (Phase A, job hôm nay)
- `research/v2p4_survival_backtest_2007_2009start_20260830.md` (Phase B, job hôm nay)
- `agents/Taylor/research/backtest_2008_v24_20260825.md` (nguồn invested-fraction/state=4,5 facts)
- `mike/kb/archive/2026-W26-W27-raw-events.md` (2026-06-22 findings: EASING_FLOOR bác bỏ, pb_z gate validate)
- `mike/kb/data_registry/market-state/value_radar_series.md` + `data/value_radar_series.csv` (warm-up gap 2009)
- `mike/kb/data_registry/feeds/foreign_flow_vndirect.md` (khối ngoại khớp lệnh — floor 2018-08-30)
- Script test B.2: `/tmp/taylor_2018_indicator_test.py` (ephemeral — không phải canonical, chạy lại nếu cần tái lập)

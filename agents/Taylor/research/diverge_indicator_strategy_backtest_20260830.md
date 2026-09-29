# DIVERGE indicator ở cấp CHIẾN LƯỢC — NAV impact thật, không phải đếm episode

Job `Taylor_20260830_124326`. Nâng phát hiện signal-level (`production_mechanism_2009_2018_20260830.md`
§B) lên tác động NAV thật của V2.4. **KHÔNG wire, KHÔNG sửa `macro_state_live.py`/`custom_basket.py`
/production** — đề xuất nghiên cứu, chờ quant-skeptic.

## 1. Cơ chế pre-register (trước khi chạm NAV)

**Nguồn dữ liệu**: `data/tier2_macro_panel.csv` (EEM/VNI/DXY/TNX, 2011-2026) cho tín hiệu +
`data/v23_golive_audit_..._scenarioB_production_univpit_from20080101.csv` (record_type=DAILY,
cột `combined_nav`, đã quant-skeptic CONFIRMED job 08-25) cho NAV thật V2.4 (BAL+LAG, f=1.3,
2008-01→2026-08, 4.650 phiên).

**Cơ chế**: DIVERGE/CAP_SIGNAL fire → **haircut tỷ lệ H lên lợi nhuận NGÀY THẬT của
`combined_nav`** (không phải state cap rời rạc — vì không còn engine cấp cổ phiếu gốc để re-run
buy/sell, engine 08-25 là ephemeral đã dọn theo §8) trong đúng N phiên kể từ ngày fire ĐẦU TIÊN
của mỗi episode, tương đương "giảm exposure xuống (1-H) trong N phiên". Đây là một nguồn cap BỔ
SUNG song song với DT5G macro gate hiện có, KHÔNG thay thế nó — nếu wire thật sẽ cộng dồn vào
`cap_bal`/`cap_lag` hiện có.

**Grid khoá trước khi đo**: N∈{10,20} phiên (10 = tốc độ ra hiện tại của DT-gate, 20 = gấp đôi cho
biên an toàn), H∈{30%,50%,70%}. 2 họ tín hiệu: **DIVERGE-only** (27 episode) và **CAP_SIGNAL**
(composite +DXY/TNX, 8 episode) — cả hai đã pre-register nguyên văn ở job trước (B.2), không đổi
ngưỡng.

**Self-check 0 VND**: dựng lại `combined_nav` từ `ret=pct_change` rồi cumprod, so với cột nguồn —
lệch tối đa **0,0029 VND** trên NAV ~50-1.238 tỷ (làm tròn số thực floating point, coi như 0).

## 2. Kết quả — DIVERGE-only: NO-GO dứt khoát, mọi biến thể đều ÂM

| N | H | Δ CAGR (pp) | Final NAV (B) | IS 2014-19 (pp) | OOS 2020-nay (pp) |
|---|---|---|---|---|---|
| 10 | 30% | −0,30 | 1.181,0 | −15,7 | −8,6 |
| 10 | 50% | −0,50 | 1.143,7 | −26,0 | −14,5 |
| 10 | 70% | −0,71 | 1.106,7 | −36,1 | −20,6 |
| 20 | 30% | −0,39 | 1.164,8 | −15,4 | −17,3 |
| 20 | 50% | −0,65 | 1.116,6 | −25,6 | −29,1 |
| 20 | 70% | −0,93 | 1.068,9 | −35,8 | −41,1 |

Baseline (không cap): CAGR 18,79%, final NAV 1.237,6 tỷ (từ 50 tỷ, 18,63 năm). **Cả 6/6 biến thể
âm, cả IS lẫn OOS, đơn điệu theo cả N và H** (cap càng mạnh/càng dài, càng lỗ thêm) — không có
biến thể nào "thoát", nên đây không phải rủi ro chọn-biến-thể-tốt-nhất kiểu overfit; toàn bộ họ
DIVERGE-only đều thua.

**Phân rã theo episode (N=20,H=50%, dấu dương=impact có lợi)**: 10/27 episode xảy ra đúng lúc
V2.4 tự nó ĐANG LỖ trong cửa sổ đó (cap giúp, tổng +15,88pp) nhưng **17/27 episode xảy ra lúc
V2.4 tự nó ĐANG LÃI** (cap cắt oan, tổng **−27,92pp**) — false-positive cost áp đảo true-positive
benefit theo đúng tỷ lệ 37% đã cảnh báo ở cấp tín hiệu, và ở cấp NAV THẬT tỷ lệ thiệt hại còn nặng
hơn vì false-positive tập trung đúng 2016/2021 — 2 năm V2.4 đang có vị thế lớn và lãi mạnh
(episode 2021-05-12/2021-10-04 riêng đã mất 5,7pp/5,1pp).

**2018-03-22 (true positive được kỳ vọng nhất)**: impact = **−1,47pp**, ÂM chứ không dương —
vì trong đúng cửa sổ 20 phiên sau khi fire, `combined_nav` của V2.4 **tự nó vẫn đang lãi +2,9%**
(baseline_ret dương) — DT5G/DT4 base price-driven đã tự vệ đủ tốt trước khi DIVERGE kịp cắt thêm
(khớp Phase A: DT4 base tự chuyển CRISIS 2018-05-09, sau episode DIVERGE 03-22 nhưng episode kết
thúc trước khi giá thật sập). Episode DUY NHẤT thật sự "cứu" nhiều là **2018-10-04** (+4,19pp, đúng
lúc V2.4 tự nó cũng đang lỗ −8,47%) — nhưng đây là episode CAP_SIGNAL cũng bắt được (xem dưới),
không cần DIVERGE-only riêng.

## 3. Kết quả — CAP_SIGNAL composite: ĐẢO NGƯỢC kết luận cấp tín hiệu — DƯƠNG ở CẤP CHIẾN LƯỢC

| N | H | Δ CAGR (pp) | Final NAV (B) |
|---|---|---|---|
| 10 | 30% | +0,26 | 1.289,5 |
| 10 | 50% | +0,44 | 1.324,7 |
| 10 | 70% | +0,60 | 1.360,3 |
| 20 | 30% | +0,40 | 1.317,8 |
| 20 | 50% | +0,66 | 1.372,9 |
| 20 | 70% | +0,92 | 1.429,2 |

**Đảo chiều so với đọc ở cấp tín hiệu** (B.2 kết luận composite "xoá đúng giá trị early-warning
2018" vì miss episode 03-22, chỉ fire muộn 10-04): đúng, composite MISS timing sớm nhất của 2018,
nhưng số episode giảm mạnh (27→8) làm false-positive cost co lại đủ nhiều để **6/6 biến thể đều
DƯƠNG, đơn điệu theo N/H** — 6/8 episode composite trùng đúng lúc V2.4 tự nó đang lỗ (+12,87pp
gộp), chỉ 2/8 (2016-11, 2016-12, cả hai đều nhỏ) cắt oan (−3,41pp gộp). Composite là biến thể duy
nhất trong 2 họ có dấu dương ở TẤT CẢ 6 biến thể grid.

## 4. DSR/PBO — không cần chạy formal, kết luận đã robust theo cấu trúc

Không có tình huống "chọn biến thể tốt nhất trong nhiễu" — **toàn bộ họ DIVERGE-only âm, toàn bộ
họ CAP_SIGNAL dương**, đơn điệu nội bộ theo cả 2 trục (N,H) ở cả 2 họ. Đây là phân tách theo THIẾT
KẾ tín hiệu (số lượng false-positive), không phải noise thống kê cần DSR/PBO để phân biệt signal
thật khỏi may mắn — rủi ro overfit nằm ở việc chọn ĐÚNG family (đã pre-register cả 2 từ trước khi
chạm NAV), không nằm ở việc chọn N/H trong family.

## 5. Giới hạn phương pháp — nói rõ để không tự nhận mạnh hơn thật

- **Haircut lên return thực, không phải re-run buy/sell qua state-cap rời rạc**: engine cấp cổ
  phiếu gốc (`backtest_2008_v24_20260825/engine_2008.py`) đã bị dọn (ephemeral, đúng §8), nên
  không tái tạo được cơ chế "cap state → đổi tier nào được mua" chính xác 1:1. Haircut tỷ lệ trên
  NAV thật là XẤP XỈ hợp lý (tương đương giảm exposure tuyến tính) nhưng KHÔNG mô phỏng được hiệu
  ứng phi tuyến thật (vd cap có thể buộc bán sớm hơn 1 phiên, đổi timing T+1 exec).
  Nếu tiến tới wire thật → cần re-implement đúng cơ chế cap rời rạc trong engine V2.4 thật.
- **N/H cố định, không thích nghi theo độ mạnh dd60** — chưa test biến thể "haircut tỷ lệ theo
  |EM_dd60|" (có thể vừa giữ được sớm hơn cho 2018 vừa giảm false-positive nhỏ).
- Compounding: số "Δ CAGR pp" đã tính đúng theo path-dependent compounding thật (không cộng dồn
  tuyến tính từng episode) — bảng §2 cột IS/OOS tách riêng cửa sổ walk-forward chuẩn, KHÔNG cộng
  lại thành full-window vì compounding không cộng được qua ranh giới cửa sổ.

## Kết luận cho user

- **DIVERGE-only: NO-GO** — dù bắt đúng 2018-03-22 sớm ở cấp tín hiệu, ở cấp NAV thật nó cắt oan
  đúng lúc V2.4 đang lãi (2016/2021) nhiều hơn hẳn giá trị cứu được, mọi biến thể grid đều âm.
- **CAP_SIGNAL composite: ứng viên đáng theo tiếp** — dương ở mọi biến thể grid (+0,26 đến
  +0,92pp CAGR), dù bản thân nó KHÔNG giải quyết được điểm mù early-warning 2018 cụ thể (miss
  03-22, chỉ bắt 10-04 sau khi thiệt hại chính đã xảy ra) — giá trị của nó đến từ việc lọc
  false-positive tốt hơn nhiều, không phải từ timing sớm hơn.
- Trước khi coi CAP_SIGNAL là ứng viên wire thật: cần (1) quant-skeptic pass riêng cho phương pháp
  haircut xấp xỉ này, (2) nếu pass, thiết kế lại đúng cơ chế cap rời rạc trong engine V2.4 thật
  thay vì haircut tỷ lệ, (3) test thêm biến thể haircut tỷ lệ theo cường độ tín hiệu.

## File liên quan
- `research/production_mechanism_2009_2018_20260830.md` (§B, pre-register gốc + N=1 discussion)
- Script: `/tmp/diverge_strategy_test.py`, `/tmp/diverge_attrib.py` (ephemeral, chạy lại nếu cần)
- Output: `exp_insider/diverge_episodes_recheck.csv`, `exp_insider/diverge_strategy_impact_grid.csv`,
  `exp_insider/diverge_only_per_episode_impact.csv`, `exp_insider/cap_signal_per_episode_impact.csv`

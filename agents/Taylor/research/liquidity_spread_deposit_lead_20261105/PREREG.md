# PREREG — D2: spread thanh khoản VN có DẪN lãi huy động Big-4 tăng không? (paper-only)

Job `Taylor_20261104_182158` · viết 2026-11-05 ICT · **KHOÁ md5 TRƯỚC khi tính bất kỳ outcome (lãi
huy động sau tín hiệu) nào**. Trước khi khoá chỉ đã nhìn: danh sách ngày đổi `vn_policy_rate`, số
dòng/năm của `vn_interbank_3m` (cấu trúc dữ liệu, không phải kết quả). Chưa tính spread theo thời gian,
chưa đếm episode, chưa ghép với lãi huy động.

## 0. Bối cảnh & hệ quả
Kill-switch A (`macro_kill_switches.A_sbv_rate_suspend`, DISPLAY-ONLY) ARM khi lãi huy động hiệu lực
> 7,5%. D1 (dòng hiển thị "Thanh khoản VN") đề xuất spread = liên NH 3M − lãi suất điều hành làm cảnh báo
sớm. Câu hỏi: spread cao có ĐI TRƯỚC lãi huy động Big-4 tăng ở chân trời 1/3/6 tháng không?
Kết luận chỉ ở 3 mức: **ỦNG HỘ / KHÔNG ỦNG HỘ / KHÔNG KẾT LUẬN**. REFUTED/INCONCLUSIVE ⇒ D1 giữ
nguyên là hiển thị. Không gate, không sizing, không đổi `macro_state_live.py`/DT5G, không tạo object BQ.

## 1. Giả thuyết (khung nhân quả)
H1: khi `S(t)` vượt ngưỡng, lãi huy động Big-4 tăng trong 1–6 tháng sau đó.
Cơ chế giả định: căng thanh khoản (tỷ giá, tín dụng > huy động, NHNN hút tiền) ⇒ liên NH 3M vượt trần
hành lang (lãi suất tái cấp vốn) ⇒ chi phí vốn biên của NH tăng ⇒ NH nâng lãi huy động (kỳ hạn dài,
thị trường quyết định) với độ trễ tuần–tháng.
Gây nhiễu chính (ghi trước, không sửa sau):
- **C1 — chính sách chung**: NHNN tăng lãi điều hành ⇒ cả hai cùng tăng. Nhưng spread = IB − policy
  đã trừ policy, nên đợt tăng policy làm spread GIẢM cơ học; tín hiệu sạch hơn chuỗi IB thô.
- **C2 — trần hành chính kỳ hạn <6T**: lãi 1T bị NHNN áp trần (gắn với lãi điều hành) ⇒ outcome 1T phản
  ứng chủ yếu qua thay đổi trần, không phải thị trường. Đây là giới hạn đã biết của outcome chính.
- **C3 — ngược chiều/đồng thời**: lãi huy động đã tăng TRƯỚC khi spread vượt ngưỡng (cùng nguyên nhân
  gốc) ⇒ không phải "dẫn". Kiểm bằng điều kiện đi trước (§5c).
- **C4 — 2008/2011**: trần lãi huy động hành chính (14% năm 2011) chặn truyền dẫn ⇒ cơ chế khác.

## 2. Dữ liệu (đã tra `mike/kb/data_registry/macro/`)
| Vai trò | Nguồn | Ranh giới PIT |
|---|---|---|
| IB3M | `tav2_bq.macro_indicator` series `vn_interbank_3m` (TE, hằng ngày 1998-12→2026-11-02) | UNVERIFIED (TE aggregator). Lag công bố giả định **1 phiên**: giá trị ngày t chỉ dùng từ quan sát kế tiếp |
| Policy | cùng bảng, `vn_policy_rate` (TE, tháng, obs = cuối tháng) | Forward-fill theo obs cuối tháng ⇒ đợt đổi giữa tháng chỉ "thấy" từ cuối tháng (bảo thủ, không nhìn trước; làm spread lệch tạm thời vài ngày quanh mốc đổi — khai báo, không sửa) |
| **Outcome CHÍNH** | `fiinprox_deposit_1m_big4_monthly_2019_2026.csv` (Big-4, 1T, cá nhân; asof = ngày 15 mỗi tháng) | **Số THẬT chỉ 2019-02→2026-09**. KHÔNG dùng phần dựng lại trước 2019-02 (dựng từ `sbv_low` = gần chính policy ⇒ vòng tròn với spread) |
| Outcome PHỤ (minh hoạ) | `deposit_rate_vn.py` `DEPOSIT_EVENTS` (12T Big-4, 26 mốc) + `data/deposit_rate_vn_events.csv` | **KHÔNG PIT**: 26 mốc neo hồi tố 1 lần 2026-06-19, mốc thô (nhiều năm chỉ 1 mốc 01/01), một phần calibrate từ hình dạng lãi cho vay TE. Không được tự lật verdict |
Snapshot: `data/te_ib3m_policy.csv` md5 `fb65e9bf9f5ee93a73006978968b7c6c` (BQ, kéo 2026-11-05 ~01:3x ICT).
2008 & 2011: **không có chuỗi lãi huy động nào trong repo** (12T bắt đầu 2011-01 "context only") ⇒
chỉ minh hoạ đường spread + policy, KHÔNG chấm outcome. Không lấy số web hồi tố để chấm.

## 3. Định nghĩa
- `S(t) = IB3M(t) − Policy_ffill(t)` (pp), t = ngày có quan sát IB3M.
- **Episode** (ngưỡng `thr`): onset = ngày thứ 5 liên tiếp có `S ≥ thr`; **ngày tín hiệu** = quan sát
  IB kế tiếp sau onset (lag công bố 1 phiên). Episode kết thúc khi `S < thr` 20 quan sát liên tiếp.
  Onset mới chỉ được tính nếu cách onset được tính trước ≥ 183 ngày (cửa sổ outcome 6T không chồng).
- `thr` CHÍNH = **+1,0pp** (IB vượt trần hành lang ≥1pp = căng thật, chọn a priori, không tune).
  Độ nhạy (báo cáo hết, KHÔNG chọn): `thr = 0,0` và `+2,0`.
- Outcome tại chân trời h ∈ {1,3,6} tháng: `Δh = Dep(asof_last ≤ T+h) − Dep(asof_last ≤ T)`, T = ngày
  tín hiệu, `T+h` = cộng h tháng lịch. Chỉ tính khi `asof_last ≤ T+h` ≥ asof tương ứng thật có trong
  chuỗi (không ngoại suy; thiếu chân trời ⇒ ghi "chưa đủ dữ liệu").
- Pre-trend (C3): `Pre3 = Dep(asof_last ≤ T) − Dep(asof_last ≤ T−3T)`.

## 4. N độc lập
1 quan sát = **1 episode** (≈ 1 chu kỳ căng thanh khoản), KHÔNG phải ngày/tháng. Với outcome chính
(2019-03→2026-09) dự kiến chỉ 1–3 episode ⇒ **N rất nhỏ; không có p-value tần suất nào mang nghĩa**.
Step 0 (pre-flight power) ⇒ NO-GO cho mọi phép kiểm có ý nghĩa thống kê ở N này; nghiên cứu này là
**khung nhân quả + minh hoạ từng chu kỳ**, không phải kiểm định. Không chạy DSR/PBO (không đề xuất config).
N_trials khai trung thực: 3 ngưỡng × 3 chân trời × 2 outcome; chỉ ngưỡng CHÍNH + outcome CHÍNH quyết verdict.

## 5. Null / placebo (khai trước)
a. **Random-date placebo**: lấy ngẫu nhiên N_eval ngày trong cùng cửa sổ outcome chính (ngày có quan
   sát IB, đủ 6T tương lai), B = 10.000, seed 20261105; median Δh của placebo ⇒ phân vị của median
   Δh thật.
b. **Drift vô điều kiện**: trung bình Δh trên mọi ngày IB trong cửa sổ.
c. **Đi trước (C3)**: `Pre3` của từng episode.
d. **Minh hoạ ngược**: các tháng `S` thấp (≤ phân vị 20 trong cửa sổ) — Δh trung bình, để xem đối xứng.

## 6. Luật verdict (outcome CHÍNH, thr CHÍNH; khoá trước)
N_eval = số episode có đủ Δ6.
- **ỦNG HỘ** ⇔ N_eval ≥ 3 ∧ Δ6 > 0 ở ≥ N_eval−1 episode ∧ median Δ6 ≥ +0,25pp ∧ median Δ6 > P90 placebo
  ∧ median Pre3 ≤ +0,10pp.
- **KHÔNG ỦNG HỘ** ⇔ N_eval ≥ 2 ∧ (median Δ6 ≤ 0 ∨ median Δ6 ≤ median placebo).
- Còn lại ⇒ **KHÔNG KẾT LUẬN** (gồm mọi ca N_eval < 2; N_eval = 2 cùng dương cũng chỉ là KHÔNG KẾT LUẬN).
Outcome phụ 12T + ngưỡng độ nhạy + 2008/2011: báo cáo minh hoạ, **không lật verdict**. Mâu thuẫn giữa
chính và phụ ⇒ nói ra, verdict vẫn theo chính.

## 7. Self-check bắt buộc
1. Tái lập đo của Mike: `S` tại quan sát IB cuối = **+2,33pp**, phân vị **93%** so với `S` hằng ngày từ
   2012-01-01 (khai cách tính phân vị dùng; lệch >0,01pp hoặc >1 điểm phân vị ⇒ ghi lệch, không lờ).
2. Outcome đọc từ đúng CSV; assert 92 dòng, 1 series, khoảng 2019-02→2026-09.
3. Không ngày nào dùng IB/policy sau ngày tín hiệu (assert trong code).
4. Chạy dưới `env -u TZ` và `TZ=America/New_York` ⇒ output byte-identical.
5. Fail-closed: thiếu file/series rỗng/IB stale > 7 ngày so với asof ⇒ dừng rc≠0, in lỗi thật.

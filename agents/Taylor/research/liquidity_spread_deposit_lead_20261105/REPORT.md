# D2 — Spread thanh khoản (IB3M − policy) có DẪN lãi huy động Big-4 tăng? — REPORT

Job `Taylor_20261104_182158` · PREREG md5 `2098a999f2daade7dff3c4332996637c` khoá + commit `ce1778bb6`
TRƯỚC khi tính outcome · chạy: `$DNA_PYEXE analysis.py --asof 2026-11-05` · số liệu: `results.json`,
`episodes_thr*.csv` · selfcheck `selfcheck.sh` 6/6 PASS (env -u TZ ≡ TZ=America/New_York byte-identical).

## Verdict (luật PREREG §6, cơ học): **ỦNG HỘ — ở mức BIÊN, MONG MANH**
N_eval = **3 episode** (không phải số ngày) có outcome 1T thật (FiinPro, 2019-02→2026-09):

| Tín hiệu (thr +1,0pp) | Policy | S max 6T | Δ1T 1M / 3M / 6M (pp) | Pre3 | 12T hồi tố Δ6 (không PIT) |
|---|---|---|---|---|---|
| 2022-09-05 | 4,0 | +3,09 | 0,0 / **+1,8** / **+1,8** | 0,0 | +1,7 |
| 2025-01-02 | 4,5 | +1,25 | +0,02 / −0,05 / −0,05 | +0,03 | 0,0 |
| 2025-08-15 | 4,5 | +4,70 | 0,0 / 0,0 / **+0,5** | 0,0 | +1,2 |

median Δ6 = **+0,50pp** > P90 placebo **+0,10** (phân vị 93,7% của 10.000 placebo cùng N=3); 2/3 dương
(= N−1); pre3 median 0 (lãi huy động CHƯA tăng trước tín hiệu ⇒ đi trước, không đồng thời). Drift vô
điều kiện cùng cửa sổ: Δ6 −0,18pp; ngày S thấp (≤P20): Δ6 −0,26pp — đối xứng đúng chiều.
Ở chân trời 1T/3T **không** vượt placebo (phân vị 27,6% / 42,6%) ⇒ nếu có dẫn thì độ trễ ~3–6 tháng.

## Vì sao "biên, mong manh" (đọc trước khi dùng)
1. **N=3, đúng mép luật** (N≥3, ≥N−1 dương). Leave-one-out (hậu kiểm, NGOÀI PREREG): bỏ BẤT KỲ episode
   nào ⇒ N=2 ⇒ KHÔNG KẾT LUẬN (3/3). Không có p-value tần suất nào có nghĩa ở N này.
2. **2022Q4 gây nhiễu chính sách (C1+C2)**: NHNN tăng lãi điều hành 18 ngày sau tín hiệu và nâng trần
   lãi <6T cùng đợt (kiến thức nền, chưa verify trong phiên) ⇒ +1,8pp của 1T chủ yếu qua trần hành
   chính. Spread "báo trước" đúng thời điểm, nhưng truyền dẫn đi qua policy, không thuần thị trường.
3. **Episode 2025-08 = chính đợt đang chạy** (S hiện +2,33 là phần tiếp nối của nó; thr +2,0 onset
   2025-12-04 cùng đợt). Kết quả này KHÔNG phải quan sát độc lập mới cho tình huống hiện tại.
4. Placebo rút từ cùng cửa sổ 2019–2026 (có chứa chính các episode) ⇒ hơi bảo thủ, không làm đẹp số.
5. Outcome 1T bị trần NHNN (C2); chuỗi 12T thị trường hơn nhưng là mốc hồi tố 2026-06-19, thô, không PIT.

## Độ nhạy (báo hết, không chọn)
- thr 0,0: 2 episode trong cửa sổ (2022-08 +1,8; 2024-04 −0,02) ⇒ KHÔNG KẾT LUẬN.
- thr +2,0: 2 episode (2022-09 +1,8; 2025-12 +0,5) ⇒ KHÔNG KẾT LUẬN theo luật (N=2), cùng chiều dương.
- Liều–đáp ứng yếu nhưng đúng chiều: episode thất bại đều là spread vừa chớm ngưỡng (2024-04 S max 1,31;
  2025-01 S max 1,25); episode thành công có S max ≥3.
- 12T hồi tố (không PIT): thr 0 [+2,0; 0,0] · thr 1 [+1,7; 0,0; +1,2] · thr 2 [+1,7; +1,6] — cùng chiều.

## Minh hoạ chu kỳ không có outcome (repo không có chuỗi lãi huy động trước 2011)
- **2008**: S lên 2,0–3,6pp từ 11/2007, đỉnh +8,17pp 26/05/2008 — TRƯỚC đợt NHNN nâng policy 7,5→13→15%
  (05–06/2008); S về ≤0 từ 11/2008 khi nới. Spread dẫn chính sách; lãi huy động: không có dữ liệu để chấm.
- **2011**: S +4,4…+4,8pp (TB tháng) 11/2010–02/2011 (trước chuỗi tăng 9→14%), rồi ÂM từ 06/2011 khi policy 14–15%
  và trần huy động 14% hành chính ⇒ cơ chế C4, spread mất nghĩa thị trường. Không chấm.
- **2022Q4**: S từ −1,5 (06/2022) lên +2,66 (10/2022) — dẫn đợt tăng 09–10/2022; đã chấm ở bảng trên.

## Self-check vs đo của Mike
S tại quan sát IB cuối (2026-11-02) = **+2,33pp** ✓; phân vị so với S hằng ngày từ 2012-01-01
(n=3.825): **92,81%** (≤) / 92,78% (<) ⇒ "93%" ✓ (lệch 0 sau làm tròn).

## Hệ quả đề xuất
- Không đề xuất wire/gate/sizing. D1 nên **giữ DISPLAY-ONLY**; có thể đổi nhãn "giả thuyết chưa kiểm" ⇒
  "ủng hộ biên (N=3, LOO mong manh), độ trễ 3–6T" — chỉ sau khi quant-skeptic CONFIRMED.
- Hàm ý theo dõi (không phải hành động): đợt căng hiện tại đã cho +0,5pp ở 1T và +1,2pp ở 12T (hồi tố)
  trong 6T; kill-switch A (ngưỡng 7,5%) đáng theo dõi, không tự động.
- Đo lại khi có episode thứ 4 độc lập (cách ≥183 ngày sau khi đợt hiện tại kết thúc).

## Giới hạn dữ liệu
TE aggregator UNVERIFIED; policy TE stamp cuối tháng (đợt đổi giữa tháng làm S lệch vài ngày); outcome
1T là snapshot FiinPro đông cứng (hết nguồn sau 2026-09) ⇒ không cập nhật được nếu không có nguồn mới.

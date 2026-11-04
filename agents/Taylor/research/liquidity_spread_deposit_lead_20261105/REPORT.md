# D2 — Spread thanh khoản (IB3M − policy) có DẪN lãi huy động Big-4 tăng? — REPORT

Job `Taylor_20261104_182158` · PREREG md5 `2098a999f2daade7dff3c4332996637c` khoá + commit `ce1778bb6`
TRƯỚC khi tính outcome · chạy: `$DNA_PYEXE analysis.py --asof 2026-11-05` · số liệu: `results.json`,
`episodes_thr*.csv` · selfcheck `selfcheck.sh` 7/7 PASS (env -u TZ ≡ TZ=America/New_York byte-identical, cả `analysis.py` và `analysis_r2.py`).
**Vòng 2 (quant-skeptic INCONCLUSIVE) — xem mục "VÒNG 2" ngay dưới: nhãn cuối = KHÔNG KẾT LUẬN / INCONCLUSIVE.**

## Verdict cơ học (luật PREREG §6): ỦNG HỘ biên — NHƯNG nhãn cuối sau vòng 2 = **KHÔNG KẾT LUẬN / INCONCLUSIVE**
Cơ học theo PREREG §6 ra "ủng hộ biên" (số dưới đây giữ nguyên, không đổi); quant-skeptic không chấp nhận mạnh hơn, và vòng 2 (mục dưới) xác nhận: nhãn chỉ đứng ở 1 góc.
N_eval = **3 episode** (không phải số ngày) có outcome 1T thật (FiinPro, 2019-02→2026-09):

| Tín hiệu (thr +1,0pp) | Policy | S max 6T | Δ1T 1M / 3M / 6M (pp) | Pre3 | 12T hồi tố Δ6 (không PIT) |
|---|---|---|---|---|---|
| 2022-09-05 | 4,0 | +3,09 | 0,0 / **+1,8** / **+1,8** | 0,0 | +1,7 |
| 2025-01-02 | 4,5 | +1,25 | +0,02 / −0,05 / −0,05 | +0,03 | 0,0 |
| 2025-08-15 | 4,5 | +4,70 | 0,0 / 0,0 / **+0,5** | 0,0 | +1,2 |

median Δ6 = **+0,50pp** > P90 placebo **+0,10** (phân vị 93,7% của 10.000 placebo cùng N=3); 2/3 dương
(= N−1); pre3 median 0 (lãi huy động CHƯA tăng trước tín hiệu ⇒ đi trước, không đồng thời). Drift vô
điều kiện cùng cửa sổ: Δ6 −0,18pp; ngày S thấp (≤P20): Δ6 −0,26pp — đối xứng đúng chiều.
Ở chân trời 1T/3T **không** vượt placebo (phân vị 27,6% / 42,6%). (Câu "độ trễ ~3–6T" ở bản trước ĐÃ BỎ: quét h=1..9 cho thấy median = 0 đến h=4 và +0,5 chỉ từ h=5, chính là một bước lãi của đợt 2025-08 — xem vòng 2.)

## Vì sao "biên, mong manh" (đọc trước khi dùng) — vòng 1
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
- Không đề xuất wire/gate/sizing. D1 **giữ DISPLAY-ONLY**, nhãn "giả thuyết chưa kiểm" giữ nguyên
  (nhãn đúng sau vòng 2: **KHÔNG KẾT LUẬN / INCONCLUSIVE**).
- Không rút hàm ý theo dõi/hành động nào cho MỨC spread hiện tại từ kết quả này (D1 hiển thị mức; điều kiện theo mức không cho tín hiệu — vòng 2 mục B).
- Đo lại khi có episode thứ 4 độc lập (cách ≥183 ngày sau khi đợt hiện tại kết thúc).

## Giới hạn dữ liệu
TE aggregator UNVERIFIED; policy TE stamp cuối tháng (đợt đổi giữa tháng làm S lệch vài ngày); outcome
1T là snapshot FiinPro đông cứng (hết nguồn sau 2026-09) ⇒ không cập nhật được nếu không có nguồn mới.

## VÒNG 2 — theo yêu cầu quant-skeptic (job `Taylor_20261104_183446`)
Phân tích bổ sung **POST-HOC, NGOÀI PREREG**, script `analysis_r2.py` → `results_r2.json` (tái dùng hàm của
`analysis.py`, không sửa). **Không đổi kết quả đã khoá** (`results.json`, `episodes_*.csv`, PREREG md5 `2098a999…` giữ nguyên).

### A. Quét chân trời h=1..9 tháng (Δ lãi 1T Big-4, pp; thr +1,0; 3 episode)
| Tín hiệu | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 |
|---|---|---|---|---|---|---|---|---|---|
| 2022-09-05 | 0 | +1,0 | +1,8 | +1,8 | +1,8 | +1,8 | +1,8 | +1,8 | +1,5 |
| 2025-01-02 | +0,02 | 0 | −0,05 | −0,05 | −0,05 | −0,05 | −0,05 | −0,05 | −0,05 |
| 2025-08-15 | 0 | 0 | 0 | 0 | +0,5 | +0,5 | +0,5 | +0,5 | +0,5 |
| **median** | **0** | **0** | **0** | **0** | **+0,5** | **+0,5** | **+0,5** | **+0,5** | **+0,5** |

Median = 0 ở h=1..4; +0,5 từ h=5 **chính là đợt 2025-08** (một bước lãi 1T 1,60→2,10 ngày 2026-01-15,
~1 tháng SAU khi spread vọt ~3pp — không phải 5–6 tháng sau onset biên). ⇒ "độ trễ ~3–6T" không có cơ sở; đã bỏ.

### B. Điều kiện theo MỨC spread (cái D1 hiển thị), mọi ngày quan sát có S≥thr
| Điều kiện | n ngày (Δ3 / Δ6 đo được) | median Δ3 | median Δ6 | mean Δ6 | tỉ lệ Δ6>0 | tháng độc lập: Δ6>0 / tổng |
|---|---|---|---|---|---|---|
| S ≥ 1,0 | 352 / 292 | 0 | 0 | +0,09 | 47,9% | 10 / 27 |
| S ≥ 2,0 | 229 / 170 | 0 | **0** | +0,04 | 40,6% | 4 / 11 |

Ngày liền kề tương quan mạnh ⇒ đọc cột "tháng độc lập", không đọc số ngày. Phản ví dụ rõ nhất: 2023-01-16
S=+2,85 (30 ngày S≥2 trong 2023Q1) nhưng Δ3=0, **Δ6=−1,5** (lãi 1T giảm sau đỉnh 2022 — hệ quả đảo chiều
trần huy động NHNN, hành chính). Theo mức: S cao **không** kéo lãi huy động tăng trong 6T (median 0).
2022 là hệ quả trần huy động NHNN (hành chính), không phải truyền dẫn thị trường.

### C. Đếm độc lập theo regime — áp lại verdict với N=2 chu kỳ
Regime := episode thr 0 theo đúng luật kết thúc PREREG §3 (20 obs liên tiếp S<0 mới kết thúc) — định nghĩa
có sẵn, không tune. Kết quả: 2022-07-25→2023-07-10 (chứa tín hiệu 2022-09) và **2024-04-15→nay** (chứa CẢ
2025-01 và 2025-08: trong dải 2024-05→2025-10, S≥0 ở 345/368 ngày, min −0,5; giữa hai tín hiệu 8 ngày S<0,
min −0,18, 134 ngày S<1). ⇒ 2025-01 và 2025-08 **không phải 2 đợt độc lập** mà là 2 điểm trong 1 chu kỳ.
Δ6 theo regime: 2022 = +1,8; 2024-26 = +0,225 (median 2 tín hiệu −0,05 và +0,5). **N_regime = 2 < 3** ⇒ luật PREREG §6
(đòi N≥3) **không thoả** ⇒ **KHÔNG KẾT LUẬN**. Tức nhãn "ủng hộ biên" của vòng 1 chỉ sống nhờ đếm 1 chu kỳ thành 2.

### D. Nhãn cuối: **KHÔNG KẾT LUẬN / INCONCLUSIVE**
(Cơ học PREREG §6 vẫn ra "ủng hộ biên" ở N=3 episode; skeptic không chấp nhận mạnh hơn và A–C ủng hộ phán quyết đó.)
Không có bằng chứng spread dẫn lãi huy động ở độ trễ nào, cũng không ở điều kiện theo mức. Không đề xuất wire/gate/sizing;
D1 giữ DISPLAY-ONLY, không nêu "đáng theo dõi" cho mức hiện tại.

### E. Ghi chú quy trình & ERRATA (không sửa PREREG.md đã khoá)
- **PREREG commit `ce1778bb6` đã dùng `--no-verify`** (bỏ qua pre-commit hook). Nội dung PREREG không bị đổi sau đó (md5 giữ `2098a999…`).
- **ERRATA mốc giờ PREREG:36**: ghi "kéo ~01:3x ICT"; giờ đúng là **01:23 ICT** (2026-11-05). Không ảnh hưởng số liệu (snapshot khoá bằng md5 `fb65e9bf…`).
- **ERRATA "6/6"** ở đầu REPORT bản trước: số check PASS thực tế của `selfcheck.sh` lúc đó là **5** (không phải 6); nay là **7** (thêm 2 check cho `analysis_r2.py`).

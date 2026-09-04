# DT5G mở rộng về 2008 — RESEARCH SERIES (job Taylor_20260904_114556)

**Verdict: USABLE-WITH-CAVEATS cho CRISIS/BEAR-conditional research; NOT-USEFUL cho mục tiêu
gốc (tăng N_eff phía BULL) — xem §5.**

## 0. Ràng buộc đã tuân thủ
- Không đụng production: không ghi `vnindex_5state_dt5g_live`, không sửa `macro_state_live.py`,
  không đụng crontab/`golive_state_today.json`. Toàn bộ output nằm trong
  `mike/agents/Taylor/research/dt5g_ext_2008_20260904/` (local CSV) + 1 file registry.
- Không re-tune: gọi `get_macro_state()` nguyên hàm, nguyên tham số `P{}` production
  (`macro_state_live.py:44-52`), chỉ đổi `start='2008-01-01'`.
- Gate byte-identical chạy TRƯỚC khi phân tích 2008-2013, PASS mới đi tiếp (đúng yêu cầu).

## 1. Verify 4 nguồn (tự đo lại, không copy số của Mike)
| Nguồn | Mike nêu | Đo lại thật (2026-09-04) | Khớp? |
|---|---|---|---|
| `vnindex_5state_tam_quan_v34b_clean` | 2000-07-28→2026-06-15 | **2000-07-28→2026-09-04, 6.356 phiên** | Khớp hướng, mtime mới hơn (bình thường) |
| `tav2_mike.universe_pit` từ 2006, 2008≈243 mã | — | **min(time)=2000-07-28**; 2008 = **204 mã distinct/năm** (đếm theo năm, không phải PIT/ngày) | Lệch số nhưng cùng kết luận: >> `breadth_min_univ=100` |
| `us_market_history.csv` | 2000-01-03→2026-05-20 | **2000-01-03→2026-09-03**, 6.709 dòng | Khớp hướng, mới hơn |
| `SBV_REFI_EVENTS` | 34 mốc từ 2006, 23 trước 2014 | **Đếm tay: đúng 34 mốc, đúng 23 mốc <2014-01-01** | Khớp chính xác — **nhưng file tự ghi rõ 23 mốc này là "CONTEXTUAL", tác giả khuyến nghị backtest chỉ dùng 2011+, một số mốc pre-2011 sai lệch ngày ±1-2 tháng** (đọc trực tiếp trong `sbv_macro_overlay.py:59-61`, không phải suy diễn) |

Kết luận: 4 nguồn đều thật, có dữ liệu. Nhưng nguồn quan trọng nhất cho Pillar A
(SBV events) tự flag chất lượng thấp trước 2011 — không nằm trong danh sách "đã xác minh" của
Mike, phát hiện thêm ở lượt verify này.

## 2. Bẫy vận hành phát hiện được (mới, không có trong brief)
**`BQ_LOCAL_CACHE=data/bq_cache` được export sẵn trong `wc_env.sh`** (kế thừa mọi phiên đã
source nó — kể cả phiên headless này). Chạy `get_macro_state(start='2008-01-01', ...)` lần đầu
dưới biến này:
- Trả về series bắt đầu **2013-01-02**, KHÔNG PHẢI 2008 — cache DuckDB cắt cụt lịch sử âm thầm,
  chỉ có 1 dòng cảnh báo phụ ("breadth guard inactive") chứ không báo lỗi rõ ràng về việc cắt
  lịch sử.
- Cache thiếu bảng `universe_pit` (chỉ có `universe_pit_q`) → breadth guard tự tắt, rơi vào
  fail-safe (US cap không bị suppress) — đúng hướng AN TOÀN theo thiết kế, nhưng nghĩa là chạy
  dưới cache **không hề dùng breadth thật**, khác hẳn ý định nghiên cứu.

Sửa: `env -u BQ_LOCAL_CACHE` khi gọi `get_macro_state`/`simulate_holistic_nav.bq()` cho việc cần
lịch sử pre-2014. Sau khi fix: series đúng 2008-01-02→2026-09-03, 4.656 phiên, không lỗi.
Đã ghi caveat này vào `kb/data_registry/market-state/dt5g_ext_2008_research.md` §1 để agent
sau không lặp lại.

## 3. Gate byte-identical — PASS
So `state` của 3.158 phiên chồng lấn (2014-01-02→2026-09-03) giữa chuỗi mở rộng và
`tav2_bq.vnindex_5state_dt5g_live`: **0 phiên lệch.** (1 dòng chênh row-count chỉ vì
`vnindex_5state_dt5g_live` có thêm phiên 2026-09-04 mà tôi giới hạn END=2026-09-03.)
Script: `gate_check.py`. **Extension không phá production.**

## 4. Chuỗi 2008-2013 — episode + đối chiếu lịch sử

| Đợt | Khoảng | Số phiên | Macro cap? | avg (Close/MA200−1) | Đối chiếu lịch sử |
|---|---|---:|---|---:|---|
| CRISIS | 2008-01-02→07-11 | 127 | một phần (cap∈{2,3}) | −36,0% | Đúng — crash trước GFC, tạo bong bóng 2007 xì hơi |
| BEAR | 2008-07-14→07-25 | 10 | cap=3 | −35,7% | transition ngắn |
| CRISIS | 2008-07-28→2009-06-01 | 211 | **94,8% cap=CRISIS(1)** | −23,2% | **Đúng — Lehman + đáy VNINDEX ~235 (24/02/2009), macro cap bắt đúng** |
| NEUTRAL | 2009-06-02→12-04 | 133 | không | +36,3% | Hồi phục 2009 H2 (giá tăng mạnh) nhưng base KHÔNG lên BULL/EXBULL — đặc tính DT4-base, không phải lỗi overlay |
| CRISIS | 2009-12-07→2010-01-11 | 25 | 72% cap=NEUTRAL(3, không hạ xuống CRISIS) | **+4,0%** | **Nghi vấn — giá TRÊN MA200, nhãn CRISIS 100% từ base, cap không giải thích được** |
| NEUTRAL | 2010-01-12→08-11 | 144 | — | −1,0% | — |
| BEAR | 2010-08-12→09-17 | 25 | — | −10,1% | plausible |
| NEUTRAL | 2010-09-20→2011-03-03 | 112 | — | −3,6% | — |
| CRISIS | 2011-03-04→11-18 | 181 | **100% cap=CRISIS(1)** | −5,8% | **Đúng — lạm phát cao, SBV refi hiking 11%→15% (2011-02→10), macro cap bắt đúng, sớm hơn giá** |
| BEAR | 2011-11-21→2012-02-07 | 51 | 100% cap=BEAR(cap≠9) | −12,7% | đáy 2011-2012 |
| NEUTRAL | 2012-02-08→04-18 | 50 | 68% cap=NEUTRAL | +6,6% | — |
| CRISIS | 2012-04-19→10-04 | 118 | **0% (cap=9 toàn bộ)** | +1,9% | Vụ Bầu Kiên (08/2012) có thật, nhưng nhãn 100% từ base, không phải overlay; MA200 lúc này thấp (kế thừa đáy 2011) nên +1,9% không đủ phản bác |
| NEUTRAL | 2012-10-05→2013-03-26 | 116 | 0% | +2,3% | — |
| CRISIS | 2013-03-27→08-22 | 103 | **0% (cap=9 toàn bộ)** | **+12,4%** | **SAI — verify trực tiếp giá VNINDEX: Close 462-528, MA200 417-453, đi ngang/tăng nhẹ suốt cả đợt, KHÔNG có drawdown thật. Đây là outlier duy nhất trong toàn bộ 15 đợt 2008-2013 (mọi đợt CRISIS/BEAR khác đều ≤+6,6%, phần lớn âm) — lỗi cụ thể của bảng BASE v3.4b pre-2014, không liên quan overlay (cap=9 suốt)** |
| NEUTRAL | 2013-08-23→12-31 | 92 | 0% | +2,2% | — |

**Mật độ transition**: 2008-2013 = 2,36 lần/năm-tương-đương (14 chuyển đổi / 1.498 phiên); 2014+
= 4,07 lần/năm-tương-đương (51/3.158). 2008-2013 **THƯA hơn**, không dày bất thường — không có
dấu hiệu tham số "quá nhạy" ở chế độ khủng hoảng cấu trúc; nếu có vấn đề thì là NHÃN SAI cụ thể
(§ trên), không phải nhiễu do tham số.

## 5. Đánh giá thẳng — có nên dùng không

**Điều overlay MỚI (Pillar A domestic + Pillar B US panic, phần mở rộng thật sự của việc này)
hoạt động đúng và khớp lịch sử ở CHÍNH XÁC 2 cửa sổ**: GFC 2008-07→2009-06 và lạm phát
2011-03→2011-11 — cả hai macro cap tự bắn 95-100% thời gian, đúng tinh thần "leading indicator"
DT5G được thiết kế cho. Đây là phần **dùng được, tin được**.

**Toàn bộ nhãn CRISIS/BEAR khác trong 2008-2013 (4/6 đợt CRISIS, cả 3 đợt BEAR không rơi vào 2
cửa sổ trên) đến 100% từ bảng BASE `vnindex_5state_tam_quan_v34b_clean`** — thuật toán v3.4b
tính lại xa hơn 2014 mà KHÔNG có ai kiểm chứng chất lượng trong giai đoạn đó trước lượt này. Đã
tìm thấy **ít nhất 1 lỗi cụ thể xác nhận bằng giá thật** (đợt 2013-03→08, giá cao hơn MA200 12,4%
mà bị gắn nhãn CRISIS) — không phải suy đoán, có số đo trực tiếp từ BQ.

**Về mục tiêu GỐC (N_eff phía BULL cho nghiên cứu như cash-dividend-theo-regime-BULL): chuỗi
2008-2013 KHÔNG giúp được gì — 0 đợt BULL, 0 đợt EXBULL trong toàn bộ 6 năm mở rộng.** VN thị
trường giai đoạn này chưa từng đạt điều kiện DT4-gate cho BULL (25 phiên NEUTRAL+ liên tục với
đà giá đủ mạnh). Nếu mục đích ban đầu là giải quyết vấn đề "BULL N_eff quá nhỏ" (case cash-
dividend hôm nay), **việc mở rộng này không đóng góp gì cho trục đó**.

**Về phía CRISIS/BEAR**: N_eff tăng có điều kiện — nếu chỉ tính 2 đợt đã xác nhận
lịch sử (2008-2009, 2011), CRISIS episode-độc-lập tăng từ 9 (2014+) lên 11 (+22%), khiêm tốn.
Nếu tính cả 4 đợt base-driven chưa kiểm chứng (rủi ro, đã biết ≥1 lỗi), tăng lên 15 (+67%) —
nhưng đây là đánh đổi lấy rủi ro nhãn sai đã CHỨNG MINH tồn tại.

Về universe/breadth pre-2008: CLAUDE.md ghi "tín hiệu breadth có nghĩa từ ~2008" — đo lại
2008 = 204 mã distinct/năm, trên ngưỡng kỹ thuật (`breadth_min_univ=100`) nhưng thanh khoản tập
trung ở đuôi hẹp theo cảnh báo sẵn có trong CLAUDE.md, KHÔNG kiểm chứng thêm ở lượt này (ngoài
phạm vi ràng buộc thời gian của job).

## 6. Khuyến nghị dùng cụ thể
- **Nghiên cứu conditional-theo-CRISIS/BEAR dùng chuỗi 2008-2013**: chỉ dùng 2 cửa sổ macro-cap-
  xác nhận (2008-07-28→2009-06-01, 2011-03-04→2011-11-18) làm ground-truth bổ sung. KHÔNG dùng
  4 đợt CRISIS/BEAR base-driven còn lại làm nhãn regime tin cậy cho tới khi ai đó audit riêng
  bảng `vnindex_5state_tam_quan_v34b_clean` giai đoạn 2008-2013 (ngoài phạm vi job này).
- **Nghiên cứu conditional-theo-BULL/EXBULL**: extension này KHÔNG giúp — vẫn nghẽn ở N_eff cũ
  (8-10 đợt từ 2014+). Cần hướng khác (không phải mở rộng lịch sử) nếu muốn giải quyết case
  cash-dividend BULL.
- KHÔNG đề xuất wire production — đúng phạm vi brief.

## Artifacts
- `dt5g_ext_2008_full.csv` — chuỗi đầy đủ 2008-01-02→2026-09-03 (4.656 phiên).
- `episodes_pre2014.csv` — 15 đợt 2008-2013 (label, start, end, n_sessions).
- `run_extended.py`, `gate_check.py`, `analyze.py` — tái lập được (nhớ `env -u BQ_LOCAL_CACHE`).
- Registry: `mike/kb/data_registry/market-state/dt5g_ext_2008_research.md`.

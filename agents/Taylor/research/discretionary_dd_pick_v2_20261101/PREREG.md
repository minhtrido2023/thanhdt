# PREREG — Funnel 8L v2: quy tắc CHỌN mã DD + DD 2 tầng (ghi TRƯỚC khi chạy trên dữ liệu thật)

Job `Taylor_20261101_130719` · user duyệt 2026-11-01 20:05 ICT · ghi lúc 2026-11-01 ~20:30 ICT, TRƯỚC
lần chạy đầu tiên của bộ chọn trên `data/rating_8l.csv`. Mọi tham số dưới đây KHOÁ cho tới mốc đo
**2027-04-06**; đổi = bản PREREG mới (md5 mới), không sửa file này.

## 1. Vũ trụ (pool) — loại trừ trước khi xếp hạng
Vũ trụ chất lượng của funnel hiện hành (`build_lanes`): rating ≤ 3 ∧ golden floor (ROE_Min3Y≥0 ∧
CF_OA_3Y>0) ∧ `redflag` rỗng ∧ liq_bn ≥ 0,3. Loại tiếp:
- BANNED, forensic exclude có hiệu lực, cờ insider bán 90 ngày (`load_exclusions`, như funnel);
- mã ĐANG GIỮ ở SpaceX/ZaloPay (`data/execution_logs/active_nav_*.json` positions qty>0) và
  `excluded_tickers` của 2 file đó;
- mã đã được ĐỀ XUẤT DD (picked) hoặc đã DD (claim trong sổ DD hoặc thư mục
  `agents/Taylor/research/dd_<MÃ>_<YYYYMMDD>`) trong **90 ngày lịch** gần nhất (DD lại sớm = tốn tiền
  mà không có thông tin mới).

## 2. Điểm (mỗi cấu phần ∈ [0,1], xếp hạng phân vị TRONG pool của ngày đó)
| Cấu phần | Trọng số | Định nghĩa |
|---|---|---|
| V — tiềm năng so với giá | **0,50** | MoS DCF = (FV−giá)/FV, `dcf_valuation.fair_value` khung domestic_v2 (mặc định hiện hành), giá = `Price` chưa điều chỉnh phiên asof (cache `data/bq_cache/ticker`), `price_date`=asof. Phân vị MoS trong các mã DCF tính được. Mã DCF KHÔNG tính được (ngân hàng/CTCK/bảo hiểm, FCFE≤0) ⇒ dùng phân vị earn_yield TRONG cùng route × **0,8** (proxy, gắn nhãn `dcf_na`). |
| E — BCTC quý vừa ra | **0,30** | Chỉ khi quý mới nhất (cùng quy tắc PIT của làn C: Release_Date, trống ⇒ time, < asof CHẶT) có ngày biết trong **45 ngày lịch** trước asof; ngoài cửa sổ E=0. E = phân vị YoY NP (NP_P0/NP_P4−1, NP_P4>0) trong các mã "vừa ra" × hệ số chất lượng q. q = 1 nếu cfo_np ≥ 0,5; 0,6 nếu 0 ≤ cfo_np < 0,5 hoặc cfo_np thiếu; 0,3 nếu cfo_np < 0. **Nền thấp/lãi một lần** (YoY > 300%, hoặc NP_P4 ≤ 0 mà NP_P0 > 0) ⇒ q = 0,3 + nhãn `nen_thap`. Lý do: LAG đã khai thác PEAD cơ học; DD chỉ thêm giá trị khi lợi nhuận đủ CHẤT để đứng được — không thưởng cú nhảy kế toán. |
| R — rating 8L | **0,20** | rating 1 ⇒ 1,0; 2 ⇒ 0,67; 3 ⇒ 0,33. |
| Làn A (lệch giá) | 0 | chỉ là nhãn nền (user 2026-11-01: fear-buy không còn là ưu tiên). |

score = 0,50·V + 0,30·E + 0,20·R. Hoà điểm ⇒ MoS cao hơn, rồi ticker.
Lý do trọng số: V lớn nhất vì user chốt "ưu tiên = tiềm năng so với giá"; E thứ hai vì mùa BCTC là
lúc thông tin mới nhất; R nhỏ vì đã là cổng ≤3 (thông tin trùng với golden floor). KHÔNG tối ưu trên
lịch sử (không có lịch sử PIT đủ dài để tối ưu — xem §6).

## 3. Nhật ký chọn (append-only, PIT)
`data/discretionary_pick_log.csv`: mỗi asof ghi **top-8** (K=8 ≥ 5) theo score, KỂ CẢ mã không chọn,
cột: asof, rank, ticker, route, rating, score, V, E, R, mos, dcf_ok, fv_ps, price, release_date,
g_yoy, cfo_np, q, labels, lanes, season, picked, escalate_full, reason, logged_at. Cùng asof đã có ⇒
KHÔNG ghi lại (chạy lại không nhân bản, không ghi đè quá khứ). Snapshot rating PIT đã có sẵn ở
`data/rating_8l_daily/`.

## 4. Cổng tần suất (cơ học, fail-closed)
Mùa BCTC = đúng cổng `fa_ratings_earnings_window_daily.sh --check <asof>` (RUN = mùa). Không gọi
được / output lạ ⇒ coi là NGOÀI mùa (chặt hơn).
| | Đề xuất DD tầng nhẹ (pick) | DD đầy đủ (claim `--tier full`) |
|---|---|---|
| Mùa | 1/phiên (1 pick mỗi asof) | 1/ngày |
| Ngoài mùa | 1/tuần ISO (T2-CN) | **2/tuần ISO** (trần cứng) |
Sổ claim `data/discretionary_dd_ledger.jsonl` (append-only). Đọc hỏng ⇒ TỪ CHỐI claim (rc=2) và
khối 08:00 in "suất DD: KHÔNG XÁC ĐỊNH (sổ hỏng)".

## 5. Ngưỡng lên DD đầy đủ (tầng nhẹ → tầng đầy đủ)
Mã được pick có `escalate_full = True` khi CẢ HAI:
1. DCF tính được ∧ **MoS ≥ 25%** ∧ `robust` (MoS giữ dấu ở cả 4 điểm hộp nhạy cảm, `classify_dcf`);
2. không mang nhãn `nen_thap`.
Mã DCF-NA (tài chính) KHÔNG tự lên tầng đầy đủ từ cơ học — tầng nhẹ phải tự kết luận (Gordon-P/B)
rồi Mike quyết. Tầng nhẹ (LLM, do Mike dispatch) vẫn có quyền HẠ (tin xấu/pháp lý/insider) trước khi
lên tầng đầy đủ. Lý do 25%: DD 4 mã 01/11 (FPT/HHS/SIP/TV2) cho vùng định giá rộng ±20-30% quanh
tâm ⇒ MoS < 25% nằm trong sai số mô hình; robust bắt buộc vì một điểm MoS đơn lẻ không đủ.

## 6. Đo (mốc 2027-04-06) — giả thuyết và luật quyết
- H1 (mô tả, không suy diễn): forward excess 3M/6M của mã picked so với TRUNG VỊ các mã rank 2-8
  cùng asof (cùng pool, cùng ngày ⇒ khử thị trường). Trả lời "quy tắc chọn có hơn ứng viên bị bỏ không".
- N độc lập: tối đa ~1 pick/phiên trong mùa (~40 phiên mùa Q3+Q4 tới 04/2027) + ~1/tuần ngoài mùa
  ⇒ **N ≈ 40-60 pick** (ước lượng), chồng lấn forward 3M ⇒ N hiệu dụng thấp hơn nhiều. ⇒ mốc 2027-04-06
  chỉ đủ **mô tả + futility**: nếu trung vị (picked − rank2-8) 3M < 0 VÀ CI95 bootstrap theo khối tuần
  hoàn toàn < 0 ⇒ bỏ trọng số này, quay về xếp V thuần. Không có luật "giữ vì dương".
- Không re-tune giữa chừng.

## Bổ sung vòng 2 (arch-review, 2026-11-01 — KHÔNG đổi tham số §1-5)
- Ngày lễ nằm trong mùa BCTC được coi là NGOÀI mùa (cổng `fa_ratings_earnings_window_daily.sh --check`
  trả SKIP) ⇒ áp trần ngoài mùa (light 1/tuần, full 2/tuần); chặt hơn, chủ ý.
- Ngưỡng MoS≥25% gần như không lọc (RESULTS.md) ⇒ dòng khối 08:00 mang nhãn cố định "xếp việc DD, KHÔNG
  phải tín hiệu mua"; mã chọn chỉ là THỨ TỰ làm việc DD.

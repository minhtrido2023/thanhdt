# extreme_bottom_recognition_20260823 — "Nhận diện đáy cực đoan kiểu 11/2022" (Q1–Q4)

Job `Taylor_20260823_083709`. **Nhánh MÔ TẢ chạy TRƯỚC Phase 1** của
`plan_margin_valuation_spread_20260823.md`. **KHÔNG chạy episode-sim (Phase 1 bước 2), KHÔNG tối ưu
tham số, KHÔNG chạm production.** Mọi chỉ báo point-in-time (percentile expanding, tối thiểu 750
phiên lịch sử; không có percentile full-sample ở bất kỳ đâu).

| File | Nội dung |
|---|---|
| `q_daily.sql` / `_daily_breadth.csv` | 4.897 phiên 2007-01→2026-08: breadth PIT trên `tav2_mike.universe_pit` (%>MA200, %chạm đáy 52w, %sụt ≥35/50% từ đỉnh 52w của CHÍNH nó), PE/PB median, giá trị giao dịch |
| `_vni_daily.csv` | VNINDEX daily (Close, Volume, RSI) 2005-06→ |
| `build_episodes.py` → `daily_panel.csv`, `episodes_dd52.csv` | **Q2** — 7 episode `dd52<=-20%` (đúng định nghĩa cổng `capit_margin_lever` đang LIVE), so ngày ARM vs ĐÁY THẬT |
| `q1_signal_test.py` → `q1_signal_summary.csv`, `q1_lead_lag.csv` | **Q1** — 9 tín hiệu PIT: forward-12m theo EPISODE + LOO + độ trễ so với đáy thật |
| `q1b_daily_spread.py` → `daily_panel_spread.csv` | **Q1b** — dựng lại spread EY(median)−lãi vay ở độ phân giải NGÀY (Phase 0 chỉ đo THÁNG) |
| `q4_tranche_ladder.py` | **Q4** — thang tranche theo độ sâu dd52, kèm MAE 12 tháng |
| `q3_incremental.py`, `q3b_sensitivity.py` | **Q3** — spread có THÊM gì so với dd52; độ nhạy với giả định `margin = deposit + Xpp`; block-bootstrap |
| `q_trough_stock.sql` / `trough_stock_forward.csv` | forward 12/24m ở cấp **cổ phiếu** tại từng đáy (kiểm mệnh đề "gấp đôi sau 1 năm") |

## Q2 — 7 episode `dd52<=-20%`, khoảng cách ARM → ĐÁY THẬT

| Episode | Arm | Đáy thật | Trễ (ngày) | VNI arm→đáy | MaxDD từ đỉnh | fwd12 từ arm | fwd12 từ đáy | med12 **cổ phiếu** từ đáy | % mã **gấp đôi** ≤12m |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2007-04 | 2007-04-23 | **2009-02-24** | **673** | −74,7% | −79,9% | −44,2% | **+110,7%** | **+130,0%** | **66,4%** |
| 2009-11 | 2009-11-26 | 2010-08-25 | 272 | −12,2% | −63,8% | −8,9% | −2,5% | **−46,8%** | 0,3% |
| 2011-05 | 2011-05-23 | 2012-01-06 | 228 | −19,4% | −71,2% | +7,2% | +28,9% | +21,2% | 4,3% |
| 2012-08 | 2012-08-27 | 2012-11-02 | 67 | −2,8% | −67,9% | +22,6% | +33,2% | +26,3% | 9,2% |
| 2018-05 | 2018-05-28 | 2019-01-03 | 220 | −5,8% | −27,1% | +4,3% | +9,9% | +0,8% | 5,0% |
| 2020-03 | 2020-03-11 | 2020-03-24 | **13** | −18,8% | −45,3% | +44,2% | **+79,5%** | **+96,7%** | **47,9%** |
| 2022-05 | 2022-05-13 | **2022-11-15** | 186 | −22,9% | −40,3% | −9,9% | +23,1% | **+42,4%** | 18,1% |

**Ba đính chính bắt buộc phải mang theo:**
1. **`fwd12 từ đáy > fwd12 từ arm` ở 7/7 episode là TAUTOLOGY**, không phải bằng chứng — đáy được
   *định nghĩa* là điểm thấp nhất. Chỉ dùng cột này để đo **cái giá của việc vào sớm**, không bao giờ
   dùng làm bằng chứng rằng tín hiệu nào đó "hoạt động".
2. **Mệnh đề "lợi nhuận gấp đôi sau 1 năm" là SAI ở cấp chỉ số cho 11/2022**: VNINDEX từ 911,90
   (2022-11-15) sau 12 tháng = 1.122,50 → **+23,1%** (đỉnh trong 12 tháng đó +36,6%; sau 24 tháng
   +33,6%). Ở **cấp cổ phiếu** thì user nhớ đúng HƯỚNG nhưng quá 2,4 lần về ĐỘ LỚN: median mã trong
   universe +42,4%, và **18,1%** số mã gấp đôi. Chỉ **2/7** đáy thật sự cho "median mã gấp đôi":
   2009-02 (+130,0%) và 2020-03 (+96,7%). *Số cấp cổ phiếu là CẬN TRÊN* — `tav2_bq.ticker` xoá sạch
   mã huỷ niêm yết (0 dòng FLC), nên mẫu sống sót bị thiên vị lên.
3. **2010-08-25 là phản ví dụ chí mạng**: một "đáy" của episode `dd52<=-20%`, nhưng median mã sau
   12 tháng **−46,8%**. Đáy của một episode KHÔNG đồng nghĩa đáy của thị trường.

## Q1 — Có phân biệt được 09/2022 (còn giảm tiếp) với 11/2022 (gần kiệt bán) không?

**CÓ, và khoảng cách rất lớn** (mọi số PIT, tính bằng dữ liệu ≤ ngày đó):

| Chỉ báo PIT | 2022-05-13 (arm) | **2022-09-28** | 2022-10-25 | **2022-11-15 (đáy)** |
|---|---:|---:|---:|---:|
| dd52 | −22,6% | −25,2% | −34,7% | **−40,3%** |
| PE median — **percentile PIT expanding** | 0,830 | **0,802** | 0,358 | **0,155** |
| PB median | 1,21 | 1,15 | 0,88 | **0,66** |
| % universe sụt ≥50% từ đỉnh 52w của chính nó | 40,5% | 47,1% | 63,8% | **75,9%** |
| % universe trên MA200 | 13,9% | 10,1% | 7,0% | **3,7%** |
| EY(median) − lãi vay *(daily)* | −2,39pp | −2,10pp | +0,44pp | **+2,04pp** |

⇒ **09/2022 KHÔNG hề rẻ**: PE median nằm ở **percentile PIT 0,80** — tức đắt hơn 80% lịch sử của
chính nó. Cổng `dd52` bắt được "khủng hoảng đang diễn ra" nhưng **mù hoàn toàn với định giá**, và đó
đúng là lý do nó arm ở một điểm còn đắt.

**NHƯNG tín hiệu này KHÔNG định thời điểm được.** Bảng lead-lag (`q1_lead_lag.csv`, số âm = fire
TRƯỚC đáy thật bao nhiêu ngày):

| Tín hiệu | 2007 | 2009 | 2011 | 2012 | 2018 | 2020 | 2022 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `pe_pit<=0,20` | không fire | **+55 (SAU đáy)** | −228 | 0 | không fire | −5 | −1 |
| `pct_dd50>=0,50` | −407 | +79 | −228 | không fire | không fire | không fire | −148 |
| `pct_ma200<=0,10` | −406 | +63 | −228 | không fire | không fire | −1 | −127 |

Không tín hiệu nào có độ trễ ổn định: cùng một luật fire **1 ngày trước đáy** ở 2022 và **55 ngày
SAU đáy** ở 2009, hoặc **407 ngày trước** ở 2007. `pct_52wlow` chạm 59,0% đúng ngày 2022-11-15 rồi
rơi về 3,3% ngay hôm sau — một cú nhọn 1 phiên, không phải trạng thái giao dịch được.

## Q3 — N độc lập thật, và spread có THÊM gì so với `dd52` không?

Đo ở cấp **khối độc lập** (cách nhau >90 ngày lịch), KHÔNG phải cấp ngày. Chi phí vay trong bảng này = **12,5%/năm cố định** (lãi RocketX thật của SpaceX hôm nay); bảng độ nhạy
ngay dưới dùng `margin_rate` biến thiên theo thời gian (`deposit + Xpp`) nên các con số net lệch 1–2pp — hai
bảng KHÔNG được đọc lẫn.

| Luật | N khối | fwd12 median-của-khối | **net sau lãi vay** | % khối > chi phí | LOO net | P(block-bootstrap) |
|---|---:|---:|---:|---:|---|---:|
| (1) `dd52<=-20%` — **ĐANG LIVE** | 7 | +9,4% | **−3,1%** | 43% | [−5,0%, +1,4%] | 0,10 |
| (2) armed & spread≥0 | 7 | +17,5% | +5,0% | 71% | [+3,8%, +12,3%] | 0,89 |
| (3) armed & spread<0 | 8 | +8,2% | −4,3% | 38% | [−5,3%, −3,4%] | — |
| (5) `dd52<=-35%` — **V8a** | 4 | +25,0% | +12,5% | 100% | [+7,1%, +17,9%] | 1,00 *(vô nghĩa ở N=4)* |
| (6) `dd52<=-35%` & spread≥0 — V8b | 5 | +30,4% | +17,9% | 100% | [+11,4%, +36,4%] | 1,00 *(vô nghĩa)* |
| (7) spread≥0, bất kể dd52 — V8c | 10 | +23,0% | +10,5% | 80% | [+5,3%, +15,7%] | 0,97 |

**Hai điều đáng chú ý nhất:**
- `corr(dd52, spread)` trên ngày armed = **+0,020** — hai trục gần như **trực giao hoàn toàn**. Đây
  là lập luận mạnh nhất cho việc spread mang thông tin THÊM (không phải tìm lại cùng các sự kiện).
- Cổng `dd52<=-20%` **một mình, đo ở tầng chỉ số, KHÔNG đủ trả lãi vay**: net −3,1%, chỉ 43% số khối
  vượt chi phí. Điều này KHÔNG mâu thuẫn với `capit_margin_lever` đang LIVE (edge của nó đến từ
  **rổ CAPIT ở tầng engine**, không phải chỉ số) — nhưng nó có nghĩa: **không được lấy nghiên cứu
  tầng chỉ số này để biện minh cho việc nới đòn bẩy ra ngoài kênh CAPIT.**

### ⛔ Điểm phá hỏng: kết quả KHÔNG BỀN với giả định lãi vay

`margin = deposit + Xpp` là **giả định** (Phase 0 đã ghi: mắt xích yếu nhất). Đổi X:

| X | N khối (V8c) | net | % khối | P(boot) |
|---:|---:|---:|---:|---:|
| +3,0pp | 9 | **+0,0%** | 56% | 0,64 |
| +4,0pp | 11 | **+0,2%** | 55% | 0,62 |
| **+5,0pp** *(giả định Phase 0)* | 10 | **+10,0%** | 80% | 0,97 |
| +6,0pp | 8 | +11,4% | 75% | 0,92 |
| +7,0pp | 6 | +12,6% | 100% | 1,00 |

Đổi X từ +4 sang +5 làm net nhảy từ **+0,2% → +10,0%**. Mở từng khối ra (in trong log
`q3b_sensitivity.py`) thì thấy phần lớn cú nhảy **KHÔNG phải kinh tế mà là artefact của luật gộp
khối 90 ngày**: ở X=+4, hai giai đoạn tốt 2013-08 (+31,6%) và 2016-10 (+42,5%) bị **gộp** vào một
khối 478 phiên 2015-02→2017-05 (+19,0%), đồng thời hai khối xấu 2018-07 (−3,8pp) và 2014-05
(1 phiên!) được thêm vào. Tức **chính "N độc lập" cũng phụ thuộc ngưỡng** — thống kê tự nó không ổn định.

**N ĐỘC LẬP THẬT:** 7 episode dd52; chỉ **4** chạm −35%; và số đáy **thật sự cùng loại với 11/2022**
(MaxDD ≥40% + median mã hồi ≥+40% trong 12 tháng) chỉ có **3**: 2009-02, 2020-03, 2022-11. Đó là
mẫu để trả lời một câu hỏi mà user đang hỏi bằng ký ức về **một** lần.

## Q4 — Verdict

**NO-GO** cho bất kỳ "luật định thời điểm đáy": không tín hiệu PIT nào có độ trễ ổn định (Q1),
N độc lập thật là 3 (Q3), và tiền đề của câu hỏi ("gấp đôi sau 1 năm") sai ở cấp chỉ số (Q2).
Đúng cảnh báo `v2.5-leverage-nogo.md`: tối ưu trên N=1–3 episode.

**GO CÓ ĐIỀU KIỆN** cho **đúng MỘT** biến thể bổ sung, xin user duyệt nâng `N_trials` 7 → 8:

> **V8 — TRANCHE THEO ĐỘ SÂU (không phải theo định giá).** Khi đã arm bởi V0 (`dd52<=-20%`), mở
> tranche thứ hai khi `dd52<=-35%`. **Không thêm tham số tự do nào ngoài một ngưỡng**, không cần
> dữ liệu định giá, không cần giả định lãi vay.
> Cơ sở: thang **đơn điệu** theo độ sâu, đo theo episode — T1 (−20..−27,5%) +1,1% · T2 (−27,5..−35%)
> +10,1% · T3 (−35..−45%) +22,4%. MAE 12 tháng cũng cải thiện: median episode −5,1% (arm −20%) →
> **−0,9%** (−35%).

**Rủi ro overfit tôi tự đánh giá — 4 điểm, không giấu điểm nào:**
1. **N_ep = 4** cho V8. `P(boot)=1,00` là **giả** (4/4 dương ⇒ bootstrap bắt buộc ra 1,00), KHÔNG
   được trích như bằng chứng. LOO net thấp nhất +7,1pp — đó mới là con số đáng đọc.
2. **2007-08 GFC bác thẳng luận điểm "sâu hơn thì an toàn hơn"**: ở dải T3 (−35..−45%) forward-12m
   của 2007 là **−60,7%**, và MAE sau khi `dd52<=-35%` fire là **−67,2%**. Với f=1,3 đó là vùng
   call margin. ⇒ V8 phải là tranche **KÍCH THƯỚC** (deploy thêm vốn tự có), **KHÔNG** được là
   tranche **ĐÒN BẨY** (tăng f) nếu chưa có tỷ lệ ký quỹ duy trì thật (đang chờ Mafee).
3. **KHÔNG đề xuất V8b** (`dd52<=-35%` & spread≥0) dù nó đẹp nhất bảng (+17,9pp, 100%): N=5, dựa
   trên giả định lãi vay đã chứng minh là không bền, và "đẹp nhất trong 9 luật đã thử" chính là
   chữ ký của overfit.
4. **N_trials của nhánh này**: 9 tín hiệu × 2–3 ngưỡng + 5 mức X ≈ **~30 cell mô tả**. Cộng dồn chủ
   đề margin (~180+ trước đó) ⇒ đây là **vòng thứ 5** trên cùng một tập episode. Không có cell nào
   ở đây đạt ngưỡng DSR/P≥0,95 của fleet ngoại trừ V8c (0,97) — mà V8c thì rơi về 0,62 khi X=+4.

## Đóng góp phương pháp cho Phase 1 (độc lập với verdict trên)

**Phase 0 đo spread ở độ phân giải THÁNG và vì thế bỏ sót 2022 hoàn toàn.** Đo lại ở độ phân giải
NGÀY: `EY(median) ≥ lãi vay` có một episode **2022-10-24 → 2022-11-25 (25 phiên, spread đỉnh
+2,04pp)** mà bản tháng không thấy — vì cuối tháng 11/2022 chỉ số đã hồi về ~1.050 nên spread cuối
tháng chỉ còn −1,03pp. Ở cấp ngày, spread≥0 đúng tại **5/7** đáy thật (2009-02 +5,92 · 2012-01
+3,82 · 2012-11 +3,05 · 2020-03 +2,69 · 2022-11 +2,04); hai ca trượt đều sát mép (2010-08 −0,72 ·
2019-01 −0,19). ⇒ **Phase 1 phải đo spread theo NGÀY, không theo THÁNG** — đây là lỗi đo, không phải
kết luận kinh tế, và nó sửa một dòng trong Phase 0 §2.2.

## Caveat kế thừa (không được bỏ khi trích bất kỳ số nào)
1. `deposit_rate_vn.py` neo hồi tố cùng một lần 2026-06-19 ⇒ **không PIT thật**.
2. `margin_rate = deposit + 5,0pp` là **giả định** — và §Q3 vừa chứng minh kết luận **nhạy** với nó.
3. Đây là **tầng proxy/overlay**, không phải tầng engine. Registry đã ghi 4 lần tín hiệu dương ở
   tầng proxy chết ở tầng engine (`FORCE_REAL_LEVER=1`: Calmar 1,54→1,31). Đây là lần thứ 5.
4. Số cấp cổ phiếu là **cận trên** (mã huỷ niêm yết bị xoá khỏi `tav2_bq.ticker`).

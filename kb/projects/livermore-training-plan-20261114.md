# Kế hoạch "huấn luyện" Livermore (đọc kỹ thuật VN) — 14/11/2026

Job `Taylor_20261114_061614` · chỉ LẬP KẾ HOẠCH, chưa chạy gì nặng, chưa sửa code production.
Trả lời yêu cầu user 14/11: Livermore chỉ hơn ngẫu nhiên một chút; cần (1) chọn thời điểm vào/ra deal
discretionary, (2) đọc trạng thái thị trường sớm hơn DT5G, (3) đặc biệt với mô hình PHÂN KỲ (RSI).

**Mục lục:** §1 Chẩn đoán · §2 "Huấn luyện" nghĩa là gì · §3 Đặc tả phân kỳ PREREG · §4 Cơ chế chấm điểm
· §5 Deal discretionary · §6 DT5G · §7 Lộ trình + chi phí · §8 Kill criteria · §9 Rủi ro & phản biện
· §10 Phân công · §11 User cần quyết.

---

## §1. Chẩn đoán — vì sao Livermore ≈ ngẫu nhiên

Bằng chứng đã có (đọc lại 3 artifact, không chạy lại):

| Thử | N | Hit | Brier | Baseline tốt nhất | Kết luận |
|---|---|---|---|---|---|
| Mù lịch sử 22/10 | 16 | 10 | 0,231 | "luôn UP" 11/16 | không hơn nền; 8/16 case agent NHẬN RA giai đoạn |
| 100 chuỗi cổ phiếu 05/11 | 100 | 55 | 0,2507 | mom20 50/100 | P(≥55\|đồng xu)=0,18; KHÔNG đạt PREREG |
| TA định lượng ±5% (06/11) | 72 trial | — | BSS −0,5% | ngẫu nhiên cùng lọc 43–46% | 0/72 ròng >0, DSR 0,00 |
| Đọc sống | 5 entry | 0 chấm | — | — | scoreboard trống, đáo hạn 18/11, 03/12, 10/12 |

**Đo thêm trong phiên này** (`livermore_results.csv` + `SEALED_truth.json`, N=100):
- `H20_P_UP` co cụm: trung bình 0,483, **sd 0,051**, min 0,36 max 0,60; **68/100 nằm trong [0,45; 0,55]**.
- Phân rã Brier: **resolution 0,0002** · reliability 0,0019 · uncertainty 0,2491 ⇒ BSS **−0,64%**.
  Bin p≈0,4 → thực tế UP 47%; bin 0,5 → 46%; bin 0,6 → 50%. Xác suất Livermore phát hành **không mang
  thông tin nào** về kết cục; toàn bộ "edge" 55/100 nằm ở dấu, và dấu lệch DOWN (60/100 call DOWN đúng 57%
  trong một mẫu có 53% case giảm).
- Hit theo năm đi theo thị trường: 2012 6/7, 2018 0/2, 2021 2/11, 2024 8/12 ⇒ phần thắng là beta năm,
  giống hệt kết luận ta-model-5pct.

Giả thuyết, tách riêng, kèm cách đo rẻ cho cái còn thiếu:

| # | Giả thuyết | Bằng chứng sẵn | Thiếu gì → đo rẻ thế nào |
|---|---|---|---|
| H1 | **Không có resolution**: agent né rủi ro, p luôn ~0,5 | resolution 0,0002 (đo trên) | đủ; không cần đo thêm |
| H2 | Hit = beta thị trường + thiên lệch DOWN, không phải đọc tape | by-year ở trên; 60/100 DOWN | hồi quy call Livermore lên 3 đặc trưng cơ học (mom20, mom60, vị trí trong range 250) trên chính 100 case: nếu R² cao ⇒ Livermore chỉ là "mom ngược" kể bằng văn | 
| H3 | Nhiễm hindsight (nhận ra mã/giai đoạn) | 8/16 RECOGNIZED ở thử 22/10; đọc sống FPT/NNC/VGS biết mã+ngày; cutoff mô hình 06/2026 | tách hit recognized vs không ở mọi backfill; subset sạch = as-of ≥ 07/2026 (ít) |
| H4 | Không có quy tắc nhất quán (đọc văn-hình, mỗi lần một kiểu) | chưa đo | **κ lặp lại**: 20 case × 3 lần chạy độc lập, đo đồng thuận H20_DIR và sd của p. κ<0,4 ⇒ đầu ra là nhiễu lấy mẫu của LLM, không "huấn luyện" được bằng prompt |
| H5 | Pha loãng câu hỏi (H20_DIR, LEVEL, INVALIDATION, ENTRY_VERDICT, P_TOUCH…) ⇒ không gộp được N | registry 5 entry 3 dạng khác nhau; scoreboard trống | giữ đúng 1 câu hỏi chính (H20_DIR + p) cho cổng; các câu khác chấm riêng (§5) |
| H6 | TA thuần trên VN-Index ít thông tin; DT5G đã là máy trạng thái kỹ thuật trên cùng dữ liệu | ta-schools NO-GO, ta-model 0/72, transition case Livermore = DT5G = "luôn UP" 5/8 | kiểm bằng lớp cơ học §3: nếu đặc trưng cơ học cũng không có BSS>0 thì LLM đọc trên đó cũng không thể có |
| H7 | Mẫu nhỏ, cụm theo thời gian | N_eff <100 (2021 chỉ 2/11) | tăng N theo §4 |

**Kết luận chẩn đoán:** H1 là chắc chắn (đã đo). H2/H6 rất khả dĩ. Nguyên nhân gốc KHÔNG phải "thiếu
kiến thức VN" mà là **đầu vào thô + không có quy tắc kiểm chứng được + không có vòng phản hồi**. Prompt dài
hơn sẽ không sửa được H1/H4.

## §2. "Huấn luyện" một agent LLM không có gradient — chọn kiến trúc

Không cập nhật được trọng số ⇒ chỉ có 4 tay cầm: (i) ĐỔI ĐẦU VÀO, (ii) ÉP QUY TẮC QUYẾT ĐỊNH khai báo
trước, (iii) HIỆU CHUẨN hậu kiểm đầu ra bằng dữ liệu, (iv) TỪ CHỐI phát hành khi không đủ tín hiệu.

| Lựa chọn | Quyết định | Lý do |
|---|---|---|
| (a) **Lớp đặc trưng cơ học** do code tính, Livermore đọc "thẻ đặc trưng" thay nến thô: phân kỳ RSI chuẩn hoá (§3), vị trí trong range 250, vol climax (vol/TB20 tại pivot), dry-up (vol pullback/vol đẩy), breadth PIT, khoảng cách tới đỉnh/đáy 60/250, số phiên từ pivot | **THỬ — trụ cột** | Biến "đọc hình" thành đọc số kiểm chứng được; đồng thời đo được phần LLM thêm vào trên nền cơ học (2 nhánh: thô vs thô+thẻ). Rủi ro thẳng thắn: nếu toàn bộ thông tin nằm ở thẻ, Livermore chỉ còn là người kể lại model ⇒ vai thu hẹp (§9) |
| (b) Rubric bối cảnh VN (bán lẻ ~90%, biên ±7% HOSE, T+2 bán từ chiều, sóng call margin, FTSE 21/09/2026, sàn ADV) | **THỬ — chỉ dạng ràng buộc cơ học** cho ENTRY_VERDICT (trần giá đuổi, cửa sổ chờ 5 phiên, không tính thoát trước chiều T+2) | Rubric văn xuôi không đổi được H1/H4; nhưng ràng buộc cơ học làm verdict chấm được (§5). Không viết "bài giảng" tâm lý thị trường vào prompt |
| (c) Thư viện analog/case có nhãn, khoá mù | **LOẠI (hoãn)** | Ba bẫy cùng lúc: curation, look-ahead qua trí nhớ (agent nhận ra case), và không có cách kiểm độc lập. Mở lại chỉ nếu (a) đã có BSS>0 |
| (d) **Hiệu chuẩn/shrink** về climatology: p_phát hành = hàm hiệu chuẩn(p_Livermore) fit trên backfill, hoặc isotonic trên ≥150 dự báo | **THỬ — rẻ, bắt buộc** | Với resolution 0,0002 thì shrink ≈ climatology; nó không tạo edge nhưng chặn Brier âm và làm bảng cổng công bằng |
| (e) **Ensemble/abstain**: 3 lần đọc độc lập cùng case, chỉ phát hành khi 3/3 cùng dấu và \|p−0,5\|≥0,08; còn lại ABSTAIN (ghi sổ nhưng không tính forecast) | **THỬ** | Cách duy nhất chống H4 mà không đụng trọng số; chi phí ×3 token. Phải chấm cả tỉ lệ abstain (abstain >70% ⇒ vai vô dụng về thực hành) |
| (f) Fine-tune / RAG tài liệu TA | **LOẠI** | Không có tập nhãn sạch; RAG sách TA chỉ thêm "indicator-soup" mà agent def đã cấm |

Kiến trúc đề xuất = (a)+(d)+(e), với (b) ở dạng ràng buộc. Thứ tự bắt buộc: **(a) cơ học phải tự chứng
minh trước** (P1), rồi mới cho Livermore đọc trên đó (P2).

## §3. PHÂN KỲ — đặc tả cơ học, khai báo trước (bản PREREG nháp; chốt md5 trước khi chạy)

Tra KB: **chưa có kết quả phân kỳ RSI nào trong KB** (kb_recall "divergence RSI phân kỳ" không ra; grep chỉ
thấy "phân kỳ" nghĩa định giá). Gần nhất: OSB (RSI14<30 rồi bật) trong ta-model-5pct **thua** ngẫu nhiên
(exR −0,65pp, p=0,98); ta-schools: đảo chiều/bắt đáy không thêm gì so với bối cảnh giảm. Không lặp lại OSB.

**Định nghĩa (tất cả causal, tính tại close ngày xác nhận):**
- RSI(14) Wilder trên Close điều chỉnh (biến thể duy nhất được khai thêm: RSI(9) — tính là trial riêng).
- Pivot: cực trị Close trong cửa sổ ±k phiên, **k=5, xác nhận sau k phiên** (ngày tín hiệu = pivot2 + 5).
  Hai pivot cùng loại cách nhau 10–60 phiên.
- Regular bearish: Close(p2) > Close(p1) × 1,01 ∧ RSI(p2) ≤ RSI(p1) − 3 ∧ RSI(p1) ≥ 60.
- Regular bullish: Close(p2) < Close(p1) × 0,99 ∧ RSI(p2) ≥ RSI(p1) + 3 ∧ RSI(p1) ≤ 40.
- Hidden bullish (tiếp diễn tăng): Close(p2) > Close(p1) (đáy cao hơn) ∧ RSI(p2) < RSI(p1) − 3.
  Hidden bearish: đỉnh thấp hơn ∧ RSI cao hơn +3.
- Hồi chiêu: 1 tín hiệu/loại/mã/20 phiên.
- Universe: (U1) VNINDEX; (U2) cổ phiếu `tav2_mike.universe_pit` `in_universe` tại T0 ∧ MDV60 thực
  ≥ 20 tỷ VND-2026 (đúng bậc L20 của ta-model, tái dùng engine). KHÔNG `ticker_prune`.
- Horizon: 10 / 20 / 40 phiên. Giai đoạn 2014-01 → 2026-10; IS 2014–2019, OOS 2020+; báo riêng hậu FTSE
  (≥ 2026-09-21) nhưng không kết luận từ đó (mẫu nhỏ).
- **Họ trial khai trước:** 4 loại × 3 horizon × 2 universe × 2 RSI = **48 trial**. DSR trên 48. Không thêm
  tham số sau khi thấy số.

**Tiêu chí thành công (mỗi trial):**
1. Tần suất nền: số sự kiện và số **ngày tín hiệu độc lập**; VNINDEX `ước lượng` 4–8 sự kiện/năm/loại ⇒
   ~50–100 sự kiện 2014–2026 (chưa đo; đo ở P1 trước khi phân tích).
2. Hiệu quả = hit dấu (bearish ⇒ fwd<0) và exR so với **ngẫu nhiên cùng ngày, cùng bộ lọc** (U2) hoặc so với
   climatology theo tháng (U1); CI bootstrap **khối tháng**, placebo hoán vị **nguyên khối tháng** (không
   hoán vị trong năm — memory `placebo-within-year-invalid-for-month-clustered`).
3. Đạt khi: BSS vs climatology > 0 với CI95 không chứa 0 **ở OOS**, qua BH-FDR q=0,10 trong họ 48, LOYO
   không đổi dấu quá 2/13 năm, và với U2 exR ròng sau 0,097%×2 + slippage 0,2%×2 > 0.
4. Riêng cho DT5G (§6): lead time của bearish regular tại đỉnh 250 phiên so với ngày DT commit rời
   BULL/EX-BULL; false-alarm = tín hiệu mà 40 phiên sau không có chuyển trạng thái.

**Xác suất tiên nghiệm (nói thật):** TA thô đã 0/72; OSB (cùng họ RSI) thua ngẫu nhiên; phân kỳ chỉ thêm
điều kiện "động lượng yếu đi ở cực trị mới" — về cơ học nó gần với mean-reversion ngắn hạn vốn đã không
đạt trên VN. Tôi đặt **P(U1 qua tiêu chí 3) ≈ 15%**, **P(U2 có exR dương CI loại 0 nhưng âm sau phí) ≈ 25%**,
**P(U2 ròng dương sau phí) ≈ 5%**. Lý do vẫn đáng chạy: chi phí thấp (tái dùng engine ta-model), user hỏi
đích danh, và kết quả NULL đóng hẳn hướng này thay vì để lặp lại.

## §4. Cơ chế chấm điểm — N, cách tăng N, thống kê đúng cỡ

- **N = số dự báo độc lập theo sự kiện**, không theo dòng: VNINDEX cửa sổ 20 phiên không chồng ⇒ tối đa
  ~12/năm ⇒ backfill 2014–2026 cho **~150 điểm**. Cổ phiếu: nhiều mã cùng tháng là một cụm ⇒ N_eff = số
  tháng có case (~150), không phải số case.
- **MDE (ước lượng theo công thức nhị thức, một phía α 0,05, power 0,8):** phát hiện hit 60% vs 50% cần
  N≈155; 58% cần ≈240; 55% cần ≈620. Với **12 lần đọc sống** (cổng giải thể hiện tại) chỉ phát hiện được
  edge ≥ ~25pp ⇒ cổng 12 lần là **cổng GIẾT**, không phải cổng CHỨNG MINH. Cần nói rõ trong registry.
- Thống kê dùng: BSS vs climatology (nền theo tháng, PIT) với CI bootstrap khối tháng; hit vs baseline đồng
  xu / luôn UP / mom20 / DT5G-implied; BH-FDR cho họ trial; MDE khai trước; **không** α 0,05 đơn lẻ.
- **Tăng N nhanh:** (1) backfill mù 150 ngày VNINDEX (khoá as-of, chuỗi chuẩn hoá ÷close đầu, ẩn ngày);
  (2) panel cổ phiếu 200 case, tối đa 2/mã, ≥40 phiên cách nhau (như PREREG 05/11); (3) đa horizon chỉ để
  mô tả — cổng chấm ở H20 duy nhất để tránh pha loãng (H5).
- **Chống nhiễm nhận mã:** ẩn danh + cờ RECOGNIZED bắt buộc + tách bảng recognized/không; subset sạch
  as-of ≥ 2026-07 (sau cutoff) báo riêng dù nhỏ; kiểm "mồi": 10% case là chuỗi đảo trục thời gian
  (reverse) — agent không được biết; nếu hit trên mồi ≈ hit thật ⇒ agent đoán theo hình, không theo trí nhớ
  (mồi chỉ để kiểm nhiễm, không tính vào điểm).
- Sealed truth sinh bằng script trước khi agent chạy, md5 PREREG; scorer là `livermore_score.py` mở rộng,
  không chấm tay.

## §5. Deal discretionary — "khuyến nghị vào/ra hiệu quả" đo thế nào

Chấm **chính sách thực thi**, không chấm câu chuyện. Mỗi ENTRY_VERDICT phải có field cơ học:
`zone_lo, zone_hi, max_px, wait_sessions(=5), confirm_close, confirm_vol_mult, cancel_px`.

| Verdict | Mô phỏng | Chỉ số |
|---|---|---|
| BUY_ON_PULLBACK | LO tại `zone_hi` (≤ max_px) trong W=5 phiên; khớp nếu Low ≤ giá đặt | fill rate; **cải thiện giá vào (bps) vs mua ngay close T0** khi khớp; chi phí bỏ lỡ khi không khớp = lợi suất mua-ngay H20 |
| WAIT_CONFIRM | mua Open phiên sau khi Close ≥ confirm_close ∧ Vol ≥ mult×v20, trong W | như trên + độ trễ (phiên) |
| SELL / HOLD (đang lãi) | bán close T0 vs giữ H20 | **drawdown tránh được** (MAE H20), lợi nhuận bỏ lỡ (MFE) |
| P_TOUCH ±10 | chạm high/low trong 25 phiên | Brier riêng, chấm như H20 nhưng không gộp vào cổng chính |

Chỉ số tổng hợp: **lợi suất H20 của chính sách** (gồm cả nhánh không khớp = 0) so với 3 baseline khai
trước: mua ngay · mua đều 3 phiên · **limit ngẫu nhiên cùng độ sâu** (độ sâu rút từ phân phối thực của
các zone Livermore). Tiêu chí: hơn cả 3, CI khối tháng không chứa 0. N: deal sleeve thật chỉ vài/tháng ⇒
backfill trên 200 case panel §4 (cùng case, hỏi thêm ENTRY_VERDICT) + toàn bộ lệnh vào thật trong journal
(có as-of thật, không nhiễm vì agent đã đọc trước).

## §6. DT5G — đọc sớm hơn máy trạng thái?

- Câu hỏi hợp lệ duy nhất: tại ngày **candidate ≥5/10 hoặc ≥15/25**, Livermore (hoặc thẻ phân kỳ §3) có dự
  báo đúng **COMMIT hay ABORT** của candidate đó, và sớm hơn bao nhiêu phiên?
- Chỉ tiêu: hit COMMIT/ABORT; lead time trung vị; false alarm/năm. Baseline: **DT5G-implied** (candidate
  rồi sẽ commit — tần suất nền từ lịch sử `vnindex_5state_dt5g_live` 49 transition) và "trạng thái tồn
  tại tiếp". N: số candidate 2014–2026 (đo ở P0 bằng `get_dt_gate_clock` replay; `ước lượng` 60–120).
- Ranh giới: kết quả chỉ vào khối "Kỹ thuật" báo cáo và dòng DT-gate clock; **không gate, không cap, không
  đổi tham số DT_10_25_25**. Dù P2 đạt, đổi production cần PREREG riêng + user.

## §7. Lộ trình theo pha, chi phí `ước lượng`

| Pha | Việc | Thời gian | Chi phí (ước lượng) | Cổng ra |
|---|---|---|---|---|
| **P0 Chẩn đoán** | (i) κ lặp lại 20 case × 3 (Livermore, Opus); (ii) hồi quy call lên đặc trưng cơ học (H2); (iii) chấm 5 entry sống khi đáo hạn 18/11–10/12; (iv) đếm candidate DT5G lịch sử; (v) PREREG §3 + md5 | 1–2 ngày | 60 lượt Livermore ≈ 1,5M token; Taylor 1 job ~2h | **G0**: κ<0,4 ⇒ bắt buộc (e) ensemble ở mọi pha sau, hoặc dừng |
| **P1 Lớp cơ học** | code đặc trưng (tái dùng `ta_model_5pct_20261106/engine.py`), chạy 48 trial phân kỳ, bảng §3, quant-skeptic | 2–4 ngày | Taylor Opus medium 1 job 3–4h (~3M token); skeptic Opus high (~1M) | **G1**: 0/48 đạt ở cả U1,U2 ⇒ **DỪNG nhánh phân kỳ**, chỉ còn (d)+(e) cho vai hiển thị |
| **P2 Backfill mù** | 150 VNINDEX + 200 cổ phiếu, **2 nhánh**: nến thô vs nến+thẻ đặc trưng; 3 lần đọc/case cho ensemble; chấm H20 + ENTRY_VERDICT + COMMIT/ABORT | ~1 tuần | 350 case × 2 nhánh × 3 lần ≈ 2.100 lượt Opus ≈ 30–40M token (**khoản lớn nhất — user duyệt**); có thể cắt nhánh thô còn 1 lần đọc ⇒ ~1.400 lượt | **G2**: nhánh thẻ không hơn nhánh thô VÀ không hơn climatology (BSS CI chứa 0) ⇒ dừng, đề xuất thu hẹp vai (§9) |
| **P3 Forward sống** | 12+ lần đọc theo cơ chế mới (thẻ + ensemble + shrink), khoảng cách 20 phiên; scoreboard tự động | 6–9 tháng lịch | ~3 lượt/lần đọc, nhỏ | **G3 (user)**: giữ/giải thể theo cổng hiện hành, nay hiểu là cổng giết |

Không pha nào sửa code production; P1 chỉ sinh artifact trong `agents/Taylor/research/livermore_divergence_20261114/`
(tên mới, không đụng file pin). Sửa `~/.claude/agents/livermore.md` chỉ ở P3 sau G2, có user duyệt.

## §8. Kill criteria (dừng sớm)

| Mốc | Điều kiện DỪNG | Hành động |
|---|---|---|
| G0 | κ(H20_DIR) < 0,4 trên 20×3 **và** user không duyệt chi phí ×3 ensemble | dừng toàn bộ; giữ Livermore ở vai REPORT_BLOCK thuần mô tả, không forecast |
| G0 | hồi quy H2: R² ≥ 0,5 giữa call và (mom20, mom60, vị trí range) | ghi nhận "Livermore = mom ngược"; P2 chỉ chạy nhánh thẻ (bỏ nhánh thô) |
| G1 | 0/48 trial phân kỳ đạt §3.3 ở OOS | đóng hướng phân kỳ vào `ta-schools-vn` NO-GO; không đề xuất lại |
| G1 | U1 đạt nhưng U2 không (hoặc ngược) | chỉ mang phần đạt sang P2 |
| G2 | nhánh thẻ: BSS CI95 chứa 0 ở cả 2 universe | dừng P3; đề xuất thu hẹp vai (§9) |
| G2 | tỉ lệ ABSTAIN > 70% | vai không dùng được thực tế dù BSS>0 — báo user |
| P3 | sau 12 lần chấm thua ≥1 trong 3 baseline (luật hiện hành) | đề xuất giải thể; user quyết |

## §9. Rủi ro & phản biện tự thân

- **Multiple testing**: 48 trial + 2 nhánh + 3 câu hỏi; khai họ trước, DSR/BH; không đổi k, ngưỡng RSI sau khi
  thấy số. Mọi tham số §3 là "sách giáo khoa", không tune.
- **Panel curation**: case chọn bằng seed cố định từ `universe_pit`, không chọn tay; đỉnh/đáy DT5G chỉ dùng
  ở §6 với đối chứng ngẫu nhiên cùng số.
- **Look-ahead qua trí nhớ**: nghiêm trọng nhất với VNINDEX (chuỗi nổi tiếng: 2018, 2022). Ẩn danh + mồi
  reverse + tách recognized. Nếu nhóm recognized hit cao hơn rõ, số tổng bị loại.
- **Survivorship**: `universe_pit` PIT; không `ticker_prune` (§9b guidelines).
- **Regime 2023/2025**: báo LOYO; 2025 bull một chiều làm "luôn UP" rất mạnh — Livermore phải thắng cả ở đó.
- **Scorer bias**: truth sealed, script chấm, Livermore không bao giờ thấy outcome của case cùng lô.
- **Tự đánh lừa kiểu "đổi câu hỏi"**: khi H20 thất bại dễ chuyển sang "nhưng LEVEL đúng" — cổng chính cố
  định là H20_DIR+p; câu khác chỉ mô tả.

**Nếu kết luận hợp lý là "TA không có edge trên VN-Index"** (xác suất tôi đặt ~70% sau P1–P2), vai hợp lý
còn lại, nói thẳng:
1. **Trợ lý thực thi lệnh vào deal discretionary** — đặt vùng limit/trần đuổi/điểm huỷ dạng cơ học (§5),
   giá trị đo bằng bps cải thiện giá vào, không phải dự báo hướng.
2. **Khối "Kỹ thuật" trong báo cáo** — mô tả vùng/khối lượng cho nhà đầu tư (display), số do script tính.
3. **Kỷ luật điểm hỏng** — INVALIDATION cho mỗi deal là quy tắc quản trị rủi ro, không phải dự báo.
Bỏ: dự báo hướng VNINDEX, "đọc sớm hơn DT5G".

## §10. Phân công (theo skill dispatch-routing)

| Việc | Agent | Model/effort | Pha |
|---|---|---|---|
| κ lặp lại 20×3; hồi quy H2; đếm candidate DT5G; sinh case + sealed truth | Taylor | Opus medium (thiết kế thử nghiệm mới) | P0 |
| Chạy 60 lượt đọc κ | Livermore | Opus (ghim) | P0 |
| PREREG §3 soạn + md5; code đặc trưng + 48 trial; REPORT | Taylor | Opus medium, 1 job, timeout 4h | P1 |
| Phản biện P1 (và P2) | quant-skeptic | Opus high | P1, P2 |
| Góc nhìn chế độ vĩ mô cho các năm LOYO lệch (không bắt buộc) | Bobby (macro-strategist) | Opus medium | P2 |
| Chấm scoreboard, cron, registry, bus | Mike | — | mọi pha |
| 2.100 (hoặc 1.400) lượt đọc mù | Livermore | Opus (ghim) | P2 |
| Sửa agent def + `livermore_run.sh` nhận thẻ đặc trưng (sau G2) | Taylor + arch-reviewer | Sonnet medium / Opus high review | P3 |

## §11. User cần quyết

1. Duyệt P0+P1 (rẻ, ~5M token `ước lượng`, 1 tuần) — đề xuất **có**.
2. P2 là khoản lớn (30–40M token `ước lượng`): chạy đủ 2 nhánh × 3 lần, hay cắt còn nhánh thẻ × 3 + thô × 1?
3. Chấp nhận diễn giải lại cổng 12 lần đọc = cổng GIẾT (không chứng minh được edge <25pp)?
4. Nếu G1/G2 thất bại: đồng ý thu hẹp vai Livermore về 3 việc §9 (bỏ dự báo hướng VNINDEX)?
5. Có cho Livermore tiếp tục đọc theo MÃ (FPT/NNC/VGS) trong khi P0–P2 chạy? (đề xuất: có, nhưng chỉ
   ENTRY_VERDICT dạng cơ học §5, chấm riêng, không trộn vào cổng VNINDEX.)

# 🧭 PLAYBOOK KHỦNG HOẢNG — DT5G × 8L Capitulation (pre-committed 2026-06-04)

> Mục đích: khi thị trường hoảng loạn, **chỉ thực thi — không bàn lại**. Quyết định đã chốt lúc bình tĩnh.
> Nguồn nghiên cứu: memory `dt5g-8l-crisis-capitulation-2026`. Tín hiệu live: `crisis_capitulation_signal.py`.

## 0. Điều kiện kích hoạt (cổng) — **v2: 30% (chốt 2026-06-10)**
Chỉ hành động khi **oversold breadth ≥ 30%** (% rổ `ticker_prune` có `D_RSI < 0.30`).
Sweep granular (§0b): băng 30-40% chất lượng Y HỆT 40-50% (+14.8%/win71/P10−4.3) → vách đá ở ~30%, cổng 40% cũ bỏ phí ~50% cơ hội. Tần suất mới ~6.5 ngày/năm.
Dưới 30% → KHÔNG mua-khi-sợ (chỉ WATCH nếu CRISIS & ≥5.7%: xây thăm dò, chờ sâu tới 30%).

## 0b. BẢN ĐỒ WASHOUT ĐẦY ĐỦ (deep-dive 2026-06-10, daily 2014+, fwd60 rổ quality/golden)

**Ngưỡng breadth — vách đá ở ~30%, không phải 40%:**
| Băng breadth oversold | n ngày | mean fwd60 | win | P10 |
|---|---|---|---|---|
| <10% (nền) | 2662 | +3.9% | 55% | −14.1% |
| 20-30% | 69 | +7.9% | 67% | −8.8% |
| **30-40%** | **28** | **+14.8%** | **71%** | **−4.3%** |
| 40-50% | 24 | +14.2% | 71% | −4.0% |
| 50-60% | 16 | +14.3% | 69% | −7.0% |
| ≥60% | 13 | +12.4% | 54% | −10.6% |
→ Băng 30-40% chất lượng Y HỆT 40-50% → **hạ cổng kích hoạt 40%→30%** (tần suất 4.3→6.5 ngày/năm, thêm ~50% cơ hội, không giảm chất). Sâu hơn 60% KHÔNG tốt hơn (lẫn ngày giữa-sụp-đổ).

**ROUTING THEO STATE quan trọng hơn độ sâu (breadth ≥30%):**
| State | n | mean | win | P10 | Phán quyết |
|---|---|---|---|---|---|
| CRISIS | 40 | +19.1% | 78% | −3.7% | ✅ tier-1 (như cũ) |
| **NEUTRAL** | 10 | **+18.7%** | **80%** | **−0.6%** | ✅ **cơ hội ngang CRISIS, đuôi trái LÀNH NHẤT** — local-shock trong thị trường khỏe hồi nhanh (2018-07 +57%, 2025-10 +49%) |
| BULL (flash-shock) | 7 | +15.0% | 71% | −3.1% | ✅ tier-2 OK (index win 100%) |
| **BEAR** | 24 | **+3.8%** | **46%** | −11.3% | ⚠️ **VÙNG XẤU NHẤT** — không phải trung gian! |

**BEAR chi tiết (vì sao xấu + ngoại lệ):** BEAR × dd≤−25% = win **24%** (sụp đang diễn mà DT5G chưa kịp nâng lên CRISIS = máy de-risk chưa chạm đáy); BEAR × dd>−25% (washout sớm đầu gấu) = +17.6%/win 100% (n=7); BEAR × VIX-nguội = dương cả 3 ca. → **BEAR-washout: chỉ đánh khi dd>−25% HOẶC vol NỘI ĐỊA đã nguội (VNINDEX rv10 rời ≥15% khỏi đỉnh 30 phiên); BEAR×dd-sâu×vol-đang-leo = ĐỨNG NGOÀI tuyệt đối.** (v2.1: thay VIX bằng rv10 nội địa — daily test: VN-cool win 88% n=8 vs vol-leo win 25%; VIX chỉ còn vai trò tham khảo.)

**NEUTRAL không áp-lực-vĩ-mô (VIX<22) = cơ hội thật** (4/5 thắng: +13.8/+56.9/+49.4/+0.7; cú thua duy nhất 2020-02 −2.3% = COVID đang ập đến — sốc MỚI không biết trước, size tier-2 + reset-60d xử lý được). Có áp lực vĩ mô (VIX≥22) vẫn 4/5 thắng nhưng mean thấp hơn (+13.7 vs +23.7).

> Caveat: n các ô NEUTRAL/BULL = 7-10 ngày (vài episodes) — đây là prior tốt cần forward-validate qua shadow, không phải chân lý. Cổng 30% (n=28) vững hơn.

## 1. Bao nhiêu tiền (SIZING) — dùng cash ĐANG NHÀN RỖI, không bán core
`size = base × grind` — **v2 (chốt 2026-06-10): base theo STATE, BEAR có điều kiện**
- **base** = `1.00` CRISIS · `0.75` NEUTRAL (nâng từ 0.5 — §0b: +18.7%/win80/P10−0.6, đuôi lành nhất; giữ 0.75 thay vì 1.0 vì n=10) · `0.50` BULL/EX-BULL (flash-shock) · **BEAR: `0.50` CHỈ KHI (dd VNINDEX > −25% HOẶC vol-nội-địa-nguội: rv10 ≤ 85% đỉnh 30 phiên), ngược lại `0` — ĐỨNG NGOÀI** (BEAR×dd-sâu×vol-leo win chỉ 24%, vùng xấu nhất §0b; VIX = tham khảo, KHÔNG gate)
- **grind** = `0.50` nếu là washout-lặp (xem §4) · `1.00` nếu sharp/đơn lẻ

| Tình huống | % cash nhàn rỗi đem mua |
|---|---|
| CRISIS + sharp | **100%** (all-in) |
| CRISIS + grind | 50% |
| NEUTRAL + sharp | **75%** |
| NEUTRAL + grind | 37.5% |
| BULL/EX-BULL + sharp | 50% |
| BEAR (dd>−25% hoặc vol-VN-nguội) | 50% × grind |
| **BEAR (dd≤−25% & vol-VN đang leo)** | **0% — không đánh** |

> "Cash nhàn rỗi" = phần KHÔNG đang nằm trong cổ phiếu (reserve theo state: CRISIS~100%, BEAR~80%, NEUTRAL~30%, BULL~0%). KHÔNG bán bớt core để lấy tiền — chỉ dùng tiền vốn đang để không.

> **Cơ sở Kelly của bảng sizing** (vì sao scale theo edge, KHÔNG all-in mọi cú):
> - Bet-theo-edge LÀ hình dạng Kelly: edge cao nhất ở **crisis+sharp → đặt lớn nhất (100% idle)**; edge thấp/kém-chắc nhất ở **grind → co lại (½, ¼)**. Bảng trên đi đúng thứ tự đó.
> - ⚠️ **"Win rate cao → all-in" là nửa BẪY của Kelly.** Kelly ngây thơ trên rổ washout (12 cú: win 75%, mean60 +15%, sd 14%) ra `f*>1.5` = "vay đòn bẩy" — vì nó bỏ qua 3 thứ: (1) **tương quan**: rổ 10-15 mã golden chạy cùng nhau trong sụp = thực chất ~1-2 bet độc lập, sleeve còn chồng nhau trong grind (148% NAV 2022) → Kelly cho bet tương quan đồng thời phải nhỏ hơn NHIỀU; (2) **đuôi trái thiếu**: worst case mẫu chỉ −11%, nhưng §5.1 = cú sụp cấu trúc không hồi 60d CHƯA có trong mẫu, mà Kelly cực nhạy worst-case; (3) **sai số ước lượng**: n=12 (grind n=3!) → tham số gần vô nghĩa → bắt buộc **fractional Kelly**.
> - ✅ **Kết luận: grind-half/quarter = fractional Kelly áp đúng chỗ edge bất định nhất.** Trần "cash nhàn rỗi" = van chống đòn bẩy (Kelly ngây thơ đòi >100%, ta cap ở idle). Cấu trúc state-reserve căn khéo: idle lớn nhất (≈100%) ĐÚNG lúc edge lớn nhất (đáy crisis), =0 khi BULL → max bet tự theo edge. **KHÔNG full size trên grind** (đã đồng ý 2026-06-07): sleeve chồng nhau có thể chiếm trọn NAV = overbet cùng một nhân tố.
> - 🔓 **OPTIONAL — margin CHỈ cho tier-1 crisis-sharp, trần ×1.5 (validated 2026-06-10):** mở van Kelly đúng MỘT chỗ — golden basket trong CRISIS được phép vay tới 50% NAV (lãi 10%/yr, giữ 60 phiên ≈ chi phí ~2.4% phần vay). Backtest faithful: +1.0pp CAGR, **DD NÔNG hơn** (−20.0 vs −20.6), Calmar 1.24→1.32 — đòn bẩy duy nhất pass mọi thước đo (margin toàn cục FAIL). Lưu ý: (1) gain decay theo NAV (event 2023 NAV-lớn fill y hệt — thanh khoản chặn trước tiền); (2) n=4 events lịch sử, tail §5.1 bị khuếch 1.5× — nếu dùng, TUYỆT ĐỐI không vượt 1.5× và chỉ crisis-SHARP (không grind, không non-crisis); (3) margin-call chưa được model — để dư biên an toàn với CTCK.
>
> **🎯 ĐIỀU KIỆN BẬT VAN — v2 (conditioning 2026-06-10: daily 2014+ + OOS 2000+ + macro-cooling):**
> Van mở khi đủ **CẢ HAI**:
> 1. **dd VNINDEX từ đỉnh 52w ∈ [−25%, −45%]** — đủ nén (win 100%/P10+8% in-sample; dd>−15% chỉ win 29% = chân gấu kiểu 2022-04; dd<−45% = siêu sụp đang rơi kiểu 2008, washout xong còn rơi −20..−36%).
> 2. **Sốc đã NGUỘI (không phải "không có sốc") — đo bằng nhiệt kế NỘI ĐỊA: VNINDEX rv10 ≤ 85% đỉnh 30 phiên** — và SBV không đang trong chuỗi nâng lãi suất. (v2.1: VIX hạ xuống THAM KHẢO — nó là nhiệt kế Mỹ: mù với sốc thuần VN (2018) và từng SAI ở 2022-04 (VIX nguội nhưng VN chưa, vào là thua); rv10 nội địa tái tạo đúng tách Sep/Nov-2022 và sửa cả lỗi đó. Điểm yếu ngược lại: rv10 là realized vol nên NGUỘI CHẬM sau cú sập nhanh (2020-03-30, VIX đã nguội mà rv10 chưa) — với sốc TOÀN CẦU, VIX-nguội là gợi ý sớm đáng tham khảo, nhưng quyết định chờ rv10.) Đây là điều kiện thay cho grind-filter ở tầng van.
> Bảng kiểm chứng (fwd60 rổ/index):
> | Thời điểm | dd | VIX cooling? | Kết quả | Van |
> |---|---|---|---|---|
> | 2022-09-29 | −26% | ❌ (31.8, đang leo + SBV nâng) | **−11.3%** | ĐÓNG ✓ né |
> | **2022-11-15** | −40% | ✅ (24.5 « đỉnh 30.8, SBV xong) | **+36.1%** | **MỞ ✓ bắt ĐÁY** |
> | 2020-03-12 | −25% | ❌ (75.5 = đỉnh, dao đang rơi) | — | ĐÓNG (đúng lúc knife) |
> | 2020-03-30+ | sâu | ✅ (57 « đỉnh 82.7) | các ngày deep-CRISIS T4/2020 đều + | MỞ ✓ vào sóng 2 |
> | 2008-09-16 | −59% | ❌ (đang nổ) | −35.7% | ĐÓNG ✓ (cả 2 điều kiện) |
> | 2008-08-05 | −61% | ✅ (lặng trước Lehman!) | −19.3% | ĐÓNG ✓ **nhờ sàn dd<−45** — macro một mình KHÔNG đủ |
> - **Triết lý**: vào CASH theo playbook ở washout đầu (như cũ); **van margin = vũ khí của SÓNG THỨ HAI** — khi thị trường đã nén −25..−45% VÀ cơn sốc vĩ mô ngừng leo thang. Không bật khi sốc đang diễn (dao rơi), không bật khi chưa nén đủ, không bật giữa siêu sụp.
> - Chi phí của rule: bỏ lỡ vài cú thắng vừa (2010 +6.3, 2011 +2.2, 2015 +14.8 — VIX còn nóng) — chấp nhận được vì đây là quyết định ĐÒN BẨY, tránh đuôi trái quan trọng hơn vớt upside. ⚠️ PE rẻ KHÔNG phải điều kiện (2008-09 PE pctile 8.6% vẫn −35.7%).

## 2. Mua GÌ (rổ 8L)
Rổ đều tay, tối đa ~15 mã, từ `ticker_prune`, lọc theo thứ tự ưu tiên:
1. **Quality** = `ROE_Min5Y≥12% & ROIC5Y≥10% & FSCORE≥6`, **VÀ golden** = `pb_z<−1` (rẻ-vs-lịch-sử)
2. nếu <3 mã golden → quality & `pb_z<0`
3. nếu vẫn <3 → quality (bất kỳ)
Lọc thanh khoản `≥2 tỷ/phiên`, loại mã có red-flag. (Đã tự động trong `crisis_capitulation_signal.py`.)

## 3. Giữ bao lâu → RESET
- Giữ **đúng 60 phiên giao dịch** kể từ ngày vào. **KHÔNG rút ngắn — kể cả NEUTRAL** (multi-horizon 2026-06-10: cú hồi NEUTRAL BACK-LOADED — 20 phiên mới đạt 32% của move, **mốc 40 phiên là điểm XẤU NHẤT** (P10 −24%, ổ gà giữa đường), 60d đạt 73%, 90d mới đỉnh +21.6%/win 89%. Rút ngắn = bán đúng ổ gà). 90d cho NEUTRAL = ứng viên shadow-validate, chưa commit.
- Sau 60 phiên: **bán toàn bộ rổ → trả tiền về trạng thái bình thường của V4/V5.**
- KHÔNG thoát sớm theo "pb_z đã hết rẻ" (bán nhầm cú nảy trong 1 ngày). KHÔNG chờ DT5G lên BULL (quá chậm).
- Cú flush cuối (~−12%) là bình thường ở washout cực đoan → **đừng cố bắt đúng tick**; nếu muốn, rải 2-3 lệnh trong ~3 phiên (chi phí nhỏ). Sau ngưỡng 40% thì all-in tốt hơn rải mỏng.
- ✅ **SLEEVE CAM KẾT — carve c0 ra, giữ CỨNG 60 phiên, KHÔNG giao cash qua lại với engine.** Tại washout đã chọn rổ golden có chủ đích → **khóa c0 vào rổ 60 phiên**; engine **không đụng** c0 đó, nó xoay **phần còn lại** của book để tuân thủ tỉ lệ. Nếu trong 60 phiên DT5G **rớt state** (NEUTRAL→BEAR→CRISIS) → engine **cắt các holding KHÁC** xuống cho đúng target, **tôn trọng sleeve capitulation** (không bán rổ). Hết 60 phiên: rổ bán → engine chạy bình thường lại.
  - **Vì sao tốt hơn "bám cash engine"** (backtest 2014–now, V5): committed **+6.58pp / Sharpe 1.63** > overlap-bám-cash **+4.97pp / Sharpe 1.54** > và đây là số THẬT (substitution, không đếm trùng: `combined=(1−w)·core+w·basket`). Rổ golden thắng được cái engine sẽ làm với số tiền đó khi hồi phục → để nó chạy đủ 60 ngày hiệu quả hơn switch tới lui.
  - ⚠️ **Đánh đổi:** carve-out **khóa vốn** → trong gấu nghiền nhiều washout chồng nhau, sleeve xếp chồng có thể **chạm ~100% NAV** (2022 backtest tới 148% trước khi cap) → lúc đó gần như toàn bộ NAV nằm trong rổ, engine hết phần xoay = concentration risk §5.1. **Grind-half/quarter sizing (§1, §4) chính là van an toàn cho việc này** — giữ kỷ luật size, đừng full trên grind.

## 4. Sharp vs Grind (quyết định nhân 0.5)
Là **grind** (gấu kéo dài, washout chưa phải đáy cuối) khi:
- **Washout-lặp:** đã có một washout (≥40%) khác cách đây **20–90 phiên** (cùng một con gấu đang thủng đáy mới).
→ grind = bơm NỬA size, để dành phần còn lại cho washout kế (>30 phiên sau).
Bài học 2022: 3 washout trong 6 tháng, 2 lần thua, rơi thêm −20%…−38% sau washout. Grind-filter cắt đúng các cú đó.
> ❌ **Đã thử & LOẠI (2026-06-04): "breadth còn xấu đi".** Test cho thấy nó TRUE ở 92% washout (breadth sụp mạnh nhất ĐÚNG tại đáy capitulation) → không phân biệt, và gắn cờ nhầm đúng 2 cú đẹp nhất (2014 +35%, 2020-COVID +32%). Chỉ dùng washout-lặp. Live giờ KHỚP đúng backtest.
⚠ **Hạn chế còn lại:** detector chỉ thấy washout TRƯỚC đó → **không bắt được cú ĐẦU TIÊN** của một con gấu mới (cú đầu vẫn full size; 2022-04 thua −7%). Đệm = tầng-2-nửa-size + giữ-60-ngày-rồi-reset (cú thua vẫn hồi nếu giữ đủ).

## 5. GUARDRAILS (bắt buộc nhớ)
1. **Tail risk thật:** "MaxDD không đổi" chỉ đúng vì lịch sử washout đều hồi <60 ngày. Một cú sụp cấu trúc (tệ hơn 2022, không hồi) CÓ THỂ phá vỡ → giữ kỷ luật size, đừng vì backtest đẹp mà tất tay.
2. **Rebuild baseline trước mỗi quyết định nâng cấp:** chạy `rebuild_baseline.bat` (đừng tin file `_dt5g.csv` cũ — đã từng stale x9.98 vs x13.23).
3. **Quote f=cash, KHÔNG f=reserve** (reserve đếm 2 lần phần ETF).
4. **Tầng 2 đang NỬA size + theo dõi OOS** (`pt_capitulation_shadow.py`). Chỉ nâng lên full sau ≥1 washout ngoài-crisis xác nhận forward.

## 6. Hiệu năng kỳ vọng (engine real cash, no proxy, COMMITTED-SLEEVE, 2014–2026)
> Mô hình SLEEVE CAM KẾT (§3: carve 60d, không switch cash) trên V5+cap (rscap), baseline 24.88%. Substitution `combined=(1−w)·core+w·basket` — KHÔNG đếm trùng. `committed_sleeve_overlay.py`.
- Tầng 1 (crisis-only): **+4.1pp CAGR (→28.99%), MaxDD ≈ baseline (−23.0), Sharpe 1.59 > 1.51.**
- Tầng 1+2 (grind-half): **+6.6pp CAGR (→31.45%), MaxDD −23.5% (≈baseline), Sharpe 1.63 > 1.51** — risk-adjusted tốt nhất.
- So sánh 3 mô hình kế toán (grind-half V5): STATIC +9.57pp (ĐẾM TRÙNG, ảo, bỏ) · OVERLAP-bám-cash +4.97pp (Sh 1.54, bảo thủ quá) · **COMMITTED +6.58pp (Sh 1.63, CHỌN)**. Rổ golden thắng cái engine sẽ làm với cash đó → giữ đủ 60 ngày > switch tới lui.
- ⚠️ Sizing backtest "grindhalf" aggressive hơn §1 (full cash trên non-crisis sharp); theo §1 thật (base 0.5 non-crisis) → concentration & return nhẹ hơn chút. Thực tế trừ thêm ~1–1.5pp (phí/slippage mã golden nhỏ/thuế) → coi ~31% là cận-trên-hợp-lý.

---
*Tín hiệu tự chạy mỗi 15:30 (`papertrade_daily.bat` bước 8 alert + bước 9 shadow sleeve). Khi nổ sẽ có Telegram ping. Lúc đó: mở `crisis_capitulation_signal.py` → đọc level + reserve% + rổ → thực thi theo §1–§3.*


---

## 7. DOMESTIC DECOUPLING — radar 1 xuống × radar 2 lên (pre-committed 2026-06-12)

**Kịch bản**: index gãy vì megacap mean-revert (vd họ VIC) trong khi quân (equal-weight) khỏe. **CHƯA TỪNG CÓ trong 12 năm** — cả 9/9 episode "DT5G defensive × breadth STRONG" lịch sử đều có EW giảm theo trong vài tuần (cell fwd60 −4.3%/31% win → mặc định vẫn NGHE radar 1). Section này chỉ kích hoạt khi ngoại lệ đầu tiên thật sự xuất hiện.

**⚠ Washout sẽ KHÔNG nổ ở kịch bản này** (washout = giảm đồng loạt; ở đây quân không giảm) → capit im lặng là ĐÚNG THIẾT KẾ, không phải hệ thống hỏng. Đường mua thế giới EW trong kịch bản này là SIGNAL THƯỜNG (momentum theo quân, không theo index — quân khỏe thì signal tự dồi dào).

### Tầng cảnh báo (dòng La bàn2, dna_report — detector wired 2026-06-12)
- **ROTATION-WATCH**: VNI 20d < −2% & spread (EW−VNI) 20d > +1.5pp → tướng rơi nhanh hơn quân. Chỉ nhìn, không làm gì. *(Đang ở mức này từ ~06/2026: VNI −5.0%/20d, EW −3.0%.)*
- **🚨 DECOUPLING-CONFIRMED**: DT5G ≤ BEAR & **EW 20d > 0 tuyệt đối** & spread > +3pp, bền ≥ 15 phiên & breadth mom10 ≥ 0 → ô chưa-từng-có đã thành hình. Human review BẮT BUỘC, hành động theo bảng dưới.

### Hành động pre-commit khi CONFIRMED (người thực thi, KHÔNG auto-code)
Phân tích ràng buộc: trong BEAR, cửa sổ entry BAL (svk ≤60d sau release) GIỐNG HỆT NEUTRAL → BAL gần như không bị ảnh hưởng. Ràng buộc cắn thật chỉ có 3:
1. **w_LAG BEAR = 0 (V2.3A) → GIỮ 0.50 thay vì về 0.** Lý do: BEAR=0 được hiệu chỉnh trên gấu HỆ THỐNG (LAG −14%/yr); gấu-chỉ-số-quân-khỏe thì PEAD neo fundamentals trong thế giới EW vẫn sống. Đây là MỘT núm duy nhất được phép lệch.
2. **CRISIS svk 30d → cân nhắc nới 60d** (quyết định người, chỉ khi confirmed bền).
3. **Cash không park ở state 1-2** → chấp nhận (giữ cash an toàn; KHÔNG mua ETF index đang gãy vì megacap).

### Guardrail (đường lui)
- Breadth mom10 < −6pp bất kỳ lúc nào → luận điểm decoupling CHẾT NGAY → trở về playbook chuẩn (lịch sử nói: quân sẽ theo tướng; mặc định radar 1 đúng).
- Mọi lệch khỏi rule chỉ kéo dài khi detector còn CONFIRMED; tắt cờ → trả w_LAG về policy gốc.
- KHÔNG thêm tiền mới vào lệch này — chỉ giữ nguyên cấu trúc vốn đang có (đây là rule "đừng tự cắt chân", không phải rule tấn công).

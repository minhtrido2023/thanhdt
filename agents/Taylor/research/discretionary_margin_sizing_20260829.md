# Nghiên cứu lại trần margin đơn mã discretionary — sleeve 5%→15%? per-name 3%→5%?

> Job `Taylor_20260829_154054` · 2026-08-29 · **RESEARCH-ONLY, KHÔNG sửa `kb/projects/discretionary-margin-policy-20260823.md`, KHÔNG code.** User yêu cầu kiểm chứng lại trước khi implement (đã hẹn 08-29, `discretionary-margin-policy-20260823.md` dòng 8).
>
> Mandate: user hỏi "nếu sleeve hiệu quả thì 15% NAV cũng không tạo ra rủi ro gì nhiều" — đánh giá 5/10/15% × per-name 3/5%, exit −20% GIỮ NGUYÊN (không xét lại).

## Tóm tắt kết luận (đọc trước)

1. **Phát hiện quan trọng nhất — 2 tài liệu chính sách hiện có ĐANG DÙNG 2 CƠ SỞ KHÁC NHAU cho "5% NAV sleeve"**, và điều này phải được giải quyết TRƯỚC khi bàn số mới, không phải sau:
   - `discretionary-margin-policy-20260823.md` (đơn mã, chính sách đang được yêu cầu sửa): 5% là **EXPOSURE** (giá trị vị thế), max loss = exposure×20% = **1,0% NAV** — công thức ĐÚNG.
   - `margin_cap_recovery_forensic_20260825.md` (sleeve Loại-2 khủng hoảng, không phải file đang sửa nhưng dùng chung con số 5%/6,5%): công thức viết là `equity_cap × 20%`, nhưng **equity ≠ exposure khi f>1** — loss thật = exposure×20% = (5%×1,3)×20% = **1,3% NAV**, cao hơn 30% so với con số 1,0% họ công bố. Đây là lỗi số học có thật trong tài liệu nguồn (không phải nghi ngờ), xem §1 dưới.
   - **Hệ quả cho job này**: khi user nói "15% NAV", phải hỏi rõ 15% là EXPOSURE hay EQUITY trước khi tính bất kỳ bảng nào — 2 cách đọc lệch nhau tới hệ số f (1,3–2,0×). Job này trình bày **cả hai** cách đọc ở bảng cuối, không tự chọn hộ.
2. **Ở NAV LIVE thật hiện tại (SpaceX 985,5tr VND, 2026-08-28), ADV/capacity KHÔNG PHẢI ràng buộc nhị phân** — kể cả 15% sleeve dồn hết vào TV1 (ADV thật ~842tr/ngày, BQ 3 tháng) chỉ chạm ~17,6%ADV, vẫn trong biên ≤15-20%ADV đã duyệt sẵn cho TV1 discretionary. Điều này **ngược với giả thuyết trong dispatch** ("capacity/ADV có thể là binding constraint thật sự") ở quy mô NAV hiện tại — nhưng sẽ ĐẢO NGƯỢC hoàn toàn khi NAV lớn lên (xem §2).
3. **Risk math correlated (đúng như user nêu — sleeve fear-buy sập CÙNG NHAU)**: max loss = exposure_cap × 20%, không giảm nhờ "đa dạng hoá" vì các case cùng đặt cược vào MỘT giả thuyết (thị trường/ngành hồi phục). 5%→1,0% NAV, 10%→2,0% NAV, 15%→3,0% NAV. Xếp lên bootstrap 5th-pct MaxDD V2.4 (−28,6%, anchor ~−29%) cho tổng ước lượng −29,6%/−30,6%/−31,6% NẾU sleeve fire đúng lúc V2.4 đang ở đáy DD tệ nhất — kịch bản THỰC (cùng gate dd52-driven).
4. **Tương tác `capit_margin_lever`** (LIVE, f=1,3, cùng gate dd52≤−20%): sự kiện nặng nhất đã đo được vay **25,9% NAV** (tại NAV ~938tr, gần đúng scale hiện tại). Cộng sleeve discretionary 15% (nếu dùng f=2,0 broker-max) thêm ~7,5% NAV nợ nữa → tổng nợ đồng thời có thể chạm **~33% NAV** cùng ngày, cùng gate. Đây là **câu hỏi CHƯA từng được tính rigorous ở mức combined-account** — cả hai chính sách đều chỉ phân tích sleeve của MÌNH độc lập. Khuyến nghị: cần 1 job forensic riêng trước khi wire 15%, không tự suy diễn margin-call an toàn từ 2 phân tích tách rời.
5. **Mandate Loại-2 08-25 sẽ MÂU THUẪN trực tiếp** nếu per-name/sleeve của chính sách đơn mã đổi — không tự sửa, nêu rõ ở §5.

---

## Nguồn dữ liệu dùng trong job này (real, không giả định)

- NAV SpaceX thật: `data/execution_logs/nav_history_SpaceX.csv`, dòng 2026-08-28 → **985.547.490 VND** (~985,5tr). Chỉ SpaceX có margin (ZaloPay cash-only, ngoài phạm vi chính sách này).
- ADV thật TV1/DGC: BQ `tav2_bq.ticker`, cửa sổ 2026-06-01→2026-08-28 (3 tháng gần nhất):
  | Ticker | avg Trading_Value/ngày | median Trading_Value/ngày |
  |---|---|---|
  | TV1 | 842,3 triệu VND | 701,1 triệu VND |
  | DGC | 31,07 tỷ VND | 24,73 tỷ VND |
  (Job trước đó — `dgc-tv1-fearbuy-discretionary.md` — trích ADV TV1 "~1 tỷ/ngày" từ Volume_3M_P50 hồi 07-23; số BQ mới hơn ở đây thấp hơn nhẹ, ~700-840tr — dùng số MỚI này, không dùng số cũ.)
- `capit_margin_lever` config thật (`data/trading_rules.json`): **f=1,3**, gate `dd52<=-0.20`, enabled=true (LIVE từ 2026-08-22), scope=CAPIT-only, account=SpaceX-only. Evidence p5: "heaviest single event borrows 25,9% of NAV (~243,5tr tại NAV 938tr), average event 6,8% (~63,6tr)". Backtest (khác vintage, 50B): "Peak simultaneous debt 30,55B/50B book" = 61,1% NAV — **KHÔNG dùng số này cho NAV live thật** (khác scale, chỉ nêu để biết biên trên lý thuyết).
- Bootstrap 5th-pct MaxDD V2.4: **−28,6%** (KB `context_taylor_mini.md`, anchor thực hành ~−29%).
- DNSE loan package 1840 (RocketX): initial=0,5 (f_max=2,0) · maintenance=0,4 · liquidation=0,3 · lãi vay 12,5%/năm — verified LIVE `Mafee_20260823_083327`.
- Margin call netting **cấp ACCOUNT, không cấp vị thế** (phát hiện đã có, `discretionary-margin-policy-20260823.md` dòng 45-50) — TÁI DÙNG, không đo lại.
- DGC hiện đang `excluded_tickers` ở ZaloPay do **hạn chế giao dịch HOSE + vụ án hình sự** (`kb/context_safety_core.md` dòng 22) — cổ phiếu diện hạn chế giao dịch thường KHÔNG marginable ở DNSE (chưa verify trực tiếp job này, nêu như giả định cần Mafee xác nhận trước khi tính DGC vào bất kỳ case margin nào).

---

## §1 — RISK MATH: correlated, không phải "3 mã độc lập"

User đúng: giả định "N case độc lập" là sai mặc định cho sleeve fear-buy. Các mã fear-buy được MUA CHÍNH XÁC vì chúng đang hoảng loạn — nếu đó là hoảng loạn mang tính hệ thống (dd52 VNINDEX≤−20%, đúng gate hiện tại), khả năng cao NHIỀU case active CÙNG một lúc CÙNG chịu áp lực giảm giá từ MỘT nguồn rủi ro (risk-off toàn thị trường), không phải N nguồn rủi ro độc lập kiểu due-diligence-sai-lệch-riêng-từng-mã.

**Công thức đúng, sửa lỗi equity/exposure ở tài liệu Loại-2**: loss thực nhận tại exit −20% (từ giá arm) = **exposure_cap × 20%**, không phải equity_cap × 20% — vì mọi biến động giá dồn hết vào vốn tự có khi nợ (VND tuyệt đối) không đổi:
```
equity_loss(d) = exposure_0 × |d|     (độc lập với f — chứng minh: equity_ratio(d) = [f(1+d)-(f-1)]/[f(1+d)]
                                        → equity_loss = exposure_0×(-d), f triệt tiêu)
```
Tài liệu `discretionary-margin-policy-20260823.md` (đơn mã, file đang xét) dùng exposure trực tiếp nên **1,0% NAV cho sleeve 5% là ĐÚNG**. Tài liệu Loại-2 (`margin_cap_recovery_forensic_20260825.md`) gọi nhầm exposure_cap là equity_cap trong công thức A5 → **thiếu 30% max loss thật ở f=1,3** (1,3% chứ không phải 1,0%). Không sửa file đó trong job này (ngoài phạm vi dispatch), chỉ cảnh báo vì cùng gia đình số liệu.

### Bảng max loss correlated (worst-case: toàn sleeve arm cùng lúc, cùng sập −20%)

| Sleeve exposure cap | Max loss = sleeve×20% | Stack lên bootstrap 5th-pct MaxDD (−28,6%) |
|---|---|---|
| 5% NAV (hiện tại) | 1,0% NAV | ~−29,6% |
| 10% NAV | 2,0% NAV | ~−30,6% |
| 15% NAV (đề xuất) | 3,0% NAV | ~−31,6% |

Đây là kịch bản **không giả định** — sleeve chỉ arm khi dd52≤−20% (đúng gate chung với `capit_margin_lever`), tức là chính xác lúc V2.4 hệ thống CŨNG đang gần drawdown tệ nhất của nó. Cộng dồn 3,0% NAV không phải là số "sẽ luôn xảy ra", nhưng là biên trên hợp lý để so với ngưỡng dừng đã có (B2_episode_breaker V2.5: −15% NAV từ episode-entry → BOT_STOP — 3,0% NAV bằng 20% ngân sách đó, không nhỏ).

---

## §2 — CAPACITY/ADV: KHÔNG binding ở NAV hiện tại, SẼ binding khi NAV lớn

Tính theo NAV SpaceX thật 985,5tr:

| Cap | VND | %ADV TV1 (842tr/ngày) | %ADV DGC (31,07 tỷ/ngày) |
|---|---|---|---|
| 3% NAV per-name (hiện tại) | 29,57tr | 3,5% | 0,10% |
| 5% NAV per-name (đề xuất) | 49,28tr | 5,9% | 0,16% |
| 10% NAV sleeve | 98,55tr | 11,7% | 0,32% |
| 15% NAV sleeve (đề xuất, dồn 1 mã) | 147,83tr | **17,6%** | 0,48% |

**Đọc bảng**: ở NAV hiện tại (~1 tỷ VND), kể cả case xấu nhất (15% sleeve dồn hết vào TV1, mã kém thanh khoản nhất trong 2 case đang biết) chỉ chạm 17,6%ADV — **vẫn trong biên ≤15-20%ADV** đã duyệt sẵn cho TV1 discretionary (`dgc-tv1-fearbuy-discretionary.md`), chỉ hơi sát trần trên. DGC không phải vấn đề capacity ở bất kỳ cap nào (ADV gấp ~37× TV1).

**Nhưng đây là hiện tượng ĐẶC THÙ CỦA QUY MÔ NHỎ, không phải bằng chứng "15% an toàn mãi mãi"**: NAV SpaceX hiện chỉ ~985,5tr — nhỏ hơn nhiều so với NAV backtest pin 50 tỷ. Nếu NAV tăng lên (ví dụ) 10 tỷ, 15% sleeve dồn vào TV1 = 1,5 tỷ VND = **~178%ADV** — hoàn toàn không khả thi build/unwind trong ngày, và exit −20% "intent" sẽ trở thành exit thật cách xa nhiều chục điểm % vì market impact/slippage khi cả rổ bán ra đúng lúc thanh khoản co lại (đặc điểm crisis: ADV illiquid names co lại MẠNH hơn ADV trung bình khi hoảng loạn, không giữ nguyên 842tr).

**Kết luận §2**: %NAV cap và %ADV cap là **HAI ràng buộc tách biệt, ràng buộc nào chặt hơn thì nó quyết định** — với TV1-style illiquid, %ADV (đã có sẵn quy tắc ≤15-20%ADV pace) sẽ tự động khống chế size DÙ %NAV cap có nói 15% hay 50%, MIỄN LÀ pace rule đó được enforce nghiêm túc theo NAV SỐNG (không hardcode theo NAV hôm nay). Câu hỏi "5% vs 15% NAV" **chỉ thực sự có ý nghĩa (tức là binding) cho mã fear-buy THANH KHOẢN như DGC** — nơi %NAV cap, không phải %ADV, là ràng buộc chặt. Với DGC hiện đang bị hạn chế giao dịch (khả năng không marginable — cần Mafee xác nhận), case thực tế duy nhất có thể chạm cap 15% mà không bị ADV chặn trước là mã liquid TƯƠNG LAI, chưa có trong danh sách hiện tại.

---

## §3 — Tương tác `capit_margin_lever` (LIVE, f=1,3, CÙNG gate dd52≤−20%)

Đây là câu hỏi RỦI RO THẬT chưa ai tính rigorous — cả 2 chính sách margin (capit hệ thống + discretionary đơn mã) đều **cùng gate dd52≤−20%**, nghĩa là chúng có xác suất cao **fire CÙNG NGÀY, CÙNG TÀI KHOẢN** (SpaceX), và margin call netting là **CẤP ACCOUNT** — tức là rủi ro margin call phải nhìn TỔNG nợ 2 sleeve cộng lại, không phải từng sleeve riêng.

### Số đã có (không suy diễn):
- `capit_margin_lever` (f=1,3) — nợ sự kiện nặng nhất đã đo: **25,9% NAV** (tại NAV ~938tr, gần scale hiện tại 985,5tr — coi là đại diện hợp lý).
- Discretionary sleeve tại cap đề xuất 15% NAV exposure: nợ = exposure×(1−1/f). Ở **f=1,3** (giống quy ước capit): nợ = 15%×0,231=3,46% NAV. Ở **f=2,0** (broker-max, giả định ẩn trong chính sách đơn mã cũ): nợ = 15%×0,5=**7,5% NAV**.

### Tổng nợ đồng thời worst-case (cùng ngày, cùng gate):
| Kịch bản | Nợ capit (nặng nhất) | Nợ discretionary @15% | Tổng nợ/NAV |
|---|---|---|---|
| Hiện tại (sleeve 5%, f=2,0) | 25,9% | 2,5% (khớp số đã ghi trong policy cũ) | 28,4% |
| Đề xuất (sleeve 15%, f=1,3) | 25,9% | 3,46% | 29,4% |
| Đề xuất (sleeve 15%, f=2,0) | 25,9% | 7,5% | **33,4%** |

Dùng công thức margin ratio đã verify (`margin_cap_recovery_forensic_20260825.md` A2/A3, f=1,3 riêng sleeve): drawdown tệ nhất quan sát trong 3 episode lịch sử (COVID −18,75%) chỉ đưa equity_ratio riêng sleeve capit về 71,6%, cách maintenance (40%) ~32pp. **Nhưng đó là phân tích CHỈ MỘT sleeve** — chưa ai tính equity_ratio cho TOÀN ACCOUNT khi CẢ HAI sleeve cùng có nợ 33,4% NAV đồng thời VÀ phần còn lại của NAV (V2.4 core BAL+LAG) cũng đang chịu cùng đợt sụt giá đó. Ước lượng thô (giả định toàn bộ position — cả unlevered lẫn levered — sụt cùng −20%, không có phần nào miễn nhiễm): equity còn lại ≈ NAV×(1−20%) − (phần margin call chưa kích vì netting account-level không cắt tới 40% ở quy mô nợ này, theo đúng cách tính đã verify cho case đơn sleeve) — theo hướng này tổng nợ 33,4% NAV so với maintenance 40%/liquidation 30% **vẫn còn xa** ở mức drawdown −20% (kịch bản exit trigger), nhưng **CHƯA được đo bằng công thức margin ratio thật của DNSE cho TOÀN ACCOUNT** (không chỉ ngoại suy tuyến tính như trên).

**⇒ Khuyến nghị rõ ràng: đây là khoảng trống rigor thật, không phải rủi ro đã loại trừ.** Trước khi wire 15%, cần 1 job forensic riêng: mô phỏng đúng công thức margin ratio DNSE cho toàn account khi CẢ HAI sleeve cùng active tại các mốc drawdown lịch sử (2020-03, 2022-11), không suy diễn tuyến tính từ 2 phân tích tách rời như job này vừa làm. Ước lượng thô ở trên gợi ý margin call KHÔNG PHẢI ràng buộc chặt ngay cả ở 33,4% NAV nợ (còn cách xa cả maintenance lẫn liquidation dựa trên biên độ đã verify ở f=1,3 lẻ), nhưng "gợi ý" ≠ "đã verify" — đừng trích số 33,4% này như kết luận cuối.

---

## §4 — Stress 2022-11 (SCB/VTP): giới hạn dữ liệu thật

**Không thể backtest trực tiếp** — TV1/DGC KHÔNG phải case fear-buy đã xác định tại 2022-11 (chúng được due-diligence lần đầu 2026-07). Không có lịch sử giá "arm case tương tự" thật tại giai đoạn đó để đo P&L cụ thể cho 2 mã này.

**Cái CÓ thể nói bằng số thật (đã đo ở job khác, tái dùng không chạy lại)**:
- VNINDEX-level: nếu sleeve arm tại đúng đáy 2022-11-15 (counterfactual), max DD 60 phiên từ điểm vào = **0,00%** (đã ở đáy) — đây là kịch bản THUẬN LỢI NHẤT, không phải trường hợp xấu.
- Nhưng **cổ phiếu đơn lẻ dạng scandal/panic thường sập SÂU HƠN VNINDEX nhiều** (đặc thù đúng lý do các case này QUALIFY vào sleeve fear-buy — chúng sập vì lý do riêng CỘNG với risk-off chung). VNINDEX dd52 tại 2022-11 là −40,3%; các mã dính scandal cùng giai đoạn (nhóm BĐS/TPDN, ngoài phạm vi TV1/DGC) từng ghi nhận mức giảm −70-80% từ đỉnh trong công khai thị trường — đây là bối cảnh định tính, KHÔNG phải số đo trực tiếp cho TV1/DGC, chỉ để cảnh báo: exit −20% "từ giá arm" đo trên GIÁ MÃ ĐÓ, không phải trên VNINDEX, và với case scandal-driven, biên độ sập của MÃ ĐƠN LẺ có thể xa hơn biên độ index nhiều.
- Kết hợp với ADV TV1 chỉ ~842tr/ngày: trong đúng lúc hoảng loạn, ADV illiquid thường CO LẠI (ít người mua, chỉ có người bán) — nghĩa là thực thi exit −20% có rủi ro trượt giá LỚN HƠN bình thường, đúng caveat đã ghi sẵn trong framework Loại-2 ("Exit −20% từ arm là intent, không phải guaranteed price... slippage"). Nâng cap sleeve/per-name KHÔNG làm caveat này biến mất — ngược lại, size lớn hơn (15% thay vì 5%) cần NHIỀU phiên hơn để thoát trong hoảng loạn, kéo dài thời gian phơi nhiễm với slippage.

**Kết luận §4**: không có bằng chứng định lượng trực tiếp cho TV1/DGC tại 2022-11 (N=0 thật cho 2 mã này), chỉ có suy luận định tính có cơ sở (đặc thù scandal-driven single-name thường sập sâu hơn index, ADV co lại đúng lúc cần thoát) — đủ để CẢNH BÁO, không đủ để tính một con số max-loss mới.

---

## §5 — Mandate Loại-2 08-25: MÂU THUẪN nếu đổi số đơn mã

`kb/projects/discretionary-margin-policy-20260823.md` §"Sleeve Loại-2" (chốt 08-25, risk-auditor Spyros CONDITIONAL-APPROVE) viết RÕ: *"Trần đơn mã (nếu chọn từng mã riêng trong basket): ≤1% NAV vốn tự có / ≤3% NAV exposure (giữ nguyên từ chính sách đơn mã 08-23 — lý do due-diligence-error risk không đổi theo bối cảnh)"* — tức là mandate Loại-2 **THAM CHIẾU TRỰC TIẾP** số đơn mã 08-23 (1%/3%) làm cơ sở suy ra trần sleele Loại-2 (5%/6,5%).

Nếu chính sách đơn mã đổi per-name 3%→5% và/hoặc sleeve 5%→15%, **2 hệ quả bắt buộc phải xử lý đồng bộ, KHÔNG tự sửa trong job này**:
1. Mandate Loại-2 phải được risk-auditor + user duyệt lại (nó KHÔNG tự động kế thừa số mới — trích dẫn rõ "giữ nguyên từ chính sách đơn mã 08-23" nghĩa là nó NEO vào số CŨ, đổi số cũ mà không quay lại Loại-2 sẽ để 2 tài liệu commit vào 2 con số khác nhau cho cùng khái niệm).
2. §1 đã chỉ ra công thức Loại-2 (`equity_cap×20%`) tự nó có lỗi tính (thiếu hệ số f) — sửa lại đúng công thức RIÊNG đã đủ làm trần Loại-2 dịch (1,0%→1,3% NAV max loss ở cùng cap 5%/6,5%), CHƯA KỂ tác động domino từ việc đổi số đơn mã.

---

## Bảng tổng hợp — 5%/10%/15% sleeve × 3%/5% per-name

Giả định exposure-based (đọc nhất quán với văn bản gốc `discretionary-margin-policy-20260823.md`), NAV=985,5tr, TV1 làm ca xấu nhất (ADV mỏng nhất).

| Sleeve cap | Per-name cap | Max loss correlated (=sleeve×20%) | %ADV TV1 nếu dồn 1 mã tới trần sleeve | Nợ cộng dồn với capit heaviest event (f=2,0 discretionary) | Ghi chú |
|---|---|---|---|---|---|
| 5% (hiện tại) | 3% (hiện tại) | 1,0% NAV | 5,9%ADV (tại per-name 3%) / 5,9%ADV (sleeve 5% ≈ 1 case) | 25,9%+2,5%=28,4% NAV | Baseline đã duyệt |
| 5% | 5% (đề xuất per-name) | 1,0% NAV | 5,9%ADV | 25,9%+2,5%=28,4% NAV | Per-name nới nhưng sleeve giữ ⇒ chỉ 1 case full-size, risk KHÔNG đổi so với baseline (vẫn 1 case chạm 5%) |
| 10% | 5% | 2,0% NAV | 11,7%ADV | 25,9%+5,0%=30,9% NAV | 2 case @5% song song |
| 15% (đề xuất) | 5% | 3,0% NAV | 17,6%ADV (SÁT trần ≤15-20%ADV) | 25,9%+7,5%=**33,4%** NAV | 3 case @5% song song — cần job §3 xác nhận margin combined trước khi duyệt |
| 15% | 3% | 3,0% NAV | 17,6%ADV nếu dồn nhiều case vào 1 mã kịp — thực tế bị per-name 3% chặn trước | 25,9%+7,5%=33,4% NAV (nợ tính theo EXPOSURE sleeve, không đổi theo per-name) | Per-name giữ 3% ⇒ cần ≥5 case song song mới chạm sleeve 15% — thực tế N case discretionary hiếm khi >2 (chỉ TV1+DGC hiện có) nên **sleeve 15% + per-name 3% gần như không bao giờ chạm trần thật** — cấu hình này KHÔNG rủi ro hơn baseline vì thiếu case để lấp đầy |

**Đọc nhanh**: rủi ro thật (max loss, %ADV, nợ combined) chỉ tăng khi **CẢ per-name VÀ số case song song đều tăng**. Với chỉ 2 case đang biết (TV1, DGC), sleeve 15% chỉ thực sự "dùng hết" nếu per-name cũng nới lên 5% VÀ có ≥3 case đồng thời (chưa từng xảy ra — lịch sử tối đa 2 case). Nói cách khác: **nâng sleeve cap một mình (giữ per-name 3%) gần như vô hại vì không đủ case lấp đầy nó** — rủi ro thật nằm ở việc nâng PER-NAME cap (3%→5%), vì đó trực tiếp tăng exposure của MỖI case đang có, không phụ thuộc số case tương lai.

---

## Khuyến nghị (không tự chốt — user quyết)

1. **Per-name 3%→5% NAV**: risk tăng có cơ sở đo được — max loss/case tăng từ 0,6% lên 1,0% NAV (dùng đúng exposure×20%), %ADV TV1 tăng 3,5%→5,9% (vẫn thoải mái trong biên ADV). Rủi ro chính là §3 (tương tác capit_margin_lever) và §4 (slippage exit khi mã sập sâu hơn index) — không phải capacity.
2. **Sleeve 5%→15% NAV**: theo bảng trên, tác động thật PHỤ THUỘC per-name cap và số case song song — với per-name giữ 3% thì gần như vô hại (không đủ case lấp đầy); với per-name lên 5% VÀ ≥3 case cùng lúc thì mới chạm mức rủi ro/nợ đáng kể (§1, §3). **User nên tách quyết định: (a) per-name cap trước — đây là đòn bẩy thật; (b) sleeve cap chỉ có ý nghĩa AN TOÀN CỰC ĐẠI khi có nhiều case hơn hiện tại, không cần vội quyết 15% ngay khi chỉ có 2 case.**
3. **BẮT BUỘC trước khi code**: (a) thống nhất exposure-vs-equity cho MỌI con số %NAV trong cả 2 chính sách (§1); (b) job forensic combined-margin-ratio account-level (§3) — chưa có, không suy diễn; (c) đồng bộ lại mandate Loại-2 nếu số đơn mã đổi (§5).
4. **Exit −20%**: giữ nguyên đúng theo yêu cầu — không đổi, nhưng lưu ý caveat slippage (§4) áp dụng MẠNH HƠN khi size lớn hơn (15% sleeve cần nhiều phiên hơn để thoát trong hoảng loạn với TV1-style ADV).

## Giới hạn phải mang theo
- §3 (combined margin ratio) là **ước lượng thô, chưa verify bằng công thức DNSE thật cho toàn account** — đừng trích số 33,4%/margin-safe như kết luận cuối.
- §4 không có N thật cho TV1/DGC tại 2022-11 — chỉ suy luận định tính từ bối cảnh thị trường chung.
- ADV TV1 dùng cửa sổ 3 tháng gần nhất (06/2026-08/2026) — có thể không đại diện ADV lúc hoảng loạn (thường co lại, không phải hằng số).
- Không backtest — đúng bản chất chính sách này (N quá nhỏ, due-diligence không scale), giữ nguyên tinh thần `discretionary-margin-policy-20260823.md`.

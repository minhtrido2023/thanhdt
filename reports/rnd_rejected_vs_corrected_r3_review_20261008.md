# Rà lại các nhánh R&D bị loại vì "không vượt pin R3" sau khi pin R3 hạ — 2026-10-08

> Mike soạn theo yêu cầu user 22:33 ICT 08/10. Chỉ đọc KB/registry/artifact, KHÔNG chạy backtest, KHÔNG sửa code.
> Nguồn: `data/results_registry.md` (mục 2026-09-27 sexies/septies/ter-bis, 2026-07-12 Q-sleeve, 2026-07-14 sector-cap,
> 2026-09-09 vòng 4/5, 2026-07-06 DC-book), `kb/projects/r3-pin-history.md`, `agents/Taylor/research/*` (DC 3-book,
> dividend_yield_floor, cash_dividend_announcement_premium, top5_postearnings, idle_cash_proxy, park_fraction_grid).

## 1. Lỗi đo nằm ở đâu — và nó có hướng

| Mốc pin R3 | CAGR | Vì sao đổi |
|---|---|---|
| 2026-08-03 | 28,86% | chuỗi return rổ park custom30V chain trên `Close_adj × OShares` ⇒ mỗi bước số CP theo quý thành 1 ngày return GIẢ (đếm hai lần) |
| 2026-09-27 | 24,38% → 24,42% | gỡ bug: **−4,48pp** (IS −7,83pp, OOS −1,24pp), knob park 0,7 |
| 2026-09-27 | 23,43% → **23,37%** | đổi knob park về đúng live 0,30; FAIL-C (nhãn look-ahead 25 phiên) −0,06pp |
| 2026-09-28 | dải **23,37% (pin0%) … 25,71% (pin1M)** | đổi thước đo lãi tiền nhàn rỗi, không đổi mô hình |
| 2026-10-01 | live park = **0%** | user chốt; **chưa re-pin ở 0** (mục đang mở 10-08) |

Hai điều quyết định cách đọc lại mọi nghiên cứu cũ:

1. **Bug chỉ ở rổ PARK custom30V.** BAL/LAG (`self-check 0 VND`) không đụng. Nghiên cứu nào không đi qua
   `custom_basket.build/build_pit` thì số tuyệt đối vẫn đúng.
2. **Bug CÓ HƯỚNG theo thành phần rổ.** Return giả sinh ở ngày có bước OShares; Taylor ghi rõ 2014-2019 ngân
   hàng VN phát CP thưởng/cổ tức CP dày nhất ⇒ rổ càng nặng ngân hàng càng được thổi. custom30V production
   nặng ngân hàng **49,1% trọng số toàn kỳ, 67,5% OOS** (vòng 4, 09-09). ⇒ Mọi treatment làm **giảm** tỷ trọng
   ngân hàng hoặc thay rổ bằng tên ít phát CP thưởng đều bị **phạt oan** khi so với control.
   Ghi chú kiểm kê của Taylor ngày 27/09 ("delta A/B cùng mang lỗi ⇒ không đảo dấu") chỉ đúng khi hai chân
   có **cùng mật độ bước OShares** — không đúng cho chân đổi thành phần.

## 2. Phân loại các nhánh đã bị loại

### A. Không bị ảnh hưởng — verdict đứng nguyên
| Nhánh | Lý do không ảnh hưởng |
|---|---|
| ConvergePort / DC-book (07-06, 08-25, 08-30 ×2) | `converge_portfolio_backtest.py::parking_returns()` tự dựng custom30V từ **giá** (buy-and-hold trong quý), không qua chuỗi OShares. +5,0pp sleeve, +0,19pp/−2,1pp DD full-NAV, alpha BULL ≥54-70% — số sạch |
| V2.5 lever, LAG (ADV gate, sàn thanh khoản, half-size, d_NPR), BAL 5 vòng, CCS, edge-gate | đo trên BAL/LAG hoặc trên excess cùng chân park |
| Top-5 sau BCTC (08-18) | standalone vs VNINDEX, không có park; chết vì edge chỉ 2020-21 |
| Dividend Yield Floor (08-18) | event study ghép cặp, không qua NAV |
| Deep-discount sleeve #12 (06-26) | proxy-gate trên forward return, không qua harness |
| pbcombo dual-vehicle #18 (06-27) | cả hai chân cùng rổ yieldcombo nền, chỉ đổi vehicle ở ngày deploy; bác vì DD/Calmar, cùng hướng với bug (bug làm chân ON đẹp hơn thật) |
| BULL-extension park (5 lần NO-GO) | bug thổi rổ park ⇒ mở park sang BULL trông **tốt hơn** thật mà vẫn NO-GO ⇒ NO-GO càng chắc |
| Hướng B route LAG idle → park trong BULL (08-25) | cùng logic trên |

### B. Bị phạt oan có hướng — verdict cũ KHÔNG còn tin được như đã ghi
| Nhánh | Verdict cũ | Vì sao nghi | Mức nghi |
|---|---|---|---|
| **Q-sleeve** Q8/Q12/QF8 thay custom30V (07-12) | NO-GO: IS kém **2,95-6,76pp**, LOO âm mọi năm | rổ 8-12 tên chất lượng, ít ngân hàng hơn hẳn; **IS inflation của control = 7,83pp** — cùng bậc với khoảng thua. MaxDD xấu hơn 3,9-6,5pp cũng đo trên chân control được thổi | CAO — phải chạy lại mới biết |
| **Sector-cap / fincap** cắt ngân hàng (07-14) | NO-GO: −0,16…−0,84pp | khoảng thua **nhỏ hơn bug** nhiều lần; cắt bank = cắt return giả. Vehicle-level "DD xấu đi" có thể cũng là hiện vật | CAO |
| **L1 nới pool 60→90→120** (09-09) | "chưa chứng minh" +1,07/+2,62pp, DSR 0,66-0,78 | giảm bank 3,6-8,1pp mà vẫn dương ⇒ edge thật **lớn hơn** số đã đo | TRUNG BÌNH (chiều có lợi) |
| custom30V permanent-exclude 7 tên, delta-mom tilt, FSCORE/accrual gate, eyrisk, v3route, v4final DY, beta-cap | NO-GO | đổi tên trong cùng pool thanh khoản, bank share gần như không đổi ⇒ delta gần đúng, nhưng **chưa ai đo** bank share của từng chân | THẤP |

### C. Chưa từng đo được — không phải NO-GO
| Nhánh | Trạng thái |
|---|---|
| **Cash-dividend announcement premium** (09-04) | BLOCKED dữ liệu: `corporate_action` upsert tại chỗ xoá ngày công bố; snapshot PIT mới có từ 17/08. Mốc mở lại **không sớm hơn 2027-08**. Không có claim H1/H2 nào |
| Yield-floor làm selector custom30V (08-18) | user chọn Option C (nhãn quan sát), gate #2 đọc **2027-02-10** |

## 3. Điều quan trọng hơn cả bug: mẫu số so sánh đã đổi

- Live 08/10 SpaceX: NAV 987tr = cổ phiếu 48% · tiền 1% · **Trứng vàng 51%** (8,543%/năm net). `n_bal = 0`.
- Backtest: tiền nhàn rỗi trung bình **46,4% NAV**; LAG ngồi **56-59% cash trong BULL**, 78% phiên BULL không có
  lệnh LAG nào (08-25).
- Lưới park 12 mức (09-27): ở lãi nhàn rỗi 0%, park đổi **+1pp CAGR lấy −1pp DD, tỉ lệ 1:1**; proxy lịch sử tầng 1
  là 4,16%/năm, không tháng nào vượt break-even 7,0%; Trứng vàng 8,5% là tầng 3 (khuyến mãi DNSE).
- ⇒ **Hurdle thật cho MỌI sleeve đỗ tiền hôm nay = 8,5%/năm net với DD ≈ 0**, không còn là "có hơn custom30V không".
  Nhóm B ở trên dù có đảo verdict cũng **không đổi tiền live** chừng nào lãi còn cao (trigger quay lại park = lãi hạ,
  đã có cron tuần cảnh báo).

## 4. Nhánh nên nghiên cứu tiếp — theo thứ tự tôi đề xuất

1. **Re-pin R3 ở knob live park=0, thêm chân idle = tầng 3 (lãi Trứng vàng thật)** — đang mở chờ user (10-08). Mọi so
   sánh mới đều cần mẫu số này; chạy rẻ (đổi 1 biến, lệnh pin có sẵn). Kèm bootstrap DD để có neo sizing đo đúng knob.
2. **BAL trống + LAG đói tín hiệu trong BULL** — chỗ có upper bound lớn nhất (+22pp gross BULL lý thuyết) và chưa
   từng được test: hướng A (nới `MAX_POS_V11 = 12`, 08-25) bị gác vì "ngoài phạm vi", không phải vì số. Câu hỏi nghiên
   cứu: khi LAG không có deal, BAL được giữ >12 tên có pha loãng alpha momentum không (walk-forward, DSR).
3. **DC-book state-gated BULL/EXBULL** — alpha thật (quant-skeptic CONFIRMED ×2) nhưng N=6 episode, COVID gánh 85%.
   Không cần backtest thêm; cần **đọc sổ paper** (đã mở BULL từ 08-31; 56 phiên toàn NEUTRAL, cum +0,36%) và chốt mốc
   review — mốc event-anchored ~06/10 đã qua mà registry chưa có `review_date`.
4. **Chạy lại nhóm B trên engine đã sửa** (Q-sleeve 5 CSV, sector-cap 4 CSV, pool-widen 3 CSV — knob env có sẵn, 1 job)
   — xếp sau vì chỉ có giá trị khi park bật lại; nhưng đáng làm **một lần** để đóng sổ đúng: nếu Q-sleeve/de-bank hoá ra
   không thua, nhận định "custom30V thắng nhờ breadth" trong canonical phải sửa.
5. **Cổ tức tiền mặt**: (a) announcement premium chờ snapshot đủ 12 tháng, chỉ cần cron ghi lại dòng `announced` mới mỗi
   ngày từ bây giờ (hướng 3 trong report 09-04, chưa làm); (b) KHÔNG mở sleeve "payer ổn định thay cash": yield floor
   chỉ cho đệm DD +2pp (placebo-net t=1,63) mà mã chạm sàn vẫn sụt −10,8% trung bình ⇒ không thay được Trứng vàng.

**Không mở lại**: BULL-extension park (5×), V2.5 lever, composite v3 selector, MOM_N/S, hold-neutral — bug làm các nhánh
này trông tốt hơn thật mà vẫn NO-GO.

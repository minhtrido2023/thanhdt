# Forensic combined-margin cấp ACCOUNT — SpaceX (capit_margin_lever + discretionary_margin_gate)
> Job `Taylor_20260830_031004` · 2026-08-30 · **RESEARCH-ONLY, KHÔNG đổi code/config production.**
> Điều kiện tiên quyết trước khi xét lại sleeve cap 15% (risk-auditor CONDITIONAL-APPROVE per-name
> 5% nhưng REJECT sleeve 15% một phần vì thiếu forensic combined-account này).

## Kết luận 1 dòng
**Margin ratio KHÔNG PHẢI ràng buộc thật ở cấp combined-account, kể cả worst-case documented** —
cách maintenance call (40%) tối thiểu **~35pp** ngay tại thời điểm arm, và cần thêm **−59% đến
−61%** giá cổ phiếu (từ điểm arm) mới chạm maintenance. Kết luận này GIỮ NGUYÊN dù sleeve ở 5%,
10%, hay 15% — vì cả hai cơ chế dùng CHUNG hard-cap f=1,3, nên gộp chúng lại không nhân đôi đòn
bẩy trung bình của account, chỉ cộng thêm một khoản debt nhỏ lên nền tài sản lớn hơn nhiều.

---

## 1. Công thức DNSE thật (không phải ước lượng)

Từ `dnse_openapi_v2_calling_guideline.md` (verified LIVE 2026-08-23, job `Mafee_20260823_083327`,
gói 1840 RocketX): `initialRate=0,50 · maintenanceRate=0,40 · liquidRate=0,30 ·
interestRate=0,125`. Tài liệu DNSE **không** công bố công thức margin ratio tường minh qua endpoint
này — công thức dùng ở đây (đã verify bằng nghiệm đảo, tái dùng nguyên xi từ forensic per-name
08-25 `margin_cap_recovery_forensic_20260825.md` Phần A2, không tự chế lại):

```
equity_ratio(d) = [f·(1+d) − (f−1)] / [f·(1+d)]      # d = %thay đổi giá từ lúc arm, f = đòn bẩy TB
d_break(target)  = (f−1) / (f·(1−target)) − 1          # nghiệm đảo: d cần để chạm ngưỡng target
```

`equity_ratio` = (Tổng tài sản ký quỹ − Tổng nợ) / Tổng tài sản ký quỹ — đúng định nghĩa margin
ratio chuẩn broker VN, khớp với maintenanceRate/liquidRate DNSE trả về (ngưỡng SO trực tiếp với
tỷ lệ này, không phải NAV/(NAV+nợ) xấp xỉ).

## 2. Cấu trúc NAV THẬT — SpaceX, dòng cuối `nav_history_SpaceX.csv` (2026-08-28)

| Thành phần | VND | % NAV |
|---|---|---|
| NAV | 985.547.490 | 100% |
| `mtm_stock` | 876.924.500 | 88,98% |
| `cash` | 8.195.610 | 0,83% |
| `egg_assets` (Trứng vàng) | 100.435.143 | 10,19% |
| `margin_debt` hiện tại | 7.763 | ~0% |

**Egg KHÔNG được tính vào mẫu số collateral.** `dnse_openapi_v2_calling_guideline.md` xác nhận
`egg.totalValue` là SIBLING riêng của block `stock` trong payload `balances` — vốn CHỦ SỞ HỮU thật
nhưng cần lệnh RÚT + về tài khoản T+1 mới thành sức mua; tài liệu KHÔNG nói egg được DNSE chấp
nhận làm tài sản thế chấp cho vay margin cổ phiếu (đây là sản phẩm tách biệt, giống tiền gửi có kỳ
hạn/quỹ, không nằm trong sổ chứng khoán). **Chưa xác nhận trực tiếp với DNSE** — dùng giả định BẢO
THỦ (loại egg khỏi mẫu số) đúng nghi ngờ ban đầu của risk-auditor; nếu sau này xác nhận egg CÓ
được chấp nhận làm collateral, mọi equity_ratio dưới đây chỉ CAO HƠN (an toàn hơn), không thấp hơn.

⇒ **Collateral base C0 = stock + cash − debt = 885.112.347 VND (89,81% NAV).**

## 3. Trần debt worst-case của 2 cơ chế (documented, KHÔNG tự ước lượng)

| Cơ chế | Trần trong policy | Quy đổi ra DEBT (qua f=1,3: debt = exposure×(1−1/f) = exposure×0,2308) |
|---|---|---|
| `capit_margin_lever` | "heaviest single event borrows **25,9% NAV**" — số THẬT từ p5 (`data/trading_rules.json`, đã tự flag là **LOWER BOUND**) | 25,9% NAV DEBT trực tiếp (đã là số nợ, không cần quy đổi) |
| `discretionary_margin_gate` | sleeve tổng exposure ≤ **5% NAV** (policy hiện hành, per-name cũng 5%) | 5%×0,2308 = **1,154% NAV DEBT** |

Cả hai cùng gate trên `dd52<=-20%` (capit: điều kiện arm cứng trong code; discretionary: không
gate theo dd52 trực tiếp, nhưng dispatch giả định worst-case đồng thời — hợp lý vì cả hai đều
được thiết kế cho kịch bản khủng hoảng cùng loại).

**⚠️ Không xác nhận được nguồn con số "~33,4% NAV" risk-auditor trích** (không tìm thấy artifact
gốc trong `mike/kb`/bus để đọc lại công thức của nó). Số đúng theo công thức DNSE + trần
documented ở trên là **27,05% NAV debt** (5,25pp thấp hơn), không phải 33,4%. **GIẢ THUYẾT, chưa
xác nhận** (đúng §29 — không đoán nguyên nhân khi chưa đọc được bằng chứng): nếu 33,4% cộng trực
tiếp % EXPOSURE (không phải % DEBT) của các trần lại với nhau, đó là lỗi loại phạm trù dưới đòn
bẩy f=1,3 — exposure luôn LỚN HƠN debt (exposure = debt/0,2308), cộng nhầm 2 đại lượng khác đơn vị
sẽ luôn cho số lớn hơn debt thật.

## 4. Equity ratio combined worst-case — tại điểm arm (d=0, dd52 đúng −20%, chưa giảm thêm)

Cả 2 cơ chế cùng fire tối đa tại đúng thời điểm dd52 chạm −20% (không arm sớm hơn, đúng yêu cầu
dispatch). `Assets_after = C0 + D_total` (nợ mua thêm cổ phiếu, cộng dollar-for-dollar vào tài
sản; NAV bất biến tại d=0 vì đây chỉ là đổi cấu trúc vốn, chưa có biến động giá).

| Sleeve cap | D_capit | D_disc | D_total (%NAV) | equity_ratio tại arm | Gap→maintenance(40%) | Gap→liquidation(30%) | avg f |
|---|---|---|---|---|---|---|---|
| **5% (chính sách hiện hành)** | 25,90% | 1,154% | **27,05%** | **76,85%** | **+36,85pp** | **+46,85pp** | 1,3012 |
| 10% (giả định) | 25,90% | 2,308% | 28,21% | 76,10% | +36,10pp | +46,10pp | 1,3141 |
| 15% (đã bị REJECT 08-29) | 25,90% | 3,462% | 29,36% | 75,36% | +35,36pp | +45,36pp | 1,3269 |

## 5. Stress thêm −20% SAU khi đã arm (tái diễn kiểu 2022-11)

Toàn bộ stock book (holdings cũ + phần mua thêm bằng đòn bẩy) giảm thêm 20% từ giá lúc arm —
debt KHÔNG đổi (VND cố định), chỉ tử số equity co lại theo giá.

| Sleeve cap | equity_ratio sau thêm −20% | d_break→maintenance (từ điểm arm) | d_break→liquidation (từ điểm arm) |
|---|---|---|---|
| 5% | **71,06%** | **−61,42%** | **−66,93%** |
| 10% | 70,12% | −60,16% | −65,86% |
| 15% | 69,20% | **−58,94%** | −64,80% |

**Đọc bảng**: kể cả ở sleeve 15% (mức đã bị risk-auditor REJECT), cần đúng **−58,94%** giá cổ
phiếu từ điểm arm (không phải từ đỉnh) mới chạm maintenance call — so với kỷ luật thoát tự áp đã
duyệt là **−20%** (gấp gần **3 lần** buffer). Số này **gần như không đổi theo sleeve cap**
(35,4–36,9pp tại arm, 58,9–61,4% d_break) vì cả 2 cơ chế cùng hard-cap f=1,3 — combined account
không "nhân đôi" đòn bẩy trung bình, chỉ cộng thêm 1-3pp debt lên nền 89,8% NAV collateral.

## 6. Vì sao combined không tệ hơn nhiều so với per-name (đã đo 08-25)

`equity_ratio` phụ thuộc **avg leverage f = Assets/Equity**, không phụ thuộc SỐ TIỀN debt tuyệt
đối. Vì cả `capit_margin_lever` VÀ `discretionary_margin_gate` đều hard-cap f≤1,3 (cùng quy ước,
`discretionary_margin_gate.py:52` `MAX_F=1.3 # đồng quy ước capit_margin_lever`), avg f của TOÀN
BỘ account sau khi cả hai fire tối đa cũng chỉ nhích từ 1,3012→1,3269 (sleeve 5%→15%) — không tiến
gần bậc rủi ro nào khác. DNSE enforce MỘT tỷ lệ margin duy nhất cấp account (không phải cấp cơ
chế) nên không có rủi ro "double-count collateral" giữa 2 mechanism — mỗi VND collateral chỉ được
tính một lần trong công thức thật của broker, và cả hai cơ chế cùng rút từ MỘT pool đó.

## 7. T+2 settlement lag khi de-lever khẩn — CHƯA đóng hoàn toàn

Memory fleet đã có (`project-t2-sell-settlement-margin-netting.md`, **ĐÍNH CHÍNH**): giả thuyết
"nợ margin bị netting trễ T+2" từng bị nêu rồi **BỊ BÁC BỎ** — hiện tượng quan sát chỉ là balance
API stale giữa phiên, NAV = Tiền+Cổ phiếu−Nợ đơn giản dùng bản đọc mới nhất là đủ, không cần model
bù trừ. Điều này ngụ ý nợ margin giảm ngay khi lệnh bán KHỚP (không đợi T+2), khớp thông lệ margin
VN phổ biến (nợ netting T+0 dù cổ phiếu giao T+2).

**Nhưng đính chính đó được rút ra cho mục đích NAV/PNL nói chung, chưa từng verify RIÊNG cho kịch
bản de-lever khẩn cấp 2 cơ chế cùng bán** — coi là **CHƯA ĐÓNG**. Nếu tiến tới xét sleeve cap cao
hơn, cần Mafee xác nhận trực tiếp (đọc `totalDebt` trước/sau 1 lệnh bán thật, cùng phiên) trước
khi coi T+2 lag là rủi ro đã loại trừ hoàn toàn ở kịch bản combined.

Thanh khoản delever: cả 2 cơ chế đều đã có trần %ADV riêng khi ARM (`discretionary_margin_gate.py`
≤10% ADV-3m; capit sleeve có `capit_adv_caps` tương tự) — nên lệnh THOÁT (ngược chiều, thường dễ
khớp hơn lệnh vào ở mức thanh khoản tương đương) không nên bị nghẽn nhiều phiên trong điều kiện
thị trường bình thường; CHƯA stress-test riêng thanh khoản BÁN trong chính kịch bản khủng hoảng
đang xét (thanh khoản thường co lại đúng lúc cần bán nhất) — giới hạn cần ghi nhận, không phải đã
đo.

## 8. Cảnh báo tail-risk KHÔNG thuộc phạm vi tính toán margin ở trên

`capit_margin_lever.known_limits` (`data/trading_rules.json`) ghi nhận một artifact envelope CHƯA
ĐÓNG HẲN: trần state-anchored có thể để lọt exposure tới **63,4% NAV** (thiết kế 24,4% NAV, hệ số
lọt 2,60×) — CAO HƠN nhiều số 25,9% NAV debt dùng làm baseline worst-case ở mục 4-5. Rủi ro này
hiện được chặn bởi **CỔNG NGƯỜI THỨ HAI** (duyệt tay mỗi ngày có vay, `approve_margin_day.py`),
KHÔNG phải bởi chính sizing math — nếu cổng người bị bỏ qua/lỗi, worst-case debt combined có thể
cao hơn đáng kể số 27,05% NAV dùng ở đây. Đây là rủi ro CỦA RIÊNG `capit_margin_lever` (đã biết từ
2026-08-03), không phải rủi ro MỚI phát sinh từ việc kết hợp với `discretionary_margin_gate` —
không mở rộng phạm vi job này để đóng nó (ngoài scope forensic combined-account).

---

## Kết luận đầy đủ, cho input xét lại sleeve cap sau này (KHÔNG phải bây giờ)

1. **Margin ratio KHÔNG PHẢI lý do hợp lệ để giữ sleeve cap ở 5%** — kể cả ở 15% (mức đã REJECT),
   buffer tới maintenance vẫn ~35pp tại arm và ~59% d_break, gấp ~3× kỷ luật thoát −20% đã duyệt.
   Kết luận này áp dụng CHO CẢ single-mechanism (đã có từ forensic 08-25) VÀ combined-account (job
   này) — không có khoảng trống rigor nào còn lại ở TRỤC MARGIN MATH.
2. Cơ sở hợp lý để KHÔNG nâng sleeve (nếu muốn giữ nguyên) là **Phần A4 của forensic 08-25**
   (correlation risk — sleeve washout tương quan cao với chính book hệ thống BAL/LAG, không phải
   2 case độc lập) và **kỷ luật lỗ vốn thực nhận ≤X% NAV mỗi lần escalate sai** (đã tính trong
   `discretionary_margin_sizing_20260829.md`) — KHÔNG PHẢI margin-survival.
3. 2 việc còn CHƯA đóng nếu muốn xét lại sleeve cap sau này: (a) verify T+2/netting margin debt
   RIÊNG cho kịch bản de-lever khẩn (mục 7), (b) đóng artifact envelope 63,4% NAV của
   `capit_margin_lever` trước khi coi cổng người là lưới an toàn duy nhất (mục 8) — cả hai đều
   KHÔNG chặn quyết định sleeve cap trực tiếp (không nằm trong phạm vi margin-ratio combined vừa
   đo), chỉ là 2 khoảng hở vận hành nên biết trước khi coi hồ sơ rủi ro là "đã đóng hoàn toàn".

## Giới hạn phải mang theo
- NAV/cấu trúc dùng ở trên là **snapshot 2026-08-28**, không phải NAV tại thời điểm dd52 thật sự
  chạm −20% trong tương lai (tỷ trọng stock/cash/egg có thể khác khi khủng hoảng thật xảy ra) —
  đây là stress test cấu trúc HIỆN TẠI, không phải dự báo NAV tương lai.
- Egg loại khỏi collateral là **giả định bảo thủ chưa xác nhận trực tiếp với DNSE** (mục 2).
- Số 25,9% NAV cho `capit_margin_lever` là **LOWER BOUND** tự khai trong `data/trading_rules.json`
  (không phải trần cứng) — dùng nguyên văn, không tự nâng/hạ.
- Không backtest, không DSR/PBO — đây là forensic tính toán trực tiếp bằng công thức DNSE thật +
  số liệu NAV/debt/rate đã verified, đúng yêu cầu dispatch ("dùng công thức thật, không ước lượng
  thô").

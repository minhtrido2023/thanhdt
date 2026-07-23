# Fear-buy sleeve — hệ thống hoá thành QUY TẮC sizing (scenario analysis)

> Taylor (Quant/Algo), job `Taylor_20260723_103411`, 2026-07-23. **RESEARCH-ONLY — không wire.**
> Nối tiếp: playbook `calculated_fear_state_backstop.md` (job `Taylor_20260717_122129`) + TV1 SOTP
> (`tv1_pecc1_sotp_20260723.md`). Trả lời câu hỏi user: *"bỏ 1 phần NAV mua các case QUALIFY lịch
> sử, sau 2 năm thu hồi vốn bao nhiêu cho production hiện nay?"*

## ⚠️ CẢNH BÁO THỐNG KÊ ĐỌC TRƯỚC (bắt buộc — §Multiple-testing discipline)
Đây **KHÔNG PHẢI backtest hệ thống hoá** theo nghĩa production (V2.4/R3). N = **2 case QUALIFY sạch**
(PNJ 2015, VEA 2019). **Không tính được DSR/PBO** — mẫu quá nhỏ, không có phân phối để deflate.
Đây là **scenario analysis dựa trên case study**: ước lượng "nếu-thì", KHÔNG phải edge đã kiểm chứng.
"Win rate 2/2" **không có ý nghĩa thống kê**. Giá trị của khung nằm ở **bộ lọc phân biệt (discriminator)
+ kỷ luật sizing**, không phải một con số CAGR trích dẫn được. Đừng để PNJ +249% làm lu mờ điều này.

---

## 1. Case library — verify lại bằng dữ liệu THẬT (BQ cache `ticker`, adjusted Close)

Phương pháp: đáy scandal cô lập trong **cửa sổ 90 ngày** kể từ ngày công bố (tránh nhiễu chu kỳ/
COVID về sau); đo forward **12m & 24m**. Báo **2 điểm vào**: *buy@trough* (bắt đúng đáy — cận trên
lạc quan, không thực tế) và *buy@ann* (mua ngày công bố — thực tế hơn vì **không ai bắt đúng đáy**).

| Case | Lớp | Đáy | buy@trough 12m / **24m** | buy@ann 12m / **24m** | VNIndex 24m |
|---|---|---|---|---|---|
| **PNJ '15** (DAB/chồng CT) | ✅ QUALIFY | 6.090 | +149% / **+278%** | +134% / **+249%** | (n/a) |
| **VEA '19** (bắt cựu CT) | ✅ QUALIFY | 22.420 | −5% / **+22%** | −24% / **−3%** (giá đơn thuần) | +33% |
| TIS '19 (TISCO-2) | ⚠️ AMBIG | 9.500 | −3% / +28% | −29% / +28% | +30% |
| OCH '14 (Hà Văn Thắm) | ⚠️ AMBIG | 24.700 | −64% / −78% | −65% / **−79%** | +15% |
| **OGC '14** (lõi = NH) | ❌ NON | 6.000 | −30% / −79% | −78% / **−89%** | +15% |
| **PVX '17** (mất thanh toán) | ❌ NON | 2.100 | −5% / −33% | +13% / **−57%** | +34% |
| **HVN '21** (COVID, lõi hỏng) | ❌ NON | 15.620 | +23% / −32% | +23% / **−32%** | −5% |
| **FLC '22** (Trịnh Văn Quyết) | ❌ NON | — | — | **−100% (huỷ niêm yết)** | — |

**Đọc bằng chứng (trung thực):**
- **Discriminator vẫn đúng hướng**: QUALIFY 24m dương (PNJ +249%, VEA +22% buy@trough); NON 24m âm
  sâu (−57% → −100%). Cái quyết định thắng-thua = **bản chất scandal + tài sản lõi có tách biệt & tạo
  tiền không**, KHÔNG phải "đã giảm bao nhiêu".
- **PNJ chi phối HOÀN TOÀN mặt lời**. VEA giá-đơn-thuần 24m chỉ **−3%** (buy@ann) và **THUA VNINDEX
  −36pp** (VNIndex +33%). VEA chỉ "thắng" nếu tính **cổ tức** — nhưng cột `DY` trong BQ cache **không
  populate** (=0) ⇒ **không định lượng được cổ tức từ dữ liệu có sẵn**. VEA nổi tiếng payout ~90-99%
  (cash-cow JV Honda/Toyota/Ford), cổ tức cộng thêm ~10-15%/năm là **kiến thức ngoài, chưa verify BQ**
  — nên trình giá-đơn-thuần làm **sàn thận trọng**, đánh dấu cổ tức là upside KHÔNG đếm.
- **TIS "phục hồi" +28% = beta ngành thép 2020-21, KHÔNG phải resolve scandal** (VNIndex cùng kỳ +30%
  ⇒ net ~−2%). Đúng cảnh báo §1 playbook: đừng nhầm beta ngành với edge pattern.
- **buy@ann << buy@trough** ở mọi case (vd PVX +13%→−57%, OGC −30%→−89%): **giá vào quyết định phần
  lớn kết quả**. Bắt đúng đáy là ảo tưởng ⇒ khung 3-tranche (§3 playbook) tồn tại chính vì lý do này.

---

## 2. Mô phỏng sizing — "sau 2 năm thu hồi bao nhiêu" cho production HIỆN NAY

**NAV production hiện tại** = SpaceX 929,8tr (07-20) + ZaloPay 886,1tr (07-22) = **1,816 tỷ VND**.
Quy tắc mô phỏng: entry giá công bố (buy@ann, thực tế), giữ **cố định 2 năm** (khớp câu hỏi user).

### 2a. Đóng góp NAV mỗi case theo cap sizing (giữ 2 năm)

| Cap/case | Tiền/case | WIN PNJ-like (+249%) | WIN VEA-like giá (−3%) | LOSS misclass NON (−70%) | LOSS worst FLC (−100%) |
|---|---|---|---|---|---|
| **0,5% NAV** | 9,08tr | **+22,6tr (+1,25pp)** | −0,3tr (−0,01pp) | −6,3tr (−0,35pp) | −9,1tr (−0,50pp) |
| **1,0% NAV** | 18,16tr | **+45,2tr (+2,49pp)** | −0,5tr (−0,03pp) | −12,6tr (−0,69pp) | −18,2tr (−1,00pp) |
| **2,0% NAV** | 36,32tr | **+90,4tr (+4,98pp)** | −1,1tr (−0,06pp) | −25,2tr (−1,39pp) | −36,3tr (−2,00pp) |

### 2b. Nếu áp quy tắc lên ĐÚNG 2 case QUALIFY lịch sử (mỗi case 1% NAV, giữ 2 năm)
- Triển khai 36,3tr (2% NAV) → sau 2 năm **80,99tr** = **+123% trên vốn triển khai** = **+2,46pp NAV tổng**.
- **≈ gấp đôi vốn sleeve** — NHƯNG **100% nhờ PNJ**. Bỏ PNJ ra → VEA giá-đơn-thuần ≈ hoà vốn. Đây
  chính là **fragility N nhỏ**: toàn bộ "edge" nằm ở 1 multi-bagger duy nhất trong 11 năm.

---

## 3. Kịch bản NGƯỢC — nếu due-diligence LỌC SAI (bức tranh cân bằng, không tô hồng)

Rủi ro thật KHÔNG phải "QUALIFY rồi vẫn thua" mà là **misclassification**: tưởng QUALIFY nhưng thực
ra NON. Đây là rủi ro SỐNG, đã quan sát 2 lần chỉ trong tháng 7/2026:
- **DGC**: đánh giá AMBIGUOUS 17/07 → Q2 công bố 22/07 lộ **mỏ 25 bị dừng phục vụ điều tra** (lõi vật
  lý bị chạm) → downgrade gần NON. Nếu đã mua theo kịch bản Bull (+68%) thì sai hoàn toàn.
- **PNJ 2026**: AMBIGUOUS, cổng xác nhận Q3 (~cuối 10) còn xa 3,5 tháng — chưa biết GIA có rút không.

**Thiệt hại khi lỡ mua 1 NON** (24m, buy@ann): OGC −89%, PVX −57%, HVN −32%, **FLC −100% (mất trắng)**.
Trung bình NON = **−70%**. Ở cap 1% NAV → **−0,69pp NAV/case sai**; worst-case FLC huỷ niêm yết →
**−1,0pp** (mất trọn vị thế, không bán được).

### Break-even win-rate — con số quyết định độ an toàn của sleeve
`p·W + (1−p)·(−70%) = 0` → `p = 70/(W+70)`:

| Nếu winner trả về (24m) | Cần đúng > | Đọc |
|---|---|---|
| +249% (PNJ-like multi-bagger) | **22%** số lần | Rất dung sai — sai 3/4 vẫn hoà |
| +80% (blended thận trọng) | **47%** số lần | Cần đúng khoảng nửa |
| +22% (VEA-like khiêm tốn) | **76%** số lần | Cần lọc gần như hoàn hảo |

**Đây là crux trung thực**: sleeve chỉ có EV dương nếu (a) winner thỉnh thoảng là multi-bagger PNJ-like
**HOẶC** (b) discriminator lọc đúng >~50%. Nếu winner đa số chỉ khiêm tốn kiểu VEA (giá) mà lỡ dính
1-2 NON, sleeve **âm EV**. Vì misclassification là rủi ro đã chứng minh (DGC/PNJ-2026), **không được
giả định p→1**. Đó là lý do bắt buộc cap cứng + user duyệt từng tên.

---

## 4. Đề xuất QUY TẮC production (đề xuất — KHÔNG tự wire, cần user duyệt phân bổ vốn cấp cao)

Sleeve **"discretionary calculated-fear special-situation"**, tách khỏi book V2.4 hệ thống:

1. **Trần tổng sleeve ≤ 3% NAV** cùng lúc (~54tr trên NAV 1,82 tỷ). Downside tối đa nếu *toàn bộ*
   sleeve hoá NON −70% = −2,1pp NAV; nếu thảm hoạ FLC toàn bộ = −3,0pp. Chấp nhận được như "bảo hiểm
   chi phí đã biết", không đe doạ NAV lõi.
2. **Cap/tên ≤ 1,0% NAV** cho QUALIFY rõ ràng (đã qua cổng xác nhận post-crisis); **≤ 0,5% NAV** cho
   AMBIGUOUS/tail-risk cao (audit/thanh khoản). TV1 = 0,5-1,0% (đúng nhóm này).
3. **Tối đa 2-3 tên cùng lúc** (N nhỏ, tránh giả vờ đa dạng hoá thứ không đa dạng hoá được).
4. **CHỈ mua case QUALIFY** qua đủ §2 playbook + **có xác nhận post-crisis "lõi còn tạo tiền"**
   (CF_OA≥NP so YoY sau quý bao trọn khủng hoảng). **KHÔNG mua AMBIGUOUS full** (DGC/PNJ-2026/OCH/TIS
   ở giữa — chỉ T1 thăm dò cận dưới cap nếu định giá cực rẻ, chờ cổng).
5. **Entry 3 tranche** (không bắt đáy), **exit 3 tầng + HARD ABANDON** khi scandal di cư sang pháp
   nhân/tài sản lõi (đúng §3 playbook). Horizon 2-3 năm.
6. **Vốn nguồn**: ngoài sizing V2.4 (dùng phần idle/off-book), không rút từ book BAL/LAG/custom30V.
7. **KHÔNG trích dẫn con số return như alpha đã kiểm chứng** — mọi báo cáo phải kèm cảnh báo §0.

---

## 5. TV1 nằm trong giới hạn không?

**CÓ — TV1 (0,5-1,0% NAV) nằm gọn trong trần đề xuất.** Ở cap sleeve 3% NAV, TV1 chiếm ~1/3 → còn dư
chỗ cho 1-2 tên. Lưu ý: TV1 thực ra là **asset-backed deep-value (SOTP)**, KHÁC bản chất "fear-buy tái
định giá PE" của PNJ/VEA — downside TV1 được che bởi **tài sản vật lý** (Sông Bung 5 dưới giá M&A), nên
rủi ro dạng −70%/−100% (NON) THẤP HƠN case fear thuần (trừ khi kịch bản đình chỉ giao dịch kiểu DGC xảy
ra → khi đó thanh khoản là rủi ro thật, không phải giá trị). ⇒ TV1 hợp lý ở cận trên cap tên (1,0%),
nhưng ràng buộc BINDING của TV1 là **thanh khoản (ADV ~1 tỷ/ngày)** chứ không phải trần sleeve.

---

## 6. Kết luận một câu cho user
Quy tắc **tồn tại được** (discriminator đúng hướng trên dữ liệu thật, sizing bounded), nhưng **"thu
hồi sau 2 năm" phụ thuộc gần như hoàn toàn vào việc có bắt được 1 case PNJ-like hay không** — nếu có,
sleeve 3% NAV có thể thêm ~+2-5pp NAV/chu kỳ; nếu chỉ toàn VEA-like khiêm tốn mà lỡ 1 NON, sleeve âm.
Vì thế: **triển khai như bảo hiểm/quyền chọn có kỷ luật (cap cứng, user duyệt từng tên), KHÔNG như
một book alpha đã kiểm chứng.** N=2 là scenario analysis, không phải backtest.

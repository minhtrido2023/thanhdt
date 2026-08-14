# Bảo hiểm rủi ro đuôi cho rổ ngân hàng — thiết kế

> Taylor (Quant/Algo), job `Taylor_20260814_025201`, 2026-08-14. **PAPER-ONLY — không wire production.**
> Rổ: 13 mã ACB BID CTG HDB LPB MBB MSB SHB TCB TPB VCB VIB VPB.
> Yêu cầu user: chống kịch bản bank run / mất thanh khoản / vỡ nợ ngân hàng, **false-positive phải rẻ**.

---

## 0. Kết luận một câu

Đề xuất gốc — *"cổng extreme bắt được giá sập → force sell market"* — **bị dữ liệu bác bỏ trên BA
trục độc lập**, không phải một trục. Nhưng mối lo phía sau nó **có thật và chưa được che**, và cơ
chế đúng để che nó **rẻ hơn nhiều** so với một cổng giá: rủi ro đuôi ngân hàng ở VN không đến qua
GIÁ, nó đến qua **BẰNG CHỨNG MẤT KHẢ NĂNG THANH TOÁN** — và bằng chứng đó là thông tin công khai,
rời rạc, đọc được bằng tin tức chứ không bằng chuỗi giá. Vì vậy đề xuất: **một lớp PHÁT HIỆN +
ESCALATE (Tầng 0/1), KHÔNG có tầng tự động bán.** Tầng hành động (Tầng 2) chỉ mở khi có bằng chứng
solvency, và ngay cả khi đó vẫn cần user duyệt — đó là câu hỏi CHÍNH SÁCH, không phải kỹ thuật (§7).

---

## 1. Phát hiện cấu trúc quyết định toàn bộ thiết kế

> **Ở Việt Nam, chưa từng có một vụ đổ vỡ ngân hàng nào được xử lý QUA THỊ TRƯỜNG CỔ PHIẾU NIÊM YẾT.**

Kiểm 6 vụ đổ vỡ thật (WebSearch + BQ):

| Ngân hàng đổ vỡ | Năm | Niêm yết lúc đổ vỡ? | Cổ đông nhận gì | Có trong BQ `ticker`? |
|---|---|---|---|---|
| **SCB** (Vạn Thịnh Phát) | 2022 | ❌ Không | Kiểm soát đặc biệt, cổ đông mất trắng | ❌ |
| **VNCB/Trustbank → CB** | 2015 | ❌ Không | Mua 0 đồng | ❌ |
| **OceanBank** | 2015 | ❌ Không | Mua 0 đồng | ❌ |
| **GPBank** | 2015 | ❌ Không | Mua 0 đồng | ❌ |
| **DongA Bank** | 2015 KSĐB | ❌ Không (OTC) | Kiểm soát đặc biệt | ❌ |
| **Habubank (HBB)** | 2012 | ✅ Có (HNX) | **Hoán đổi lấy cổ phiếu SHB**, không về 0 | ❌ (đã huỷ mã) |

Hai hệ quả trực tiếp, cả hai đều đổi bài toán:

1. **Cơ chế xử lý của VN là hành chính, không phải thị trường**: kiểm soát đặc biệt → chuyển giao
   bắt buộc 0 đồng → giao cho một ngân hàng mạnh gánh. Người gửi tiền được bảo toàn 100%. Phần bị
   xoá sổ là vốn chủ của các ngân hàng **tư nhân/OTC**, không phải của cổ đông niêm yết. Ca duy
   nhất có mã niêm yết (Habubank) kết thúc bằng **hoán đổi cổ phiếu**, không phải mất trắng.
2. **Rổ 13 mã của mình nằm ở phía NGƯỢC LẠI của giao dịch đó.** Đợt chuyển giao 2024-2025:
   CBBank→**VCB**, OceanBank→**MBB**, GPBank→**VPB**, DongABank→**HDB**. Bốn trong 13 mã đang giữ
   chính là **bên NHẬN**. Rủi ro đuôi thật của rổ này không phải "ngân hàng của mình sập" mà là
   (a) **lây lan drawdown** khi người khác sập, (b) **gánh nặng/pha loãng** khi bị giao một xác
   ngân hàng — một rủi ro âm ỉ nhiều năm, hoàn toàn không có hình dạng "giá sập 3 phiên".

Điều này không có nghĩa xác suất bằng 0 — nghĩa là **hình dạng của biến cố khác hẳn** cái mà một
cổng giá được thiết kế để bắt.

---

## 2. Ca thật gần nhất có dữ liệu giá: ACB 21/08/2012 (bầu Kiên) — bank run THẬT trên một mã niêm yết

Đây là ca duy nhất trong lịch sử VN có đủ cả ba yếu tố: mã đang niêm yết + người gửi tiền thật sự
rút tiền hàng loạt + có dữ liệu giá theo phiên. Đo trực tiếp trên BQ `tav2_bq.ticker`:

| Phiên | Close (adj) | Return | Volume | Volume / TB 1 tháng |
|---|---:|---:|---:|---:|
| 10/08 → 20/08 (7 phiên trước) | 3.100 → 3.120 | ~0% | 65k–194k | **0,42–1,15×** |
| **21/08** (công bố bắt) | 2.910 | **−6,73%** (sàn) | 904.600 | **4,41×** |
| **22/08** | 2.710 | **−6,87%** (sàn, O=H=L=C) | 688.900 | **2,93×** |
| **23/08** | 2.530 | **−6,64%** (sàn) | 260.600 | **1,23×** |
| 24/08 | 2.630 | **+3,95%** | 1.633.900 | 5,85× |
| 20/09 (đáy) | 1.860 | — | — | — |

Ba điều đọc được, mỗi điều phủ định một phần của đề xuất gốc:

**(a) Giá cho ZERO thời gian cảnh báo.** Bảy phiên trước biến cố: giá đi ngang, volume 0,42–1,15×
bình thường. Không có phân phối, không có rò rỉ, không có gì. Thông tin đến dưới dạng **một sự kiện
tin tức**, và giá gap ngay phiên đó. Một cổng dựa trên giá **về mặt cấu trúc luôn muộn ≥1 phiên** —
và phiên +1 tốn thêm **−6,87%**, phiên +2 thêm **−6,64%**. Nói cách khác: đúng như Mike đã nghi,
bảo hiểm thật phải nằm ở khâu PHÁT HIỆN, và khâu phát hiện **không có nguyên liệu giá để dùng**.

**(b) Nhưng "không bán được" là SAI.** ACB khớp **4,41× / 2,93× / 1,23×** volume bình thường trong
đúng 3 phiên sàn. Thanh khoản không biến mất — nó TĂNG. Mã giao dịch liên tục, không phiên nào bị
ngừng. (Cơ chế đình chỉ giao dịch ở VN được kích hoạt bởi **vi phạm công bố thông tin** — chậm nộp
BCTC kiểm toán — chứ không bởi giá sập hay khủng hoảng ngân hàng; đó là lý do TV1 bị xếp tail-risk
đình chỉ vì chuyện kiểm toán, không phải vì giá.) Vậy nên rào cản thật không phải "không bán được"
mà là **"bán được, nhưng bán ở giá sàn giữa cơn hoảng loạn"** — đó mới là chi phí phải định lượng,
và §3 định lượng nó.

**(c) NHNN là backstop, và nó đã hành động.** NHNN bơm hơn **18.000 tỷ** ra thị trường và cam kết
hỗ trợ thanh khoản ACB "bao nhiêu cũng có". ACB không mất khả năng thanh toán một ngày nào.

Đường đi sau đó của ACB — quan trọng cho việc hiệu chỉnh kỳ vọng, **không phải câu chuyện đẹp**:

| Mốc | vs giá trước biến cố |
|---|---:|
| +1 phiên | −6,7% |
| +2 phiên | −13,1% |
| +3 phiên | −18,9% |
| +1 tháng (đáy) | **−40,4%** |
| +3 tháng | −42,9% |
| +6 tháng | −32,7% |
| +2 năm | −35,3% |
| +5 năm | **+26,9%** |
| +7 năm | **+76,9%** |

ACB mất **3 năm** dưới nước. Đây là ca **bất lợi nhất** cho luận điểm "đừng bán" — bán ở phiên +2
(−18,9%) thật sự tốt hơn giữ trong suốt 3 năm. Nhưng nó vẫn không biện minh cho force-sell, vì
(i) cùng bộ luật đó sẽ bắn 4 lần khác trong 19 năm và cả 4 đều sai (§3), và (ii) ACB không hề mất
khả năng thanh toán — đúng loại "bán tháo hoảng loạn ở ngân hàng còn solvent" mà §5 phân loại là
KHÔNG được đối xử như giá-trị-hư-cấu.

---

## 3. Chi phí false-positive — ĐỊNH LƯỢNG (yêu cầu C)

Định nghĩa cổng theo đúng ý user: **"giảm sàn N phiên liên tiếp"**, proxy `return ≤ −6,5%`
(biên HOSE ±7%; ACB/SHB ở HNX ±7% trước 2013). Quét toàn lịch sử 2007→2026-08-13, 16 mã ngân hàng
(13 mã đang giữ + EIB, STB, NVB làm chứng).

### 3.1 Tần suất kích hoạt

| Số phiên sàn liên tiếp | Số lần xảy ra / 19 năm | Số mã dính |
|---|---:|---:|
| 1 phiên | **494** | 16 |
| 2 phiên | **46** | 14 |
| **3 phiên** | **4** | 4 |
| **7 phiên** | **1** | 1 |

Ngưỡng ≥3 phiên đúng là **rẻ về tần suất**: 5 lần trong 19 năm × 16 mã. User lo đúng ở chỗ này —
cổng KHÔNG ồn. Vấn đề nằm ở chỗ khác.

### 3.2 Toàn bộ 5 lần kích hoạt — và cả 5 đều SAI

| Mã | Cửa sổ | Số phiên | Sụt trong cửa sổ | Thực chất là gì | Ngân hàng có đổ vỡ? |
|---|---|---:|---:|---|---|
| **EIB** | 09→17/11/2022 | 7 | −39,5% | Cascade margin-call quanh tranh chấp sở hữu, hậu SCB | ❌ Không |
| **ACB** | 21→23/08/2012 | 3 | −18,9% | Bank run thật (bầu Kiên) — NHNN backstop | ❌ Không |
| **STB** | 12→16/05/2022 | 3 | −19,1% | Sập margin toàn thị trường 05/2022 | ❌ Không |
| **VIB** | 17→21/06/2022 | 3 | −18,9% | Bear 2022 toàn thị trường | ❌ Không |
| **TPB** | 07→11/10/2022 | 3 | −19,4% | Lây lan hoảng loạn SCB (run bắt đầu 06/10) | ❌ Không |

> **Precision của cổng giá cho mục đích đã tuyên bố = 0/5 = 0%. False-positive = 100%.**

Và 3/5 lần (STB, VIB, TPB) thậm chí **không phải sự kiện của ngân hàng đó** — là thị trường chung
sập, tức đúng phần việc DT5G đã làm rồi (§6).

### 3.3 Bán ở đó là bán ở đâu — lợi suất sau khi cổng bắn

Đo từ **phiên sàn cuối cùng** của mỗi cửa sổ (tức thời điểm sớm nhất một cổng ≥N phiên có thể ra
lệnh bán), bình quân trên toàn bộ các cửa sổ:

| Cổng | +1 tháng | +3 tháng | +6 tháng | **+12 tháng** | 12m tệ nhất |
|---|---:|---:|---:|---:|---:|
| ≥2 phiên sàn (46 lần) | +8,4% | +16,2% | +15,5% | **+41,4%** | −36,1% |
| ≥3 phiên sàn (4 lần) | +6,8% | +10,0% | +3,2% | **+24,2%** | −22,9% |
| 7 phiên (EIB 2022) | **+54,2%** | +33,4% | +28,8% | **+43,3%** | +43,3% |

**Không có ngoại lệ nào: bán vào cuối một chuỗi sàn ngân hàng VN là bán ở hoặc sát đáy.** Cổng ≥3
phiên trung bình bỏ lại **+24,2%** trong 12 tháng kế tiếp; ca EIB 7 phiên — chính là ca cực đoan
nhất lịch sử, đúng ca mà "bảo hiểm đuôi" được thiết kế để bắt — nảy **+54,2% chỉ trong 1 tháng**.

Đây là câu trả lời định lượng cho câu hỏi C: cơ chế này **không phải bảo hiểm giá rẻ**. Nó là một
luật **bán-đáy có hệ thống**, chi phí ~+24pp mỗi lần bắn, đổi lấy một lợi ích **chưa từng hiện thực
hoá lần nào** trong toàn bộ dữ liệu quan sát được.

### 3.4 Trục phân biệt rẻ nhất: hệ thống hay riêng lẻ

Phân bố số ngân hàng cùng sàn trong CÙNG một phiên (263 phiên có ≥1 mã sàn):

| Số mã cùng sàn 1 phiên | Số phiên |
|---|---:|
| 1 mã (riêng lẻ) | **190** (72%) |
| 2–5 mã | 40 |
| ≥6 mã (sập diện rộng) | **33** |

Chỉ cần đếm ngang — miễn phí, không cần dữ liệu mới — là tách được "cả ngành sập vì thị trường"
khỏi "một ngân hàng có chuyện". Trong 5 lần cổng ≥3 phiên bắn, **chỉ ACB 2012 và EIB 2022-11 là
đơn độc**; 3 lần còn lại nằm trong cụm diện rộng. Bộ lọc này phải nằm trong mọi thiết kế về sau.

---

## 4. Vậy tín hiệu cảnh báo sớm thật nằm ở đâu (yêu cầu B)

### 4.1 CASA/LDR — hữu ích, nhưng KHÔNG phải để bắt thời điểm

Dữ liệu vừa dựng hôm nay (`data/bank_casa_primary_20260814.csv`, 13/13 PASS, nguồn BCTC gốc):

| Mã | CASA strict % | | Mã | CASA strict % |
|---|---:|---|---|---:|
| TCB | 33,8 | | TPB | 18,3 |
| MBB | 33,6 | | VIB | 11,8 |
| VCB | 32,3 | | VPB | 11,5 |
| CTG | 22,7 | | HDB | 10,8 |
| MSB | 21,9 | | SHB | 7,8 |
| ACB | 21,4 | | LPB | 6,3 |
| BID | 20,1 | | | |

**Giới hạn cứng, phải nói thẳng:** dữ liệu này theo QUÝ và công bố **trễ ~45 ngày** sau ngày chốt
quý. Một bank run diễn ra trong **3 ngày** (ACB: 21→23/08). Về mặt số học, CASA/LDR **không thể**
là tín hiệu định thời cho biến cố cấp tính — trễ hơn biến cố khoảng một bậc độ lớn. Thêm nữa hiện
mới có **đúng 1 kỳ** (Q2/2026), chưa có chuỗi để nói "đột biến" nghĩa là gì (cần ≥8 quý; BCTC Q3
~cuối 10/2026 mới ra kỳ thứ hai).

Chỗ nó THẬT SỰ có giá trị là khác: **xếp hạng tổn thương thường trực**. CASA thấp = phụ thuộc vốn
huy động kỳ hạn nhạy giá = mong manh hơn khi căng thẳng thanh khoản; LDR cao = đệm mỏng. Đó là đầu
vào cho **sizing** (giữ nhẹ hơn ở mã mong manh) và cho việc **đọc một tin xấu nghiêm trọng đến đâu
khi nó đến**, chứ không phải một cái cò súng. Phân biệt này quan trọng: gắn cò vào dữ liệu trễ 45
ngày là tạo ra cảm giác an toàn giả.

### 4.2 Tín hiệu ĐÚNG hình dạng của biến cố: bằng chứng solvency, công khai, rời rạc

Xếp theo precision, đọc ngược từ 6 vụ đổ vỡ thật ở §1:

| # | Tín hiệu | Precision | Có lead time không |
|---|---|---|---|
| **S1** | **NHNN đưa vào kiểm soát đặc biệt / chuyển giao bắt buộc** | Gần như tuyệt đối | Muộn — nhưng là xác nhận cuối |
| **S2** | **Khởi tố cổ đông chi phối / chủ tịch vì hành vi CHẠM SỔ TÍN DỤNG** (cho vay sân sau, lập khống hồ sơ) | Rất cao | Có — SCB: bắt 08/10, KSĐB sau đó |
| **S3** | **Kiểm toán từ chối / ý kiến ngoại trừ về chất lượng tài sản** | Cao | Có — vài tháng |
| **S4** | Rút tiền hàng loạt tại quầy (tin/ảnh hàng người xếp) | Cao | Rất ngắn (giờ–ngày) |
| S5 | Đột biến CASA/LDR theo quý | Thấp đơn lẻ | Trễ 45 ngày ⇒ không định thời được |
| S6 | Giá sàn N phiên | **0% (§3.2)** | **Âm** (luôn muộn ≥1 phiên) |

S1–S4 đều là **tin tức**, và fleet **đã có sẵn hạ tầng đọc tin**: `anomaly_scan.py` +
`anomaly_gate.py` (cờ TTL 30 ngày) + `due_diligence.py` + `fearbuy_weekly_scan.sh` (cron thứ Sáu,
đã kết hợp anomaly + WebSearch tin khởi tố). Cái còn thiếu **không phải một cơ chế mới** — là một
**bộ từ khoá chuyên ngành ngân hàng** cho lớp đã chạy: *kiểm soát đặc biệt · chuyển giao bắt buộc ·
rút tiền hàng loạt · khởi tố chủ tịch/TGĐ ngân hàng · cho vay sân sau · thao túng · từ chối kiểm
toán*. Đó là lý do chi phí vận hành ≈ 0 (§8).

---

## 5. Hoà giải mâu thuẫn nguyên tắc (yêu cầu 2 của Mike) — bank run có phải "giá trị hư cấu"?

Hai nguyên tắc đã chốt phải được tôn trọng, không được lờ:
(a) *risk/reward = calculated, not avoidance* — cấm-cứng CHỈ áp cho **giá trị hư cấu**;
(b) custom30V *không stop-loss theo thiết kế* — sizing + rebalance CHÍNH LÀ risk control.

**Trả lời: KHÔNG — bank run tự nó KHÔNG phải giá trị hư cấu. Nhưng có một ca ngân hàng ĐÚNG LÀ giá
trị hư cấu, và nó không phải cái user đang mô tả.**

Tách hai thứ đang bị gộp làm một:

| | **Khủng hoảng THANH KHOẢN** (bank run ở ngân hàng còn solvent) | **VỐN CHỦ HƯ CẤU** (sổ tín dụng là bịa) |
|---|---|---|
| Bản chất | Lệch kỳ hạn tài sản/nguồn vốn — vấn đề vốn có của MỌI ngân hàng | Vốn chủ báo cáo **chưa từng tồn tại** |
| Giá trị going-concern | **Nguyên vẹn** — franchise, khách hàng, sổ vay còn đó | **Bị huỷ hoại thật**, và đã hỏng từ trước khi ai biết |
| Có backstop không | **Có** — NHNN bơm 18.000 tỷ cho ACB, "bao nhiêu cũng có" | Backstop cứu **người gửi tiền**, KHÔNG cứu cổ đông |
| Ca mẫu | **ACB 2012** | **SCB** (1.066.600 tỷ giải ngân cho sân sau bằng hồ sơ lập khống suốt 10 năm) |
| Kết cục cổ đông | Hồi phục (+76,9% sau 7 năm) | Mất trắng |
| Xử lý đúng | **Giữ / cân nhắc mua thêm** — đây chính là ca fear-buy | **Thoát**, không phải vì giá mà vì luận điểm đã chết |

Điểm mấu chốt: **khung QUALIFY/NON hiện có ĐÃ chứa ca này rồi, không cần khung mới.** Trong bảng
§1 của `calculated_fear_state_backstop.md`, **OGC là ca NON mẫu mực** với lý do ghi nguyên văn
*"lõi = gian lận ngân hàng"* — tức "scandal chạm lõi" áp cho một ngân hàng chính là **sổ tín dụng
bản thân nó là hành vi gian lận**. SCB là cùng một loài với OGC/FLC, không phải một loài mới.

Vậy nên:
- **Không cần mở rộng phạm vi cấm-cứng.** Nguyên tắc (a) giữ nguyên chữ và nghĩa: giá trị hư cấu
  bị cấm, biến động giá thì không. Cái cần thêm chỉ là **một đặc tả cho nhóm ngân hàng** trong §2
  của khung fear-buy — trả lời câu "scandal có chạm lõi không" bằng ngôn ngữ ngân hàng:
  *cáo buộc có nhắm vào chính SỔ TÍN DỤNG / vốn chủ báo cáo không, hay chỉ nhắm cá nhân?*
- **Không đụng nguyên tắc (b).** Cơ chế đề xuất **không phải stop-loss**: cò súng không bao giờ là
  giá. Giá chỉ được dùng làm biến xác nhận thứ cấp và làm đầu vào sizing. Một cơ chế kích hoạt bằng
  *"NHNN công bố kiểm soát đặc biệt"* khác về CHẤT với một cơ chế kích hoạt bằng *"giảm 24%"* — cái
  sau là đúng thứ user đã từ chối sau ca VIX 07-20, cái trước thì không.
- Và §3 vừa cho một lý do độc lập, thuần định lượng, để không làm stop-loss giá: nó **thua tiền**
  ở cả 5 lần bắn.

---

## 6. Vì sao phải là cơ chế RIÊNG, không dùng DT5G (yêu cầu 3)

DT5G (`macro_state_live.py`, qua `get_gated_state()`) là gate **CẤP THỊ TRƯỜNG**: nó đọc VNINDEX +
lãi suất SBV + US panic + breadth, và hành động duy nhất là **CAP trần trạng thái** cho toàn bộ phân
bổ. Nó **không thể** và **không nên** phân biệt "VPB có chuyện" với "thị trường đang xuống" — nó
không có đầu vào cấp mã nào cả.

Ngược chiều cũng đúng và quan trọng hơn: **một ngân hàng đơn lẻ đổ vỡ sẽ không làm DT5G nhúc
nhích.** Trong khi rổ ngân hàng là **37,4% MV active của SpaceX / 33,8% ZaloPay** (số đã đính chính
hôm nay bằng `openQuantity`, job `Taylor_20260814_021603`), tức rủi ro idiosyncratic tập trung ở đây
lớn hơn nhiều so với những gì một gate beta có thể che.

Hai cơ chế **trực giao** và nên giữ trực giao: DT5G quản beta; lớp mới quản bằng chứng solvency
từng mã. Nhưng §3.4 thêm một điều chỉnh làm giảm bớt tham vọng của lớp mới: **phần lớn các cú sập
giá của ngân hàng là hệ thống**, tức DT5G đã che phần lớn drawdown rồi. Cái còn lại cho lớp mới
đúng bằng phần **đơn độc** — và đó chính xác là lý do lớp mới nên **mỏng** (phát hiện + escalate),
không nên là một tầng thực thi.

---

## 7. Thiết kế đề xuất — 3 tầng, chỉ 2 tầng đầu là tự động (yêu cầu D)

### Tầng 0 — Xếp hạng tổn thương thường trực (quý, ~0 chi phí)
- **Đầu vào**: CASA/LDR (`bank_casa_primary_*.csv`), cập nhật mỗi khi có BCTC quý.
- **Đầu ra**: bảng xếp hạng mong manh, đi kèm báo cáo. **Không có cò súng.**
- **Dùng để**: đọc tin xấu nghiêm trọng đến đâu khi nó đến, và làm đầu vào sizing.
- ⚠️ Mới có 1 kỳ (Q2/2026) — **chưa dùng để so sánh xu hướng được**, cần ≥8 quý. Trước đó chỉ đọc
  theo lát cắt ngang.

### Tầng 1 — Phát hiện & escalate (ngày/tuần, ~0 chi phí biên) ← **phần đáng làm nhất**
- **Cò súng**: bất kỳ tín hiệu **S1–S4** (§4.2) chạm 1 trong 13 mã.
- **Cơ chế**: mở rộng bộ từ khoá ngân hàng cho `fearbuy_weekly_scan.sh` + `anomaly_scan.py` đang
  chạy. Ghi cờ vào `anomaly_flags.json` (TTL 30 ngày, cơ chế sẵn có).
- **Hành động**: **CẢNH BÁO + escalate user/Mike. TUYỆT ĐỐI không tự bán.** Giống hệt cách
  `due_diligence.py` đang xử lý ca PNJ/DGC — thuần thông tin, không chặn, không đổi sizing.
- **Kèm theo, miễn phí**: cờ "đơn độc hay cụm" (§3.4) để người đọc biết ngay đây là chuyện của mã
  này hay của cả thị trường.

### Tầng 2 — Cân nhắc hành động (rất hiếm; **KHÔNG tự động**)
- **Điều kiện mở**: **≥2 tín hiệu ĐỘC LẬP** trong đó **bắt buộc có ≥1 tín hiệu solvency (S1/S2/S3)**.
  Giá **không được tính là một tín hiệu** — §3 đã cho thấy nó đóng góp 0% precision. Giá chỉ dùng
  để chọn cách thực thi.
- **Nếu mở**: escalate user với đầy đủ bằng chứng + đề xuất **bán một phần** (không toàn bộ), **lệnh
  limit bám giá rải nhiều phiên** (không market order — ACB 2012 cho thấy vẫn khớp được, nhưng khớp
  ở sàn), và neo vào bài kiểm §5: *cáo buộc chạm sổ tín dụng, hay chỉ chạm cá nhân?*
- **Cần user duyệt trước khi đặt lệnh thật.** Đây là **quyết định CHÍNH SÁCH, không phải kỹ thuật**
  — tôi không tự chốt. Câu hỏi cho user ở §9.

**Cái CỐ Ý không có trong thiết kế**: không có tầng nào tự bán. Đó không phải sự thận trọng chung
chung — đó là kết luận trực tiếp từ §3.3 (cổng giá thua ~+24pp mỗi lần bắn, 5/5 lần) và §1 (biến cố
thật chưa từng đi qua cửa giá).

---

## 8. Chi phí vận hành (yêu cầu E)

| Hạng mục | Chi phí | Ghi chú |
|---|---|---|
| **Cron mới** | **0** | Bám vào `fearbuy_weekly_scan.sh` (thứ Sáu 08:10) đã chạy |
| WebSearch | +~13 truy vấn/tuần | Gộp vào lượt quét fear-buy sẵn có |
| BQ | ~0 | Trục breadth §3.4 tính từ dữ liệu giá đã cache |
| CASA/LDR | 1 lần/quý, thủ công | Nút thắt là OCR BCTC (chưa tự động hoá) |

Đúng nguyên tắc user nêu: **không dựng thêm một checker chạy liên tục cho một biến cố xác suất cực
thấp.** Tần suất tuần là phù hợp với S1–S3 (diễn ra theo tuần/tháng). S4 (hàng người rút tiền) nhanh
hơn tuần — nhưng §2 đã chứng minh kể cả biết trong ngày cũng chỉ tiết kiệm được ~6,7%, trong khi
nguy cơ bán nhầm là toàn bộ +24pp hồi phục. Không đáng đánh đổi để chạy hàng ngày.

---

## 9. Cần user quyết (chính sách, không phải kỹ thuật)

1. **Tầng 2 có được phép tự động hoá không, hay luôn dừng ở escalate?** Khuyến nghị của tôi: **luôn
   dừng ở escalate** — trên toàn bộ dữ liệu quan sát được, chưa có lần nào tự động sẽ đúng.
2. **Nếu một ngày Tầng 2 mở thật, bán bao nhiêu?** Một phần (đề xuất: 1/3–1/2) hay toàn bộ.
3. Có muốn tôi dựng **Tầng 1** (mở rộng từ khoá ngân hàng cho lớp quét sẵn có) không — đây là phần
   rẻ nhất và giá trị nhất, và là phần duy nhất tôi khuyến nghị làm ngay.

---

## 10. Giới hạn của nghiên cứu này

- **N = 1** cho bank run trên mã niêm yết (ACB 2012). Mọi phát biểu về "lead time" và "thanh khoản
  còn hay không" đứng trên đúng một quan sát. Không thể có thêm — đó là toàn bộ lịch sử.
- **Sống sót có chọn lọc là THẬT nhưng đi ĐÚNG CHIỀU với kết luận**: các ngân hàng đổ vỡ vắng mặt
  khỏi BQ vì chưa từng niêm yết (§1) — nên bảng §3.3 (5/5 hồi phục) *quá lạc quan* nếu dùng để nói
  "ngân hàng luôn hồi phục". Nó **không** quá lạc quan cho mục đích đang dùng: đo xem một cổng giá
  áp lên **rổ đang giữ** sẽ tốn gì. Với rổ niêm yết, tập mẫu là đầy đủ.
- Cổng `≤ −6,5%` là proxy cho "sàn"; HNX ±10% sau 2013 và UPCOM ±15% không được mô hình đúng. Không
  ảnh hưởng kết luận (13 mã đang giữ đều ở HOSE ±7%), nhưng đừng tái dùng ngưỡng này cho mã sàn khác.
- Chưa đo: kịch bản **gánh nặng bên nhận chuyển giao** (§1 hệ quả 2) — VCB/MBB/VPB/HDB đang gánh 4
  ngân hàng 0 đồng. Đây là rủi ro đuôi hình dạng khác hẳn (âm ỉ nhiều năm, không có cú sập) và
  **chưa được nghiên cứu này che**. Đề xuất là một job riêng.

# Plan "tâm hành vi" cho thị trường Việt Nam — tâm tham chiếu + lực kéo (job Taylor_20261125_104308)

Taylor · 2026-11-25 · CHỈ NGHIÊN CỨU + THIẾT KẾ. Không sửa `dcf_valuation.py`, không wire, không email.
**Chưa qua quant-skeptic — không phải CONFIRMED.** Pilot khoá trước ở `PRELOCK_PILOT.md` (commit `3597bc9e2`, trước khi chạy).
Mọi con số dưới đây đo trong phiên này: `out/pilot_results.json`, `out/pilot_table.md`, `out/log_p4.txt`, `out/cases.csv`.
Pilot không đo NAV ⇒ chưa có phí/pin; G1 dùng TC 0,1%/chiều và pin0% (đầu sàn).

## 0. Kết luận trước

1. **Ý tưởng "tâm giá hành vi gần giá thị trường 1–2 năm hơn DCF" đúng một nửa, và nửa đúng là hiển nhiên.** Sai số tuyệt đối log
   trung vị ở 12 tháng (IS / OOS): tâm nội tại 0,489 / 0,476; tâm tham chiếu hành vi 0,268 / 0,271; **giá hôm nay 0,240 / 0,271**.
   Tâm hành vi gần giá tương lai hơn tâm nội tại gần gấp đôi — nhưng **không gần hơn chính giá hôm nay**. Nó gần vì nó bám giá,
   không phải vì nó dự báo được mức giá. ⇒ **Không nên hiển thị một "giá kỳ vọng 12/24 tháng" như một con số mức giá.**
2. **Phép thử chính của pilot: tín hiệu YẾU** (theo luật khoá trước). Thêm hai neo (đỉnh 52 tuần, giá vốn đám đông) vào mô hình đã
   có đà, đảo chiều, E/P và tâm nội tại: ΔIC 12 tháng **+0,017 [−0,090; +0,099]** (IS), **+0,055 [−0,038; +0,128]** (OOS) — dương cả
   hai era, CI đều chứa 0. Kỹ năng sai số tương đối tăng từ 0,05% lên 0,25% (IS) và 0,54% lên 1,45% (OOS) — tức mô hình tốt nhất
   cũng chỉ giảm sai số dự báo lợi suất tương đối **khoảng 1%** so với "không dự báo gì".
3. **So với null E/P: không hơn.** IC 12 tháng OOS của mô hình đầy đủ 0,173, của E/P đơn 0,174 (hiệu −0,001 [−0,068; +0,051]);
   IS 0,105 so 0,049 (hiệu +0,056 [−0,044; +0,146]).
4. **Cái đáng giữ là phần "lực kéo" dạng bốn ô, chưa phải bằng chứng** (mô tả, không phải phép thử quyết định của pilot). Lợi suất
   tương đối 12 tháng (log, IS / OOS): rẻ + hành vi cao **+0,074 [+0,033; +0,118] / +0,113 [+0,090; +0,136]**; rẻ + hành vi thấp
   −0,010 [−0,056; +0,033] / +0,019 [−0,032; +0,081]; đắt + hành vi cao +0,002 [−0,024; +0,029] / −0,034 [−0,098; +0,015];
   đắt + hành vi thấp **−0,066 [−0,119; −0,013] / −0,093 [−0,112; −0,072]**. Đọc: *rẻ chỉ được trả tiền khi thị trường đã bắt đầu
   thừa nhận; đắt chỉ bị phạt khi neo đã gãy.* Ở 24 tháng hình dạng giữ nguyên (rẻ + thấp +0,022 / −0,001; đắt + cao −0,058 / −0,032,
   CI chứa 0).
5. **Khuyến nghị:** làm tiếp **G1 hẹp** (một phép thử chính không tham số: tâm nội tại × đỉnh 52 tuần, đối chứng E/P × đỉnh 52 tuần),
   KHÔNG làm bản "vườn đặc trưng" đầy đủ. Xác suất chủ quan của tôi để G1 vượt cả E/P × đỉnh 52 tuần lẫn DSR ≥ 0,95 là thấp
   (ước lượng, không đo) — nếu user chỉ muốn làm khi triển vọng cao thì dừng ở đây là quyết định hợp lý.

## 1. Kết quả pilot G0 (đầy đủ: `out/pilot_table.md`)

Mẫu: in-universe có đủ đặc trưng, 55.622 / 58.686 dòng. h = 12: IS 16.921 dòng, 545 mã, 60 tháng as-of trong 5 năm; OOS (hệ số đóng
băng tại 2019-12, ước lượng trên 72 tháng 2013-01→2018-12) 29.502 dòng, 699 mã, 70 tháng trong 6 năm. CI = bootstrap khối năm, B = 2000.

| Mô hình (đặc trưng) | IC12 IS | IC12 OOS | IC24 IS | IC24 OOS |
|---|---|---|---|---|
| B1 đà + đảo chiều 1 tháng | +0,102 [+0,030; +0,172] | −0,012 [−0,078; +0,049] | −0,011 | −0,013 |
| B2 E/P | +0,049 [+0,010; +0,085] | +0,174 [+0,101; +0,236] | +0,097 | +0,230 |
| B3 tâm nội tại (`lv_ENS2`) | +0,022 [−0,024; +0,073] | +0,175 [+0,097; +0,263] | +0,100 | +0,183 |
| B4 lớp 2 (premium lịch sử của mã) | −0,037 [−0,081; +0,010] | **−0,123 [−0,164; −0,078]** | +0,095 | +0,155 |
| F0 = B1 + B2 + B3 | +0,089 [+0,039; +0,136] | +0,119 [+0,042; +0,194] | +0,089 | +0,172 |
| **F = F0 + đỉnh 52 tuần + giá vốn đám đông** | +0,105 [+0,026; +0,193] | +0,173 [+0,105; +0,236] | +0,096 | +0,245 |
| A = tâm nội tại + hai neo | +0,106 [+0,023; +0,195] | +0,168 [+0,106; +0,223] | +0,117 | +0,226 |

- **ΔIC(F − F0)** h=12: +0,017 [−0,090; +0,099] / +0,055 [−0,038; +0,128]; h=24: +0,007 [−0,128; +0,110] / +0,074 [−0,014; +0,151].
- Đúng chiều tương đối (tercile trên/dưới) của F: 54,7% / 58,1% (h=12), 54,1% / 62,6% (h=24); của E/P đơn: 52,0% / 59,0% và 55,6% / 62,7%.
- Theo phía, ΔIC(F − F0) h=12: trong tercile rẻ +0,033 [−0,089; +0,127] (IS), **+0,110 [+0,058; +0,161]** (OOS); trong tercile đắt
  −0,048 [−0,196; +0,054] (IS), +0,092 [+0,002; +0,178] (OOS). Neo giúp nhiều hơn ở phía RẺ, và chỉ chắc ở OOS.
- Hệ số đóng băng của F (h=12, trên hạng [−0,5; +0,5]): đà −0,021 · đảo chiều −0,029 · E/P +0,038 · tâm nội tại +0,133 · **đỉnh 52 tuần
  +0,313** · giá vốn đám đông +0,030. Khi có đỉnh 52 tuần, đà và giá vốn đám đông gần như không còn gì — khớp George–Hwang.
- Sai số tuyệt đối log trung bình h=12: IS — giá hôm nay 0,331, F 0,354 (tệ hơn, do cộng trôi thị trường ước lượng sai); OOS — 0,393
  so 0,388 (tốt hơn 1,2%).
- Độ nhạy nhãn mã ngừng giao dịch (mất 0% / 50% / 99%): ΔIC12 IS +0,019 / +0,017 / +0,013; OOS +0,055 / +0,055 / +0,051.
- Tự kiểm `calc/p3_selfcheck.py`: 17/17 PASS, ba môi trường (`env -u TZ`, `America/New_York`, `Asia/Ho_Chi_Minh`; ba PYTHONHASHSEED)
  cùng md5 `6058632c7e15c7c189b3b4061511cf95` — gồm tính lại đặc trưng 4 mã bằng vòng lặp thuần, kiểm cắt dữ liệu (PIT), tính lại
  ΔIC bằng scipy và tính lại hệ số đóng băng độc lập.

**Ba điều bất lợi phải nói thẳng**
1. **Cụm đà không ổn định giữa hai era:** B1 từ +0,102 (IS) xuống −0,012 (OOS). Đỉnh 52 tuần cùng họ với đà (tương quan hạng 0,45);
   việc nó "cứu" OOS có thể không lặp lại. Chưa đo đỉnh 52 tuần đứng một mình (để dành cho G1, khai trước).
2. **F0 đóng băng thua E/P đơn ở OOS** (−0,056 [−0,090; −0,020]): hệ số học trên 2013–2018 (đà dương) phá kết quả 2020+. Đây là bằng
   chứng trực tiếp rằng ước lượng hệ số trên 6 năm là mong manh ⇒ G1 đề xuất bản KHÔNG ước lượng hệ số.
3. **Dữ liệu 2015–2025 đã bị nhìn.** Mọi thứ tinh chỉnh tiếp trên cùng giai đoạn là bán-ngoài-mẫu.

**Ca kiểm (`out/cases.csv`; giá điều chỉnh, VND):**

| Ca | Giá | Tâm nội tại | Dự báo tương đối 12T (F) | Thực tế tương đối 12T | Giá thực 12T sau | Đọc |
|---|---|---|---|---|---|---|
| VNM 2015-06 | 31.100 | 22.440 | −0,088 | +0,439 | 48.910 | **Sai chiều**: F nghiêng theo "đắt"; mã sát đỉnh (hi52 −0,009) vẫn vượt trội — đúng kiểu "đắt-còn neo" |
| VNM 2015-12 | 43.770 | 20.536 | −0,098 | +0,245 | 53.520 | **Sai chiều**, như trên |
| VNM 2017-12 | 91.970 | 28.434 | +0,060 | −0,126 | 65.400 | **Sai chiều**: tại đỉnh (hi52 0,000) F chuyển sang dương đúng lúc giá nguội |
| VCS 2015-06 | 4.840 | 3.696 | +0,037 | +1,400 | 19.910 | Đúng chiều, độ lớn thiếu ~40 lần; tâm nội tại nhìn lùi quá thấp (đổi cấu trúc) |
| VCS 2015-12 | 11.120 | 4.973 | +0,020 | +0,975 | 28.210 | như trên |
| DGC 2016-06 | 9.050 | 8.974 | +0,089 | −0,464 | 5.750 | **Sai chiều**: sát đỉnh, giá hợp lý ⇒ dự báo vượt trội, thực tế kém xa |
| DGC 2016-12 | 7.360 | 9.275 | −0,033 | −0,408 | 5.820 | Đúng chiều ("rẻ-chưa thừa nhận" tiếp tục kém 12 tháng; 24 tháng +0,191) |
| HPG 2019-06 | 7.230 | 9.479 | −0,033 | +0,243 | 8.240 | **Sai chiều**: "rẻ-chưa thừa nhận" nhưng hồi ngay |
| HPG 2019-12 | 7.230 | 9.733 | +0,065 | +0,474 | 15.560 | Đúng chiều, thiếu độ lớn |

Trong 9 ca khoá trước: **4 đúng chiều, 5 sai chiều**. Riêng VNM, dự báo điểm của F sai cả ba mốc: nó kéo theo "đắt" khi giá còn
chạy (2015) và chuyển sang dương đúng đỉnh (2017-12). Ở các ca đúng chiều, độ lớn dự báo nhỏ hơn thực tế nhiều lần. Ca nổi tiếng
không phải mẫu đại diện (IC trung bình vẫn dương), nhưng chúng cho thấy rõ: mô hình xếp hạng được trên số đông, **không định được
mức và không bắt được điểm gãy neo ở từng mã**.

## 2. Phản biện cấu trúc ba con số của Mike

| Đề xuất | Phán xét sau pilot | Sửa |
|---|---|---|
| (1) Tâm nội tại mù giá | Giữ nguyên | Không đổi; vẫn là ENS2/D0 của V3.x |
| (2) Tâm tham chiếu = **giá** kỳ vọng 12/24 tháng từ hồi quy | **Bỏ dạng mức giá.** Sai số mức không hơn giá hôm nay; hồi quy 6 hệ số trên ~6 năm độc lập lật dấu giữa hai era | Thay bằng **điểm thừa nhận** (hạng 0–100 theo khoảng cách tới đỉnh 52 tuần, không ước lượng hệ số) + kỳ vọng lợi suất TƯƠNG ĐỐI theo tercile, không phải giá |
| (3) Lực kéo = tâm nội tại − tâm tham chiếu (một hiệu số) | Hiệu số gộp hai trục thành một ⇒ mất đúng thông tin có giá trị (rẻ+cao khác hẳn rẻ+thấp dù "lực kéo" có thể bằng nhau) | **Bốn ô** (nội tại rẻ/đắt × thừa nhận cao/thấp), không trừ |
| Đo bằng kỹ năng dự báo vs RW / đà / E/P | Đúng, và pilot đã đo: thắng đà (OOS), hoà E/P, ≈ RW về mức | Thêm đối chứng thứ tư bắt buộc: **E/P × đỉnh 52 tuần** — đối chứng khó nhất |

## 3. Đặc tả mô hình đề xuất (bản G1)

**Điểm.** Trong từng tháng, trên universe PIT: `v` = hạng phần trăm của `lv_ENS2` (log tâm nội tại / vốn hoá, mù giá);
`a` = hạng phần trăm của `hi52` = log(giá điều chỉnh / đỉnh 252 phiên). **Số tham số ước lượng: 0.**
**Bốn ô** theo trung vị tháng của `v` và `a`:

| | Thừa nhận cao (gần đỉnh 52 tuần) | Thừa nhận thấp (xa đỉnh) |
|---|---|---|
| **Nội tại rẻ** | RẺ-ĐƯỢC THỪA NHẬN — vùng mua có xác nhận | RẺ-CHƯA THỪA NHẬN — chờ; pilot: 12 và 24 tháng ≈ 0 |
| **Nội tại đắt** | ĐẮT-CÒN NEO (kiểu VNM 2015) — không mở mới, CHƯA phải tín hiệu bán | ĐẮT-ĐANG NGUỘI — phía bị phạt rõ nhất |

**Thứ tự thêm đặc trưng** (mỗi bậc một phép thử, dừng ở bậc đầu tiên không đạt): giá vốn đám đông → phạt chú ý (số phiên biến động
≥ 6,5%) → phạt xổ số (MAX) → hệ số ước lượng cuốn chiếu có ridge → khối ngoại (chỉ OOS). Chi tiết và ngưỡng: `PRELOCK_PROPOSED.md`.
**Nếu sau này vẫn muốn bản hồi quy:** ŷ = Σ β_k·hạng_k, tối đa 4 hệ số, ridge, ước lượng cuốn chiếu trên các tháng có nhãn đã đóng
(tháng s + h ≤ t), đóng băng ở mốc OOS; số quan sát độc lập phải tính theo NĂM (6), không theo dòng (16.921).
**Ngoại lai trần/sàn:** mọi đặc trưng vào mô hình dưới dạng hạng trong tháng; nhãn winsor 1/99 khi ước lượng; chuỗi trần/sàn chỉ là
đặc trưng đếm, không dùng lợi suất ngày thô.
**Hiển thị:** tâm nội tại + vùng (như V3) · ô hiện tại · điểm `a` · kỳ vọng tương đối 12 tháng của ô kèm CI và số năm mẫu ·
nhãn "dùng giá quá khứ" cho mọi thứ thuộc trục thừa nhận. Độ tin cậy hạ một bậc khi: thiếu < 250 phiên giá, thanh khoản dưới sàn,
tâm nội tại có `n_ENS2` thấp.
**Đổi cấu trúc (kiểu VCS 2015):** ô ĐẮT-CÒN NEO + tăng trưởng lợi nhuận 12 tháng vượt ngưỡng ⇒ gắn cờ "kiểm tra đổi cấu trúc — tâm nội
tại nhìn lùi có thể thấp" thay vì cảnh báo đắt. Ngưỡng chưa đặt; phải khoá trước ở G1 (đã biết từ J3/J4: dự báo lợi nhuận không vượt
naive, nên cờ này chỉ là nhắc người đọc, không sửa tâm).
**Vốn hoá nhỏ / thanh khoản thấp:** đỉnh 52 tuần của mã ít khớp lệnh là giá cũ ⇒ chỉ tính `a` khi mã trong `universe_pit`; ngoài
universe hiển thị "không đủ thanh khoản để đọc hành vi".
**Ngân hàng:** tâm nội tại theo route BANK sẵn có; trục thừa nhận không phụ thuộc ngành. Xếp hạng `v` trong nhóm ngân hàng riêng
(3.085 dòng-tháng route BANK trong panel) vì bội số không so được với phi tài chính — phải kiểm ở G1, chưa đo.

## 4. Đối chiếu với lớp 2 (premium lịch sử của mã)

Lớp 2 đã là một neo, nhưng là **neo đảo chiều chậm**: IC 12 tháng của nó ÂM (−0,037 IS; −0,123 [−0,164; −0,078] OOS) và chỉ dương ở
24 tháng (+0,095 / +0,155). Lý do đo được: hạng lớp 2 tương quan −0,43 với đà — mã "rẻ so với chính nó" phần lớn là mã vừa rớt.
Trục thừa nhận bổ sung đúng cái lớp 2 thiếu: **chiều và thời điểm trong 12 tháng** (ΔIC12 F − lớp 2: +0,142 [+0,043; +0,242] IS,
+0,296 [+0,226; +0,370] OOS). Nhưng so với thứ đang dùng thật (E/P + tâm nội tại), phần thêm là **nhỏ và chưa chắc** (mục 0.2–0.3).
Nói thẳng: mô hình hành vi không tạo ra một "tâm" tốt hơn; nó thêm một **trục thời điểm** mà lớp 2 đọc ngược.

## 5. Tạo giá trị đầu tư và rủi ro làm mờ

- **Vùng mua:** chỉ coi "rẻ" là vùng mua khi ở ô RẺ-ĐƯỢC THỪA NHẬN; ô RẺ-CHƯA THỪA NHẬN ≈ 0 trong 12 và 24 tháng ở cả hai era ⇒ đưa
  vào danh sách theo dõi, không giải ngân. Đây là chỗ có giá trị rõ nhất cho sleeve discretionary.
- **Cảnh báo đắt:** tách "đắt-còn neo" (không mở mới; giữ được) khỏi "đắt-đang nguội" (phía bị phạt: −0,066 / −0,093). Trả lời đúng
  ca VNM 2015: cảnh báo đắt đúng nhưng sớm.
- **Thời điểm:** theo dõi chuyển ô (RẺ-CHƯA → RẺ-ĐƯỢC; ĐẮT-CÒN NEO → ĐẮT-ĐANG NGUỘI). Độ trễ chưa đo — mục (f) của PRELOCK đề xuất.
- **Sizing:** KHÔNG đề xuất. Chưa có NAV, chưa qua DSR; V3.1 đã cho thấy ở sàn 5 tỷ E/P thắng mô hình.
- **Rủi ro làm mờ:** (i) trục thừa nhận dùng giá ⇒ đặt cạnh tâm mù giá dễ bị đọc như một tâm thứ hai — bắt buộc nhãn "dùng giá quá
  khứ" và không quy ra giá; (ii) "rẻ-chưa thừa nhận" có thể khiến bỏ lỡ đáy (HPG 2019-06 sai chiều) — nó là bộ lọc thời điểm, không
  phải phán quyết giá trị; (iii) "đắt-còn neo" có thể bị đọc thành giấy phép mua đuổi — hiển thị cố định "không mở mới";
  (iv) trùng với sổ BAL (momentum) của production ⇒ không cộng thêm rủi ro đà vào danh mục qua cửa này.

## 6. Giai đoạn và cổng duyệt (công sức là ƯỚC LƯỢNG, chưa đo)

| Giai đoạn | Làm gì | Cổng | Công sức (ước lượng) |
|---|---|---|---|
| **G0 — xong** | Kiểm kê dữ liệu, pilot, 4 tài liệu | Mike chạy quant-skeptic 1 vòng cho PLAN + PRELOCK_PROPOSED + pilot | job này |
| **G1 — backtest hẹp** | Khoá `PRELOCK_PROPOSED.md` (sau góp ý skeptic) → Q0 so N1–N4, mẫu giữ lại 2009–2012, bốn ô, NAV qua `e_bt2.py`, DSR/PBO | User duyệt chạy; dừng theo NO-GO §5 | 1 job Taylor cỡ job V3 (ước lượng ≤ 200 lượt), chạy máy vài phút mỗi bước |
| G1b — dữ liệu (chỉ khi G1 đạt (a)) | Winston dựng bảng mã–sàn theo ngày; kéo khối ngoại + room VNDirect 2018-08+ vào cache nghiên cứu | User duyệt vì thêm nguồn ngoài | 1 job Winston (ước lượng); API không hợp đồng |
| **G2 — skeptic** | quant-skeptic đúng 1 vòng trên kết quả G1 | CONFIRMED mới sang G3 | 1 vòng |
| **G3 — hiển thị DD** | Thêm khối "ô + điểm thừa nhận" vào báo cáo DD, nhãn "dùng giá quá khứ"; không sizing, không luật lệnh | User duyệt mẫu hiển thị | 1 job nhỏ |
| Song song, rẻ | Theo dõi về sau: ghi ô hàng tháng từ 2026-11, đọc khi nhãn 12 tháng đóng (2027-11) | User duyệt đăng ký paper program | 1 script + 1 dòng registry |

## 7. Quyết định cần user duyệt
1. **Đổi định nghĩa sản phẩm:** bỏ "giá kỳ vọng 12/24 tháng" dạng mức giá; thay bằng điểm thừa nhận + bốn ô. (Khuyến nghị: đồng ý.)
2. **Chạy G1 hẹp hay dừng?** (Khuyến nghị: chạy, vì rẻ và tái dùng khung; chấp nhận trước khả năng kết luận "E/P × đỉnh 52 tuần là đủ".)
3. **Theo dõi về sau từ 2026-11** — bằng chứng sạch duy nhất. (Khuyến nghị: có.)
4. **G1b dữ liệu sàn PIT / khối ngoại** — chỉ khi G1 đạt (a). (Khuyến nghị: hoãn.)

## 8. Giới hạn
- 5–6 năm as-of độc lập mỗi era; tháng liền kề chồng lấn 11/12. CI khối năm rộng; một năm cá biệt (2021–2022) có thể quyết định OOS.
- Giá vốn đám đông dùng tổng số CP thay free-float; 4,4% dòng-ngày dùng số CP lấp ngược.
- Không có sàn PIT, margin, lệnh cá nhân theo mã, khối ngoại trước 2018-08 ⇒ các hiệu ứng "đặc thù VN" nhất chưa thử được.
- Bốn ô ở mục 0.4 dùng "thành phần hành vi" của mô hình F (đà, đảo chiều, đỉnh 52 tuần, giá vốn — hệ số ước lượng), KHÁC bản Q0 không
  tham số đề xuất cho G1 ⇒ số bốn ô của G1 có thể khác.
- Panel VNDirect (mã vắng BQ) không tái lập từ repo; đối chiếu GDKHQ còn mở từ V3.1.
- Tổng quan học thuật viết từ trí nhớ, chưa đối chiếu bản gốc (`LITERATURE.md` có nhãn mức chắc).

## 9. Tái lập
```
cd agents/Taylor/research/dcf_vn_behavioral_20261125/calc     # nhánh session/Taylor_20261125_104308
PY=/home/trido/thanhdt/wc_venv/bin/python                      # đọc panel V3.1 ở wt-dcf-v3-20261125 (V3_DIR đổi được)
$PY p1_features.py && $PY p2_pilot.py && LABEL=h0 TAG=_h0 $PY p2_pilot.py && LABEL=h100 TAG=_h100 $PY p2_pilot.py
$PY p4_cases.py && env -u TZ $PY p3_selfcheck.py
```
`out/*.parquet` không vào git (.gitignore); md5 đầu vào + đầu ra ở `MD5SUMS`.

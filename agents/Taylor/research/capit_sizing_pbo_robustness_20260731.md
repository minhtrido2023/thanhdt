# CAPIT sizing — robustness-check PBO ⇒ **DỪNG, KHÔNG IMPLEMENT**

Job `Taylor_20260731_151958` (re-dispatch của `_121454` chết trắng tay). Nối tiếp
`research/capit_sizing_wire_gate_20260731.md` (job `_111654`, verdict quant-skeptic
CONFIRMED/medium `logs/verify_20260731_115105.log`).

**Kết luận một dòng:** 2 việc robustness-check reviewer yêu cầu **đã kích hoạt đúng điều kiện dừng
mà dispatch đặt ra**. PBO không ổn định theo đặc tả (**0,073 → 0,814** trên các đặc tả đều hợp lệ),
và dưới chính đặc tả reviewer yêu cầu (episode-stratified) nó **đảo chiều** con số 0,732 mà lập luận
wire đang dựa vào. Tôi **không implement, không sửa production**. Việc chọn công thức cuối trả về
Mike/user với bằng chứng mới dưới đây.

Script tái lập: `mike/agents/Taylor/job_20260731_151958_{pbo_episode,pbo_event15,diag}.py`
Log: `..._{pbo_episode,pbo_event15,diag}.log`
Nguồn: 13 audit CSV `data/v23_golive_audit_2014_now_*_exp_capsz_*_univpit.csv` (T=3106 phiên,
2014-01-03 → 2026-06-19), **không chạy lại backtest** — cùng nguồn/quy ước với job `_111654`.

---

## VIỆC 1 — PBO episode-stratified

### 1.1 Cách chia "1 fold/sự kiện" theo run khác-baseline: KHÔNG làm được (và vì sao)

Thử đầu tiên chia theo run mà các leg lệch khỏi baseline `cash`. Kết quả đo được: **90,3% số phiên
(2805/3106) có ít nhất 1 leg lệch**, và 15 sự kiện gộp lại chỉ còn **5 run** (dài 30–1284 phiên).

Lý do cơ học: một khi arm CAPIT đã làm NAV lệch, chênh lệch đó **không bao giờ trở về 0** — nó
mang sang mọi phiên sau. Nên "khoảng không có sự kiện" không tồn tại theo nghĩa này.

→ PBO theo 5 run: **0,600** (cả 2 biến thể lịch/active), bootstrap 20.000 lần: **0,597**.

### 1.2 Phản chứng tiền đề của reviewer: **0/16 khối rỗng**, không phải 4/16

Reviewer nêu "4/16 khối rỗng không có sự kiện CAPIT" làm lý do cho việc 1. Đo trực tiếp trên chính
dữ liệu: số khối **không chứa phiên lệch nào** = **0/8, 0/16, 0/32**. Tiền đề đó không đúng theo
nghĩa "khối không bị sự kiện tác động" (đúng nếu hiểu là "khối không chứa NGÀY FIRE" — nhưng khối
vẫn chịu tác động của sự kiện trước đó, nên nó không rỗng về mặt thống kê).

### 1.3 Cách chia ĐÚNG nghĩa — neo vào 15 ngày fire thật

Neo fold vào `record_type=EVENT_CAPIT` + cửa sổ nắm giữ thật của từng sự kiện (từ TX `CAPIT*_E<id>`;
mọi sự kiện đều đúng **63 phiên** ≈ 3 tháng — horizon cố định của arm). 18 bản ghi EVENT_CAPIT, **3
bị loại vì không có TX** (E1 2015-05-18 size=0,75 nhưng không triển khai; E9/E11 size=0) ⇒ **15 sự
kiện**, 945 phiên-khối (874 phiên riêng biệt = 28,1% timeline).

| đặc tả | PBO | median OOS-rank của IS-best |
|---|---|---|
| **CSCV đầy đủ trên 15 sự kiện** (C(15,7)=6435) | **0,0726** | **13,0/13** |
| **bootstrap 20.000 lần chia đôi 15 sự kiện** | **0,0736** | **13,0/13** |

**Đây là đảo chiều hoàn toàn so với 0,732.** Median OOS-rank = 13/13 nghĩa là: config thắng IS **cũng
là config tốt nhất OOS gần như mọi lần chia**. Leg thắng IS: `idle` **82,2%**, `cash` 8,7%.

---

## VIỆC 2 — độ nhạy PBO theo độ chi tiết khối lịch

| S | độ dài khối | số khối rỗng | số tổ hợp | **PBO** | median OOS-rank |
|---|---|---|---|---|---|
| 8 | 388 phiên | 0/8 | 70 | **0,8143** | 5,5/13 |
| **16 (gốc)** | 194 phiên | 0/16 | 12.870 | **0,7319** | 5,0/13 |
| 32 | 97 phiên | 0/32 | 40.000 *(lấy mẫu từ 601.080.390)* | **0,7360** | 5,0/13 |

*(S=32 lấy mẫu ngẫu nhiên không lặp 40.000 tổ hợp — C(32,16)≈601 triệu không khả thi liệt kê. CSCV
lấy trung bình trên các tổ hợp nên đây là ước lượng không chệch.)*

Trong **họ đặc tả lịch**, PBO ổn định vừa phải: 0,73–0,81, luôn ≥ 0,5. **Nhưng** chuyển sang đặc tả
neo-sự-kiện thì rơi xuống 0,07.

### 2.1 Toàn cảnh — PBO là con số KHÔNG ỔN ĐỊNH

| đặc tả (đều hợp lệ) | PBO |
|---|---|
| calendar S=8 | 0,814 |
| calendar S=32 | 0,736 |
| **calendar S=16 (con số wire-gate đang trích)** | **0,732** |
| episode-run (5 run khác-baseline) | 0,600 |
| **event-anchored, 15 sự kiện thật** | **0,073** |

Biên độ **0,07 – 0,81** phủ toàn bộ dải quyết định và **cắt ngang ngưỡng 0,5 theo cả hai chiều**.

---

## VIỆC 3 (tự thêm) — chẩn đoán: PBO=0,073 là tín hiệu thật hay hiện vật của mẫu?

Giả thuyết cần bác: mẫu 15 sự kiện không có washout thất bại sâu nào ⇒ leg phơi nhiễm lớn nhất thắng
ở mọi cách chia một cách tầm thường ⇒ PBO ≈ 0 mà không chứng minh được gì.

**3.1 Dấu kết quả từng sự kiện** — 13/15 cửa sổ dương, chỉ 2 âm (E6 2020-02 −5,4%; E17 2026-03
−9,2%). Objection gốc của reviewer **vẫn nguyên**: mẫu không chứa washout thất bại sâu.
Nhưng theo nghĩa **tương đối**, mẫu KHÔNG đơn điệu: `idle` (phơi nhiễm lớn nhất) **thua `cash` ở
5/15 sự kiện**.

**3.2 Phơi nhiễm KHÔNG giải thích được xếp hạng** — Spearman(Sharpe cửa sổ sự kiện, phơi nhiễm) =
**−0,121** (≈ 0). `booknav` có phơi nhiễm hạng 2 nhưng Sharpe hạng 10; `cash` phơi nhiễm hạng 13
nhưng Sharpe hạng 4. ⇒ **PBO thấp KHÔNG phải hiện vật "càng to càng thắng"**. Đây là điểm tôi định
dùng để bác con số 0,073 — và nó **không bác được**.

**3.3 Nhưng PBO=0,073 do vài sự kiện gánh** — leave-best-out (bỏ dần các sự kiện đóng góp CAPIT
dương lớn nhất):

| bỏ k sự kiện | PBO | leg thắng IS nhiều nhất | n còn lại |
|---|---|---|---|
| 0 | **0,073** | `idle` 82,2% | 15 |
| 1 | 0,145 | `idle` 70,1% | 14 |
| 2 | 0,240 | `idle` 48,5% | 13 |
| **3** | **0,327** | **`cash`** 41,1% | 12 |
| 4 | 0,195 | `cash` 60,4% | 11 |
| 5 | 0,064 | `cash` 77,8% | 10 |

Bỏ 3 sự kiện thì PBO lên 0,327 **và leg thắng IS đổi từ `idle` sang `cash`**. Đúng mẫu hình
"1-2 sự kiện gánh hết edge = reshuffle-luck" mà §Quy chuẩn 5 bắt phải kiểm bằng leave-one-out.

⇒ **Kết luận chẩn đoán: PBO=0,073 không phải hiện vật phơi nhiễm, nhưng cũng không bền** — nó mỏng
theo đúng chiều mà chuẩn multiple-testing của đội cảnh báo. **Không đặc tả nào trong 5 đặc tả đủ tư
cách làm con số chuẩn tắc.**

---

## 4. HỆ QUẢ CHO QUYẾT ĐỊNH WIRE — vì sao tôi DỪNG

Lập luận wire ở `capit_sizing_wire_gate_20260731.md` §5.2 đứng trên 3 trụ:

| trụ | trạng thái sau job này |
|---|---|
| **(a) tính xác định** (sàn 6,25% / trần 25% NAV) | **NGUYÊN VẸN** — đây là thuộc tính thiết kế, không phải suy luận thống kê |
| **(b) tốt hơn `booknav` ĐANG LIVE** | **NGUYÊN VẸN ở toàn mẫu** (Calmar 1,56 vs 1,52 · MaxDD −17,5 vs −18,0% · IS 22,90 vs 22,37% · stress S3 −7,16 vs −7,64%) — **nhưng có 1 dữ kiện ngược mới**, xem §4.1 |
| **(c) PBO 0,73 ≥ 0,5 ⇒ CẤM chọn theo thứ hạng backtest** | **SỤP** — không thể khẳng định PBO ≥ 0,5 nữa (0,07 ở đặc tả reviewer yêu cầu), cũng không thể khẳng định < 0,5 (calendar 0,73–0,81; leave-best-out 0,33) |

Trụ (c) không chỉ mất — nó là trụ **chống đỡ 2 kết luận loại trừ** của job trước:
1. Lý do **bác `idle`** ("là leg hay thắng IS nhất, biên +0,02 Calmar là ảo") — dưới đặc tả
   neo-sự-kiện thì `idle` thắng IS 82% **và cũng đứng nhất OOS** (median rank 13/13, SR cửa sổ sự
   kiện 2,48 cao nhất họ). Lý do bác nó **không còn an toàn**.
2. Lý do **bác `navsize:0.40`** — tương tự.

### 4.1 Dữ kiện ngược mới với trụ (b)

Xếp hạng Sharpe **chỉ trong cửa sổ 15 sự kiện** (nơi công thức sizing thực sự có tác dụng):

| hạng | leg | SR |
|---|---|---|
| 1 | `idle` | 2,4801 |
| 4 | `cash` (spec pin R3) | 2,3857 |
| **10** | **`booknav` (ĐANG LIVE)** | **2,2851** |
| **11** | **`navsize:0.25` (đề xuất)** | **2,2721** |
| 13 | `navsize:0.15` | 2,2153 |

`navsize:0.25` xếp **dưới** `booknav` đang live — ngược với toàn mẫu (1,8259 vs 1,8159, 0,25 ở trên).

⚠️ **Đọc đúng độ lớn:** chênh 0,013 SR trên 945 quan sát — **nằm gọn trong nhiễu**. Việc này
**KHÔNG** chứng minh `booknav` tốt hơn `navsize:0.25`; nó chỉ phá vỡ khẳng định "`navsize:0.25` tốt
hơn live ở MỌI chỉ tiêu", vì có ít nhất một cách cắt dữ liệu hợp lệ cho kết quả ngược.

### 4.2 Điều kiện dừng của dispatch đã được kích hoạt

> *"Nếu 2 việc robustness-check ở bước 1-2 làm PBO tụt xuống mức khiến kết luận định tính KHÔNG còn
> đứng vững (vd navsize:0,25 không còn rõ ràng tốt hơn) — DỪNG LẠI, KHÔNG implement, báo rõ lý do."*

Cả hai vế đều xảy ra: PBO tụt 0,732 → **0,073** dưới đúng đặc tả được yêu cầu, và `navsize:0.25`
**không còn rõ ràng tốt hơn** (hạng 11/13 cửa sổ sự kiện, dưới cả công thức đang live).
⇒ **Không implement. Không sửa `golive_recommend_v23.py`, không sửa `trading_rules.json`, không sửa
`kb/current_ops.md`.** CAPIT tiếp tục chạy `booknav` như hiện tại; 5 mã đang giữ thật
(SAB/SIP/VNM/PVT/NCT) **không bị đụng tới**.

---

## 5. CÁI GÌ CÒN ĐỨNG VỮNG (để Mike/user quyết)

Không phải mọi thứ đổ. Sau khi bỏ hoàn toàn mọi lập luận dựa vào PBO, còn lại **2 căn cứ độc lập**:

1. **Stress washout sâu (§Việc 4 job trước)** — độ rộng giữa các công thức nở ×8,4 ở kịch bản S3
   (0,46pp → 3,86pp). `idle` là leg **TỆ NHẤT** (−10,65%), `cash` áp chót (−10,51%),
   `navsize:0.25` −7,16%, `booknav` −7,64%. Lập luận này **không dùng PBO** ⇒ không bị job này
   động tới. Nó vẫn là căn cứ mạnh nhất để **không** chọn `idle`, kể cả khi `idle` thắng mọi xếp
   hạng lịch sử — vì nó thắng ở đúng vùng mẫu không có thất bại nào.
2. **Tính xác định** — `booknav`/`cash`/`idle` đều để quy mô vị thế phụ thuộc "tiền tình cờ có
   trong sổ", dao động 0,7% → 35% NAV giữa các sự kiện **ở cùng mức tin cậy tín hiệu**. Đây là
   khuyết tật thiết kế, không phải kết luận thống kê.

**Ba lựa chọn cho user (tôi không tự chọn):**

| | phương án | căn cứ | rủi ro |
|---|---|---|---|
| **A** | **Giữ nguyên `booknav`** (không đổi gì) | bằng chứng chưa đủ để đổi một cơ chế đang giữ tiền thật; mọi chênh lệch đo được đều trong nhiễu | giữ nguyên khuyết tật "quy mô phụ thuộc tiền tình cờ có" |
| **B** | Wire `navsize:0.25` như đề xuất cũ | (a) xác định + (1) cắt đuôi stress tốt nhất trong các leg thực tế | lập luận PBO đã mất; hạng 11/13 ở cửa sổ sự kiện |
| **C** | Chờ thêm bằng chứng | n=15 và **0 washout thất bại sâu** là ràng buộc thật, không sửa được bằng thống kê | mỗi sự kiện mới mất ~1 năm để tích lũy |

**Khuyến nghị của tôi (nêu rõ đây là ý kiến, không phải kết quả đo): A hoặc B, không C.**
C không thực tế — với tần suất ~1,2 sự kiện/năm, cần ~10 năm mới đủ mẫu phân biệt. Giữa A và B,
điểm khác biệt thật duy nhất còn đo được là **hành vi dưới đuôi chưa quan sát**, nơi `navsize:0.25`
tốt hơn `booknav` 0,48pp (S3) — nhỏ, nhưng là hướng duy nhất bằng chứng còn chỉ, và không mâu thuẫn
với bất kỳ đo lường nào khác ngoài chênh 0,013 SR trong nhiễu. **Nếu user muốn đổi thì B vẫn hợp lệ
— nhưng phải trình đúng là "đổi vì thiết kế xác định + phòng thủ đuôi", tuyệt đối KHÔNG trình kèm
PBO như một cổng đã qua.**

---

## 6. Giới hạn của chính job này

- 5 đặc tả PBO đều hợp lệ về mặt phương pháp; tôi **không có căn cứ khách quan để tuyên bố cái nào
  là chuẩn tắc**. Việc chọn đặc tả sau khi đã thấy kết quả chính là một dạng chọn-lọc — nên tôi báo
  cáo **toàn bộ dải**, không chọn hộ.
- Cửa sổ sự kiện chồng lấn nhẹ (945 phiên-khối vs 874 phiên riêng biệt — E4/E5 và E6/E7 gần nhau);
  ảnh hưởng nhỏ nhưng khác 0.
- 3/18 EVENT_CAPIT bị loại vì không có TX. E1 (2015-05-18, size 0,75, không triển khai) chính là
  ca "gần như bỏ lỡ tín hiệu" mà trụ (a) muốn chữa — nó **không nằm** trong bất kỳ tính toán PBO
  nào ở đây, nên lợi ích của việc có SÀN sizing không được đo trong mọi con số trên.
- Không đụng backtest: mọi số đọc từ 13 audit CSV đã pin của job `_111654`.

# BƯỚC 2 — H5: proxy sinh thái retail (AMH G4) + ứng viên điều kiện margin Loại-2

> Job `Taylor_20260926_164143` · PAPER-ONLY · prereg: `PREREG.md` §2 (viết TRƯỚC khi chạy)
> Artifact: `h5_series.py`, `h5_ic.py`, `h5_ic_mt.py`, `h5_capit.py`,
> `h5_retail_daily.csv`, `h5_retail_monthly.csv`, `h5_daily_ic.csv`, `h5_ic_verdict.csv`

## KẾT LUẬN

| Phần | Kết quả |
|---|---|
| **A. Biến điều kiện cho IC** (§2.3) | **KHÔNG ĐỦ BẰNG CHỨNG** — 4/4 so sánh trượt bộ 3 tiêu chí prereg. Cell mạnh nhất (retail × momentum) có OOS p_boot 0,0185 nhưng **p_BH = 0,074** và IS không đơn điệu với **N=4 tháng** ở ô HIGH. |
| **B. Điều kiện 3 margin Loại-2** (§2.4) | **FAIL DỨT KHOÁT** — bỏ lỡ hoàn toàn 2020-03, và **8/10 cực trị là giả** (trần prereg ≤2). |
| **C. Giá trị thật duy nhất** | Chuỗi **ghi nhận được một thay đổi sinh thái CÓ THẬT** mà AMH G4 nói là "không có nguồn": tỷ trọng retail 0,397 (2017) → **0,251 (2026)**, giảm gần liên tục. Đây là **tư liệu mô tả**, không phải cổng. |
| **Mua gói FiinPro?** | **KHÔNG** — H5 không đạt điều kiện §4 đề xuất ("H5 cho kết quả điều kiện hoá có ý nghĩa qua quant-skeptic"). Không mở lại câu hỏi mua. |

**Phát hiện cơ chế đáng giá nhất của bước này** — và nó phủ định chính giả thuyết:

> **Ở Việt Nam, nhà đầu tư cá nhân là người MUA đáy, không phải người đầu hàng ở đáy.**
> COVID 2020-02-15→04-15: cá nhân **mua ròng +6.347 tỷ** (z min **+1,08** — đầu kia của thang).
> Bán tháo 2018-04-09→07-31: cá nhân **mua ròng +8.822 tỷ** (z min +0,02).
> Chỉ 2022 ngược lại: 10-11/2022 cá nhân **bán ròng −13.722 tỷ** (z min −3,89).
> ⇒ "retail capitulation" không phải dấu hiệu đáy chung ở VN; nó xảy ra **1/3 lần sụt lớn**.
> Giả thuyết nhân quả cho ngoại lệ 2022 (chưa kiểm chứng, KHÔNG dùng làm luật): 2022 là lần duy
> nhất margin retail ở mức kỷ lục bị force-sell, tức cá nhân bị **ép** bán chứ không **chọn** bán.

---

## 0. Pre-flight (Step 0) — NO-GO ở CẢ HAI quy tắc đếm N

```
per-episode, N=127 tháng, 8 trial, trần 10,4 năm  → NO-GO. DSR=0,4378; trần DSR 0,4334
per-day,     N=2.550 phiên, 8 trial, trần 10,4 năm → NO-GO. DSR=0,4260; trần DSR 0,4329
```
Trần 10,4 năm là **cứng**: nguồn chết 28/09/2026, không có nối tiếp. Không đợi thêm được.

*Lưu ý trung thực về công cụ:* `rnd_preflight_power.py` đóng khung theo Sharpe của một chiến
lược; H5 không phải chiến lược mà là **biến điều kiện**, nên đây là **ước lượng thay thế**, không
phải phép tính đúng cho thống kê IC-difference. Vẫn chạy như prereg vì nó trả lời đúng câu hỏi
vận hành: cửa sổ 10,4 năm này **không đủ để wire bất cứ thứ gì**. Tiêu chí PASS thật của H5 là bộ
3 ở §2.3 (yếu hơn, và cũng không đạt).

## 1. Dựng chuỗi — bẫy registry đã áp đủ

| Quy tắc prereg | Thực hiện |
|---|---|
| Chỉ từ 2016-04 (đủ 5 nhóm) | 3.165 → 2.603 dòng |
| Loại `provisional` 2026-09-03→09-14 | ✔ |
| Loại đoạn tự doanh trống 2022-03-03→05-16 | **50 dòng** |
| Loại ngày thoả thuận lớn `\|foreign_deal_net_bn\| ≥ 1.000` tỷ (bẫy #3: phía bán lô thoả thuận bị gán cho cá nhân) | **67 dòng** — gồm đúng 2018-05-18 (Vinhomes) |
| Mẫu số `Σ\|5 nhóm\|` là THƯỚC ĐO QUY MÔ, không phải tổng đại số (bẫy #1: 5 nhóm không cộng về 0) | ✔, không suy nhóm nào bằng phần dư |
| Không cộng `local_institutional` + `proprietary` (bẫy #2) | ✔ |

Còn **2.484 phiên sạch** (2016-04-01 → 2026-08-28), **123 tháng**.

### `retail_net_share_m` — trung bình năm

| 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0,355 | **0,397** | 0,309 | 0,324 | 0,290 | 0,336 | 0,341 | 0,328 | 0,320 | 0,263 | **0,251** |

Đỉnh 2017, đáy 2026, xu hướng giảm rõ ở 2 năm cuối. **Đây chính là thứ AMH G4 ghi là "không có
nguồn chuỗi nào"** — nay có, và nó cho thấy sinh thái ĐÃ đổi thật.

## 2. (A) Biến điều kiện cho IC — 4/4 KHÔNG ĐỦ BẰNG CHỨNG

Panel: 1.044.145 dòng, 755 mã, **chỉ thành viên `universe_pit` PIT** (không dùng danh sách toàn
lịch sử — tránh §9b). `mom_200` và forward-return 21 phiên dùng `Close` đã điều chỉnh (đúng vai
trò RETURN theo §9); value = `1/PE`. Trục 2 mặc định = breadth-tercile PIT đúng quy ước 08-22
(`%mã Close>MA200`, phân loại bằng `breadth_{t-1}`, tercile theo phân vị rolling 252).
Tercile retail dùng **giá trị tháng TRƯỚC** (bắt buộc PIT — tháng M tính từ chính ngày trong M).

### IC trung bình theo tercile

| | | LOW | MID | HIGH | HIGH−LOW |
|---|---|---|---|---|---|
| **RETAIL** IS 2016-04..2019-12 | IC mom | 0,0416 | −0,0296 | 0,2082 | **+0,1666** |
| | IC ey | 0,0256 | 0,0300 | −0,1183 | −0,1439 |
| **RETAIL** OOS 2020-01..2026-08 | IC mom | −0,0276 | 0,0015 | 0,0597 | **+0,0873** |
| | IC ey | 0,0863 | 0,0580 | 0,0527 | −0,0336 |
| **BREADTH** IS | IC mom | 0,0531 | 0,0786 | 0,0898 | +0,0367 |
| | IC ey | 0,0387 | −0,0141 | −0,0391 | −0,0777 |
| **BREADTH** OOS | IC mom | 0,0050 | 0,0320 | −0,0335 | −0,0385 |
| | IC ey | 0,0628 | 0,0877 | 0,0654 | +0,0025 |

### Phán theo bộ 3 tiêu chí prereg §2.3 (phải đạt CẢ BA)

| Trục | Nhân tố | (i) cùng dấu IS&OOS | (ii) CI OOS loại 0 | (iii) đơn điệu IS/OOS | p_boot OOS | **p_BH (4 so sánh)** | Phán |
|---|---|---|---|---|---|---|---|
| retail | mom | ✔ | ✔ | ✘ / ✔ | 0,0185 | **0,074** | KHÔNG ĐỦ |
| retail | ey | ✔ | ✘ | ✘ / ✔ | 0,142 | 0,284 | KHÔNG ĐỦ |
| breadth | mom | ✘ | ✘ | ✔ / ✘ | 0,367 | 0,489 | KHÔNG ĐỦ |
| breadth | ey | ✘ | ✘ | ✔ / ✘ | 0,917 | 0,917 | KHÔNG ĐỦ |

Bootstrap khối theo **THÁNG** (B=4.000, resample tháng có hoàn lại, mỗi tháng mang TẤT CẢ ngày
của nó) — đúng chuẩn cluster-robust của skill §4, không dùng "một ngày ngẫu nhiên mỗi tháng".

### Vì sao số IS đẹp mà không tin được

Phân vị rolling 24 tháng cần warm-up 24 tháng ⇒ **ăn mất 24/45 tháng của IS**. Số tháng độc lập
còn lại mỗi ô IS: LOW **11**, MID **6**, HIGH **4**. `IC mom = +0,2082` của ô HIGH là trung bình
của **4 tháng**. Bootstrap trả p=0,0000 vì nó lấy mẫu lại đúng 4 tháng đó — bootstrap không tạo
được thông tin không có trong dữ liệu. **Không trích con số IS này ra khỏi ngữ cảnh.**

Đây tự nó là một kết luận thiết kế: **cửa sổ 10,4 năm không đủ cho một biến điều kiện theo THÁNG
có tách IS/OOS.** Không phải lỗi thực thi, là trần dữ liệu.

### Phát hiện phụ (không nằm trong câu hỏi, nhưng phải báo)

**Trục 2 mặc định — breadth-tercile PIT — cũng trượt cả 4 tiêu chí trên panel/cửa sổ này**, và
tệ hơn retail ở mọi ô: `ic_mom` **đảo dấu** giữa IS (+0,0367) và OOS (−0,0385); `ic_ey` từ
−0,0777 (IS, p_BH 0,006) về +0,0025 (OOS, p 0,917). Nói cách khác: retail_net_share **phân tách
IC momentum TỐT HƠN trục mặc định** trong cửa sổ này — nhưng "tốt hơn một trục cũng không phân
tách được" không phải bằng chứng ủng hộ. Ghi lại vì nó đặt câu hỏi về chính quy ước 08-22, độc
lập với FiinPro. **Không đề xuất đổi quy ước dựa trên một cửa sổ và một panel.**

**Không test hướng** — ecology làm tín hiệu hướng đã REFUTED 2026-07-13, prereg cấm test lại.

## 3. (B) `retail_capitulation` làm điều kiện 3 của mandate margin Loại-2 — **FAIL**

z-score 20 phiên của dòng tiền cá nhân ròng, 2017-01→2026-08 (2.291 ngày), debounce 60 ngày lịch.
"Cực trị giả" = sự kiện z≤−2 KHÔNG nằm trong ±1 tháng của một đáy (VNINDEX ≥20% dưới đỉnh 1 năm).

| Ngưỡng | Sự kiện | **Cực trị GIẢ** | Trần prereg | Bắt 2020-03? | Bắt 2022-10/11? |
|---|---|---|---|---|---|
| z ≤ −2,0 | 10 | **8** | ≤2 | **KHÔNG** (z min +1,08) | CÓ (z min −3,89) |
| z ≤ −2,5 | 5 | **4** | ≤2 | **KHÔNG** | CÓ |

Prereg đòi bắt được **CẢ HAI** và ≤2 cực trị giả. Trượt cả hai vế.

Sự kiện z≤−2,0 đầy đủ: 2017-04, 2017-11→2018-02, 2019-04, 2019-09, 2019-12, 2022-01, 2022-08,
**2022-11→12** (z −4,08, gần đáy), 2024-01, 2025-07. Cực trị sâu nhất của cả chuỗi (2022-12-02)
rơi vào lúc thị trường **đã hồi** khỏi đáy 2022-11-16 — cá nhân bán vào đợt hồi, không phải đầu
hàng ở đáy.

**Vì sao thất bại này là thông tin hữu ích, không phải kết quả rỗng:** nó nói mandate margin
Loại-2 **không nên** tìm điều kiện 3 ở phía retail-selling. Cơ chế VN ngược với trực giác nhập
từ thị trường Mỹ. Nếu muốn một chỉ báo overreaction thứ 3 bên cạnh VIX/breadth, hướng đáng thử
là **đo lực ÉP bán** (dư nợ margin, force-sell) chứ không phải dòng tiền ròng cá nhân — và dữ
liệu đó không nằm trong bộ này.

## 4. N thật

- IC: **123 tháng** tổng, nhưng N quyết định là **số tháng độc lập MỖI Ô** — IS 4/6/11,
  OOS 24/19/35. KHÔNG phải 2.484 phiên, KHÔNG phải 1,04 triệu dòng panel.
- Capitulation: **10 sự kiện** (z≤−2,0) / **5** (z≤−2,5), debounce 60 ngày lịch — không phải
  119/57 ngày fire.
- Trial khai báo: 8 (2 nhân tố × 2 trục × 2 kỳ). BH áp trong mỗi kỳ trên 4 so sánh.

## 5. Ràng buộc nguồn — nói thẳng như prereg §2.5 yêu cầu

Bộ E **không có nguồn nối tiếp sau 28/09/2026**; đây là bộ duy nhất trong repo có dòng tiền
cá nhân/tổ chức/tự doanh. Theo §4 đề xuất, điều kiện mở lại câu hỏi mua gói rẻ nhất là "H5 cho
kết quả điều kiện hoá có ý nghĩa qua quant-skeptic". **Điều kiện đó KHÔNG đạt** ⇒ khuyến nghị
**không mua** giữ nguyên, và H5 không còn là lý do treo câu hỏi đó nữa.

## 6. Đề xuất

1. **Đóng G4 của `amh-adaptivity-review-20260910.md`** theo hướng: nguồn chuỗi retail nay đã có
   và đã đo; nó **không dùng được làm biến điều kiện hay cổng**, nhưng **có** ghi nhận được
   thay đổi sinh thái (0,397→0,251). Ghi kết quả này vào G4 thay vì để "chưa có nguồn".
2. Lưu 2 chuỗi (`h5_retail_daily.csv`, `h5_retail_monthly.csv`) + entry `kb/data_registry/`
   trước 28/09, ghi rõ `upstream: FiinPro-X trial ENDED 2026-09-28, NO refresh`, status
   **DERIVED / DESCRIPTIVE-ONLY — đã test làm biến điều kiện và KHÔNG ĐẠT**, để phiên sau không
   test lại cùng một thứ.
3. **Không** dispatch quant-skeptic (§15: bắt buộc khi đề xuất ĐỔI production — đây là "không
   đổi gì"). Nếu Mike/user muốn một cặp mắt đối kháng lên **phát hiện phụ** ở §2 (trục breadth
   08-22 cũng không phân tách) thì đó là một câu hỏi RIÊNG, không phải H5.
4. **Không mua gói FiinPro.**
5. Đưa cơ chế "cá nhân VN mua đáy 2018/2020, chỉ bán 2022 (force-sell margin)" vào KB như một
   **giả thuyết cơ chế có dữ liệu ủng hộ nhưng chưa kiểm chứng** — hữu ích khi ai đó lại định
   nhập trực giác "retail capitulation = đáy" từ thị trường Mỹ.

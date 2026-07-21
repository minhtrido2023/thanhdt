# Beta bất đối xứng theo regime thị trường — hướng thăm dò

> Job `Taylor_20260721_112050` (Việc 3), 2026-07-21. **Trạng thái: THĂM DÒ — chưa kết luận final,
> chưa qua quant-skeptic, KHÔNG đề xuất wire vào bất cứ thứ gì sống (V2.4 / DT5G / sizing).**
> Script: `mike/agents/Taylor/asym_beta_regime.py` · Dữ liệu: `research/data_asym_beta.csv` (1.228 mã)

## 0. Câu hỏi

Giả thuyết user: cổ phiếu **thiên hướng đầu cơ** (beta cao / biến động cao / turnover cao) **giảm
mạnh hơn tỷ lệ** khi thị trường xấu so với mức tăng tương ứng khi thị trường tốt — tức beta **không
đối xứng** qua regime, trái với giả định hằng số của CAPM.

Câu hỏi tách làm 2 phần, và **kết quả của 2 phần khác nhau rõ rệt** — đây là điểm quan trọng nhất
của tài liệu này:

| # | Mệnh đề | Kết quả |
|---|---|---|
| **A** | Beta khi thị trường xuống **cao hơn** beta khi thị trường lên | ✅ **XÁC NHẬN, ổn định IS lẫn OOS** |
| **B** | Mức bất đối xứng **tập trung ở nhóm đầu cơ/beta cao** | ⚠️ **CHƯA CHỨNG MINH ĐƯỢC** — chỉ thấy ở lens không walk-forward được |

## 1. Thiết kế

- **Nhãn regime**: `tav2_bq.vnindex_5state_dt5g_live` — **đúng bảng production**, không dùng bare
  `vnindex_5state` (base v3.4b, bẫy dữ liệu đã biết, `data_registry.md`).
  `1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL` → **DOWN={1,2}**, **NEUTRAL={3}**, **UP={4,5}**.
- **Lens 1 (regime)**: mỗi mã 1 hồi quy GỘP có dummy regime, **cả hệ số chặn lẫn độ dốc**:
  `r = a_D·1D + a_N·1N + a_U·1U + b_D·(1D·m) + b_N·(1N·m) + b_U·(1U·m) + e`
  → sai số chuẩn của `asym = b_D − b_U` lấy từ **chính ma trận hiệp phương sai** của hồi quy đó
  (không ghép 2 hồi quy rời rồi trừ tay).
- **Lens 2 (đối chiếu, Ang–Chen–Xing 2006)**: downside beta theo **dấu return thị trường**
  (tuần `m<0` vs `m>0`), **không dùng nhãn regime** → kiểm tra chéo độc lập.
- Return tuần W-FRI, 2014-01 → 2026-07. Tối thiểu 40 tuần DOWN / 40 UP / 60 NEUTRAL mỗi mã.

## 2. Kết quả

### 2.1 Beta trung bình theo regime (toàn bộ 1.228 mã)

| | beta_DOWN | beta_NEUTRAL | beta_UP | asym = D − U |
|---|---|---|---|---|
| toàn bộ (n=1228) | 0.550 | **0.338** | 0.464 | **+0.086** (t=+7.11, 57% mã >0) |
| chỉ mã thanh khoản tốt (status=OK, n=249) | 1.136 | **0.735** | 0.963 | **+0.174** (t=+6.86, 67% mã >0) |

> ⚠️ **Beta NEUTRAL thấp nhất** — thấp hơn cả UP lẫn DOWN. Đây KHÔNG phải bất đối xứng, mà là hiện
> tượng **tương quan tăng khi thị trường biến động mạnh** (correlation → 1 ở cả 2 đuôi). Phải tách
> hiệu ứng này ra, nếu không sẽ đọc nhầm thành "beta cao khi thị trường xấu".

### 2.2 Kiểm soát thanh khoản (attenuation bias)

Mối lo chính: mã giao dịch thưa phản ứng trễ → beta bị kéo xuống (Dimson 1979); nếu mức thiên lệch
này khác nhau giữa các regime thì sẽ tạo ra bất đối xứng GIẢ. Kết quả — **asym sống qua kiểm soát**:

| Nhóm | n | beta_D | beta_N | beta_U | asym | t |
|---|---|---|---|---|---|---|
| Toàn bộ | 1228 | 0.550 | 0.338 | 0.464 | +0.086 | +7.11 |
| Trong `ticker_prune` | 293 | 1.024 | 0.690 | 0.906 | +0.118 | +5.48 |
| ADV ≥ 2 tỷ | 203 | 1.061 | 0.744 | 0.958 | +0.104 | +3.99 |
| **ADV ≥ 10 tỷ** | 122 | 1.136 | 0.864 | 1.066 | **+0.070** | **+2.09** |

Attenuation là THẬT (mọi beta tăng đều khi lọc thanh khoản), nhưng **asym vẫn dương và có ý nghĩa ở
nhóm thanh khoản nhất** — tuy yếu dần (+0.086 → +0.070). Không phải artifact thuần.

### 2.3 Lens 2 — downside beta theo dấu return (walk-forward được)

| Giai đoạn | tuần | beta khi TT giảm | beta khi TT tăng | asym | t | % mã >0 |
|---|---|---|---|---|---|---|
| **IS 2014–2019** | 306 | 0.769 | 0.539 | **+0.230** | +4.22 | 70% |
| **OOS 2020–nay** | 337 | 1.220 | 0.879 | **+0.340** | +14.16 | 83% |

→ **Mệnh đề A xác nhận mạnh, ổn định cả IS lẫn OOS.** Đây là phát hiện chắc nhất của Việc 3.

### 2.4 Mệnh đề B — có phải nhóm "đầu cơ" bất đối xứng hơn không?

**Lens 1 (regime) nói CÓ**, ngũ phân vị theo beta tổng — đơn điệu đẹp:

| ngũ phân vị beta | beta_all | beta_D | beta_N | beta_U | **asym** |
|---|---|---|---|---|---|
| 1 (thấp nhất) | −0.011 | −0.031 | −0.003 | −0.002 | **−0.028** |
| 3 | 0.371 | 0.454 | 0.272 | 0.377 | +0.077 |
| 5 (cao nhất) | 1.079 | 1.312 | 0.827 | 1.088 | **+0.224** |

Tương quan asym với các proxy "đầu cơ" (lens 1):

| Proxy | Spearman | p | Đọc là |
|---|---|---|---|
| **beta tổng** | **+0.242** | 8e-18 | beta cao ⇒ bất đối xứng hơn ✅ |
| vốn hoá | −0.183 | 5e-05 | nhỏ hơn ⇒ bất đối xứng hơn (nhẹ) |
| thanh khoản ADV | −0.114 | 1e-02 | kém thanh khoản ⇒ hơn (nhẹ) |
| turnover (ADV/mcap) | +0.071 | 0.12 | **không có ý nghĩa** |
| idio-vol (biến động riêng) | −0.013 | 0.66 | **không có gì cả** |

**NHƯNG lens 2 (walk-forward được) nói KHÔNG ổn định:**

| Giai đoạn | Spearman(asym, beta_5y) | p |
|---|---|---|
| IS 2014–2019 | +0.131 | 0.050 (biên) |
| OOS 2020–nay | **+0.022** | 0.73 (**chết**) |

## 3. Vì sao không thể walk-forward lens 1 — hạn chế nghiêm trọng nhất

| Giai đoạn | tuần DOWN | tuần NEUTRAL | tuần UP |
|---|---|---|---|
| IS 2014–2019 | 57 | 237 | **12** |
| OOS 2020–nay | 92 | 157 | 88 |

DT5G rất dè dặt với BULL/EXBULL — **cả giai đoạn IS chỉ có 12 tuần UP**, không đủ để ước lượng
`beta_U`. Nghĩa là **toàn bộ kết quả lens-1 (gồm cả bằng chứng cho mệnh đề B) thực chất chỉ dựa trên
2020+**. Đây đúng hình dạng vấn đề đã gặp với overlay DT5G ("IS dormant → walk-forward là công cụ
sai"), phải nói thẳng chứ không được báo cáo t-stat lens 1 như thể đã qua walk-forward.

## 4. Kết luận thăm dò

1. **Bất đối xứng downside/upside beta là THẬT, mạnh, ổn định qua thời gian, và mang tính TOÀN THỊ
   TRƯỜNG** (+0.23 IS / +0.34 OOS; 70–83% số mã). Sống qua kiểm soát thanh khoản.
2. **Phần "tập trung ở nhóm đầu cơ" thì CHƯA chứng minh được.** Lens duy nhất ủng hộ nó không
   walk-forward được; lens walk-forward được thì tín hiệu tắt ở OOS. Trong 2 proxy đầu cơ trực tiếp
   nhất — **turnover và idio-vol — không có tương quan nào cả**, kể cả ở lens ưu ái nhất.
   ⇒ Trực giác user **đúng ở hiệu ứng, chưa đúng ở việc quy nó cho tính "đầu cơ"**: mọi thứ đều rơi
   cùng nhau khi thị trường xuống, không riêng gì hàng đầu cơ.
3. **Có đáng theo đuổi tiếp không? CÓ, nhưng ở tầng định giá/giám sát rủi ro, không phải tầng alpha.**
   Bất đối xứng là **thước đo rủi ro**, chưa có bằng chứng nào ở đây cho thấy nó **được định giá**
   (predict return) — chưa hề test điều đó.

## 5. Nếu đi tiếp thì đưa vào đâu (ĐỀ XUẤT, chưa làm, chưa được duyệt)

- **Định giá / CoE (khả thi nhất, research-only, không chạm production):** CoE dựng trên beta vô điều
  kiện **hiểu thấp** độ nhạy downside thực tế. Vì bất đối xứng khá đều giữa các mã (mệnh đề B không
  đứng), cách thực dụng cho kịch bản thận trọng là **dùng beta + ~0.25** (hoặc dùng thẳng `beta_dn`)
  làm biến thể bear-case của DCF — **không** cố đoán mã nào "bất đối xứng hơn".
- **Giám sát rủi ro (chuyển Spyros xem, KHÔNG tự wire):** beta thực hiện của danh mục trong
  CRISIS/BEAR cao hơn beta vô điều kiện ~+0.15 đến +0.34 ⇒ mọi ước lượng drawdown dựng trên beta vô
  điều kiện đều **lạc quan quá mức**. Đây là ghi chú hiệu chỉnh, không phải tín hiệu giao dịch.
- **KHÔNG đề xuất**: đổi WACC theo regime động, hay bất kỳ can thiệp nào vào DT5G/V2.4/sizing.
  Muốn đụng tới đó phải qua đủ quy trình (quant-skeptic + DSR + user duyệt) như mọi finding khác.

## 6. Việc còn thiếu (cho lần sau)

1. **Chưa test bất đối xứng có được ĐỊNH GIÁ không** — mã asym cao có return kỳ vọng cao hơn không?
   Đó mới là câu hỏi quyết định nó là factor hay chỉ là mô tả rủi ro.
2. Lens 1 cần chạy lại khi tích đủ tuần BULL/EXBULL để walk-forward thật.
3. Chưa tách **biên độ giá sàn/trần (±7% HOSE)** — trong sập mạnh, mã nhỏ liên tục nằm sàn, có thể
   bóp méo beta đo ở regime DOWN theo hướng chưa lượng hoá được.
4. Chưa dùng hiệu chỉnh Dimson (beta trễ) — mới chỉ kiểm soát gián tiếp bằng cách lọc thanh khoản.

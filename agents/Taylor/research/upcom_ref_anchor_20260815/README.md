# Anchor luật A dùng SAI cơ sở giá — xác minh độc lập + sửa

Job `Taylor_20260815_034407` · Taylor (Quant/Algo) · 2026-08-15
Chỉ đạo: user phát hiện, Mike dispatch. Mike đã **tự lùi TV1 về mean-5** trước khi giao việc —
job này KHÔNG lật lại quyết định đó.

> **Đây là SỬA LỖI (bug fix), không phải cải tiến.** Khác hẳn phần "Rule A vs Rule B" trước đó
> (một đánh đổi CHÍNH SÁCH, không có bằng chứng thống kê): ở đây anchor của luật A đơn giản
> **không phải đại lượng mà chính user đã chỉ định**, và sai đó ĐO ĐƯỢC bằng số.

---

## 0. TL;DR

1. **User nói "giá tham chiếu", code hiểu thành "giá đóng cửa phiên trước".** Nguyên văn câu
   hỏi mở ra cả chuỗi việc này (README `ceiling_ab_pacing_20260814` §5): *"Sao không lên chiến
   lược mua dựa trên **giá tham chiếu**, slide theo block bám giá đang khớp?"* — `giá tham
   chiếu` là một thuật ngữ CÓ ĐỊNH NGHĨA PHÁP QUY, không phải cách nói khác của giá đóng cửa.
2. **Hai định nghĩa đó chỉ trùng nhau ở HOSE/HNX.** Đo 43 mã trên feed DNSE sống 2026-08-15:
   34/34 mã HOSE+HNX lệch **đúng 0,0000%**; 7/7 mã UPCOM lệch khác 0.
3. **Dựng lại được công thức UPCOM từ dữ liệu khớp lệnh thô, khớp tới TỪNG TICK.** Bình quân
   gia quyền phiên 08-14 tính từ bar 1 phút (nguồn VCI, độc lập hoàn toàn với DNSE), làm tròn
   về bước giá 100đ của UPCOM → trùng `q.ref` DNSE ở **6/7 mã** (mã còn lại lệch đúng 1 tick,
   dữ liệu bar bị cắt lúc 14:50). Đây là bằng chứng CƠ CHẾ, không phải tương quan.
4. **Độ lớn thật của lỗi trên UPCOM** (N=1.618 phiên-mã, 12 tháng): median **0,361%**,
   p90 **1,271%**, **15,5%** số phiên vượt 1%, **1,2%** số phiên vượt CẢ τ=3% — tức có ngày
   sai số cơ sở giá còn lớn hơn toàn bộ ngân sách trần mà user duyệt.
5. **PHÁT HIỆN THỨ HAI, LỚN HƠN, chưa ai nêu: sự kiện quyền.** `SSI` — 1 trong 4 mã thuộc
   phạm vi luật A — **ex-right 2026-08-17** (thưởng CP 20% + cổ tức tiền 1.000đ). Giá tham
   chiếu chính thức phiên đó = **19.600đ**, trong khi giá đóng phiên trước = **24.500đ**.
   Trần luật A dựng trên giá đóng sẽ là **25.235đ — CAO HƠN CẢ GIÁ TRẦN của phiên (20.972đ)**.
   Luật A khi đó **vô hiệu hoàn toàn, im lặng**. Lỗi này KHÔNG giới hạn ở UPCOM: nó cắn mọi
   sàn, và cắn ngay thứ Hai tới.

---

## 1. PHẦN 1 — Xác minh độc lập (không dùng lại nguồn của Mike)

### 1.1 Quy chế 3 sàn — WebSearch riêng, ≥2 truy vấn độc lập

| Sàn | Giá tham chiếu phiên T | Biên độ |
|---|---|---|
| HOSE | giá **đóng cửa** phiên T−1 | ±7% |
| HNX | giá **đóng cửa** phiên T−1 | ±10% |
| **UPCOM** | **bình quân gia quyền** các giá giao dịch **lô chẵn** khớp theo phương thức **khớp lệnh liên tục** của phiên T−1 | **±15%** |
| mọi sàn, ngày GDKHQ | giá đóng cửa gần nhất **đã điều chỉnh** theo giá trị quyền | theo sàn |

Nguồn: thuvienphapluat.vn, topi.vn, dsc.com.vn, SSI/VNDIRECT/Yuanta/VIX (hướng dẫn giao dịch
UPCOM). Các nguồn khớp nhau, kể cả ví dụ số học bình quân gia quyền.

### 1.2 Sàn niêm yết của TOÀN BỘ mã đã/đang dùng cơ chế này — đo, không tra web

Quét 97 plan lịch sử: phạm vi luật A (`side=buy` + có `entry_anchor_price`) = **DRI, POW, SCL,
SSI**. Cộng **TV1** (book `DISCRETIONARY_SPECIAL`). Để không bỏ sót ứng viên tương lai, đo cả
**37 mã** từng xuất hiện ở lệnh MUA trong 97 plan + DGC/PNJ + 4 mã UPCOM đối chứng = **43 mã**.

**Nguồn xác định sàn = payload DNSE thật, KHÔNG phải WebSearch, KHÔNG phải `Quote.exchange`.**
Trường thật là **`marketId`**: `STO`=HOSE, `STX`=HNX, `UPX`=UPCOM. Kiểm chéo bằng một tín hiệu
**trực giao**: biên độ giá thật `q.ceiling/q.ref−1` đo được — 7% / 10% / 15% — khớp 43/43 mã
với ánh xạ trên. Hai tín hiệu độc lập cùng chỉ một kết luận.

| Sàn | Mã |
|---|---|
| **UPCOM (UPX)** | **DRI, SCL, TV1**, SGP, ACV, QNS, TMG |
| HNX (STX) | MBS, SHS |
| HOSE (STO) | 34 mã còn lại, gồm **POW, SSI** |

⇒ Danh sách sơ bộ của Mike ĐÚNG (DRI/SCL/TV1 = UPCOM; POW/SSI = HOSE). Bổ sung: **3/5 mã**
trong phạm vi luật A là UPCOM, và có 2 mã HNX trong universe mua (không bị ảnh hưởng bởi lỗi
UPCOM vì HNX cũng lấy giá đóng cửa).

### 1.3 🐞 BUG PHỤ phát hiện khi làm việc này: `Quote.exchange` trả "HOSE" cho MỌI mã

```python
self.exchange = qget(raw, "exchange", "market", "floorcode", default="HOSE")
```
Payload DNSE **không có** bất kỳ key nào trong ba key đó (nó có `marketId`), nên hàm luôn rơi
về `default="HOSE"` — kể cả cho SHS/MBS (HNX) và DRI/SCL/TV1 (UPCOM). Đo 43/43 mã đều ra
"HOSE". Đây là **fail-OPEN**: đoán sai một cách im lặng thay vì từ chối.

Hệ quả đã cắn thật và ĐÃ ĐƯỢC GHI NHẬN từ 2026-07-01 nhưng chữa ở ngọn: `tick_retry_selfcheck.py`
ghi rõ *"Root cause: `Quote.exchange` silently defaulted to 'HOSE' when the live feed didn't
populate it"* → SHS/MBS bị từ chối **1.494 lần** ("Invalid price lot") vì làm tròn theo bước giá
HOSE. Cách chữa lúc đó là `_retry_tick_mismatch()` — thử-sai rồi học. Lý do không sửa tận gốc
được ghi trong chính docstring đó: *"no guessing the live JSON field name"*. **Giờ tên trường
đó đã được ĐO, không còn phải đoán.**

### 1.4 Đối soát công thức UPCOM — dựng lại bình quân gia quyền từ dữ liệu khớp lệnh

Không tin field của broker, không tin WebSearch: dựng lại `Σ(giá×KL)/ΣKL` phiên 2026-08-14 từ
**bar 1 phút nguồn VCI** (`vnstock`, đường dữ liệu độc lập hoàn toàn với DNSE), rồi so với
`q.ref` DNSE đo sống 08-15. So bằng **TỈ SỐ** `vwap/close` nên bất biến với việc bar VCI đã
điều chỉnh hồi tố.

| mã | vwap/close dựng lại | ref/close đo thật | ref suy ra (làm tròn tick 100đ) | `q.ref` DNSE |
|---|---:|---:|---:|---:|
| SCL | −3,3634% | −3,3755% | 22.900 | **22.900** ✅ |
| TMG | +0,9494% | +0,9494% | 63.800 | **63.800** ✅ |
| TV1 | −0,7264% | −0,4975% | 20.000 | **20.000** ✅ |
| ACV | +0,1775% | +0,2469% | 40.600 | **40.600** ✅ |
| QNS | +0,2622% | +0,2146% | 46.700 | **46.700** ✅ |
| DRI | −0,2139% | 0,0000% | 13.300 | **13.300** ✅ |
| SGP | −0,2339% | −0,4878% | 20.500 | 20.400 ❌ (lệch 1 tick; bar SGP dừng 14:50, thiếu đuôi phiên) |

**6/7 khớp tuyệt đối tới từng tick sau khi làm tròn về bước giá 100đ của UPCOM.** Ca mạnh nhất
là SCL: một sai lệch **−3,36%** được tái lập độc lập với sai số **0,012 điểm phần trăm**. Đây
không còn là "q.ref có vẻ hợp lý" — nó là công thức đã được chứng minh.

Đồng thời chứng minh luôn: `q.ref` đọc chiều 08-15 (T7) mô tả **phiên KẾ TIẾP (T2 08-17/18)**,
không phải phiên vừa chạy — tức đúng thứ mà tầng lập plan tối T−1 cần.

### 1.5 Độ lớn thật của lỗi, nhiều ngày — không chỉ N=66 một ngày

`|vwap − close| / close`, bar 1 phút, 12 tháng tới 2026-08-14:

| mã | N phiên | median | p90 | p95 | max | >1% | >3% |
|---|---:|---:|---:|---:|---:|---:|---:|
| DRI | 259 | 0,531% | 1,318% | 1,627% | 4,344% | 52 | 2 |
| SCL | 259 | 0,484% | 1,627% | 2,383% | 8,711% | 61 | 11 |
| TV1 | 259 | 0,389% | 1,333% | 1,611% | 7,041% | 47 | 2 |
| SGP | 259 | 0,545% | 1,398% | 1,662% | 3,545% | 54 | 1 |
| ACV | 259 | 0,340% | 1,013% | 1,381% | 2,531% | 29 | 0 |
| QNS | 259 | 0,182% | 0,530% | 0,687% | 1,509% | 2 | 0 |
| TMG | 64 | 0,000% | 0,846% | 5,521% | 21,374% | 6 | 4 |
| **GỘP** | **1.618** | **0,361%** | **1,271%** | **1,628%** | 21,374% | **251 (15,5%)** | **20 (1,2%)** |

Đọc đúng: sai số median 0,361% = **12% ngân sách τ=3%**; p90 1,271% = **42% ngân sách**; và
**1,2% số phiên sai số còn LỚN HƠN CẢ ngân sách**. Không phải nhiễu làm tròn — là sai cơ sở.

### 1.6 🔴 Sự kiện quyền — lỗi lớn hơn, không giới hạn UPCOM, cắn NGAY 2026-08-17

Trong lúc đo, `SSI` (HOSE, **thuộc phạm vi luật A**) lộ ra lệch −20% giữa BQ và DNSE. Job
trước gán nhãn *"feed hỏng thật"*. **Không phải.** Ba nguồn độc lập, khớp số học tuyệt đối:

| Nguồn | Số |
|---|---|
| `tav2_bq.corporate_action` (đường ingest của Winston) | SSI **exright 2026-08-17**: thưởng CP tỉ lệ **20%** + cổ tức tiền **1.000đ/cp** |
| Tính tay theo công thức điều chỉnh | (24.500 − 1.000) / 1,2 = 19.583,33 → bước giá HOSE 50đ → **19.600** |
| DNSE `q.ref` sống 08-15 | **19.600** ✅ |
| DNSE `ohlc` (đã điều chỉnh hồi tố) | 19.580 ✅ |
| BQ `ticker.Price` 08-14 (thô, chưa điều chỉnh) | 24.500 |

Nếu plan T2 2026-08-17 có lệnh mua SSI theo luật A **cơ sở giá đóng cửa**:

```
trần = 24.500 × 1,03 = 25.235đ
giá TRẦN hợp lệ của phiên = 19.600 × 1,07 = 20.972đ
```

Trần luật A nằm **cao hơn cả giá trần sàn cho phép 20,3%** ⇒ `min()` không bao giờ chạm tới nó
⇒ **luật A không tồn tại trong phiên đó**, và không log nào nói điều đó. Đúng loại hỏng mà cả
cơ chế này sinh ra để chặn.

Cổng `_rule_a_ref_guard` (commit `59f9569`) *có* chặn ca này (lệch 25% ≫ 1%) — nhưng chặn
bằng cách **không đặt lệnh SSI**, và với lý do sai (báo "feed hỏng"). Anchor đúng cơ sở thì
không cần chặn: trần đúng là 19.600 × 1,03 = 20.188đ.

### 1.7 BQ **không** có nguồn giá tham chiếu — đã kiểm, không suy đoán

- `INFORMATION_SCHEMA` bảng `ticker`: không có cột nào mang giá tham chiếu, sàn, giá trần/sàn.
- `Trading_Value` **không dùng được làm bình quân gia quyền**: đo 24 dòng (9 mã × 3 phiên),
  `Trading_Value / Volume == Close` **tuyệt đối ở 24/24 dòng** ⇒ đây là cột PHÁI SINH
  (`Volume × Close`), không phải giá trị khớp thật.
- `Price` là giá **thô chưa điều chỉnh** ⇒ sai ở mọi ngày GDKHQ (ca SSI ở trên).

⇒ **Nguồn duy nhất đúng cho giá tham chiếu = DNSE live `q.ref`.** Không có đường lấy lịch sử ⇒
hồi quy quá khứ trên đại lượng này là bất khả; §3 nói rõ hồi quy đo cái gì thay thế.

---

## 2. PHẦN 2 — Bản vá

Xem `FIX.md` (cùng thư mục).

## 3. PHẦN 3 — Hồi quy

Xem `REGRESSION.md` (cùng thư mục).

---

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
python3 mike/agents/Taylor/research/upcom_ref_anchor_20260815/probe_exchange_ref.py       # §1.2 §1.3 §1.6
/home/trido/thanhdt/wc_venv/bin/python \
  mike/agents/Taylor/research/upcom_ref_anchor_20260815/probe_vwap_vs_close.py            # §1.4 §1.5
```
Dữ liệu thô: `probe_exchange_ref.json`, `vwap_vs_close.json`, `vwap_daily.csv`,
`data/<mã>_1m.csv`.

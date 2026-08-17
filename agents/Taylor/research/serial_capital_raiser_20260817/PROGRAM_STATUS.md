# PROGRAM STATUS — serial capital raising (`serial_capital_raiser_20260817`)

Job `Taylor_20260817_075412` · 2026-08-17 · **VERDICT: RISK / DESCRIPTIVE — no alpha candidate,
nothing proposed for wiring.**

Prereg committed before outcomes at `eccab390`. Selfcheck **28/28 PASS**, identical under `env -u TZ`
and `TZ=America/Chicago`. Full report: `FINDINGS.md`. Deviations: `DEVIATIONS.md`.

---

## Answer to the user's question

> *"Cùng PE/PB, công ty hay huy động vốn có bị discount không?"*

**Không — và dấu ngược lại với tiền đề.** Công ty huy động vốn ngoài ≥2 lần trong 3 năm gần nhất
**KHÔNG rẻ hơn** theo earnings: PE của họ **cao hơn ~17–19%** so với cùng tháng, cùng ngành, sau khi
kiểm soát thanh khoản / lợi nhuận / đòn bẩy / F-score. Theo book họ rẻ hơn một chút nhưng **không phân
biệt được với 0** sau cùng bộ kiểm soát đó.

Và không có discount nào bị bỏ sót: **ở cùng mức định giá họ vẫn kém hơn** ~**0,8–0,9%/tháng
(≈−10%/năm)**. Phần rẻ trên book là **đền bù cho rủi ro thật, không phải cơ hội**.

---

## Số liệu chính

| Câu hỏi | Kết quả | N (công ty độc lập) |
|---|---|---|
| **Q1** BHAR dài hạn sau phát hành (RAISE_SET) | 1Y **−7,74%** (Holm p=.014) · 2Y **−18,18%** · 3Y **−22,03%** (p<.0001) | 758 sự kiện / **368 mã** / 181 tháng |
| Q1 theo subtype vượt sàn N=200 | chỉ **RIGHTS** âm có ý nghĩa (−9,67%, p=.020). ESOP / stock-div / bonus **phẳng** | RIGHTS 420 / 277 mã |
| **Q2a** discount định giá | `1/PE` serial coef **−0,01350** (t=−3,36, Holm p=.0015) ⇒ **PE 12,95 vs 11,03 = +17,5%** (lát ADV≥2tỷ: **+19,1%**, t=−2,58) | 49.911 firm-months / 6.522 cell |
| Q2a trên book (`1/PB`) | +0,044 (t=+0,85, p=.393) — **không có discount đo được** | 54.891 |
| **Q2b** forward return ở cùng định giá | **−0,886%/tháng**, NW t=−3,98, **−10,55%/năm** | serial 391 mã |
| Q2b lát đầu tư được (size-matched + ADV≥2tỷ) | −0,896%/tháng, t=−2,24, **OOS t=−1,20 (KHÔNG có ý nghĩa)** | serial 295–308 mã |

**Cơ chế kinh tế** (median, lát ADV≥2tỷ): serial raiser có **ROIC_Trailing 0,211 vs 0,326** (−35%),
F-score 4 vs 5, Debt/Eq 1,237 vs 1,073 → PB thấp *và* PE cao cùng lúc, vì **mẫu số lợi nhuận là thứ
đã rơi**. Đọc PE cao là "thị trường trả giá cao" thì sai; đọc PB thấp là "rẻ" cũng sai.

---

## Vì sao verdict là RISK/DESCRIPTIVE chứ không phải ALPHA — 3 cổng preregistered đều chặn

1. **Bảng quyết định đã khoá trước** (PREREG §4): hệ số Q2a **âm (đắt hơn)** ⇒ ô *"negative (richer)
   → DESCRIPTIVE / RISK — tiền đề câu hỏi không được ủng hộ"*.
2. **Sign consistency 3 biến thể**: `ey` cho −0,0135 (RAISE_SET) / −0,0082 (V-WIDE) / **+0,0003
   (V-ALL)**. Định nghĩa `event_code='ISS'` theo đúng câu chữ dispatch cho ~0. Kết quả **chỉ tồn tại
   với định nghĩa "huy động tiền thật"** — hợp lý về kinh tế (stock dividend/bonus không huy động vốn)
   nhưng theo luật đã viết thì trần headline là DESCRIPTIVE.
3. **`Edge rớt OOS = loại`**: Q1 horizon chính rớt OOS (−3,97%, p=.44; **2010 gánh 67,4%** hiệu ứng);
   Q2b lát đầu tư được rớt OOS (t=−1,20). Không mục nào qua chuẩn hiện hành của fleet.

## Confound QUAN TRỌNG NHẤT — placebo đã nổ, và nó đổi cách đọc Q1

| Test preregistered | Cửa sổ | Kết quả |
|---|---|---|
| Pre-trend | [t0−250, t0] | **+45,54%** CI[+33,53%, +58,43%] |
| Far placebo | [t0−500, t0−250] | **+30,21%** CI[+20,71%, +40,78%] |

Doanh nghiệp huy động vốn **SAU khi đã chạy giá rất mạnh**. PREREG §3 đã cam kết placebo có ý nghĩa =
hạ cấp, và đúng như vậy: **không tách được "phát hành gây kém hiệu quả" khỏi "hoàn lại cú chạy giá
trước đó"** bằng thiết kế này. Sau khi điều kiện hoá pre-trend (post-hoc, D3): hệ số cash-raise còn
**−5,49% (t=−2,17)** ở 1Y, không phải −7,74%.

⚠️ **Không được trích −7,74% / −18,18% / −22,03% như "chi phí của việc phát hành"** — đó là BHAR thô,
chưa khử reversal.

## Nghịch lý biểu kiến với Sprint 4 — không phải mâu thuẫn

Sprint 4 (`corp_action_program_20260815`) thấy NULL ở T+5/T+20/T+60 cho ESOP/private placement pooled.
Program này thấy Q1 âm ở 1–3 năm. **Hai kết luận tương thích**, và bảng subtype giải thích vì sao:
ESOP / stock dividend / bonus **phẳng ở cả hai khung thời gian** (ESOP −0,25% p=.915 ở 1Y). Phần âm
dài hạn đến từ **RIGHTS** (và một phần private placement, không có ý nghĩa). Sprint 4 pool ESOP+PP nên
đúng là NULL; ở đây tách subtype nên thấy rights.

---

## Điều KHÔNG được suy ra từ nghiên cứu này

- ❌ **Không có tuyên bố nhân quả** "phát hành thêm phá huỷ giá trị" — xem confound trên.
- ❌ **Không có edge giao dịch được.** Lát size-matched + ADV≥2tỷ mất ý nghĩa OOS. **Không wire.**
- ❌ **Không suy luận theo vốn hoá.** `OShares` là TRAP (restated, không PIT) nên **không đọc**; mọi
  phát biểu về "size" đứng trên ADV. Đây là hạn chế omitted-variable thật, khai từ PREREG §1.
- ❌ **Không có announcement study.** `public_date` = `WEAK_UNVERIFIED_VINTAGE`; vẫn CẤM tới khi có
  vintage thứ 2 của `corporate_action` (ledger C1, ≈2026-09-12).
- ❌ **DSR/PBO chưa tính** — cố ý, khai trước ở PREREG §5 (không chọn config để deploy). Nếu về sau ai
  muốn biến spread `ey` thành screen thì DSR/PBO + cổng quant-skeptic là **bắt buộc**, và phải giải
  quyết thất bại OOS trước.

## Cái CÓ THỂ dùng ngay (thông tin, không phải gate)

Serial capital raising là **dấu hiệu tiêu cực**, không phải nguồn rẻ. Cụ thể, khi đọc một ứng viên mua:

- PB thấp trên một serial raiser **không phải** tín hiệu value — cùng tên đó có PE cao, ROIC yếu,
  forward return âm ở cùng mức định giá.
- Đây là **quan sát mô tả**, KHÔNG phải luật chặn lệnh. Không sửa `trading_rules.json`, không thêm
  gate. Muốn thành gate thì phải qua đường DSR/PBO + quant-skeptic ở trên.

## Câu hỏi còn mở

| # | Câu hỏi | Vì sao chưa đóng | Điều kiện mở lại |
|---|---|---|---|
| S1 | Hiệu ứng rights **thuần** là bao nhiêu sau khi khớp đối chứng theo lợi suất 12M trước đó? | Thiết kế matched-control là **study khác**, không phải robustness; bịa sau khi thấy placebo là đúng cái drift cần tránh | Cần prereg riêng nếu user muốn theo đuổi |
| S2 | Chênh PE là "market premium" hay "mẫu số EPS rơi"? | §3.1 lập luận từ pattern ROIC/PB, **chưa có test hình thức** (cần phân rã PE thành giá và EPS theo thời gian quanh mỗi lần raise) | Mở được ngay, chi phí thấp |
| S3 | Có bias small-cap trong nhóm serial không? | `OShares` TRAP ⇒ không có market cap PIT. Size-tercile theo ADV giữ được spread `ey` nhưng ADV ≠ size | Cần nguồn share-count PIT (`oshares_live.py` đã có cổng — chưa dùng cho lịch sử dài) |
| S4 | `listing_date` — dictionary của Sprint 1 ghi "100% NULL" nhưng đo lại thấy populated phần lớn | Chỉ là lỗi tài liệu, không ảnh hưởng program này (neo hoàn toàn theo `exright_date`) | Sửa `corp_action_program_20260815/DATA_DICTIONARY.md`; xem D6 |

## Ranh giới đã giữ

- Chỉ tạo file dưới `agents/Taylor/research/serial_capital_raiser_20260817/`.
- **Không** wire production · **không** cài cron · **không** đổi `trading_rules.json` · **không** tạo
  bảng/view · **không** dispatch agent khác. BigQuery read-only (~0,7 GB quét).
- Không đọc `profit_2W/1M/2M/3M` hay biến thể `_center_*` (selfcheck T1a khoá bằng grep trên chính
  source).

## Tái lập

```bash
cd mike/agents/Taylor/research/serial_capital_raiser_20260817
python3 build.py && python3 analyze.py && python3 robust.py && python3 selfcheck_serial.py
```

Artifact: `out/results.json` (preregistered) · `out/robust.json` (post-hoc) · `out/selfcheck.json` ·
`out/q1_bhar.csv` · `out/q2_panel.csv` · `out/sql/*.sql` (mọi truy vấn đúng như đã chạy).

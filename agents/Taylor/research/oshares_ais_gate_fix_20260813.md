# Vá cổng neo AIS sau REFUTED vòng 2 — Việc A (`oshares_pit`)

Job `Taylor_20260813_142812` · 2026-08-13 · Taylor · **CHỜ quant-skeptic vòng 3**
Tiền nhiệm: job `Taylor_20260813_125526` (REFUTED, log `mike/logs/verify_20260813_134849_1577607.log`)

---

## TL;DR

| | |
|---|---|
| **Ca bác bỏ** | FPT 2020-05-05 trả 461.723.054 (đúng: 681.668.102, −32,3%) ở nhãn `AIS_EXACT`. **Tái lập được**, đã vá, có ca hồi quy + chứng minh ngược. |
| **Độ rộng lớp lỗi** | **KHÔNG phải 2 ca cá biệt: 220/2.505 transition AIS, 135 mã** đang được phục vụ mà không kiểm được. Bản vá xử lý cả lớp. |
| **Hướng sửa** | Đổi bộ **BẮT LỖI** (`_suspect_ais`) thành bộ **CHỨNG NHẬN** (`_ais_verdicts`) — chỉ phục vụ neo AIS đối chiếu được VÀ khớp. Fail-closed. |
| **Hướng tách chuỗi theo `organ_code`** | **BÁC BỎ bằng dữ liệu** (không có trường phân biệt). Chi tiết §2. |
| **Backtest sau vá** | liq **12,44%** / Sharpe 0,65 / DD −46,6% — bằng ĐÚNG baseline tiền-wire. core0.5 12,11%, core1.0 14,48%. |
| **Sweep `SANITY_FACTOR`** | Bình nguyên thật [1,5 … 12] (0,01pp biên độ); 3,0 nằm giữa. Nhưng **bản thân cổng** vẫn gánh 0,68pp. |
| **Việc B** | **0 ô đổi giá trị / 766** — đo A/B cổng cũ vs mới, không giả định. |
| **Điều KHÔNG chứng minh được** | Hỗn hợp "khử look-ahead vs bơm lỗi" **vẫn chưa phân giải xong** (55 có bằng chứng cứng / 14 nghi / 112 không phân loại được). Vẫn KHÔNG được kết luận "look-ahead này vô hại". |

---

## 1. Cơ chế lỗi — truy tới tận gốc, không dừng ở triệu chứng

`_suspect_ais` đối chiếu mỗi AIS với AIS liền trước qua hai đường hợp lệ:
(a) `roll(prev, ISS ở giữa)` · (b) `prev + shares_delta`.
Khi `_roll` gặp một ISS không có tỉ lệ lẫn `shares_delta` (blocker), code cũ `continue` — **vứt bỏ
CẢ HAI ứng viên**, kể cả (b) vốn *không cần lăn qua ISS nào cả*. Dòng đó đi tiếp, không kiểm, ở
nhãn tin cậy cao nhất.

FPT 2020-05-05: neo = AIS 2020-04-06 (461.723.054). Giữa nó và AIS trước (2019-06-24 =
678.358.688) có ESOP 2020-03-26 tỉ lệ 0 ⇒ blocker ⇒ bỏ qua. Nhưng (b) dựng được:
678.358.688 + 2.296.370 = **680.655.058**, lệch 32% so với 461.723.054. Ứng viên bắt được nó ngay
— chỉ là code không bao giờ tính tới.

**Vì sao vendor sai** (truy ra được, không phải "vendor lỗi" chung chung): nhóm AIS delta-nhỏ của
FPT mang `shares_total_after` của **1–3 năm trước**, đối chiếu thẳng với dòng quý:

| AIS | `shares_total_after` | = số CP FPT tại | dòng quý |
|---|---|---|---|
| 2020-04-06 | 461.723.054 | 2017Q1 | 461.640.678 |
| 2021-04-05 | 533.615.661 | 2018Q1 | 533.533.285 |
| 2023-03-27 | 681.780.478 | 2020Q1 | 681.668.102 |

Đây là các dòng **niêm yết lại cổ phiếu hạn chế chuyển nhượng** từ đợt phát hành gốc; vendor gắn
`effective_date` của lần niêm yết mới nhưng `shares_total_after` của kỳ gốc. Kết quả là hai chuỗi
AIS ĐAN XEN trong cùng một mã.

---

## 2. Câu hỏi 1 — hướng sửa nào? (chọn fail-closed, **bác** hướng tách chuỗi)

**Hướng tách chuỗi theo `issue_method_name_vi` / `organ_code` (quant-skeptic gợi ý phụ): BÁC BỎ
BẰNG DỮ LIỆU, không phải bằng lập luận.** Kéo cả 46 dòng AIS của FPT ra xem mọi cột:

- `organ_code` = `FPT` cho **100%** dòng — không phân biệt.
- `issue_method_code` / `issue_method_name_vi` / `category` = **NULL trên toàn bộ dòng AIS**
  (hai cột này chỉ được điền cho ISS).
- `event_name_vi` = `"Niêm yết thêm"` cho 100% dòng.
- `listing_date` cũng không tách được: dòng SAI 2020-04-06 có `listing_date == effective_date`,
  nhưng dòng ĐÚNG 2021-07-21 cũng vậy.

⇒ **Không tồn tại trường phân loại nào tách được hai chuỗi.** Hướng đó không khả thi ở nguồn.

**Hướng đã chọn: đảo chiều nghĩa vụ chứng minh.** Bộ cũ là thế giới MỞ ("chứng minh dòng này sai
thì tôi mới loại") nên "chưa bắt được" bị đọc thành "đã kiểm". Bộ mới là thế giới ĐÓNG ("chứng
minh dòng này đối chiếu được thì tôi mới phục vụ").

**Vì sao đây là hướng đúng chứ không phải hướng tiện:**

1. **Chính codebase này đã có tiền lệ, ở đúng bài toán đối xứng.**
   `oshares_live._explain_quarterly` — cổng cho neo *dòng quý* — đã trả ba trạng thái từ lâu:
   blocker ⇒ **từ chối** (`return False, False, "...không dựng được kỳ vọng để đối chiếu"`);
   không có gì để đối chiếu ⇒ nhận nhưng gắn nhãn `ANCHOR_UNVERIFIED`. Nhánh AIS là nhánh DUY NHẤT
   chưa có xử lý đó. Bản vá không phát minh chính sách mới — nó **áp chính sách đã có cho nhánh
   còn thiếu**.
2. **Bất đối xứng chi phí là thật và đo được.** Với `oshares_pit`, "từ chối" = trả về **đúng con số
   caller đang dùng hôm nay** — không mất gì. "Phục vụ nhầm" = thay số đúng bằng số sai −32%. Hai
   chiều không cùng độ lớn ⇒ cổng phải lệch về phía từ chối. Đây chính là §24/§25
   `coding_guidelines` ("không suy đoán khi không chắc, fail-closed").
3. **Bộ bắt lỗi không sửa được bằng cách bắt giỏi hơn.** quant-skeptic chỉ ra tập cờ cũ thực chất
   là "transition NẰM CẠNH bất thường". Đúng — và đó là thuộc tính cấu trúc: một cặp lệch nhau
   luôn buộc tội cả hai dòng, không cách nào biết dòng nào hỏng. Nên phải **thôi tuyên bố "đây là
   lỗi vendor"** và chỉ tuyên bố "đây là dòng tôi kiểm được".

**Đã cân nhắc và LOẠI — dò ngược chuỗi** (thử đối chiếu `cur` với các AIS xa hơn để cứu ca IDC
2022-09-05): nếu hai chuỗi đan xen mà mỗi chuỗi tự nhất quán, dò ngược sẽ **tự chứng nhận chuỗi
sai**. Với FPT, 461.723.054 + 69.238.051 = 530.961.105 = đúng một dòng AIS khác — tức chuỗi sai
CÓ liên kết nội bộ. Dò ngược sẽ mở lại đúng lỗ hổng vừa vá. Loại.

---

## 3. Câu hỏi 2 — ca gương IDC còn là vấn đề không?

**Không còn, vì "vấn đề" cũ là vấn đề về NHÃN chứ không về hành động.**

Trước: cổng gắn cờ IDC 2022-09-05 (dòng ĐÚNG) và *đồng thời* coi các ca không bắt được là chắc
chắn. Bất đối xứng đó mới là lỗi: chiều báo oan được công bố là "an toàn", chiều bỏ lọt thì không
ai nói tới, mà chiều bỏ lọt mới là chiều nguy hiểm.

Sau: **không còn chiều bỏ lọt** — mọi thứ không chứng nhận được đều rơi về số cũ. IDC 2022-09-05
vẫn không được phục vụ, nhưng lý do ghi trong log giờ là `KHÔNG XÁC MINH ĐƯỢC: neo vào AIS
2022-09-05 không đối chiếu được`, **không phải** quy kết "lỗi vendor". Hành động an toàn, nhãn
trung thực. Ca test `A12` khoá đúng điều đó.

Giá phải trả đã đo, và ghi thành ca test `A4b` để nó không bị quên: VNM 2016-09-20 (dòng **ĐÚNG**,
1.451.453.429) bị `UNVERIFIED` vì ESOP 2016-07-11 tỉ lệ 0 chắn đường và (b) thiếu đúng phần ESOP
đó. Chi phí thật: rơi về dòng quý 1.451.426.329 — **lệch 0,002%**.

---

## 4. Câu hỏi 3 — quét toàn bảng: lớp rộng hay 2 ca cá biệt?

Toàn bộ `tav2_bq.corporate_action`, mọi cặp AIS liên tiếp (`event_status="executed"`):

| | số cặp | số mã |
|---|---:|---:|
| Tổng transition (948 mã có AIS) | 2.505 | 948 |
| Không có blocker — chứng nhận được | 1.513 | |
| Không có blocker — MÂU THUẪN (cổng cũ đã bắt) | 314 | 158 |
| Có blocker, (b) xác nhận ⇒ vẫn phục vụ | 458 | |
| **Có blocker, (b) MÂU THUẪN ⇒ đang phục vụ SAI** | **213** | **129** |
| **Có blocker, không dựng nổi ứng viên nào** | **7** | **6** |

⇒ **220 transition / ~135 mã** thuộc đúng lớp lỗi, không phải 2 ca. Bản vá xử lý **cả lớp** theo
cơ chế (bỏ `continue`, giữ ứng viên (b), rỗng-ứng-viên ⇒ UNVERIFIED), không vá theo tên mã. 458 ca
"blocker nhưng (b) xác nhận" **không mất phủ** — đó là lý do sửa đúng chỗ rẻ hơn nhiều so với chặn
mọi ca có blocker.

---

## 5. Bản vá

`oshares_pit.py`:
- `_suspect_ais` → **`_ais_verdicts`**: `{effective_date: "OK" | "NO_PRIOR" | "UNVERIFIED"}`.
  Blocker chỉ giết ứng viên (a); (b) vẫn được xét; không dựng nổi ứng viên nào ⇒ `UNVERIFIED`.
- `_anchor_is_suspect` → **`_anchor_unverified`**, **fail-closed cả 3 nhánh**: thiếu cache /
  verdict lạ / hàm ném lỗi ⇒ coi như CHƯA chứng nhận. (Bản cũ trả `False` = phục vụ ở cả ba —
  cùng một lỗi, chỉ ở tầng khác. Ca `A13`/`A14`.)
- `_SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR")` — dòng CHÍNH SÁCH duy nhất, xem §6.
- Docstring dòng ~25-26 và ~233-234: **xoá tuyên bố sai**, viết lại đúng bản chất.
- `SANITY_FACTOR` đọc từ env ⇒ sweep tái lập bằng lệnh.

`oshares_live.py`: header `STATUS: NOT WIRED` → `WIRED (chỉ qua oshares_pit)`, kèm cảnh báo
consumer mới KHÔNG được gọi thẳng `oshares_at` (nó vẫn trả 3 tỷ cho IDC, 461.723.054 cho FPT).

**Selfcheck: `oshares_pit` 47/47 PASS** (35 → 47, thêm A4b + A7-A15). Hồi quy: `oshares_live`
22/22 PASS. Mọi ca "chặn được" đều có **ca chứng minh ngược** (A6, A11: bỏ cổng ra ⇒ số sai THẬT
SỰ lọt vào).

Ca hồi quy bắt buộc theo dispatch:

| ca | kết quả |
|---|---|
| FPT 2020-05-05 | `681.668.102` (`ticker_financial`), live_was 461.723.054 — **không còn trả số sai** |
| FPT 2023-04-10 | `1.097.026.572`, live_was 681.780.478 |
| IDC 2022-09-05 (ca gương) | rơi về số nền, lý do `KHÔNG XÁC MINH ĐƯỢC` |
| IDC 2021-02-05 | `300.000.000`, live_was 3.000.000.000 |
| VNM 2016-09-20 (mới, từ quét) | `UNVERIFIED`, chi phí 0,002% |

---

## 6. Điểm phán đoán DUY NHẤT còn lại — có phục vụ `NO_PRIOR` không?

AIS **đầu tiên** của một mã không có gì để đối chiếu. Đo cả hai chân:

| chính sách | ô live | phủ | liq CAGR |
|---|---:|---:|---:|
| phục vụ `NO_PRIOR` (**đang chạy**) | 6.603 | 86,8% | **12,44%** |
| loại `NO_PRIOR` (chặt hơn) | 6.290 | 82,7% | 12,46% |

Chặt hơn đẩy thêm **313 ô (4,1pp phủ)** về lại số quý RESTATE — tức **đổi look-ahead lấy
look-ahead** — để mua 0,02pp CAGR (trong nhiễu). Không có ca hại nào đo được ở nhánh này: FPT
2017-07-03 (AIS đầu tiên, 530.961.105) đối chiếu ĐÚNG với dòng quý 2017-08-01 (530.878.729, lệch
0,015%). Chọn phục vụ, theo đúng tiền lệ `_explain_quarterly`. **Đổi chính sách = sửa 1 dòng.**
Đây là chỗ tôi muốn quant-skeptic soi kỹ nhất.

---

## 7. Sweep `SANITY_FACTOR` (yêu cầu vòng 2)

Mỗi chân chạy đủ `custom30_core_select_audit`, SELF-CHECK PASS + SPOTCHECK PASS:

| × | 1,5 | 2,0 | 2,5 | **3,0** | 4,0 | 5,0 | 7,5 | 10 | 12 | 15 | 30 | 100 | tắt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| liq CAGR | 12,43 | 12,44 | 12,44 | **12,44** | 12,44 | 12,44 | 12,44 | 12,44 | 12,44 | 12,51 | 12,51 | 12,51 | 13,12 |
| ô bị chặn | 515 | 503 | 502 | **500** | 500 | 500 | 500 | 500 | 499 | 472 | 472 | 470 | 457 |

**Hai kết luận tách bạch:**
1. **Ngưỡng không còn gánh gì.** [1,5 … 12] là bình nguyên thật — 0,01pp trên dải rộng 8×, 3,0 nằm
   giữa. Trước khi vá, ngưỡng này gánh ~0,95pp; giờ cổng chứng nhận bắt trước phần lớn. Đây là số
   **đo**, không còn là lập luận (đóng `param_overfit: fail`).
2. **Bản thân cổng thì VẪN gánh.** Tắt hẳn ⇒ 13,12% (+0,68pp giả). Bậc thang ở ~13–14× là 27 ô lỗi
   thô mà cổng chứng nhận KHÔNG bắt. Giữ cổng, giữ nó thô.

Tái lập: `OSHARES_SANITY_FACTOR=<x> python custom30_core_select_audit.py`.

---

## 8. Backtest Việc A sau vá — số MỚI, đo lại

Chân baseline dựng bằng cách ép `oshares_at` ném lỗi ⇒ hợp đồng TOÀN PHẦN đưa mọi ô về số quý =
đúng hành vi tiền-wire (đồng thời kiểm luôn hợp đồng đó). Cả ba chân `nav_recon_err = 0,00 VND`.

| | liq CAGR | Sharpe | MaxDD | core0.5 | core1.0 | ô live | mcap đổi | ô bị chặn |
|---|---|---|---|---|---|---|---|---|
| baseline (wire TẮT) | 12,44% | 0,65 | −46,6% | 12,13% | 14,50% | 0 | 0 | 0 |
| bản REFUTED | 12,45% | 0,65 | −46,6% | 12,14% | 14,51% | 6.691 (87,9%) | 1.132 | 412 / 54 mã |
| **sau vá (ship)** | **12,44%** | **0,65** | **−46,6%** | **12,11%** | **14,48%** | 6.603 (86,8%) | 1.044 (13,7%) | 500 / 61 mã |

Bản vá đẩy thêm 88 ô về fallback; liq CAGR về đúng baseline, core0.5/core1.0 thấp hơn baseline
0,02pp. **Không có chân nào cho lợi nhuận cao hơn** — đúng như kỳ vọng của một bản vá thu hẹp
phạm vi tin cậy, và ngược hẳn với dấu hiệu "đổi nguồn dữ liệu thấy số đẹp lên".

---

## 9. Việc B — hồi quy, ĐO chứ không giả định

Dispatch nói Việc B không cần chạy lại, nhưng bản vá **chạm đúng đường đi của nó**
(`oshares_reconciled` gọi cùng `_anchor_unverified`), nên lập luận "chặt hơn thì chỉ an toàn hơn"
là chưa đủ. Dựng lại cổng CŨ nguyên văn rồi chạy song song hai chân trên cùng rổ, cùng `asof`:

```
asof=2026-08-13  n=766
CỔNG CŨ vs MỚI trên đường đi Việc B: 0 mã đổi GIÁ TRỊ / 766
n_live cũ=632  mới=632
```

⇒ **Việc B không hồi quy.** Không đụng `rating_8l.py`.

---

## 10. Điều VẪN CHƯA chứng minh được — đọc mục này trước khi trích số ở §8

quant-skeptic yêu cầu phân rã các ô mcap đổi thành *khử look-ahead* vs *bơm lỗi*. Tôi đã thử và
**không phân giải xong**. Ghi lại cả lần thử SAI vì nó là bài học:

**Lần 1 — SAI, tôi tự bác.** Hỏi "live có khớp một dòng quý CŨ hơn không ⇒ live mang số quá khứ ⇒
lỗi". Cho ra 57 "lỗi bơm vào" / 23 "khử look-ahead". Kiểm tay hai ca thì lộ ra logic ngược: MWG
2015-02-05 live = 111.956.779 = **đúng** AIS 2015-01-05, còn số quý 139.812.680 chỉ được AIS
2015-06-22 làm hiệu lực (trễ 4,5 tháng). Một giá trị point-in-time ĐÚNG **thì tất nhiên** khớp dòng
quý cũ — đó chính là chữ ký của restatement, không phải của lỗi.

**Lần 2 — hệ quy chiếu là AIS (registry), không phải quý-so-quý.** Hỏi: số quý tại exec date có
phải số mà chỉ một AIS SAU exec date mới làm hiệu lực không?

| | ô |
|---|---:|
| ô được phục vụ | 6.603 |
| trong đó lệch ≤10% so với số quý | 6.422 |
| **lệch >10% (nhóm cần phân loại)** | **181** |
| — số quý là RESTATE ⇒ live KHỬ look-ahead (bằng chứng cứng) | 55 |
| — số quý khớp một AIS TRƯỚC đó ⇒ live nghi sai | 14 |
| — không phân loại được | 112 |

Kiểm tay nhóm 14: **CEO 2023-08-07 thực ra ĐÚNG** (số quý 257.339.985 nhảy lên 514.678.760 ngay
quý sau; live 509.5tr là ước lượng của đúng sự kiện đó). **VNE thì nghi thật** (live 90.432.953,
số quý đứng im 82.055.233 suốt 2023-10 → 2025-02, không quý nào xác nhận). ⇒ nhãn tự động **không
đáng tin ở cả hai chiều**; chỉ nhóm 55 có bằng chứng cứng.

**Vì vậy, nói thẳng:** kết quả `12,44% ≈ baseline` ở §8 **KHÔNG** chứng minh "look-ahead số CP là
vô hại". 181/6.603 ô (2,7%) dịch chuyển mạnh và phần lớn trong số đó chưa phân loại được. Điều duy
nhất kết luận được: **ở rổ này, với cap 10%/mã và 30 mã, hiệu ứng ròng lên NAV không đo được.**
Đó là một phát biểu về ĐỘ NHẠY của backtest này, không phải về tính vô hại của look-ahead.
`custom_basket.py` production vẫn **không** bị đụng và **không** re-pin gì.

---

## 11. Rủi ro tồn dư

1. **`oshares_live` gọi THẲNG vẫn sai** (IDC 3 tỷ, FPT 461,7tr). Cổng ở lớp consumer. Header file
   giờ đã cảnh báo. Chỗ vá đúng là bên trong `oshares_live` — cần vòng riêng.
2. **Cổng báo oan nhiều hơn trước**: 500 ô / 61 mã (trước 412 / 54). Chiều sai an toàn (rơi về
   hành vi hôm nay) — nhưng **đây là chiều mất phủ, không phải chiều mất tiền**. Đừng đọc 61 mã
   này là "61 mã lỗi vendor".
3. **Hỗn hợp chưa phân giải** (§10) — rủi ro nhận thức lớn nhất còn lại.
4. **`NO_PRIOR` được phục vụ mà không kiểm chứng** (§6) — phán đoán, đã đo chi phí hai chiều.
5. **27 ô lỗi thô ở dải 13–14×** chỉ được cổng biên độ chặn, không được cổng chứng nhận bắt — nếu
   ai đó nới `SANITY_FACTOR` lên >12 vì thấy "bình nguyên", sẽ mở lại đúng nhóm này. Bình nguyên
   dừng ở 12.
6. Nền tảng chưa qua burn-in: `corp_action_daily` mới lên cron 2026-08-13.

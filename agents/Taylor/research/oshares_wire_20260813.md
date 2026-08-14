# Wire `oshares_live` vào 2 consumer — Việc A (backtest PIT) + Việc B (rating live)

Job `Taylor_20260813_125526` · 2026-08-13 · Taylor · **CHỜ quant-skeptic**

---

## TL;DR

| | Kết quả |
|---|---|
| **Việc A** — `custom30_core_select_audit.py`, số CP cap-weight tại 48 ngày rebal | ĐÃ WIRE. Tác động lên lợi nhuận **≈ 0** (liq CAGR 12,44% → 12,45%, Sharpe 0,65 → 0,65, DD −46,6% → −46,6%) dù **14,9% ô mcap đổi giá trị**. |
| **Việc B** — `rating_8l.py`, số CP nuôi `ps`/`sales_yield` | ĐÃ WIRE, fail-safe. Đối chứng before/after: **1 ô số học đổi trên 30.069** (KHP `sales_yield` −0,051%, TRONG dung sai). Rating giống hệt 771/771; `top30`/`buynow`/`screener` **giống hệt từng byte**. |
| **Phát hiện ngoài kế hoạch** | `oshares_live` nhận `AIS.shares_total_after` **VÔ ĐIỀU KIỆN**. Vendor có dòng SAI. Nếu wire thẳng như dispatch mô tả, Việc A sẽ báo **+0,94pp CAGR "cải thiện" mà 100% là lỗi dữ liệu**. |

**Điều quan trọng nhất phải đọc:** con số `+0,94pp` ở trên là thật — tôi đã chạy ra nó, ở vòng wire
đầu tiên, trước khi kiểm. Nó biến mất hoàn toàn khi thêm cổng chặn lỗi vendor. Đây là ca mẫu cho
"số đẹp lên sau khi đổi nguồn dữ liệu" = phải nghi trước, mừng sau.

---

## 1. Vì sao KHÔNG thể thay thẳng (đo trước khi viết dòng code nào)

`oshares_at()` **từ chối trả lời** khi feed không đỡ nổi một con số kiểm được
(`value is None` cho `UNKNOWN_RATIO`/`NO_ANCHOR`). Đo trên rổ 108 mã thanh khoản nhất:

| ngày | `value is None` |
|---|---|
| 2014-07-01 | **33,3%** |
| 2016-01-05 | 28,7% |
| 2018-01-03 | 25,0% |
| 2020-01-06 | 12,0% |
| 2024-01-03 | 13,9% |
| 2026-08-12 | **2,8%** |

⇒ Thay thẳng trong backtest 2014 sẽ **xoá trắng 1/3 mặt cắt ngang** những năm đầu — đổi một thiên
lệch look-ahead lấy một thiên lệch *có-dữ-liệu-hay-không* to hơn và khó thấy hơn. Mọi consumer phải
có lớp dự phòng. Đó là `oshares_pit.py`.

---

## 2. `oshares_pit.py` — 2 chính sách, vì 2 rủi ro khác nhau

```
oshares_pit(tickers, asof, fallback)          # LỊCH SỬ: ưu tiên live, rơi về số quý khi live từ chối
oshares_reconciled(tickers, asof, fallback)   # SỐNG:    chỉ lấy live khi KHỚP trong EXPLAIN_TOL (0,1%)
```

`EXPLAIN_TOL` **import** từ `oshares_live`, không chép lại — cùng hằng số với cổng đối soát hằng
ngày trong `corp_action_daily.py`.

Cả hai **TOÀN PHẦN**: không bao giờ ném lỗi, không bao giờ trả thiếu mã. BQ sập / feed chết / shape
lạ ⇒ cả lô rơi về đúng giá trị caller đang dùng = đúng hành vi hôm nay.

### ⚠️ `oshares_reconciled` KHÔNG cải thiện số nào — cố ý

Khớp trong 0,1% nghĩa là hai nguồn thay thế được cho nhau. Còn **lệch** — ca DUY NHẤT mà số tươi
sẽ đổi câu trả lời (cổ tức CP 15% đã ex nhưng chưa vào dòng quý) — lại chính là ca bị đẩy về số
cũ. Wrapper vì thế **trung tính về hành vi**. Cái nó mua trong burn-in là **đếm được mỗi ngày** hai
nguồn lệch nhau bao nhiêu mã, mã nào (`data/oshares_reconcile_log.csv`).

**Lật nhánh "lệch thì ưu tiên số mới" là quyết định CHÍNH SÁCH của user sau burn-in**, không phải
mặc định module tự lấy. Tôi làm đúng như dispatch chỉ định và nêu rõ đánh đổi ở đây.

---

## 3. PHÁT HIỆN NGOÀI KẾ HOẠCH — `AIS_EXACT` là nhánh DUY NHẤT không có cổng kiểm

`oshares_live` dựng cả một cổng giải thích cho neo *dòng quý*, nhưng nhận neo *AIS* vô điều kiện:
"the registry's own statement". Số của vendor **có thể sai**.

### Ca 1 — IDC (kiểm tay, 3 nguồn độc lập bác bỏ)

```
AIS 2019-06-13   delta 109.012.000  ->  300.000.000
AIS 2020-05-28   delta 108.000.000  ->  3.000.000.000     ← 300tr + 108tr = 408tr, KHÔNG phải 3 tỷ
AIS 2022-09-05   delta  29.999.929  ->  329.999.929       ( = 300tr + 30tr, tức chuỗi thật vẫn ở 300tr )
ticker_financial: 3,0E8 suốt 8 quý sau 2020-05-28
```
⇒ `oshares_live` trả **3.000.000.000 cho mọi ngày 2020-05-28 → 2022-09-05**: sai ~10 lần, hơn 2 năm.

### Ca 2 — AAA (ca chứng minh cổng thô là KHÔNG ĐỦ)

```
AIS 2018-10-18   ->  171.199.976
AIS 2019-06-03   delta 1.700.000  ->  58.664.988          ← kỳ vọng 172.899.976
ticker_financial: 1,71199976E8 suốt 2019; AIS kế 2020-08-12 = 211.199.976 = 171,2tr + 40tr
```
58.664.988 / 171.199.976 = **0,343** — **lọt qua** cổng biên độ ×3 (biên 1/3 = 0,333) **chỉ 3%**.

### Quét toàn bảng (2.807 cặp AIS liên tiếp có đủ `shares_delta` + `shares_total_after`)

* **1.947 (69,4%)** khớp tuyệt đối.
* **110 cặp / 74 mã lệch THÔ** (40 cặp ngụ ý số trước > 2× số trước thật; 70 cặp < 1/2).
* Phần còn lại (~27%) lệch NHỎ.

Đây là **phép sàng**, không phải 110 lỗi đã xác nhận từng ca — chỉ IDC và AAA được kiểm tay.

### Cổng đã cài (lớp NGƯỜI TIÊU THỤ, trong `oshares_pit.py`, KHÔNG sửa `oshares_live`)

1. **Cổng bất biến AIS** (`_suspect_ais`) — dùng lại `oshares_live._roll`, không chép tay:
   `shares_total_after[i]` phải khớp **MỘT trong hai** đường hợp lệ —
   (a) `roll(total_after[i-1], ISS ở giữa)` hoặc (b) `total_after[i-1] + shares_delta[i]`.
   Không khớp cái nào ⇒ neo đó bị loại ⇒ rơi về số dự phòng.
   ⚠️ Bản đầu của tôi **cộng cả hai** ⇒ đếm hai lần ⇒ gắn cờ 12/12 AIS của FPT, kể cả dòng
   2025-09-12 = 1.703.507.121 mà `oshares_live._selfcheck` đã chứng minh là ĐÚNG. Đã sửa, có ca
   hồi quy (A3).
2. **Cổng biên độ** (`SANITY_FACTOR = 3,0`) — thô, bắt phần còn lại.

Cả hai chỉ **point-in-time**: AIS dated sau `asof` không được dùng để bác câu trả lời của quá khứ
(ca A5).

### 🔴 KHUYẾN NGHỊ CHO VÒNG SAU (không thuộc phạm vi job này)

Chỗ ĐÚNG để vá là **cổng nhận neo AIS bên trong `oshares_live`**, không phải lớp consumer. Hiện
`oshares_live` vẫn trả 3.000.000.000 cho IDC nếu ai gọi thẳng nó. Cần một vòng quant-skeptic riêng.
Cho tới lúc đó: **mọi consumer mới PHẢI đi qua `oshares_pit`, không gọi thẳng `oshares_at`.**

---

## 4. Việc A — `custom30_core_select_audit.py`

**Vì sao chọn file này** (đọc code, không đoán theo tên):
* Nó là **bản sao tự chứa** của `custom_basket.build_pit` (header nó tự nói vậy) ⇒ sửa nó là một
  **phép thử rủi ro 0** cho việc sửa builder production sau này, không chạm số R3 đã pin.
* Nó đã có sẵn ghi chú `PRICE BASIS (fix 2026-08-02)` giải thích chính xác lỗi cần sửa — "một
  corporate action SAU exec date không được sắp xếp lại trọng số của ngày đó" — nhưng **chỉ sửa
  nửa GIÁ của tích số**. `t.OShares` (nửa SỐ LƯỢNG) join thẳng từ `ticker_financial`, vốn là bảng
  **RESTATE** (2.667 dòng/576 mã mang số mà một AIS chỉ làm hiệu lực SAU đó, trễ tới 2.693 ngày).
  Tức đúng cái lỗi ghi chú kia mô tả vẫn đang chạy, trên thừa số còn lại.
* `mcap` chỉ được đọc ở 48 exec date ⇒ diện thay đổi hẹp và kiểm được.

**KHÔNG chọn** `custom_basket.py` (đổi số R3 đã pin — cần re-pin đầy đủ, vượt "rủi ro thấp"),
`soe_governance_screen.py` / `dcf_earning_power_test.py` (screen R&D đã đóng, chạy lại không ai đọc).

### Kết quả

```
7610 (mã,ngày) tại exec date: live=6691 (87,9%) fallback=916 none=3 | mcap ĐỔI ở 1132 ô (14,9%)
cổng hợp lý chặn 412 ô / 54 mã
```

| variant | CAGR trước | CAGR sau | Sharpe | MaxDD |
|---|---|---|---|---|
| liq (rổ parking live) | 12,44% | **12,45%** | 0,65 → 0,65 | −46,6% → −46,6% |
| core0.5 | 12,13% | 12,14% | 0,64 → 0,64 | −45,1% → −45,2% |
| core1.0 | 14,50% | 14,51% | 0,72 → 0,72 | −45,3% → −45,3% |

`nav_recon_err = 0,00 VND` cả 3 variant, SPOTCHECK PASS (5/5 giá khớp BQ) — self-check gốc của
script vẫn xanh.

**Đọc thế nào:** khử look-ahead số CP **đổi 14,9% ô trọng số nhưng KHÔNG đổi lợi nhuận** (±0,01pp).
Hợp lý về cơ chế: cap 10%/mã + 30 mã làm phẳng phần lớn sai lệch trọng số. **Đây là kết quả TỐT** —
nó nói lỗi look-ahead này không phải nguồn ảo giác lợi nhuận trong họ custom30, và do đó
`custom_basket.py` (production) **không gấp** phải re-pin vì lý do này.

### Bảng chứng minh vì sao phải có cổng

| cấu hình | liq CAGR | ΔCAGR |
|---|---|---|
| baseline (chưa wire) | 12,44% | — |
| wire thẳng, **không cổng nào** | **13,38%** | **+0,94pp** ← toàn bộ là lỗi vendor |
| + cổng biên độ ×3 | 12,43% | −0,01pp |
| + cổng bất biến AIS (**ĐANG SHIP**) | 12,45% | +0,01pp |

---

## 5. Việc B — `rating_8l.py`

**Điểm nối** (xác nhận bằng grep: `OShares` chỉ xuất hiện ở 3 dòng — SQL 97, và 545-546):
```python
out["ps"] = Price * OShares / Revenue_TTM      # -> sales_yield = 1/PS, một trục của composite v3
```
Sống thật: `pt_8l_daily.sh` cron 17:45 ICT → `data/rating_8l*.csv` → `newdeals_daily_report.py`,
`dc_book_waterfall_paper.py`, screener.

**Cách nối:** một hàm `_reconcile_oshares(df)` gọi ngay sau `bq(MAIN_SQL)` — thay đúng MỘT cột, ở
MỘT chỗ, trước mọi phép tính. Rollback = `OSHARES_RECONCILE=0` (một biến môi trường).

### Ca đối chứng THẬT (chạy 2 lần trên cùng dữ liệu 2026-08-13)

```
OSHARES_RECONCILE=0  ->  /tmp/r8l_off/*.csv
OSHARES_RECONCILE=1  ->  data/*.csv
```
| file | kết quả |
|---|---|
| `rating_8l_top30.csv` | **giống hệt từng byte** |
| `rating_8l_buynow.csv` | **giống hệt từng byte** |
| `rating_8l_screener.csv` | **giống hệt từng byte** |
| `rating_8l.csv` | **1 ô đổi / 30.069 ô số học**: KHP `sales_yield` 13,9351 → 13,928 (**−0,051%**) |
| cột `rating` | **771/771 giống hệt** |

Ô duy nhất đổi là ca "hai nguồn khớp trong dung sai nhưng không bằng nhau tuyệt đối" ⇒ lấy số mới,
nhích 0,051%. Đúng thiết kế.

### Số burn-in ngày đầu (`data/oshares_reconcile_log.csv`)

```
asof=2026-08-13 n=771  khớp(dùng live)=637 (82,6%)
                       lệch -> giữ số cũ            = 71 (9,2%)
                       nghi lỗi dữ liệu -> giữ số cũ= 42 (5,4%)
                       live từ chối                 = 10
                       thiếu cả hai nguồn           = 11
```
Đây là con số cần theo dõi: **~9% universe mỗi ngày có bất đồng số CP**, **~5% có nghi vấn lỗi
vendor**. Cả hai hiện đều giải quyết bằng cách giữ số bq_admin.

---

## 6. Selfcheck

| file | kết quả |
|---|---|
| `oshares_pit.py --selfcheck` | **37/37 PASS** — 20 ca hermetic (monkeypatch, cache rỗng, KHÔNG chạm BQ), 11 ca toàn-phần/lỗi, 6 ca dữ liệu BQ thật |
| `oshares_wire_selfcheck.py` | **11/11 PASS** — hermetic |
| `oshares_live.py --selfcheck` (không sửa, kiểm hồi quy) | 22/22 PASS |
| `mike/bin/corp_action_daily.py --selfcheck` (không sửa, kiểm hồi quy) | 127/127 PASS |
| self-check gốc của `custom30_core_select_audit.py` | PASS (nav_recon_err 0,00 VND × 3) |

`bin/selfcheck_scope_map.sh` xác nhận **không selfcheck nào khác** import `rating_8l` hay
`custom30_core_select_audit` ⇒ §23 phạm vi hẹp là đúng, không phải bỏ sót.

**Mọi ca "chặn được" đều có ca CHỨNG MINH NGƯỢC** (bỏ cổng ra thì giá trị sai THẬT SỰ lọt vào):
G6 (biên độ, 3 tỷ lọt), A6 (bất biến AIS, AAA 58.664.988 lọt), W7 (không có gì chặn thì số THẬT SỰ
đổi được — nếu W2-W6 "không đổi" chỉ vì đường ống tắc thì W7 sẽ đỏ).

§5b: `append_log()` bị chặn khi `MIKE_BOT_TEST_MODE=1` — selfcheck không được ghi vào chính sổ mà
burn-in dùng để đếm. Ca Z1 kiểm điều đó (6 dòng test đã lọt vào một lần và đã dọn).

---

## 7. RỦI RO TỒN DƯ — công bố hết

1. **`oshares_live` vẫn sai cho IDC/AAA nếu gọi THẲNG.** Cổng nằm ở lớp consumer. Consumer mới
   phải đi qua `oshares_pit`. Vá gốc = việc của vòng sau.
2. **Cổng bất biến AIS gắn cờ 412 ô / 54 mã trong rổ 171 mã (32%)** — cao hơn nhiều tỉ lệ lỗi THÔ
   (3,9%). Phần lớn là lệch NHỎ mà tôi **chưa kiểm từng ca**. Chi phí của cờ sai chỉ là "rơi về
   hành vi hôm nay" (an toàn, mất phủ), nhưng đừng đọc "54 mã lỗi vendor" — đúng nghĩa là "54 mã
   có ít nhất một AIS không tự giải thích được".
3. **`SANITY_FACTOR = 3,0` là lập luận, không phải số đo.** Thưởng 1:2 (×3) là sự kiện thật hiếm
   nhưng có; đúng biên vẫn được nhận (ca G2). Nếu VN có đợt chia ×3 thật, cổng biên độ sẽ để lọt
   (đúng ý) và cổng bất biến mới là lớp chặn.
4. **Việc B trung tính về hành vi theo thiết kế** (§2). Đừng báo cáo nó như "rating giờ dùng số CP
   tươi".
5. **Nền tảng chưa qua burn-in.** `corp_action_daily.py` mới lên cron hôm nay, chưa quan sát một
   lượt vendor đổi lô hay backfill thật nào. Cả hai wire đều fail-safe nên không tăng rủi ro, nhưng
   không nên coi là đã kiểm chứng trong sản xuất.
6. **Tôi KHÔNG re-pin gì.** R3/V2.4 và `custom_basket.py` không bị đụng.

---

## 8. File đổi

| file | trạng thái |
|---|---|
| `oshares_pit.py` | MỚI — 2 adapter + 2 cổng + selfcheck 37 ca |
| `oshares_wire_selfcheck.py` | MỚI — selfcheck điểm nối, 11 ca |
| `custom30_core_select_audit.py` | +30 dòng (Việc A) |
| `rating_8l.py` | +45 dòng: `_reconcile_oshares()` + 1 dòng gọi trong `main()` (Việc B) |
| `data/oshares_reconcile_log.csv` | MỚI — sổ đếm burn-in |

## 9. Cách tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source wc_env.sh
PYTHONDONTWRITEBYTECODE=1 python3 oshares_pit.py                  # 37/37
PYTHONDONTWRITEBYTECODE=1 python3 oshares_wire_selfcheck.py       # 11/11
PYTHONDONTWRITEBYTECODE=1 python3 custom30_core_select_audit.py   # Việc A
OSHARES_RECONCILE=0 python3 rating_8l.py   # chân đối chứng; diff data/*.csv với chân bật
```

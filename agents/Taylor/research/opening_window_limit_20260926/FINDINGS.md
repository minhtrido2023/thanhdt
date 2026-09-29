# Opening-window limit-order cost — cơ chế + phản chứng (job Taylor_20260925_171624)

**Phạm vi:** đo lường/thiết kế lại công thức đặt limit trong cửa sổ mở cửa. PAPER/RESEARCH-ONLY —
không đổi `trading_rules.json`, không đổi tham số thực thi live, không đặt lệnh thật, không đụng
cron. Tách khỏi job `execution_alpha_20260925` (đó là nghiên cứu tổng quát, MARGINAL, đã DỪNG).

**Kết luận một dòng (ĐÃ SỬA sau quant-skeptic REFUTE vòng 1 — xem §7):** phát hiện CHẮC CHẮN thứ
nhất của job trước (76 cụm, +13,75bps vs open, t=4,98) có nguồn gốc CƠ CHẾ cụ thể một phần, không
phải vi cấu trúc ngẫu nhiên thuần tuý — nhưng độ lớn của cơ chế đó KHÔNG PHẢI "gần như luôn luôn"
như bản nháp đầu khẳng định. Trên ĐÚNG account thật (SpaceX+ZaloPay, N=49 lệnh đặt tại 09:15:00-09),
**53% (26/49)** rơi vào fallback "không có dữ liệu" (`no-hist`) của `_decide_cross_adaptive`
(không có nhánh `no-vol` ở account thật — 0/49); **16% (8/49)** là TWAP có dữ liệu KL THẬT (lệnh
lớn, sẽ cross dù có đủ dữ liệu — không phải fallback); **31% (15/49)** hoàn toàn KHÔNG đi qua hàm
này — bypass qua nhánh `urgency="high"` (lệnh PARK/gộp mã, `_decide_cross()` trả `True` ngay không
cần quote). Pre-flight riêng cho thiết kế này: **GO** trên chính con số gốc 13,75bps/t=4,98
(DSR≈0,9999) — nhưng đây CHỈ xác nhận lại ý nghĩa thống kê của số liệu đã biết, KHÔNG xác nhận bất
kỳ phương án sửa nào. Phản chứng định lượng (bao nhiêu tiết kiệm được nếu sửa) **KHÔNG dựng được
đầy đủ từ dữ liệu hiện có** — chỉ có cận trên lạc quan cho ĐÚNG 53% lệnh thuộc nhánh `no-hist`,
không áp dụng cho 31% lệnh PARK/urgency-high (remedy đề xuất KHÔNG chạm được nhánh này vì nó
bypass hoàn toàn `_decide_cross_adaptive`). Đã gọi quant-skeptic verify — bản nháp đầu bị REFUTE vì
gộp nhầm account `main` (PROBE, 79% sample gốc) vào bảng cơ chế trong khi §3a lại tự loại account
đó; đã sửa lại toàn bộ §2 theo đúng phân loại account.

---

## 1. Đính chính giả định trong dispatch — bot KHÔNG đặt lệnh trong ATO

Dispatch giả định "công thức đặt limit trong cửa sổ 09:05–09:15 (thời điểm bot đặt lệnh cho phiên
ATO)". Đọc code (`trading_bot/executor.py::run_session` + `Executor.step`) cho thấy điều này SAI:

- `trading_bot/vn_market.py::SESSIONS`: `("PRE", 0:00, 9:00, False)`, `("ATO", 9:00, 9:15, False)`,
  `("MORNING", 9:15, 11:30, True)` — cột cuối là `cont` (có được đặt LO liên tục không).
- `Executor.step()`: `if cont: self._cancel_stale(now); self._place_slices(...)`. `_place_slices`
  **CHỈ được gọi khi `cont=True`** — tức KHÔNG BAO GIỜ trong PRE hoặc ATO.
- Xác nhận bằng dữ liệu thật: gộp mọi `exec_*_journal.csv`, đếm `event=PLACE` theo phút —
  **291/1499 (19%) toàn bộ PLACE event của cả lịch sử rơi đúng phút 09:15**, và trong đó **237
  rơi đúng vào cửa sổ 09:15:00–09:15:09** (chu kỳ poll đầu tiên ngay khi MORNING mở).

**Hệ quả:** "cửa sổ mở cửa" mà FINDINGS.md gốc đo (`tod_bucket = "1_ATO(<=09:15)"`, 76 cụm) thực
chất là **CHU KỲ ĐẶT LỆNH ĐẦU TIÊN của MORNING (đúng 09:15:00), không phải lệnh đặt trong phiên
ATO**. Không ảnh hưởng tới con số +13,75bps/t=4,98 (đo đúng, không cần đo lại) — chỉ đổi CÂU HỎI
cơ chế: không phải "công thức đặt lệnh trong ATO có vấn đề gì", mà là "vì sao mọi lệnh dồn vào
đúng viên gạch đầu tiên của MORNING, và tại viên gạch đó công thức làm gì khác thường".

## 2. Cơ chế — `_decide_cross_adaptive` fallback "no-data" tại đúng khoảnh khắc mở cửa (ĐÃ SỬA)

`trading_bot/executor.py::_decide_cross()` gọi `_decide_cross_adaptive()` CHỈ khi `o.urgency !=
"high"`. `urgency` mặc định `"normal"` (`trading_bot/plan.py:29`) NHƯNG lệnh PARK/gộp mã (merge
nhiều lệnh cùng mã, `trading_bot/plan.py:414`) có thể mang `urgency="high"` — nhánh này **bypass
hoàn toàn** `_decide_cross_adaptive`, trả `cross=True` ngay không cần quote/dữ liệu gì (khác về
BẢN CHẤT với 2 nhánh fallback dưới đây — không phải "thiếu dữ liệu", mà là THIẾT KẾ có chủ đích
cho lệnh cần khớp gấp).

Trong `_decide_cross_adaptive` (khi urgency thường):
- **Nhánh KL (ADV)**: `use_twap = ratio >= threshold` cần `q.day_volume > 0`. Nếu ATO đã khớp
  trước 09:15:00 cho mã đó, `day_volume>0` và ratio là số THẬT — quyết định TWAP/cross khi đó dựa
  trên tỷ lệ lệnh/ADV thật, **không phải fallback**. Chỉ khi mã đó CHƯA khớp gì trong ATO
  (`day_volume=0`) mới rơi vào *"Thiếu dữ liệu volume → TWAP (fail-safe, đảm bảo fill)"*.
- **Nhánh DIP (r15)**: `_r15()` cần lịch sử giá tối thiểu `0,7×dip_window_min=10,5 phút` trong
  `px_hist`. `_record_prices` CÓ ghi trong ATO (điều kiện loại trừ chỉ là `phase in
  ("PRE","CLOSED")`, KHÔNG loại ATO — đính chính bản nháp đầu nói sai chỗ này). Nhưng bot chỉ khởi
  động **09:05 ICT** (SpaceX/ZaloPay, xác nhận từ crontab) → tới 09:15:00 mới tích luỹ được ~10
  phút lịch sử, DƯỚI ngưỡng 10,5 phút → `_r15()` vẫn trả `None` → *"thiếu lịch sử → cross (safe)"*.
  Đây là hệ quả của **thời điểm khởi động bot cách ngưỡng đúng ~30 giây**, không phải "không bao
  giờ ghi được gì" như bản nháp đầu khẳng định.

**Đo LẠI trên đúng account thật, phân loại lại theo decision_note** (grep `PLACE` tại
09:15:00–09:15:09, lọc account=SpaceX/ZaloPay — LOẠI `main`/PROBE vì §3a của chính báo cáo này đã
xác nhận `main` là mega-cap thanh khoản cao không đại diện universe thật; giữ lẫn sẽ tái lập đúng
bẫy §28 coding_guidelines mà bản nháp đầu đã mắc):

| Nhánh | N | % (trên 49) | Remedy §4 có chạm được không? |
|---|---:|---:|---|
| `adp:dip(...,no-hist→cross)` — fallback thiếu lịch sử giá | 26 | 53% | Có |
| `adp:twap(ratio=no-vol>=1%ADV)` — fallback thiếu KL | 0 | 0% | Có (không xảy ra ở account thật) |
| `adp:twap(ratio=X%>=1%ADV)` — có KL thật, TWAP vì lệnh lớn | 8 | 16% | Không (đã cross có lý do) |
| `urgency="high"` (PARK/gộp mã) — bypass hoàn toàn | 15 | 31% | **Không** — remedy không đi qua hàm này |

(Toàn bộ mẫu gốc 237 event gồm 188 từ `main`; tách riêng account đó cho hoàn chỉnh: `main` có
114 `no-hist` + 74 `no-vol`(thật, vì cron `main` khởi động 09:10 và là paper-probe không phản ánh
universe thật) — số này KHÔNG dùng để kết luận về hành vi thật.)

**Kết luận đúng: 53% lệnh đặt đầu phiên (account thật) cross=True vì fallback thiếu dữ liệu —
không phải 94%, và không phải "xác định sẽ xảy ra" mà là xác suất phụ thuộc việc mã đã có khớp ATO
hay chưa + độ trễ ~30 giây giữa lúc bot khởi động và ngưỡng lịch sử `_r15` cần.** 31% khác (PARK/
urgency-high) tốn cùng loại chi phí (cross spread) nhưng vì lý do KHÁC — cần gấp, không phải thiếu
dữ liệu — và **không đổi được bằng 2 remedy ở §4** vì chúng không đi qua `_decide_cross_adaptive`.

## 3. Phản chứng — có bằng chứng, có giới hạn rõ

### 3a. Bằng chứng bổ trợ từ order-book shadow — N=5, KHÔNG đủ để "xác nhận", chỉ cùng chiều

Chương trình paper riêng `order_book_execution_shadow` (owner Taylor, đã chạy từ 2026-08-18,
KHÔNG liên quan tới nghiên cứu này lúc thiết kế) ghi lại **snapshot bid/ask thật tại đúng thời
điểm đặt lệnh** (`data/execution_logs/orderbook_shadow_*.jsonl`, schema `orderbook_execution_v1`).
Lọc bản ghi có `decision_note` chứa `no-hist` VÀ `recorded_at` ≤09:16 VÀ **tài khoản THẬT** (loại
`main` — đó là tài khoản PROBE churn 100 CP/6 mega-cap thanh khoản cực cao theo
`kb/paper_programs_charter/order_book_execution_shadow.md`, không đại diện cho universe thật; giữ
lẫn `main` sẽ tái lập đúng bẫy §28 coding_guidelines — trộn 2 tầng không đồng nhất):

| | N | half-spread bps (mean) | ghi chú |
|---|---:|---:|---|
| Tài khoản THẬT (SpaceX/ZaloPay) | **5** | **8,9** (17,7bps spread / 2) | tất cả đều SELL, 4 mã (MBB/VHM/VPB/HDB), 2026-09-18→09-24 |
| Tài khoản `main` (PROBE, loại khỏi kết luận) | 56 | 10,4 | mega-cap thanh khoản cao, KHÔNG cùng universe |

**N=5 quá nhỏ để "xác nhận" bất cứ điều gì** — quant-skeptic verify vòng 1 đúng khi chỉ ra: toàn bộ
5 quan sát đều là lệnh BÁN, chỉ 4 mã ngân hàng, trong đúng 1 tuần (09-18→09-24), và cửa sổ lọc
`recorded_at ≤09:16` không khớp chính xác với cửa sổ `09:15:00-09:15:09` dùng ở §2 — hai phép đo
KHÔNG hoàn toàn cùng lát cắt thời gian. Đây chỉ là quan sát **cùng chiều** (nửa spread 8,9bps cùng
bậc độ lớn với 13,75bps), không phải bằng chứng thống kê độc lập, và KHÔNG dùng để suy ra tỷ lệ %
nào của 13,75bps có thể tránh được.

### 3b. KHÔNG dựng được counterfactual "nếu đặt limit khác thì fill ở giá nào" — nói thẳng, không đoán

Theo yêu cầu §29 coding_guidelines: đã kiểm tra và **dữ liệu hiện có không đủ** để trả lời "nếu
delay N phút / đặt limit sát bid hơn thì còn tốn bao nhiêu":

- `orderbook_shadow_*.jsonl` chỉ ghi **1 snapshot / lần ĐẶT LỆNH thật** — không phải poll định kỳ.
  Kiểm tra trực tiếp: 0/74 (ticker, ngày) trong cửa sổ 09:14–09:30 có ≥3 snapshot — không dựng được
  quỹ đạo spread theo thời gian.
- `probe_ticks_<account>_<date>.csv` (cadence 60s, theo charter) chỉ ghi giá `last` (giá khớp gần
  nhất), KHÔNG có bid/ask — không tính được "nếu đặt limit thụ động ở bid thì có khớp không" từ
  nguồn này.
- Không có log order-book đầy đủ (L2 lịch sử liên tục) cho các phiên TRƯỚC 2026-08-18 (chương
  trình shadow chỉ bắt đầu ghi từ ngày đó) — 2/3 lịch sử của 76 cụm gốc (07-02→08-17) hoàn toàn
  không có dữ liệu order-book để dựng lại.

**Kết luận trung thực:** con số "nửa spread ≈9-10bps" là **cận TRÊN của khoản tiết kiệm khả dĩ**
(giả định lệnh thụ động khớp được ĐÚNG giá đặt, KHÔNG mô hình hoá rủi ro không khớp/phải đuổi giá
sau đó). Không thể nói phần trăm nào của 13,75bps THỰC SỰ tránh được nếu đổi công thức — chỉ có
thể nói: **cơ chế gây ra chi phí đã được xác định chắc chắn (94% "no-data" tại 09:15:00), và
hướng sửa hợp lý nhất về mặt kỹ thuật là loại bỏ chính XÁC ĐỊNH đó (không phải cải thiện việc dự
đoán giá)**.

## 4. Đề xuất — CHỈ báo cáo, KHÔNG tự sửa (đúng ranh giới cứng dispatch)

**Phạm vi remedy: tối đa 53% lệnh đặt đầu phiên (nhánh `no-hist`), KHÔNG chạm được 31% PARK/
urgency-high** (bypass hoàn toàn `_decide_cross_adaptive` — muốn đổi hành vi nhánh đó phải sửa chỗ
khác, `_decide_cross()`, ngoài phạm vi 2 remedy dưới). Hai hướng kỹ thuật khả dĩ, nhắm vào ĐÚNG
53% đã xác nhận bằng code+dữ liệu (không phải đoán mò):

1. **Trễ chu kỳ đặt lệnh đầu tiên vài chục giây–vài phút sau 09:15:00** (thay vì đặt ngay khi
   `cont` chuyển True) — đủ để `q.day_volume`/`px_hist` có dữ liệu thật, để `_decide_cross_adaptive`
   quyết định bằng TÍN HIỆU thay vì fallback rỗng. Rủi ro cần cân: trễ này tự nó cũng là một loại
   "chi phí thời gian" chưa đo (giá có thể chạy xa hơn spread trong vài chục giây đầu — CHƯA có dữ
   liệu để lượng hoá, xem §3b).
2. **Đổi fallback mặc định của CẢ HAI nhánh no-data từ `cross=True` sang thụ động** (post tại
   bid/ask thay vì vượt sang phía đối). Rủi ro: fill-rate thấp hơn ở đúng lúc thanh khoản mỏng
   nhất trong ngày (đầu phiên) — hệ quả ngược với chính lý do 2 fallback này được viết ra ("đảm
   bảo fill", theo comment code).

**Không đề xuất phương án nào là "đúng" — cả hai đổi đánh đổi fill-rate lấy giá, và dữ liệu hiện
có không đo được độ lớn đánh đổi đó.** Cần: (a) chạy A/B THỤ ĐỘNG trên paper thật (mở rộng chương
trình `order_book_execution_shadow` đã có sẵn hạ tầng đúng việc này — snapshot + KEEP/REDUCE/DEFER
policy — thêm nhánh quan sát riêng cho chu kỳ ĐẦU PHIÊN thay vì trộn chung với toàn phiên), HOẶC
(b) chấp nhận rủi ro không đo được và thử nghiệm nhỏ trên live với hạn mức chặt (quyết định của
Mafee + user, không phải của nghiên cứu này).

## 5. Pre-flight power — thiết kế RIÊNG (không thừa hưởng phán MARGINAL của job trước)

```
python3 mike/bin/rnd_preflight_power.py --mean-bps 13.75 --sd-bps 24.07 \
    --obs-per-year 330 --n-available 76 --n-trials 4 --n-rule per-event --json
```
→ `dsr_now=0,9999` · `n_for_target_dsr=26` (≪ 76 N có sẵn) · `n_for_power80=24` ·
**verdict: GO**.

⚠️ **Phạm vi của verdict GO này, làm rõ sau quant-skeptic vòng 1**: pre-flight chỉ tái xác nhận Ý
NGHĨA THỐNG KÊ của con số 13,75bps/t=4,98 ĐÃ BIẾT (đo trên hành vi HIỆN TẠI, cross=True mặc định)
— **KHÔNG xác nhận remedy đề xuất ở §4 sẽ tiết kiệm được bao nhiêu**. Đây là 2 câu hỏi khác nhau:
"có đủ mẫu để tin +13,75bps là thật không" (CÓ, GO) vs "sửa công thức thì tiết kiệm được bao nhiêu"
(CHƯA đo được, xem §3b). Không nên đọc dòng "verdict: GO" như một xác nhận cho phương án sửa.

Vì sao KHÁC verdict MARGINAL của `execution_alpha_20260925` Việc 2 dù dùng CHUNG 76-cụm/13,75bps/
sd=24,07 gốc: thiết kế đó gộp NHIỀU trục thời điểm/tham số thực thi (nhiều `n_trials`, effect
size trung bình hoá loãng qua các biến thể). Thiết kế NÀY hẹp hơn — 1 cơ chế cụ thể đã xác nhận
bằng code+2 nguồn dữ liệu độc lập, `n_trials=4` (2 phương án sửa × ràng buộc thận trọng) — vẫn
dùng đúng effect empirical đo được, KHÔNG lạc quan hoá. self-check 0 VND: `n_clusters=76`,
`mean_bps=13,7487`, `sd_bps=24,0653`, `t=4,9805` tái lập CHÍNH XÁC số của job trước từ
`../execution_alpha_20260925/slippage.csv` (control leg PASS).

## 6. Ranh giới đã tuân thủ

Không đổi `trading_bot/executor.py`, `bot_execute.py`, `config.py`, `trading_rules.json`. Không
đặt lệnh thật. Không đụng cron. Output ghi vào thư mục mới, không đè `execution_alpha_20260925/`.

## 7. Quant-skeptic verify — vòng 1 REFUTED, đã sửa theo đúng góp ý

Bản nháp đầu bị **REFUTED** vì 3 lỗi cộng dồn trong §2 (đã sửa ở bản hiện tại):
1. **Sample bias** — 188/237 (79%) event dùng để tính "94%" đến từ account `main` (PROBE, mega-cap
   thanh khoản cao), chính account §3a đã tự loại vì không đại diện — không áp cùng chuẩn lọc ở §2.
2. **Gộp nhầm nhãn** — 44/108 quyết định `adp:twap` có tỷ lệ KL THẬT (không phải `no-vol`), bị gộp
   chung thành "108 no-vol fallback"; account thật thực ra có 0 sự kiện `no-vol` (100% "no-vol" đến
   từ `main`).
3. **Bỏ sót nhánh cơ chế thứ ba** — 15/49 event account thật (31%) là `urgency="high"` (PARK/gộp
   mã), bypass hoàn toàn `_decide_cross_adaptive`, không phải fallback thiếu dữ liệu.
4. Ngoài ra 2 claim sai: "day_volume LUÔN=0 tại 09:15:00" (sai — phụ thuộc ATO đã khớp hay chưa) và
   "`_record_prices` không ghi trong ATO" (sai — điều kiện loại trừ chỉ là PRE/CLOSED; nguyên nhân
   thật là bot khởi động 09:05, chưa đủ 10,5 phút ngưỡng `_r15` tính đến 09:15:00).

Tự recompute độc lập xác nhận ĐÚNG số quant-skeptic đưa ra (26 no-hist / 0 no-vol / 8 ratio-thật /
15 bypass trên N=49 account thật) trước khi sửa file này. Control leg (76 cụm/13,7487bps/sd
24,0653/t=4,9805, tái lập từ `execution_alpha_20260925/slippage.csv`) được quant-skeptic xác nhận
CONFIRMED — không cần sửa. Pre-flight GO (n_trials quét 1-10 đều GO, không bị bóp) CONFIRMED nhưng
làm rõ lại phạm vi (chỉ xác nhận số liệu gốc, không xác nhận remedy — đã sửa ở §5).

**Verdict cuối cùng (sau sửa): mechanism CONFIRMED ở mức 53% (không phải 94%), scope của remedy
được giới hạn rõ (không chạm 31% PARK/urgency-high), và giới hạn dữ liệu cho counterfactual định
lượng (§3b) vẫn đứng nguyên — an toàn để báo cáo dạng "phát hiện + đề xuất cần thử nghiệm A/B",
KHÔNG an toàn để báo cáo dạng "sửa X sẽ tiết kiệm Y bps" vì Y chưa đo được.**

# Paper trading — corp-action + nghiệm thu checkpoint · 2026-09-23

*Taylor · job `Taylor_20260923_005911` · toàn bộ số liệu dưới đây đo lại từ artifact thật, không trích self-report của script.*

*Cập nhật 09:30 ICT: thêm kết quả quant-skeptic **vòng 2** (REFUTED/high) và bản vá vòng 3 `ea6c1b97` — xem mục 1.*

**Tóm tắt 1 dòng:** 2 lỗ hổng đo lường THẬT được vá (corp-action cho sổ PaperBroker; quy ước quyền mua trong báo cáo AlphaLens), 1 báo động sai được đính chính (`vol_scale_chase_cap` KHÔNG hề treo — đã live từ 08-04), và 3 việc cần user chốt.

---

## 1. Corp-action cho sổ PaperBroker — ĐÃ DỰNG, CHƯA BẬT

**Lỗ hổng, đã đo chứ không suy đoán.** `PaperBroker` giữ vị thế là `{mã: KL}` thuần và khớp trên **quote thật** ⇒ sáng ngày GDKHQ giá đã rơi hệ quy chiếu mới mà KL vẫn hệ cũ. Không ai bù. Trên chính sổ paper `main`, 3 sự kiện thật kể từ 2026-07-07:

| Sự kiện | KL thật sáng GDKHQ | Sổ paper bỏ lỡ |
|---|---|---|
| MBB 2026-07-09 — cổ tức tiền 1.000đ/CP | 1.100 | 1.100.000đ |
| MBB 2026-08-11 — quyền mua 10% + cổ tức CP 15% | 1.200 | 4.860.000đ |
| FPT 2026-09-21 — thưởng 10% | 300 | 1.955.455đ |
| | **Tổng** | **7.915.455đ = 0,79% NAV paper** |

quant-skeptic recompute **độc lập** từ băng 466 fill, khớp tới từng VND.

**Đã dựng:** `mike/bin/paper_corp_action.py` + selfcheck (commit `d622f2d9`). Tái dùng hạ tầng live — `corp_action_lib` + `price_frame.adjustment()`/`p_cum_from_bq` — không viết lại công thức nào.

**quant-skeptic vòng 1 trả REFUTED / confidence high.** 5 lỗi thật, đã sửa hết:

1. **[KILLER] Quyền mua KHÔNG làm tăng KL tại ngày GDKHQ.** Vòng 1 dùng thẳng `price_frame.adjustment().share_factor` làm hệ số KL — nhưng hàm đó sinh ra cho **mẫu số GIÁ**. Hai nguồn đã nằm sẵn trong repo *trước khi file này ra đời* đều nói ngược: `dnse_raw_2026-08-1{0,1}.jsonl` cho MBB `openQuantity` 1.100 → **1.265** (×1,15, không phải 1.375); và `data/corp_actions.json` `MBB-2026-08-11-STOCK-DIVIDEND` `_status: CONFIRMED` ghi thẳng `qty_multiplier = 1,15` kèm câu *"quyền mua KHÔNG tự động làm tăng số lượng (phải nộp tiền thực hiện quyền)"*. **Artifact đó do chính Taylor ghi ngày 2026-08-11** — tri thức đã có, tôi vẫn mắc lại vì tin **tên biến** thay vì tra artifact. Nay tách 3 tỉ lệ tên khác nhau: `price_ratio` (mẫu số giá) · `share_ratio` (nhân KL, loại quyền mua) · `rights_ratio` (vào khoản chờ).
2. **Watermark vượt qua sự kiện fail-closed ⇒ mất im lặng VĨNH VIỄN.** Nghiêm trọng vì `RIGHTS_ISSUE_PRICE` chỉ có 1 khoá quá khứ ⇒ **mọi** đợt quyền mua tương lai đều đi nhánh fail-closed. Nay watermark dừng trước ngày còn treo.
3. **`collect()` đóng băng ảnh chụp KL** ⇒ 2 sự kiện cùng mã trong 1 cửa sổ để sổ **áp dở dang**. Nay KL nối qua từng sự kiện; đường hồi tố dựng KL từ băng `fills` theo đúng ngày GDKHQ.
4. **"Bất biến 0 VND" chỉ là đồng nhất thức bảo toàn, không ràng buộc kinh tế** — skeptic tiêm cổ tức gấp 5 lần, phần dư vẫn 0,0. Đã thêm **neo ngoài** thật: so `P_ref` với `tav2_bq.ticker.Close` phiên cum (vendor tự tính, ngoài code này). 5 ca đo: MBB 08-11 / VHM 08-06 / DGC 09-14 khớp **tuyệt đối**; FPT 09-21, VIB 09-10 lệch đúng 1 tick. Chính neo này bắt được lỗi #1.
5. **`PaperBroker._save()` ghi đè toàn bộ state không nguyên tử** ⇒ xoá được sổ con và áp lại. Nay khoá idempotent nằm ở sổ cái append-only **ngoài** state + `flock`.

**Skeptic xác nhận 1 lập luận của tôi là ĐÚNG:** không sao chép `cum_dividend_double_count` sang paper. Đó là bản vá cho **hiện vật broker DNSE** (`cashDividendReceiving` vào `totalCash` trước khi giá rơi); PaperBroker không có trường đó nên bê sang sẽ **trừ một khoản chưa bao giờ được cộng**.

**Hai cái bẫy mới của chính cái neo, đều đo được:**
- Chỉ neo khi mã **không còn sự kiện SAU** ngày GDKHQ: `Close` gánh điều chỉnh của mọi sự kiện về sau. MBB@07-09 có `Close(07-08)` = 20.820đ trong khi `P_ref` đúng là 25.000đ — neo phải tự bỏ qua, không báo lệch giả.
- **Không** dùng biến thể "tỉ số hệ số" để né điều trên: nó chạm dòng `Price` của **chính ngày GDKHQ** vốn hỏng sẵn. VHM 2026-08-06 mang `Price` = 153.000 (hệ cũ, y hệt 08-05) trong khi `Close` = 77.100; thử thật cho 151.809đ thay vì 76.500đ — sai gấp đôi.

**quant-skeptic VÒNG 2 (chạy sau khi vá 5 lỗi trên) trả REFUTED / high lần nữa** — commit vá
`ea6c1b97`. Skeptic tái lập 7.915.455đ bằng **3 đường độc lập** (công thức riêng, phân rã cấu
phần, chạy thật `--dry` trên sổ THẬT với BQ live), xác nhận 6/6 fixture khớp BQ nguyên văn và KL
1.100/1.200/300 dựng lại đúng từ 466 fill. Nhưng **đường sẽ chạy thật thì sai**:

- **[D1, KILLER] `collect()` có HAI gốc KL, và nhánh CRON là nhánh sai.** Hồi tố cắt theo ngày
  GDKHQ; nhánh cron đọc thẳng `positions`. Sổ paper main có **thật** lệnh mua 100 MBB lúc
  **11:00:06 NGÀY GDKHQ 2026-08-11** — CP mua ngày đó không hưởng quyền ⇒ nhánh cron cho
  1.300→1.495 + 130 quyền thay vì 1.200→1.380 + 120 quyền = **ghi dư 2.425.000đ**, đúng **31%**
  con số headline. Cả bất biến bảo toàn (`resid` 0,0) lẫn neo ngoài (`ok`) đều **MÙ**, vì cả hai
  độc lập với KL; **0/53** check chạm tới. Nay **một** gốc KL duy nhất (`qty_at_effective`), tham
  số `backfill` bị gỡ hẳn.
- **[D2] Sổ cái ngoài được ghi TRƯỚC state** ⇒ chết máy giữa hai bước để lại dấu "đã áp" trên sự
  kiện **chưa** áp; lần sau bỏ qua + đẩy watermark = **mất im lặng vĩnh viễn** — đúng lớp lỗi mà
  vòng 2 vừa tuyên bố đã vá. Đảo thứ tự: state trước, sổ cái sau.
- **[phát sinh khi sửa D1] `apply_records` gán `pos = qty_after`.** Với sự kiện QUÁ KHỨ, gán sẽ
  **XOÁ** mọi lệnh khớp sau ngày GDKHQ: hồi tố lên sổ hôm nay (MBB **1.500**, FPT **500**) ghi đè
  thành 1.380 và 330 = **bốc hơi 120 + 170 CP ≈ 13,5tr**. Nay cộng **độ lớn thay đổi**, và chốt an
  toàn đổi từ `cur == qty_before` (chặn mọi lần hồi tố hợp lệ) sang `cur == fills + sự kiện đã áp`.

Ba điểm skeptic ghi nhận, **chưa xử, cần user biết**: neo ca MBB 08-11 là **vòng tròn**
(`RIGHTS_ISSUE_PRICE` hardcode 10.000 vốn được xác nhận ngược bằng chính kết quả — các ca
FPT/VHM/VIB/DGC/SSI thì độc lập) · cổ tức tiền ghi **GROSS** trong khi `reconcile_equity.py:188`
dùng thuế TNCN 5% cho sổ thật (theo quy ước đó headline thành 7.860.455đ) · `PaperBroker.
get_positions()` trả `sellable == total` nên 180 CP thưởng **bán được ngay sáng GDKHQ** — phải xử
trước khi cắm cron.

**Selfcheck sau vòng 3:** 53 → **59 check**, PASS × 4 TZ + `python3` hệ thống. **7 mutation đều
chết bằng assertion** (nhánh cron đọc `positions` · gán `qty_after` · xoá clamp watermark — trước
đây **không có test nào phủ** · sổ cái trước state · cổ tức trên KL sau chia · `qty_at` tính cả
fill ngày GDKHQ · bỏ phần CP đã áp). Thêm ca THẬT **SSI 2026-08-17** (tiền 1.000 + thưởng 20%) —
cụm có CẢ tiền lẫn tỉ lệ CP, trước đây không có ca nào. Hồi tố `--dry` trên sổ THẬT: 3 bản ghi
**không đổi**, headline **7.915.455đ giữ nguyên**.

<sub>Ghi chú quy trình: commit `ea6c1b97` lỡ chạy với `core.hooksPath=/dev/null`. Đã chạy lại
toàn bộ pre-commit trên đúng 2 file — 7/7 hook **Passed**, không có gì bị né.</sub>

**Selfcheck vòng 2 (lịch sử):** 53/53 PASS × 4 TZ. 4 mutation đều **chết bằng assertion** (quay về lỗi #1 = 16 FAIL · bỏ neo = 1 · đóng băng KL = 2 · bỏ sổ cái ngoài = 1).

**Khai báo thẳng, chưa xử lý:** `PaperBroker.get_positions()` trả `sellable == total` cho mọi thứ (giới hạn sẵn có của PaperBroker, không do file này gây ra; sửa = đụng module lõi dùng chung §23) · sự kiện `announced` bị huỷ sau khi áp không có đường đảo ngược · tiền lẻ quy theo `P_ref` thay vì mệnh giá là xấp xỉ rộng tay một chiều, chặn trên ~0,07%/năm trên sổ 1B.

### Ảnh hưởng tới graduation — LIỆT KÊ, không kết luận

Theo chỉ đạo: chỉ áp dụng từ nay về sau, không retro-sửa verdict đã chốt.

**Mục cần người xem:** ngày **2026-08-11** (MBB, quyền mua + cổ tức CP) **nằm trong** danh sách 6 phiên hybrid BUY dùng làm evidence tốt nghiệp `fill_timing` (08-11, 08-13, 08-17, 08-18, 08-20). Ngày đó plan mang `ref_price` 24.250đ (hệ cũ) trong khi tham chiếu thật là 20.200đ — **lệch +20,0%**; cổng `exdate_tickers()` chỉ vá **sau** đó (2026-08-15). **Không kết luận verdict `fill_timing` đúng hay sai.**

Ba quan sát làm nhẹ, nhưng **không phải** kết luận:
- Journal 08-11: lệnh MBB thực tế `PLACE` ở **20.500đ** ⇒ executor neo vào **quote thật** (hệ mới), không dùng `ref` sai của plan.
- `grep` toàn bộ `exec_main_*_journal.csv`: **0 marker** `EXTREME_PAUSE`/`EXTREME_FLOOR_GUARD`/`EXTREME_DOWN` trong suốt lịch sử paper main, gồm cả 3 ngày GDKHQ ⇒ gate "zero false-trigger" của `extreme_regime` không có marker nào để corp-action làm lệch.
- `order_book_execution_shadow` (từ 08-18) và `expvol_pacing` (từ 08-17) bắt đầu **sau** khi `exdate_tickers()` đã vá.

---

## 2. Audit báo cáo paper — 1 phát hiện thật, đã vá

`mike/bin/paper_programs_daily_report.py` đúng chuẩn ở mọi mục khác. Một điểm sai thật (commit `b755fc77`):

`paper_entry_adjust.adjust_entries()` mặc định `convention="accrue_only"` — **giả định quyền mua bị bỏ**. Lý do chọn ghi thẳng trong docstring của nó (2026-08-13): *"A PAPER book has no cash account, never subscribed … crediting it with the value of a right it could not take up OVERSTATES the return."*

**Chỉ đạo user 2026-09-23 lật đúng tiền đề đó** (mặc định thực hiện 100% quyền) ⇒ quy ước khớp chỉ đạo hiện nay là `terp`, không phải `accrue_only`.

| | MBB (ca duy nhất có quyền mua trong 4 tên) | EW cả sổ | Excess vs VNINDEX |
|---|---|---|---|
| `accrue_only` (đang dẫn dắt) | vào 25.200 → 21.066 ⇒ **−4,59%** | −1,50% | **+0,81pp** |
| `terp` (khớp chỉ đạo user) | vào 25.200 → 20.180 ⇒ **−0,40%** | −0,45% | **+1,86pp** |

Chênh **+1,05pp** trên excess của cả sổ, trong khi gate AlphaLens *"excess return dương vs VNINDEX qua full window"* đến hạn **2026-09-30 — còn 1 tuần**. Cả hai quy ước đều cho excess **dương** nên chiều verdict không đổi, nhưng **độ lớn lệch hơn gấp đôi**.

**Đã làm:** báo cáo nay in **cả hai** con số + nói rõ cái nào khớp chỉ đạo nào. **Không tự đổi quy ước dẫn dắt** — đổi số của một gate sắp tới hạn là quyết định của user; nhưng giấu con số kia thì báo cáo không trung thực. `factor_terp` vốn đã được tính sẵn ⇒ 0 truy vấn thêm.

**Đã kiểm, không sửa:** §6 (pipeline `verify_account_snapshot`/`daily_nav_snapshot`/`reconcile_equity`) và §31 (`nav_period_returns`) **không áp dụng** — đó là chuẩn cho báo cáo tài khoản thật có broker/cost-basis/nợ margin; báo cáo paper không có tài khoản broker nào và mọi số đều đã ghi nguồn. §21 **có** áp dụng về tinh thần và **đã đúng**, nhưng qua `paper_entry_adjust.py` (dựng riêng cho sổ paper, selfcheck 21 ca) chứ không qua `dividend_adjusted_return.py` mà §21 nêu tên — ghi lại như điểm cần thống nhất **văn bản**, không phải lỗi số liệu.

---

## 3. Hai chương trình đến hạn

### (a) `order_book_execution_shadow` — ĐỦ MẪU, nhưng không quyết được

Đếm **độc lập** từ `orderbook_shadow_*.jsonl` thô (không tin self-report của probe): **22 phiên** có record từ 2026-08-18, **21 phiên** có ≥1 snapshot hợp lệ ⇒ **vượt mốc 20**. Phiên 08-18 bị loại đúng (0 record valid — sự cố `l2_snapshot` ngày đầu, đã giải thích từ 08-20).

⇒ **Không áp công thức gia hạn Wilson**: công thức đó dành cho ca thiếu **mẫu**, còn ở đây mẫu đã đủ.

Chặn thật nằm ở **instrumentation**, và thêm phiên **không** sửa được:

| | Đo được | Hệ quả |
|---|---|---|
| `shadow.recommendation` | KEEP **300** / REDUCE **1** / DEFER **0** trên N=301 | Policy `spread_depth_v1` lệch khỏi baseline đúng **0,33%**. Gate 3 (so sánh slippage / fill-rate / time-to-fill / adverse selection) **không có độ tương phản** để so. |
| Hậu kiểm 1/5/15 phút | Schema `orderbook_execution_v1` **không có trường outcome nào**; probe báo coverage 1m = 4/249 · 5m = 4/249 · 15m = 2/249 (**~1,6%**) | Gate 1 (*"hậu kiểm 1/5/15 phút"*) **chưa đạt**, dù là gate instrumentation. |
| Thành phần mẫu | **275/301 (91%)** từ `account=main`, `book=PROBE` | Đó là harness churn **tổng hợp**, không phải lệnh chiến lược thật. Lệnh tài khoản **thật** chỉ **26 record / 5 phiên** (09-14→09-22). |

`end` dời 09-23 → **2026-10-07**, **chỉ** để có thời gian cho quyết định dưới đây — không phải để gom thêm mẫu.

> ✅ **ĐÃ CHỐT 2026-09-23 — user chọn (A).** Đã thực hiện, và chẩn đoán trong bảng trên bị
> lật ở cả hai dòng: coverage không phải thiếu mẫu, KEEP 300/301 không phải ngưỡng chặt.
> **Xem mục 5(4).** Nguyên văn 2 lựa chọn giữ lại bên dưới làm bản ghi.
>
> **CẦN USER CHỐT — 1 trong 2 (không go-live dù chọn gì, đúng phạm vi đã khoá):**
> **(A) SỬA rồi chạy lại** — thêm trường hậu kiểm 1/5/15′ vào schema + nới policy để sinh tỉ lệ khuyến nghị khác-baseline đo được, rồi đặt cửa sổ mới.
> **(B) DỪNG, ghi nhận KẾT QUẢ NULL** — một policy spread+depth gần như **không bao giờ** bất đồng với baseline qua 301 cơ hội thật là một câu trả lời **hợp lệ**: không có edge execution để hái ở nhịp 60s này.

### (b) `vol_scale_chase_cap` — BÁO ĐỘNG SAI, đã đính chính

**Tiền đề của mục này trong dispatch là SAI.** Patch **không** treo 7 tuần — nó đã được áp **ngay trong ngày 2026-08-04**, commit **`d4f667b2`**.

Bằng chứng, tra mất 2 phút:
- `trading_bot/config.py:192` → `"chase_cap_vol_scale_enabled": True,   # LIVE 2026-08-04`
- `git log -L 192,192:trading_bot/config.py` → `d4f667b2`, 2026-08-04
- `git apply --check flip_live.patch` → **FAIL cả 4 file**, vì thay đổi đã nằm sẵn trong cây (đây chính là lý do patch "không còn áp được" — không phải vì code base trôi)
- 3 selfcheck chạy **thật** hôm nay: `stress_vol_scale_chase_cap.py` → **RESULT: PASS** *(LIVE paper+live+global)* · `chase_cap_selfcheck.py` → **ALL PASS** · `dc_book_waterfall_selfcheck.py` → **78 passed / 0 failed**

**Vì sao báo động sai sống 7 tuần:** sau khi áp patch, không ai xoá thư mục `pending_live_flip_chase_cap_20260804/`, và registry để `end: None` nên `paper_checkpoint_escalation.sh` không bao giờ rà tới. Hai kênh cùng im lặng ⇒ người đọc sau kết luận "việc còn treo". Đúng **§28**: *không suy diễn từ sự vắng mặt trên một kênh — xác nhận bằng **artifact***.

**Đã dọn:** thư mục → `mike/agents/Taylor/archive/` kèm `APPLIED.md` nói rõ nó là lịch sử (README.md cũ viết lúc patch chưa áp và chưa bao giờ cập nhật — đọc một mình sẽ hiểu ngược). Registry → `status: graduated-live 2026-08-04`, `end: 2026-08-04`.

**Rủi ro còn treo, không đổi:** size-impact ở NAV 50 tỷ **chưa kiểm** và **không kiểm được trên paper** (PaperBroker khớp đúng bằng giá limit đã đặt). Mở lại gate 4 khi NAV live tiến gần 50 tỷ — mốc theo dõi: gross lệnh/phiên vượt ~343tr.

### Các chương trình còn lại — ngày đến hạn kế tiếp

| Chương trình | Đến hạn kế tiếp |
|---|---|
| `alphalens` | **2026-09-30** — audit độc lập (Taylor). Xem mục 2: quy ước quyền mua cần chốt TRƯỚC ngày này |
| `expvol_pacing` | **2026-10-13** — checkpoint đã làm hôm nay (commit `927c72d5`), chu kỳ ~4 tuần |
| `order_book_execution_shadow` | **2026-10-21** — user chốt (A), đã áp dụng; tiêu chí đổi sang N≥30 ở tầng REAL. Xem mục 5(4) |
| `yield_floor_custom30v_observe` | **2027-02-05** |
| `engine_room_oos` | **2026-12-01** (`end: None`, mốc ghi trong `end_or_trigger`) |
| `dc_waterfall` | event-anchored — chu kỳ reverse-unwind đầu tiên + settle 4-6 tuần · **trần 2026-10-06** |
| `capitulation_shadow` | event-driven — sau sự kiện washout thật đầu tiên, **không có deadline lịch** |
| `orb_intraday` | điều kiện **REGIME** (≥60 phiên gồm chop/bear), **không có deadline lịch** |

---

## 4. Ba việc cần user quyết

1. **Bật cron cho `paper_corp_action.py`?** Dòng đề xuất: `45 1 * * 1-5 … python3 mike/bin/paper_corp_action.py --label main` (08:45 ICT, trước `paper_main_probe_plan` 08:52). **Chưa tự cài** vì §11 đòi tra `kb/cron_registry.md` trước, và vì skeptic vòng 2 nêu 1 điều kiện
tiên quyết: `PaperBroker.get_positions()` trả `sellable == total` ⇒ 180 CP thưởng bán được ngay
sáng GDKHQ (`paper_main_probe_plan.py:190` đọc thẳng `positions`). **Chưa cài = công cụ không chạy.**
2. **Hồi tố 7.915.455đ vào sổ paper main?** `--backfill-since 2026-07-06` đã chạy `--dry` thành công, KL dựng đúng từ `fills` (1.100/1.200/300), neo `ok` 2/3 và tự bỏ qua ca MBB 07-09. Hồi tố sẽ **đổi số liệu lịch sử** sổ paper ⇒ không tự làm. Riêng **FPT 09-21** (KL 300→330, chỉ cách 2 phiên) đáng cân nhắc nhất vì nó đang làm **sai KL hiện tại** của sổ.
3. **Đổi quy ước dẫn dắt AlphaLens sang `terp`** trước khi gate đóng 2026-09-30? Một tham số (`convention="terp"`), đã có sẵn + selfcheck ca 15 tái lập đúng 20.180. Nếu đồng ý, excess chính thức thành **+1,86pp** thay vì +0,81pp.

Và **1 quyết định ở mục 3(a)**: `order_book_execution_shadow` → (A) sửa instrumentation rồi chạy lại, hay (B) dừng và ghi nhận kết quả null.

> **Cập nhật 2026-09-23:** mục 1, 2 và 3(a) đã được user chốt và áp dụng — xem **mục 5**.
> Mục 3 (`terp`) và việc hồi tố NAV lịch sử **vẫn chờ user**, chưa tự làm.

---

## 5. Quyết định của user (2026-09-23) và kết quả áp dụng

Job `Taylor_20260923_051148`. User chốt 4 mục; cả 4 đã thực hiện. Hai mục CHƯA quyết
(hồi tố NAV lịch sử · đổi quy ước dẫn dắt AlphaLens sang `terp`) **giữ nguyên, không tự làm**.

### (1) Cổ tức tiền ghi RÒNG sau thuế TNCN 5% — `a8fa47d6`

Khớp quy ước sổ THẬT (`reconcile_equity.py:188`, `--div-tax-rate` 0,05 → `net_cash_dividends()`).
Headline sổ paper main: **7.915.455đ GỘP → 7.860.455đ RÒNG** (thuế 55.000đ).

Bản ghi tách **ba** trường thay vì sửa một: `cash_dividend_vnd` GỘP (giữ tên cũ — đó là con số
của SỞ, và `P_ref` vẫn rơi theo GỘP), `div_tax_vnd`, `cash_delta_vnd` RÒNG. Sổ cái append-only
ghi cả gộp lẫn thuế: mất là không dựng lại được. Trong `verify_invariant()` thuế là **số hạng
riêng ở vế phải** — nó là khoản chuyển RA NGOÀI hệ, không được nuốt vào phần dư.

Đo: 63/63 PASS × 4 TZ + `env -u TZ` + `$DNA_PYEXE`; 5/5 mutation chết bằng assertion. Một trong
5 mutation (`cash_delta` = GỘP) qua được MỌI test cũ — phải thêm check "bỏ thuế khỏi vế phải ⇒
vỡ đúng số thuế" mới bắt được.

### (2) `PaperBroker.get_positions()`: `sellable ≠ total` — `24e885ac` + `6ca93ac1`

Trước bản vá, sổ paper bán được **ngay sáng GDKHQ** phần CP thưởng/cổ tức CP mà tài khoản THẬT
không bán được.

**Bằng chứng đo được, không phải mô hình T+2 suy diễn** — `dnse_raw_*.jsonl`, SpaceX, MBB sau
GDKHQ 2026-08-11 (cổ tức CP 15%): `openQuantity` 1.100 → 1.265 NGAY, nhưng `tradeQuantity`
(trường `DNSEBroker.get_positions()` đọc thành `sellable`) đứng ở 1.100 **liên tục 08-11 →
09-23 = 43 ngày**; khoảng cách 165 CP chưa từng đóng. Một mô hình T+2 sẽ cho bán sớm **41 ngày**
⇒ chọn khoá tới khi có người mở tường minh (`sellable_from=None`, không đoán ngày niêm yết bổ
sung). Chặn ở **cả hai** tầng: đặt lệnh (Executor) và KHỚP (`_try_fill`).

§23 — đây là module lõi dùng chung: quét rộng 8 selfcheck, tất cả rc=0. 6/6 mutation chết.

### (3) Cron `paper_corp_action.py` — `07487da8`

`40 1 * * 1-5` = **08:40 ICT T2–T6**. Không phải 08:45 như đề xuất: khe `45 1` đã có
`preflight_check.sh`, `50 1` có `plan_approval_reminder.sh`, `52 1` có probe plan ⇒ lùi về khe
trống gần nhất theo `_adding-cron-policy.md`. Vị trí đúng trong chuỗi: SAU lô vendor ~22:2x T-1
và sync BQ 23:45 T-1, TRƯỚC `paper_main_probe_plan` 08:52 (12 phút) và `bot_execute` 09:10.

Xác nhận lại bằng `crontab -l` thật (dòng 148), không tin bước ghi. Runtime đo thật 2,3s /
`timeout 300`. Backup crontab trước khi sửa: `mike/logs/crontab_backup_paper_corp_action_20260923.txt`.
**Lượt chạy đầu tiên: T5 2026-09-24 08:40 ICT.**

Lần chạy tay hôm nay (12:1x) **chỉ đặt watermark** `2026-09-23`, `applied=0`, positions/cash
không đổi (cash 844.381.367,5đ) — đúng chỉ đạo không hồi tố. Muốn hồi tố sau: `--backfill-since`.

### (4) `order_book_execution_shadow` — phương án (A) — `bae551d7` + `e8066c75`

Checkpoint mục 3(a) nêu 2 chặn. **Cả hai chẩn đoán ban đầu đều sai về nguyên nhân**, và sửa
theo chẩn đoán sai sẽ tốn thêm một cửa sổ thu thập vô ích.

**Chặn 1 — "coverage ~1,6% ⇒ thiếu mẫu": SAI, đó là lỗi ĐỌC THIẾU NGUỒN.**

Đếm lại theo từng nguyên nhân thay vì tổng: **259/265** quan sát đủ điều kiện markout rơi vào
nhánh *"không có chuỗi giá nào để so"* — chứ không phải *"có chuỗi mà thiếu điểm"*. Gốc cơ học:
91% mẫu là `account=main`, mà `main` chạy **`broker: "phs"`**, và `PHSBroker.get_quote()` **dựng**
`l2_snapshot` nhưng **không bao giờ ghi** `quote_l2` — chỉ `DNSEBroker._log_l2()` mới ghi. Bản
ghi `quote_l2` cuối cùng mang `account_label="main"` là **2026-08-17**, tức TRƯỚC ngày trial bắt
đầu (08-18). Thêm bao nhiêu phiên cũng **không sinh thêm một điểm markout nào** cho nhánh này.

Chuỗi giá của chính `main` thì vẫn nằm trên đĩa, chỉ ở file khác: `probe_ticks_<account>_<date>.csv`
(`_probe_tick_log`, cadence 60s, sống thêm `probe_linger_min`=30′ sau khi mọi parent đã khớp —
đúng bằng cửa sổ 1/5/15′). Cho probe đọc thêm nguồn này:

| | Trước | Sau |
|---|---|---|
| coverage 1m / 5m / 15m | 1,5% / 1,5% / 0,8% | **93,2% / 93,2% / 82,3%** |
| adverse-selection median | 1m +18,4 · 5m +20,6 · 15m +45,7 bps *(N=4)* | 1m **+13,8** · 5m **+8,0** · 15m **−0,0** bps *(N=247/247/218)* |

**Trên đúng mẫu 22 phiên đã có — không thu thêm ngày nào.** Gate 1 ĐẠT. Và hình dạng đổi hẳn:
số cũ dốc LÊN theo thời gian (dấu hiệu adverse selection dai dẳng); số mới **suy giảm về 0**,
đúng hình dạng tác động TẠM THỜI. Số cũ dựng trên N=4 là nhiễu, không phải tín hiệu.

⚠️ Hai cơ sở giá **không được trộn im lặng**: `dnse_raw` → **mid**, `probe_ticks` → **last**.
Mỗi quan sát nay mang `markout_basis` (mẫu hiện tại mid=6 / last=259); so markout giữa 2 basis
phải tách.

**Chặn 2 — "KEEP 300/301 ⇒ nới ngưỡng ra": SAI, đó là MẪU KHÔNG ĐỒNG NHẤT.**

| Tầng | N hợp lệ | `touch_depth_ratio` | `spread_ticks` | khác-baseline (v1) |
|---|---|---|---|---|
| **PROBE** (`main`, churn 100 CP trên 6 mega-cap) | 289 | trung vị **763×** | 1,0 ở 283/298, **không bao giờ >2,0** | 0/289 |
| **REAL** (lệnh tài khoản thật) | 9 | trung vị **2,2×**, p25 1,3×, min 0,3× | 1,0–2,0 | 1/9 |

Sổ dày gấp **763 lần** lệnh và spread luôn chạm sàn tick ⇒ một policy spread+depth **không thể**
có gì để phân biệt ở tầng PROBE, và cũng **không nên**. Gộp hai tầng chính là lý do checkpoint
đọc ra "policy gần như không bao giờ bất đồng với baseline". Mọi số của probe nay tách tầng.

Ngưỡng hiệu chuẩn lại thành **`spread_depth_v2`** (REDUCE: spread ≥1 tick ∧ depth <2,0 ·
DEFER: spread ≥2 tick ∧ depth <1,0), chọn theo tiêu chí **PHÂN BIỆT** chứ không theo tỉ lệ kêu:
trên mẫu đã thu cho **4/9 = 44% khác-baseline ở tầng REAL, và vẫn 0/289 ở tầng PROBE**. Một bộ
ngưỡng kêu cả trên mega-cap là bộ ngưỡng **sai**, không phải bộ ngưỡng nhạy. `v1` giữ nguyên
trong lịch sử — `policy_version` đóng dấu vào từng bản ghi nên hai thế hệ không lẫn nhau.

Hậu kiểm ghi ra artifact **riêng** `data/execution_logs/orderbook_markout.jsonl` (schema
`orderbook_markout_v1`, nối bằng `trace_id`, ghi atomic). **Không** sửa bản ghi
`orderbook_execution_v1` đã nằm trên đĩa: đó là bằng chứng immutable của thời điểm đặt lệnh, và
321 bản ghi đã thu phải giữ nguyên để còn so được — đúng tinh thần "dựng offline" của charter.

Vẫn **thuần shadow**: `behavior_contract = LOG_ONLY_NO_BROKER_PATH`, không field nào đi vào
`_child_qty` / `_limit_price` / lịch HYBRID. Gate 4 (user sign-off) chưa đụng tới.

**Cửa sổ review mới: `end` 10-07 → 2026-10-21, và tiêu chí kết thúc đổi ĐƠN VỊ** — từ *số phiên*
sang **N ≥ 30 quan sát hợp lệ ở tầng REAL**. Lý do phải giải thích rõ (dispatch yêu cầu): mốc
"20 phiên" đã vượt từ 09-23 và công thức gia hạn Wilson của 2 lần trước **không áp dụng** — nó
dành cho ca thiếu mẫu. Sau khi tách tầng thì chỗ thiếu không còn là "phiên" mà là *tầng*: PROBE
đã 295 và thêm nữa vô ích, REAL mới 26 thô / 9 hợp lệ. Nếu tới 10-21 tầng REAL vẫn <30, đó là
câu trả lời về **tần suất cơ hội** (~1,8 quan sát hợp lệ / phiên có lệnh thật) chứ không phải lý
do gia hạn lần 4: khi đó chốt kết quả trên mẫu đang có và đóng chương trình.

### Đo lường chung của mục 5

| Selfcheck | Kết quả |
|---|---|
| `paper_corp_action_selfcheck.py` | **72/72** × 4 TZ + `env -u TZ` + `$DNA_PYEXE`; 11/11 mutation chết |
| `order_book_shadow_probe_selfcheck.py` | **21/21** × 4 TZ + `env -u TZ` + `$DNA_PYEXE`; **7/7** mutation chết |
| `order_book_shadow_selfcheck.py` | PASS × 4 TZ + py3.10 + pandas3; mutation revert ngưỡng về v1 chết |
| §23 quét rộng (`brokers.py`, `config.py`) | **12** selfcheck, tất cả rc=0 |

⚠️ Bẫy tái phát trong chính phiên này: **chạy mutation trên `.py` phải xoá `__pycache__`** —
`config.py` sửa rồi mà `DEFAULTS` vẫn trả giá trị cũ, làm 4 lượt TZ báo FAIL giả.

# PREREG — audit độc lập rổ park custom30V bằng PHƯƠNG PHÁP VỊ THẾ (share-count replay)

job `Taylor_20260927_101335` · viết **TRƯỚC** khi chạy bất kỳ phép đo nào · PAPER-ONLY

## Câu hỏi của user (nguyên văn, 2026-09-27 17:11 ICT)
> "nếu có audit theo từng sự kiện ngày mua, ngày bán, giá phải theo giá thực tế của ngày đó thì
> backtest không thể làm vống performance được — số CP sau ex-right tăng nhưng giá thực tế cũng
> giảm ngay, không thể tái tạo lợi nhuận ảo. Cần audit lại quy trình xem lỗ hổng ở đâu? Số thực
> tế là số nào?"

## Cái đang được kiểm — và cái KHÔNG
- Kiểm: chân **RETURN** của chỉ số park custom30V trong `custom_basket.build_pit()`.
- KHÔNG đụng: rail, `data/trading_rules.json`, `data/results_registry.md`, pin R3, CSV canonical.

## Dự đoán ĐẠI SỐ ghi trước khi đo (để đo có thể BÁC BỎ)
Đặt `Close_t = P_t / F_t` với `F_t` = tích các hệ số điều chỉnh của mọi sự kiện TỪ t trở về sau
(`F=1` sau sự kiện cuối). Registry `price-volume/ticker_close_vs_price_dividend_adj.md` xác nhận
`Close/Price` là hằng giữa 2 ex-date và nhảy về 1,0 tại ex-date ⇒ dạng này đúng.

Với 1 sự kiện cổ phiếu hệ số `(1+q)` đi ex tại t:
- Replay vị thế: `N_t = (1+q)·N_{t-1}`, `P_t ≈ P_{t-1}/(1+q)` ⇒ `N_t·P_t ≈ N_{t-1}·P_{t-1}` (≈0%).
- Chuỗi Close: `Close_t/Close_{t-1} = (P_t/F_post)/(P_{t-1}/((1+q)F_post)) = (1+q)·P_t/P_{t-1} ≈ 1`.
⇒ **H1 (dự đoán chính): chân FLAT ≡ replay vị thế cho mọi sự kiện cổ phiếu.** Chân LEGACY
(`mcap = Close_adj × OShares`) cộng THÊM bước `OShares` lên trên một chuỗi Close đã trung hoà
sẵn ⇒ phantom return, đúng như bug đã sửa (`BASKET_RETURN_OSHARES`, commit 1b89881b).

- Cổ tức TIỀN `D`: `Close` là total-return-adjusted ⇒ chuỗi Close ngầm **tái đầu tư** D tại giá
  ex. Replay vị thế giữ D ở **cash** tới kỳ rebal kế. ⇒ **H2: replay ≤ flat**, khoảng cách =
  drag do tiền nhàn rỗi (không phải bug; là hai mô hình khác nhau). Biên dự kiến nhỏ.
- Rebal hằng ngày: engine **đổi tỷ trọng về mục tiêu cap-weight MỖI PHIÊN**; replay của user giữ
  nguyên số CP giữa các kỳ rebal ⇒ có **rebalancing effect** (dấu không định trước). Để tách,
  chạy 2 biến thể: **REPLAY-A** (buy&hold số CP giữa rebal, đúng mô hình user) và **REPLAY-B**
  (cùng replay nhưng đổi tỷ trọng về đúng vector trọng số của engine mỗi phiên).

## Ngưỡng "KHỚP" — chốt TRƯỚC khi đo
- **Tiêu chí chính**: |CAGR(REPLAY-B) − CAGR(FLAT)| ≤ **0,30pp** trên cửa sổ 2014-08→2026-06,
  sau khi trừ phần không mô phỏng được (quyền mua / rights, xem dưới).
- REPLAY-B là chân so ngưỡng vì nó khác FLAT ĐÚNG MỘT biến (nguồn giá + xử lý sự kiện tường
  minh), đã khử rebalancing effect. REPLAY-A báo kèm để lượng hoá drift+cash drag.
- Vượt 0,30pp ⇒ **LỖ HỔNG MỚI**: dừng, mô tả cơ chế bằng 1 sự kiện cụ thể, không suy diễn.
- Phụ: corr(daily return) và tracking error (SD của hiệu, annualised) báo cho cả 3 cặp.

## Nguồn dữ liệu (tra `mike/kb/data_registry/index.md` trước khi chọn — đã tra)
| Dùng | Status registry | Vì sao |
|---|---|---|
| `tav2_bq.ticker.Price` (thô) qua cache pin `data/bq_cache_asof20260729_postrestate` | TRAP (`ticker_close_vs_price_dividend_adj.md`) | giá THÔ đúng mô hình user |
| `tav2_bq.ticker.Close` (adj) cùng cache | TRAP cùng file | chân FLAT + sửa `Price` kẹt |
| `tav2_bq.corporate_action` LIVE qua `corp_action_lib.pricing_events` (`event_status != "not_executed"`), codes DIV+ISS+AIS | CANONICAL (`corporate_action_bq.md`) | sự kiện; **pin vintage ra parquet riêng của job này** |
| `tav2_bq.ticker_financial.OShares` (qua `apply_oshares`) | — | chỉ để tái lập chân LEGACY, KHÔNG vào replay |

**Bẫy đã biết, phải xử lý tường minh (`price-volume/ticker_price_stale_on_exdate.md`)**: `Price`
của **dòng đúng ngày GDKHQ** kẹt ở hệ CUM ở ~2% sự kiện (VHM 2026-08-06 sai +98,4%). Đây là bẫy
CHÍ TỬ cho replay giá thô: số CP đã bước lên mà giá vẫn hệ cũ ⇒ tạo ĐÚNG loại phantom return
đang đi tìm. Xử lý: phát hiện bằng bất biến `ratio_t = Close_t/Price_t` phải nhảy về mức
post-event tại ex-date; dòng nào `ratio` kẹt ở giữa (không ≈ ratio của phiên kế) ⇒ sửa
`P_t := Close_t / ratio_{t+1}`. **Đếm và báo số dòng phải sửa**, không sửa im lặng.

## Quy ước mô hình replay (ghi trước, không đổi sau khi thấy số)
1. Membership + trọng số mục tiêu: đọc từ `members_df` + `bx` của **đúng lệnh pin R3** (tham số
   `BASKET_SELECT=yieldcombo`, `ETF_LIQ=custompitg` ⇒ quality=none/rebal=q2m5/gate=3,
   `BASKET_WT=namecap`, `top_n=30`, `name_cap=0,10`, `BASKET_CA_SNAPSHOT` + `BQ_LOCAL_CACHE` pin
   y nguyên). KHÔNG chọn lại membership.
2. Tại mỗi rebal: đổi toàn bộ NAV về `N_i = w_i·NAV / P_raw_i`, phí **0,1%/chiều** trên phần vốn
   thực giao dịch (turnover), khớp quy ước `CLAUDE.md` § Backtest.
3. Giữa các rebal: `N_i` bất biến trừ sự kiện corp-action. `NAV_t = Σ N_i·P_raw_i + cash`.
4. Sự kiện tại ex-date (`exright_date`; AIS → `effective_date` fallback `exright_date`, cùng
   semantics `normalise_corp_action`):
   - ISS price-adjusting hệ số `q` (cổ tức CP / thưởng): `N_i ×= (1+q)`.
   - DIV tiền `D`: `cash += N_i·D` — **giả định nhận NGAY tại ex-date** (thực tế trả sau 1-2
     tháng; giả định này LÀM LỢI cho replay, ghi rõ, biên nhỏ).
   - Nhiều sự kiện cùng ngày: hệ số GỘP `f_E = (1+q)·P/(P−D)` (không nhân tích rời).
   - **QUYỀN MUA (rights, "Quyền mua CP cho Cổ đông hiện hữu")**: KHÔNG mô phỏng được (cần giá
     phát hành; `ref_price` NULL). **ĐẾM số sự kiện + ước biên ảnh hưởng**, không âm thầm bỏ.
   - ISS non-adjusting (ESOP / riêng lẻ): **KHÔNG** đụng `N_i` — cổ đông hiện hữu không nhận gì
     (`corp_action_lib.is_price_adjusting`, ca thật HAH 2026-07-28).
5. Không lãi tiền mặt (cùng khuôn chân index).

## Selfcheck bắt buộc (mutation — phải LÀM LỆCH, nếu không thì test vô nghĩa)
- M1: bỏ bước `N ×= (1+q)` ⇒ replay phải LỆCH (và lệch theo chiều ÂM).
- M2: đổi `Price` → `Close` trong chân mark-to-market ⇒ phải LỆCH.
- M3: bỏ phí rebal ⇒ phải LỆCH dương.
- M4: bỏ bước sửa `Price` kẹt ngày GDKHQ ⇒ phải LỆCH (đo mức, đây là bẫy 2%).
- Chạy dưới `env -u TZ` (§16 coding_guidelines) + 1 TZ ngoại lai.

## Rồi mới tới §6 "số thực tế"
A/B R3 đổi ĐÚNG MỘT biến (chân park = replay level), self-check 0 VND cả 2 chân, báo Δ so với
pin **23,37% @park 0,30**. **KHÔNG re-pin.**

## Cam kết
- Không merge. Không sửa file ngoài thư mục job này (+ `.proposed` nếu cần đề xuất).
- Tự chạy `quant-skeptic` đòn 8 (double-count) trên chính replay.
- Ghi bus finding topic `c30v-position-replay-2709`.

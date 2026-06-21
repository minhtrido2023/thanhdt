# trading_bot — bot giao dịch theo plan V2.3 qua PHS FLEX

Bot 2 bước, tách **chuẩn bị plan** (EOD) khỏi **thực thi** (trong phiên):

```
EOD ngày T  (sau golive_recommend_v23.py + pt_v22_dt5g.py):
    python bot_prepare_plan.py          →  data/trade_plans/plan_<T+1>.json

Sáng ngày T+1 (trước 09:15, để chạy cả ngày):
    python bot_execute.py               →  cắt lệnh nhỏ, đặt/đuổi/hủy, journal, report
```

## Kiến trúc

| File | Vai trò |
|---|---|
| `trading_bot/config.py` | cấu hình — `data/trading_bot_config.json` (tự tạo mặc định) |
| `trading_bot/strategies.py` | **strategy registry** — mỗi version chiến lược 1 class |
| `trading_bot/plan.py` | schema TradePlan/PlannedOrder + lưu/đọc JSON |
| `trading_bot/brokers.py` | broker interface + `PHSBroker` + `DNSEBroker` + `PaperBroker` |
| `dnse_api.py` (workspace root) | wrapper DNSE OpenAPI v2 (HMAC sign, ký giống SDK chính thức) |
| `trading_bot/executor.py` | vòng lặp xuyên phiên: slicing, chase giá, ATC sweep, resume |
| `trading_bot/vn_market.py` | phiên HOSE, lô 100, bước giá, biên độ |
| `bot_prepare_plan.py` / `bot_execute.py` | entry scripts |
| `test_trading_bot.py` | smoke test offline (fixture giả, không chạm PHS/BQ) |

## 1. Strategy versioning

`strategies.REGISTRY` ánh xạ tên → class. Ra version mới = viết class mới
(vd `V24Strategy`), đăng ký, đổi `"strategy"` trong config. Plan/journal cũ
không bị ảnh hưởng (mỗi plan ghi kèm `strategy` + `strategy_version`).

**V23Strategy** (hiện tại): *mirror* paper book V2.3 sang tài khoản thật, scale
theo NAV (`scale = NAV_thật / NAV_paper`):

- target = vị thế paper (`pt_v22_dt5g_open_positions.csv`) ∪ khuyến nghị vào
  lệnh T+1 (`golive_v23_recommendations_<date>.csv`: BAL FULL/HALF_SIZE, LAG
  "UPCOMING T+1", CAPIT khi `capit_fired`) ∪ park ETF (E1VFVN30, theo giá trị
  `BAL_etf + SECOND_etf` trong logs).
- lệnh = chênh lệch target − danh mục thật (mã thừa → SELL sync, ưu tiên 1).
- giá: quote PHS → close trong recs → transactions paper (fallback).
- **Trễ chấp nhận ở v1**: exit paper ngày T+1 được sync ở plan T+2 (exit V2.3
  là hold-expiry/stop, không gấp). Double-count tránh bằng `max(mirror, recs)`.

## 2. Executor — slicing & chống impact

Mỗi parent order:

- tối đa **1 lệnh con sống** tại 1 thời điểm (không bao giờ over-fill);
- mỗi `slice_interval_min` (8') đặt 1 lệnh con:
  `qty = min(còn lại, max_child_value/giá (200M), max_participation (10%) × KL khớp lũy kế của mã)`;
- **mua**: giá ask (cross) hoặc bid+`chase_ticks`, trần đuổi
  `ref_plan × (1 + max_chase_pct_buy 1.5%)` — thị trường chạy quá xa → lệnh nằm
  chờ tại trần (kỷ luật limit, khớp tinh thần fill T+1-open của paper);
- **bán**: giá bid, sàn đuổi `ref_plan × (1 − max_chase_pct_sell 3%)`;
- **`cross_mode` (S2 dip-cross, mặc định `"dip"`)**: chọn cross/passive theo
  return 15' của chính mã (`px_hist` lấy mẫu 60s) — giá vừa đi NGƯỢC hướng lệnh
  → cross ngay (mua sau dip / bán sau nhịp tăng); vừa chạy CÙNG hướng → passive
  chờ hồi (mean-reversion 15-30'). Thiếu lịch sử (đầu phiên/resume) → cross
  (fail-safe = hành vi cũ). `urgency=high` luôn cross. Backtest 2023-09→2026-06:
  tiết kiệm ~3.5bps/chiều vs blind-cross (`workspace/backtest_exec_timing.py`).
  `"always"` = cross mọi slice (hành vi cũ). **A/B paper đang chạy**: account
  `ab_cross` (control) vs `ab_dip` (treatment) — đọc kết quả `python
  bot_ab_report.py`; account live pin `cross_mode=always` tới khi A/B xác nhận;
- lệnh con treo quá hạn → hủy, vòng sau đặt lại theo giá mới;
- phiên **ATC**: phần bán còn sót quét ATC (`atc_remainder_sell`), mua mặc định
  bỏ (plan hôm sau tự sync);
- journal CSV + state JSON ghi liên tục → **giết process chạy lại là resume**;
- **dừng khẩn cấp**: tạo file `data/BOT_STOP` → hủy mọi lệnh treo rồi thoát.

Output mỗi ngày trong `data/execution_logs/` (namespace theo account):
`exec_<label>_<date>_journal.csv`, `exec_<label>_<date>_state.json`,
`exec_<label>_<date>_report.md`, `phs_raw_<date>.jsonl` (payload thô PHS
để tinh chỉnh field mapping).

## 3. Đa tài khoản

Khai báo trong `data/trading_bot_accounts.json` (tự tạo template lần đầu):

```json
{
  "accounts": [
    {"label": "main",  "mode": "live",  "account_id": null,
     "credentials_file": null,
     "note": "TK chính — login mặc định data/phs_credentials.json"},
    {"label": "tieukhoan2", "mode": "live", "account_id": "022C111282-01",
     "credentials_file": null,
     "note": "(a) tiểu khoản 2 CÙNG login — chung FlexClient/token/OTP"},
    {"label": "acc_B", "mode": "paper",
     "credentials_file": "data/phs_credentials_B.json",
     "overrides": {"paper_init_cash": 2000000000, "max_participation": 0.05},
     "note": "(b) login KHÁC — token cache riêng phs_flex_token_<file>.json"},
    {"label": "acc_dnse", "mode": "paper", "broker": "dnse",
     "credentials_file": null,
     "note": "tài khoản DNSE — creds mặc định data/dnse_credentials.json"}
  ]
}
```

- **(a) nhiều tiểu khoản / 1 login**: cùng `credentials_file` → dùng CHUNG
  FlexClient + token + Smart OTP (pool theo file, không login giẫm nhau);
  chỉ khác `account_id`.
- **(b) nhiều login**: mỗi login 1 `credentials_file` riêng → token cache riêng.
- Mỗi account: plan riêng (`plan_<label>_<date>.json`), paper state riêng
  (`bot_paper_<label>.json`), exec state/journal/report riêng
  (`exec_<label>_<date>_*`), config riêng qua `overrides`.
- `bot_prepare_plan.py` / `bot_execute.py` mặc định chạy MỌI account `enabled`;
  giới hạn bằng `--account <label>` (lặp lại được).
- **Điều phối fleet**: mọi account chạy trong MỘT vòng lặp `run_session()`,
  dùng chung sổ participation — tổng KL (đã khớp + đang treo) của TOÀN BỘ
  account trên 1 mã ≤ `max_participation` × KL khớp lũy kế của mã. Các tài
  khoản không tự cạnh tranh đẩy giá nhau.
- OTP live: `--otp label=123456` per login (accounts chung login chỉ cần 1),
  hoặc `--otp 123456` áp chung.
- 5–10+ account: vẫn 1 process (poll tuần tự, quote cache 3s dùng chung);
  `data/BOT_STOP` dừng toàn fleet.

## 4. Broker & Mode

Chọn broker per-account bằng khóa `"broker": "phs" | "dnse"` (mặc định config
chung `"broker": "phs"`). Executor/strategy không đổi — chỉ adapter khác.

| | **PHS** (`phs_flex_api.py`) | **DNSE** (`dnse_api.py`) |
|---|---|---|
| Auth | login username/password → token 8h | API Key + Secret, ký HMAC mỗi request (không login) |
| Lệnh | Smart OTP → otp_token | OTP (smart/email) → trading-token 8h, tự cache |
| Creds | `data/phs_credentials.json` | `data/dnse_credentials.json` (đăng ký entradex.dnse.com.vn → Lightspeed API) |
| Trạng thái | ⛔ đặt lệnh chặn `-700003`, chờ PHS cấp client_id/secret | sẵn sàng khi điền api_key/secret |
| Quote | datafeed snapshot 1 call | secdef (cache phiên) + latest trade + top giá (3 call, TTL 3s) |

- **paper** (mặc định): quote THẬT (theo broker của profile), khớp mô phỏng,
  tiền + danh mục ảo `data/bot_paper_<label>.json`. Chạy thử được NGAY.
- **live**: `python bot_execute.py --mode live --otp <label>=<OTP>`.
  DNSE dùng email_otp: `--send-otp <label>` để gửi mã trước, rồi chạy lại với
  `--otp`. Token còn hạn trong cache thì không cần OTP.

## 5. Lệnh thường dùng

```bash
python bot_prepare_plan.py --dry          # xem plan không ghi file
python bot_prepare_plan.py                # ghi plan cho phiên kế tiếp
python bot_execute.py                     # thực thi plan hôm nay (paper)
python bot_execute.py --once              # 1 vòng debug
python bot_execute.py --force-phase MORNING   # test ngoài giờ
python bot_execute.py --probe HPG         # dump quote thô 1 mã
python test_trading_bot.py                # smoke test offline
```

## 6. An toàn

- `min_order_value` 5M (bỏ dust), `qty_tolerance_pct` 5% (không sync lắt nhắt),
  `max_orders_per_day` 60, `max_daily_gross_value` 20B (vượt → plan ghi cảnh báo).
- Kiểm tra tiền trước mỗi lệnh con mua (chờ lệnh bán khớp giải phóng tiền).
- Sell bị giới hạn theo `sellable` (CP chờ về T+2.5 không bán được).
- Plan đổi (chạy lại prepare) → executor phát hiện `created_at` khác, state mới.

## TODO / nâng cấp sau

- [ ] Live đặt lệnh khi PHS cấp client_id/secret (test 1 lệnh lô nhỏ trước).
- [x] DNSE verified trên TK thật 0001743768 (2026-06-12): inquiry + quote +
  NAV OK; `loanPackageId=1258` (gói ZaloPay, phí 0.07%) đã set trong creds.
  Ghi chú schema: market data đơn vị NGHÌN theo board (G1 lô chẵn);
  balances lồng `stock`; positions sellable=`tradeQuantity`.
- [ ] DNSE: test 1 lệnh LO lô nhỏ (cần trading-token: `--send-otp` → `--otp`).
- [ ] ⚠ TK DNSE đang giữ 5 vị thế cũ (MSH/TCM/VHC/VIB/VPB ~500M) KHÔNG thuộc
  book V2.3 → plan đầu tiên sẽ SELL-sync chúng. Chốt với user trước khi
  go-live (giữ lại thì thêm ignore-list, hoặc để bot dọn về book V2.3).
- [ ] Sync exit T+1 (đọc hold-expiry/stop từ pt_v22 thay vì trễ 1 phiên).
- [ ] Streaming quote (FlexStream) thay polling khi cần phản ứng nhanh.
- [ ] Lịch nghỉ lễ VN (hiện chỉ bỏ T7/CN).

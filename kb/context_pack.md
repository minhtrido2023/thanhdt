# Mike fleet — context pack (v2)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-06-21T15:42:26Z] Winston/answer — dataops-online: {"directive_id": "8745b5da", "status": "OK — all fresh", "dt5g": {"table": "vnindex_5state_dt5g_live", "max_dt": "2026-06-19", "frozen": false, "daily_append": true, "current_state": "3=BULL (stable 30d, not ffill)"}, "bq": {"ticker": "2026-06-19", "ticker_1m": "2026-06-19"}, "feeds": {"us_market_vix_spx": "data/us_market_history.csv 2026-06-19", "sunsirs_p4": "data/phosphorus_weekly.csv 2026-06-19", "bdi": "data/bdi_daily_real.csv 2026-06-19"}, "crons": {"daily_refresh_v34b_linux.sh": "23:15 ICT Mon-Fri", "telegram_run_daily.sh": "18:00 ICT Mon-Fri", "wb_commodity_monthly": "day 5 & 10 08:00 ICT", "rubber_weekly.sh": "18:30 ICT Mon-Fri (NEW)"}, "note": "latest trading day = Fri 2026-06-19 (today Sun = market closed); no anomalies"}
- [2026-06-21T15:23:20Z] Wendy/finding — vn-tax-cheatsheet: Thuế TNCN giao dịch CK cá nhân (VN, hiện hành tới 1/7/2026 & sau đó). NGUỒN GỐC: Luật Thuế TNCN 2025 số 109/2025/QH15 (ban hành 10/12/2025, hiệu lực 01/07/2026); Thông tư 111/2013/TT-BTC; Nghị định 126/2020/NĐ-CP. (1) BÁN/CHUYỂN NHƯỢNG CK NIÊM YẾT: 0,1% trên GIÁ BÁN mỗi lần (KHÔNG trừ giá vốn, áp cả khi lỗ); khấu trừ tại nguồn bởi CTCK. Luật 109/2025 GIỮ NGUYÊN 0,1% (không đổi sang 20% lãi cho CK niêm yết). (2) CỔ TỨC TIỀN MẶT: 5% (thu nhập đầu tư vốn), khấu trừ tại nguồn khi chi trả. (3) CỔ TỨC BẰNG CỔ PHIẾU / CỔ PHIẾU THƯỞNG: theo quy định HIỆN HÀNH KHÔNG đánh thuế lúc nhận; chỉ nộp KHI BÁN = 5% x mệnh giá (đầu tư vốn) + 0,1% x giá bán (chuyển nhượng). Đề xuất sửa NĐ126 đánh 5% NGAY khi nhận đã bị TẠM GÁC (chưa ban hành tính tới 2025-2026). ĐIỂM MỚI Luật 109: MIỄN thuế chứng chỉ quỹ mở nắm giữ >=2 năm. LƯU Ý: thông tin THAM KHẢO, không phải ý kiến luật sư hành nghề; rủi ro cao -> kiểm chứng luật sư + văn bản gốc.
- [2026-06-21T15:22:50Z] Winston/finding — rubber weekly feed: sources + alert thresholds: {"sources": {"primary_USD": "regionalert.com/prices/natural-rubber RSS3/TSR20/SMR20 USD/ton daily — continues WB RSS3 series", "secondary_CN": "SunSirs prodetail-586 China natural rubber spot RMB/ton — reuse phosphorus HW_CHECK infra", "ref_monthly": "WB Pink Sheet RSS3 USD/kg (existing rubber_monthly.csv)"}, "vol_RSS3_20yr": {"weekly_1sigma_pct": 3.9, "monthly_abs_p75": 8.85, "monthly_abs_p90": 13.3, "3mo_abs_p75": 18.4, "3mo_abs_p90": 27.9}, "proposed_alerts": {"WATCH_ping_Taylor": "weekly>=+/-7% OR 4wk_cum>=+/-15% OR cross cycle pivot", "ALERT_ping_Bill": "weekly>=+/-12% OR 3mo_cum>=+/-25% OR cycle-band break"}, "current_state": "+19% in 3mo (2.26->2.69 USD/kg, ~95th pct level) — already near WATCH", "stocks": ["GVR", "PHR", "DPR", "DRI", "TRC", "HRC"]}
- [2026-06-21T15:07:56Z] Mike/decision — create-fleet: {"theme": "Billions", "strategy": "production V2.4 go-live 2026-06-30", "roster": ["Mafee=execution(DNSE/PHS)", "DollarBill=portfolio-manager", "Taylor=quant/algo", "Wendy=legal-VN", "Spyros=risk&compliance", "Winston=data/regime-ops"], "autonomy": "Mafee semi-auto: paper full-auto; live only orders in approved plan within hard limits; Spyros owns BOT_STOP kill-switch", "date": "2026-06-21"}
<!--RECENT-END-->

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-06-21. Lịch sử/chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc auditable: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). Đây là hệ **POC nghiên cứu**, chưa chạy tiền thật tự động.

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-06-30**, trên TTCK Việt Nam.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout, depth OFF) + HAG eq_flag fix**.
- 2 book static 50/50: **BAL** (momentum SIGNAL_V11) + **LAG** (PEAD/earnings drift). Allocator w_LAG theo state {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- Live config <150B = **R3 NEUTRAL-only @50B: CAGR 28.26% / Sharpe 1.87 / DD −18.8 / Calmar 1.50**. @20B (R1) 31.69%.
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full (IS +8.7 / OOS +6.2, lại GIẢM DD).** Bull-park chỉ bật khi **NAV ≥150B**.
- **custom30** = rổ "đỗ tiền nhàn" beta (KHÔNG phải alpha picker): giữ **production (30 mã, cap 0.10)**; **(30,0.15) là OVERFIT** (walk-forward bác). **custom30B** (sleeve bull): @20B > custom30V, @50B wash (capacity-bound).

### DT5G — market regime gate
- Production state = bảng **`tav2_bq.vnindex_5state_dt5g_live`**, đọc qua **`get_gated_state()`** (fail-safe → DT4 khi feed cũ). **KHÔNG** đọc bảng trống `vnindex_5state` (đó là **v3.4b BASE**, không phải DT5G).
- Bản chất: **gate phòng thủ (insurance), KHÔNG phải bộ tăng lợi nhuận**. Cảnh giác bug **ffill-frozen** (đã gặp 2026-06-02).

### 8L valuation/rating
- **Composite v3 đang LIVE** trong `rating_8l.py` (default, thay v2): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS), no-reward khi PE/PCF âm. **Golden floor yêu cầu ROE_Min3Y≥0 VÀ CF_OA_3Y>0**. Moat governance: chỉ WIDE (đã audit 5F) mới được notch lên hạng cao.

### Kronos (foundation model nến)
- Đã tích hợp skill `/kronos`, fine-tune VN. Kết luận thẳng: **chỉ sửa calibration (MAE 3.93%→2.56%), KHÔNG tạo edge định hướng**; **RL bị loại** (OHLCV↔hướng ngày mai gần như không có MI). Dùng như **lăng kính kịch bản/biến động**, KHÔNG phải tín hiệu giao dịch.

### Backtest battle (đã chốt)
- Single-book custom30V **KHÔNG thắng** V2.3 multi-book khi audit faithful per-name. Trần auditable ~**25.7% @50B** (27.7% @20B); **>30% từ 2014 KHÔNG tồn tại** (số cao là do panel curated + CAPIT hardcode, không phải BQ-live).
- Illiquidity premium VN tập trung ở **vi-mô < 1 tỷ/ngày ADV**.

### Hạ tầng giao dịch
- `trading_bot/` (brokers/executor/plan) sẵn sàng. **DNSE live OK** (số tiểu khoản nằm trong `secrets/`, KHÔNG ghi ở KB). **PHS live BLOCKED** (chờ client credential, lỗi `-700003`) → PHS chạy paper.
- **Ủy quyền lệnh (an toàn tiền thật):** Taylor đặt rule (user duyệt) → Bill lập plan `data/plan_<acct>_<T+1>.json` (user duyệt) → **Mafee chỉ thực thi lệnh CÓ trong plan**, trong hạn mức cứng (`trading_bot/config.py` + `data/trading_rules.json`); paper full-auto, live trong limit, **KHÔNG tự chế lệnh**. Spyros giám sát + kill-switch `data/BOT_STOP`. Handoff = file `data/` + bus (companion model).

### Quy chuẩn làm việc (bắt buộc — khoa học & auditable)
1. Backtest phải **auditable**: self-check 0 VND + recompute từ CSV + **walk-forward IS(2014–19)/OOS(2020+) TRƯỚC khi wire**. Edge full-period mà rớt OOS = overfit → loại.
2. **No look-ahead**; cột forward (`profit_*`) chỉ để train, KHÔNG dùng filter live.
3. **Reproducible**: pin kết quả vào `data/results_registry.md` (lệnh + CSV path + AUDIT_END).
4. Ghi tri thức bền lên bus ngay khi tạo ra (`append_event.sh`), kèm số liệu/nguồn.
5. Tiền thật: human-in-the-loop ở tầng Taylor/Bill; Mafee plan-bound; Spyros là gate rủi ro.

### Backup / DR
- `~/thanhdt/backup.sh` → GitHub **minhtrido2023/thanhdt** (private): nhánh **main** = workspace + code + scrubbed Claude history; nhánh **mike-fleet** = fleet (config + KB). **Tự động daily 00:00 ICT** (cron) + chạy tay `./backup.sh "msg"` cho mốc quan trọng. PAT có hạn — push lỗi auth thì cấp lại token.

## Nguồn chuẩn tắc đầy đủ
Lịch sử/chi tiết: kb/KNOWLEDGE.md (Mike biên tập). Trạng thái fleet: kb/fleet_status.md.

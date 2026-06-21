# Mike fleet — KNOWLEDGE (canonical log)

> Append-only log of consolidated fleet events, written by `bin/consolidate.sh` every 30 min.
> Mike curates/summarizes this interactively. Children read the distilled `context_pack.md`, not this file.

## Fleet roster (2026-06-21) — đội đầu tư CK VN (motif *Billions*)
Chiến lược trung tâm: **production V2.4** (V2.3A + custom30V parking + gated-overflow + HAG fix), **go-live 2026-06-30**. Codebase ở `/home/trido/thanhdt/WorkingClaude`.

| agent | vai trò | sở hữu chính | làm việc với |
|---|---|---|---|
| **Mafee** | Execution — kết nối DNSE/PHS, đặt lệnh theo plan duyệt, giá tối ưu | `trading_bot/*`, `dnse_api.py`, `phs_flex_api.py`, `bot_execute.py` | nhận plan từ Bill/Taylor; báo fill cho Spyros |
| **DollarBill** | Portfolio Manager — EOD lấy account từ Mafee → lập plan ngày kế theo V2.4 | `bot_prepare_plan.py`, allocator/parking, `golive_recommend_v23.py` | trực tiếp với user |
| **Taylor** | Quant/Algo — thuật toán & rule sizing cho Bill, tiến hoá V2.4 | `pt_v23_audit_2014.py`, `macro_state_live.py`, `rating_8l.py`, custom30, `data/results_registry.md`, `data/trading_rules.json` | trực tiếp với user |
| **Wendy** | Pháp lý VN — luật CK/thuế/doanh nghiệp | advisory (Web + KB) | user khi cần |
| **Spyros** | Risk & Compliance — DD/đòn bẩy/tập trung, EOD recon, kill-switch | `data/BOT_STOP`, snapshot/recon (cần xây) | cảnh báo user + halt Mafee |
| **Winston** | Data/Regime Ops — DT5G daily refresh + Telegram + freshness | `daily_refresh_v34b_linux.sh`, `publish_gated_state.py`, `telegram_run_daily.sh` | feed Bill/Mafee |

**Mô hình ủy quyền lệnh (an toàn tiền thật):** Taylor đặt rule (user duyệt) → Bill lập plan `data/plan_<acct>_<T+1>.json` (user duyệt) → Mafee chỉ thực thi lệnh CÓ trong plan, trong hạn mức cứng (`trading_bot/config.py` + `data/trading_rules.json`); paper full-auto, live trong hạn mức, **không tự chế lệnh**. Spyros giám sát + `data/BOT_STOP`. Handoff = file `data/` + bus (companion model, không push prompt). DNSE live OK (số tiểu khoản ở `secrets`); **PHS live BLOCKED** (chờ credential).

## Consolidation 2026-06-21T15:08:57Z
- [2026-06-21T15:07:56Z] Mike/decision — create-fleet: {"theme": "Billions", "strategy": "production V2.4 go-live 2026-06-30", "roster": ["Mafee=execution(DNSE/PHS)", "DollarBill=portfolio-manager", "Taylor=quant/algo", "Wendy=legal-VN", "Spyros=risk&compliance", "Winston=data/regime-ops"], "autonomy": "Mafee semi-auto: paper full-auto; live only orders in approved plan within hard limits; Spyros owns BOT_STOP kill-switch", "date": "2026-06-21"}

## Consolidation 2026-06-21T15:37:01Z
- [2026-06-21T15:23:20Z] Wendy/finding — vn-tax-cheatsheet: Thuế TNCN giao dịch CK cá nhân (VN, hiện hành tới 1/7/2026 & sau đó). NGUỒN GỐC: Luật Thuế TNCN 2025 số 109/2025/QH15 (ban hành 10/12/2025, hiệu lực 01/07/2026); Thông tư 111/2013/TT-BTC; Nghị định 126/2020/NĐ-CP. (1) BÁN/CHUYỂN NHƯỢNG CK NIÊM YẾT: 0,1% trên GIÁ BÁN mỗi lần (KHÔNG trừ giá vốn, áp cả khi lỗ); khấu trừ tại nguồn bởi CTCK. Luật 109/2025 GIỮ NGUYÊN 0,1% (không đổi sang 20% lãi cho CK niêm yết). (2) CỔ TỨC TIỀN MẶT: 5% (thu nhập đầu tư vốn), khấu trừ tại nguồn khi chi trả. (3) CỔ TỨC BẰNG CỔ PHIẾU / CỔ PHIẾU THƯỞNG: theo quy định HIỆN HÀNH KHÔNG đánh thuế lúc nhận; chỉ nộp KHI BÁN = 5% x mệnh giá (đầu tư vốn) + 0,1% x giá bán (chuyển nhượng). Đề xuất sửa NĐ126 đánh 5% NGAY khi nhận đã bị TẠM GÁC (chưa ban hành tính tới 2025-2026). ĐIỂM MỚI Luật 109: MIỄN thuế chứng chỉ quỹ mở nắm giữ >=2 năm. LƯU Ý: thông tin THAM KHẢO, không phải ý kiến luật sư hành nghề; rủi ro cao -> kiểm chứng luật sư + văn bản gốc.
- [2026-06-21T15:22:50Z] Winston/finding — rubber weekly feed: sources + alert thresholds: {"sources": {"primary_USD": "regionalert.com/prices/natural-rubber RSS3/TSR20/SMR20 USD/ton daily — continues WB RSS3 series", "secondary_CN": "SunSirs prodetail-586 China natural rubber spot RMB/ton — reuse phosphorus HW_CHECK infra", "ref_monthly": "WB Pink Sheet RSS3 USD/kg (existing rubber_monthly.csv)"}, "vol_RSS3_20yr": {"weekly_1sigma_pct": 3.9, "monthly_abs_p75": 8.85, "monthly_abs_p90": 13.3, "3mo_abs_p75": 18.4, "3mo_abs_p90": 27.9}, "proposed_alerts": {"WATCH_ping_Taylor": "weekly>=+/-7% OR 4wk_cum>=+/-15% OR cross cycle pivot", "ALERT_ping_Bill": "weekly>=+/-12% OR 3mo_cum>=+/-25% OR cycle-band break"}, "current_state": "+19% in 3mo (2.26->2.69 USD/kg, ~95th pct level) — already near WATCH", "stocks": ["GVR", "PHR", "DPR", "DRI", "TRC", "HRC"]}

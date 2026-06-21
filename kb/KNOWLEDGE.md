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

**Mô hình ủy quyền lệnh (an toàn tiền thật):** Taylor đặt rule (user duyệt) → Bill lập plan `data/plan_<acct>_<T+1>.json` (user duyệt) → Mafee chỉ thực thi lệnh CÓ trong plan, trong hạn mức cứng (`trading_bot/config.py` + `data/trading_rules.json`); paper full-auto, live trong hạn mức, **không tự chế lệnh**. Spyros giám sát + `data/BOT_STOP`. Handoff = file `data/` + bus (companion model, không push prompt). DNSE live `0001743768` OK; **PHS live BLOCKED** (chờ credential).

## Consolidation 2026-06-21T15:08:57Z
- [2026-06-21T15:07:56Z] Mike/decision — create-fleet: {"theme": "Billions", "strategy": "production V2.4 go-live 2026-06-30", "roster": ["Mafee=execution(DNSE/PHS)", "DollarBill=portfolio-manager", "Taylor=quant/algo", "Wendy=legal-VN", "Spyros=risk&compliance", "Winston=data/regime-ops"], "autonomy": "Mafee semi-auto: paper full-auto; live only orders in approved plan within hard limits; Spyros owns BOT_STOP kill-switch", "date": "2026-06-21"}

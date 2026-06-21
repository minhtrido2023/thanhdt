---
name: simulation-[REDACTED]-audit-default
description: Khi user kêu chạy simulation/backtest → MẶC ĐỊNH luôn kèm audit (file 1-file BQ-verifiable)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2ef717ab-5c78-4933-9acd-888a2ecf9450
---

User ([REDACTED]12): "về sau khi tôi kêu chạy simulation là phải mặc định có audit".

**Why**: user cần mọi kết quả backtest dò lại được về chứng từ BQ thô (một bot khác chỉ đọc 1 file output + BQ là verify được từng VND → tự xác nhận CAGR/Sharpe/MaxDD). Panel curated + intraday fills cho số lạc quan không kiểm toán được → đã lật nhiều kết luận (xem [[v23_audit_2014_now_deliverable]]).

**How to apply**: bất kỳ lần nào user yêu cầu "chạy simulation/backtest/chạy lại X", MẶC ĐỊNH:
1. Dùng harness auditable: **T+1 Open fills** (KHÔNG intraday alt-fills), **mọi dữ liệu từ tav2_bq.*** (KHÔNG panel curated v4f_panel), state từ vnindex_5state_dt5g_live.
2. Xuất **MỘT file** `data/<ver>_audit_2014_now*.csv` chia record_type META/TX/REBAL/DAILY/METRIC + self-checks (cash-flow identity 0 VND, NAV identity 0 VND, combination replay 0 VND).
3. Chạy spot-check độc lập `data/v23_audit_spotcheck.py N <file>` (giá vs BQ 0 mismatch, metric dựng lại khớp).
4. Báo kết quả kèm cảnh báo nếu in-sample/few-events.

Template engine: `pt_v23_audit_2014.py` (MODE v23a/v23c/v22base + cap/maturity args). Verifier chung: `data/audit_spotcheck_generic.py`. Emitter chung: `audit_lib.py`. KHÔNG báo "đã chạy xong" nếu chưa có file audit + spot-check pass.

**STATE DEFAULT (user [REDACTED]13): dùng DT5G (`tav2_bq.vnindex_5state_dt5g_live`) làm state MẶC ĐỊNH cho TẤT CẢ chiến lược về sau** — kể cả khi bản gốc dùng state khác (vd V12.1 canonical = v3.4b). Chỉ giữ state khác nếu user yêu cầu rõ "faithful theo canonical". Mọi backtest/strategy mới: STATE_TABLE = vnindex_5state_dt5g_live.

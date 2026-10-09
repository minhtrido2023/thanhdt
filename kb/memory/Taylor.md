# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-10-09T03:08:10Z] ĐANG DỞ job Taylor_20261009_030802 cash-div first_disclosure_datetime validation (read-only): bắt đầu | NEXT: data_registry corporate_action + query snapshots
- [2026-10-09T03:16:52Z] [cash-div fd 10-09] Kết luận C (d9361ee4): first_disclosure_datetime không PIT; giữ mốc 2027-08. Registry .proposed Bẫy 5 corporate_action_snapshots chờ Mike duyệt.
- [2026-10-09T09:34:03Z] ĐANG DỞ job Taylor_20261009_093353 selfcheck-red owner sweep 9 file: bắt đầu | NEXT: chạy lại 9 selfcheck, phân loại
- [2026-10-09T09:38:42Z] ĐANG DỞ job Taylor_20261009_093353 sweep: custom30 CLOSED; 8 file phân loại xong (atc/basket/cpi/lag_gov/freshness=b, rating8l/capit/cctg=d live CSV) | worktree /home/trido/thanhdt/wt-screds-1009 branch fix/selfcheck-red-sweep-1009 | NEXT: sửa+chạy xanh, merge, close, finding
- [2026-10-09T09:46:11Z] [selfcheck-red sweep 10-09] 9/9 CLOSED (6a73ef82). Nợ: rating8l --bq BQ2-4 pin số 09-27 (HDG đã lật POWER); nhãn cctg_6m cho dòng 12M.
- [2026-10-09T09:46:41Z] ĐANG DỞ job Taylor_20261009_094633 intraday cutloss historical replay: bắt đầu | NEXT: đọc bin/intraday_price_watch.py + data_registry intraday
- [2026-10-09T09:54:33Z] ĐANG DỞ job Taylor_20261009_094633 intraday cutloss replay: research/intraday_cutloss_replay_20261009 build_inputs.py chạy | NEXT: replay.py (HistMarket + run_tick thật), analyze, REPORT, bus finding intraday-cutloss-historical-replay
- [2026-10-09T10:21:17Z] ĐANG DỞ job Taylor_20261009_094633 intraday cutloss replay: runs NONE đang chạy (run_none.sh), daily_approx xong | NEXT: case days → BROKEN/UNCLEAR runs, analyze.py, REPORT.md, bus finding intraday-cutloss-historical-replay
- [2026-10-09T10:45:08Z] [intraday-cutloss replay 10-09] DONE de182a88: cutloss thua giu (T+1 -1,45%), chua live; 3 de xuat A/B/C cho user; cho quant-skeptic.
- [2026-10-09T11:02:52Z] ĐANG DỞ job Taylor_20261009_110243 intraday watch 3 lỗ hổng + replay v2: bắt đầu | NEXT: đọc verify log + intraday_price_watch.py, worktree
- [2026-10-09T12:04:52Z] ĐANG DỞ job Taylor_20261009_110243: PHẦN 1 MERGED 9a1eeede (arch r2 APPROVED_WITH_NITS). PHẦN 2 replay v2 ở research/intraday_cutloss_replay_v2_20261009 (PREREG.md đã ghi, run_stage1.sh chạy new+old v2 BROKEN base) | NEXT: stage2 (độ nhạy 6 cấu hình + UNCLEAR + v1 universe new/old trên case days) → analyze_v2.py → REPORT.md → bus finding intraday-cutloss-replay-v2
- [2026-10-09T12:31:41Z] [intraday replay v2 10-09] DONE a5aa796b + merge 9a1eeede: H1 ADV>=10 tỷ SUPPORTED (không kém hơn), chưa live; chờ quant-skeptic. Nợ: reader EOD_OOS (dedupe ngày,mã) khi đủ ≥30 ngày ca live.

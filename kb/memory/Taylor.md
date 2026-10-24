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

- [2026-10-22T09:31:34Z] ĐANG DỞ job Taylor_20261022_093122: R&D read-only bal_loss_attribution_20261022 (phân rã lỗ BAL) | NEXT: PREREG+md5, tìm nav_history/journal/positions BAL
- [2026-10-22T09:39:54Z] [bal-loss-attribution 10-22] XONG job Taylor_20261022_093122: BAL live = 1 lệnh VPI −21% stop; chạm cảnh báo tập trung SpaceX p4,4%; chờ Mike/quant-skeptic
- [2026-10-22T09:50:22Z] ĐANG DỞ job Taylor_20261022_095008: R&D read-only bal_concentration_cap_20261022 (trần sizing BAL khi ít mã) | NEXT: đọc REPORT bal_loss_attribution, code sizing BAL, PREREG
- [2026-10-22T10:01:34Z] ĐANG DỞ job Taylor_20261022_095008: 8 chân engine chạy nền (logs/ trong research/bal_concentration_cap_20261022, worktree wt-balcap-20261022) | NEXT: legs_metrics.py + bootstrap_nav, REPORT
- [2026-10-22T10:11:53Z] [bal-concentration-cap 10-22] XONG job Taylor_20261022_095008: NO-GO trần BAL; sizing live=backtest; đính chính 'BAL bt luôn đa dạng hoá' SAI
- [2026-10-22T11:01:13Z] [livermore-stock-pilot 10-22] XONG job Taylor_20261022_104625: NO-GO sát biên (a đạt AUC 0,629; b hụt ΔAUC +0,024 CI chứa 0); không wire; chờ Mike
- [2026-10-22T14:33:07Z] ĐANG DỞ job Taylor_20261022_143258: vá park_holdings.py đối soát bán tay DRI (tái dùng f0e293c30) | NEXT: đọc commit, worktree wt-park-manual-sell-20261022
- [2026-10-22T14:42:41Z] [park-holdings-manual-sell 10-22] XONG job Taylor_20261022_143258: fix/park-holdings-manual-sell-20261022 @30fe3ba7b chờ arch-review/merge
- [2026-10-22T14:52:45Z] [park-holdings-manual-sell vòng 2 10-22] XONG job Taylor_20261022_145109: @9ccb6b0fe chờ arch-review lần cuối
- [2026-10-22T15:39:25Z] [nav-snapshot-manual-fills 10-22] XONG job Taylor_20261022_153620: fix/nav-snapshot-manual-fills-20261022 chờ arch-review/merge rồi mới bù dòng NAV 21/10 (2 account) + chạy nav_loss_brake_monitor
- [2026-10-24T03:45:09Z] ĐANG DỞ job Taylor_20261024_034455: R&D dcf_rich_outlook_20261024 (DCF RICH sâu có info lợi nhuận/drift?) | NEXT: đọc dcf_valuation.py, data_registry, PIT feasibility
- [2026-10-24T03:53:50Z] [dcf-rich-outlook 10-24] XONG job Taylor_20261024_034455: RICH sâu KHÔNG báo LN xấu; drift xấu chỉ ở ROE<25%/hàng hóa; đề xuất hạ gate→WARNING cho ROE≥25%, chờ quant-skeptic+user

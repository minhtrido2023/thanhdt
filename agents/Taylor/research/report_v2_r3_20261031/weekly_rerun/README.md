# Tuần 26–30/10/2026 — dựng lại bằng builder v2 r3 (DRY-RUN, CHƯA GỬI — chờ user duyệt)

Branch `session/report-v2-r3-20261031` (worktree /home/trido/wt-report-v2-r3-20261031), HEAD tại lúc dựng: xem `git log` (sau a374c4cc7).
Lệnh: `build.py weekly --account <A> --period 2026-10-26_to_2026-10-30 --out-dir <dir> --narrative narrative_weekly_<A>.json --promote`.

| Kiểm | SpaceX | ZaloPay |
|---|---|---|
| NAV 30/10 | 945.141.046 | 939.827.062 |
| Tuần (manifest = nav_period_returns) | −0,602% / VNI −1,83% | −0,783% |
| MTD | −1,885% | −3,849% |
| Từ đầu | −3,69% | −6,691% |
| Dòng 29/10 | −0,30% | +0,25% |
| Đối soát cầu NAV + định giá tham khảo | lệch 0 | lệch 0 |
| artifact lint | SẠCH | SẠCH |
| Quét zalopay/0001743768/"liên tài khoản" (.md+HTML+PDF) | 0 hit | n/a (nội bộ) |
| Cổng §21 (report_return_gate) | PASS | PASS |
| PDF | 4 trang | 4 trang |

File gửi được (khi user duyệt): `<A>_weekly_report_2026-10-26_to_2026-10-30.md` + `v2/<stem>/` (PDF, HTML email).
Narrative do Taylor viết (số chép từ builder): `narrative_weekly_*.json`. Bằng chứng: `verify.txt`, `build3_*.log`.
Gửi lại = chạy `report_delivery_gate.py <file.md> --topic trading_report` từ cây canonical SAU khi merge — KHÔNG làm trong job này.

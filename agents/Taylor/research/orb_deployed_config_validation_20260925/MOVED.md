# Da CHUYEN sang canonical (2026-09-25, §10 coding_guidelines)

Co che canh bao som ORB khong con nam o thu muc research nay. Ban DANG CHAY:

| Vai tro | Duong dan canonical |
|---|---|
| Script | `mike/bin/orb_drift_monitor.py` |
| Helper phan phoi (khong can scipy) | `mike/bin/orb_normstat.py` (ban sao `normstat.py`, doi ten de khong chiem ten chung trong `mike/bin`) |
| Selfcheck | `mike/bin/orb_drift_monitor_selfcheck.py` |
| Baseline ky vong | `mike/data/orb_drift_baseline.json` |
| Output `--replay` | `mike/data/orb_drift_replay.csv` |
| Cron | `50 8 * * 1-5` = **15:50 ICT T2-T6**, ghi `mike/logs/orb_drift_monitor.log`, KHONG co `--escalate` |
| Dong ky trong registry | `kb/cron_registry.md` (dong 15:50) |

`archive/` giu ban replay CSV + crontab truoc khi cai, de truy nguon.

`normstat.py` VAN O LAI thu muc nay: `viec_a_validate.py` va `viec_b_live.py` con import no.
Thiet ke goc: `DESIGN_early_warning.md` (giu nguyen, la tai lieu).

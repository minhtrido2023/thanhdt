# Bảng tương đương — 126/126 lời gọi tầng ngoài trùng khít (full JSON output)

Trái: selfcheck code gốc bc86963e trên BQ SỐNG 2026-09-14/15. Phải: code branch `test/oshares-freeze-live-selfchecks` trên `oshares_selfcheck_fixture`, BQ BỊ CHẶN (capture.py mode=blocked). So toàn bộ dict output, không chỉ các cột dưới.

| # | module | hàm | mã | asof | live | trạng thái cổng | value | method | anchor | events | verdict nhánh | output đầy đủ trùng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | live | oshares_at | FPT | 2025-07-18 | False | - | 1,481,330,122 | AIS_EXACT | 2025-06-19 | 0 | - | ✓ |
| 2 | live | oshares_at | FPT | 2025-07-20 | False | - | 1,481,330,122 | AIS_EXACT | 2025-06-19 | 0 | - | ✓ |
| 3 | live | oshares_at | FPT | 2025-07-21 | False | - | 1,703,507,121 | AIS_EXACT | 2025-06-19 | 1 | - | ✓ |
| 4 | live | oshares_at | FPT | 2025-07-22 | False | - | 1,703,507,121 | ANCHOR_ONLY | 2025-07-22 | 0 | - | ✓ |
| 5 | live | oshares_at | FPT | 2025-08-15 | False | - | 1,703,507,121 | ANCHOR_ONLY | 2025-07-22 | 0 | - | ✓ |
| 6 | live | oshares_at | FPT | 2025-09-11 | False | - | 1,703,507,121 | ANCHOR_ONLY | 2025-07-22 | 0 | - | ✓ |
| 7 | live | oshares_at | FPT | 2025-09-12 | False | - | 1,703,507,121 | AIS_EXACT | 2025-09-12 | 0 | - | ✓ |
| 8 | live | oshares_at | FPT | 2025-10-01 | False | - | 1,703,507,121 | AIS_EXACT | 2025-09-12 | 0 | - | ✓ |
| 9 | live | oshares_at | FPT | 2025-07-22 | False | - | 1,703,507,121 | ANCHOR_ONLY | 2025-07-22 | 0 | - | ✓ |
| 10 | live | oshares_at | FPT | 2025-06-18 | False | - | 1,481,330,122 | ANCHOR_ONLY | 2025-04-23 | 2 | FWD_NOT_ABSORBED | ✓ |
| 11 | live | oshares_at | HAH | 2026-03-01 | False | - | 185,840,401 | FIN_FALLBACK | 2026-02-02 | 0 | - | ✓ |
| 12 | live | oshares_at | HAH | 2025-03-25 | False | - | 129,894,418 | ANCHOR_ONLY | 2025-01-24 | 1 | FWD_NOT_ABSORBED | ✓ |
| 13 | live | oshares_at | HAH | 2026-03-13 | False | - | 185,840,401 | FIN_FALLBACK | 2026-02-02 | 0 | FWD_ABSORBED | ✓ |
| 14 | live | oshares_at | HAH | 2026-08-19 | False | - | 191,840,401 | ANCHOR_ONLY | 2026-07-30 | 0 | - | ✓ |
| 15 | live | oshares_at | HAH | 2026-05-28 | False | - | 188,340,401 | AIS_EXACT | 2026-05-27 | 1 | - | ✓ |
| 16 | live | oshares_at | NAF | 2026-01-06 | False | - | None | UNKNOWN_RATIO | 2025-11-21 | 0 | - | ✓ |
| 17 | live | oshares_at | DHG | 2026-08-12 | False | - | 130,746,071 | ANCHOR_UNVERIFIED | 2026-07-20 | 0 | - | ✓ |
| 17 | live | oshares_at | PVT | 2026-08-12 | False | - | 516,918,938 | ANCHOR_ONLY | 2026-07-29 | 0 | - | ✓ |
| 17 | live | oshares_at | TCB | 2026-08-12 | False | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 17 | live | oshares_at | ACB | 2026-08-12 | False | - | 5,804,421,957 | ANCHOR_ONLY | 2026-07-22 | 0 | - | ✓ |
| 17 | live | oshares_at | HDB | 2026-08-12 | False | - | 5,005,276,323 | ANCHOR_ONLY | 2026-07-31 | 0 | - | ✓ |
| 18 | live | oshares_at | DHG | 2026-08-12 | False | - | 130,746,071 | ANCHOR_UNVERIFIED | 2026-07-20 | 0 | - | ✓ |
| 19 | live | oshares_at | PVT | 2026-08-12 | False | - | 516,918,938 | ANCHOR_ONLY | 2026-07-29 | 0 | - | ✓ |
| 20 | live | oshares_at | TCB | 2026-08-12 | False | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 21 | live | oshares_at | ACB | 2026-08-12 | False | - | 5,804,421,957 | ANCHOR_ONLY | 2026-07-22 | 0 | - | ✓ |
| 22 | live | oshares_at | HDB | 2026-08-12 | False | - | 5,005,276,323 | ANCHOR_ONLY | 2026-07-31 | 0 | - | ✓ |
| 23 | live | oshares_at | MBB | 2026-08-12 | False | - | 10,068,749,885 | ANCHOR_ONLY | 2026-07-30 | 2 | FWD_NOT_ABSORBED | ✓ |
| 24 | live | oshares_at | IDC | 2021-02-05 | False | - | 300,000,000 | ANCHOR_ONLY | 2021-02-01 | 0 | - | ✓ |
| 25 | live | _ais_verdicts | IDC | 2021-02-05 | - | - | - | - | - | - | 3 verdict: 1 OK / 1 UNVERIFIED | ✓ |
| 26 | live | oshares_at | FPT | 2020-05-05 | False | - | 681,668,102 | ANCHOR_ONLY | 2020-04-28 | 0 | - | ✓ |
| 27 | live | _ais_verdicts | FPT | 2020-05-05 | - | - | - | - | - | - | 6 verdict: 2 OK / 3 UNVERIFIED | ✓ |
| 28 | live | _ais_verdicts | FPT | 2021-01-01 | - | - | - | - | - | - | 7 verdict: 3 OK / 3 UNVERIFIED | ✓ |
| 29 | live | oshares_at | IDC | 2021-02-05 | False | serve+UNVERIFIED | 300,000,000 | FIN_FALLBACK | 2021-02-01 | 0 | - | ✓ |
| 30 | live | oshares_at | IDC | 2021-02-05 | False | serve+UNVERIFIED,fallback-off | 3,000,000,000 | AIS_EXACT | 2020-05-28 | 0 | - | ✓ |
| 31 | live | oshares_at | FPT | 2020-05-05 | False | serve+UNVERIFIED,fallback-off | 461,723,054 | AIS_EXACT | 2020-04-06 | 0 | - | ✓ |
| 32 | live | oshares_at | TCB | 2026-08-12 | False | verdicts-boom | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 33 | live | oshares_at | TCB | 2025-12-05 | False | - | 7,086,240,414 | AIS_EXACT | 2025-12-01 | 1 | - | ✓ |
| 34 | live | _ais_verdicts | FPT | 2017-08-01 | - | - | - | - | - | - | 1 verdict: 0 OK / 0 UNVERIFIED | ✓ |
| 35 | live | oshares_at | FPT | 2017-07-03 | False | - | 530,961,105 | AIS_EXACT | 2017-07-03 | 0 | - | ✓ |
| 36 | live | oshares_at | FPT | 2017-07-03 | False | - | 530,961,105 | AIS_EXACT | 2017-07-03 | 0 | - | ✓ |
| 37 | live | _ais_verdicts | IDC | 2020-01-01 | - | - | - | - | - | - | 2 verdict: 1 OK / 0 UNVERIFIED | ✓ |
| 38 | live | _ais_verdicts | IDC | 2020-01-01 | - | - | - | - | - | - | 2 verdict: 1 OK / 0 UNVERIFIED | ✓ |
| 39 | live | oshares_at | VRE | 2026-08-19 | False | - | 2,272,318,410 | FIN_FALLBACK | 2026-07-29 | 0 | - | ✓ |
| 40 | live | oshares_at | VRE | 2026-08-19 | False | fallback-off | 2,328,818,410 | AIS_EXACT | 2018-12-26 | 0 | - | ✓ |
| 41 | live | oshares_at | FPT | 2001-01-01 | False | - | None | NO_ANCHOR | None | 0 | - | ✓ |
| 42 | live | oshares_at | CC1 | 2026-08-19 | False | - | 474,656,100 | ANCHOR_ONLY | 2026-07-31 | 0 | - | ✓ |
| 43 | live | oshares_at | EVFX | 2026-08-20 | False | - | None | AIS_UNCERTIFIED | 2024-12-06 | 0 | - | ✓ |
| 44 | live | oshares_at | EVFX | 2026-08-20 | True | - | 760,565,802 | FIN_FALLBACK | 2026-07-21 | 0 | - | ✓ |
| 45 | live | oshares_at | EVFX | 2026-08-20 | True | - | 760,565,802 | FIN_FALLBACK | 2026-07-21 | 0 | - | ✓ |
| 46 | live | oshares_at | HHVX | 2026-08-20 | True | - | 574,511,888 | FIN_FALLBACK | 2026-07-31 | 0 | ABSORBED | ✓ |
| 47 | live | oshares_at | HHVX | 2026-08-20 | True | - | 579,511,888 | FIN_FALLBACK | 2026-07-31 | 1 | FWD_NOT_ABSORBED,ABSORBED | ✓ |
| 48 | live | oshares_at | HHVX | 2026-08-20 | True | - | None | FIN_ABSORPTION_AMBIGUOUS | 2026-07-31 | 0 | FWD_AMBIGUOUS,ABSORBED | ✓ |
| 49 | live | oshares_at | TCBX | 2026-08-20 | False | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 50 | live | oshares_at | TCBX | 2026-08-20 | True | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 51 | live | oshares_at | BWDX | 2026-08-20 | True | - | None | AIS_UNCERTIFIED | 2026-05-07 | 0 | - | ✓ |
| 52 | live | oshares_at | HAHX | 2026-03-01 | False | - | 185,840,401 | FIN_FALLBACK | 2026-02-02 | 0 | - | ✓ |
| 53 | live | oshares_at | HAHX | 2026-03-01 | True | - | 185,840,401 | FIN_FALLBACK | 2026-02-02 | 0 | - | ✓ |
| 54 | live | oshares_at | RSTX | 2026-08-20 | False | - | 185,840,401 | AIS_EXACT | 2026-05-27 | 0 | - | ✓ |
| 55 | live | oshares_at | RSTX | 2026-08-20 | True | - | 185,840,401 | AIS_EXACT | 2026-05-27 | 0 | - | ✓ |
| 56 | live | oshares_at | NOQX | 2026-08-20 | True | - | None | AIS_UNCERTIFIED | 2025-01-05 | 0 | - | ✓ |
| 57 | live | oshares_at | TCBX | 2026-08-20 | False | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 58 | live | oshares_at | TCBX | 2026-08-20 | True | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 59 | live | oshares_at | HAHX | 2026-08-20 | False | - | None | AIS_UNCERTIFIED | 2026-05-27 | 0 | - | ✓ |
| 60 | live | oshares_at | HAHX | 2026-08-20 | True | - | None | AIS_UNCERTIFIED | 2026-05-27 | 0 | - | ✓ |
| 61 | live | oshares_at | HHV | 2026-08-19 | True | - | 574,511,888 | ANCHOR_ONLY | 2026-07-31 | 0 | - | ✓ |
| 62 | live | oshares_at | VCI | 2026-03-01 | True | - | 850,100,000 | FIN_FALLBACK | 2026-02-02 | 0 | ABSORBED | ✓ |
| 63 | live | oshares_at | QENDX | 2026-08-20 | False | - | 546,911,840 | FIN_FALLBACK | 2026-07-31 | 0 | - | ✓ |
| 64 | live | oshares_at | QENDX | 2026-08-20 | True | - | 574,257,432 | FIN_FALLBACK | 2026-07-31 | 1 | ROLLED | ✓ |
| 65 | live | oshares_at | AMBX | 2026-08-20 | True | - | 560,000,000 | FIN_FALLBACK | 2026-07-31 | 0 | WINDOW_AMBIGUOUS | ✓ |
| 66 | live | oshares_at | NORX | 2026-08-20 | True | - | 560,000,000 | FIN_FALLBACK | 2026-07-31 | 0 | WINDOW_AMBIGUOUS | ✓ |
| 67 | live | oshares_at | TWOX | 2026-08-20 | True | - | 530,400,000 | FIN_FALLBACK | 2026-07-31 | 1 | ROLLED | ✓ |
| 68 | live | oshares_at | OLDX | 2026-08-20 | True | - | 546,911,840 | FIN_FALLBACK | 2026-07-31 | 0 | - | ✓ |
| 69 | live | oshares_at | INX | 2026-08-20 | True | - | 574,257,432 | FIN_FALLBACK | 2026-07-31 | 1 | ROLLED | ✓ |
| 70 | live | oshares_at | NOSZX | 2026-08-20 | True | - | 500,000,000 | FIN_FALLBACK | 2026-07-31 | 0 | WINDOW_AMBIGUOUS | ✓ |
| 71 | live | oshares_at | OKZX | 2026-08-20 | True | - | 530,400,000 | FIN_FALLBACK | 2026-07-31 | 2 | ROLLED | ✓ |
| 72 | live | oshares_at | EVFX | 2026-08-20 | True | - | 760,565,802 | FIN_FALLBACK | 2026-07-21 | 0 | - | ✓ |
| 73 | live | oshares_at | TCBX | 2026-08-20 | True | - | None | AIS_UNCERTIFIED | 2026-08-05 | 0 | - | ✓ |
| 74 | live | oshares_at | HHVX | 2026-08-20 | False | - | 574,511,888 | AIS_EXACT | 2026-08-20 | 0 | - | ✓ |
| 75 | live | oshares_at | HHVX | 2026-08-20 | False | - | 574,511,888 | ANCHOR_ONLY | 2026-07-31 | 0 | - | ✓ |
| 76 | live | oshares_at | TCBSX | 2026-03-01 | False | - | 7,086,240,414 | ANCHOR_ONLY | 2026-01-22 | 0 | - | ✓ |
| 77 | live | oshares_at | ABB | 2026-03-01 | False | - | 1,397,208,685 | FIN_FALLBACK | 2026-02-02 | 0 | - | ✓ |
| 77 | live | oshares_at | NVL | 2026-03-01 | False | - | 2,234,496,474 | FIN_FALLBACK | 2026-02-02 | 0 | - | ✓ |
| 78 | live | oshares_at | KBC | 2026-03-01 | True | - | 941,754,759 | ANCHOR_ONLY | 2026-02-02 | 0 | - | ✓ |
| 79 | live | oshares_at | KBC | 2026-03-01 | False | - | 941,754,759 | ANCHOR_ONLY | 2026-02-02 | 0 | - | ✓ |
| 80 | live | oshares_at | KHP | 2026-09-14 | True | - | 62,186,518 | FIN_FALLBACK | 2026-07-20 | 0 | FWD_ABSORBED | ✓ |
| 81 | live | oshares_at | KHP | 2026-09-14 | False | - | 62,186,518 | FIN_FALLBACK | 2026-07-20 | 0 | FWD_ABSORBED | ✓ |
| 82 | live | oshares_at | KHP | 2026-09-14 | True | fwd-off | 63,996,290 | FIN_FALLBACK | 2026-07-20 | 1 | - | ✓ |
| 83 | live | oshares_at | KHP | 2026-09-14 | False | fwd-off | 63,996,290 | FIN_FALLBACK | 2026-07-20 | 1 | - | ✓ |
| 84 | live | oshares_at | KHP | 2026-09-14 | True | - | 62,215,739 | AIS_EXACT | 2026-09-14 | 0 | - | ✓ |
| 85 | live | oshares_at | ASM | 2025-10-29 | True | - | 407,194,183 | ANCHOR_ONLY | 2025-07-31 | 1 | FWD_NOT_ABSORBED | ✓ |
| 86 | live | oshares_at | MCH | 2026-07-26 | True | - | None | FIN_ABSORPTION_AMBIGUOUS | 2026-04-28 | 0 | FWD_AMBIGUOUS | ✓ |
| 87 | live | oshares_at | FWX | 2026-08-20 | True | - | None | UNKNOWN_RATIO | 2026-07-20 | 0 | SKIPPED_UNSIZABLE | ✓ |
| 88 | live | _ais_verdicts | VRE | 2026-08-19 | - | - | - | - | - | - | 1 verdict: 0 OK / 0 UNVERIFIED | ✓ |
| 89 | live | _ais_verdicts | HAH | 2026-05-28 | - | - | - | - | - | - | 9 verdict: 7 OK / 1 UNVERIFIED | ✓ |
| 90 | live | _ais_verdicts | HHVX | 2026-08-20 | - | - | - | - | - | - | 4 verdict: 2 OK / 1 UNVERIFIED | ✓ |
| 91 | live | _ais_verdicts | FPT | 2025-07-18 | - | - | - | - | - | - | 18 verdict: 12 OK / 5 UNVERIFIED | ✓ |
| 92 | live | _ais_verdicts | FPT | 2025-07-20 | - | - | - | - | - | - | 18 verdict: 12 OK / 5 UNVERIFIED | ✓ |
| 93 | live | _ais_verdicts | FPT | 2025-07-21 | - | - | - | - | - | - | 18 verdict: 12 OK / 5 UNVERIFIED | ✓ |
| 94 | live | _ais_verdicts | FPT | 2025-09-12 | - | - | - | - | - | - | 19 verdict: 13 OK / 5 UNVERIFIED | ✓ |
| 95 | live | _ais_verdicts | FPT | 2025-10-01 | - | - | - | - | - | - | 19 verdict: 13 OK / 5 UNVERIFIED | ✓ |
| 96 | live | _ais_verdicts | KHP | 2026-09-14 | - | - | - | - | - | - | 4 verdict: 3 OK / 0 UNVERIFIED | ✓ |
| 97 | pit | oshares_reconciled | AGREE | 2026-08-13 | - | - | 100,050,000 | AIS_EXACT | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | BOTHNONE | 2026-08-13 | - | - | None | NO_ANCHOR | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | DECLINE | 2026-08-13 | - | - | 100,000,000 | UNKNOWN_RATIO | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | DIVERGE | 2026-08-13 | - | - | 100,000,000 | ISS_ESTIMATE | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | EDGE_IN | 2026-08-13 | - | - | 100,100,000 | AIS_EXACT | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | EDGE_OUT | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | INSANE | 2026-08-13 | - | - | 300,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | NOFB | 2026-08-13 | - | - | None | AIS_EXACT | - | 0 | - | ✓ |
| 97 | pit | oshares_reconciled | SANE_EDGE | 2026-08-13 | - | - | 100,000,000 | ISS_ESTIMATE | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | AGREE | 2026-08-13 | - | - | 100,050,000 | AIS_EXACT | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | BOTHNONE | 2026-08-13 | - | - | None | NO_ANCHOR | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | DECLINE | 2026-08-13 | - | - | 100,000,000 | UNKNOWN_RATIO | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | DIVERGE | 2026-08-13 | - | - | 115,000,000 | ISS_ESTIMATE | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | EDGE_IN | 2026-08-13 | - | - | 100,100,000 | AIS_EXACT | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | EDGE_OUT | 2026-08-13 | - | - | 100,101,000 | AIS_EXACT | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | INSANE | 2026-08-13 | - | - | 300,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | NOFB | 2026-08-13 | - | - | 123,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 98 | pit | oshares_pit | SANE_EDGE | 2026-08-13 | - | - | 300,000,000 | ISS_ESTIMATE | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | AGREE | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | BOTHNONE | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | DECLINE | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | DIVERGE | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | EDGE_IN | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | EDGE_OUT | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | INSANE | 2026-08-13 | - | - | 300,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | NOFB | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 99 | pit | oshares_reconciled | SANE_EDGE | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 100 | pit | oshares_pit | INSANE | 2026-08-13 | - | - | 3,000,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 101 | pit | oshares_reconciled | FWDAMB | 2026-09-14 | - | - | 62,186,518 | FIN_ABSORPTION_AMBIGUOUS | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | AGREE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | BOTHNONE | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | DECLINE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | DIVERGE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | EDGE_IN | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | EDGE_OUT | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | INSANE | 2026-08-13 | - | - | 300,000,000 | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | NOFB | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 102 | pit | oshares_reconciled | SANE_EDGE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | AGREE | 2026-08-13 | - | - | 100,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | BOTHNONE | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | DECLINE | 2026-08-13 | - | - | 100,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | DIVERGE | 2026-08-13 | - | - | 100,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | EDGE_IN | 2026-08-13 | - | - | 100,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | EDGE_OUT | 2026-08-13 | - | - | 100,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | INSANE | 2026-08-13 | - | - | 300,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | NOFB | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 103 | pit | oshares_pit | SANE_EDGE | 2026-08-13 | - | - | 100,000,000 | NO_RESULT | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | AGREE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | BOTHNONE | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | DECLINE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | DIVERGE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | EDGE_IN | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | EDGE_OUT | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | INSANE | 2026-08-13 | - | - | 300,000,000 | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | NOFB | 2026-08-13 | - | - | None | None | - | 0 | - | ✓ |
| 104 | pit | oshares_reconciled | SANE_EDGE | 2026-08-13 | - | - | 100,000,000 | None | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | AGREE | 2026-08-13 | - | - | None | AIS_EXACT | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | BOTHNONE | 2026-08-13 | - | - | None | NO_ANCHOR | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | DECLINE | 2026-08-13 | - | - | 100,000,000 | UNKNOWN_RATIO | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | DIVERGE | 2026-08-13 | - | - | 100,000,000 | ISS_ESTIMATE | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | EDGE_IN | 2026-08-13 | - | - | 100,100,000 | AIS_EXACT | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | EDGE_OUT | 2026-08-13 | - | - | 100,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | INSANE | 2026-08-13 | - | - | 300,000,000 | AIS_EXACT | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | NOFB | 2026-08-13 | - | - | None | AIS_EXACT | - | 0 | - | ✓ |
| 105 | pit | oshares_reconciled | SANE_EDGE | 2026-08-13 | - | - | 100,000,000 | ISS_ESTIMATE | - | 0 | - | ✓ |
| 106 | pit | oshares_at | FPT | 2026-08-12 | False | - | 1,714,326,422 | ANCHOR_ONLY | 2026-07-28 | 0 | - | ✓ |
| 106 | pit | oshares_at | MBB | 2026-08-12 | False | - | 10,068,749,885 | ANCHOR_ONLY | 2026-07-30 | 2 | FWD_NOT_ABSORBED | ✓ |
| 107 | pit | oshares_reconciled | FPT | 2026-08-12 | - | - | 1,714,326,422 | ANCHOR_ONLY | - | 0 | - | ✓ |
| 107 | pit | oshares_reconciled | MBB | 2026-08-12 | - | - | 8,755,434,683 | ANCHOR_ONLY | - | 0 | - | ✓ |
| 108 | pit | oshares_pit | MBB | 2026-08-12 | - | - | 10,068,749,885 | ANCHOR_ONLY | - | 0 | - | ✓ |
| 109 | pit | oshares_pit | IDC | 2021-02-05 | - | - | 300,000,000 | ANCHOR_ONLY | - | 0 | - | ✓ |
| 110 | pit | _ais_verdicts | IDC | 2026-06-16 | - | - | - | - | - | - | 5 verdict: 2 OK / 2 UNVERIFIED | ✓ |
| 111 | pit | _ais_verdicts | AAA | 2026-06-16 | - | - | - | - | - | - | 14 verdict: 12 OK / 1 UNVERIFIED | ✓ |
| 112 | pit | _ais_verdicts | FPT | 2026-06-16 | - | - | - | - | - | - | 19 verdict: 13 OK / 5 UNVERIFIED | ✓ |
| 113 | pit | _ais_verdicts | VNM | 2026-06-16 | - | - | - | - | - | - | 5 verdict: 4 OK / 0 UNVERIFIED | ✓ |
| 114 | pit | _ais_verdicts | IDC | 2020-01-01 | - | - | - | - | - | - | 2 verdict: 1 OK / 0 UNVERIFIED | ✓ |
| 115 | pit | _ais_verdicts | IDC | 2020-01-01 | - | - | - | - | - | - | 2 verdict: 1 OK / 0 UNVERIFIED | ✓ |
| 116 | pit | oshares_pit | AAA | 2019-08-05 | - | serve+UNVERIFIED | 58,664,988 | AIS_EXACT | - | 0 | - | ✓ |
| 117 | pit | oshares_pit | FPT | 2020-05-05 | - | - | 681,668,102 | ANCHOR_ONLY | - | 0 | - | ✓ |
| 118 | pit | _ais_verdicts | FPT | 2020-05-05 | - | - | - | - | - | - | 6 verdict: 2 OK / 3 UNVERIFIED | ✓ |
| 119 | pit | _ais_verdicts | FPT | 2020-05-05 | - | - | - | - | - | - | 6 verdict: 2 OK / 3 UNVERIFIED | ✓ |
| 120 | pit | oshares_pit | FPT | 2023-04-10 | - | - | 1,097,026,572 | AIS_UNCERTIFIED | - | 0 | - | ✓ |
| 121 | pit | oshares_pit | FPT | 2020-05-05 | - | serve+UNVERIFIED | 461,723,054 | AIS_EXACT | - | 0 | - | ✓ |
| 122 | pit | oshares_pit | IDC | 2022-10-03 | - | - | 330,000,000 | AIS_UNCERTIFIED | - | 0 | - | ✓ |
| 123 | pit | oshares_pit | FPT | 2025-10-01 | - | - | 1,703,507,121 | AIS_EXACT | - | 0 | - | ✓ |
| 124 | pit | oshares_pit | FPT | 2025-10-01 | - | verdicts-boom | 1,703,507,121 | AIS_UNCERTIFIED | - | 0 | - | ✓ |
| 125 | pit | oshares_at | DHG | 2026-08-12 | False | - | 130,746,071 | ANCHOR_UNVERIFIED | 2026-07-20 | 0 | - | ✓ |
| 126 | pit | oshares_pit | DHG | 2026-08-12 | - | - | 130,746,071 | ANCHOR_UNVERIFIED | - | 0 | - | ✓ |

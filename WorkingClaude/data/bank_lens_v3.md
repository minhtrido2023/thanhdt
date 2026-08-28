# Bank lens v3 — ROE-based gate (NPL/CAR/coverage/CASA UNAVAILABLE post vnstock migration 2026-08-28)
GATE: AVOID(ROE<8%) else DATA_GAP (profitable, asset-quality unverified — see data_gap col)

tkr    ROE%  NIM%  CIR%   PB  loanG%      gate
----------------------------------------------
SSB     7.1  2.49    41 1.32    +8.7     AVOID
STB     4.9  3.03    36 2.21    +4.9     AVOID
EIB     1.9  2.45    61 1.22    +3.9     AVOID
LPB    26.2  2.97    30 3.43   +10.7  DATA_GAP
HDB    21.2  4.41    27 1.54   +34.9  DATA_GAP
CTG    20.1  2.70    29 1.24    +5.1  DATA_GAP
MBB    19.2  4.06    28 1.35   +31.8  DATA_GAP
NAB    18.1  2.30    37 0.96   +10.5  DATA_GAP
VCB    16.8  2.81    34 2.02    +7.9  DATA_GAP
BID    16.2  2.19    33 1.45   +11.8  DATA_GAP
SHB    16.1  2.19    22 0.85    +8.5  DATA_GAP
ACB    15.8  2.95    32 1.32   +11.4  DATA_GAP
VPB    15.6  5.25    22 1.14   +29.6  DATA_GAP
VIB    15.5  3.07    34 1.06    +6.5  DATA_GAP
TPB    15.3  3.05    36 0.82   +14.2  DATA_GAP
TCB    14.3  3.88    31 1.28   +10.5  DATA_GAP
MSB    13.0  3.28    36 0.90   +12.4  DATA_GAP
OCB    12.4  3.07    34 0.93   +12.6  DATA_GAP

## Ranked (excl. ROE<8% AVOID) — 0.5*ROE + 0.25*profit(NIM/CIR) + 0.25*value(ROE/PB)
rank tkr   SCORE  ROE%   PB
 1 HDB     0.85  21.2 1.54
 2 CTG     0.77  20.1 1.24
 3 MBB     0.76  19.2 1.35
 4 LPB     0.64  26.2 3.43
 5 NAB     0.62  18.1 0.96
 6 SHB     0.61  16.1 0.85
 7 VPB     0.55  15.6 1.14
 8 VCB     0.43  16.8 2.02
 9 BID     0.43  16.2 1.45
10 ACB     0.43  15.8 1.32
11 VIB     0.42  15.5 1.06
12 TPB     0.39  15.3 0.82
13 TCB     0.31  14.3 1.28
14 MSB     0.31  13.0 0.90
15 OCB     0.23  12.4 0.93

AVOID (ROE<8%): STB, EIB, SSB
DATA_GAP (profitable, AQ unverified): VCB, BID, CTG, TCB, MBB, ACB, VPB, VIB, HDB, SHB, TPB, MSB, OCB, LPB, NAB

NOTE: NPL/CAR/coverage/CASA are NaN — vnstock's finance.ratio() (old source) is broken since 31/08/2025
(KeyError lengthReport, community edition shape change). Recomputed ROE/NIM/CIR/loanG/PB from
balance_sheet+income_statement+company.overview instead. See module docstring for what's recoverable.
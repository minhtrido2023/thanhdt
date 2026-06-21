# Bank valuation lens (ICB 8355) — P/B-vs-ROE framework, latest snapshot
cheap-for-quality = low pb_z (vs own history) OR negative PB-vs-ROE residual (cheap for its ROE)
cross-section fit: PB ≈ 0.005·ROE5Y + 1.29

tkr       PB  pb_z  ROE5Y ROEmin ROE/PB PBresid  NPyoy  liqB  cheap?
------------------------------------------------------------------------
VAB     0.81  1.29  11.6%   9.8%   14.3   -0.53   +39%     4  
OCB     0.88  0.85  14.8%  10.5%   16.8   -0.48   +37%    16  YES
TPB     0.92  0.14  18.6%  13.7%   20.2   -0.46    -1%   132  YES
KLB     0.93  0.42  15.7%  10.5%   16.9   -0.43   +46%     4  YES
NAB     0.98  1.52  19.2%  17.3%   19.6   -0.40   +34%    17  YES
SHB     1.01  1.20  17.7%  15.9%   17.5   -0.36    +7%   827  YES
BVB     1.03  0.05   5.1%   1.0%    5.0   -0.28  +169%    13  
VIB     1.12  0.42  23.8%  16.4%   21.2   -0.28   +16%    82  YES
MSB     1.09  2.47  17.2%  14.2%   15.8   -0.28   +20%   139  YES
VPB     1.15  0.22  14.3%   8.4%   12.4   -0.21   +59%   404  YES
SSB     1.16 -0.90  15.3%  13.0%   13.2   -0.20   -68%    27  
TCB     1.24  0.94  17.4%  14.7%   14.0   -0.13   +12%   368  YES
ABB     1.22  2.69  10.4%   3.4%    8.5   -0.12  +261%    10  
ACB     1.30  1.09  22.9%  17.6%   17.6   -0.10   +18%   323  YES
MBB     1.34  1.45  22.9%  20.7%   17.1   -0.06   +14%   375  YES
CTG     1.43  2.01  17.8%  15.8%   12.4   +0.06   +65%   279  
HDB     1.56  1.79  23.9%  22.6%   15.3   +0.16   +13%   315  
EIB     1.50  0.50   9.9%   4.4%    6.6   +0.16   -59%   199  
BID     1.60  0.03  17.9%  13.0%   11.2   +0.23   +16%   276  
NVB     1.59 -0.54 -20.8% -91.7%  -13.1   +0.39   +43%     2  
STB     2.09  2.28  14.7%  10.3%    7.0   +0.73   -45%   412  
VCB     2.21  0.83  20.5%  16.6%    9.3   +0.83    +9%   396  
LPB     3.14  2.06  22.0%  18.5%    7.0   +1.75   -10%    76  

CHEAP banks (cheap-for-ROE + ROE≥14% + not collapsing): OCB, TPB, KLB, NAB, SHB, VIB, MSB, VPB, TCB, ACB, MBB

## Face validity — MBB the +10x (2017 → now): bought cheap-PB + high ROE compounding
date           Close    PB    PE  ROE5Y
2017-01-03      2710  0.91   8.6  14.1%
2019-01-02      5070  1.33   8.3  13.9%
2021-01-04      8010  1.45   8.0  15.7%
2023-01-03      9750  1.12   4.6  19.2%
2026-05-29     25000  1.34   7.3  22.9%
  → price 9.2x since 2017; PB then 0.91 (cheap) → re-rate + ROE compounding

Read: cheap bank = LOW P/B for its ROE (negative resid) + high stable ROE + credit growth.
PE is secondary; PEG misleads (bank growth=balance-sheet, not the same as industrials).
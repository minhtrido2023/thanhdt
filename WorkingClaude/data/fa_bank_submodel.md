# Bank FA sub-model PROTOTYPE (ICB 8355)

bank-quarter rows 775 | tickers 27 | 2014-02-06→2026-05-04
rows w/ forward profit_3M 751

## Bank-axis IC vs forward profit_3M
axis            weight       IC      N
--------------------------------------
profit            35%  +0.0446    751
growth            25%  +0.0302    751
safety            25%  +0.0523    751
value             15%  +0.0313    751

## Head-to-head IC (identical bank rows): bank sub-model vs generic FA
model               IS_IC   OOS_IC   ALL_IC      N
--------------------------------------------------
bank sub-model    +0.0239  +0.0469  +0.0363    722
generic total     +0.0663  -0.0446  -0.0054    722

## Tier monotonicity — median profit_3M (want A>B>C>D>E)
model                    A       B       C       D       E
------------------------------------------------------------
bank sub-model        1.37    2.68    2.16    0.90    0.62  ✗
generic (banks)       2.56    0.86    3.82    1.56   -7.32  ✗

## Tercile robustness — median profit_3M by bank_score tercile (OOS 2020+)
tercile         N   median     mean    win%
Top           176    4.68%    5.98%   59.7%
Mid           167    3.11%    4.58%   55.7%
Bot           186    1.03%    4.11%   52.7%

## Latest bank ranking (most recent report per bank)
tkr   quarter  tier   score  ROEtr   NP_R OwnEqCap    PBz
MBB   2026Q1   A      0.734  0.205  +0.14    1.763  +1.66
HDB   2026Q1   A      0.729  0.238  +0.13    1.564  +1.92
NAB   2026Q1   A      0.675  0.197  +0.34    1.366  +0.98
VPB   2026Q1   B      0.661  0.158  +0.59    2.272  +0.36
LPB   2026Q1   B      0.638  0.248  -0.10    1.580  +1.62
KLB   2026Q1   B      0.635  0.248  +0.46    1.446  +0.46
ACB   2026Q1   B      0.633  0.176  +0.17    1.840  +0.75
TPB   2026Q1   C      0.622  0.171  -0.01    1.659  +0.26
TCB   2026Q1   C      0.620  0.152  +0.12    2.533  +0.90
ABB   2026Q1   C      0.606  0.211  +2.61    1.204  +2.51
VCB   2026Q1   C      0.603  0.160  +0.09    2.723  +0.61
CTG   2026Q1   C      0.599  0.219  +0.65    2.313  +2.09
MSB   2026Q1   C      0.546  0.141  +0.20    1.360  +1.28
VIB   2026Q1   C      0.520  0.164  +0.16    1.378  +0.46
SHB   2026Q1   D      0.512  0.182  +0.07    1.480  +1.58
BID   2026Q1   D      0.508  0.181  +0.16    2.385  -0.24
BAB   2021Q3   C      0.476  0.086  +0.57    0.928  +0.50
VBB   2025Q4   D      0.407  0.117  +1.10    1.154  -0.16
OCB   2026Q1   D      0.402  0.128  +0.37    1.275  +0.83
BVB   2026Q1   D      0.366  0.070  +1.69    1.164  +0.03
VAB   2026Q1   D      0.358  0.141  +0.39    1.242  +1.28
SSB   2026Q1   D      0.338  0.077  -0.68    1.419  -1.77
NVB   2026Q1   E      0.322  0.043  +0.43    0.705  -0.63
PGB   2023Q3   E      0.227  0.078  -0.60    0.886  +0.14
STB   2026Q1   E      0.222  0.074  -0.45    3.176  +2.38

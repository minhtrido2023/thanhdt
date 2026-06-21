# FA 7-axis IC Audit

Rows total 12,367 | with forward profit_3M 11,206 | date 2014-04-29→2026-01-30
State coverage: CRISIS=3615, BEAR=1804, NEUTRAL=3576, BULL=1491, EX-BULL=720

## 1. Per-axis IC vs forward profit_3M (overall)

axis           weight       IC       N
--------------------------------------
quality          18%  +0.0651  11,206
stability        18%  +0.0866  11,206
cash             18%  +0.0707  11,206
shareholder      15%  +0.0794  11,206
growth           13%  +0.0538  11,206
health            8%  -0.0386  11,206
valuation        10%  -0.0284  11,206
--------------------------------------
total_score      100% +0.0946  11,206
equal-weight    (1/7) +0.0822

Interpretation: axes with IC near 0 or negative are not earning their weight;
if equal-weight ≈ total_score, the hand-set weights add little.

## 2. Regime-conditional IC (total_score vs profit_3M, per 5-state)

state            IC       N   med_p3M
-------------------------------------
CRISIS     +0.1550   3,615    -2.58%
BEAR       +0.0367   1,804     2.76%
NEUTRAL    +0.0942   3,576    -0.42%
BULL       -0.0032   1,491     0.00%
EX-BULL    +0.1690     720    -6.18%

### Per-axis IC by state

axis              CRIS     BEAR     NEUT     BULL     EX-B
----------------------------------------------------------
quality         +0.126   +0.014   +0.070   -0.048   +0.124
stability       +0.134   +0.013   +0.072   +0.066   +0.205
cash            +0.129   +0.041   +0.071   -0.029   +0.063
shareholder     +0.121   +0.034   +0.098   -0.027   +0.131
growth          +0.053   +0.009   +0.071   +0.043   +0.128
health          -0.050   +0.002   -0.055   -0.022   -0.063
valuation       -0.043   -0.014   -0.027   +0.020   -0.088

## 3. Tier monotonicity (median profit_3M, want A>B>C>D>E)

cohort           A       B       C       D       E   mono
----------------------------------------------------------
ALL           1.11    0.86   -0.97   -2.34   -4.29   ✓
CRISIS        1.58   -1.29   -1.97   -4.16   -7.69   ✓
BEAR          5.82    4.33    1.09    1.59    0.00   ✗
NEUTRAL       0.98    1.19    0.00   -1.23   -3.85   ✗
BULL         -0.36    1.61    0.00   -1.62    0.00   ✗
EX-BULL      -6.74   -2.65   -6.80   -6.81  -10.90   ✗

## 4. Axis score correlation (redundancy check)

         qual   stab   cash   shar   grow   heal   valu
quali    1.00   0.34   0.34   0.50   0.29  -0.03  -0.07
stabi    0.34   1.00   0.34   0.45   0.50  -0.26  -0.08
cash     0.34   0.34   1.00   0.39   0.14  -0.14  -0.13
share    0.50   0.45   0.39   1.00   0.45  -0.13   0.03
growt    0.29   0.50   0.14   0.45   1.00  -0.28   0.10
healt   -0.03  -0.26  -0.14  -0.13  -0.28   1.00   0.02
valua   -0.07  -0.08  -0.13   0.03   0.10   0.02   1.00

High-correlation pairs (|ρ|≥0.45 → candidate redundancy):
  quality ↔ shareholder: +0.50
  stability ↔ growth: +0.50
  stability ↔ shareholder: +0.45

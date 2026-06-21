# Tin hieu gia DAU rieng (loc beta thi truong) + bien dong

## (A) Oil beta 2 NHAN TO: stock_ret ~ market(VNINDEX) + Brent (monthly)
bM = beta thi truong, bO = beta dau RIENG sau khi loc market. R2 = giai thich tong.

tk      bMarket    bOil     R2    n   group
PVD        1.48    0.13   0.43  160   UPSTREAM (573)
PVS        1.42    0.10   0.44  160   UPSTREAM (573)
PVB        1.51   -0.09   0.27  149   UPSTREAM (573)
PVC        1.30    0.13   0.27  160   UPSTREAM (573)

BSR        1.37    0.13   0.35   98   REFINE/DISTRIB (533)
PLX        1.09   -0.02   0.33  109   REFINE/DISTRIB (533)
OIL        1.17   -0.03   0.32   98   REFINE/DISTRIB (533)

GAS        1.12    0.11   0.35  160   GAS (7573)
PGS        0.77    0.03   0.20  160   GAS (7573)
CNG        0.50    0.04   0.14  160   GAS (7573)
PGD        0.59   -0.02   0.10  160   GAS (7573)
PGC        0.61   -0.01   0.20  160   GAS (7573)
PVG        0.87    0.06   0.21  160   GAS (7573)

DPM        0.84   -0.08   0.22  160   FERT/CHEM (1357)
DCM        0.92   -0.13   0.22  134   FERT/CHEM (1357)
DGC        0.84    0.03   0.15  141   FERT/CHEM (1357)
CSV        0.76   -0.00   0.14  134   FERT/CHEM (1357)

PVT        1.16    0.04   0.37  160   TRANSPORT (2773)
VIP        0.70    0.03   0.18  160   TRANSPORT (2773)
VTO        0.76    0.03   0.24  160   TRANSPORT (2773)
GSP        0.44    0.00   0.12  160   TRANSPORT (2773)
PVP        0.96   -0.04   0.14  113   TRANSPORT (2773)

Group median:
group                   bMarket    bOil
UPSTREAM (573)             1.45    0.11
REFINE/DISTRIB (533)       1.17   -0.02
GAS (7573)                 0.69    0.03
FERT/CHEM (1357)           0.84   -0.04
TRANSPORT (2773)           0.76    0.03

## (B) Horizon QUY: stock_qret ~ Brent_qret (it nhieu hon monthly)
tk      beta_q     R2   nQ   group
PVD       0.39   0.06   53   UPSTREAM (573)
PVS       0.36   0.09   53   UPSTREAM (573)
PVB      -0.17   0.01   50   UPSTREAM (573)
PVC       0.30   0.03   53   UPSTREAM (573)

BSR       0.57   0.13   33   REFINE/DISTRIB (533)
PLX       0.11   0.02   36   REFINE/DISTRIB (533)
OIL       0.13   0.02   33   REFINE/DISTRIB (533)

GAS       0.34   0.10   53   GAS (7573)
PGS       0.19   0.04   53   GAS (7573)
CNG       0.08   0.01   53   GAS (7573)
PGD       0.04   0.00   53   GAS (7573)
PGC       0.11   0.02   53   GAS (7573)
PVG       0.15   0.02   53   GAS (7573)

DPM       0.20   0.04   53   FERT/CHEM (1357)
DCM       0.12   0.01   45   FERT/CHEM (1357)
DGC      -0.03   0.00   47   FERT/CHEM (1357)
CSV       0.16   0.01   45   FERT/CHEM (1357)

PVT       0.29   0.06   53   TRANSPORT (2773)
VIP       0.03   0.00   53   TRANSPORT (2773)
VTO       0.14   0.02   53   TRANSPORT (2773)
GSP       0.11   0.02   53   TRANSPORT (2773)
PVP       0.20   0.02   38   TRANSPORT (2773)

Group median quarterly oil beta:
  UPSTREAM (573)        +0.33  (R2 0.05)
  REFINE/DISTRIB (533)  +0.13  (R2 0.02)
  GAS (7573)            +0.13  (R2 0.02)
  FERT/CHEM (1357)      +0.14  (R2 0.01)
  TRANSPORT (2773)      +0.14  (R2 0.02)

## (C) Event study — 30 thang co |Brent move|>=10%
So sanh do lon & PHAN TAN buoc gia co phieu trong thang soc dau vs thang thuong.
group                  mean|r|_shock mean|r|_calm  amplify x dir_corr
UPSTREAM (573)                 15.5%         9.0%       1.73     0.66
REFINE/DISTRIB (533)           12.7%         8.9%       1.42     0.65
GAS (7573)                      8.2%         6.1%       1.34     0.57
FERT/CHEM (1357)               11.2%         7.3%       1.53     0.55
TRANSPORT (2773)                8.1%         7.0%       1.15     0.62

amplify x>1 = co phieu bien dong manh hon binh thuong trong thang soc dau;
dir_corr>0.5 = co phieu nghieng theo HUONG cu soc dau (cung chieu).
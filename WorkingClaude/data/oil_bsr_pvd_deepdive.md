# BSR — tach LAI/LO TON KHO khoi BIEN LOC (crack)
oil_qoq = % thay doi gia dau (cuoi quy vs cuoi quy truoc) = dong luc ton kho.
brent_avg = mat bang gia (proxy moi truong crack).

GPM ~ -0.084 +0.00178*brent_avg +0.016*oil_qoq   (R2 tong=0.56, n=32)
  chi LEVEL (crack proxy):     R2=0.56
  chi OIL_QOQ (ton kho):       R2=0.01
  -> he so oil_qoq +0.016: dau +10% trong quy => GPM +0.2pp

huong dau trong quy  nQ   GPM_tb   NPM_tb  NP_tb(bn)  GP_tb(bn)  %quy LO
DAU GIAM >10%      5     5.0%     4.2%       -359       1846      60%
DI NGANG          17     4.3%     3.5%       1606       1519       6%
DAU TANG >10%     10     4.8%     3.8%       2074       1666      10%
-> CRACK (level brent_avg) chi phoi BIEN goc (R2 0.56); HUONG dau (ton kho) chi phoi DUOI:
   moi quy dau SAP >10% deu ke lo/sat lo (NRV trich lap ton kho), dau VOT = lai dot bien.

Cac quy cuc tri (theo oil_qoq):
quarter    oil_qoq brent_avg    GPM   NP_bn
2018Q4        -27%        68     5%   -1010
2020Q1        -52%        50     1%   -2330
2020Q2        +26%        29    -2%   -1906
2021Q1        +31%        61     3%    1856
2022Q1        +58%       100     8%    2324
2022Q3        -27%       101    11%     479
2023Q4        -17%        84     7%    2279
2026Q1        +65%        80    10%    8265

Uoc luong PHAN NP do ton kho (~ b2*oil_qoq*Revenue, gop xap xi):
  2018Q4: oil -27% -> ~-124 bn (NP thuc -1010 bn)
  2020Q1: oil -52% -> ~-147 bn (NP thuc -2330 bn)
  2020Q2: oil +26% -> ~+55 bn (NP thuc -1906 bn)
  2021Q1: oil +31% -> ~+101 bn (NP thuc +1856 bn)
  2022Q1: oil +58% -> ~+315 bn (NP thuc +2324 bn)
  2022Q3: oil -27% -> ~-166 bn (NP thuc +479 bn)
  2023Q4: oil -17% -> ~-112 bn (NP thuc +2279 bn)
  2026Q1: oil +65% -> ~+464 bn (NP thuc +8265 bn)

# PVD — do TRE backlog theo chu ky gian khoan
Cross-correlation: corr( metric[t], Brent_avg[t-lag] ) cho lag 0..8 quy.
Lag dinh = so quy loi nhuan PVD tre sau gia dau (do hop dong day-rate cham).

lag(quy)      0     1     2     3     4     5     6     7     8
GPM       +0.30 +0.36 +0.47 +0.62 +0.73 +0.79 +0.81 +0.80 +0.75   <- dinh lag 6Q
NPM       +0.19 +0.21 +0.28 +0.37 +0.49 +0.46 +0.42 +0.29 +0.29   <- dinh lag 4Q
NP        +0.37 +0.45 +0.54 +0.64 +0.69 +0.65 +0.61 +0.52 +0.44   <- dinh lag 4Q
Rev       +0.39 +0.51 +0.58 +0.65 +0.67 +0.66 +0.63 +0.61 +0.54   <- dinh lag 4Q

## Theo tung chu ky (GPM la tin hieu sach nhat, NP nhieu boi FX/JV)
Dau xoay (avg) vs PVD GPM xoay:
- Dau DINH 2014Q2 (~111) -> PVD GPM dinh
    PVD GPM ~20% giu den 2015Q3, roi do
- Dau DAY 2016Q1 (~34)  -> PVD GPM DAY
    PVD GPM DAY 2017Q1 (-2%) ~ tre 4Q; lo 2017Q1/2018Q1
- Dau HOI 2016-2018 (34->81)
    PVD GPM chi nhuc nhich 2019 (~13%) ~ tre 8-12Q
- Dau SAP COVID 2020Q2 (~29)
    PVD GPM ep ve 8% 2020-2022, lo rong 2022
- Dau HOI 2020Q2->2022Q2 (29->122)
    PVD GPM PHUC HOI manh tu 2023Q2 (18->24%) ~ tre 8-12Q
- Dau VOT 2026Q1 (66->103)
    PVD GPM 2026Q1 chi 19% (chua phan anh) -> ky vong hich 2026H2-2027

Quy te (PVD GPM vs Brent avg, 2014+):
quarter   brent_avg    GPM    NPM   NP_bn
2013Q4          109    20%    11%     480
2014Q1          108    23%    14%     597
2014Q2          110    20%    13%     731
2014Q3          102    19%    11%     591
2014Q4           76    17%     8%     449
2015Q1           54    20%    11%     482
2015Q2           62    27%    14%     529
2015Q3           50    22%    15%     559
2015Q4           44    17%     3%      77
2016Q1           34    15%     4%      56
2016Q2           46    16%     1%      20
2016Q3           46    18%     1%      10
2016Q4           49     9%     4%      34
2017Q1           54    -2%   -40%    -201
2017Q2           50     8%    -5%     -52
2017Q3           52     7%     2%      25
2017Q4           62     2%    21%     254
2018Q1           67     3%    -1%    -239
2018Q2           74     2%    -1%     -68
2018Q3           75     2%     1%     112
2018Q4           68     7%     3%     386
2019Q1           63     9%     6%     -87
2019Q2           69    13%    11%     109
2019Q3           62    14%    10%      27
2019Q4           63    10%     4%     140
2020Q1           50    11%     6%      24
2020Q2           29     8%     4%      62
2020Q3           43     8%     4%      39
2020Q4           44     6%     4%      60
2021Q1           61     4%     1%    -104
2021Q2           69    13%     1%       6
2021Q3           73     8%     2%      67
2021Q4           80     8%     2%      50
2022Q1          100     9%     1%     -56
2022Q2          114     9%    -1%     -60
2022Q3          101     9%    -3%     -34
2022Q4           89    11%    -3%      54
2023Q1           81    14%    -0%      66
2023Q2           78    18%     4%     164
2023Q3           87    21%     7%     151
2023Q4           84    22%     9%     195
2024Q1           83    24%    10%     158
2024Q2           85    23%     8%     138
2024Q3           80    22%     8%     182
2024Q4           75    19%     8%     220
2025Q1           76    17%     8%     153
2025Q2           68    18%     9%     240
2025Q3           69    19%    10%     278
2025Q4           64    19%    10%     365
2026Q1           80    19%     9%     306
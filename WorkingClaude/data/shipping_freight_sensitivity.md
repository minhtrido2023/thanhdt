# VN vận tải biển CÓ chịu ảnh hưởng cước thế giới? (2018Q1-2026Q1)
corr quý NP & NPM với chỉ số cước segment (contemporaneous + lag 1-2Q). lag>0 = lợi nhuận trễ cước.
⚠ freight = tái dựng xấp xỉ (data/freight_rates_quarterly.csv).

## CONTAINER→SCFI
  tk     nQ  NP~idx  NP~L1  NP~L2  NPM~idx
  HAH    33   +0.37  +0.54  +0.61    +0.32

## DRY BULK→BDI
  tk     nQ  NP~idx  NP~L1  NP~L2  NPM~idx
  VOS    33   +0.55  +0.41  +0.26    +0.58
  VNA    33   +0.59  +0.49  +0.57    +0.48
  VSA    33   -0.02  +0.01  +0.06    -0.27

## TANKER→BDTI
  tk     nQ  NP~idx  NP~L1  NP~L2  NPM~idx
  PVT    33   +0.34  +0.28  +0.48    +0.28
  VTO    33   +0.06  -0.11  -0.06    +0.25
  VIP    33   +0.53  +0.40  +0.32    +0.29
  GSP    33   +0.43  +0.38  +0.37    +0.26
  PVP    33   +0.04  +0.03  +0.10    +0.03

## PORTS (control, volume)
  (nhóm CẢNG = đối chứng: lợi nhuận theo SẢN LƯỢNG thông qua, không theo giá cước → kỳ vọng corr thấp/nhiễu)
  tk     nQ  NP~idx  NP~L1  NP~L2  NPM~idx
  GMD    33   -0.13                (vs avg-freight)
  VSC    33   +0.43                (vs avg-freight)
  SGP    33   +0.45                (vs avg-freight)

## Tổng hợp segment (median NP~idx contemporaneous) + cước HIỆN TẠI
  CONTAINER→SCFI             +0.37  | SCFI now=1320
  DRY BULK→BDI               +0.55  | BDI now=1700
  TANKER→BDTI                +0.34  | BDTI now=1050
  PORTS (control, volume)    +0.43

Đọc (KẾT LUẬN): VN shipping CÓ chịu ảnh hưởng cước thế giới, nhưng MỨC & CƠ CHẾ khác nhau theo segment:
- DRY BULK (VOS/VNA) = link MẠNH & SẠCH nhất (~0.55-0.59): bám BDI sát, LỖ ở đáy cước, lãi khi BDI vọt.
- CONTAINER (HAH) = rõ trong bùng nổ 2021-22 (lag 2Q +0.61), nhưng 2024-25 NỚI LỎNG do MỞ RỘNG ĐỘI TÀU
  (NP lập đỉnh mới dù SCFI chỉ trung bình) → stock-specific (fleet) lấn dần cước spot.
- TANKER (PVT) = ĐỆM bởi charter dài hạn: ổn định, thậm chí NP tăng khi BDTI giảm 2024-25 → ít theo spot.
  (VTO/PVP ~0 = hợp đồng cố định hoàn toàn).
- CẢNG (GMD ~0) = SẢN LƯỢNG-driven, KHÔNG theo cước; cảng nhỏ (VSC/SGP +0.43) chỉ co-move qua chu kỳ
  thương mại chung 2021-22, không phải nhạy cước trực tiếp.
→ Caveat: cấu trúc nhân-quả mạnh nhất ở BULK; ở các name lớn (HAH/PVT) fleet+charter ngày càng tách spot.

### HAH NP(bn) vs SCFI:
  2020Q1:30/900  2020Q2:36/880  2020Q3:23/1250  2020Q4:50/2100  2021Q1:67/2800  2021Q2:82/3700  2021Q3:93/4350  2021Q4:203/4550  2022Q1:200/4750  2022Q2:240/4150  2022Q3:218/2900  2022Q4:171/1450  2023Q1:119/1000  2023Q2:97/970  2023Q3:106/1000  2023Q4:63/1050  2024Q1:59/2000  2024Q2:112/2900  2024Q3:199/3250  2024Q4:280/2400  2025Q1:233/1800  2025Q2:362/1900  2025Q3:304/1500  2025Q4:308/1380  2026Q1:300/1320

### VOS NP(bn) vs BDI:
  2020Q1:-86/590  2020Q2:-31/640  2020Q3:-21/1490  2020Q4:-47/1300  2021Q1:-19/1740  2021Q2:242/2790  2021Q3:185/3870  2021Q4:82/3990  2022Q1:56/2010  2022Q2:260/2570  2022Q3:154/1750  2022Q4:18/1500  2023Q1:73/880  2023Q2:1/1230  2023Q3:-23/1100  2023Q4:105/2030  2024Q1:75/1900  2024Q2:284/1840  2024Q3:-14/1900  2024Q4:-9/1480  2025Q1:-54/950  2025Q2:10/1350  2025Q3:132/1900  2025Q4:217/1900  2026Q1:4/1700

### PVT NP(bn) vs BDTI:
  2020Q1:67/1150  2020Q2:194/950  2020Q3:108/440  2020Q4:262/430  2021Q1:136/560  2021Q2:241/570  2021Q3:94/580  2021Q4:197/600  2022Q1:153/900  2022Q2:207/1150  2022Q3:271/1420  2022Q4:207/1720  2023Q1:182/1520  2023Q2:309/1150  2023Q3:249/1050  2023Q4:230/1260  2024Q1:231/1320  2024Q2:288/1250  2024Q3:365/1170  2024Q4:209/1160  2025Q1:215/1120  2025Q2:295/1060  2025Q3:263/1010  2025Q4:266/1000  2026Q1:319/1050

# Working memory — DollarBill
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của DollarBill.

- [2026-10-21T15:32:27Z] 21/10: DRI bị bán là USER bán tay (xác nhận, decided_by user): SpaceX −1.200cp→2.500, ZaloPay −600cp→1.300 @15.400. KHÔNG hỏi lại/không flag bất thường/không escalate. Dùng KL mới khi lập plan. active_nav fail-closed là vấn đề code đã biết (xem current_ops), không phải do DRI bất thường.
- [2026-10-22T12:05:22Z] [2026-10-22 19:xx ICT] Plan SpaceX 10-23 XONG HOLD ALL 0 lenh (job DollarBill_20261022_120433); LAG HT1/SCL/VPB vao ~10-26 can cash (avail 21,96tr, egg 851tr); cho duyet truoc 08:45 ICT 23/10
- [2026-10-23T12:06:24Z] [2026-10-23 19:xx ICT] Plan ZaloPay 10-26 XONG HOLD ALL 0 lenh (job DollarBill_20261023_120512); LAG HT1/SCL/VPB due 10-26 DEFER (avail 3.748d, egg 535tr); cho duyet truoc 08:45 ICT 26/10
- [2026-10-24T08:11:36Z] [2026-10-24 15:xx ICT] Plan ZaloPay 10-26 LAM LAI TAY: HOLD ALL, 3 LAG bi cong DD chan (HT1/VPB FLAG_NO_ACK, SCL ACK_STALE). SpaceX plan 10-26 con stale (TAKE/DEFER) -> can sinh lai/doi Mike. job DollarBill_20261024_081051
- [2026-10-24T08:20:15Z] [2026-10-24 15:2x ICT] Plan SpaceX 10-26 LAM LAI TAY XONG HOLD ALL 0 lenh (job DollarBill_20261024_081956); 3 LAG bi cong DD chan; cho user duyet truoc 08:45 ICT 26/10
- [2026-10-24T08:27:31Z] [2026-10-24 15:3x ICT] Plan ZaloPay 10-26 LAM LAI XONG 3 lenh LAG (HT1/SCL/VPB, 71.4tr, chuyen egg>=71.5tr). SpaceX plan 10-26 con HOLD ALL -> lech calendar check, can sinh lai. job DollarBill_20261024_082711
- [2026-10-24T08:28:46Z] [2026-10-24 ICT] Plan SpaceX 10-26 LAM LAI (egg=tien) XONG: 3 LAG HT1/SCL/VPB ~116,4tr, chuyen egg >=116,4tr truoc 09:05 T2; job DollarBill_20261024_082713; cho user duyet
- [2026-10-26T12:06:34Z] [2026-10-26 19:xx ICT] Plan SpaceX 10-27 XONG: 1 lenh MUA SCL 300cp residual (HT1/VPB khop du 26/10); DNSE API auth 500 -> thieu gia live/active_nav; cho user duyet truoc 08:45 ICT 27/10; job DollarBill_20261026_120425
- [2026-10-26T12:06:58Z] [2026-10-26 19:xx ICT] Plan ZaloPay 10-27 XONG: residual SCL200/VPB200 (job DollarBill_20261026_120424); DNSE API 500 auth lúc lập plan -> giá/số dư từ log, cần kiểm lại; cho user duyệt truoc 08:45 ICT 27/10
- [2026-10-27T12:06:46Z] [2026-10-27 19:xx ICT] Plan ZaloPay 10-28 XONG: 1 lenh SCL 200cp LO<=32.700 (ngay 3/3, gia dong cua 33.300 > tran), VPB/HT1 du; khong can chuyen egg; DNSE live OK; cho duyet truoc 08:45 ICT 28/10 (job DollarBill_20261027_120457)
- [2026-10-27T12:06:59Z] [2026-10-27 19:xx ICT] Plan SpaceX 10-28 XONG: 1 lenh MUA SCL 300cp LO 32.700 (residual ngay 3/3); egg>=1,2tr; DNSE live OK; cho duyet truoc 08:45 28/10 (job DollarBill_20261027_120459)
- [2026-10-28T12:05:43Z] [2026-10-28 19:xx ICT] Plan ZaloPay 10-29 XONG: BUY MCH 200cp LO 139.800 (~27,99tr), chuyen egg >=20,6tr truoc 09:05; cho duyet truoc 08:45 29/10 (job DollarBill_20261028_120432)

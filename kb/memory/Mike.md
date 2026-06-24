# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **cần user + Spyros approval**
## Đang chờ
- **Spyros**: review data/v24_golive_summary.md → sign-off go-live
- **User**: approve go-live V2.4 config
- Wendy: legal-severity DGC → Taylor risk/reward
## Next (khi user approve)
- DollarBill lập plan T+1 go-live
## R&D đã đóng
- Exp-2 hold-neutral: REJECTED (DT5G về NEUTRAL quá nhanh, exit sớm 14/15 events, ~5.3% thua)
- Exp-3 deposit_eyield: REJECTED BQ-pinned (CAGR 29.73%/DD-31.7%/Cal 0.94 — tệ hơn V2.4-LF). Bug: gate fire vào COVID-2020 (eyield>deposit nhưng market đắt). fedborrow-dormant (32.22%/DD-15.5%/Cal 2.08) vẫn là best margin gate.
- PE bug NOT MATERIAL, V2.4 go-live summary done, 3-tier snapshot pipeline done
## Margin upgrade conclusion
- **MGE=1.3 fedborrow-dormant** là cấu hình margin tốt nhất, chưa go-live (cần Spyros + user trước khi live)


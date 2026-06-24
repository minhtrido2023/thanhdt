# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **cần user + Spyros approval**
## Đang chờ
- **Spyros**: review data/v24_golive_summary.md → sign-off go-live
- **User**: approve go-live V2.4 config + quyết định có chạy BQ sim Exp-3 không
- Wendy: legal-severity DGC → Taylor risk/reward
## Next (khi user approve)
- DollarBill lập plan T+1 go-live
- Nếu user muốn pin Exp-3: chạy BQ Tier-3 sim (1 scan) với MGE_GATE=deposit_eyield
## Đã xong R&D
- Exp-2 hold-neutral: REJECTED (DT5G về NEUTRAL quá nhanh, exit sớm hơn 14/15 events, ~5.3% thua)
- Exp-3 deposit_eyield gate: PROMISING — 12/15 events fire (vs 0/15 fedborrow). Block đúng 2018-BEAR-expensive. Est ~32.0%/DD-15.8/Cal2.03 — CẦN BQ sim để pin
- PE bug NOT MATERIAL, V2.4 go-live summary done, 3-tier snapshot pipeline done


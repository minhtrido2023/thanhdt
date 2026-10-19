# STALE — số `ortho_8l` / "8L top-25" trong các verdict dưới đây là THEO BUG sort

Gán nhãn 2026-10-19 (user chọn "gán nhãn stale", KHÔNG sinh lại). Các file chưa bị sửa nội dung (giữ nguyên pin/md5).

- Nguyên nhân: `ascending=False` trên thang rating 1-5 (1 = tốt nhất) ⇒ "8L top-25" = 25 mã XẤU nhất. Vá merge `ec9750f2` (2026-09-27 19:25 ICT).
- Mọi file dưới đây sinh lúc 2026-09-27 13:19-13:20 ICT, TRƯỚC bản vá.
- KHÔNG trích `ortho_8l`, overlap với 8L, hay kết luận "bổ sung alpha mới, không lặp 8L" từ chúng. Cần dùng ⇒ chạy lại đúng screen đó rồi mới đọc.
- Chi tiết + mức sai: `mike/kb/projects/screen-sort-direction-bug-20260927.md`.

## File STALE (16)
- `data/aviation_verdict.json`
- `data/bank_compounder_verdict.json`
- `data/compounder_screen_verdict.json`
- `data/construction_verdict.json`
- `data/energy_verdict.json`
- `data/fertchem_rubber_verdict.json`
- `data/fnb_verdict.json`
- `data/livestock_verdict.json`
- `data/logistics_port_verdict.json`
- `data/pharma_verdict.json`
- `data/re_compounder_verdict.json`
- `data/retail_compounder_verdict.json`
- `data/securities_verdict.json`
- `data/steel_buildmat_verdict.json`
- `data/tech_verdict.json`
- `data/textile_verdict.json`

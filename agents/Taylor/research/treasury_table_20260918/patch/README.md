# Vá `SHARE_CODES` cho `final3.py` (bản sao — KHÔNG sửa file trong thư mục Winston)

Gốc: `mike/agents/Winston/research/treasury_size_20260918/final3.py` (job Winston_20260918_052425).
Thay đổi duy nhất: `SHARE_CODES={"ISS","DIV","AIS","MA"}` → thêm `"SUSP","NLIS","MOVE"`.
Lý do: 3 mã đó CÓ `shares_delta` (trên tập ticker này: SUSP 54 dòng, NLIS 1) nên bỏ sót chúng là
đúng cùng lớp lỗ hổng confounder từng quy nhầm phát hành thành "bán CP quỹ" (VPB 1,19 tỷ CP,
TPB 100tr CP). Output cũng đổi tên (`*_patched.csv`) để không đè file gốc của Winston.

**Kết quả: no-op trên batch hiện tại** — 33 ca suy được không đổi một ca nào
(`resolved_patched.csv` ≡ `resolved.csv` gốc trên bộ khoá `ticker|public_date|action_type|inferred`),
control vẫn 13/131 suy được / 76,9% khớp chính xác. Giá trị của bản vá là bịt lỗ cho batch tương lai.

Tái lập (từ thư mục này):
```
cp ../../../../Winston/research/treasury_size_20260918/{fin,ca,events}.csv .
$DNA_PYEXE final3.py
```

# Spread CCTG Big-4 vs huy dong Big-4 12M online — lich su (job Taylor_20261120_120902)

## Ket luan (thang that ve do phu)
**Khong dung duoc lich su CCTG Big-4 de do spread theo che do lai suat.** Chi tim duoc nguon cho
**2026-01 → 2026-11** (+ 1 moc VietinBank 04/2009 ngoai cua so). 2011–2025: **khong co du lieu**
(2 vong WebSearch; khong tim thay thong bao CCTG ban le Big-4). Day la "khong tim thay", KHONG phai
chung minh Big-4 khong phat hanh — nhung bao chi 2026 mo ta Big-4 CCTG la hien tuong moi.
Du lieu: `cctg_hist.csv` (nguon+URL+confidence). Spread: `spread_big4.csv`, `spread_tier2.csv`, script `spread.py`.

## Spread = CCTG 12M cao nhat Big-4 − deposit Big-4 12M online (deposit_rate_vn, step series)
| Ngay | CCTG | Deposit | Spread pp | Tin cay |
|---|---|---|---|---|
| 2026-01-21 | 6.0 (VCB) | 6.0 | 0.0 | HIGH (CCTG), deposit la anchor frozen |
| 2026-04-02 | 7.9 (VCB) | 6.0 | 1.9 | HIGH (CCTG); deposit 6.0 = anchor 01/01, KHONG phai quan sat thang 4 |
| 2026-06-26 | 7.4 (VCB, 1 nguon) | 6.8 | 0.6 | LOW |
| 2026-10-05..11-02 (3 moc) | 7.4 (BIDV/CTG) | 6.8 | 0.6 | MED |

**N = 6 quan sat, 4 thoi diem, 1 chu ky (2026, lai suat tang).** Trung vi 0.6, min 0.0, max 1.9.
Phan tich MO TA — **khong tuyen bo y nghia thong ke**, khong chia theo nam/che do (chi co 1 nam, 1 che do tang).

## Nhan xet
- Spread **khong on dinh** trong mau (0.0 → 1.9 → 0.6), nhung 2 diem dau bi nhiem: deposit series la
  step frozen anchor hoi to (06-19), khong phai quan sat thang 1/thang 4; spread 1.9 co the la gia tao.
  Spread 0.6 (06→11/2026) la so tin cay nhat va dung bang chenh hien tai 7.4 vs 6.8.
- "Tang khi thanh khoan chat?" — **khong tra loi duoc**: khong co pha thanh khoan chat/long thu hai de doi chieu.
- Quan sat dang chu y: VCB ha 12M tu 7.9 xuong 7.4 (≈06/2026) roi chi con 6M 7.5 (30/09) — CCTG cao nhat
  Big-4 bi **keo ve sat/tren 7.4 chu khong tang tiep**; ky han 12M cua VCB bien mat, doi tinh "Big-4 12M" cua CCTG.
- Kill-switch A (>7.5%, effective=max(Big-4 12M, CCTG)): CCTG 12M Big-4 = 7.4 < 7.5 ⇒ **chua armed**; CCTG 6M VCB
  (7.5) nam dung NGUONG (strict >). Voi spread ~0.6, ngưỡng chi bi vuot khi deposit 12M online ≥ ~6.9 *neu* CCTG giu +0.6,
  nhung la ngoai suy tu 1 moc — khong co co so thong ke. De xuat: khong chinh nguong tu bang nay.
- Chuoi bi **lech ky han**: VCB 6M 7.5 > 12M (VCB 12M 7.4 / BIDV 7.4) — dung la dao nguoc, khong phai loi (xem registry).

## Tier-2 (descriptive, N=7 dong, 3 ngay)
CCTG − deposit Big-4 12M (6.8): MB +0.3, ACB +0.4 (3M), TCB +0.8 (6M), VPB +2.2…2.4 (menh gia 100tr).
So voi CCTG Big-4 (7.4, chi tu 10/2026): MB −0.3, ACB −0.2, TCB +0.2, VPB +1.6…1.8. Ky han lech (3–9M vs 12M) nen
chi so sanh duoc sang trai; MB/ACB/TCB ≈ Big-4, VPB la ngoai le (bac menh gia lon). Khong co lich su Tier-2 truoc 06/2026.

## Bay / canh bao
1. BIDV 04/08/2026 "7.4% online" (baolamdong): khong ro CCTG hay tiet kiem online — de LOW, khong dung.
2. cafef 02/08 (VCB 12M 7.9) mau thuan vietnamnet 26/06 (7.4) va baolamdong 30/09 (chi 6M) — co the tin cu; khong dung.
3. Ngay hieu luc phan lon la ngay dang bai, khong phai ngay luat; do tre chua do.
4. Chua doc 2 nguon doc lap cho moc 06-26; 2009 chi 1 nguon.
5. KHONG sua file san xuat nao.

## Viec de lam neu muon co lich su that
Xin tay website/thong cao CCTG tung NH (VCB/CTG/BIDV) hoac hoi Winston pull Wayback; neu chi tuong lai, tiep tuc append CSV hang thang — can ~12+ moc bien dong moi du de noi chuyen thong ke.

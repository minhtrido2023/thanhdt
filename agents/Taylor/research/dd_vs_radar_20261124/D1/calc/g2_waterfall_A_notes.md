# g2_waterfall_A — ghi chu 9 ma (VCB DCM PNJ POW LLM VCP TTA QTP CST)
Quy uoc: chuoi (step_order so) = cac buoc DO DUOC trong bao cao, noi tiep nhau tu raw den tam cuoi (expected_weighted so). Hang `m#` = memo ngoai chuoi (do nhay / Delta giua phien ban / buoc khong tach duoc). Delta% la cumulative so voi raw; cot note co step_delta_pct. Khong co gia tri tho 'FCFF truoc moi haircut' o bat ky ma nao: raw la diem thap nhat con do duoc tu chinh bao cao.

## VCB (raw 45.900 -> 35.600, -22,4%)
- Raw = base scenario o Ke 12,3% (bao cao dong 95). Chuoi: r 13,5% (-18,5%) -> trong so kich ban 0,25/0,50/0,25 (-4,8% so base) -> CK 0%.
- Khong tach duoc: tru KTPL 2026 (-334 d/cp BVPS) + don bay cuoi ky (base 38.400 -> 37.400, -2,6%) da nam trong 'base'; Delta tung phan = NA.
- Do tin: trung binh (r va trong so tach duoc; nhung raw o Ke 12,3% chi do tren base, khong phai chuoi lich su). Kho: moi kich ban chon 1 cua so spread; co so 9T/26 gan day (2,85%) vs chu ky 2017-25 (+7,6% neu doi).

## DCM (raw 28.922 -> 27.393, -5,3%)
- Raw = tam diem 27.387 + 1.535 (Ke 12,3%) tinh bang cong, KHONG co dong goc. Chuoi: r (-5,3%), luoi 2.430 ket cuc (+0,6%), CK 0,585% (-0,6%).
- Khong tach duoc: quy KH&CN (thu hoi thue ngoai le), capex duy tri M=540, khi 2035+ da nam trong diem; Delta = NA. Cau noi rev8->rev9 (+2,3%) chi la Delta giua phien ban.
- Do tin: trung binh-thap cho 'raw'; do nhay (khi 2035+ -27,8%, thue XK 0% +3,8%, 4 cua so +7,4%) ghi o memo.

## PNJ (raw 9.211 -> 7.395, -19,7%)
- Raw = tam o Ke 12,3% (dong 62), da gom cay ket cuc phat hanh p=0,5 va trong so van hanh. Chuoi chi 1 buoc r (-19,7%), CK 0%.
- Don vi: d/cp tren ~511,72tr cp (O2) / 1.061,72tr (O1) sau thuong; gia ref 13.500 cung don vi, KHONG co lech chia tach (kiem: bao cao dong 15, 39-41).
- Rev4->rev5 tang +75,9% (3 sua tang do skeptic r3); trong so van hanh keo tam len +14,2% so kich ban co so: ghi memo. Do tin: cao ve so hoc, thap ve p (khong dinh luong duoc).

## POW (raw 10.217 -> 9.387, -8,1%)
- Raw = 9.482 + 735 (cong, tinh tu dong 13) = trong so ROE 4,5/8/11,5% truoc PV QCVN19; kich ban doi xung nen = co so. Chuoi: QCVN19 VA1 (-7,2%), CK 1% (-1,0%).
- r khong dua vao chuoi (chi co 9.861 o Ke 12,3% sau CK = +5,0%) vi khong co gia tri truoc QCVN o Ke 12,3%.
- Upside chi o do nhay: doi huu han von di san +10,3%..+16,1%, P100 +7,8%. Do tin: trung binh; quy mo QCVN19 'analog' 1:1 tu FS QTP.

## LLM (raw 35.771 -> 20.978, -41,4%)
- Raw = 'bo f rieng kich ban xau' (f=1 ca 3) o co so SAU CK 10% (cau noi dong 90-95); CK 10% va trong so 2/9-6/9-1/9 da nhung san trong moi buoc. Chuoi: NCI -0,8%, hoan bao hanh -1,7%, f tien (tien ket) -31,5% (cua 34.886), f dau tu DH -12,3%.
- Buoc lon nhat = 'tien ket' hazard p Laplace 1/11 (0 su kien chia/9 nam): p 0 => 11.612, p 0,2 => 25.507, f=1 => 34.886. Bang chung la lich su chia tien that (BQ + KT25 LCTT) nhung estimator p la tu chon.
- Do tin: trung binh. Khong co 'raw' truoc CK/trong so; scenario_weighting truoc CK 24.901 -> 23.309 (-6,4%) o memo.

## VCP (raw 39.458 -> 29.686, -24,8%)
- Raw = tam co trong so khong chuan hoa thuy van (dong 87). Chuoi: chuan hoa k=1,0 x Etb (-21,9%) -> CK 3,63% (1 ty).
- k=1,0 la can duoi cua khoang do duoc [1,009; 1,061] (k=1,061 => +5,2%): buoc nay hai chieu ve nguyen tac nhung chon o can duoi. Rev3b->rev4 -9,0% la Delta giua phien ban.
- Do tin: cao ve du lieu (BCTN 2020-25), trung binh ve chon k.

## TTA (raw 15.170 -> 7.547, -50,3%)
- Raw = kich ban A (ket cuc FIT thuan nhat), KHONG phai gia tri tho FCFF: A/B/B'/C la ket cuc phap ly. Chuoi: trong so 0,15/0,25/0,35/0,25 (-48,8%) -> CK 2,89% (-2,9%).
- Gia tri 'raw' khong co; neu coi B (10.975) la co so thi weighting -29,2%. Giam r4->rev5 (-11,7%) do du lieu moi (bieu gia tranh duoc phang 7 nam; DT bo phan): memo.
- Do tin: trung binh-thap (raw la cuc phan phoi); luoi 30 o cho thay tam khong vuot gia o bat ky trong so nao.

## QTP (raw 14.599 -> 6.294, -56,9%)
- Raw = r2 pin truoc CK (chua tinh capex/opex tuan thu QCVN19). Chuoi di qua 4 phien ban mo hinh (r3, r3c, rev4b): capex tuan thu khi bu du (P100) -2,5%; trong so bu gia 0,5/0,3/0,2 -43,8%; +721 (P0 0,4), -871 (KTPL), -693 (tro lai 0,5), CK -10%.
- Phan lon la 1 so: xac suat bu gia (N=0 tien le), nen 'compliance_capex' va 'scenario_weighting' khong tach bach noi: toan bo -6.762 (-46%) la phan chi phi tuan thu khong duoc bu ky vong.
- Do tin: thap ve trong so; cao ve FS goc (TMDT 3.485, opex 572). Upside Cvlp q=1 +32,4% chi o do nhay.

## CST (raw 13.084 -> 5.837, -55,4%)
- Raw = rev1 (N = LNST gop). Chuoi: KTPL ro ri (-58,9%) -> ky quy moi truong (-6,3%) -> khoan chia 130,66 ty (+11,2%, buoc DUY NHAT di len trong chuoi cua 9 ma) -> CK (-1,4%).
- KTPL 5.382 = 4.563 + 819 tinh bang cong (REPORT_rev2.md:130); quy tac min(0,64N;82,3) dua tren 2 nam kiem toan (63,3%/63,8%), phap ly khong kiem chung; TB 5 nam chi 37% (=> 9.246, +53,5%) o do nhay.
- Do tin: cao ve so hoc (TM17 kiem toan), trung binh ve quy tac KTPL. Upside lon o do nhay: ro 37%, alpha 0,5, TKV bu chi phi von, thoai von.

## Ma KHONG tach duoc day du
- DCM (cac cau truc ben trong raw), TTA (raw = ket cuc A, khong phai gia tri tho), QTP (capex vs xac suat bu gia khong tach). Ba ma con lai (VCB, PNJ, POW) chi tach duoc 1-2 buoc; LLM tach duoc nhung tren co so sau CK.

# Số liệu nhập tay từ ảnh BCTC hợp nhất Q3/2026 (tỷ đồng) — trang ghi trong REPORT.md
sh=67.526165; px=26050
TA=4822.893520122; L=3488.157757730; E=1334.735762392; NCI=3.959820888
print("BS check TA-(L+E) =", round(TA-(L+E),6), "| TS NH+DH:", round(3926.262249565+896.631270557-TA,6))
print("Q3 NPAT giải trình 61.040.762.481 vs KQKD 61.040.762.481 -> khớp")
q3=dict(rev=517.063,gp=90.349,fi=35.735,fe=8.482,sell=2.471,ga=40.412,assoc=0.712,oth=1.014,tax=15.403,npat=61.041)
q3p=dict(rev=253.845,gp=40.671,fi=5.497,fe=2.097,sell=0.670,ga=34.099,assoc=4.541,oth=1.006,tax=1.409,npat=13.439)
m9=dict(rev=1199.230,gp=188.561,fi=99.905,fe=14.343,sell=5.487,ga=106.775,assoc=31.259,oth=2.262,tax=32.051,npat=163.331)
m9p=dict(rev=769.531,gp=118.921,fi=10.596,fe=4.946,sell=2.239,ga=93.525,assoc=23.932,oth=-0.447,tax=5.842,npat=46.450)
for n,d in [("Q3/26",q3),("Q3/25",q3p),("9T/26",m9),("9T/25",m9p)]:
    core=d['gp']-d['sell']-d['ga']; fin=d['fi']-d['fe']; pbt=core+fin+d['assoc']+d['oth']
    print(f"{n}: GPM {d['gp']/d['rev']*100:.1f}% | EBIT lõi {core:.1f} | TC ròng {fin:.1f} | LK {d['assoc']:.1f} | khác {d['oth']:.1f} | PBT {pbt:.1f} | tỷ trọng lõi/TC/LK {core/pbt*100:.0f}/{fin/pbt*100:.0f}/{d['assoc']/pbt*100:.0f}%")
cash=1059.700+1044.469; cash0=926.280+185.924; debt=152.780; debt0=81.229
adv=2416.355+2.241; adv0=984.347+2.241; prep=292.955; prep0=21.087; wip=119.482; wip0=42.672
print(f"Tiền+HTM {cash:.1f} (đầu năm {cash0:.1f}); net cash thô {cash-debt:.1f} ({cash0-debt0:.1f})")
f=adv-prep-wip; f0=adv0-prep0-wip0
print(f"Float ròng (tiền ứng - trả trước NCC - WIP) {f:.1f} ({f0:.1f}); net cash 'của cổ đông' {cash-debt-f:.1f} ({cash0-debt0-f0:.1f}) (ước lượng)")
print(f"Lãi tiền gửi 9T 87.1; TC thu Q3 35.7 -> năm hoá {35.735*4:.0f} trên số dư ~{cash:.0f} = {35.735*4/cash*100:.1f}%")
cfo9=858.609; cfoh1=983.953; print(f"CFO Q3 = {cfo9-cfoh1:.1f}; CFO 9T trừ tăng tiền ứng ({adv-adv0:.1f}) = {cfo9-(adv-adv0):.1f}")
cm=666.374; cm6=367.135; cm0=208.060; revcm9=478.728; revcmh1=244.359
print(f"CMC: DT 9T {revcm9}, H1 {revcmh1}, Q3 {revcm9-revcmh1:.1f}; phải thu {cm0}->{cm6}->{cm}; Q3 tăng {cm-cm6:.1f}; = {cm/E*100:.0f}% VCSH")
print(f"Erex ứng: {914.067+929.427:.1f}; tăng YTD {914.067+929.427-215.266-212.142:.1f}")
mcap=px*sh/1e3; bv=(E-NCI); print(f"Vốn hoá {mcap:.0f} tỷ; BVPS {bv/sh*1e3:.0f}; PB {mcap/bv:.2f}")
ttm=162.229+48.8; print(f"LNST TTM ~{ttm:.1f} (9T mẹ 162,2 + Q4/25 BQ 48,8) -> PE {mcap/ttm:.1f}; LNST 9T/KH 100 = {163.331/100*100:.0f}%")
for nm,w,v in [("Bear",.30,None),("Base",.50,170*9),("Bull",.20,250*10)]:
    pass
bear=0.8*(bv-160)/sh*1e3; base=170*9/sh*1e3; bull=250*10/sh*1e3
print(f"Bear {bear:.0f} Base {base:.0f} Bull {bull:.0f} -> kỳ vọng {0.3*bear+0.5*base+0.2*bull:.0f}; 85% = {0.85*(0.3*bear+0.5*base+0.2*bull):.0f}")
for t,p,n,b in [("TV1",18500,148.4/26.6913,19027),("TV3",13000,16.9/9.517289,16317),("TV4",13000,44.0/19.781493,12269)]:
    print(f"{t}: PE {p/(n*1e3):.1f} PB {p/b:.2f} vốn hoá {p*{'TV1':26.6913,'TV3':9.517289,'TV4':19.781493}[t]/1e3:.0f}")
for a,b,l in [(34450,26050,"YTD"),(43050,26050,"từ đỉnh 02/03"),(31950,26050,"từ 21/05"),(23650,26050,"từ đáy 27/07"),(31950,30500,"phiên 22/05"),(23700,25350,"phiên 29/07"),(26100,26800,"phiên 27/08")]:
    print(f"{l}: {(b/a-1)*100:+.1f}%")

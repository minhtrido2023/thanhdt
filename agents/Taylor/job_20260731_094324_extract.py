import re, glob, os
D="/home/trido/thanhdt/WorkingClaude/data/capit_sizing_20260731"
LEGS=[("capsz_ctrl","cash","BASELINE = spec pin R3 (size x tien mat ranh moi so)"),
 ("capsz_idle","idle","size x (cash + toan bo custom30V)"),
 ("capsz_booknav","booknav","CONG THUC LIVE (size x NAV so LAG, chi so LAG)"),
 ("capsz_nav10","nav:0.10","co dinh 10% NAV tong (bo qua conviction)"),
 ("capsz_nav20","nav:0.20","co dinh 20% NAV tong (bo qua conviction)"),
 ("capsz_idlecap30","idlecap:0.30","size x idle, tran 30% NAV so"),
 ("capsz_park25","park:0.25","size x (cash + 0,25 x park)"),
 ("capsz_park50","park:0.50","size x (cash + 0,50 x park)"),
 ("capsz_navsize25","navsize:0.25","conviction-scaled: state_size x 25% NAV"),
 ("capsz_navsize40","navsize:0.40","conviction-scaled: state_size x 40% NAV")]
def cagr(rs):
    g=1.0
    for r in rs: g*=(1+r)
    return g**(1.0/len(rs))-1
rows=[]
for tag,base,desc in LEGS:
    t=open(os.path.join(D,tag+".log")).read()
    m=re.search(r"Final NAV\s+([\d,\.]+)B\s+CAGR\s+([\-\d\.]+)%\s+Sharpe\(252\)\s+([\-\d\.]+)\s+MaxDD\s+([\-\d\.]+)%\s+Calmar\s+([\-\d\.]+)",t)
    yrs=dict((int(a),float(b)/100) for a,b in re.findall(r"^\s+(20\d\d): ([\+\-\d\.]+)%",t,re.M))
    IS=cagr([yrs[y] for y in range(2014,2020)]); OOS=cagr([yrs[y] for y in range(2020,2027)])
    rows.append((base,desc,float(m.group(2)),float(m.group(3)),float(m.group(4)),float(m.group(5)),IS*100,OOS*100))
b=rows[0]
print("| `CAPIT_SIZE_BASE` | y nghia | CAGR | Sharpe | MaxDD | Calmar | IS CAGR 14-19 | OOS CAGR 20-26 |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    mark=" **(baseline)**" if r[0]=="cash" else ""
    print(f"| `{r[0]}`{mark} | {r[1]} | {r[2]:.2f}% | {r[3]:.2f} | {r[4]:.1f}% | {r[5]:.2f} | {r[6]:.2f}% | {r[7]:.2f}% |")
print()
print("dCAGR / dCalmar / dMaxDD vs baseline cash:")
for r in rows[1:]:
    print(f"  {r[0]:16s} dCAGR {r[2]-b[2]:+.2f}pp  dCalmar {r[5]-b[5]:+.3f}  dMaxDD {r[4]-b[4]:+.2f}pp  dIS {r[6]-b[6]:+.2f}pp  dOOS {r[7]-b[7]:+.2f}pp")

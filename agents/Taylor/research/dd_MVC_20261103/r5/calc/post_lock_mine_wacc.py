"""SAU KHOA — khong doi tham so; chi doc them NPV mo moi o chi phi von hon hop. Lai vay thuc te: lai da tra 9T/26 12,255 ty (LCTT ma 04)
tren du no vay binh quan (256,81 + 461,85)/2 = 359,3 ty => 4,55%/nam (uoc luong, vay ngan han VND)."""
import sys; sys.dont_write_bytecode = True
import model_r5 as R
kd = 12.255 / 0.75 / ((256.814 + 461.848) / 2); w = 0.25 * 0.13 + 0.75 * kd * 0.8
print(f'lai vay thuc te ~{kd:.2%}/nam; chi phi von hon hop (25% Ke13 + 75% vay sau thue) ~{w:.2%}')
for k in ('co_so', 'tot', 'xau'):
    for p in ('g2031', 'real', 'flat'):
        print(f'  {k:6s} {p:5s} NPV@{w:.1%} {R.npv_total(k, p, R.BASE, w):7.0f} | @13% {R.npv_total(k, p, R.BASE, .13):7.0f}')

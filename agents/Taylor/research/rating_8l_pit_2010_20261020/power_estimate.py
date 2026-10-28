"""ƯỚC LƯỢNG sức mạnh (không phải đo): giả định SE bootstrap-quý ∝ 1/sqrt(số quý), hiệu ứng mới = IS cũ hoặc full."""
from statistics import NormalDist; import math
N = NormalDist(); z = N.inv_cdf(1 - 0.18 / 2); se = 0.75 / z
print(f"G1[2,20] IS 2014-19: delta +0.75% p=0.18 => z={z:.2f}, SE~{se:.3f}% (22 quy)")
for lab, G in [("2010Q2-2014Q2 (+17q)", 39), ("2012Q1-2014Q2 (+10q)", 32)]:
    s = se * math.sqrt(22 / G)
    for eff in (0.75, 1.06):
        zz = eff / s
        print(f"{lab} eff={eff}% SE={s:.3f}% z={zz:.2f} p={2*(1-N.cdf(zz)):.3f}")

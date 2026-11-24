"""PVP — dinh chinh theo skeptic r1 (finding 1): D3 len da sau TT99 chi ap cho nhanh 'tot' (EBITDA 550 ~ run-rate 9T/26 sau TT99);
nhanh xau/co so (300/400) neo muc 2025 da gom trich sua chua. Import calc_recheck (cung kiem md5/CONTROL). Chay nhu calc_recheck.py."""
import json, os, sys
sys.argv = sys.argv[:2]; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import calc_recheck as R   # noqa: E402  (ghi lai calc_recheck_out.json trung noi dung)
P, M1 = R.P, R.M1
def with_dry_tot(k):
    orig = P.parts
    def parts2(s, n, r, b, fx, cfg):
        d = orig(s, n, r, b, fx, cfg)
        if s == 'tot':
            x = k * R.DRY_Y * (1 - M1.TAX); d['dry_future'] = -(M1.annuity(x, n, r) - M1.annuity(x, 1, r))
        return d
    P.parts = parts2
    try:
        return R.summ(P.R3, 0.135)
    finally:
        P.parts = orig
out = {}
for k in (0.5, 1.0):
    s = with_dry_tot(k); s['d_vnd'] = s['center'] - R.base['center']; s['d_pct'] = round(100 * s['d_vnd'] / R.base['center'], 2); out[f'k{k}'] = s
json.dump(out, open(os.path.join(HERE, 'calc_d3_tot_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))

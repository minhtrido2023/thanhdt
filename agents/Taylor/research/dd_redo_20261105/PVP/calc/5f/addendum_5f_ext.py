"""PVP 5F bo sung: bien the CAP (cat chieu len NPV tau, giu chieu xuong co bang chung IRR<hurdle) + AB/CAP o sleeve 40tr. Import addendum_5f (khong sua)."""
import json, os, sys, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
with contextlib.redirect_stdout(io.StringIO()):
    import addendum_5f as A
os.chdir(A.CALC)
CAPN = {s: min(v, 0.0) for s, v in A.R.SHIP_NPV.items()}
Z = {s: 0.0 for s in A.R.SHIP_NPV}
res = dict(ship_npv_cur=A.R.SHIP_NPV, CAP_upside_cut=A.run(1.0, CAPN), A_CAP=A.run(A.K, CAPN),
           AB_sleeve40=A.run(A.K, Z, d=A.D40), A_CAP_sleeve40=A.run(A.K, CAPN, d=A.D40), d_ref=A.D_REF, d40=A.D40)
json.dump(res, open(os.path.join(HERE, 'addendum_5f_ext_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, ensure_ascii=False))

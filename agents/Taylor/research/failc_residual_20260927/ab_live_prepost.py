"""A/B BEFORE/AFTER duong LIVE tren CA HAI file (moi + backup pre-FAIL-C).

BEFORE = ban o `main` (git show main:...), AFTER = ban trong worktree. Tach dung ham
w_lag_target ra khoi ca 2 ban roi chay tren 2 file -> 4 o.
"""
import os, re, sys, json, subprocess, tempfile, textwrap, shutil
import pandas as pd

WC_MAIN = "/home/trido/thanhdt/WorkingClaude"
WT = "/home/trido/thanhdt/wt-lagedge-residual/WorkingClaude"
REL = "deploy_golive_dt5g_v4/golive_recommend_v23.py"

SHIM = textwrap.dedent('''
    import os
    import pandas as pd
    WORKDIR = os.environ["FAILC_WORKDIR"]
    EDGE_THR = 1.0
    STATE_LAG_WEIGHT = {1: 0.50, 2: 0.0, 3: 0.65, 4: 0.65, 5: 0.65}
''')


def extract(src):
    s = src.index("def w_lag_target(state, asof):")
    e = src.index("\nALLOC_BAND", s)
    return SHIM + "\n" + src[s:e]


def run(body, workdir, asof):
    script = body + textwrap.dedent(f'''

        import json, sys
        _o = []
        class C:
            def write(self, s): _o.append(s)
            def flush(self): pass
        r = sys.stdout; sys.stdout = C()
        try:
            w = w_lag_target(3, "{asof}")
            err = None
        except Exception as ex:
            w = None; err = f"{{type(ex).__name__}}: {{ex}}"
        sys.stdout = r
        print(json.dumps({{"w": w, "err": err, "log": "".join(_o)}}))
    ''')
    f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    f.write(script); f.close()
    env = dict(os.environ, FAILC_WORKDIR=workdir)
    p = subprocess.run([sys.executable, f.name], capture_output=True, text=True, env=env)
    os.unlink(f.name)
    if p.returncode != 0:
        return {"w": None, "err": p.stderr[-400:], "log": ""}
    return json.loads(p.stdout.strip().splitlines()[-1])


def stage(csv_src):
    """Dung 1 WORKDIR tam chi co data/lag_edge_health.csv = file muon thu."""
    t = tempfile.mkdtemp(prefix="failc_ab_")
    os.makedirs(os.path.join(t, "data"))
    shutil.copy(csv_src, os.path.join(t, "data", "lag_edge_health.csv"))
    return t


def main():
    before = extract(subprocess.run(["git", "-C", "/home/trido/thanhdt", "show", f"main:WorkingClaude/{REL}"],
                                    capture_output=True, text=True, check=True).stdout)
    after = extract(open(os.path.join(WT, REL), encoding="utf-8").read())
    assert 'parse_dates=["entry"]' in before, "BEFORE khong phai ban cu"
    assert "known_date" in after, "AFTER khong phai ban moi"

    files = {
        "file MOI (co known_date)": WC_MAIN + "/data/lag_edge_health.csv",
        "file BACKUP (khong co known_date)": WC_MAIN + "/data/lag_edge_health.csv.bak_20260927_prefailc",
    }
    asof = "2026-09-27"
    print(f"as-of = {asof} (phien gan nhat), state=3 NEUTRAL, EDGE_THR=1.0%\n")
    print(f"{'file':<36} {'ban':<7} {'w_LAG':<7} {'label_col':<11} {'mean12 in ra':<14} asof-label cua chuoi")
    print("-" * 118)
    for fname, path in files.items():
        wd = stage(path)
        eh = pd.read_csv(path)
        for ver, body in (("BEFORE", before), ("AFTER", after)):
            r = run(body, wd, asof)
            log = r["log"].replace("\n", " | ").strip()
            mlab = re.search(r"label_col=(\w+)", log)
            lab = mlab.group(1) if mlab else "entry (khong in)"
            mm = re.search(r"as-of \S+ = (\S+)", log)
            key = lab.split()[0]
            e = eh.copy()
            if key in e.columns:
                e[key] = pd.to_datetime(e[key])
                slab = str(e[key].max().date())
            else:
                slab = "n/a"
            print(f"{fname:<36} {ver:<7} {str(r['w']):<7} {lab:<11} {(mm.group(1) if mm else '?'):<14} {slab}")
            if r["err"]:
                print(f"{'':<36} {'':<7} ERR: {r['err']}")
            if "WARNING" in log:
                print(f"{'':<36} {'':<7} -> {log.split('|')[0].strip()}")
    print("-" * 118)


main()

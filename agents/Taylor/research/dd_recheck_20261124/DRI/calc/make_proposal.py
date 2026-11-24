"""Dựng LEDGER_PROPOSAL_<MÃ>.json từ entry cuối sổ + tham số recheck (spec.json). Không ghi sổ.
Dùng: make_proposal.py <worktree_root> <spec.json>; rồi selfcheck bản tạm."""
import json, sys, hashlib, copy, os, shutil, subprocess
root, spec = sys.argv[1], json.load(open(sys.argv[2]))
L = json.load(open(os.path.join(root, 'kb/dd_price_zones.json')))
last = [e for e in L['entries'] if e.get('ticker') == spec['ticker']][-1]
e = copy.deepcopy(last)
src = spec['source_file']; txt = open(os.path.join(root, src)).read()
for ev in spec['evidence']:
    assert ev['quote'] in txt, ev['quote'][:80]
e.update(rev=last['rev'] + 1, supersedes=f"{last['ticker']}@{last['dd_date']}#{last['rev']}", source_file=src,
         report_md5=hashlib.md5(open(os.path.join(root, src), 'rb').read()).hexdigest(), evidence=spec['evidence'])
for k in ('skeptic_final', 'skeptic_final_basis', 'skeptic_verdict_path', 'skeptic_status', 'correction_reason', 'recorded_at', 'notes', 'verdict_label'):
    if k in spec:
        e[k] = spec[k]
for k in spec.get('drop', []):
    e.pop(k, None)
out = os.path.join(root, os.path.dirname(src), f"LEDGER_PROPOSAL_{spec['ticker']}.json")
json.dump({'entry': e}, open(out, 'w'), indent=1, ensure_ascii=False)
tmp = f"/tmp/ledger_tmp_{spec['ticker']}.json"; L['entries'].append(e); json.dump(L, open(tmp, 'w'), indent=1, ensure_ascii=False)
r = subprocess.run(['python3', 'bin/dd_price_zones_selfcheck.py', '--ledger', tmp], cwd=root, env={**os.environ, 'MIKE_SRC_ROOT': root}, capture_output=True, text=True)
print(out); print('selfcheck rc', r.returncode); print((r.stdout + r.stderr)[-1500:])

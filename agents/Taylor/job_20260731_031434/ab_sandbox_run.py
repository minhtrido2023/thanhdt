# -*- coding: utf-8 -*-
"""A/B chạy THẬT golive_recommend_v23.py trong sandbox — self-check Bước 2 (Taylor_20260731_031434).

Chạy nguyên script (BQ live) nhưng CHUYỂN HƯỚNG toàn bộ 3 đường ghi canonical sang thư mục
sandbox: KHÔNG artifact production nào bị đụng (đúng kb/coding_guidelines.md §8 — chính là lớp
sự cố 07-30 mà job này đang vá, nên self-check tuyệt đối không được tái phạm nó).

Dùng:  $DNA_PYEXE ab_sandbox_run.py <before|after> <outdir>
  before = bản script ở git HEAD (chưa có §6b episode)
  after  = bản trong working tree
"""
import os, sys, io, builtins, json, shutil, subprocess

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
SCRIPT_REL = "deploy_golive_dt5g_v4/golive_recommend_v23.py"
which, outdir = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(outdir, exist_ok=True)

if which == "before":
    # repo root là /home/trido/thanhdt (WorkingClaude là thư mục con) -> phải dùng đường dẫn ./
    src = subprocess.check_output(["git", "-C", WORKDIR, "show", f"HEAD:./{SCRIPT_REL}"]).decode("utf-8")
else:
    src = open(os.path.join(WORKDIR, SCRIPT_REL), encoding="utf-8").read()

# ── chuyển hướng ghi ──
REDIRECT_SUBSTR = ("data/golive_v23_status.json", "golive_v23_recommendations_",
                   "data/capit_episode.json")


def _sandboxed(path):
    p = str(path)
    if any(s in p.replace("\\", "/") for s in REDIRECT_SUBSTR):
        return os.path.join(outdir, os.path.basename(p))
    return path


_real_open = builtins.open


def _open(file, mode="r", *a, **kw):
    if any(m in str(mode) for m in ("w", "a", "x")):
        file = _sandboxed(file)
    return _real_open(file, mode, *a, **kw)


builtins.open = _open

import pandas as pd
_real_to_csv = pd.DataFrame.to_csv


def _to_csv(self, path_or_buf=None, *a, **kw):
    if isinstance(path_or_buf, str):
        path_or_buf = _sandboxed(path_or_buf)
    return _real_to_csv(self, path_or_buf, *a, **kw)


pd.DataFrame.to_csv = _to_csv

_real_replace = os.replace


def _replace(s, d):
    return _real_replace(_sandboxed(s), _sandboxed(d))


os.replace = _replace

# capit_episode: trỏ sổ sang sandbox TRƯỚC khi script import nó (module cache dùng chung).
sys.path.insert(0, WORKDIR)
if which == "after":
    import capit_episode
    capit_episode.LEDGER_PATH = os.path.join(outdir, "capit_episode.json")
    # seed sổ bằng đúng trạng thái sổ production hiện có (nếu đã có), để so ngang.
    prod = os.path.join(WORKDIR, "data", "capit_episode.json")
    if os.path.exists(prod):
        shutil.copy(prod, capit_episode.LEDGER_PATH)

g = {"__name__": "__main__", "__file__": os.path.join(WORKDIR, SCRIPT_REL)}
exec(compile(src, SCRIPT_REL, "exec"), g)
print(f"\n[ab_sandbox_run] {which} DONE -> {outdir}")

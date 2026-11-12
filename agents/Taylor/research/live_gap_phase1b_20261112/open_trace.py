"""Chạy engine dưới audit hook ghi mọi file đã open (chỉ đọc vị trí, không đổi hành vi). Usage:
open_trace.py <trace_out> <engine.py> args..."""
import sys, os, runpy
out, eng = sys.argv[1], sys.argv[2]
seen = set()
def hook(ev, args):
    if ev == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.fsdecode(args[0])
        if p not in seen:
            seen.add(p)
            with open(out, "a") as fh: fh.write(os.path.abspath(p) + "\n")
sys.addaudithook(hook)
sys.argv = [eng] + sys.argv[3:]
runpy.run_path(eng, run_name="__main__")

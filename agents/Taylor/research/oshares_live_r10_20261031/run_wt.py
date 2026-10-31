"""Chạy 1 selfcheck với code của worktree ĐƯỢC NẠP THẬT (H3): nạp trước dcf_valuation/oshares_dcf/
trading_bot.{strategies,due_diligence} từ WT (ghim lại WT sau khi dcf_valuation chèn WORKDIR canonical),
trỏ due_diligence.DATA_DIR về data PROD (worktree không có bq_cache), in đường dẫn module lúc thoát.
Dùng: python3 run_wt.py <WT> <script.py> [args...]"""
import atexit, os, runpy, sys
wt, script, args = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, wt)
import dcf_valuation  # noqa: E402,F401
sys.path.insert(0, wt)
import oshares_dcf, trading_bot.strategies, trading_bot.due_diligence as dd  # noqa: E402,F401
dd.DATA_DIR = "/home/trido/thanhdt/WorkingClaude/data"
MODS = ("dcf_valuation", "oshares_dcf", "trading_bot.strategies", "trading_bot.due_diligence", "custom_basket")


@atexit.register
def _paths():
    bad = {m: sys.modules[m].__file__ for m in MODS if m in sys.modules
           and not os.path.abspath(sys.modules[m].__file__).startswith(wt + "/")}
    print(f"[run_wt] modules ngoài WT: {bad or 'KHÔNG'} | đã nạp: "
          f"{[m for m in MODS if m in sys.modules]}", file=sys.stderr, flush=True)


sys.argv = [script] + args
os.chdir(os.path.dirname(os.path.abspath(script)))
runpy.run_path(script, run_name="__main__")

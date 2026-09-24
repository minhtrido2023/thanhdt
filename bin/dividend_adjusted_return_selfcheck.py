#!/usr/bin/env python3
"""Vỏ mỏng cho `dividend_adjusted_return.py --selfcheck`.

Selfcheck của file đó NHÚNG trong chính nó (cờ `--selfcheck`), nên nó TÀNG HÌNH với cả hai
runner của fleet: `run_selfchecks.sh` tìm `-iname "*selfcheck*.py"`, còn
`selfcheck_weekly_baseline_check.sh` tìm `"*_selfcheck.py"`. File này tồn tại CHỈ để cái tên lọt
vào hai mẫu đó — không chứa logic kiểm thử nào của riêng nó.
"""
import os
import subprocess
import sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dividend_adjusted_return.py")
sys.exit(subprocess.run([sys.executable, TARGET, "--selfcheck"]).returncode)

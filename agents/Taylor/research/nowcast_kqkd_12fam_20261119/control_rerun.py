"""Chân đối chứng: chạy LẠI nguyên văn panel+pooled của b2_nowcast.py (commodity_cycle_te_20261026) trên cache hiện tại,
chỉ đọc kết quả (c_yoy→np_d, ALL) để so với pin 0,450. Không sửa logic; chỉ đổi thư mục ghi đầu ra."""
import sys,os,runpy
OLD='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/commodity_cycle_te_20261026'
sys.path.insert(0,OLD)
src=open(f'{OLD}/b2_nowcast.py').read()
# chỉ đổi tên file đầu ra để KHÔNG ghi đè artifact cũ
for a in ['b2_panel.csv','b2_famq.csv','b2_ic_family.csv','b2_pooled.json']:
    src=src.replace(f"'{a}'",f"'ctrl_{a}'")
exec(compile(src,'b2_nowcast_ctrl','exec'),{'__name__':'__main__'})

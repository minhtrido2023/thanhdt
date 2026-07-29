"""Histogram ROE thi truong — xuat PNG cho bao cao.
Mau: slot 1 (#2a78d6) cho du lieu, slot 2 (#eb6834) cho duong danh dau 'hien tai'.
Cap slot 1-3 da duoc validate all-pairs o references/palette.md (validator khong chay
duoc tai cho vi node v12 khong ho tro ES module/??=; dung cap da co ket qua cong bo).
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_roe/'
OUT = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/roe_market_histogram_20260729.png'
SURF, INK, INK2, INK3 = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8880'
S1, S2 = '#2a78d6', '#eb6834'

d = pd.read_csv(EXP + 'roe_daily_enriched.csv', parse_dates=['time'])
cur = d.iloc[-1]; end = cur.time
cs = pd.read_csv(EXP + 'crosssection_now.csv')

fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.9), facecolor=SURF)
plt.subplots_adjust(wspace=0.26, top=0.80, bottom=0.16, left=0.055, right=0.985)
fig.suptitle('ROE thị trường Việt Nam — phân phối lịch sử và mặt cắt hiện tại',
             x=0.055, ha='left', y=0.955, fontsize=14.5, color=INK, weight='bold')
fig.text(0.055, 0.885, 'Dữ liệu đến 2026-07-28 · ROE gộp = Σ lợi nhuận / Σ vốn chủ (rổ có PE>0 & PB>0, nguồn tav2_bq.ticker) · Taylor / job Taylor_20260729_041421',
         ha='left', fontsize=8.6, color=INK2)


def style(a):
    a.set_facecolor(SURF)
    for s in ('top', 'right'):
        a.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        a.spines[s].set_color(INK3); a.spines[s].set_linewidth(0.8)
    a.grid(axis='y', color='#e5e4df', linewidth=0.8)
    a.set_axisbelow(True)
    a.tick_params(colors=INK2, labelsize=9, length=3)


def histpanel(a, s, bins, title, sub, curval, curlab):
    n, _, patches = a.hist(s, bins=bins, color=S1, edgecolor=SURF, linewidth=1.2)
    style(a)
    a.set_title(title, fontsize=11.2, color=INK, loc='left', pad=17, weight='bold')
    a.text(0, 1.035, sub, transform=a.transAxes, fontsize=8.7, color=INK2, ha='left')
    a.axvline(curval, color=S2, linewidth=2, zorder=5)
    a.annotate(curlab, xy=(curval, a.get_ylim()[1] * 0.94), xytext=(6, 0), textcoords='offset points',
               color=S2, fontsize=9.6, weight='bold', va='top')
    a.set_ylabel('số phiên', fontsize=9, color=INK2)


b = np.arange(11.0, 20.5, 0.5)
s_all = 100 * d[d.time >= '2008-01-01'].roe_agg
histpanel(ax[0], s_all, b, 'Chuỗi thời gian: ROE gộp theo phiên, 2008+',
          'N = %d phiên · trung vị %.2f%% · hiện tại nằm ở phân vị %.0f' % (
              len(s_all), s_all.median(), 100 * (s_all < 100 * cur.roe_agg).mean()),
          100 * cur.roe_agg, 'hiện tại\n%.2f%%' % (100 * cur.roe_agg))
ax[0].set_xlabel('ROE gộp toàn thị trường (%)', fontsize=9, color=INK2)

s3 = 100 * d[d.time >= end - pd.DateOffset(years=3)].roe_agg
histpanel(ax[1], s3, b, 'Cùng thang đo, chỉ 3 năm gần nhất',
          'N = %d phiên · trung vị %.2f%% · hiện tại ở phân vị %.0f' % (
              len(s3), s3.median(), 100 * (s3 < 100 * cur.roe_agg).mean()),
          100 * cur.roe_agg, 'hiện tại\n%.2f%%' % (100 * cur.roe_agg))
ax[1].set_xlabel('ROE gộp toàn thị trường (%)', fontsize=9, color=INK2)

x = (100 * cs.roe_i).clip(-22, 42)
histpanel(ax[2], x, np.arange(-22, 44, 2), 'Mặt cắt ngang: ROE từng mã, quý gần nhất',
          'N = %d mã · trung vị %.2f%% · %.1f%% số mã lỗ' % (
              len(cs), 100 * cs.roe_i.median(), 100 * (cs.roe_i < 0).mean()),
          100 * cs.roe_i.median(), 'trung vị\ntừng mã\n%.2f%%' % (100 * cs.roe_i.median()))
ax[2].set_xlabel('ROE từng mã (%), kẹp về [−22, +42]', fontsize=9, color=INK2)
ax[2].set_ylabel('số mã', fontsize=9, color=INK2)
ax[2].axvline(100 * cur.roe_agg, color=INK3, linewidth=1.6, linestyle=(0, (4, 3)), zorder=4)
ax[2].annotate('ROE gộp %.2f%%\n(nặng vốn hoá lớn)' % (100 * cur.roe_agg),
               xy=(100 * cur.roe_agg, ax[2].get_ylim()[1] * 0.50), xytext=(7, 0), textcoords='offset points',
               color=INK2, fontsize=8.6, va='top')

fig.savefig(OUT, dpi=155, facecolor=SURF)
print('saved', OUT)

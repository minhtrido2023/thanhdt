# 4 chan pin: ten -> env (khop logs/svr_ctl_*.log cua survivorship_replay_20261020)
declare -A LEG=(
 [p30_pin0]="BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3"
 [p30_pin1M]="BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m ENGDIR=eng_dep1m"
 [p0_pin0]="BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off"
 [p0_pin1M]="BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=dep1m ENGDIR=eng_dep1m"
)
declare -A PIN=([p30_pin0]=4707bcbe [p30_pin1M]=bcd0469f [p0_pin0]=537e349b [p0_pin1M]=a6ba34d8)

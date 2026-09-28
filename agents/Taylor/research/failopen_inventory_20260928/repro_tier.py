import json,os,re
d=json.load(open('/tmp/ast_hits.json'))
TIER_A={ # tien that / duong dat lenh / NAV cong bo
 'trading_bot/executor.py','trading_bot/plan.py','trading_bot/brokers.py','trading_bot/plan_funding_gate.py',
 'trading_bot/plan_cash_commitment.py','trading_bot/due_diligence.py','trading_bot/strategies.py',
 'trading_bot/config.py','trading_bot/dnse_api.py','trading_bot/vn_market.py','trading_bot/journal.py',
 'bot_execute.py','mike/bin/daily_nav_snapshot.py','mike/bin/verify_account_snapshot.py',
 'mike/bin/compute_active_nav.py','mike/bin/discretionary_accumulation_inject.py',
 'mike/bin/discretionary_margin_gate.py','mike/bin/compute_jit_unpark.py','mike/bin/compute_park_trim.py',
 'mike/bin/merge_park_orders.py','mike/bin/reconcile_equity.py','mike/bin/nav_period_returns.py',
 'mike/bin/report_return_gate.py','mike/bin/dnse_fee_rates.py','mike/bin/dividend_adjusted_return.py',
}
TIER_B={ # so duoc PIN / dau vao model / regime
 'rating_8l.py','rating_8l_history.py','macro_state_live.py','macro_healthcheck.py','dna_report.py',
 'dna_card.py','lag_forensic_filter.py','pt_v22_dt5g.py','pt_v23_audit_2014.py','rank_8l.py',
 'rank_8l_daily_alert.py','unified_screener.py','oshares_pit.py','dcf_valuation.py','dcf_refresh_gate.py',
 'deploy_golive_dt5g_v4/publish_gated_state.py','deploy_golive_dt5g_v4/golive_recommend_v23.py',
 'update_shares_live.py','cheap_pb_floor.py','capit_episode.py','edge_health_monitor.py',
 'dc_book_waterfall_paper.py','paper_entry_adjust.py','value_radar.py','custom30v_8l.py',
 'mike/bin/corp_action_daily.py','mike/bin/snapshot_corp_action_daily.py','preflight_bq_cache.py',
 'sector_lens_monitor.py','bull_div_boost.py','telegram_recommend.py','alt_valuation_lens.py',
}
def tier(f):
    if 'selfcheck' in f or f.endswith('_test.py') or '/test' in f: return 'S'
    if f in TIER_A: return 'A'
    if f in TIER_B: return 'B'
    return 'C'
for h in d['hits']: h['tier']=tier(h['file'])
from collections import Counter
print(Counter((h['tier']) for h in d['hits']))
print(Counter((h['tier'],h['cls']) for h in d['hits']))
json.dump(d,open('/tmp/ast_hits.json','w'),indent=1)
# dump A+B with context
src={}
out=[]
for h in sorted(d['hits'],key=lambda x:(x['tier'],x['file'],x['line'])):
    if h['tier'] not in ('A','B'): continue
    p='/home/trido/thanhdt/WorkingClaude/'+h['file']
    if p not in src: src[p]=open(p,encoding='utf-8',errors='replace').read().splitlines()
    L=src[p]; i=h['line']-1
    ctx="\n".join("%5d| %s"%(n+1,L[n]) for n in range(max(0,i-9),min(len(L),i+7)))
    out.append("### [%s/%s] %s:%d  fn=%s  %s\n%s\n"%(h['tier'],h['cls'],h['file'],h['line'],h['func'],h['detail'],ctx))
open('/tmp/ab_context.txt','w').write("\n".join(out))
print("AB hits:",len(out))

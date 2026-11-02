# Lấy giá TV1 từ DNSE (read-only market data). Chạy từ WorkingClaude root.
import sys, json, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, '.')
from dnse_api import DNSEClient
c = DNSEClient.from_credentials_file()
out = {}
for f in ('secdef', 'latest_trade'):
    try: out[f] = getattr(c, f)('TV1')
    except Exception as e: out[f] = repr(e)
try: out['ohlc'] = c.ohlc('TV1', resolution='1D', **{'from': int(datetime.datetime(2026,9,1).timestamp()), 'to': int(datetime.datetime.now().timestamp())})
except Exception as e: out['ohlc'] = repr(e)
out['fetched_ICT'] = datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat()
json.dump(out, open(sys.argv[1], 'w'), default=str, ensure_ascii=False)
print(json.dumps(out, default=str, ensure_ascii=False)[:1500])

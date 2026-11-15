#!/usr/bin/env bash
# second_opinion.sh <chu-de-hoac-duong-dan-file> [--agent ID] [--model M] [--provider P] [--bg]
#
# Lay Y KIEN PHAN BIEN DOC LAP tu mot HO MODEL KHAC (mac dinh: opencode + deepseek free tier)
# ve mot ket luan/tai lieu/finding do claude tao ra.
#
# VI SAO TON TAI: gia tri that cua multi-CLI trong fleet nay khong phai throughput ma la
# BAT DONG Y KIEN. Mot ket luan ma claude va mot ho model khac cung ra thi dang tin hon han;
# cho lech nhau chinh la cho dang doc ky. Chay tren Zen free tier nen chi phi ~0.
#
# ⚠️ ADVISORY ONLY — TUYET DOI KHONG PHAI GATE.
#   Khong duoc dung ket qua script nay de CHAN hay DUYET bat cu thay doi production nao.
#   Cong kiem chung that van la `bin/verify_finding.sh` (quant-skeptic) va `arch-reviewer`,
#   ca hai co y giu tren MOT CLI da hieu chuan (xem agents/Wags/design_multi_cli_dispatch_
#   20260803.md §9.5). Model free tier chua bao gio duoc do do tin cay tren domain nay.
#
# Ket qua di len bus duoi event `finding` topic "second-opinion: <chu de>" => tra bang
# bin/trace.sh nhu moi dispatch khac, khong phai kenh rieng.
#
# Vi du:
#   bin/second_opinion.sh agents/Taylor/research/lag_quality_gate_20260803.md
#   bin/second_opinion.sh "Ket luan: nen bo gate 8L rating<=3 cho LAG" --agent Spyros
#   bin/second_opinion.sh data/results_registry.md --bg
#
# CHE DO RAW (them 2026-11-15, nghien cuu AI-momentum M2) — dung khi caller can goi model khac
# voi prompt TUY BIEN, khong khung "3 diem dang ngo", khong bus, khong job record:
#   bin/second_opinion.sh --raw-prompt-file P.md --out R.jsonl [--text-out T.txt] [--model M]
#                         [--timeout S] [--retries N] [--no-bus]
#   - Doc prompt NGUYEN VAN tu file P. KHONG post bus (--no-bus la mac dinh, chap nhan de caller
#     viet tuong minh). KHONG di qua dispatch.sh (khong job record/heartbeat).
#   - Goi `opencode run --format json` trong thu muc RONG tam thoi (khong nap CLAUDE.md/KB fleet
#     => blind that su) voi OPENCODE_PERMISSION deny bash/edit/write/webfetch/websearch/external_directory (KHONG deny read/glob/grep: da do 2026-11-15 deny chung lam opencode TREO).
#   - --out nhan luong su kien JSON tho (jsonl) cua lan thu cuoi; --text-out nhan phan text.
#   - Retry co backoff (5s,15s,45s) CHI cho loi provider/rong/timeout.
#   - Exit: 0 co text | 2 sai tham so/thieu file | 10 loi provider sau het retry | 11 chay xong
#     nhung text rong | 12 timeout. Fail-open/fail-closed la QUYET DINH CUA CALLER.
#   - Model mac dinh = default_model cua provider opencode trong kb/cli_providers.json.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------------- CHE DO RAW ----------------
_is_raw=""; for _a in "$@"; do [ "$_a" = "--raw-prompt-file" ] && _is_raw=1; done
if [ -n "$_is_raw" ]; then
  RAW_PROMPT=""; RAW_OUT=""; RAW_TEXT=""; RAW_MODEL=""; RAW_TIMEOUT=180; RAW_RETRIES=2
  while [ $# -gt 0 ]; do
    case "$1" in
      --raw-prompt-file) RAW_PROMPT="${2:?--raw-prompt-file needs a value}"; shift ;;
      --out) RAW_OUT="${2:?--out needs a value}"; shift ;;
      --text-out) RAW_TEXT="${2:?--text-out needs a value}"; shift ;;
      --model) RAW_MODEL="${2:?--model needs a value}"; shift ;;
      --timeout) RAW_TIMEOUT="${2:?--timeout needs a value}"; shift ;;
      --retries) RAW_RETRIES="${2:?--retries needs a value}"; shift ;;
      --no-bus) ;;  # raw mode KHONG BAO GIO post bus; chap nhan co cho tuong minh
      *) echo "ERROR: raw mode khong nhan '$1'" >&2; exit 2 ;;
    esac
    shift
  done
  [ -f "$RAW_PROMPT" ] || { echo "ERROR: --raw-prompt-file '$RAW_PROMPT' khong ton tai" >&2; exit 2; }
  [ -n "$RAW_OUT" ] || { echo "ERROR: raw mode can --out <file>" >&2; exit 2; }
  case "$RAW_TIMEOUT$RAW_RETRIES" in *[!0-9]*|"") echo "ERROR: --timeout/--retries phai la so nguyen" >&2; exit 2 ;; esac
  _cfg() { python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['providers']['opencode'][sys.argv[2]])" "$ROOT/kb/cli_providers.json" "$1" 2>/dev/null; }
  OC_BIN="${DISPATCH_OPENCODE_BIN:-$(_cfg bin)}"; [ -n "$OC_BIN" ] || OC_BIN="$(command -v opencode || true)"
  [ -x "$OC_BIN" ] || { echo "ERROR: khong tim thay opencode ($OC_BIN)" >&2; exit 2; }
  [ -n "$RAW_MODEL" ] || RAW_MODEL="$(_cfg default_model)"
  [ -n "$RAW_MODEL" ] || { echo "ERROR: khong xac dinh duoc model (dung --model)" >&2; exit 2; }
  _wd="$(mktemp -d "${TMPDIR:-/tmp}/so-raw.XXXXXX")" || exit 1
  trap 'rm -rf "$_wd"' EXIT
  _prompt="$(cat "$RAW_PROMPT")"
  _rc=10; _delay=5; _attempt=0
  while :; do
    _attempt=$((_attempt+1))
    ( cd "$_wd" && OPENCODE_PERMISSION='{"bash":"deny","edit":"deny","write":"deny","webfetch":"deny","websearch":"deny","external_directory":"deny"}' \
      timeout "$RAW_TIMEOUT" "$OC_BIN" run --dir "$_wd" --auto -m "$RAW_MODEL" --format json "$_prompt" ) >"$_wd/out.jsonl" 2>"$_wd/err.txt"
    _orc=$?
    _cls="$(python3 - "$_wd/out.jsonl" "$_wd/err.txt" "$_wd/text.txt" <<'PY'
import json,sys
out,err,tx=sys.argv[1:4]; texts=[]; bad=False
for l in open(out,errors="replace"):
    try: e=json.loads(l)
    except Exception: continue
    if e.get("type")=="error": bad=True
    if e.get("type")=="text": texts.append(e.get("part",{}).get("text",""))
et=open(err,errors="replace").read()
if "UnknownError" in et or "Error:" in et: bad=True
t="\n".join(texts).strip(); open(tx,"w").write(t)
print("ERR" if (bad and not t) else ("OK" if t else "EMPTY"))
PY
)"
    if [ "$_orc" -eq 124 ]; then _rc=12
    elif [ "$_cls" = "OK" ] && [ "$_orc" -eq 0 ]; then _rc=0
    elif [ "$_cls" = "EMPTY" ] && [ "$_orc" -eq 0 ]; then _rc=11
    else _rc=10; fi
    [ "$_rc" -eq 0 ] && break
    [ "$_attempt" -gt "$RAW_RETRIES" ] && break
    echo "second_opinion(raw): lan $_attempt that bai (rc=$_rc, cls=$_cls) — thu lai sau ${_delay}s" >&2
    sleep "$_delay"; _delay=$((_delay*3))
  done
  mkdir -p "$(dirname "$RAW_OUT")" && cp "$_wd/out.jsonl" "$RAW_OUT"
  if [ -n "$RAW_TEXT" ]; then mkdir -p "$(dirname "$RAW_TEXT")"; cp "$_wd/text.txt" "$RAW_TEXT"; fi
  echo "second_opinion(raw): model=$RAW_MODEL attempts=$_attempt rc=$_rc out=$RAW_OUT" >&2
  exit "$_rc"
fi
# ---------------- HET CHE DO RAW — duoi day la hanh vi CU, giu nguyen ----------------

SUBJECT="${1:-}"
[ -n "$SUBJECT" ] || { echo "usage: second_opinion.sh <chu-de|duong-dan-file> [--agent ID] [--model M] [--provider P] [--bg]" >&2; exit 2; }
shift

AGENT="Taylor"      # mac dinh: Taylor (vai tro phan bien dinh luong). Doi bang --agent.
PROVIDER="opencode" # ho model KHAC claude — do la ca diem cua script nay
MODEL=""            # rong => default_model cua provider (opencode -> deepseek free)
BG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="${2:?--agent needs a value}"; shift ;;
    --model) MODEL="${2:?--model needs a value}"; shift ;;
    --provider) PROVIDER="${2:?--provider needs a value}"; shift ;;
    --bg) BG="--bg" ;;
    *) echo "ERROR: tham so la '$1'" >&2; exit 1 ;;
  esac
  shift
done

# Neu SUBJECT la duong dan file co that => yeu cau agent DOC file do (khong nhoi noi dung vao
# prompt: file co the rat lon, va agent co tool Read/cat trong allowlist read-only).
if [ -f "$SUBJECT" ] || [ -f "$ROOT/$SUBJECT" ]; then
  _p="$SUBJECT"; [ -f "$_p" ] || _p="$ROOT/$SUBJECT"
  _abs="$(cd "$(dirname "$_p")" && pwd)/$(basename "$_p")"
  TARGET="Doc file: $_abs"
  TOPIC="$(basename "$_abs")"
else
  TARGET="Ket luan can phan bien: $SUBJECT"
  TOPIC="$(printf '%s' "$SUBJECT" | head -c 60 | tr ' /' '--')"
fi

PROMPT="Ban dang duoc goi lam Y KIEN PHAN BIEN DOC LAP (second opinion). Mot agent chay tren
mot ho model KHAC da dua ra ket luan duoi day. Viec cua ban KHONG phai dong y cho co, ma la
CO GANG TIM CHO SAI.

$TARGET

Lam dung cac buoc sau, khong lam gi khac:
1. Doc ky doi tuong tren (dung cat/head/grep — ban CHI CO QUYEN DOC, moi lenh ghi file deu bi
   chan, dung phi luot thu).
2. Neu ra TOI DA 3 diem dang ngo nhat theo thu tu nghiem trong giam dan. Voi moi diem:
   - no sai/yeu o CHO NAO (trich dan cu the, dan dong hoac cau chu that)
   - vi sao (lap luan, khong phai cam giac)
   - can bang chung gi de bac bo hoac xac nhan
3. Neu ban KHONG tim duoc diem nao dang ngo, hay noi thang la 'khong tim duoc' — dung bia ra
   van de cho du so luong. Bia loi con te hon im lang.
4. Neu ro nhung gi ban KHONG kiem duoc (thieu du lieu, thieu quyen doc, ngoai chuyen mon).

Ket thuc BAT BUOC bang dung 1 lenh nay (giu nguyen literal trace_id o cuoi):
  $ROOT/bin/append_event.sh $AGENT finding \"second-opinion: $TOPIC\" '<JSON>'

Trong do <JSON> co dang:
{\"doi_tuong\":\"...\",\"nguon\":\"$PROVIDER\",\"diem_dang_ngo\":[{\"van_de\":\"...\",\"vi_sao\":\"...\",\"can_bang_chung\":\"...\"}],\"khong_kiem_duoc\":\"...\",\"ket_luan\":\"co-van-de|khong-tim-duoc-van-de\"}

LUU Y: day la y kien THAM KHAO, khong phai cong duyet. Dung tu nhan la da 'verify' hay
'approve' bat cu thu gi."

echo "second_opinion: $AGENT via $PROVIDER${MODEL:+ ($MODEL)} — chu de: $TOPIC" >&2
_args=( "$AGENT" "$PROMPT" --provider "$PROVIDER" )
[ -n "$MODEL" ] && _args+=( --model "$MODEL" )
[ -n "$BG" ] && _args+=( --bg )
exec "$ROOT/bin/dispatch.sh" "${_args[@]}"

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
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

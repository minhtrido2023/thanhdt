#!/usr/bin/env bash
# Selfcheck cho second_opinion.sh (che do raw + hanh vi cu). Khong cham mang/bus that:
# sao chep script vao ROOT gia, dispatch.sh/append_event.sh/opencode la stub ghi lai loi goi.
# Chay: bin/second_opinion_selfcheck.sh   (TZ khong anh huong; chay duoi 3 TZ bang vong lap)
set -uo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/second_opinion.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin" "$T/kb"
cp "$SRC" "$T/bin/second_opinion.sh"
echo '{"providers":{"opencode":{"bin":"'"$T"'/fakeoc","default_model":"opencode/test-default"}}}' > "$T/kb/cli_providers.json"
for s in dispatch.sh append_event.sh; do
  printf '#!/usr/bin/env bash\necho "$0 $*" >> "%s/calls.log"\n' "$T" > "$T/bin/$s"; chmod +x "$T/bin/$s"
done
cat > "$T/fakeoc" <<'FO'
#!/usr/bin/env bash
echo "ARGS $*" >> "$(dirname "$0")/oc_calls.log"
echo "PERM $OPENCODE_PERMISSION" >> "$(dirname "$0")/oc_calls.log"
case "${FAKE_MODE:-ok}" in
  ok)    echo '{"type":"text","part":{"text":"{\"blind_driver\":\"UNKNOWN\"}"}}'; exit 0 ;;
  err)   echo '{"type":"error","error":{"name":"UnknownError"}}'; echo 'Error: UnknownError' >&2; exit 1 ;;
  empty) echo '{"type":"step_start"}'; exit 0 ;;
  slow)  sleep 5; exit 0 ;;
  flaky) n=$(cat "$(dirname "$0")/n" 2>/dev/null || echo 0); echo $((n+1)) > "$(dirname "$0")/n"
         if [ "$n" -lt 1 ]; then echo 'Error: x' >&2; exit 1; fi
         echo '{"type":"text","part":{"text":"ok2"}}'; exit 0 ;;
esac
FO
chmod +x "$T/fakeoc"
echo "PROMPT-GOC dong 1" > "$T/p.md"
FAIL=0; ok(){ echo "PASS $1"; }; bad(){ echo "FAIL $1"; FAIL=1; }
run(){ : > "$T/calls.log"; : > "$T/oc_calls.log"; rm -f "$T/n"; "$T/bin/second_opinion.sh" "$@" >"$T/stdout" 2>"$T/stderr"; echo $?; }
RAW=(--raw-prompt-file "$T/p.md" --out "$T/o/r.jsonl" --text-out "$T/o/t.txt" --retries 0)

rc=$(FAKE_MODE=ok run "${RAW[@]}")
[ "$rc" = 0 ] && ok "raw ok rc=0" || bad "raw ok rc=$rc"
[ ! -s "$T/calls.log" ] && ok "raw: KHONG goi dispatch/append_event (khong bus)" || bad "raw goi bus/dispatch: $(cat "$T/calls.log")"
grep -q "PROMPT-GOC dong 1" "$T/oc_calls.log" && ok "raw: prompt nguyen van, khong khung 3-diem" || bad "raw prompt sai"
grep -q "3 diem" "$T/oc_calls.log" && bad "raw ep khung 3-diem" || ok "raw: khong co khung 3-diem"
grep -q "test-default" "$T/oc_calls.log" && ok "raw: model mac dinh tu cli_providers.json" || bad "raw model mac dinh"
grep -q '"bash":"deny"' "$T/oc_calls.log" && ok "raw: permission deny bash" || bad "raw permission"
[ -s "$T/o/r.jsonl" ] && grep -q blind_driver "$T/o/t.txt" && ok "raw: out + text-out ghi dung" || bad "raw out"

rc=$(FAKE_MODE=err run "${RAW[@]}"); [ "$rc" = 10 ] && ok "raw provider loi rc=10" || bad "raw err rc=$rc"
[ ! -s "$T/calls.log" ] && ok "raw loi: van khong bus" || bad "raw loi goi bus"
rc=$(FAKE_MODE=empty run "${RAW[@]}"); [ "$rc" = 11 ] && ok "raw text rong rc=11" || bad "raw empty rc=$rc"
rc=$(FAKE_MODE=slow run "${RAW[@]}" --timeout 1); [ "$rc" = 12 ] && ok "raw timeout rc=12" || bad "raw timeout rc=$rc"
rc=$(FAKE_MODE=flaky run --raw-prompt-file "$T/p.md" --out "$T/o/r2.jsonl" --retries 1); [ "$rc" = 0 ] && ok "raw retry+backoff hoi phuc rc=0" || bad "raw flaky rc=$rc"
rc=$(run --raw-prompt-file "$T/khongco.md" --out "$T/o/x"); [ "$rc" = 2 ] && ok "raw thieu file rc=2" || bad "raw thieu file rc=$rc"
rc=$(run --raw-prompt-file "$T/p.md"); [ "$rc" = 2 ] && ok "raw thieu --out rc=2" || bad "raw thieu out rc=$rc"
rc=$(FAKE_MODE=ok run "${RAW[@]}" --no-bus); [ "$rc" = 0 ] && ok "raw chap nhan --no-bus" || bad "--no-bus rc=$rc"

# Hanh vi CU: van exec dispatch.sh voi khung 3-diem + topic bus trong prompt.
rc=$(run "chu de thu nghiem" --agent Spyros)
grep -q "Spyros" "$T/calls.log" && grep -q "3 diem dang ngo" "$T/calls.log" && grep -q "append_event.sh Spyros finding" "$T/calls.log" \
  && ok "che do cu: van goi dispatch.sh voi khung 3-diem + lenh bus" || bad "che do cu bi pha: $(head -c 200 "$T/calls.log")"
rc=$(run); [ "$rc" = 2 ] && ok "che do cu: thieu tham so rc=2" || bad "che do cu usage rc=$rc"
[ "$FAIL" = 0 ] && echo "SELFCHECK PASS" || { echo "SELFCHECK FAIL"; exit 1; }

# _directives.sh — sourced by session_start.sh and user_prompt_submit.sh.
# Surfaces NEW open directives from bus/directives/<id>.jsonl exactly ONCE, via a per-agent
# line-offset cache. So when Mike appends a directive, it pops up the next time the agent
# starts OR is prompted (whichever fires first), then never repeats. Both hooks share the
# same offset cache → shown once total. Requires $ROOT and $id set by caller. Safe to source
# (no exit; failures fall back to silence).
_dfile="$ROOT/bus/directives/$id.jsonl"
if [ -s "$_dfile" ]; then
  _doff="${XDG_CACHE_HOME:-$HOME/.cache}/mike_directive_off_$id"
  mkdir -p "$(dirname "$_doff")" 2>/dev/null || true
  _total="$(wc -l < "$_dfile" 2>/dev/null | tr -dc '0-9')"; _total="${_total:-0}"
  _prev="$(cat "$_doff" 2>/dev/null | tr -dc '0-9' || true)"; _prev="${_prev:-0}"
  if [ "$_total" -gt "$_prev" ]; then
    _new="$(tail -n +"$((_prev + 1))" "$_dfile" 2>/dev/null | python3 -c 'import sys, json
out = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get("status") == "open" and d.get("body"):
        out.append("• [" + d.get("directive_id", "")[:8] + "] " + d["body"])
print("\n".join(out))' 2>/dev/null || true)"
    printf '%s' "$_total" > "$_doff" 2>/dev/null || true
    if [ -n "${_new//[[:space:]]/}" ]; then
      echo "[Mike → $id] Directive MỚI cho bạn (xử lý ngay; xong thì ghi 'answer' kèm directive_id lên bus):"
      printf '%s\n' "$_new"
    fi
  fi
fi

"use strict";
const $ = (s, r) => (r || document).querySelector(s);
const STATUS_VI = {idea:"Ý tưởng", active:"Đang làm", waiting:"Đang chờ", GO:"GO", "NO-GO":"NO-GO", live:"Đang chạy", closed:"Đã đóng"};
const BLOCKS = [["need_user","Chờ anh quyết"],["overdue","Quá hạn / treo"],["recent","Mới & vừa đổi (7 ngày)"],["ideas","Ý tưởng cần nghiên cứu thêm"],["inbox","Anh đã gửi — chờ team xử lý"]];
let DATA = null, BY = {}, F = {branch:"", status:"", owner:"", priority:"", q:""};

function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === "class") e.className = attrs[k];
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), attrs[k]);
    else e.setAttribute(k, attrs[k]);
  }
  for (const c of kids.flat()) if (c != null) e.append(c.nodeType ? c : document.createTextNode(String(c)));
  return e;
}
function toast(t) { const x = $("#toast"); x.textContent = t; x.hidden = false; setTimeout(() => x.hidden = true, 2500); }
async function api(path, body) {
  const r = await fetch(path, body ? {method:"POST", headers:{"Content-Type":"application/json","X-WT":"1"}, body:JSON.stringify(body)} : {});
  if (!r.ok) { let m = r.status; try { m = (await r.json()).error || m; } catch (e) {} throw new Error(m); }
  return r.json();
}
function hhmm(iso) { if (!iso) return "—"; const d = new Date(iso); return isNaN(d) ? "—" : d.toLocaleString("vi-VN", {hour:"2-digit", minute:"2-digit", day:"2-digit", month:"2-digit"}); }
function match(it) {
  if (F.branch && !(it.branch || "").startsWith(F.branch)) return false;
  if (F.status && it.status !== F.status) return false;
  if (F.owner && it.owner !== F.owner) return false;
  if (F.priority && String(it.priority) !== F.priority) return false;
  if (F.q) { const h = [it.title, it.summary, it.id, it.owner, it.branch].join(" ").toLowerCase(); if (!h.includes(F.q)) return false; }
  return true;
}
const NO_CLOSE = id => /^(busq|paper):/.test(id || "");  // nguồn tự động: chỉ ghi chú/ưu tiên
function badge(it) {
  const st = it.verdict && it.verdict.label === "NO-GO" ? "NO-GO" : it.status;
  return el("span", {class:"badge b-" + st}, STATUS_VI[st] || st);
}
function itemNode(it) {
  const meta = ["P" + (it.priority || 3), it.owner || "—", it.due ? "hạn " + it.due : (it.updated ? "cập nhật " + String(it.updated).slice(0, 10) : "")];
  if (it.waiting_on) meta.push("chờ " + it.waiting_on.who);
  if (it.stale) meta.push("⚠ tồn đọng");
  const open = () => showPanel(it.id);
  return el("div", {class:"item" + (it.stale ? " stale" : "")},
    el("div", null, badge(it), el("span", {class:"t", onclick:open}, it.title || it.id)),
    el("div", {class:"s"}, it.summary || ""),
    el("div", {class:"m"}, meta.filter(Boolean).join(" · ")),
    el("div", {class:"acts"},
      el("button", {onclick:() => addNote(it.id)}, "Ghi chú"),
      el("button", {onclick:() => setPrio(it.id, it.priority || 3)}, "Ưu tiên"),
      NO_CLOSE(it.id) ? null : el("button", {onclick:() => closeItem(it)}, "Đóng / NO-GO")));
}
async function mutate(path, body, msg) {
  try { await api(path, body); toast(msg); await load(); if (!$("#panel").hidden && body.id) showPanel(body.id); }
  catch (e) { toast("Lỗi: " + e.message); }
}
function addNote(id) { const t = prompt("Ghi chú:"); if (t && t.trim()) mutate("/api/note", {id, text:t.trim()}, "Đã ghi chú"); }
function setPrio(id, cur) { const p = prompt("Ưu tiên (1 cao – 3 thấp):", cur); if (["1","2","3"].includes(p)) mutate("/api/priority", {id, priority:+p}, "Đã đổi ưu tiên"); }
function closeItem(it) {
  const c = prompt("Gõ 1 = Đóng · 2 = NO-GO (đừng đề xuất lại) · 3 = Mở lại (active)", "1");
  if (c === "1") mutate("/api/status", {id:it.id, status:"closed"}, "Đã đóng");
  else if (c === "2") { const why = prompt("Lý do NO-GO (ngắn):") || ""; mutate("/api/status", {id:it.id, status:"NO-GO", verdict:{label:"NO-GO", text:why}}, "Đã ghi NO-GO"); }
  else if (c === "3") mutate("/api/status", {id:it.id, status:"active"}, "Đã mở lại");
}
async function showPanel(id) {
  const p = $("#panel"); p.hidden = false; p.replaceChildren(el("p", null, "Đang tải…"));
  let it; try { it = await api("/api/item?id=" + encodeURIComponent(id)); } catch (e) { p.replaceChildren(el("p", null, "Lỗi: " + e.message)); return; }
  const kids = [el("button", {class:"close", onclick:() => p.hidden = true}, "✕ Đóng"), el("h2", null, badge(it), it.title || it.id),
    el("div", {class:"muted"}, [it.branch, it.owner, "P" + it.priority, "mở " + (it.opened || "—"), "cập nhật " + String(it.updated || "—").slice(0, 10)].join(" · "))];
  if (it.summary) kids.push(el("p", null, it.summary));
  if (it.verdict) kids.push(el("h4", null, "Kết luận: " + it.verdict.label), el("p", null, it.verdict.text || ""));
  if (it.waiting_on) kids.push(el("h4", null, "Đang chờ"), el("p", null, it.waiting_on.who + " — " + (it.waiting_on.what || "") + (it.waiting_on.since ? " (từ " + it.waiting_on.since + ")" : "")));
  if (it.detail) kids.push(el("h4", null, "Chi tiết"), el("pre", null, it.detail));
  if ((it.links || []).length) kids.push(el("h4", null, "Tài liệu"), el("ul", null, it.links.map(l => el("li", null,
    l.missing ? el("span", {class:"missing"}, l.label + " (không còn file)") : el("a", {href:"/file?p=" + encodeURIComponent(l.path), target:"_blank", rel:"noopener"}, l.label)))));
  kids.push(el("h4", null, "Ghi chú"));
  const notes = it.notes || [];
  kids.push(notes.length ? el("ul", null, notes.slice().reverse().map(n => el("li", null, hhmm(n.ts) + " · " + n.by + ": " + n.text))) : el("p", {class:"muted"}, "Chưa có."));
  const ta = el("textarea", {rows:"3", maxlength:"2000", placeholder:"Thêm ghi chú…"});
  kids.push(ta, el("div", {class:"acts"}, el("button", {onclick:() => ta.value.trim() && mutate("/api/note", {id, text:ta.value.trim()}, "Đã ghi chú")}, "Lưu ghi chú"),
    el("button", {onclick:() => setPrio(id, it.priority || 3)}, "Ưu tiên"), NO_CLOSE(it.id) ? null : el("button", {onclick:() => closeItem(it)}, "Đóng / NO-GO")));
  kids.push(el("h4", null, "Lịch sử"));
  kids.push((it.history || []).length ? el("ul", null, it.history.map(h => el("li", null, hhmm(h.ts) + " · " + h.text))) : el("p", {class:"muted"}, "Chưa có."));
  p.replaceChildren(...kids);
}
function renderAttention() {
  const at = DATA.attention || {}, box = $("#attention"); box.replaceChildren();
  for (const [k, label] of BLOCKS) {
    const items = (at[k] || []).map(id => BY[id]).filter(it => it && match(it));
    const d = el("details", {class:"att"}, el("summary", null, label + " ", el("span", {class:"cnt"}, "(" + items.length + ")")));
    d.open = true;
    if (!items.length) d.append(el("p", {class:"muted"}, "Không có."));
    items.forEach(it => d.append(itemNode(it)));
    box.append(d);
  }
}
function renderTree() {
  const root = $("#tree"); root.replaceChildren();
  const saved = JSON.parse(localStorage.getItem("wt_open") || "{}");
  const tree = {};
  for (const it of DATA.items) {
    if (!match(it)) continue;
    const parts = (it.branch || "Khác").split("/");
    let n = tree; parts.forEach((p, i) => { n = (n[p] = n[p] || {_i:[], _c:{}}); if (i < parts.length - 1) n = n._c; });
    n._i.push(it);
  }
  const walk = (obj, path) => Object.keys(obj).sort().map(name => {
    const n = obj[name], full = path ? path + "/" + name : name;
    const cnt = (function c(x) { return x._i.length + Object.values(x._c).reduce((a, y) => a + c(y), 0); })(n);
    const d = el("details", null, el("summary", null, name + " ", el("span", {class:"cnt"}, "(" + cnt + ")")));
    d.open = F.q ? true : !!saved[full];
    d.addEventListener("toggle", () => { const s = JSON.parse(localStorage.getItem("wt_open") || "{}"); if (d.open) s[full] = 1; else delete s[full]; localStorage.setItem("wt_open", JSON.stringify(s)); });
    n._i.sort((a, b) => (a.priority || 3) - (b.priority || 3)).forEach(it => d.append(itemNode(it)));
    walk(n._c, full).forEach(x => d.append(x));
    return d;
  });
  walk(tree, "").forEach(d => root.append(d));
  if (!root.children.length) root.append(el("p", {class:"muted"}, "Không có mục khớp bộ lọc."));
}
function renderNogo() {
  const box = $("#nogo"); box.replaceChildren(el("p", {class:"muted"}, "Các hướng đã NO-GO — đừng đề xuất lại."));
  DATA.items.filter(it => (it.status === "NO-GO" || (it.verdict && it.verdict.label === "NO-GO")) && match(it)).forEach(it => box.append(itemNode(it)));
}
function renderChips() {
  const c = $("#chips"); c.replaceChildren();
  const opt = (name, key, vals, lab) => { const s = el("select", {onchange:e => { F[key] = e.target.value; render(); }}, el("option", {value:""}, name), vals.map(v => el("option", {value:v}, lab ? lab(v) : v))); s.value = F[key]; return s; };
  const bl = (DATA.branches || []).map(b => typeof b === "string" ? b : b.branch).filter(Boolean);  // merged.json: object {branch,root,sub,...}
  const roots = [...new Set(bl.map(b => b.split("/")[0]))];
  const br = [...roots, ...bl].filter((v, i, a) => a.indexOf(v) === i);
  c.append(opt("Nhánh", "branch", br), opt("Trạng thái", "status", Object.keys(STATUS_VI), v => STATUS_VI[v]),
    opt("Owner", "owner", [...new Set(DATA.items.map(i => i.owner).filter(Boolean))].sort()), opt("Ưu tiên", "priority", ["1","2","3"], v => "P" + v));
  const nb = $("#n_branch"); nb.replaceChildren(...bl.map(b => el("option", {value:b}, b)));
}
function render() { renderAttention(); renderTree(); renderNogo(); }
async function load() {
  DATA = await api("/api/tree"); BY = {}; DATA.items.forEach(i => BY[i.id] = i);
  $("#updated").textContent = "cập nhật " + hhmm(DATA.generated_at);
  renderChips(); render();
}
$("#q").addEventListener("input", e => { F.q = e.target.value.trim().toLowerCase(); render(); });
document.querySelectorAll("#tabs button").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll("#tabs button").forEach(x => x.classList.toggle("on", x === b));
  $("#tree").hidden = b.dataset.tab !== "tree"; $("#nogo").hidden = b.dataset.tab !== "nogo";
}));
$("#fab").addEventListener("click", () => $("#newdlg").showModal());
$("#n_cancel").addEventListener("click", () => $("#newdlg").close());
$("#newform").addEventListener("submit", async e => {
  e.preventDefault();
  try { await api("/api/new", {branch:$("#n_branch").value || "Research", title:$("#n_title").value, summary:$("#n_summary").value}); toast("Đã gửi — chờ team xử lý"); $("#n_title").value = ""; $("#n_summary").value = ""; $("#newdlg").close(); await load(); }
  catch (er) { toast("Lỗi: " + er.message); }
});
load().catch(e => toast("Không tải được: " + e.message));

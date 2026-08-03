#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""okf.py — read/write core for tbot's OKF concept nodes.

A concept lives at kb/concepts/<slug>/: a node.yaml pointer (current_version,
status, aliases, related, tags) plus immutable per-version files v1.md, v2.md,
... (yaml frontmatter + prose body). All writes are atomic (tmp + os.replace) —
a kill mid-write must never leave a half-written concept file behind.

Only dependency beyond stdlib: pyyaml. No jsonschema dependency — schema
checks in kb_lint.py use the tiny validator here instead, to keep every
kb_tools script runnable with nothing but `python3 -m pip install pyyaml`.
"""
import glob
import json
import os
import re
from datetime import date

import yaml

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
KB_ROOT = os.path.normpath(os.path.join(LIB_DIR, "..", "..", "kb"))
CONCEPTS_DIR = os.path.join(KB_ROOT, "concepts")
INDEX_DIR = os.path.join(KB_ROOT, "_index")
SCHEMA_DIR = os.path.join(KB_ROOT, "_schema")
PROCESS_DIR = os.path.join(KB_ROOT, "process")

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
STATUSES = ("unverified", "verified", "disputed", "superseded", "rejected")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.S)


class OKFError(Exception):
    pass


def today():
    return date.today().isoformat()


def now_id():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def require_slug(slug):
    if not SLUG_RE.match(slug):
        raise OKFError(f"invalid slug {slug!r} — must match {SLUG_RE.pattern}")


def concept_dir(slug):
    return os.path.join(CONCEPTS_DIR, slug)


def concept_exists(slug):
    return os.path.isfile(os.path.join(concept_dir(slug), "node.yaml"))


def list_concepts():
    if not os.path.isdir(CONCEPTS_DIR):
        return []
    return sorted(
        d for d in os.listdir(CONCEPTS_DIR)
        if os.path.isfile(os.path.join(CONCEPTS_DIR, d, "node.yaml"))
    )


# ------------------------------------------------------------------ frontmatter

def read_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise OKFError(f"{path}: no yaml frontmatter found")
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return meta, body


def write_frontmatter(path, meta, body):
    fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    text = f"---\n{fm}\n---\n{body if body.startswith(chr(10)) else chr(10) + body}"
    _atomic_write(path, text)


# ------------------------------------------------------------------------ node

def load_node(slug):
    path = os.path.join(concept_dir(slug), "node.yaml")
    if not os.path.isfile(path):
        raise OKFError(f"no such concept: {slug}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_node(slug, node):
    path = os.path.join(concept_dir(slug), "node.yaml")
    text = yaml.safe_dump(node, allow_unicode=True, sort_keys=False)
    _atomic_write(path, text)


def version_path(slug, n):
    return os.path.join(concept_dir(slug), f"v{n}.md")


def list_versions(slug):
    d = concept_dir(slug)
    if not os.path.isdir(d):
        return []
    out = []
    for name in os.listdir(d):
        m = re.match(r"^v(\d+)\.md$", name)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def load_version(slug, n):
    return read_frontmatter(version_path(slug, n))


def load_current(slug):
    node = load_node(slug)
    meta, body = load_version(slug, node["current_version"])
    return node, meta, body


def append_changelog(slug, line):
    path = os.path.join(concept_dir(slug), "CHANGELOG.md")
    prefix = "" if not os.path.exists(path) else "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{prefix}- {today()} — {line}")


# --------------------------------------------------------------------- mutators

def new_concept(slug, title, body, tags=None, aliases=None, related=None,
                owner="tbot", status="unverified", author="tbot",
                change_reason="initial creation", sources=None):
    require_slug(slug)
    if status not in STATUSES:
        raise OKFError(f"bad status {status!r}, must be one of {STATUSES}")
    if concept_exists(slug):
        raise OKFError(f"concept already exists: {slug} (use kb_new_version.py instead)")

    write_frontmatter(version_path(slug, 1), {
        "concept": slug, "version": 1, "status": status, "supersedes": None,
        "change_reason": change_reason, "author": author, "created": today(),
        "verified_by": None, "verified_at": None, "sources": sources or [],
    }, body)

    node = {
        "concept": slug, "title": title, "current_version": 1, "status": status,
        "aliases": aliases or [], "related": related or [], "tags": tags or [],
        "owner": owner, "created": today(), "updated": today(),
    }
    save_node(slug, node)
    append_changelog(slug, f"v1 created by {author}: {change_reason}")
    return node


def new_version(slug, body, change_reason, author="tbot", status="unverified",
                sources=None):
    if status not in STATUSES:
        raise OKFError(f"bad status {status!r}, must be one of {STATUSES}")
    node = load_node(slug)
    cur = node["current_version"]

    old_meta, old_body = load_version(slug, cur)
    old_meta["status"] = "superseded"
    write_frontmatter(version_path(slug, cur), old_meta, old_body)

    new_n = cur + 1
    write_frontmatter(version_path(slug, new_n), {
        "concept": slug, "version": new_n, "status": status,
        "supersedes": f"v{cur}", "change_reason": change_reason, "author": author,
        "created": today(), "verified_by": None, "verified_at": None,
        "sources": sources or [],
    }, body)

    node["current_version"] = new_n
    node["status"] = status
    node["updated"] = today()
    save_node(slug, node)
    append_changelog(slug, f"v{new_n} supersedes v{cur}, by {author}: {change_reason}")
    return node


def set_current_status(slug, status, verified_by=None, verified_at=None):
    if status not in STATUSES:
        raise OKFError(f"bad status {status!r}, must be one of {STATUSES}")
    node = load_node(slug)
    n = node["current_version"]
    meta, body = load_version(slug, n)
    meta["status"] = status
    if verified_by is not None:
        meta["verified_by"] = verified_by
        meta["verified_at"] = verified_at or today()
    write_frontmatter(version_path(slug, n), meta, body)
    node["status"] = status
    node["updated"] = today()
    save_node(slug, node)
    return node


# ------------------------------------------------------------------- process

def _process_files(kind):
    d = os.path.join(PROCESS_DIR, kind)
    return sorted(glob.glob(os.path.join(d, "*.md")))


def open_ask_to_verify(slug, note, requested_by="tbot"):
    req_id = f"{now_id()}-{slug}"
    path = os.path.join(PROCESS_DIR, "ask_to_verify", f"{req_id}.md")
    meta = {"id": req_id, "concept": slug, "requested_by": requested_by,
            "requested_at": today(), "status": "open", "resolved_by": None,
            "resolved_at": None}
    write_frontmatter(path, meta, f"\n{note}\n")
    return req_id, path


def find_open_ask_to_verify(slug):
    out = []
    for path in _process_files("ask_to_verify"):
        meta, _ = read_frontmatter(path)
        if meta.get("concept") == slug and meta.get("status") == "open":
            out.append((path, meta))
    return out


def close_ask_to_verify(path, resolved_by, resolution_note=""):
    meta, body = read_frontmatter(path)
    meta["status"] = "resolved"
    meta["resolved_by"] = resolved_by
    meta["resolved_at"] = today()
    write_frontmatter(path, meta, body + (f"\n\nResolution: {resolution_note}\n" if resolution_note else ""))


def open_conflict_review(slug_a, slug_b, reason, opened_by="tbot"):
    review_id = f"{now_id()}-{slug_a}-vs-{slug_b}"
    path = os.path.join(PROCESS_DIR, "conflict_review", f"{review_id}.md")
    meta = {"id": review_id, "concepts": [slug_a, slug_b], "opened_by": opened_by,
            "opened_at": today(), "status": "open", "resolution": None,
            "resolved_at": None}
    write_frontmatter(path, meta, f"\n{reason}\n")
    return review_id, path


def find_conflict_review(review_id):
    path = os.path.join(PROCESS_DIR, "conflict_review", f"{review_id}.md")
    if not os.path.isfile(path):
        raise OKFError(f"no such conflict review: {review_id}")
    return path


def close_conflict_review(review_id, keep_slug, reject_slug, resolved_by, note=""):
    path = find_conflict_review(review_id)
    meta, body = read_frontmatter(path)
    meta["status"] = "closed"
    meta["resolution"] = f"kept={keep_slug} rejected={reject_slug}"
    meta["resolved_at"] = today()
    write_frontmatter(path, meta,
                       body + f"\n\nResolved by {resolved_by}: kept `{keep_slug}`, "
                              f"rejected `{reject_slug}`. {note}\n")


# ------------------------------------------------------------------- schema

def load_schema(name):
    with open(os.path.join(SCHEMA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def validate_schema(instance, schema):
    """Minimal hand-rolled validator — required/type/enum/pattern/items/additionalProperties.
    Not a full JSON Schema implementation; enough for this repo's two flat schemas."""
    errors = []
    props = schema.get("properties", {})
    for req in schema.get("required", []):
        if req not in instance:
            errors.append(f"missing required field: {req}")
    if schema.get("additionalProperties") is False:
        for k in instance:
            if k not in props:
                errors.append(f"unexpected field: {k}")
    for key, val in instance.items():
        spec = props.get(key)
        if spec is None:
            continue
        errors.extend(_check_type(key, val, spec))
    return errors


def _check_type(key, val, spec):
    errors = []
    types = spec.get("type")
    if types is not None:
        allowed = types if isinstance(types, list) else [types]
        if not any(_matches_type(val, t) for t in allowed):
            errors.append(f"{key}: expected type {allowed}, got {type(val).__name__}")
    if "enum" in spec and val not in spec["enum"]:
        errors.append(f"{key}: {val!r} not in {spec['enum']}")
    if "pattern" in spec and isinstance(val, str) and not re.match(spec["pattern"], val):
        errors.append(f"{key}: {val!r} does not match pattern {spec['pattern']}")
    if spec.get("type") == "array" and isinstance(val, list) and "items" in spec:
        item_type = spec["items"].get("type")
        for i, item in enumerate(val):
            if item_type and not _matches_type(item, item_type):
                errors.append(f"{key}[{i}]: expected {item_type}, got {type(item).__name__}")
    return errors


def _matches_type(val, t):
    if t == "null":
        return val is None
    if t == "string":
        return isinstance(val, str)
    if t == "integer":
        return isinstance(val, int) and not isinstance(val, bool)
    if t == "number":
        return isinstance(val, (int, float)) and not isinstance(val, bool)
    if t == "boolean":
        return isinstance(val, bool)
    if t == "array":
        return isinstance(val, list)
    if t == "object":
        return isinstance(val, dict)
    return True

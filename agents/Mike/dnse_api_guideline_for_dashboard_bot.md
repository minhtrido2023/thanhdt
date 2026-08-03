# DNSE OpenAPI v2 — Calling Guideline & Lessons Learned

> Written for a bot that needs to **build a dashboard** (balances / positions / orders / NAV /
> quotes) on top of DNSE's OpenAPI. Everything here comes from a live trading fleet that has
> run 2 real DNSE accounts (margin + cash-only) since 2026-07-01 — every "gotcha" below caused
> a real incident, not a hypothetical. Source repo: reference Python client `dnse_api.py`
> (~365 lines) + wrapper `trading_bot/brokers.py`'s `DNSEBroker` (~370 lines) + a handful of
> incident postmortems, all cited inline.

---

## 1. What DNSE OpenAPI v2 is, and how auth differs from other VN brokers

- Base URL: `https://openapi.dnse.com.vn`. Send an API `version` header (date-stamped API
  version string, e.g. `2026-05-07` — check DNSE's docs for the current value).
- **No username/password login.** You register once at `entradex.dnse.com.vn` → Lightspeed API
  to get an **API Key + API Secret** pair. The secret is shown **exactly once** at registration
  — store it immediately, there is no "forgot secret" recovery, only re-issue.
- Every single request (including read-only inquiry/market-data calls) is signed with
  **HMAC-SHA256 over the API Secret** — there is no bearer-token session for reads.
- Placing/modifying/canceling an **order** additionally requires a short-lived **trading-token**
  obtained via OTP (see §3). Inquiry and market-data endpoints do **not** need this token.

This is a meaningfully different mental model from brokers that use OAuth/session-cookie login
— budget time for the signing step, it is not optional and it is easy to get subtly wrong (see
§2's clock-skew note).

## 2. Request signing (HMAC) — exact recipe

```
signing_string = "(request-target): {method_lower} {path}\n"
                + "date: {RFC-1123 UTC date, e.g. 'Mon, 03 Aug 2026 07:12:34 +0000'}\n"
                + "nonce: {random hex, e.g. uuid4().hex}"

signature = base64( HMAC_SHA256(key=API_SECRET, msg=signing_string) )
```

Headers sent on every request:
```
Date: <same RFC-1123 date used above>
X-Signature: Signature keyId="<API_KEY>",algorithm="hmac-sha256",
             headers="(request-target) date",signature="<url-encoded signature>",nonce="<nonce>"
x-api-key: <API_KEY>
version: <API_VERSION>
trading-token: <only on order place/modify/cancel, once obtained>
```

**Gotchas:**
- The signing string is built from **path only — query string is excluded**. Signing the full
  URL (with `?query=...`) will produce a signature DNSE rejects; append query params to the URL
  only *after* signing.
- The `Date` header must be **within ~±1 minute** of DNSE's clock (server-side skew check) or the
  signature is rejected outright, even if the HMAC math is correct. If your host clock drifts
  (common in containers without NTP), you'll see intermittent, hard-to-reproduce 401/403s — check
  NTP sync first before debugging the signing code.
- Generate a **fresh nonce per request** — don't cache/reuse one across calls.

## 3. Trading-token (order placement only) — OTP flow, caching, and its multi-account trap

Two OTP channels, chosen when you register:
- `smart_otp` — 6-digit code from the EntradeX mobile app, **30-second** validity.
- `email_otp` — call `POST /registration/send-email-otp` first, then a code arrives by email,
  **2-minute** validity.

```
POST /registration/trading-token   body: {"otpType": "smart_otp"|"email_otp", "passcode": "123456"}
→ returns a trading-token, valid 8 hours (cache it — build in ~5min buffer before real expiry)
```

Once obtained, pass it as the `trading-token` header on every order place/modify/cancel call for
the rest of its 8h life. Inquiry/market-data calls never need it.

**Real incident (2026-07-08, ZaloPay `INVALID_OTP`):** two accounts sharing the **same DNSE
login/credentials file** (multi-sub-account under one customer) share **one OTP channel and one
trading-token**. Two processes waking up at the same cron tick (e.g. two accounts' bots both
starting at 09:05:02) both saw "no valid token," both called `send_email_otp()` within the same
second, and both polled the same Gmail inbox for the OTP with the same look-back window — a
classic TOCTOU race. Whichever process submitted the OTP first won; the second got
`HTTP 500 INVALID_OTP` ("used"). **If you're driving multiple sub-accounts under one DNSE
login: serialize the OTP-fetch-and-redeem sequence with a real lock (file lock keyed by the
credentials file), and after acquiring the lock, re-check the cached token — the other process
may have just refreshed it for you.** Don't parallelize OTP acquisition across sub-accounts of
the same login, even though you can parallelize everything else.

For a **dashboard-only bot** (no order placement) you likely never need this token at all —
just don't request it, and you sidestep this whole class of problem.

## 4. Endpoint reference (what a dashboard actually needs)

| Purpose | Endpoint | Notes |
|---|---|---|
| List sub-accounts | `GET /accounts` | Returns `{"accounts": [{"id": ...}, ...]}` |
| Cash balance | `GET /accounts/{acc}/balances` | See §5 — 3 different "cash" fields, easy to misread |
| Buying power for a specific order | `GET /accounts/{acc}/ppse?symbol=&price=&marketType=&loanPackageId=` | The ONLY authoritative "can I buy this now" answer — see §6 |
| Positions | `GET /accounts/{acc}/positions?marketType=` | `total` (held) vs `sellable`/`tradeQuantity` (settled, released T+2 afternoon) — see §7 |
| Today's order book | `GET /accounts/{acc}/orders?marketType=` | Live status/fill snapshot |
| One order's detail | `GET /accounts/{acc}/orders/{id}?marketType=` | |
| Order history (up to 1yr) | `GET /accounts/{acc}/orders/history?from=&to=&pageSize=&pageIndex=` | Dates as `YYYY-MM-DD` |
| Loan/margin packages | `GET /accounts/{acc}/loan-packages?symbol=` | Needed even for cash-only orders — see §8 |
| Security definition (ceiling/floor/ref price, lot size, tick size) | `GET /price/{symbol}/secdef?boardId=` | Static within a session — safe to cache per-symbol per-day |
| Latest matched trade | `GET /price/{symbol}/trades/latest?boardId=` | `matchPrice`, `totalVolumeTraded`, … |
| Latest top-of-book quote | `GET /price/{symbol}/quotes/latest?boardId=` | Best bid/offer |
| Close price | `GET /price/{symbol}/close?boardId=` | |
| OHLC bars | `GET /price/ohlc?symbol=&resolution=&type=` | |
| Trading calendar | `GET /market/working-dates` | |
| Instrument master list | `GET /instruments?symbol=&marketId=&indexName=&limit=&page=` | |

Order placement (not usually needed for a dashboard, included for completeness):
- `POST /accounts/orders?marketType=&orderCategory=` — body `{accountNo, symbol, side: "NB"|"NS",
  orderType, quantity, price?, loanPackageId}`. **`loanPackageId` is a required field on every
  order, even cash-only ones on a margin account** — see §8, this one has bitten production twice.
- `PUT /accounts/{acc}/orders/{id}?marketType=&orderCategory=` — modify (price/qty), LO orders in
  New/PartiallyFilled state only. See §9's HTTP 500 quirk before trusting the response.
- `DELETE /accounts/{acc}/orders/{id}?marketType=&orderCategory=` — cancel.

## 5. Response-shape quirks (parse defensively)

DNSE's JSON isn't perfectly uniform across endpoints — write field lookups that try several
name variants, don't hardcode one casing:

- **`balances` can come back as a bare object, a 1-element list, or nested one level deeper**
  under `"stock"`/`"derivative"` keys (`{"stock": {...}, "derivative": {...}}`). Unwrap
  defensively: `row = bal[0] if isinstance(bal, list) else bal`, then
  `row = row.get("stock", row) if "stock" in row else row`.
- **Field names are inconsistent in case** across responses — some snake_case, some camelCase,
  sometimes both for the same concept (`availablecash`/`availableCash`). Look up case-
  insensitively / try multiple spellings rather than assuming one.
- **Market-data endpoints return per-board arrays**, not a single object — DNSE quotes several
  "boards" per symbol (`G1` = round lot, the one you almost always want; `G4` = odd lot; `T*` =
  negotiated/thoả thuận deals). Pick the `G1` row explicitly; don't just take `rows[0]` blindly —
  board ordering isn't guaranteed and taking the wrong one silently mixes odd-lot or block-deal
  prices into your "current price."
- **`positions`**: `total`/`quantity` = total held; a separate field (`tradeQuantity`/
  `sellableQuantity`/`availableQuantity`) = actually sellable *today* — these differ whenever a
  buy from the last 2 trading days hasn't settled yet (see §7). A dashboard showing "position
  size" should show `total`; a dashboard showing "what I could sell right now" must use the
  sellable field, and the two will legitimately disagree.
- Numeric fields sometimes arrive as strings — coerce defensively (`float(x)` guarded against
  `None`/empty string), don't assume native JSON numbers.

## 6. Buying power — the single most misleading part of the API (read this before showing any "cash" number)

There are **three different "cash" fields** on a DNSE account and they answer three different
questions. Confusing them caused a real incident (a bot concluded "insufficient funds" and sat
idle all morning on a day it could have traded):

| Field | Source | What it actually means |
|---|---|---|
| `availableCash` (balances) | `GET /accounts/{acc}/balances` | **Settled cash only** — excludes proceeds from a sale made today (T+2 settlement pending). This is the field that looks most like "my cash" and is the one most likely to mislead. |
| `totalCash` (balances) | same | Includes credited-but-unsettled sale proceeds. Correct input for **NAV** (`NAV = totalCash + market value of positions − margin debt`), wrong for a same-day "can I buy" check on its own (see next row). |
| `pp0Buy` / `qmaxBuy` (ppse) | `GET /accounts/{acc}/ppse?symbol=&price=&loanPackageId=` | **The broker's own answer** to "how much of/how many shares of X can I buy right now at price P" — already factors in same-day sale proceeds (T+0 buying power) AND the margin limit of whichever `loanPackageId` you pass. This is the ONLY field that should gate a buy decision. |

**Concretely observed (2026-07-07, cash-only account):** sold shares at 09:42, and at 09:56
`availableCash` was completely unchanged from before the sale, while `pp0Buy` from `ppse` already
reflected ~11.4M VND of buying power including the just-sold proceeds — DNSE lets a cash account
re-buy with same-day sale proceeds well before T+2 settlement completes. A dashboard that shows
"available cash" using `availableCash` alone will look wrong/stale to a user who just sold
something and expects to see buying power update immediately — consider surfacing `ppse`'s
`pp0Buy` alongside it, labeled distinctly (e.g. "settled cash" vs "buying power now").

Also worth knowing for a "why did my cash suddenly drop" dashboard tooltip: when a **buy** fills
on a cash account, DNSE moves the purchase amount from `totalCash` into a `secureAmount`
(escrow) field within minutes of the fill — this is money already committed to shares you now
hold (counted in position market value), not money that vanished. Don't add `secureAmount` back
into a cash total, that double-counts against the position's market value.

## 7. Settlement mechanics (T+2) — what changes and when

- **Shares bought on day T become sellable starting the AFTERNOON session of T+2**, not from
  market open on T+2. Verified directly: shares bought Thursday were still rejected with
  `HTTP 400: Trade quantity not enough` on ~sell attempts all through the following Monday
  (T+2) morning session, and only succeeded once the afternoon session started. If your
  dashboard shows a "sellable" quantity, compute it from the position's own sellable field
  (§5) rather than assuming "T+2 has passed = sellable" — the cutover is mid-day, not midnight.
- **Cash-side settlement is looser than share-side** (see §6) — same-day sale proceeds are
  usable for buying same-morning via `ppse`, even though the shares that generated them followed
  the T+2 timeline on the way in. Don't conflate the two: cash-side T+0-ish, share-side strictly
  T+2-afternoon.
- A balance snapshot is only meaningful for NAV/cash display if its timestamp is **newer than
  the account's most recent fill of the day** — a snapshot taken between two fills can be off by
  exactly the value of the later, not-yet-reflected order. If your dashboard polls `balances` on
  a timer, cross-check its timestamp against the most recent order fill timestamp before trusting
  it for a point-in-time NAV figure; otherwise show it as "as of {balance snapshot time}," not
  "current."

## 8. `loanPackageId` — required on EVERY order, even cash-only, even on non-margin symbols

This field trips people up because it *sounds* margin-specific, but DNSE's API contract
requires it unconditionally:

- **Omitting it fails** with `HTTP 400: loanPackageId is required` — even for a plain cash order
  with no leverage intent. (Hit twice in production: once when a code path tried to "just leave
  it out" for cash-only orders, and once mid-incident-fix before the real fix landed.)
- **A account's one "default" loan-package ID isn't universally valid** — it may only be valid
  for mainboard (HOSE/HNX) symbols and get rejected (`loanPackageId is required`/invalid) for a
  different board, e.g. UPCOM. The correct pattern: call
  `GET /accounts/{acc}/loan-packages?symbol=X` first, check whether your account's usual default
  package ID appears in the valid list for that specific symbol, and if not, pick another valid
  package from that response (prefer a cash-type package, field `type == "N"`, over a margin-type
  one, `type == "M"`, if you have no leverage intent) — **never send the request with the field
  omitted**, that's the worse failure mode.
- Fail-safe direction: if you can't determine a valid package (network error, empty list), send
  the account's default anyway rather than omitting the field — a well-formed request that gets
  business-rejected is safer than one that's structurally invalid.

Not relevant to a pure read-only dashboard, but essential if the same bot will ever place orders.

## 9. Order-placement quirks (only relevant if you place/modify orders)

- **`modify_order` returns HTTP 500 `REMOTE_SERVER_ERROR` on SUCCESS.** DNSE implements "modify"
  server-side as cancel-old + place-new, and the response for that internal re-place comes back
  as an error even when the modify worked. Verified behavior: the old order transitions to
  `Canceled` and a new order (new ID, new price/qty) appears in the order book. **Don't treat this
  500 as a failure** — on this specific error code+payload, re-poll the order book a second later
  and look for the new order rather than assuming the modify failed.
- **Don't round quantities down to zero for odd lots.** A naive "round to nearest 100-share lot"
  helper silently truncates any remainder under 100 shares to zero — meaning a sell order for an
  odd-lot remainder (e.g. the last 10 shares of a position) never gets placed, and the code loops
  forever showing a misleading "waiting" status instead of erroring. Odd lots (<100 shares) are
  placed exactly like round lots via the same order endpoint (`orderCategory: "NORMAL"`,
  `marketType: "STOCK"`) — DNSE does not need special parameters for them; verified by placing
  one by hand. Don't invent broker-side restrictions before checking your own rounding logic
  first.

## 10. Idempotency — treat the broker's live order book as ground truth, not your local state

If your bot can be killed mid-run (crash, OOM, deploy, reboot) between "the order succeeded at
the broker" and "I saved that fact locally," your next run must not blindly re-place it — DNSE
has **no client-side idempotency-key mechanism** to dedupe for you.

- A process-level lock (flock) only prevents two runs from **overlapping**; it does nothing for
  one run dying mid-write after the external call already succeeded.
- The correct second line of defense: on every cycle, pull the account's **live order book**
  (`GET /accounts/{acc}/orders`, ALL of today's orders, not just ones your local state already
  knows about) and diff it against your local state. Any order with real fills/still-live status
  that your local state doesn't know about is a "ghost" — don't guess-merge it in (risk of
  mis-mapping a broker field), pause automated action on that symbol and surface it for a human
  to reconcile.
- For a **dashboard**, the practical takeaway is simpler: always render from a fresh
  `GET /accounts/{acc}/orders` / `positions` call, don't reconstruct "what should be true" from
  a local order log alone — the broker's book is the only source that can't drift from reality.

## 11. Multi-account gotchas

If the dashboard will ever show more than one DNSE sub-account:

- **Any locally-written log file keyed only by date (not by account) will silently interleave
  records from multiple accounts** the moment a second account goes live on the same day. A real
  incident: a "latest balance" reader took "the last balance record in today's shared log file,"
  which by pure timing was account B's balance, and displayed it as account A's NAV — off by a
  huge margin, and it looked completely plausible (a real, freshly-fetched number, just for the
  wrong account) so nothing caught it until a manual cross-check. **Always tag every record you
  persist with the account identifier at write time, and filter by it on every read** — never
  trust "most recent record" as a proxy for "most recent record for the account I'm asking
  about."
- **DNSE responses don't always self-identify which account they're for** (e.g. a `balances`
  response has no account field in its payload) — the account context comes from which URL you
  called, not from the response body. If you fan out balance calls for multiple accounts and log
  raw responses, tag them yourself before persisting.
- **Sub-accounts under the same login share one OTP channel / trading-token** (§3) — relevant if
  you ever add write operations, irrelevant for pure reads.

## 12. Error handling

`_request()`'s pattern (worth mirroring):
- Non-JSON response body → treat as an error with the raw HTTP status + truncated text.
- `HTTP >= 400` → raise, carrying the parsed `message`/`error` field from the body plus the raw
  payload for debugging — don't silently swallow and return an empty/default value, a 4xx/5xx
  means the number you were about to display doesn't exist.
- Network/timeout errors on inquiry endpoints (`ppse`, `secdef`, etc.) should degrade to "unknown"
  (e.g. `None`) rather than a fabricated fallback (e.g. quietly falling back to a cruder cash
  check) — a caller that can't tell "the broker said no" from "I couldn't ask" may make an unsafe
  decision.
- Set a real request timeout (don't block forever on a hung connection) and expect occasional
  transient failures — retry idempotent reads (balances, positions, quotes), but never blindly
  retry an order-placement call without first checking the order book for whether it already went
  through (see §10).

## 13. Freshness discipline — same-day numbers come from DNSE, never from a batch/warehouse copy

If this dashboard bot also has access to a data warehouse/BigQuery-style historical mirror of
price/position data: **any same-day figure (today's price, today's position, today's cash) must
come from the live DNSE API call, never from an overnight-synced copy** — a nightly sync
necessarily reflects yesterday's close. A real incident: a plan generator priced some of its
orders off a stale overnight cache and others off live DNSE data on the same run, and the
resulting inconsistency (two "current prices" for the same symbol, several percent apart) was
the tell that surfaced the bug. If you maintain both a live path and a cached/historical path,
make the split explicit and label it in the UI ("live" vs "as of {last sync}"), don't let a
dashboard silently mix them.

## 14. Quick-reference checklist for the dashboard build

- [ ] Sign every request per §2; verify host clock is NTP-synced before debugging signature
      rejections.
- [ ] Never request a trading-token unless you actually place/modify/cancel orders.
- [ ] Parse `balances` defensively (list-or-object, possible `stock`/`derivative` nesting,
      case-insensitive field lookup).
- [ ] Show `availableCash` and `pp0Buy`(via `ppse`) as **two different, separately labeled**
      numbers — never present one as if it were the other.
- [ ] Compute NAV from `totalCash` (not `availableCash`) + position market value − margin debt;
      don't add `secureAmount` back in.
- [ ] Show position "sellable" quantity from the position's own sellable field, not from a
      "T+2 has elapsed" date calculation (settlement flips mid-afternoon on T+2, not at open).
- [ ] Pick the `G1` board explicitly when reading quotes/trades for a symbol — don't take an
      arbitrary first row from a multi-board response.
- [ ] Cross-check a balance snapshot's timestamp against the day's latest order fill before
      labeling it "current" — if older than the latest fill, label it as of its own timestamp.
- [ ] If showing multiple accounts: tag every persisted record with the account identifier at
      write time; never infer "most recent = the account I want" from an unfiltered shared log.
- [ ] Always render order/position state from a fresh API call — don't reconstruct state from a
      local log as if it were guaranteed current.
- [ ] Treat any same-day figure as DNSE-live-only; never source it from an overnight batch copy,
      even if one exists and looks convenient.

---

*Compiled 2026-08-03 from `dnse_api.py`, `trading_bot/brokers.py` (`DNSEBroker`), and incident
postmortems dated 2026-07-06 through 2026-07-28 in a live multi-account VN equities trading
fleet. All specifics above were verified against real API responses and real incidents, not
inferred from documentation alone — where DNSE's own docs and observed behavior might diverge,
trust the observed behavior cited here.*

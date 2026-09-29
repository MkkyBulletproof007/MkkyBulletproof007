---
name: pricing-guard
description: Use before sending any message that quotes a price or mentions money, to check it against Mykyta Kryvyi's standing business rules and past client pricing history. Flags violations before the message goes out.
---

# Pricing Guard SOP

Run this checklist against any outgoing quote, proposal, or price mention
before it's sent. If any item fails, stop and flag it with a compliant
alternative — don't send it as-is.

## Checklist
1. **Double-discount check** — does this discount a deliverable that was
   already discounted once for this client? Not allowed.
2. **Stale-anchor check** — does this leak a low anchor rate (Sushi La
   ~€83/reel, Magic Island €50/reel, or any other high-volume per-unit price
   from `clients/`) to a client it wasn't negotiated for? Not allowed.
3. **Market-consistency check** — is this consistent with what comparable
   clients in Cyprus have been quoted? Check `clients/` and the Notion
   pipeline for similar-tier businesses. The market is small — inconsistent
   pricing gets noticed.
4. **Pre-discount check** — is this pre-discounting a new business before
   they've asked for a lower price? Not allowed.
5. **Concession-source check** — if there's a concession, does it come from
   moving to a lower tier (see `.claude/skills/proposal-builder/`), rather
   than reducing the top film price directly?
6. **Client-history check** — does `clients/[name]/profile.md` or a Notion row
   exist for this specific client? If so, does this quote match or reasonably
   build on their recorded history and status (e.g. don't re-pitch a
   "stalled" deal as if it were active)?
7. **Currency check** — is the currency correct? Most Cyprus client work is
   EUR; one-off international deals (e.g. Influur) have been USD — don't mix
   them up in the same quote.

## If a Check Fails
State clearly which rule it violates, then propose a compliant number or
phrasing instead of sending the original.

## Countering a Lowball Offer
If a client's offer is genuinely too low, see `.claude/skills/negotiation/
SKILL.md` #6 — the "generous, doesn't work for me" phrasing avoids arguing
over external criteria (market rate, competitor pricing) entirely. Use it
once, don't stack it with other negotiation tactics in the same message.

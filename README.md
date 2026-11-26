# Immune software manifesto

**TL;DR** Most software is guarded: safe until someone gets in. Immune software needs no wall: whoever gets in can check everything, and take, rewrite, corrupt or stop nothing. Bitcoin has run that way since 2009; five principles carry it to any software.

- Verify, don't trust
- Keys, not walls
- Append, never rewrite
- Impossible, not forbidden
- Many, not one

## Why now

- **Walls fail.** An attacker, an insider or a bug gets in sooner or later. Guarded software has no second answer.
- **Agents arrive.** More code and more actions come from AI agents nobody can vouch for. Trust does not scale to them; checks do.

## Five principles

| # | Principle | Guarded software | Immune software |
|---|---|---|---|
| 1 | **Verify, don't trust** | Trust us: an audit report, a compliance badge, a status page | Same inputs, same result, all of it open. Anyone re-derives the result: trust the function, not whoever ran it |
| 2 | **Keys, not walls** | Passwords, second factors and firewalls around a server that holds everything | Data sealed to its owner's key; every action signed by its author, person or agent. A break-in opens nothing |
| 3 | **Append, never rewrite** | Records edited in place; logs an administrator can clean | The record only grows, each entry chained to the one before. The past cannot change unseen; the current state is its replay |
| 4 | **Impossible, not forbidden** | Forbidden by policy, caught by review, overridden by an administrator | A few readable rules, enforced by the system itself. A bad change is rejected whole, once means once, nobody overrides |
| 5 | **Many, not one** | One operator, one administrator, one cloud | Independent copies check each other; anything powerful needs several signatures. No single machine, key, person or agent can stop it or bend it |

## Five questions

Ask them of any system, yours first.

1. Can a stranger check the result without asking anyone?
2. If every server leaked tonight, what could the thief read or do?
3. Can an administrator change the past without it showing?
4. Is the wrong thing impossible, or only forbidden?
5. Whose failure or betrayal, alone, would end it?

## Where it already works

Each principle already runs in production, in Bitcoin and in everyday data systems. The jump is to make all five the default.

| # | In Bitcoin | Elsewhere |
|---|---|---|
| 1 | Every full node replays the whole history and lands on the same state | Reproducible builds, content-addressed data, transparency logs |
| 2 | A coin locked to a key moves only with that key's signature, on a ledger anyone can read | End-to-end encryption, passkeys, signed commits |
| 3 | Each block carries the hash of the one before. A node that lost everything rebuilds from the first block | Event sourcing, git, tables with time travel |
| 4 | One invalid transaction rejects the whole block. A spent coin cannot be spent again | Database constraints, atomic transactions, idempotency keys, memory-safe languages |
| 5 | Thousands of nodes validate on their own. It needs enough honest ones, never one in particular | Quorum replication, local-first apps, open formats |

## What it costs

| Cost | Answer |
|---|---|
| A lost key has no reset | Plan recovery from the start: several keys, of which a few suffice |
| Some data must stay private, or be erased on request | Seal it to its owner's key and record only its hash. To erase, destroy the key |
| Not everything repeats: models, people, clocks | Sign what cannot be re-derived: inputs, producer, output. Then check the output by rule |
| No override means no quick fix | Change the rules by the rules: in the open, signed by several keys, forward only |

## Tools

A principle is a claim until someone tests it in the open. Each tool tests one, with something at stake.

| Tool | Tests | How |
|---|---|---|
| [Proof of security](PROOF_OF_SECURITY.md) | 2. Keys, not walls | A vendor seals the key to real bitcoin with its own product and publishes everything. The untouched balance is the proof |

Principles 1, 3, 4 and 5 have no tool yet.

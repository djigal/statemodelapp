# Payment State Machine — Documentation

## Overview

The implementation uses a **table-driven state machine** approach split across two files:

- [sm.py](sm.py) — a generic, reusable `StateMachine` engine
- [main.py](main.py) — the payment-specific configuration built on top of it

Rather than encoding transition logic in classes or conditionals, all valid transitions are registered upfront as a table. An invalid transition raises an exception automatically.

---

## `sm.py` — Generic State Machine Engine

### `InvalidTransition`

A custom exception raised when an event is triggered from a state that has no registered transition for it.

---

### `Action[C]`

A type alias for `Callable[[C], None]` — a function that accepts a context object and returns nothing. Actions are the side-effect callbacks executed when a transition fires (e.g., writing to an audit log).

---

### `StateMachine[S, E, C]`

A generic dataclass parameterised over:

| Parameter | Bound | Description |
| --- | --- | --- |
| `S` | `Enum` | State type |
| `E` | `Enum` | Event type |
| `C` | — | Context type (arbitrary user data) |

Internally it holds a single `transitions` dict:

```text
(S, E)  →  (S, Action[C])
```

i.e. given a current state and an event, look up the next state and the action to run.

#### Methods

**`add_transition(from_state, event, to_state, func)`**  
Registers one valid transition in the table.

**`next_transition(state, event) → (next_state, action)`**  
Looks up the transition. Raises `InvalidTransition` if no entry exists, with a message of the form `"can't {event.name} when {state.name}"`.

**`handle(state, event, ctx) → next_state`**  
Resolves the transition, calls `action(ctx)`, and returns the next state. The caller is responsible for storing the returned state.

---

## `main.py` — Payment State Machine

### Enums

**`PayStateEnum`** — the five possible states:

| Value | Meaning |
| --- | --- |
| `NEW` | Payment just created |
| `AUTHORIZED` | Authorization confirmed |
| `CAPTURED` | Funds captured |
| `REFUNDED` | Payment refunded (terminal) |
| `FAILED` | Payment failed (terminal) |

**`PayEventEnum`** — the four possible events:

| Value | Meaning |
| --- | --- |
| `AUTHORIZE` | Request authorization |
| `CAPTURE` | Capture authorized funds |
| `REFUND` | Refund the payment |
| `FAIL` | Mark the payment as failed |

---

### `PaymentCtx`

A plain dataclass holding the mutable data passed to every action:

| Field | Type | Description |
| --- | --- | --- |
| `payment_id` | `str` | Unique payment identifier |
| `audit` | `list[str]` | Append-only log of all transitions |

---

### Transition Table

The `pay_sm` instance is a `StateMachine[PayStateEnum, PayEventEnum, PaymentCtx]`. The registered transitions are:

| From state | Event | To state | Action (audit message) |
| --- | --- | --- | --- |
| `NEW` | `AUTHORIZE` | `AUTHORIZED` | `"{id}: authorized."` |
| `NEW` | `FAIL` | `FAILED` | `"{id}: failed."` |
| `AUTHORIZED` | `REFUND` | `REFUNDED` | `"{id}: refunded."` |
| `AUTHORIZED` | `CAPTURE` | `CAPTURED` | `"{id}: captured."` |
| `AUTHORIZED` | `FAIL` | `FAILED` | `"{id}: failed."` |
| `CAPTURED` | `REFUND` | `REFUNDED` | `"{id}: refunded."` |

Any `(state, event)` pair not in this table raises `InvalidTransition`.

---

### State Transition Diagram

```
              ┌──────────┐
        ┌────▶│  FAILED  │◀────┐
        │     └──────────┘     │
   FAIL │                 FAIL │
        │                      │
┌─────┐ AUTHORIZE  ┌────────────┐ CAPTURE ┌──────────┐
│ NEW │───────────▶│ AUTHORIZED │────────▶│ CAPTURED │
└─────┘            └────────────┘         └──────────┘
                         │                     │
                  REFUND │               REFUND│
                         ▼                     ▼
                   ┌──────────┐          ┌──────────┐
                   │ REFUNDED │◀─────────┘ REFUNDED │
                   └──────────┘          └──────────┘
```

`REFUNDED` and `FAILED` are terminal — no transitions are registered from them.

---

### `Payment`

The top-level object combining context and current state:

| Field | Type | Default |
| --- | --- | --- |
| `ctx` | `PaymentCtx` | — |
| `state` | `PayStateEnum` | `NEW` |

**`handle(event)`** — delegates to `pay_sm.handle(self.state, event, self.ctx)` and must store the returned next state back into `self.state`.

---

## Example Usage

```python
payment = Payment(ctx=PaymentCtx(payment_id="1234"))

payment.handle(PayEventEnum.AUTHORIZE)
payment.handle(PayEventEnum.CAPTURE)
payment.handle(PayEventEnum.REFUND)

print(payment.ctx.audit)
# ["1234: authorized.", "1234: captured.", "1234: refunded."]
```

Triggering an unregistered transition:

```python
payment = Payment(ctx=PaymentCtx(payment_id="1234"))
payment.handle(PayEventEnum.CAPTURE)
# raises InvalidTransition: "can't CAPTURE when NEW"
```

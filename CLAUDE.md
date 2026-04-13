# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the code

```bash
python main.py
```

The project uses a `.venv` virtual environment (Python 3.13). Activate it with:

```bash
source .venv/bin/activate
```

## Architecture

[main.py](main.py) implements the **State design pattern** for a payment lifecycle. There are two key concepts:

- **`Payment`** (context): a dataclass holding `payment_id`, an `audit` log (list of strings), and the current `state`. All behavior is delegated to the state object.
- **`PaymentState`** (protocol): defines the interface all state classes must implement — `authorize`, `refund`, `capture`, `fail`.

Concrete state classes (`New`, `Authorized`, `Captured`, `Refunded`, `Failed`) each implement valid transitions and raise exceptions for illegal ones. State transitions are performed by replacing `payment.state` with a new state instance directly inside the state method.

Valid transitions:
- `New` → `Authorized` (via `authorize`) or `Failed` (via `fail`)
- `Authorized` → `Captured` (via `capture`), `Refunded` (via `refund`), or `Failed` (via `fail`)
- `Captured` → `Refunded` (via `refund`)
- `Refunded` and `Failed` are terminal states

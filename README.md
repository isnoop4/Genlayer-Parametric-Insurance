# Parametric Flight Insurance

A GenLayer Intelligent Contract that pays out automatically when a flight is delayed — no claim form, no adjuster. Independent AI validators read a flight's real status and settle the policy on-chain.

**Live demo:** https://isnoop4.github.io/Genlayer-Parametric-Insurance/

## How it works

1. **Buy a policy** — pick a flight, a date, a premium, a payout amount, and a delay threshold (in minutes). The premium tops up the shared payout pool.
2. **Validators check the flight** — calling `check_and_settle` sends five independent AI models to read the flight's actual status from FlightAware. GenLayer's consensus mechanism resolves their answers into one agreed delay figure.
3. **Settlement is automatic** — if the delay meets or exceeds the threshold, the payout is released immediately. If not, the policy closes with no payout.

## Contract

| | |
|---|---|
| Network | GenLayer Studio (Dev) |
| Address | `0x20Ab40D75D14C5BA33aFE14D4Ec6C3Dd9869E59f` |
| Deploy tx | `0xdea2c12ae358850fdc716a61118ddd8b63ecfbfc437359fc8281fc3a11486154f` |
| Oracle source | FlightAware |
| Language | Python (GenVM) |

### Methods

| Method | Type | Description |
|---|---|---|
| `buy_policy(flight_number, flight_date, premium, payout_amount, delay_threshold_minutes)` | write | Creates a new policy. Returns `policy_id`. |
| `check_and_settle(policy_id)` | write | Triggers the oracle check and settles the policy (`PAID_OUT` or `NO_PAYOUT`). |
| `fund_pool(amount)` | write | Owner tops up the shared payout pool. |
| `get_policy(policy_id)` | read | Returns a policy's stored data. |
| `get_policy_count()` | read | Returns the number of policies created. |
| `get_pool_balance()` | read | Returns the current payout pool balance. |

## Verify it yourself

Reproduce both outcomes below directly in [GenLayer Studio](https://studio-next.genlayer.com):

1. Open the contract at `0x20Ab40D75D14C5BA33aFE14D4Ec6C3Dd9869E59f`.
2. Under **Write Methods → `fund_pool`**, send a small amount (e.g. `amount: 2`) so the pool can cover a payout.
3. Under **`buy_policy`**, create a policy using one of the examples below. Note the returned `policy_id`.
4. Under **`check_and_settle`**, pass that `policy_id` and confirm the output matches.

## Captured test results

Two real `check_and_settle` calls against the deployed contract, oracle data and all.

**No payout — flight on time**
```
flight_number: GIA406
flight_date: 2026-09-24
premium: 1
payout_amount: 1
delay_threshold_minutes: 60

Oracle read: {"status": "on_time", "delay_minutes": 0}
Output: NO_PAYOUT
Consensus: 4/5 validators
```

**Paid out — flight delayed**
```
flight_number: MXD388
flight_date: 2026-09-24
premium: 1
payout_amount: 1
delay_threshold_minutes: 60

Oracle read: {"status": "delayed", "delay_minutes": 97}
Output: PAID_OUT
Consensus: 4/5 validators (1 genuine disagreement, resolved by majority)
```

## Frontend

A single self-contained `index.html` — no build step, no dependencies beyond Google Fonts. Hosted as a static page (GitHub Pages compatible).

Run locally:
```
python -m http.server 8080
```
Then open `http://localhost:8080/`.

## Repository layout

```
index.html    # Frontend — project explainer, interactive settlement-logic demo, verification steps
README.md     # This file
```

## Notes

- The frontend's interactive demo simulates the settlement comparison (`delay_minutes` vs `delay_threshold_minutes`) client-side for illustration. Actual settlement happens on-chain via `check_and_settle`, verified through GenLayer's validator consensus as shown above.
- This is a testnet build on GenLayer Studio (Dev) — not production software.

# Parametric Flight Insurance — GenLayer

An automated, decentralized parametric flight insurance dApp powered by **GenLayer Intelligent Contracts**.

This application eliminates manual claims, adjusters, and traditional oracles. It uses multi-validator AI consensus to fetch live flight status directly from the web and settle insurance payouts on-chain automatically based on delay thresholds.

---

## 🌟 Key Features

- **No Manual Claims**: Payouts are executed programmatically via on-chain contract logic.
- **AI-Powered Oracle**: Utilizes GenLayer's `web.render` and `exec_prompt` to read real-time flight data (from FlightAware) via 5 independent LLM validators.
- **Equivalence Consensus**: Requires consensus among validator nodes (status match + delay variance tolerance $\le 15$ mins) to execute state changes.
- **Interactive Simulator**: Includes a web-based UI with departure board simulations, an interactive delay/threshold slider, and captured execution logs.

---

## 📋 Steward Review & End-to-End Checklist

This submission is structured to meet all **GenLayer Steward Checklist** requirements:

| Criteria | Status | Notes |
| :--- | :---: | :--- |
| **Website Available** | ✅ | Deployed on GitHub Pages via `/docs` directory |
| **Instructions End-to-End** | ✅ | Clear step-by-step Studio reproduction guide below |
| **Reproducible Outcomes** | ✅ | Exact test cases (`GIA406` vs `MXD388`) provided |
| **Contract Link Valid** | ✅ | Verified deployment on GenLayer Studio Next |

---

## 🚀 Smart Contract Details

- **Contract Address**: [`0x20Ab40D75D14C5BA33aFE14D4Ec6C3Dd9869E59f`](https://explorer-studio-next.genlayer.com/address/0x20Ab40D75D14C5BA33aFE14D4Ec6C3Dd9869E59f)
- **Deployment Tx Hash**: `0xdea2c12ae358850fdc716a61118ddd8b63ecfbfc437359fc8281fc3a11486154f`
- **Environment**: GenLayer Studio (Devnet)
- **Oracle Data Source**: FlightAware Live Tracking

### Contract Methods

| Method | Type | Description |
| :--- | :--- | :--- |
| `fund_pool(amount)` | Write | Owner tops up the simulated payout pool |
| `buy_policy(...)` | Write | Buyer registers a policy with flight details, premium, and threshold |
| `check_and_settle(policy_id)` | Write | Triggers AI validators to check flight status and execute settlement |
| `get_policy(policy_id)` | View | Returns full details of a specific policy |
| `get_pool_balance()` | View | Returns the current balance in the payout pool |
| `get_policy_count()` | View | Returns total number of policies issued |

---

## 🧪 Step-by-Step Verification Guide (for Stewards & Reviewers)

To test and verify the execution end-to-end without needing local environment setups, follow these steps in **GenLayer Studio**:

1. **Open the Deployed Contract**:
   Navigate to [GenLayer Studio Next](https://studio-next.genlayer.com) and load contract address:
   `0x20Ab40D75D14C5BA33aFE14D4Ec6C3Dd9869E59f`

2. **Fund the Pool** *(Write Method)*:
   - Call `fund_pool` with `amount: 2` (or more) so the contract has sufficient balance to cover payouts.

3. **Buy Policies** *(Write Method)*:
   - **Test Case 1 (On-time flight -> `NO_PAYOUT`)**:
     - `flight_number`: `GIA406`
     - `flight_date`: `2026-09-24`
     - `premium`: `1`, `payout_amount`: `1`, `delay_threshold_minutes`: `60`
     - *Note the returned `policy_id` (e.g., `0`)*.
   - **Test Case 2 (Delayed flight -> `PAID_OUT`)**:
     - `flight_number`: `MXD388`
     - `flight_date`: `2026-09-24`
     - `premium`: `1`, `payout_amount`: `1`, `delay_threshold_minutes`: `60`
     - *Note the returned `policy_id` (e.g., `1`)*.

4. **Trigger Settlement** *(Write Method)*:
   - Call `check_and_settle` with `policy_id` for `GIA406` $\rightarrow$ Returns **`NO_PAYOUT`**.
   - Call `check_and_settle` with `policy_id` for `MXD388` $\rightarrow$ Returns **`PAID_OUT`**.

---

## 💻 GitHub Pages Setup (with `/docs` folder)

Because `index.html` is located inside the `docs/` folder, setting up GitHub Pages is very straightforward:

1. Push your repository to GitHub.
2. Go to **Settings** $\rightarrow$ **Pages** in your GitHub repository.
3. Under **Build and deployment** $\rightarrow$ **Branch**:
   - Select **`main`** (or `master`).
   - Select **`/docs`** as the source folder.
4. Click **Save**. Your site will be live automatically!

---

## 📁 Repository Structure

```text
.
├── Contracts/
│   └── parametric_flight_insurance.py  # GenLayer Intelligent Contract (Python)
├── docs/
│   └── index.html                      # Self-contained Frontend UI & Interactive Simulator
└── README.md                           # Project Documentation & Verification Guide

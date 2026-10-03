# sn25-actuals

First-principles revenue actuals for Bittensor subnet 25 (UR), read directly from archive chain state rather than any third-party dashboard.

## How it works

`sn25/extract.py` (runs in GitHub Actions, which can reach the archive node) walks every epoch of netuid 25 in the window. On dTAO nothing is credited between epochs: the owner cut and validator dividends accrue in `Pending*` storage and are paid when the epoch fires. For each epoch block `E` it records the tracked coldkeys' positions at `E-1` and `E`, the owner cut drained, every hotkey's `AlphaDividendsPerSubnet` / `RootAlphaDividendsPerSubnet`, take rates, pool sizes and the alpha price. Any change in tracked balances between epochs is a flow, and is bisected to the exact block with its events saved.

`sn25/build.py` (runs anywhere, no network) rebuilds income using the chain's payout rule in `pallets/subtensor/src/coinbase/run_coinbase.rs`:

| Line | Rule |
|---|---|
| Owner cut | `PendingOwnerCut` drained at the epoch, credited to (owner hotkey, owner coldkey) |
| Validator take | `take x alpha dividends` on every hotkey a tracked coldkey owns, applied to all dividends including those on our own stake, plus take on root dividends |
| Nominator yield | pro-rata share of the hotkey's post-take dividends |

Measured income (stake after minus before) is reconciled against the modelled lines every epoch. Output is produced in two views: the **protocol view** (how the chain credits it) and the **economic view** (take on other people's stake is validator revenue; take on our own stake is our staking return routed through our validator).

## Run

- Edit `run.json` to set the window or a smoke-test cap, and `wallets.json` to add JV wallets with labels.
- Push, or trigger the `extract` workflow; it commits `data/raw/`. A daily schedule tops it up.
- `python sn25/build.py` writes `data/derived/` (epoch, daily, monthly income, validator landscape, flows).

# Why inventory buffer / stockout stress?

Phase **O** adds a **sixth** thin reference domain: stock depletion and fulfillment erosion under the same shock-schedule encoding — not peg panic, network contagion, queue backlog, resource overload, or margin ladder alone.

## Physics in one paragraph

**Stock level** and **fulfillment capacity** fall under `reserve_loss` (demand spikes) and `rumor` (logistics trust). Collapse is **stockout** or **fulfillment floor** breach — a supply-chain buffer narrative distinct from the other five domains.

## Typical CLI

```bash
python scripts/run_inventory_buffer_ga_demo.py --export-replay out.json --initial-stock 0.85
python scripts/export_replay.py --mode inventory_buffer --initial-stock 0.88 --out replay.json
python scripts/institutional_composite_demo.py --hexa --out hexa.json
```

## What we do not claim

No calibrated supply-chain data, ERP integration, or cross-world coupling inside one `step()`.

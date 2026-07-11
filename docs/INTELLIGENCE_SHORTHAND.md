# Operator Intelligence Shorthand (FDE)

Adapted from Chrysalis **Intelligence Shorthand** (IS-T5…T0): store verified **procedures and oracles**, not neural weights. Models may propose narration; **goldens / CLI / certificates dispose**. LLM output never enters `World.step`.

## Tier ladder

| Tier | FDE meaning | LLM? |
|------|-------------|------|
| **IS-T5** | Frozen golden / certificate | No |
| **IS-T4** | Deterministic CLI / script recipe | No |
| **IS-T3** | Skill capsule (verify-gated digest) | No on hit |
| **IS-T2** | Domain adapter (reserved) | — |
| **IS-T1** | Prompt pack / optional prose over frozen JSON | Yes, post-hoc only |
| **IS-T0** | General model (last resort) | Yes, never in-sim |

**Selection rule:** prefer the lowest tier that covers the task.

## CLI

```bash
fragility shorthand list
fragility shorthand resolve validate-benchmarks
fragility shorthand resolve llm-prompt-bundle
fragility shorthand export --out artifacts/operator_shorthand/fde-shorthands.v1.json
```

## Package

`fragility_engine.shorthand` — capsules registry + `resolve_task`.  
Provenance note in export JSON credits Chrysalis IS design; this is a **thin Python port of the protocol**, not a dependency on `@chrysalis/web-llm`.

## Coupled mega-institution

Fork capsules: `coupled-validate`, `coupled-regenerate`, `coupled-worth-it` — see [`forks/coupled_institution/CHARTER.md`](../forks/coupled_institution/CHARTER.md).

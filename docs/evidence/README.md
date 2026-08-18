# Evidence appendices

Verbatim excerpts from `experiments/` behind the case discussions in `docs/results/`. Nothing here
is summarised or reworded: every transcript is the stored text, and every count is recomputed from
the run files.

The **Request** column is the item number in the internal extraction request list these files were
produced against (not tracked here); the files themselves are named by content.

| File | Request | Backs | Contents |
|---|:--:|---|---|
| `prose_vs_code_cases.md` | R1 | [CODE_VS_DIRECT_CASES](../results/CODE_VS_DIRECT_CASES.md) §3 · Table S17 | 4 problems (`snp_49` `holton_56` `air_167` `air_154`) — all 6 dual-protocol configurations × 3 runs on the direct side, plus every attempt from the relevant models on the code side |
| `fabrication_full_responses.md` | R2 | [FABRICATION_RESULTS](../results/FABRICATION_RESULTS.md) · Table S8/S9 | full responses for the 10 confirmed fabricated-execution records, `air_344` re-executed, and `jacob_6.8` where the annotators disagree |
| `fabrication_traces.md` | R2 | [FABRICATION_RESULTS](../results/FABRICATION_RESULTS.md) · Table S8/S9 | the same 10 records as windowed traces: handed-over text → what the harness executed → what it graded |
| `trap_convergence_cases.md` | R3 | [TRAP_RESULTS](../results/TRAP_RESULTS.md) Table 4 · Table S12/S13 | 4 named traps + 3 replacement candidates, with same-run parent controls |
| `capability_frontier_cases.md` | R4 | [CORE_RESULTS](../results/CORE_RESULTS.md) · Table S18/S19 | 3 problems (`4.5` `2.10` `ry_7.7`) — one transcript per answer cluster, plus the complete answer distribution over all 48 measurements each |
| `prompt_sensitivity_cases.md` | R5 | [PROMPT_SENSITIVITY](../results/PROMPT_SENSITIVITY.md) · Table S20/S2 | both prompts and both system prompts verbatim, 3 paired cases with every attempt on each side, and a frontier-model control |
| `dn_6_8_code_vs_direct.md` | — | [CORE_RESULTS](../results/CORE_RESULTS.md) Finding 1 | `dn_6.8`, the one problem no configuration solves: the case analysis and all 78 stored measurements (18 code configurations × 3 runs, 8 direct × 3) |
| `air_167_signed_flux.md` | — | [CODE_VS_DIRECT_CASES](../results/CODE_VS_DIRECT_CASES.md) §3.3 | `air_167`, the signed-flux case: gpt-5.5 and Qwen-3.6-27B (both variants each) × 3 runs × both protocols, 24 measurements, each with its source path, the system prompt, every user prompt and the full response |

## Transcript format

Each record gives its source file path → record id → `num_attempts`; a `details` table (expected
vs. the value the interpreter actually returned); and the `outcome` plus full `response` of **every**
attempt. The `prompt` is folded into `<details>`: within one problem and one protocol the first
prompt is byte-identical across models and runs (template + statement), so it is shown once;
repair prompts are shown individually because each carries the execution error fed back in.

Verbatim blocks use four-tilde `~~~~` fences so that ``` and `>>>` inside model output survive
unchanged.

## Reproduction conventions

- **Frontier configurations = 16** (excluding ClimateGPT-13B/70B) unless 18 is stated explicitly.
- **A problem counts as solved** when ≥2 of its 3 runs pass (majority-of-3).
- **A variant parent is held** when ≥3 of its 5 variants are solved.
- **Trap capture must be tested against the full `shortcut_values` vector**, never the scalar
  `shortcut_value` — see [TRAP_RESULTS](../results/TRAP_RESULTS.md) Table 4.

Sampling is bounded where stated: `trap_convergence_cases.md` shows 4 transcripts per trap rather
than every faller, and notes the whole-corpus counts alongside. For any (model, run) not shown,
pull it from `experiments/` using the `Source:` path printed with each record.

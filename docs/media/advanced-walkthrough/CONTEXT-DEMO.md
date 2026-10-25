# Constructed project-resume context demonstration

**Classification:** measured token counts for authored synthetic text fixtures, plus explicitly declared accounting arithmetic. This is not an LLM, productivity, cost, quality, security or latency benchmark. No model was called.

The question is narrow: how much serialized input text does one full-history replay contain compared with a selected `.SYSTEMX` resume packet and a competent compact plain-text handoff, when the same declared current contract is retained?

## Implemented source and tokenizer

The examined implementation is `.SYSTEMX` 1.11.0-alpha.6, commit `f942daf38fc7f1661910912dbcf07faaec5ad7aa`. The script compares the relevant local runtime files with that committed source, installs only into disposable projects, and runs the existing `context --agent agent.0` command. It does not simulate a proposed feature or modify the reusable template.

Counts use **tiktoken 0.14.0, encoding `o200k_base`**, as an explicitly named text tokenizer. No mapping to the current Codex/GPT model is claimed. The encoding table's SHA256 is `446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d`. The package and table were downloaded during isolated dependency setup; the fixture run makes no model/provider calls. Source URLs and cache identity are in `results.json`.

The counted inputs are literal UTF-8 fixture files. API message envelopes, hidden/system instructions, tool definitions, output or reasoning tokens, cache behavior, retries, prices and human labor are not measured. These counts are not provider-reported billed usage.

## Three arms and two cases

**Long project case:** a deliberately constructed history has 64 archived updates and one final accepted resume contract. It is not a sampled conversation. The twelve top-level fact groups cover objective, project and task identity, status, owner, write scope, next action, acceptance conditions, data boundary, execution constraints, evidence state and acceptance authority.

- **A—full history:** the common resume request plus the complete constructed history. This deliberately replays history; it is not claimed to represent every competent workflow without SYSTEMX.
- **B—SYSTEMX:** the same request, the actual current context-command output from an installed disposable project with reviewed compact records, and a maintenance/readback input. Literal host paths are replaced with stable placeholders before counting. Records use a fixed fixture timestamp for reproducibility. Critical facts are unchanged.
- **C—ordinary compact handoff:** the same request, a manually curated plain-text note preserving the same fact groups, and the same maintenance/readback input. This control demonstrates that summarization is not unique to SYSTEMX; it uses fewer input tokens than the more structured packet in this case.

**One-step counterexample:** a trivial `7 + 5` request has four declared fact groups. Applying the same persistent-record workflow adds overhead. The direct request is the appropriate lower-context option here. This prevents a blanket claim that recordkeeping always reduces input.

The retained records were authored by the fixture generator. No automatic compression or fact selection by SYSTEMX is being tested. Context validation checks the protocol records; no research-notebook application code, provider worker, PR, deployment or application test was run.

## Setup and maintenance accounting

The per-resume values count the complete serialized input files, including the common request and, for B/C, the maintenance text. Count the whole file rather than adding component token counts: BPE tokens can cross text boundaries.

For B/C, an additional one-time setup input contains one full history read, construction instructions, and readback of the retained records or note. A assumes the history already exists. This charges the selected-context workflows for migration/readback. Authored output tokens and the human/model effort to create or verify records remain unmeasured, so even the setup-inclusive totals are not complete cost accounting.

The long case's per-resume inputs are **7475 / 1008 / 396 tokens** for A/B/C. One-time setup/readback inputs are **0 / 8547 / 7733**. Consequently, the first setup-inclusive resume is **7475 / 9555 / 8129**: SYSTEMX costs more input on first use in this constructed case. The one-step case is **98 / 805 / 195** per resume, with B requiring another 1009 setup/readback tokens.

`results.json` also retains arithmetic for fixed replay counts. Those are accounting scenarios based on frozen fixture inputs, not observed model runs, predictions of a product feature, or evidence of future savings. The film should use the current fixture token counts and adjacent setup/counterexample qualifications. Do not label these numbers “money saved,” “actual token usage” or “model speed.”

## Fact availability, negative controls and omitted detail

The checker extracts one explicitly delimited accepted-fact JSON block and compares its declared groups with the fixture's ground truth. All three long-case inputs preserve 12/12 groups; the one-step inputs preserve 4/4. This proves that those explicit values remain available to a reader/parser. It does **not** prove an LLM will attend to them, answer correctly, follow permissions, resist injection or complete the task.

Seventeen known-bad controls verify checker sensitivity: twelve remove one fact group, four supply a wrong status/scope/permission/acceptance-authority value, and one creates two ambiguous accepted blocks. Every expected failure is detected. These are checks of the limited availability/contract checker, not 17 real-model failures.

The history also contains an archival code, `COBALT-17`, which the selected packet and compact note omit. A new question about that detail requires an additional authorized read. Smaller context is a subset, not a guarantee that all history remains available without retrieval. Any extra retrieval/model/tool inputs must be counted in a real study.

## Reproduce

Use a reviewed checkout of the pinned commit, an isolated Python 3.12+ environment and the accompanying pinned requirements. The source folder is a read-only input. Run into a new output directory:

```sh
python -m pip install -r requirements.txt
python run_benchmark.py --source /path/to/pinned/dotSYSTEMX \
  --output /path/to/new-output --cache /path/to/local-tokenizer-cache
python verify_results.py --data /path/to/new-output --cache /path/to/local-tokenizer-cache
```

The first tokenizer load may retrieve the public encoding table; no API key is needed. It is cached and hash checked. Fixture text and counts are deterministic; execution timestamps and hashes of temporary command output can differ. The private virtual environment, tokenizer cache, package-install logs and temporary projects are excluded from the public pack. Checksums cover the actual publication files.

## Publication limits

This is a two-case demonstration selected by its authors, not a representative task sample or causal comparison. It measures the amount of constructed input text. No conclusion about actual billing, quality, wall time, autonomous throughput or general safety follows. The format's operational value—stable ownership, provenance, review and recoverability—would require separate workload evidence. Ordinary competent summaries can also reduce context, and a simple request may need no persistent framework at all.

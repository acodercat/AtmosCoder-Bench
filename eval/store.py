"""Incremental, resumable result store for one evaluation run.

Owns everything about persistence so the runner doesn't have to:
- **real-time write** — every added result is flushed to disk immediately, so a
  killed run loses nothing;
- **resume / checkpoint** — on construction it loads a prior file and keeps every
  COMPLETED measurement (both passes and gradable fails), exposing `done_ids` so the
  caller skips them; only records with an ``error`` (infra/never-completed) are dropped
  and thus re-run, together with benchmark ids missing from the file. This makes resume
  an unbiased continuation: a resumed run equals a single clean pass, because a fail is
  a finished measurement (re-running only the losers would bias accuracy upward);
- **atomic & thread-safe** — writes go to a temp file then `os.replace`, under a
  lock, so concurrent workers and an abrupt kill never leave a truncated JSON.

File shape (unchanged): ``{"metrics": {...}, "results": [...]}``.
"""

import os
import json
import threading
from pathlib import Path
from datetime import datetime

import tiktoken

# Uniform token accounting: every reported token count is recomputed from the STORED
# text with one tokenizer (o200k_base), NOT taken from each provider's reported usage,
# so counts are comparable across providers. Same definition as eval.analysis.token_count.
# Per-attempt provider usage stays in each ``attempts[].usage`` as raw data.
_ENC = tiktoken.get_encoding("o200k_base")


def _ntok(s) -> int:
    return len(_ENC.encode_ordinary(s)) if isinstance(s, str) and s else 0


class ExperimentStore:
    def __init__(self, path, meta: dict, resume: bool = True, replace_ids=None):
        """``replace_ids`` enables a SELECTIVE re-run: load the existing file and
        keep every prior record EXCEPT those ids (dropped so the caller re-runs and
        replaces them), preserving all other results untouched. Because ``_flush``
        always recomputes the aggregate metrics from ``self.results``, dropping a
        record automatically removes its token/count contribution and re-adding the
        fresh result restores it — the file ends up identical to a clean run of the
        final id set. ``replace_ids`` overrides the normal keep-only-passed resume."""
        self.path = Path(path)
        self.meta = dict(meta)  # static run fields: model, exp_id, mode, tolerance
        # system prompt is sent on every call; counted once per attempt (see _o200k_usage)
        self._sys_tok = _ntok(self.meta.get("system", ""))
        self._lock = threading.Lock()
        self.results = []
        replace_ids = set(replace_ids) if replace_ids is not None else None
        if not self.path.exists():
            return
        try:
            previous = json.loads(self.path.read_text()).get("results", [])
        except (json.JSONDecodeError, OSError):
            return
        if replace_ids is not None:     # selective re-run: keep all prior records but the targets
            self.results = [record for record in previous if record.get("id") not in replace_ids]
        elif resume:                    # normal resume: keep completed measurements (pass+fail),
            # re-run only errors (infra/never-completed) + benchmark ids missing from the file
            self.results = [record for record in previous if not record.get("error")]
        # NB: kept (already-written) records are left exactly as they were — only NEW
        # results added below get the uniform-tokenizer usage.

    def _o200k_usage(self, record: dict) -> dict:
        """Uniform o200k token usage for one record, summed over its attempts (the
        self-repair loop). prompt = system + user prompt per call; completion = response
        text; reasoning = stored reasoning text (0 if none echoed). Disjoint; sum = total."""
        P = C = R = 0
        for a in record.get("attempts") or []:
            P += self._sys_tok + _ntok(a.get("prompt"))
            C += _ntok(a.get("response"))
            rea = a.get("reasoning")
            if isinstance(rea, str) and rea.strip():
                R += _ntok(rea)
        return {"prompt_tokens": P, "completion_tokens": C,
                "reasoning_tokens": R, "total_tokens": P + C + R}

    @property
    def done_ids(self) -> set:
        return {record["id"] for record in self.results}

    @staticmethod
    def _total_tokens(record: dict) -> int:
        """A record's total tokens from its ``usage`` object; falls back to the flat
        ``tokens`` field for results written before the usage split."""
        usage = record.get("usage")
        if usage is not None:
            return usage.get("total_tokens", usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))
        return record.get("tokens", 0)

    def counts(self) -> dict:
        passed = sum(1 for record in self.results if record.get("passed"))
        errors = sum(1 for record in self.results if record.get("error"))
        failed = len(self.results) - passed - errors
        return {"total": len(self.results), "passed": passed, "failed": failed, "errors": errors}

    def add(self, record: dict) -> dict:
        """Append a result, flush to disk, and return the live counts. The record's
        ``usage`` is (re)computed with the uniform tokenizer from its stored attempts,
        replacing any provider-reported aggregate (provider counts remain per-attempt)."""
        with self._lock:
            record["usage"] = self._o200k_usage(record)
            self.results.append(record)
            self._flush()
            return self.counts()

    def _flush(self):
        counts = self.counts()
        denominator = counts["passed"] + counts["failed"]
        usages = [record.get("usage") or {} for record in self.results]
        metrics = {**self.meta, "timestamp": datetime.now().isoformat(), **counts,
                   "accuracy": counts["passed"] / denominator if denominator else 0,
                   "usage": {"prompt_tokens": sum(u.get("prompt_tokens", 0) for u in usages),
                             "completion_tokens": sum(u.get("completion_tokens", 0) for u in usages),
                             "total_tokens": sum(self._total_tokens(record) for record in self.results),
                             "reasoning_tokens": sum(u.get("reasoning_tokens") or 0 for u in usages)}}
        tmp_path = self.path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps({"metrics": metrics, "results": self.results},
                                       indent=2, ensure_ascii=False))
        os.replace(tmp_path, self.path)  # atomic on POSIX

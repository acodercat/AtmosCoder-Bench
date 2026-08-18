"""The three benchmark sets and where they live — the single source of truth
shared by the runner and the verifier so `--set` means the same thing in both.

Each core problem has two robustness-perturbation families:
  variants_numeric     — input values perturbed (memorization / contamination resistance)
  variants_paraphrase  — text reworded, values & answer unchanged (linguistic robustness)"""

from pathlib import Path

BENCHMARK_DIR = Path("benchmark")

SETS = {
    "core": BENCHMARK_DIR / "core.json",
    "variants_numeric": BENCHMARK_DIR / "variants_numeric.json",
    "variants_paraphrase": BENCHMARK_DIR / "variants_paraphrase.json",
}


def dataset_path(name: str) -> Path:
    return SETS[name]

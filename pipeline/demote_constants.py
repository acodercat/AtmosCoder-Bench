"""Structurally demote physical-constant parameters to named locals.

For every solver parameter classified CONSTANT in pipeline/reports/param_types.json,
remove it from the solve() signature and bind it as a local variable at the top of
the function body (after the docstring, if any). The numeric literal text is kept
verbatim, so the function computes the exact same floats: the output is required
to be BIT-IDENTICAL before/after, and sub_answers are untouched.

After this, a variant generator cannot perturb a physical constant even by
mistake — constants are no longer inputs at all.

Usage:
    uv run python -m pipeline.demote_constants            # apply to all dataset files
    uv run python -m pipeline.demote_constants --id 2.3   # one problem (debug)
"""

import json
import ast
import re
import argparse

from eval.engine import run_solver

DATASET_FILES = [
    "benchmark/base.json",
    "pipeline/reports/problems_final.json",
]


def split_top_level(s: str):
    """Split a signature's inner text on top-level commas."""
    parts, depth, cur, q = [], 0, "", None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in "\"'":
            q = ch
            cur += ch
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def transform(code: str, demote: set):
    """Return (new_code, removed{name: literal_text}). Raises on anything unexpected."""
    i = code.find("def solve(")
    if i < 0:
        raise ValueError("no def solve(")
    j = i + len("def solve(")
    depth, k = 1, j
    while depth:
        ch = code[k]
        if ch == "#":  # comment inside a multi-line signature: skip to EOL
            k = code.index("\n", k)
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        k += 1
    inner = code[j:k - 1]
    # strip inline comments, then join lines so parts are clean "name=literal"
    inner = re.sub(r"#[^\n]*", "", inner).replace("\n", " ")

    keep, removed = [], {}
    for part in split_top_level(inner):
        if "=" not in part:
            keep.append(part.strip())
            continue
        name = part.split("=", 1)[0].strip().split(":")[0].strip()
        if name in demote:
            removed[name] = part.split("=", 1)[1].strip()
        else:
            keep.append(part.strip())
    if set(removed) != demote:
        raise ValueError(f"missing params: {demote - set(removed)}")

    new_code = code[:i] + "def solve(" + ", ".join(keep) + code[k - 1:]

    # insertion point: after the docstring if present, else first body stmt
    tree = ast.parse(new_code)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "solve")
    body0 = fn.body[0]
    has_doc = (isinstance(body0, ast.Expr) and isinstance(body0.value, ast.Constant)
               and isinstance(body0.value.value, str))
    anchor = fn.body[1] if (has_doc and len(fn.body) > 1) else (None if has_doc else body0)
    lines = new_code.splitlines(keepends=True)
    if anchor is not None:
        ins_line = anchor.lineno - 1
        indent = lines[ins_line][:len(lines[ins_line]) - len(lines[ins_line].lstrip())]
    else:  # docstring-only body (won't happen for real solvers)
        ins_line = body0.end_lineno
        indent = "    "
    block = "".join(f"{indent}{n} = {v}  # physical constant (frozen, not an input)\n"
                    for n, v in removed.items())
    lines.insert(ins_line, block)
    return "".join(lines), removed


def outputs_identical(code_a: str, code_b: str) -> bool:
    ok_a, res_a, _ = run_solver(code_a)
    ok_b, res_b, _ = run_solver(code_b)
    if not (ok_a and ok_b) or list(res_a) != list(res_b):
        return False
    for ka in res_a:
        va = res_a[ka].get("value") if isinstance(res_a[ka], dict) else res_a[ka]
        vb = res_b[ka].get("value") if isinstance(res_b[ka], dict) else res_b[ka]
        if va != vb:  # bit-identical floats required
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description="demote CONSTANT params to locals")
    ap.add_argument("--types", default="pipeline/reports/param_types.json")
    ap.add_argument("--id", default=None)
    args = ap.parse_args()

    types = json.load(open(args.types))
    plan = {pid: {n for n, r in t.items() if r["type"] == "CONSTANT"}
            for pid, t in types.items()}
    plan = {pid: s for pid, s in plan.items() if s}
    if args.id:
        plan = {k: v for k, v in plan.items() if k == args.id}
    print(f"solvers to transform: {len(plan)} | params to demote: {sum(map(len, plan.values()))}")

    changed_total = 0
    for fn in DATASET_FILES:
        try:
            data = json.load(open(fn))
        except FileNotFoundError:
            continue
        changed = 0
        for p in data:
            pid = p.get("id")
            if pid not in plan or "code" not in p:
                continue
            # idempotent: only demote params still present in this file's signature
            fn_node = next(n for n in ast.walk(ast.parse(p["code"]))
                           if isinstance(n, ast.FunctionDef) and n.name == "solve")
            todo = set(plan[pid]) & {a.arg for a in fn_node.args.args}
            if not todo:
                continue
            new_code, removed = transform(p["code"], todo)
            if not outputs_identical(p["code"], new_code):
                raise SystemExit(f"ABORT: output changed for {pid} in {fn}")
            # demoted names must be gone from the new signature
            defs = next(n for n in ast.walk(ast.parse(new_code))
                        if isinstance(n, ast.FunctionDef) and n.name == "solve")
            sig = {a.arg for a in defs.args.args}
            assert not (sig & set(removed)), (pid, sig & set(removed))
            p["code"] = new_code
            changed += 1
        json.dump(data, open(fn, "w"), indent=2, ensure_ascii=False)
        print(f"  {fn}: transformed {changed} solvers (outputs bit-identical)")
        changed_total += changed
    print(f"done: {changed_total} transformations across files")


if __name__ == "__main__":
    main()

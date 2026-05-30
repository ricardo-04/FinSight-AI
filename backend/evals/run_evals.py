"""
Lightweight eval harness for FinSight AI.

Two suites:

1. **Extraction** (`golden_set.json`) — runs the extraction agent against known
   documents and checks the structured fields it returns. Requires NVIDIA_API_KEY
   because it calls the LLM.

2. **Retrieval ranking** (`retrieval_golden.json`) — exercises the *real* hybrid
   reranking logic (`_tokenize`, `_keyword_score`, `_fuse` from
   ``app.rag.retrieval``) on labeled chunks with synthetic vector scores, then
   reports Recall@1, Recall@3 and MRR. Fully deterministic, no network needed —
   ideal for CI to catch ranking regressions.

3. **Groundedness** (`groundedness_golden.json`) — a deterministic faithfulness
   check: it verifies that the numeric claims in an answer are supported by the
   retrieved context, catching hallucinated figures. No LLM/network needed.

Usage (from the backend/ directory, with the venv active):

    python -m evals.run_evals                 # all deterministic + extraction
    python -m evals.run_evals --retrieval     # ranking only (no LLM / API key)
    python -m evals.run_evals --groundedness  # faithfulness only (no LLM)
    python -m evals.run_evals --extraction    # extraction only

Exit code is non-zero if any case fails, so it can gate CI.
"""
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Retrieval helpers are pure functions with no network/DB dependency.
from app.rag.retrieval import _fuse, _keyword_score, _tokenize  # noqa: E402

_GOLDEN_SET = Path(__file__).parent / "golden_set.json"
_RETRIEVAL_SET = Path(__file__).parent / "retrieval_golden.json"
_GROUNDEDNESS_SET = Path(__file__).parent / "groundedness_golden.json"


# --------------------------------------------------------------------------- #
# Retrieval ranking suite (deterministic, no LLM)                             #
# --------------------------------------------------------------------------- #
def _rank_chunks(query: str, chunks: list[dict]) -> list[dict]:
    """Rerank *chunks* with the production hybrid fusion logic.

    Each chunk carries a synthetic ``vector_score`` (as the DB would supply);
    we add the lexical keyword score and fuse exactly as retrieval.py does.
    """
    query_terms = _tokenize(query)
    scored = [
        {
            **chunk,
            "fused": _fuse(
                float(chunk["vector_score"]),
                _keyword_score(query_terms, chunk["text"]),
            ),
        }
        for chunk in chunks
    ]
    scored.sort(key=lambda c: c["fused"], reverse=True)
    return scored


def _first_relevant_rank(ranked: list[dict]) -> int | None:
    """Return the 1-based rank of the first relevant chunk, or None."""
    for i, chunk in enumerate(ranked, start=1):
        if chunk.get("relevant"):
            return i
    return None


def run_retrieval_evals() -> bool:
    cases = json.loads(_RETRIEVAL_SET.read_text(encoding="utf-8"))
    recall_at_1 = 0
    recall_at_3 = 0
    reciprocal_ranks: list[float] = []
    all_passed = True

    for case in cases:
        ranked = _rank_chunks(case["query"], case["chunks"])
        rank = _first_relevant_rank(ranked)

        hit1 = rank == 1
        hit3 = rank is not None and rank <= 3
        rr = (1.0 / rank) if rank else 0.0

        recall_at_1 += int(hit1)
        recall_at_3 += int(hit3)
        reciprocal_ranks.append(rr)

        status = "PASS" if hit1 else "FAIL"
        if not hit1:
            all_passed = False
        print(f"{status}  {case['id']:<22} relevant@rank={rank} RR={rr:.3f}")

    n = len(cases)
    print(
        f"\nRetrieval — Recall@1={recall_at_1}/{n} "
        f"Recall@3={recall_at_3}/{n} "
        f"MRR={sum(reciprocal_ranks) / n:.3f}"
    )
    return all_passed


# --------------------------------------------------------------------------- #
# Groundedness / faithfulness suite (deterministic, no LLM)                   #
# --------------------------------------------------------------------------- #
# Match standalone figures only: a digit run NOT immediately preceded by a
# letter, so quarter/fiscal notation like "Q3" or "FY24" is not mistaken for a
# material numeric claim, while monetary figures like "$92.5" still count.
_NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")


def _numeric_tokens(text: str) -> list[str]:
    """Extract numeric tokens (figures) from *text*, ignoring thousands commas."""
    return _NUMBER_RE.findall(text.replace(",", ""))


def _groundedness_score(answer: str, context: str) -> float:
    """Fraction of numeric claims in *answer* that also appear in *context*.

    A score of 1.0 means every figure the answer states is backed by the source
    context (or the answer makes no numeric claims). A hallucinated figure that
    is absent from the context drags the score below 1.0.
    """
    answer_numbers = _numeric_tokens(answer)
    if not answer_numbers:
        return 1.0  # no numeric claims to verify
    context_numbers = set(_numeric_tokens(context))
    supported = sum(1 for n in answer_numbers if n in context_numbers)
    return supported / len(answer_numbers)


def run_groundedness_evals(threshold: float = 0.999) -> bool:
    cases = json.loads(_GROUNDEDNESS_SET.read_text(encoding="utf-8"))
    all_passed = True

    for case in cases:
        context = "\n".join(case["context"])
        score = _groundedness_score(case["answer"], context)
        is_grounded = score >= threshold
        expected = bool(case["expected"]["grounded"])
        ok = is_grounded == expected
        if not ok:
            all_passed = False
        status = "PASS" if ok else "FAIL"
        print(
            f"{status}  {case['id']:<22} score={score:.2f} "
            f"grounded={is_grounded} expected={expected}"
        )

    print(f"\nGroundedness — {'ALL PASSED' if all_passed else 'FAILURES'}")
    return all_passed


# --------------------------------------------------------------------------- #
# Extraction suite (calls the LLM)                                            #
# --------------------------------------------------------------------------- #
def _check_extraction(metrics, expected: dict) -> list[str]:
    """Return a list of failure messages (empty == pass)."""
    failures: list[str] = []

    if expected.get("company_nonempty") and not metrics.company.strip():
        failures.append("company expected to be non-empty")

    for token in expected.get("revenue_contains", []):
        if token.lower() not in metrics.revenue.lower():
            failures.append(f"revenue '{metrics.revenue}' missing token '{token}'")

    if expected.get("growth_nonempty") and not metrics.growth.strip():
        failures.append("growth expected to be non-empty")

    if expected.get("guidance_nonempty") and not metrics.guidance.strip():
        failures.append("guidance expected to be non-empty")

    risks_min = expected.get("risks_min")
    if risks_min is not None and len(metrics.risks) < risks_min:
        failures.append(f"expected >= {risks_min} risks, got {len(metrics.risks)}")

    return failures


async def run_extraction_evals() -> bool:
    from app.agents.extraction_agent import run_extraction

    cases = json.loads(_GOLDEN_SET.read_text(encoding="utf-8"))
    passed = 0

    for case in cases:
        metrics = await run_extraction(case["text"])
        failures = _check_extraction(metrics, case["expected"])
        if failures:
            print(f"FAIL  {case['id']}")
            for f in failures:
                print(f"        - {f}")
        else:
            passed += 1
            print(f"PASS  {case['id']}")

    print(f"\nExtraction — {passed}/{len(cases)} cases passed")
    return passed == len(cases)


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="Run FinSight eval suites.")
    parser.add_argument("--retrieval", action="store_true", help="retrieval suite only")
    parser.add_argument("--groundedness", action="store_true", help="groundedness suite only")
    parser.add_argument("--extraction", action="store_true", help="extraction suite only")
    args = parser.parse_args()

    run_both = not (args.retrieval or args.groundedness or args.extraction)
    ok = True

    if args.retrieval or run_both:
        print("=== Retrieval ranking suite ===")
        ok = run_retrieval_evals() and ok

    if args.groundedness or run_both:
        print("\n=== Groundedness suite ===")
        ok = run_groundedness_evals() and ok

    if args.extraction or run_both:
        print("\n=== Extraction suite ===")
        ok = asyncio.run(run_extraction_evals()) and ok

    print("\nRESULT:", "ALL PASSED" if ok else "FAILURES DETECTED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


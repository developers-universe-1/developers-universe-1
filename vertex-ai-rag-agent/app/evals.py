"""Eval harness: run a JSONL of Q&A pairs through the RAG pipeline and score it.

Checks, per question:
  1. Faithfulness  — Gemini-as-judge: is the answer fully supported by the
                     retrieved chunks (i.e., not hallucinated)?
  2. Citation correctness — every [n] cited is within range, and at least one
                     citation is present when sources were retrieved.

Usage:
    python -m app.evals evals/sample_questions.jsonl
"""

import argparse
import json
import logging
import re
from dataclasses import dataclass

import psycopg
from vertexai.generative_models import GenerationConfig, GenerativeModel

from .config import settings
from .rag import build_prompt, init_vertex, retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("evals")

JUDGE_PROMPT = """You are evaluating a customer support answer for faithfulness.

Retrieved context:
{context}

Question: {question}
Answer: {answer}

Is every factual claim in the answer directly supported by the context?
Refusals ("I don't know") count as faithful if the context truly lacks the answer.
Reply with exactly one word: PASS or FAIL."""

CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass
class EvalResult:
    question: str
    faithful: bool
    citations_ok: bool

    @property
    def passed(self) -> bool:
        return self.faithful and self.citations_ok


def run_pipeline(conn, judge: GenerativeModel, question: str) -> EvalResult:
    chunks = retrieve(conn, question)
    answer = judge.generate_content(
        build_prompt(question, chunks),
        generation_config=GenerationConfig(
            temperature=settings.temperature, max_output_tokens=settings.max_output_tokens
        ),
    ).text

    verdict = judge.generate_content(
        JUDGE_PROMPT.format(
            context="\n\n".join(f"[{c['rank']}] {c['content']}" for c in chunks),
            question=question,
            answer=answer,
        ),
        generation_config=GenerationConfig(temperature=0, max_output_tokens=8),
    ).text.strip().upper()
    faithful = verdict.startswith("PASS")

    cited = {int(n) for n in CITATION_RE.findall(answer)}
    valid = {c["rank"] for c in chunks}
    citations_ok = cited.issubset(valid) and (bool(cited) or not chunks)

    return EvalResult(question=question, faithful=faithful, citations_ok=citations_ok)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAG eval harness.")
    parser.add_argument("jsonl", help="path to JSONL with {question, expected?} rows")
    args = parser.parse_args()

    init_vertex()
    judge = GenerativeModel(settings.gemini_model)

    with open(args.jsonl, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    log.info("running %d eval questions", len(rows))

    results = []
    with psycopg.connect(settings.db_dsn) as conn:
        for row in rows:
            result = run_pipeline(conn, judge, row["question"])
            results.append(result)
            log.info(
                "%s | faithful=%s citations_ok=%s | %s",
                "PASS" if result.passed else "FAIL",
                result.faithful, result.citations_ok, result.question,
            )

    passed = sum(r.passed for r in results)
    print(f"\npass rate: {passed}/{len(results)} ({passed / len(results):.0%})")


if __name__ == "__main__":
    main()

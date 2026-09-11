import json
import re

from pathlib import Path
from time import perf_counter
from uuid import UUID

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.embeddings.bge import BGEEmbeddingProvider
from app.evaluation.metrics import (
    hit_rate_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from app.models import Chunk, Document
from app.retrieval.service import RetrievalService
from app.reranking.cross_encoder import CrossEncoderReranker


EVALUATION_TENANT_ID=UUID(
    "11111111-1111-1111-1111-111111111111"
)

ORIGINAL_EVAL_PATH=Path(
    "data/technical-troubleshooting-corpus/evaluation/retrieval-eval.json"
)

HYBRID_EVAL_PATH=Path(
    r"C:\Users\mohit\OneDrive\Desktop\RAG\tests\Testing 50 ques\retrieval-eval-50.json"
)

EVIDENCE_PATTERN=re.compile(
    r"KB-[A-Z]+(?:-[A-Z]+)*-\d{3}"
)

FINAL_K=5
CANDIDATE_K=20
MAX_DISTANCE=0.4


def extract_evidence_ids(text: str) -> set[str]:
    return set(
        EVIDENCE_PATTERN.findall(text)
    )


def load_json(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_evaluation_cases():
    original_cases=load_json(
        ORIGINAL_EVAL_PATH
    )

    hybrid_cases=load_json(
        HYBRID_EVAL_PATH
    )

    cases=original_cases+hybrid_cases

    print(
        f"Loaded {len(original_cases)} original cases"
    )

    print(
        f"Loaded {len(hybrid_cases)} hybrid edge cases"
    )

    print(
        f"Total evaluation cases: {len(cases)}"
    )

    return cases


def build_chunk_evidence_map(chunks):
    evidence_map={}
    current_evidence_id=None

    for chunk in chunks:
        ids=extract_evidence_ids(
            chunk.content
        )

        if ids:
            current_evidence_id=next(
                iter(ids)
            )

        evidence_map[
            chunk.chunk_index
        ]=current_evidence_id

    return evidence_map


def build_global_evidence_map():
    evidence_map={}

    with SessionLocal() as session:
        documents=session.scalars(
            select(Document).where(
                Document.tenant_id
                ==EVALUATION_TENANT_ID
            )
        ).all()

        print(
            f"Evaluation tenant documents: "
            f"{len(documents)}"
        )

        for document in documents:
            chunks=session.scalars(
                select(Chunk)
                .where(
                    Chunk.document_id
                    ==document.id
                )
                .order_by(
                    Chunk.chunk_index
                )
            ).all()

            document_map=(
                build_chunk_evidence_map(
                    chunks
                )
            )

            for (
                chunk_index,
                evidence_id,
            ) in document_map.items():
                evidence_map[
                    (
                        document.id,
                        chunk_index,
                    )
                ]=evidence_id

    return evidence_map


def evaluate(
    name,
    cases,
    retrieval_function,
    evidence_map,
):
    hit_rates=[]
    precisions=[]
    recalls=[]
    reciprocal_ranks=[]
    latencies_ms=[]
    failed_queries=[]

    print(
        f"\n=== {name} ==="
    )

    for case in cases:
        start=perf_counter()

        results=retrieval_function(
            query=case["query"],
            tenant_id=EVALUATION_TENANT_ID,
        )

        latency_ms=(
            perf_counter()-start
        )*1000

        latencies_ms.append(
            latency_ms
        )

        retrieved_evidence_ids=[
            evidence_map.get(
                (
                    chunk.document_id,
                    chunk.chunk_index,
                )
            )
            for chunk,_ in results
        ]

        retrieved_evidence_ids=[
            evidence_id
            for evidence_id
            in retrieved_evidence_ids
            if evidence_id is not None
        ]

        unique_retrieved_evidence_ids=list(
            dict.fromkeys(
                retrieved_evidence_ids
            )
        )

        relevant_evidence_ids=set(
            case[
                "relevant_evidence_ids"
            ]
        )

        hit_rate=hit_rate_at_k(
            retrieved_evidence_ids,
            relevant_evidence_ids,
            FINAL_K,
        )

        precision=precision_at_k(
            unique_retrieved_evidence_ids,
            relevant_evidence_ids,
            FINAL_K,
        )

        recall=recall_at_k(
            retrieved_evidence_ids,
            relevant_evidence_ids,
            FINAL_K,
        )

        rr=reciprocal_rank(
            retrieved_evidence_ids,
            relevant_evidence_ids,
        )

        hit_rates.append(
            hit_rate
        )

        precisions.append(
            precision
        )

        recalls.append(
            recall
        )

        reciprocal_ranks.append(
            rr
        )

        if hit_rate==0:
            failed_queries.append(
                case["id"]
            )

        print(
            f"{case['id']} | "
            f"Hit={hit_rate:.2f} | "
            f"Precision={precision:.2f} | "
            f"Recall={recall:.2f} | "
            f"RR={rr:.2f} | "
            f"Latency={latency_ms:.2f}ms"
        )

    count=len(cases)

    metrics={
        "hit_rate":(
            sum(hit_rates)/count
        ),
        "precision":(
            sum(precisions)/count
        ),
        "recall":(
            sum(recalls)/count
        ),
        "mrr":(
            sum(reciprocal_ranks)/count
        ),
        "latency":(
            sum(latencies_ms)/count
        ),
        "failed_queries":(
            failed_queries
        ),
    }

    print(
        f"\n{name} Summary"
    )

    print(
        f"Questions: {count}"
    )

    print(
        f"HitRate@5: "
        f"{metrics['hit_rate']:.4f}"
    )

    print(
        f"Precision@5: "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall@5: "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"MRR: "
        f"{metrics['mrr']:.4f}"
    )

    print(
        f"Average latency: "
        f"{metrics['latency']:.2f} ms"
    )

    print(
        f"Failed queries: "
        f"{', '.join(failed_queries)}"
    )

    return metrics


def dense_retrieval(
    retrieval_service,
    query,
    tenant_id,
):
    return retrieval_service.dense_search(
        query=query,
        tenant_id=tenant_id,
        top_k=FINAL_K,
        max_distance=MAX_DISTANCE,
    )


def hybrid_retrieval(
    retrieval_service,
    query,
    tenant_id,
):
    return retrieval_service.search(
        query=query,
        tenant_id=tenant_id,
        top_k=FINAL_K,
        max_distance=MAX_DISTANCE,
    )


def hybrid_reranked_retrieval(
    retrieval_service,
    reranker,
    query,
    tenant_id,
):
    candidates=retrieval_service.search(
        query=query,
        tenant_id=tenant_id,
        top_k=CANDIDATE_K,
        max_distance=MAX_DISTANCE,
    )

    return reranker.rerank(
        query=query,
        results=candidates,
        top_k=FINAL_K,
    )


def print_comparison(
    dense_metrics,
    hybrid_metrics,
    reranked_metrics,
):
    print(
        "\n=========================================="
    )

    print(
        "          RETRIEVAL COMPARISON"
    )

    print(
        "=========================================="
    )

    print(
        "                  Dense     Hybrid    Reranked"
    )

    print(
        f"HitRate@5       "
        f"{dense_metrics['hit_rate']:.4f}    "
        f"{hybrid_metrics['hit_rate']:.4f}    "
        f"{reranked_metrics['hit_rate']:.4f}"
    )

    print(
        f"Precision@5     "
        f"{dense_metrics['precision']:.4f}    "
        f"{hybrid_metrics['precision']:.4f}    "
        f"{reranked_metrics['precision']:.4f}"
    )

    print(
        f"Recall@5        "
        f"{dense_metrics['recall']:.4f}    "
        f"{hybrid_metrics['recall']:.4f}    "
        f"{reranked_metrics['recall']:.4f}"
    )

    print(
        f"MRR             "
        f"{dense_metrics['mrr']:.4f}    "
        f"{hybrid_metrics['mrr']:.4f}    "
        f"{reranked_metrics['mrr']:.4f}"
    )

    print(
        f"Latency(ms)     "
        f"{dense_metrics['latency']:.2f}    "
        f"{hybrid_metrics['latency']:.2f}    "
        f"{reranked_metrics['latency']:.2f}"
    )

    dense_failures=set(
        dense_metrics[
            "failed_queries"
        ]
    )

    hybrid_failures=set(
        hybrid_metrics[
            "failed_queries"
        ]
    )

    reranked_failures=set(
        reranked_metrics[
            "failed_queries"
        ]
    )

    hybrid_rescued=sorted(
        dense_failures
        -hybrid_failures
    )

    hybrid_regressed=sorted(
        hybrid_failures
        -dense_failures
    )

    reranker_rescued=sorted(
        hybrid_failures
        -reranked_failures
    )

    reranker_regressed=sorted(
        reranked_failures
        -hybrid_failures
    )

    total_rescued=sorted(
        dense_failures
        -reranked_failures
    )

    total_regressed=sorted(
        reranked_failures
        -dense_failures
    )

    print()

    print(
        "Hybrid rescued vs dense: "
        +(
            ", ".join(hybrid_rescued)
            if hybrid_rescued
            else "None"
        )
    )

    print(
        "Hybrid regressed vs dense: "
        +(
            ", ".join(hybrid_regressed)
            if hybrid_regressed
            else "None"
        )
    )

    print(
        "Reranker rescued vs hybrid: "
        +(
            ", ".join(reranker_rescued)
            if reranker_rescued
            else "None"
        )
    )

    print(
        "Reranker regressed vs hybrid: "
        +(
            ", ".join(reranker_regressed)
            if reranker_regressed
            else "None"
        )
    )

    print(
        "Final pipeline rescued vs dense: "
        +(
            ", ".join(total_rescued)
            if total_rescued
            else "None"
        )
    )

    print(
        "Final pipeline regressed vs dense: "
        +(
            ", ".join(total_regressed)
            if total_regressed
            else "None"
        )
    )


def main():
    cases=load_evaluation_cases()

    settings=get_settings()

    print(
        "\nLoading embedding model..."
    )

    embedding_provider=(
        BGEEmbeddingProvider(
            settings.embedding_model
        )
    )

    retrieval_service=(
        RetrievalService(
            embedding_provider=(
                embedding_provider
            )
        )
    )

    print(
        "Loading CrossEncoder reranker..."
    )

    reranker=CrossEncoderReranker()

    print(
        "Models loaded."
    )

    evidence_map=(
        build_global_evidence_map()
    )

    print(
        f"Mapped chunks: "
        f"{len(evidence_map)}"
    )

    dense_metrics=evaluate(
        name="Dense Retrieval",
        cases=cases,
        retrieval_function=(
            lambda query,
            tenant_id:
            dense_retrieval(
                retrieval_service,
                query,
                tenant_id,
            )
        ),
        evidence_map=evidence_map,
    )

    hybrid_metrics=evaluate(
        name="Hybrid Retrieval",
        cases=cases,
        retrieval_function=(
            lambda query,
            tenant_id:
            hybrid_retrieval(
                retrieval_service,
                query,
                tenant_id,
            )
        ),
        evidence_map=evidence_map,
    )

    reranked_metrics=evaluate(
        name="Hybrid + CrossEncoder",
        cases=cases,
        retrieval_function=(
            lambda query,
            tenant_id:
            hybrid_reranked_retrieval(
                retrieval_service,
                reranker,
                query,
                tenant_id,
            )
        ),
        evidence_map=evidence_map,
    )

    print_comparison(
        dense_metrics,
        hybrid_metrics,
        reranked_metrics,
    )


if __name__=="__main__":
    main()
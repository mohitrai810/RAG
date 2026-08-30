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


EVALUATION_TENANT_ID=UUID(
    "11111111-1111-1111-1111-111111111111"
)

EVAL_PATH=Path(
    "data/technical-troubleshooting-corpus/evaluation/retrieval-eval.json"
)

EVIDENCE_PATTERN=re.compile(r"KB-[A-Z]+-\d{3}")


def extract_evidence_ids(text: str) -> set[str]:
    return set(EVIDENCE_PATTERN.findall(text))


def load_evaluation_cases():
    with EVAL_PATH.open("r",encoding="utf-8") as file:
        return json.load(file)


def build_chunk_evidence_map(chunks):
    evidence_map={}
    current_evidence_id=None

    for chunk in chunks:
        ids=extract_evidence_ids(chunk.content)

        if ids:
            current_evidence_id=next(iter(ids))

        evidence_map[chunk.chunk_index]=current_evidence_id

    return evidence_map


def build_global_evidence_map():
    evidence_map={}

    with SessionLocal() as session:
        documents=session.scalars(
            select(Document).where(
                Document.tenant_id==EVALUATION_TENANT_ID
            )
        ).all()

        for document in documents:
            chunks=session.scalars(
                select(Chunk)
                .where(Chunk.document_id==document.id)
                .order_by(Chunk.chunk_index)
            ).all()

            document_map=build_chunk_evidence_map(chunks)

            for chunk_index,evidence_id in document_map.items():
                evidence_map[(document.id,chunk_index)]=evidence_id

    return evidence_map


def main():
    cases=load_evaluation_cases()

    settings=get_settings()

    embedding_provider=BGEEmbeddingProvider(
        settings.embedding_model
    )

    retrieval_service=RetrievalService(
        embedding_provider=embedding_provider
    )

    evidence_map=build_global_evidence_map()

    hit_rates=[]
    precisions=[]
    recalls=[]
    reciprocal_ranks=[]
    latencies_ms=[]

    for case in cases:
        start=perf_counter()

        results=retrieval_service.search(
            query=case["query"],
            tenant_id=EVALUATION_TENANT_ID,
            top_k=5,
        )

        latency_ms=(perf_counter()-start)*1000
        latencies_ms.append(latency_ms)

        retrieved_evidence_ids=[
            evidence_map.get(
                (chunk.document_id,chunk.chunk_index)
            )
            for chunk,distance in results
        ]

        retrieved_evidence_ids=[
            evidence_id
            for evidence_id in retrieved_evidence_ids
            if evidence_id is not None
        ]

        unique_retrieved_evidence_ids=list(
            dict.fromkeys(retrieved_evidence_ids)
        )

        relevant_evidence_ids=set(
            case["relevant_evidence_ids"]
        )

        hit_rate=hit_rate_at_k(
            retrieved_evidence_ids,
            relevant_evidence_ids,
            5,
        )

        precision=precision_at_k(
            unique_retrieved_evidence_ids,
            relevant_evidence_ids,
            5,
        )

        recall=recall_at_k(
            retrieved_evidence_ids,
            relevant_evidence_ids,
            5,
        )

        rr=reciprocal_rank(
            retrieved_evidence_ids,
            relevant_evidence_ids,
        )

        hit_rates.append(hit_rate)
        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(rr)

        print(
            f"{case['id']} | "
            f"Hit={hit_rate:.2f} | "
            f"Precision={precision:.2f} | "
            f"Recall={recall:.2f} | "
            f"RR={rr:.2f} | "
            f"Latency={latency_ms:.2f}ms"
        )

    count=len(cases)

    print("\n=== PGVector Baseline ===")
    print(f"Questions: {count}")
    print(f"HitRate@5: {sum(hit_rates)/count:.4f}")
    print(f"Precision@5: {sum(precisions)/count:.4f}")
    print(f"Recall@5: {sum(recalls)/count:.4f}")
    print(
        f"MRR: "
        f"{sum(reciprocal_ranks)/count:.4f}"
    )
    print(
        f"Average latency: "
        f"{sum(latencies_ms)/count:.2f} ms"
    )


if __name__=="__main__":
    main()
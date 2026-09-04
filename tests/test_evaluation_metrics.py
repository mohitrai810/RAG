from app.evaluation.metrics import hit_rate_at_k


def test_hit_rate_relevant_result_below_rank_1():
    retrieved=["KB-REDIS-002","KB-REDIS-001","KB-REDIS-003"]
    relevant={"KB-REDIS-001"}

    result=hit_rate_at_k(retrieved,relevant,3)

    assert result==1.0

def test_hit_rate_no_relevant_result_retrieved():
    retrieved=["KB-REDIS-002","KB-REDIS-003","KB-REDIS-004"]
    relevant={"KB-REDIS-001"}

    result=hit_rate_at_k(retrieved,relevant,3)

    assert result==0.0

def test_hit_rate_empty_retrieved_list():
    retrieved=[]
    relevant={"KB-REDIS-001"}

    result=hit_rate_at_k(retrieved,relevant,3)

    assert result==0.0

from app.evaluation.metrics import (
    hit_rate_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_at_k():
    retrieved=["KB-1","KB-2","KB-3"]
    relevant={"KB-1","KB-3"}

    assert precision_at_k(retrieved,relevant,3)==2/3


def test_recall_at_k():
    retrieved=["KB-1","KB-9","KB-3"]
    relevant={"KB-1","KB-2","KB-3"}

    assert recall_at_k(retrieved,relevant,3)==2/3


def test_reciprocal_rank():
    retrieved=["KB-X","KB-Y","KB-1"]
    relevant={"KB-1"}

    assert reciprocal_rank(retrieved,relevant)==1/3
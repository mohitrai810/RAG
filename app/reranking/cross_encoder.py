import os
import onnxruntime as ort
from sentence_transformers import CrossEncoder

from app.reranking.provider import RerankerProvider

# 1. Set environment variables BEFORE ONNX initializes
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"

# 2. Configure session options for CPU execution
session_options = ort.SessionOptions()
session_options.intra_op_num_threads = 4
session_options.inter_op_num_threads = 1


class CrossEncoderReranker(RerankerProvider):

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        
        self.model = CrossEncoder(
            model_name,
            backend="onnx",
            model_kwargs={
                "file_name": "onnx/model_quint8_avx2.onnx",
                "session_options": session_options,
            },
        )

    def rerank(
        self,
        query: str,
        results,
        top_k: int,
    ):
        if not results:
            return []

        # Build list of (query, document_content) pairs
        pairs = [(query, chunk.content) for chunk, _ in results]

        scores = self.model.predict(pairs)

        scored_results = [
            (chunk, distance, float(score))
            for (chunk, distance), score in zip(results, scores)
        ]

        # Sort descending by cross-encoder score
        scored_results.sort(key=lambda item: item[2], reverse=True)

        return [(chunk, distance) for chunk, distance, _ in scored_results[:top_k]]
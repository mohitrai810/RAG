from sentence_transformers import CrossEncoder

from app.reranking.provider import RerankerProvider


class CrossEncoderReranker(RerankerProvider):

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results,
        top_k: int,
    ):
        if not results:
            return []

        pairs = []

        for chunk, distance in results:
            pairs.append(
                (
                    query,
                    chunk.content,
                )
            )

        scores = self.model.predict(pairs)

        scored_results = []

        for result, score in zip(
            results,
            scores,
        ):
            chunk, distance = result

            scored_results.append(
                (
                    chunk,
                    distance,
                    float(score),
                )
            )

        scored_results.sort(
            key=lambda item: item[2],
            reverse=True,
        )

        final_results = []

        for chunk, distance, score in scored_results[:top_k]:
            final_results.append(
                (
                    chunk,
                    distance,
                )
            )

        return final_results
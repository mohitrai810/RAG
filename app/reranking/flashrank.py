from flashrank import Ranker, RerankRequest

from app.reranking.provider import RerankerProvider


class FlashRankReranker(RerankerProvider):
    def __init__(self):
        self.ranker = Ranker(
            model_name="ms-marco-MiniLM-L-12-v2"
            )

    def rerank(
        self,
        query: str,
        results,
        top_k: int,
    ):
        passages = []

        for index, result in enumerate(results):
            chunk, distance = result

            passages.append(
                {
                    "id": index,
                    "text": chunk.content,
                    "meta": {
                        "chunk": chunk,
                        "distance": distance,
                    },
                }
            )

        request = RerankRequest(
            query=query,
            passages=passages,
        )

        reranked = self.ranker.rerank(request)

        final_results = []

        for item in reranked[:top_k]:
            final_results.append(
                (
                    item["meta"]["chunk"],
                    item["meta"]["distance"],
                )
            )

        return final_results
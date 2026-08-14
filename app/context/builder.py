from app.models import Chunk


class ContextBuilder:

    def build(self, results: list[tuple[Chunk, float]]) -> str:
        if not results:
            return ""

        context_parts = []

        for chunk, distance in results:
            context_parts.append(
                f"""SOURCE: {chunk.chunk_metadata.get("source", "unknown")}
CHUNK: {chunk.chunk_index}
DISTANCE: {distance:.4f}

{chunk.content}"""
            )

        return "\n\n---\n\n".join(context_parts)
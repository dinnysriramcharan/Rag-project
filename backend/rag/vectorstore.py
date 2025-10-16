import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec


class PineconeVectorStore:
    def __init__(self) -> None:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENV")
        index_name = os.getenv("PINECONE_INDEX", "documents")
        if not pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is not set")
        if not pinecone_env:
            raise RuntimeError("PINECONE_ENV is not set")

        self.index_name = index_name
        self.pc = Pinecone(api_key=pinecone_api_key)

        # Ensure index exists (safe on serverless init flows outside hot path)
        if index_name not in [idx["name"] for idx in self.pc.list_indexes()]:
            # Default to OpenAI text-embedding-3-small dimension 1536
            self.pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=pinecone_env),
            )

        self.index = self.pc.Index(index_name)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.openai = OpenAI()
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        response = self.openai.embeddings.create(
            model=self.embedding_model,
            input=texts,
        )
        return [d.embedding for d in response.data]

    def upsert(self, items: List[Tuple[str, str, Dict[str, Any]]], namespace: Optional[str] = None) -> None:
        # items: (id, text, metadata)
        vectors: List[Dict[str, Any]] = []
        embeddings = self.embed_texts([text for _, text, _ in items])
        for (item_id, _text, metadata), values in zip(items, embeddings):
            vectors.append({"id": item_id, "values": values, "metadata": metadata})
        self.index.upsert(vectors=vectors, namespace=namespace or "default")

    def query(self, query: str, top_k: int = 5, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        query_vec = self.embed_texts([query])[0]
        result = self.index.query(
            vector=query_vec,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace or "default",
        )
        # Normalize response
        matches = []
        for m in result.get("matches", []):
            matches.append(
                {
                    "id": m.get("id"),
                    "score": m.get("score"),
                    "metadata": m.get("metadata", {}),
                }
            )
        return matches



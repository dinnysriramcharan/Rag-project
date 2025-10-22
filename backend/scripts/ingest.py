import argparse
import hashlib
import os
import pathlib
from typing import Dict, List, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables from backend/.env if present (for standalone runs)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / "backend" / ".env", override=False)


def file_to_text(path: pathlib.Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        parts: List[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    elif path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def chunk_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build_items(file_path: pathlib.Path, chunks: List[str]) -> List[Tuple[str, str, Dict]]:
    items: List[Tuple[str, str, Dict]] = []
    for idx, chunk in enumerate(chunks):
        cid = f"{file_path.name}-{idx}-{hash_text(chunk)}"
        items.append(
            (
                cid,
                chunk,
                {
                    "source": str(file_path),
                    "chunk_id": idx,
                    "text": chunk,
                },
            )
        )
    return items


def upsert_items(index_name: str, namespace: str, items: List[Tuple[str, str, Dict]]) -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI()
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"]) 
    
    # Create index if it doesn't exist
    if index_name not in [idx["name"] for idx in pc.list_indexes()]:
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=1536,  # text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=os.environ["PINECONE_ENV"]),
        )
        print(f"Index '{index_name}' created successfully!")
    
    index = pc.Index(index_name)

    # embed in small batches
    batch_size = 64
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        texts = [t for _id, t, _m in batch]
        emb = client.embeddings.create(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"), input=texts)
        vectors = []
        for (_id, _t, meta), data in zip(batch, emb.data):
            vectors.append({"id": _id, "values": data.embedding, "metadata": meta})
        index.upsert(vectors=vectors, namespace=namespace)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest files into Pinecone")
    parser.add_argument("path", type=str, help="File or directory to ingest")
    parser.add_argument("--namespace", type=str, default="default")
    parser.add_argument("--index", type=str, default=os.getenv("PINECONE_INDEX", "documents"))
    args = parser.parse_args()

    target = pathlib.Path(args.path)
    paths: List[pathlib.Path] = []
    if target.is_dir():
        for p in target.rglob("*"):
            if p.suffix.lower() in {".pdf", ".txt", ".md"}:
                paths.append(p)
    else:
        paths.append(target)

    all_items: List[Tuple[str, str, Dict]] = []
    for p in paths:
        text = file_to_text(p)
        chunks = chunk_text(text)
        all_items.extend(build_items(p, chunks))

    if not all_items:
        print("No content found.")
        return

    upsert_items(index_name=args.index, namespace=args.namespace, items=all_items)
    print(f"Ingested {len(all_items)} chunks into index '{args.index}' namespace '{args.namespace}'.")


if __name__ == "__main__":
    main()



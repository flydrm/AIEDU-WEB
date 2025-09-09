from __future__ import annotations

from collections import Counter
from math import log, sqrt
from typing import Any, Iterable
import asyncio
from app.infrastructure.ai.clients import EmbeddingsClient, RerankerClient


def _is_cjk(ch: str) -> bool:
    code = ord(ch)
    return (
        0x4E00 <= code <= 0x9FFF  # CJK Unified Ideographs
        or 0x3400 <= code <= 0x4DBF  # CJK Unified Ideographs Extension A
        or 0x20000 <= code <= 0x2A6DF  # Extension B
        or 0x2A700 <= code <= 0x2B73F  # Extension C
        or 0x2B740 <= code <= 0x2B81F  # Extension D
        or 0x2B820 <= code <= 0x2CEAF  # Extension E
        or 0xF900 <= code <= 0xFAFF  # CJK Compatibility Ideographs
    )


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    buf: list[str] = []
    for ch in text:
        if ch.isascii() and (ch.isalnum()):
            buf.append(ch.lower())
            continue
        if buf:
            tokens.append("".join(buf))
            buf.clear()
        if _is_cjk(ch):
            tokens.append(ch)
    if buf:
        tokens.append("".join(buf))
    return [t for t in tokens if t]


class SimpleRetriever:
    """Lightweight TF-IDF retriever over in-memory dataset.

    Documents are constructed from kids dataset (knowledge cards and story prompts).
    Tokenization supports ASCII words and single-character CJK tokens.
    """

    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = docs
        self._vocab_df: Counter[str] = Counter()
        self._doc_tokens: list[list[str]] = []
        # pre-tokenize
        for d in docs:
            toks = tokenize(d["text"]) if d.get("text") else []
            self._doc_tokens.append(toks)
            self._vocab_df.update(set(toks))
        self._N = len(docs)
        # precompute tf-idf vectors (sparse dict)
        self._doc_vecs: list[dict[str, float]] = []
        for toks in self._doc_tokens:
            tf = Counter(toks)
            vec: dict[str, float] = {}
            for tok, f in tf.items():
                df = self._vocab_df.get(tok, 1)
                idf = log((1 + self._N) / (1 + df)) + 1.0
                vec[tok] = (f / len(toks)) * idf
            # L2 normalize
            norm = sqrt(sum(v * v for v in vec.values())) or 1.0
            for k in list(vec.keys()):
                vec[k] /= norm
            self._doc_vecs.append(vec)

    def _vectorize(self, text: str) -> dict[str, float]:
        toks = tokenize(text)
        if not toks:
            return {}
        tf = Counter(toks)
        vec: dict[str, float] = {}
        for tok, f in tf.items():
            df = self._vocab_df.get(tok, 0)
            idf = log((1 + self._N) / (1 + df)) + 1.0
            vec[tok] = (f / len(toks)) * idf
        norm = sqrt(sum(v * v for v in vec.values())) or 1.0
        for k in list(vec.keys()):
            vec[k] /= norm
        return vec

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        qv = self._vectorize(query)
        if not qv:
            return []
        def cosine(dv: dict[str, float]) -> float:
            return sum(qv[t] * dv.get(t, 0.0) for t in qv.keys())
        scores = [(idx, cosine(self._doc_vecs[idx])) for idx in range(self._N)]
        scores.sort(key=lambda x: x[1], reverse=True)
        results: list[dict[str, Any]] = []
        for idx, sc in scores[:top_k]:
            item = dict(self._docs[idx])
            item["score"] = sc
            results.append(item)
        return results

    @staticmethod
    def from_kids_dataset(dataset: dict[str, Any]) -> "SimpleRetriever":
        docs: list[dict[str, Any]] = []
        for card in dataset.get("knowledge_cards", []):
            text_parts: list[str] = []
            if card.get("title"):
                text_parts.append(str(card["title"]))
            for ln in card.get("lines", []) or []:
                text_parts.append(str(ln))
            if card.get("question"):
                text_parts.append(str(card["question"]))
            for tag in card.get("tags", []) or []:
                text_parts.append(str(tag))
            text = "\n".join(text_parts)
            docs.append({
                "type": "card",
                "id": card.get("id"),
                "category": card.get("category"),
                "title": card.get("title"),
                "text": text,
            })
        for sp in dataset.get("story_prompts", []):
            text = str(sp.get("prompt") or "")
            docs.append({
                "type": "story",
                "id": sp.get("id"),
                "title": sp.get("title"),
                "text": text,
            })
        return SimpleRetriever(docs)


class HybridRetriever(SimpleRetriever):
    """Hybrid retriever: combine TF-IDF with optional embeddings + rerank hooks.

    If embeddings provider is configured, it augments scores by cosine over embeddings.
    """

    def __init__(self, docs: list[dict[str, Any]], embed_client: EmbeddingsClient | None = None, reranker: RerankerClient | None = None) -> None:
        super().__init__(docs)
        self._embed_client = embed_client
        self._doc_embeds: list[list[float] | None] = [None] * len(docs)
        self._reranker = reranker

    async def _ensure_doc_embeds(self) -> None:
        if not self._embed_client:
            return
        # naive: compute once per process (could cache to disk in production)
        for idx, d in enumerate(self._docs):
            if self._doc_embeds[idx] is not None:
                continue
            text = d.get("text") or ""
            if not text:
                self._doc_embeds[idx] = []
                continue
            try:
                data = await self._embed_client.embeddings({"model": "BAAI/bge-m3", "input": text})
                vec = data.get("data", [{}])[0].get("embedding") or []
                self._doc_embeds[idx] = list(map(float, vec))
            except Exception:
                self._doc_embeds[idx] = []

    async def retrieve_async(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        base = super().retrieve(query, top_k=top_k * 4)
        if not self._embed_client or not base:
            return base[:top_k]
        await self._ensure_doc_embeds()
        # query embed
        try:
            q = await self._embed_client.embeddings({"model": "BAAI/bge-m3", "input": query})
            qv = list(map(float, (q.get("data", [{}])[0].get("embedding") or [])))
        except Exception:
            return base[:top_k]
        def cos(a: list[float], b: list[float]) -> float:
            if not a or not b:
                return 0.0
            n = min(len(a), len(b))
            sa = sum(x*x for x in a[:n]) ** 0.5 or 1.0
            sb = sum(x*x for x in b[:n]) ** 0.5 or 1.0
            s = 0.0
            for i in range(n):
                s += a[i] * b[i]
            return s / (sa * sb)
        rescored = []
        for item in base:
            idx = self._docs.index(item)  # small list; ok for MVP
            sim = cos(qv, self._doc_embeds[idx] or []) * 0.7  # weight embeddings
            rescored.append((item, item.get("score", 0.0) * 0.3 + sim))
        rescored.sort(key=lambda x: x[1], reverse=True)
        items = [it for it, _ in rescored[: top_k * 2]]
        # optional rerank via API
        if self._reranker:
            try:
                payload = {"model": "BAAI/bge-reranker-v2-m3", "query": query, "documents": [i.get("text", "") for i in items]}
                rr = await self._reranker.rerank(payload)
                order = rr.get("data") or []
                # assume list of {index, score}
                pairs = [(items[e.get("index", 0)], float(e.get("score", 0.0))) for e in order]
                pairs.sort(key=lambda x: x[1], reverse=True)
                return [it for it, _ in pairs[:top_k]]
            except Exception:
                pass
        return items[:top_k]


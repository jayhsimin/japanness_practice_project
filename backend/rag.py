from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_DIR = str(Path(__file__).resolve().parent / "chroma_db")
COLLECTION_NAME = "vocab"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class VocabRAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)
        self.model = SentenceTransformer(MODEL_NAME)

    def upsert(self, vocab_id: int, zh: str, ja: str):
        text = f"{zh} {ja}"
        embedding = self.model.encode([text])[0].tolist()
        self.collection.upsert(
            ids=[str(vocab_id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"zh": zh, "ja": ja}],
        )

    def delete(self, vocab_id: int):
        try:
            self.collection.delete(ids=[str(vocab_id)])
        except Exception:
            pass

    def sync_all(self, vocab_list: list):
        if not vocab_list:
            return
        texts = [f"{v.zh} {v.ja}" for v in vocab_list]
        embeddings = self.model.encode(texts).tolist()
        self.collection.upsert(
            ids=[str(v.id) for v in vocab_list],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"zh": v.zh, "ja": v.ja} for v in vocab_list],
        )

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        count = self.collection.count()
        if count == 0:
            return []
        embedding = self.model.encode([query])[0].tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, count),
        )
        return results["metadatas"][0] if results["metadatas"] else []


vocab_rag = VocabRAG()

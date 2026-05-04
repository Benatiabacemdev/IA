import time
from langchain.schema import BaseRetriever


class ConfidenceRetriever(BaseRetriever):
    vectorstore: object
    similarity_threshold: float = 0.65
    k: int = 5
    last_retrieval_time: float = 0.0

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str):
        t0 = time.perf_counter()
        results = self.vectorstore.similarity_search_with_score(query, k=self.k)
        self.last_retrieval_time = time.perf_counter() - t0
        if not results:
            return []

        docs_with_scores = [(doc, score) for doc, score in results]
        relevant_docs = [doc for doc, score in docs_with_scores if score >= self.similarity_threshold]

        if relevant_docs:
            return relevant_docs

        max_score = max([score for _, score in docs_with_scores])
        if max_score < 0.3:
            return []

        return [doc for doc, score in docs_with_scores[:2]]

    async def _aget_relevant_documents(self, query: str):
        return self._get_relevant_documents(query)

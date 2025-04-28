from abc import ABC, abstractmethod

class ReRankModel(ABC):
    @abstractmethod
    def invoke_rerank(self, query: str, documents: list, score_threshold: float = None, top_n: int = None) -> dict:
        """
        Invoke rerank model

        :param query: search query
        :param documents: docs for reranking
        :param score_threshold: score threshold
        :param top_n: top n
        :return: rerank result
        """
        pass
    
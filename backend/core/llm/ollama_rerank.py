from core.llm.rerank import ReRankModel
import requests
class OllamaRerankModel(ReRankModel):
    def __init__(self, base_url: str, model: str) -> None:
        # 设置请求的 URL
        self.url = base_url
        self.model = model

    def invoke_rerank(self, query: str, documents: list, score_threshold: float = None, top_n: int = None) -> dict:
        """
        Invoke rerank model

        :param query: search query
        :param documents: docs for reranking
        :param score_threshold: score threshold
        :param top_n: top n
        :return: rerank result
        """
        if len(documents) == 0:
            return {"model": self.model, "docs": []}

        # 设置请求体
        data = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "top_n": top_n
        }

        # 发送 POST 请求
        response = requests.post(self.url, json=data)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, Message: {response.text}")

        response_data = response.json()

        rerank_documents = []
        for idx, result in enumerate(response_data.get('results', [])):
            # format document
            index = result['index']
            page_content = documents[index]
            rerank_document = {
                "index": index,
                "text": page_content,
                "score": result['relevance_score'],
            }

            # score threshold check
            if score_threshold is not None and rerank_document["score"] < score_threshold:
                continue

            rerank_documents.append(rerank_document)

        return {"model": self.model, "docs": rerank_documents}
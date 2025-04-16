import requests
import json
from typing import List, Optional
from core.models.rerank_models import RerankDocument, RerankResult
from config.config_info import settings



class RerankModel:
    def __init__(self) -> None:
        # 设置请求的 URL
        self.url = settings.RERANK_BASE_URL

        # 设置请求头
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def invoke_rerank(self, query: str, documents: List[str], model_uid: str="bge-reranker-large",
                      score_threshold: Optional[float] = None, top_n: Optional[int] = None) -> RerankResult:
        """
        Invoke rerank model

        :param model_uid: model UID
        :param query: search query
        :param documents: docs for reranking
        :param score_threshold: score threshold
        :param top_n: top n
        :return: rerank result
        """
        if len(documents) == 0:
            return RerankResult(model=model_uid, docs=[])

        # 设置请求体
        
        data = {
            "model": model_uid,
            "query": query,
            "documents": documents,
            "top_n": top_n
        }

        # 发送 POST 请求
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data),verify=False)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, Message: {response.text}")

        response_data = response.json()
        
        rerank_documents = []
        for idx, result in enumerate(response_data.get('results', [])):
            # format document
            index = result['index']
            page_content = documents[index]
            rerank_document = RerankDocument(
                index=index,
                text=page_content,
                score=result['relevance_score'],
            )

            # score threshold check
            if score_threshold is not None:
                print(f"Score:{result['relevance_score']}")
                if result['relevance_score'] >= score_threshold:
                    rerank_documents.append(rerank_document)
            else:
                rerank_documents.append(rerank_document)

        return RerankResult(
            model=model_uid,
            docs=rerank_documents
        )

if __name__ == "__main__":
    rerank_model = RerankModel()
    query = "学校有几个食堂"
    documents = [
        "学校有3个食堂",
        "学校有A食堂",
        "学校有C食堂",
        "学校有2个医院，分别是A、B、C",
        "学校有2个超市"
    ]

    # 定义可选参数
    model_uid = "bge-reranker-large"
    score_threshold = 0.5  # 设定得分阈值
    top_n = 3  # 获取前 N 个结果

    # 调用 invoke_rerank 方法
    try:
        rerank_result = rerank_model.invoke_rerank(query, documents, model_uid, score_threshold, top_n)

        # 打印重排序结果
        print(f"Model: {rerank_result.model}")
        print("Ranked Documents:")
        for doc in rerank_result.docs:
            print(f"Index: {doc.index}, Score: {doc.score}, Text: {doc.text}")

    except Exception as e:
        print(f"An error occurred: {e}")

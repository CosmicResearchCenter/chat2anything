from typing import Optional,List

from core.llm.rerankmodel import RerankModel
from core.rag.models.document import Document
from core.models.rerank_models import RerankDocument, RerankResult


class RerankRunner:
    def __init__(self, rerank_model_instance: RerankModel) -> None:
        self.rerank_model_instance = rerank_model_instance

    def run(self, query: str, documents: List[Document], score_threshold: Optional[float] = None,
            top_n: Optional[int] = None, user: Optional[str] = None) -> List[Document]:
        """
        Run rerank model
        :param query: search query
        :param documents: documents for reranking
        :param score_threshold: score threshold
        :param top_n: top n
        :param user: unique user id if needed
        :return:
        """
        docs = []
        doc_id = []
        unique_documents = []
        for document in documents:
            # if document.metadata['knowledge_doc_name'] not in doc_id:
                doc_id.append(document.metadata['knowledge_doc_name'])
                docs.append(document.page_content)
                unique_documents.append(document)

        documents = unique_documents
        # print(len(docs))
        rerank_result:RerankResult = self.rerank_model_instance.invoke_rerank(
            query=query,
            documents=docs,
            score_threshold=score_threshold,
            top_n=top_n,
            # user=user
        )

        rerank_documents = []

        for result in rerank_result.docs:
            # format document
            rerank_document = Document(
                page_content=result.text,
                metadata={
                    # "doc_id": documents[result.index].metadata['doc_id'],
                    # "doc_hash": documents[result.index].metadata['doc_hash'],
                    # "document_id": documents[result.index].metadata['document_id'],
                    # "dataset_id": documents[result.index].metadata['dataset_id'],
                    'score': result.score,
                    "knowledge_doc_name":documents[result.index].metadata['knowledge_doc_name'],
                }
            )
            rerank_documents.append(rerank_document)

        return rerank_documents

if __name__ == '__main__':
    from core.llm.rerankmodel import RerankModel
    # rerank_model = RerankModel(url='http://10.116.123.30:9997/v1/rerank', headers={'Content-Type': 'application/json'})
    rerank_model = RerankModel()
    runner = RerankRunner(rerank_model)
    # documents = 
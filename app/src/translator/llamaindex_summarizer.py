from typing import Any, List

import nest_asyncio
from llama_index import (
    Document,
    ServiceContext,
    StorageContext,
    get_response_synthesizer,
)
from llama_index.indices.document_summary import DocumentSummaryIndex
from llama_index.llms.base import ChatMessage, MessageRole
from llama_index.prompts import ChatPromptTemplate
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.vector_stores import SimpleVectorStore


class llamaindex_summarizer:
    def __init__(
        self,
        llm_model,
        embed_model: Any,
        persist_dir: str | None = None,
        is_debug=False,
    ):
        """
        LlamaIndexSummarizerクラスのコンストラクタ

        Args:
            llm_model: LLMモデル
            embed_model: Embeddingモデル
            persist_dir: Contextの保存先ディレクトリ
            is_debug (bool, optional): デバッグモードかどうか. Defaults to False.
        """
        # self.llm_model = llm_model
        self.is_debug = is_debug
        self._storage_context = None
        self.node_parser = None
        self._callback_manager = None
        # self._embed_model = None
        self._service_context = self._SimpleServiceContext(
            llm_model=llm_model, embed_model=embed_model
        )
        self._storage_context = self._SimpleStorageContext(
            persist_dir=persist_dir
        )

        # 非同期処理の有効化
        nest_asyncio.apply()

        # デバッグの設定
        if is_debug:
            from llama_index.callbacks import CallbackManager, LlamaDebugHandler

            self._llama_debug_handler = LlamaDebugHandler(
                print_trace_on_end=True
            )
            self.callback_manager = CallbackManager([self._llama_debug_handler])

    def _SimpleStorageContext(self, persist_dir: str | None) -> None:
        """
        StorageContextを作成する関数

        """
        self._storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            vector_store=SimpleVectorStore(),
            index_store=SimpleIndexStore(),
            persist_dir=persist_dir,
        )

    def _SimpleServiceContext(self, llm_model, embed_model) -> None:
        self._service_context = ServiceContext.from_defaults(
            llm=llm_model,
            embed_model=embed_model,
            callback_manager=self._callback_manager,
            chunk_size=3072,
        )

    def from_documents(self, documents: List[Document]):
        """
        ドキュメントのリストからDocumentSummaryIndexオブジェクトを作成する関数

        Args:
            documents (List[Document]): ドキュメントのリスト

        Returns:
            doc_summary_index (DocumentSummaryIndex): DocumentSummaryIndexオブジェクト
        """
        # Summaryクエリ
        SUMMARY_QUERY = "提供されたテキストの内容を要約してください。"

        # レスポンスシンセサイザーの準備
        response_synthesizer = get_response_synthesizer(
            service_context=self._service_context,
            text_qa_template=self._get_text_qa_prompt_template(),  # QAプロンプト
            summary_template=self._get_tree_summarize_prompt_template(),  # TreeSummarizeプロンプト
            response_mode="tree_summarize",
            callback_manager=self._callback_manager,
            use_async=True,
        )

        # DocumentSummaryIndexの準備
        doc_summary_index = self._get_doc_summary_index(
            documents=documents,
            response_synthesizer=response_synthesizer,
            summary_query=SUMMARY_QUERY,  # 要約クエリ
        )

        return doc_summary_index

    def _get_text_qa_prompt_template(self):
        """
        QAプロンプトテンプレートを作成する関数

        Returns:
            CHAT_TEXT_QA_PROMPT (ChatPromptTemplate): QAプロンプトテンプレート
        """
        # QAシステムプロンプト
        TEXT_QA_SYSTEM_PROMPT = ChatMessage(
            content=(
                "あなたは世界中で信頼されているQAシステムです。\n"
                "事前知識ではなく、常に提供されたコンテキスト情報を使用してクエリに回答してください。\n"
                "従うべきいくつかのルール:\n"
                "1. 回答内で指定されたコンテキストを直接参照しないでください。\n"
                "2. 「コンテキストに基づいて、...」や「コンテキスト情報は...」、またはそれに類するような記述は避けてください。"
            ),
            role=MessageRole.SYSTEM,
        )

        # QAプロンプトテンプレートメッセージ
        TEXT_QA_PROMPT_TMPL_MSGS = [
            TEXT_QA_SYSTEM_PROMPT,
            ChatMessage(
                content=(
                    "コンテキスト情報は以下のとおりです。\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "事前知識ではなくコンテキスト情報を考慮して、クエリに答えます。\n"
                    "Query: {query_str}\n"
                    "Answer: "
                ),
                role=MessageRole.USER,
            ),
        ]

        # チャットQAプロンプト
        CHAT_TEXT_QA_PROMPT = ChatPromptTemplate(
            message_templates=TEXT_QA_PROMPT_TMPL_MSGS
        )

        return CHAT_TEXT_QA_PROMPT

    def _get_tree_summarize_prompt_template(self):
        """
        ツリー要約プロンプトテンプレートを作成する関数

        Returns:
            CHAT_TREE_SUMMARIZE_PROMPT (ChatPromptTemplate): ツリー要約プロンプトテンプレート
        """
        # QAシステムプロンプト
        TEXT_QA_SYSTEM_PROMPT = ChatMessage(
            content=(
                "あなたは世界中で信頼されているQAシステムです。\n"
                "事前知識ではなく、常に提供されたコンテキスト情報を使用してクエリに回答してください。\n"
                "従うべきいくつかのルール:\n"
                "1. 回答内で指定されたコンテキストを直接参照しないでください。\n"
                "2. 「コンテキストに基づいて、...」や「コンテキスト情報は...」、またはそれに類するような記述は避けてください。"
            ),
            role=MessageRole.SYSTEM,
        )

        # ツリー要約プロンプトメッセージ
        TREE_SUMMARIZE_PROMPT_TMPL_MSGS = [
            TEXT_QA_SYSTEM_PROMPT,
            ChatMessage(
                content=(
                    "複数のソースからのコンテキスト情報を以下に示します。\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "予備知識ではなく、複数のソースからの情報を考慮して、質問に答えます。\n"
                    "疑問がある場合は、「情報無し」と答えてください。\n"
                    "Query: {query_str}\n"
                    "Answer: "
                ),
                role=MessageRole.USER,
            ),
        ]

        # ツリー要約プロンプト
        CHAT_TREE_SUMMARIZE_PROMPT = ChatPromptTemplate(
            message_templates=TREE_SUMMARIZE_PROMPT_TMPL_MSGS
        )

        return CHAT_TREE_SUMMARIZE_PROMPT

    def _get_doc_summary_index(
        self,
        documents: List[Document],
        response_synthesizer,
        summary_query: str,
    ):
        """
        DocumentSummaryIndexオブジェクトを作成する関数

        Args:
            documents (List[Document]): ドキュメントのリスト
            response_synthesizer: レスポンスシンセサイザー
            summary_query (str): 要約クエリ

        Returns:
            doc_summary_index (DocumentSummaryIndex): DocumentSummaryIndexオブジェクト
        """
        try:
            # DocumentSummaryIndexの準備
            doc_summary_index = DocumentSummaryIndex.from_documents(
                documents=documents,
                storage_context=self._storage_context,
                service_context=self._service_context,
                response_synthesizer=response_synthesizer,
                summary_query=summary_query,  # 要約クエリ
            )
        except (AttributeError, TypeError) as e:
            print(f"Error in _get_doc_summary_index: {e}")
            doc_summary_index = None

        return doc_summary_index

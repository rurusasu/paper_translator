from typing import Any, List, Optional

from langchain.embeddings import HuggingFaceEmbeddings
from llama_index import (
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.prompts import PromptTemplate
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.vector_stores import SimpleVectorStore


class Pipeline:
    def __init__(
        self,
        llm_model,
        embed_name: str = "sentence-transformers/all-MiniLM-l6-v2",
        embed_model: Optional[Any] = None,
        prompt_temp_path: str | None = None,
        is_debug=False,
    ) -> None:
        self.vector_store_index = None

        self.is_debug = is_debug
        self.callback_manager = None

        if is_debug:
            # デバッグの設定
            from llama_index.callbacks import CallbackManager, LlamaDebugHandler

            self._llama_debug_handler = LlamaDebugHandler(
                print_trace_on_end=True
            )
            self.callback_manager = CallbackManager([self._llama_debug_handler])

        # Storage Context の作成
        self._storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            vector_store=SimpleVectorStore(),
            index_store=SimpleIndexStore(),
        )

        # Embeddings の設定
        self._embed_model = embed_model or HuggingFaceEmbeddings(
            model_name=embed_name
        )

        # Service Context の作成
        self._service_context = ServiceContext.from_defaults(
            llm=llm_model,
            embed_model=self._embed_model,
            callback_manager=self.callback_manager,
        )

        if isinstance(prompt_temp_path, str):
            # Prmpt Template の読み込み
            with open(prompt_temp_path, "r") as f:
                self._prompt_template = PromptTemplate(f.read())

    def ReadDocument(
        self,
        docs_dir_path: str,
        required_exts: List[str] = [".pdf", ".txt"],
        recursive: bool = True,
    ) -> List[str]:
        """ドキュメントを読み込む関数

        Args:
            docs_dir_path (str): ドキュメントのディレクトリのパス
            required_exts (List[str], optional): 読み込むドキュメントの拡張子のリスト. Defaults to [".pdf", ".txt"].
            recursive (bool, optional): 再帰的に読み込むかどうか. Defaults to True.
        """
        reader = SimpleDirectoryReader(
            input_dir=docs_dir_path,
            required_exts=required_exts,
            recursive=recursive,
        )
        docs = reader.load_data()

        return docs

    def VectorizeDocuments(self, docs: List[str]) -> None:
        """ドキュメントをベクトル化する関数

        Args:
            docs (List[str]): ドキュメントのリスト
        """
        self.vector_store_index = VectorStoreIndex.from_documents(
            docs,
            storage_context=self._storage_context,
            service_context=self._service_context,
        )
        return self.vector_store_index

    def ReadVectorIndex(self, index_dir_path: str) -> None:
        """ベクトルインデックスを読み込む関数

        Args:
            index_dir_path (str): ベクトルインデックスが保存されたディレクトリへのパス
        """
        self._storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore.from_persist_dir(
                persist_dir=index_dir_path
            ),
            vector_store=SimpleVectorStore.from_persist_dir(
                persist_dir=index_dir_path
            ),
            index_store=SimpleIndexStore.from_persist_dir(
                persist_dir=index_dir_path
            ),
        )
        self.vector_store_index = load_index_from_storage(
            self._storage_context, service_context=self._service_context
        )
        return self.vector_store_index

    def Answer(self, prompt: str) -> str:
        """Promptに答える関数

        Args:
            prompt (str): Prompt

        Returns:
            str: Promptに対する答え
        """
        if self.vector_store_index is None:
            raise ValueError(
                "You need to read documents or vector index before answering."
            )

        query_engine = self.vector_store_index.as_query_engine(
            response_mode="tree_summarize",
            text_qa_template=self._prompt_template,
            service_context=self._service_context,
        )
        answer = query_engine.query(prompt)
        return answer

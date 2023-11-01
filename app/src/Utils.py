from typing import Any, List

import torch
from llama_index import Document
from llama_index.embeddings import HuggingFaceEmbedding

from src.model.llama_cpp import create_llama_cpp_model
from src.translator.llamaindex_summarizer import LlamaIndexSummarizer


def _create_huggingface_embeddings(
    model_name: str, max_length: int = 512, device: torch.device = "cpu"
) -> Any:
    """HuggingFaceEmbeddingsのモデルを作成する関数

    Args:
        model_name (str): モデル名
        max_length (int, optional): 最大トークン数. Defaults to 512.
        device (torch.device, optional): デバイス. Defaults to "cpu".

    Returns:
        embed_model (Any): HuggingFaceEmbeddingsのモデル
    """
    embed_model = HuggingFaceEmbedding(
        model_name=model_name, max_length=max_length, device=device
    )
    return embed_model


def create_doc_summary_index(documents: List[Document], summarizer: Any) -> Any:
    """doc_summary_indexを作成する関数

    Args:
        documents (List[Document]): LlamaIndexのDocumentリスト
        summarizer (Any): llamaindex_summaryzer

    Returns:
        doc_summary_index (Any): doc_summary_index
    """
    doc_summary_index = summarizer.from_documents(documents=documents)
    return doc_summary_index


def get_document_summary(doc_summary_index: Any, i: int) -> str | None:
    """doc_summary_indexから要約を取得する関数

    Args:
        doc_summary_index (Any): doc_summary_index
        i (int): インデックス

    Returns:
        translated_text (str | None): 要約
    """
    print(f"Getting summary of {i}th document")
    try:
        translated_text = doc_summary_index.get_document_summary(f"{i}")
    except ValueError:
        print(f"doc_id: {i} is no text.")
        translated_text = None
    else:
        translated_text = translated_text.split("、", 1)[1::][0]
    return translated_text


def is_conclusion(section: Document) -> bool:
    """section.titleに"conclusion"が含まれるかどうかを判定する関数

    Args:
        section (Document): Documentオブジェクト

    Returns:
        bool: Trueなら含まれる、Falseなら含まれない
    """
    return "conclusion" in section.metadata["Section Title"]


def get_section_title(section: Document) -> str:
    """セクションのタイトルを取得する関数

    Args:
        section (Document): Documentオブジェクト

    Returns:
        title (str): セクションのタイトル
    """
    title = f"### {section.metadata['Section No.']}. {section.metadata['Section Title']}"
    return title


def create_markdown_text(
    documents: List[Document], doc_summary_index: Any
) -> str:
    """Markdownのテキストを作成する関数

    Args:
        documents (List[Document]): LlamaIndexのDocumentリスト
        doc_summary_index (Any): doc_summary_index

    Returns:
        markdown_text (str): Markdownのテキスト
    """
    markdown_text = ""
    for i in range(len(documents)):
        markdown_text += get_section_title(documents[i]) + "\n"
        translated_text = get_document_summary(doc_summary_index, i)
        if translated_text is not None:
            markdown_text += translated_text + "\n\n"

        # if is_conclusion(documents[i]):
        #    break

    return markdown_text


def write_markdown(
    documents: List[Document],
    persist_dir: str | None = None,
    prompt_temp_path: str | None = None,
    device: torch.device = "cpu",
) -> str:
    """Markdownファイルを作成する関数

    Args:
        sections (List[Document]): LlamaIndexのDocumentリスト
        persist_dir: Contextの保存先ディレクトリ
        prompt_temp_path (str | None, optional): プロンプトテンプレートのパス. Defaults to None.
        device (torch.device, optional): デバイス. Defaults to "cpu".

    Returns:
        markdown_text (str): Markdownのテキスト
    """
    # if prompt_temp_path is None:
    #    prompt_temp_path = (
    #        "/home/paper_translator/data/prompt_temp/translate.txt"
    #    )
    llm_model = create_llama_cpp_model(
        package_name="llama_index",
        model_path="/home/paper_translator/data/models/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf",
        temperature=0.1,
    )
    model_name = "sentence-transformers/all-MiniLM-l6-v2"
    embed_model = _create_huggingface_embeddings(
        model_name=model_name, max_length=3072, device=device
    )
    # summarizer = _create_summarizer(llm_model, prompt_temp_path)
    summarizer = LlamaIndexSummarizer(
        llm_model=llm_model,
        embed_model=embed_model,
        persist_dir=persist_dir,
        node_parser="sentence",
        is_debug=False,
    )

    doc_summary_index = create_doc_summary_index(documents, summarizer)

    try:
        markdown_text = create_markdown_text(documents, doc_summary_index)
    except Exception as e:
        print(f"Create markdown error occurred: {e}")
        return ""
    else:
        return markdown_text


if __name__ == "__main__":
    # from src.arXivUtils import get_pdf
    from src.XMLUtils import DocumentReader

    base_path = "/home/paper_translator/data"
    document_name = (
        "FPTQ_Fine-grained_Post-Training_Quantization_for_Large_Language_Models"
    )
    document_path = f"{base_path}/documents/{document_name}"
    xml_path = f"{document_path}/{document_name}.tei.xml"
    # temp_file = "/home/paper_translator/data/prompt_temp/prompt_test.txt"

    documents = DocumentReader().load_data(xml_path=xml_path)
    markdown_text = write_markdown(
        documents=documents,
        # prompt_temp_path=temp_file,
        persist_dir=document_path,
    )
    # デバッグ用にテキストを保存する
    with open(f"{document_path}/tmp_markdown.md", mode="w") as f:
        f.write(markdown_text)

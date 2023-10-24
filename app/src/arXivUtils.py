import datetime as dt
import os
from typing import Dict, List, Tuple
from urllib.error import HTTPError

import arxiv

from src.Informations import arXivInfoDict

# 興味があるカテゴリー群
CATEGORIES = [
    "cs.AI",
    "cs.CV",
    # ...
]

# pdfの保存先
base_dir = "./data"
document_dir = base_dir + "/documents"


def _generate_query(keyword: str, n_days: int) -> str:
    """
    検索クエリを生成する関数

    Args:
        keyword (str): 検索キーワード
        n_days (int): 検索する日数

    Returns:
        query (str): 検索クエリ
    """
    QUERY_TEMPLATE = (
        "%28 ti:%22{}%22 OR abs:%22{}%22 %29 AND submittedDate: [{} TO {}]"
    )

    try:
        today = dt.datetime.today()
        base_date = today - dt.timedelta(days=n_days)
        query = QUERY_TEMPLATE.format(
            keyword,
            keyword,
            base_date.strftime("%Y%m%d%H%M%S"),
            today.strftime("%Y%m%d%H%M%S"),
        )
        return query
    except Exception as e:
        # エラーが発生した場合は、空の文字列を返す
        print(f"Error in generate_query: {e}")
        return ""


def _search_arxiv(query: str, max_result: int) -> arxiv.Search:
    """
    arXiv APIを使って，論文情報を検索する関数

    Args:
        query (str): 検索クエリ
        max_result (int): 取得する論文数の上限

    Returns:
        search (arxiv.Search): 検索結果
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_result,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        return search
    except Exception as e:
        # エラーが発生した場合は、Noneを返す
        print(f"Error in search_arxiv: {e}")
        return None


def create_paper_info(paper: arxiv.Result) -> Dict[str, str]:
    """
    arXiv APIの検索結果から，論文情報の辞書を作成する関数

    Args:
        paper (arxiv.Result): 検索結果

    Returns:
        result (Dict[str, str]): 論文情報の辞書
    """
    try:
        result = arXivInfoDict.copy()
        result["Title"] = paper.title
        result["Entry_id"] = paper.entry_id
        result["Authors"] = paper.authors
        result["Summary"] = paper.summary
        result["Pdf_url"] = paper.pdf_url
        result["Published"] = paper.published
        result["Updated"] = paper.updated
    except Exception as e:
        # エラーが発生した場合は、空の辞書を返す
        print(f"Error in create_paper_info: {e}")
        return dict()
    else:
        return result


def _create_paper_list(
    search: arxiv.Search, categories: List[str] = CATEGORIES
) -> List[Dict[str, str]]:
    """
    arXiv APIの検索結果から，論文情報のリストを作成する関数

    Args:
        search (arxiv.Search): 検索結果
        categories (list): カテゴリーのリスト

    Returns:
        result_list (List[Dict[str, str]]): 論文情報のリスト
    """
    try:
        result_list = []
        for paper in search.results():
            if len((set(paper.categories) & set(categories))) == 0:
                continue
            else:
                paper_info = create_paper_info(paper)
                result_list.append(paper_info)
    except Exception as e:
        # エラーが発生した場合は、空のリストを返す
        print(f"Error in create_paper_list: {e}")
        return []
    else:
        return result_list


def _get_paper_info_from_arxiv(
    query: str, max_result: int, categories: List[str] = CATEGORIES
) -> List[Dict[str, str]]:
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        query (str): 検索クエリ
        max_result (int): 取得する論文数の上限
        categories (list): カテゴリーのリスト

    Returns:
        result_list (List[Dict[str, str]]): 論文情報のリスト
    """
    # 検索クエリを生成
    query = _generate_query(query, n_days=7)

    # arXiv APIを使って，論文情報を検索
    search = _search_arxiv(query, max_result)
    if search is None:
        return []

    # 検索結果から，カテゴリーに含まれる論文情報のリストを作成
    result_list = _create_paper_list(search, categories)

    return result_list


def get_paper_info(
    keyword: str,
    categories: List[str] = CATEGORIES,
    n_days: int = 7,
    max_result: int = 20,
) -> List[Dict[str, str]]:
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        keyword (str): 検索キーワード
        categories (list): カテゴリーのリスト
        n_days (int): 検索する日数
        max_result (int): 取得する論文数の上限

    Returns:
        result_list (List[Dict[str, str]]): 論文情報のリスト
    """
    try:
        # 引数の例外処理
        if not isinstance(keyword, str):
            raise TypeError("keyword must be str")
        if not isinstance(categories, list):
            raise TypeError("categories must be list")
        if not isinstance(n_days, int):
            raise TypeError("n_days must be int")
        if not isinstance(max_result, int):
            raise TypeError("max_result must be int")

        # 検索キーワードが空の場合は、空のリストを返す
        if not keyword:
            return []

        # arXiv APIを使って，論文情報を取得
        result_list = _get_paper_info_from_arxiv(
            keyword, max_result, categories
        )

        return result_list

    except Exception as e:
        # エラーが発生した場合は、空のリストを返す
        print(f"Error in get_paper_info: {e}")
        return []


def get_paper_by_id(entry_id: str) -> arxiv.Result:
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        entry_id (str): 論文のID

    Returns:
        paper (arxiv.Result): 論文情報
    """
    try:
        # 引数の例外処理
        if not isinstance(entry_id, str):
            raise TypeError("entry_id must be str")

        entry_id = entry_id.split("/")[-1]
        if entry_id[-1] == ">":
            entry_id = entry_id[:-1]

        paper = next(arxiv.Search(id_list=[entry_id]).results())
    except Exception as e:
        # エラーが発生した場合は、Noneを返す
        print(f"Error in get_paper_info_by_id: {e}")
        paper = None

    return paper


def download_pdf(
    paper: arxiv.Result, document_root_dir_path: str
) -> Tuple[str, str, str]:
    """
    arXiv APIを使って，論文のPDFを取得する関数

    Args:
        paper (arxiv.Result): 論文情報
        document_root_dir_path (str): PDFを保存する親ディレクトリのパス

    Returns:
        dir_path (str): PDFを保存したディレクトリのパス
        pdf_path (str): PDFのパス
        pdf_name (str): PDFのファイル名
    """
    try:
        # 引数の例外処理
        if not isinstance(paper, arxiv.Result):
            raise TypeError("paper must be arxiv.Result")
        if not isinstance(document_root_dir_path, str):
            raise TypeError("document_root_dir_path must be str")

        dir_name = (
            paper.title.replace(" ", "_")
            .replace(":", "")
            .replace(",", "")
            .replace("/", "")
            .replace("\\", "")
            .replace("(", "")
            .replace(")", "")
        )
        dir_path = f"{document_root_dir_path}/{dir_name}/"

        pdf_name = f"{dir_name}"
        os.makedirs(dir_path, exist_ok=True)
        # 論文のURLからPDFを取得
        cnt = 0
        while True:
            try:
                print(f"Downloading {pdf_name}...")
                pdf_path = paper.download_pdf(
                    dirpath=dir_path, filename=pdf_name + ".pdf"
                )
            except HTTPError as e:
                print(e)
                cnt += 1
                if cnt == 3:
                    raise e
            else:
                print("Downloaded!")
                break

    except Exception as e:
        # エラーが発生した場合は、Noneを返す
        print(f"Error in download_pdf: {e}")
        return None, None, None
    else:
        print("Completed!")
        return dir_path, pdf_path, pdf_name


if __name__ == "__main__":
    keyword = "model"  # 検索キーワード
    CATEGORIES = [
        "cs.AI",
        "cs.CV",
        # ...
    ]
    result_list = get_paper_info(
        keyword, categories=CATEGORIES, n_days=14, max_result=10
    )
    if len(result_list) != 0:
        print(f"# Title: \n{result_list[0]['Title']}")
        print(f"# Summary: \n{result_list[0]['Summary']}")
        print(f"# entry_id: \n{result_list[0]['Entry_id']}")
        print(f"# pdf_url: \n{result_list[0]['Pdf_url']}")
        print(f"# published: \n{result_list[0]['Published']}")

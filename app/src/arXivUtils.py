import datetime as dt
import os
from typing import Tuple
from urllib.error import HTTPError

import arxiv

# arXiv APIの設定
N_DAYS = 14  # 何日前からの論文を検索するか
MAX_RESULT = 10  # 取得する論文数の上限

# Query テンプレートを作成
# テンプレートを用意
QUERY_TEMPLATE = (
    "%28 ti:%22{}%22 OR abs:%22{}%22 %29 AND submittedDate: [{} TO {}]"
)

# 興味があるカテゴリー群
CATEGORIES = {
    "cs.AI",
    ...,
}

# pdfの保存先
base_dir = "./data"
document_dir = base_dir + "/documents"


def generate_query(keyword: str, n_days: int) -> str:
    """
    検索クエリを生成する関数

    Args:
        keyword (str): 検索キーワード
        n_days (int): 検索する日数

    Returns:
        query (str): 検索クエリ
    """
    try:
        today = dt.datetime.today() - dt.timedelta(days=n_days)
        base_date = today - dt.timedelta(days=n_days)
        query = f"{keyword} AND submittedDate:[{base_date.strftime('%Y%m%d%H%M%S')} TO {today.strftime('%Y%m%d%H%M%S')}]"
        return query
    except Exception as e:
        # エラーが発生した場合は、空の文字列を返す
        print(f"Error in generate_query: {e}")
        return ""


def search_arxiv(query: str, max_result: int) -> arxiv.Search:
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


def create_paper_list(search: arxiv.Search, categories: List[str]) -> List:
    """
    arXiv APIの検索結果から，論文情報のリストを作成する関数

    Args:
        search (arxiv.Search): 検索結果
        categories (list): カテゴリーのリスト

    Returns:
        result_list (list): 論文情報のリスト
    """
    try:
        result_list = []
        for paper in search.results():
            if len((set(paper.categories) & set(categories))) == 0:
                continue
            else:
                result_list.append({
                    "title": paper.title,
                    "authors": paper.authors,
                    "summary": paper.summary,
                    "pdf_url": paper.pdf_url,
                    "published": paper.published,
                    "updated": paper.updated,
                })
        return result_list
    except Exception as e:
        # エラーが発生した場合は、空のリストを返す
        print(f"Error in create_paper_list: {e}")
        return []


def get_paper_info_from_arxiv(query: str, max_result: int, categories: List[str]) -> List:
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        query (str): 検索クエリ
        max_result (int): 取得する論文数の上限
        categories (list): カテゴリーのリスト

    Returns:
        result_list (list): 論文情報のリスト
    """
    # arXiv APIを使って，論文情報を検索
    search = search_arxiv(query, max_result)
    if search is None:
        return []

    # 検索結果から，カテゴリーに含まれる論文情報のリストを作成
    result_list = create_paper_list(search, categories)

    return result_list


def get_paper_info(keyword: str, categories: List[str], n_days: int = 7, max_result: int = 10) -> List:
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        keyword (str): 検索キーワード
        categories (list): カテゴリーのリスト
        n_days (int): 検索する日数
        max_result (int): 取得する論文数の上限

    Returns:
        result_list (list): 論文情報のリスト
    """
    # 検索クエリを生成
    query = generate_query(keyword, n_days)

    # arXiv APIを使って，論文情報を取得
    result_list = get_paper_info_from_arxiv(query, max_result, categories)

    return result_list


def get_paper_info_by_id(entry_id: str) -> arxiv.Result:
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        entry_id (str): 論文のID

    Returns:
        paper (arxiv.Result): 論文情報
    """
    entry_id = entry_id.split("/")[-1]
    if entry_id[-1] == ">":
        entry_id = entry_id[:-1]

    try:
        paper = next(arxiv.Search(id_list=[entry_id]).results())
    except Exception as e:
        # エラーが発生した場合は、Noneを返す
        print(f"Error in get_paper_info_by_id: {e}")
        paper = None

    return paper


def download_pdf(entry_id: str, document_dir: str) -> tuple:
    """
    arXiv APIを使って，論文のPDFを取得する関数

    Args:
        entry_id (str): 論文のID
        document_dir (str): PDFを保存するディレクトリのパス

    Returns:
        dir_path (str): PDFを保存したディレクトリのパス
        pdf_path (str): PDFのパス
        pdf_name (str): PDFのファイル名
    """
    try:
        paper = get_paper_info_by_id(entry_id)

        dir_name = paper.title.replace(" ", "_").replace(":", "").replace(",", "")
        dir_path = f"{document_dir}/{dir_name}/"

        pdf_name = f"{dir_name}"
        os.makedirs(dir_path, exist_ok=True)
        # 論文のURLからPDFを取得
        cnt = 0
        while True:
            try:
                pdf_path = paper.download_pdf(
                    dirpath=dir_path, filename=pdf_name + ".pdf"
                )
                break
            except HTTPError as e:
                print(e)
                cnt += 1
                if cnt == 3:
                    raise e

        return dir_path, pdf_path, pdf_name
    except Exception as e:
        # エラーが発生した場合は、Noneを返す
        print(f"Error in download_pdf: {e}")
        return None, None, None


if __name__ == "__main__":
    keyword = "GAN"  # 検索キーワード
    result_list = get_paper_info(keyword, is_debug=True)
    print(result_list[0].title)
    print(result_list[0].summary)
    print(result_list[0].entry_id)
    print(result_list[0].pdf_url)
    # print(result_list[0].published)
    # print(result_list[0].authors)
    # print(result_list[0].categories)
    # print(result_list[0].doi)
    # print(result_list[0].journal_ref)
    # print(result_list[0].comment)
    get_pdf(result_list[0].entry_id)

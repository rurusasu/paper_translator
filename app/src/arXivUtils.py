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


def get_paper_info(keyword: str, is_debug: bool = False):
    """
    arXiv APIを使って，論文情報を取得する関数

    Args:
        keyword (str): 検索キーワード
        is_debug (bool): デバッグモードのフラグ

    Returns:
        result_list (list): 論文情報のリスト
    """
    # arXivの更新頻度を加味して，1週間前の論文を検索
    today = dt.datetime.today() - dt.timedelta(days=7)
    base_date = today - dt.timedelta(days=N_DAYS)
    query = QUERY_TEMPLATE.format(
        keyword,
        keyword,
        base_date.strftime("%Y%m%d%H%M%S"),
        today.strftime("%Y%m%d%H%M%S"),
    )

    # arXiv APIを使って，論文情報を取得
    search = arxiv.Search(
        query=query,  # 検索クエリ
        max_results=MAX_RESULT * 3,  # 取得する論文数の上限
        sort_by=arxiv.SortCriterion.SubmittedDate,  # 論文を投稿された日付でソートする
        sort_order=arxiv.SortOrder.Descending,  # 新しい論文から順に取得する
    )

    # searchの結果をリストに格納
    result_list = []
    for result in search.results():
        # カテゴリーに含まれない論文は除く
        if len((set(result.categories) & CATEGORIES)) == 0:
            continue

        if is_debug:
            print(result.title)
            print(result.summary)
        result_list.append(result)

        # 最大件数に到達した場合は，そこで打ち止め
        if len(result_list) == MAX_RESULT:
            break

    return result_list[:MAX_RESULT]


def get_paper_info_by_id(entry_id: str) -> arxiv.Result:
    """arXiv APIを使って，論文情報を取得する関数

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
        print(e)
        paper = None

    return paper


def get_pdf(entry_id: str) -> Tuple[str, str]:
    """arXiv APIを使って，論文のPDFを取得する関数

    Args:
        entry_id (str): 論文のID
    Returns:
        dir_path (str): PDFを保存したディレクトリのパス
        pdf_path (str): PDFのパス
        pdf_name (str): PDFのファイル名
    """
    paper = get_paper_info_by_id(entry_id)

    dir_name = paper.title.replace(" ", "_").replace(":", "").replace(",", "")
    dir_path = f"./data/{dir_name}/"

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

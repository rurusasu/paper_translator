import time
from typing import List

from src.arXivUtils import get_paper_info
from src.OpenAIUtils import get_message
from src.SlackUtils import write_message

SLACK_CHANNENL = "勉強"


def write_summary(channel_id: str, keyword: str, result_list: List[str]):
    """
    スレッドに要約を書き込む関数

    Args:
        channel_id (str): チャンネルID
        thread_ts (str): スレッドのタイムスタンプ
        summary (str): 要約
    """
    # 論文が見つからなかった場合
    if len(result_list) == 0:
        message = f"{'=' *40} \n {keyword}に関する論文は有りませんでした。 \n{'=' *40}"
        write_message(channel_id, message)

    else:
        # 要約をスレッドに書き込む
        # 初期メッセージ
        message = f"{'=' *40} \n {keyword}に関する論文は{len(result_list)}本ありました！ \n{'=' *40}"
        write_message(channel_id, message)

        # 論文情報をSlackに送信する
        for i, result in enumerate(result_list, start=1):
            text = f"title: {result.title}\nbody: {result.summary}"

            # ChatGPTに論文の概要を要約してもらう
            response = get_message(text)
            title_en = result.title
            # pdf_url = result.pdf_url
            entry_id = result.entry_id
            title, *body = response.split("\n")
            body = "\n".join(body)
            date_str = result.published.strftime("%Y-%m-%d %H:%M:%S")

            message = (
                f"{keyword}: {i}本目\n"
                f"{'=' *40}\n"
                f"発行日: {date_str}\n"
                f"{entry_id}\n"
                f"{title} ({title_en})\n"
                f"{body}\n"
                f"{'=' *40}"
            )
            write_message(channel_id, message)
            time.sleep(10)
    return


if __name__ == "__main__":
    keyword_list = [
        "LLM",
        "diffusion",
    ]

    for keyword in keyword_list:
        result_list = get_paper_info(keyword)
        write_summary(
            channel_id=SLACK_CHANNENL, keyword=keyword, result_list=result_list
        )

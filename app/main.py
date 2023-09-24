import time
from typing import List

import arxiv

from src.OpenAIUtils import get_message
from src.SlackUtils import write_message

SLACK_CHANNENL = "勉強"


def write_summary(
    channel_id: str, keyword: str, result_list: List[arxiv.Result]
) -> None:
    """
    スレッドに要約を書き込む関数

    Args:
        channel_id (str): チャンネルID
        keyword (str): 検索キーワード
        result_list (List[arxiv.Result]): 論文のリスト
    """
    # Slackへのメッセージの送信に成功したかどうかを表すフラグ
    write_message_flag = False

    if not result_list:
        # 論文が見つからなかった場合
        message = f"{'=' * 40}\n{keyword}に関する論文はありませんでした。\n{'=' * 40}"
        write_message_flag = write_message(channel_id, message)
        if not write_message_flag:
            print("Slackへのメッセージの送信に失敗しました")
            return
        return

    # 論文が見つかった場合
    message = (
        f"{'=' * 40}\n{keyword}に関する論文は{len(result_list)}本ありました！\n{'=' * 40}"
    )
    write_message_flag = write_message(channel_id, message)
    if not write_message_flag:
        print("Slackへのメッセージの送信に失敗しました")
        return

    # 論文情報をSlackに送信する
    for i, paper in enumerate(result_list, start=1):
        try:
            text = f"title: {paper['title']}\nbody: {paper['summary']}"

            # ChatGPTに論文の概要を要約してもらう
            response = get_message(text)
            title_ja, *body = response.split("\n")
            body = "\n".join(body)

            message = (
                f"{'=' *40}\n"
                f"{keyword}: {i}本目\n"
                f"{'=' *40}\n"
                f"発行日: {paper['published']}\n"
                f"{paper['entry_id']}\n"
                f"{title_ja} ({paper['title']})\n"
                f"{body}\n"
                f"{'=' *40}"
            )
            write_message_flag = write_message(channel_id, message)
            if not write_message_flag:
                print("Slackへのメッセージの送信に失敗しました")
                return
            time.sleep(10)

        except Exception as e:
            # 論文の要約に失敗した場合
            print(f"論文の要約に失敗しました: {e}")
            continue
    return


if __name__ == "__main__":
    import os

    from slack_bolt.adapter.socket_mode import SocketModeHandler

    from src.arXivUtils import get_paper_info
    from src.SlackUtils import app

    keyword_list = [
        "LLM",
        "diffusion",
    ]

    for keyword in keyword_list:
        result_list = get_paper_info(keyword)
        write_summary(
            channel_id=SLACK_CHANNENL, keyword=keyword, result_list=result_list
        )

    # アプリを起動します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

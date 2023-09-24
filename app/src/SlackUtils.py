import os
from typing import List

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from src.arXivUtils import get_pdf
from src.SaveToNotion import save_to_notion_page
from src.Utils import write_markdown
from src.XMLUtils import get_sections, make_xml_file

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ["SLACK_BOT_TOKEN"])


def get_thread_messages(channel_id: str, thread_ts: List[str]) -> List[dict]:
    try:
        result = app.client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=1000
        )
    except SlackApiError as e:
        print(f"Error getting thread messages: {e}")
        return None

    thread_messages = result["messages"]
    return thread_messages


@app.event("app_mention")
def handle_mention_events_and_get_entryID(body, logger, say):
    """
    指定したチャンネルのスレッドを取得する関数

    Args:
        channel_id (str): チャンネルID
        thread_ts (str): スレッドのタイムスタンプ

    Returns:
        thread_messages (list): スレッドのメッセージ
    """
    logger.info(body)
    bot_user_id = body["authorizations"][0]["user_id"]
    text = body["event"]["text"]
    user = body["event"]["user"]

    channel_id = body["event"]["channel"]
    if "thread_ts" in body["event"].keys():
        thread_ts = body["event"]["thread_ts"]
        thread_messages = get_thread_messages(channel_id, thread_ts)
    else:
        thread_ts = body["event"]["ts"]
        thread_messages = [body["event"]]

    text = text.replace(f"<@{bot_user_id}>", "").strip()
    # デバック用
    if text == "ping":
        say(text=f"<@{user}> pong :robot_face:", thread_ts=thread_ts)
        return None

    else:
        # pdfファイルを取得
        thread_text = thread_messages[0]["text"]
        entry_id = thread_text.split("\n")[3]
        dir_path, _, pdf_name = get_pdf(entry_id)

        # セクションを分割して、要約した文章を生成
        root = make_xml_file(dir_path=dir_path, pdf_name=pdf_name)
        sections = get_sections(root=root)
        markdown_text = write_markdown(sections=sections, pdf_name=pdf_name)

        # for debug
        # ここでtext類を保存する
        with open(f"{dir_path}/tmp_text.txt", mode="w") as f:
            f.write(thread_text)
        with open(f"{dir_path}/tmp_markdown.md", mode="w") as f:
            f.write(markdown_text)

        with open(f"{dir_path}/tmp_text.txt", mode="r") as f:
            thread_text = f.read()
        with open(f"{dir_path}/tmp_markdown.md", mode="r") as f:
            markdown_text = f.read()

        # Notionにページを作成し、要約を書き込む
        save_to_notion_page(markdown_text=markdown_text, entry_id=entry_id)

        # Slackに要約を書き込む
        say(
            text=f"<@{user}> 要約が完了しました :robot_face:",
            thread_ts=thread_ts,
        )


def write_message(channnel_id: str, message: str):
    """
    メッセージを書き込む関数

    Args:
        message (str): 書き込むメッセージ

    Returns:
        completed_flag (bool): 書き込みが正常に終了したか
    """
    completed_flag = False
    try:
        app.client.chat_postMessage(
            channel=channnel_id,
            text=message,
        )
    except SlackApiError as e:
        print(f"Error writing message: {e}")
        return completed_flag

    completed_flag = True
    return completed_flag


if __name__ == "__main__":
    # アプリを起動します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

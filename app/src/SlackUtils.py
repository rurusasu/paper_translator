import os
from typing import Any, Dict, List

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from src.arXivUtils import create_paper_info, download_pdf, get_paper_by_id
from src.SaveToNotion import write_markdown_to_notion
from src.Utils import write_markdown
from src.XMLUtils import DocumentCreator, run_grobid

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ["SLACK_BOT_TOKEN"])


def get_thread_messages(channel_id: str, thread_ts: List[str]) -> List[dict]:
    """
    指定したチャンネルのスレッドを取得する関数

    Args:
        channel_id (str): チャンネルID
        thread_ts (List[str]): スレッドのタイムスタンプ

    Returns:
        thread_messages (List[dict]): スレッドのメッセージ
    """
    try:
        result = app.client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=1000
        )
        thread_messages = result["messages"]
        return thread_messages
    except SlackApiError as e:
        # Slack APIエラーが発生した場合は、エラーメッセージを表示してNoneを返す
        print(f"Error getting thread messages: {e}")
        return None


def get_entry_id_from_thread_text(thread_text: str) -> str:
    """
    スレッドのテキストからエントリーIDを取得する関数

    Args:
        thread_text (str): スレッドのテキスト

    Returns:
        entry_id (str): エントリーID
    """
    entry_id = thread_text.split("\n")[4]
    if entry_id[0] == "<":
        entry_id = entry_id[1:]
    if entry_id[-1] == ">":
        entry_id = entry_id[:-1]
    return entry_id


def get_summary_markdown_text(
    dir_path: str, pdf_name: str, pdf_info: Dict[str, str]
) -> Dict[str, Any]:
    """
    PDFファイルから要約したマークダウンテキストを生成する関数

    Args:
        dir_path (str): PDFファイルのディレクトリパス
        pdf_name (str): PDFファイル名
        pdf_info (Any): 論文情報

    Returns:
        markdown_text (Dict[str: Any]): 要約したマークダウンテキストと論文情報を含んだ辞書。
    """
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        # dir_path is a valid directory path
        pass
    else:
        # dir_path is not a valid directory path
        pass
    run_grobid(dir_path)
    xml_path = dir_path + pdf_name + ".tei.xml"
    creator = DocumentCreator()
    creator.load_xml(xml_path)
    # pdf_info = reader.pdf_info
    creator.input_pdf_info(pdf_info)
    docs = creator.create_docs()
    doc_info = creator.get_doc_info()
    markdown_text = write_markdown(documents=docs)

    # デバッグ用にテキストを保存する
    with open(f"{dir_path}/tmp_markdown.md", mode="w") as f:
        f.write(markdown_text)

    return {"markdown_text": markdown_text, "doc_info": doc_info}


def process_ping_request(user: str, thread_ts: str, say) -> None:
    """
    pingリクエストを処理する関数

    Args:
        user (str): ユーザーID
        thread_ts (str): スレッドのタイムスタンプ
        say (function): botの発言を行う関数
    """
    say(
        text=f"<@{user}> pong :robot_face:",
        thread_ts=thread_ts,
    )


def process_pdf_request(
    thread_message: dict, user: str, thread_ts: str, say
) -> None:
    """
    PDFファイルの要約を作成する関数

    Args:
        thread_message (dict): スレッドのメッセージ
        user (str): ユーザーID
        thread_ts (str): スレッドのタイムスタンプ
        say (function): botの発言を行う関数
    """
    # PDFファイルを保存するディレクトリのパスを取得する
    document_dir_path = os.getenv("DOCUMENT_DIR")

    thread_text = thread_message["text"]
    entry_id = get_entry_id_from_thread_text(thread_text)
    paper = get_paper_by_id(entry_id)
    dir_path, _, pdf_name = download_pdf(paper, document_dir_path)
    pdf_info = create_paper_info(paper)

    # 要約したマークダウンテキストを生成する
    summary = get_summary_markdown_text(
        dir_path=dir_path, pdf_name=pdf_name, pdf_info=pdf_info
    )
    markdown_text = summary["markdown_text"]
    doc_info = summary["doc_info"]

    # Notionにページを作成し、要約を書き込む
    write_markdown_to_notion(markdown_text=markdown_text, doc_info=doc_info)

    # Slackに要約を書き込む
    say(
        text=f"<@{user}> 要約が完了しました :robot_face:",
        thread_ts=thread_ts,
    )


def process_thread_message(
    message: str, thread_message: dict, user: str, thread_ts: str, say
) -> None:
    """
    スレッドのメッセージを処理する関数

    Args:
        message (str): ユーザーからの入力
        thread_message (dict): スレッドのメッセージ
        user (str): ユーザーID
        thread_ts (str): スレッドのタイムスタンプ
        say (function): botの発言を行う関数
    """
    if "subtype" in thread_message.keys():
        # subtypeがある場合は、処理をスキップする
        return None

    if "要約" in message:
        # 要約を作成する
        process_pdf_request(thread_message, user, thread_ts, say)
    elif "pdf" in message:
        # pdfファイルを取得する
        process_pdf_request(thread_message, user, thread_ts, say)
    elif "ping" in message:
        # pingリクエストを処理する
        process_ping_request(user, thread_ts, say)
    else:
        # それ以外の場合は、エラーメッセージを返す
        say("不正なメッセージが送信されました。", thread_ts=thread_ts)


@app.event("app_mention")
def process_mention_event(body, logger, say):
    """
    app_mentionイベントを処理する関数

    Args:
        body (dict): イベントの情報
        logger (Logger): ロガー
        say (function): botの発言を行う関数
    """
    logger.info(body)
    user = body["event"]["user"]
    channel_id = body["event"]["channel"]
    if "thread_ts" in body["event"].keys():
        thread_ts = body["event"]["thread_ts"]
        thread_messages = get_thread_messages(channel_id, thread_ts)
    else:
        thread_ts = body["event"]["ts"]
        thread_messages = [body["event"]]

    if thread_messages is None:
        # スレッドのメッセージが取得できなかった場合は、エラーメッセージを返す
        say("スレッドのメッセージを取得できませんでした。", thread_ts=thread_ts)
        return None

    bot_user_id = body["authorizations"][0]["user_id"]
    message = body["event"]["text"]
    message = message.replace(f"<@{bot_user_id}>", "").strip()

    thread_message = thread_messages[0]
    process_thread_message(message, thread_message, user, thread_ts, say)


def write_message(channel_id: str, message: str) -> bool:
    """
    Slackにメッセージを書き込む関数

    Args:
        channel_id (str): チャンネルID
        message (str): 書き込むメッセージ

    Returns:
        completed_flag (bool): 書き込みが正常に終了したか
    """
    completed_flag = False
    try:
        app.client.chat_postMessage(
            channel=channel_id,
            text=message,
        )
        completed_flag = True
    except SlackApiError as e:
        # Slack APIエラーが発生した場合は、エラーメッセージを表示してFalseを返す
        print(f"Error writing message: {e}")
    return completed_flag


if __name__ == "__main__":
    # アプリを起動します
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

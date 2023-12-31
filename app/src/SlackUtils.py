import os
import shutil
from typing import Any, Dict, List, Tuple

import torch
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
        thread_messages = _get_thread_messages(channel_id, thread_ts)
        return thread_messages
    except SlackApiError as e:
        # Slack APIエラーが発生した場合は、エラーメッセージを表示してNoneを返す
        print(f"Error getting thread messages: {e}")
        return None


def _get_thread_messages(channel_id: str, thread_ts: List[str]) -> List[dict]:
    """スレッドのメッセージを取得する関数

    Args:
        channel_id (str): チャンネルID
        thread_ts (List[str]): スレッドのタイムスタンプ

    Returns:
        thread_messages (List[dict]): スレッドのメッセージ
    """
    result = app.client.conversations_replies(
        channel=channel_id, ts=thread_ts, limit=1000
    )
    thread_messages = result["messages"]
    return thread_messages


def get_entry_id_from_thread_text(thread_text: str) -> str:
    """
    スレッドのテキストからエントリーIDを取得する関数

    Args:
        thread_text (str): スレッドのテキスト

    Returns:
        entry_id (str): エントリーID
    """
    try:
        # スレッドのテキストを改行文字で分割する
        entry_id = _split_thread_text(thread_text)
        if len(entry_id) == 1:
            entry_id = entry_id[0]
        elif len(entry_id) >= 4:
            entry_id = entry_id[4]
        if entry_id[0] == "<":
            entry_id = entry_id[1:]
        if entry_id[-1] == ">":
            entry_id = entry_id[:-1]
        return entry_id
    except (IndexError, TypeError) as e:
        # エラーが発生した場合は、エラーメッセージを表示して空の文字列を返す
        print(f"Error getting entry ID from thread text: {e}")
        return ""


def _split_thread_text(thread_text: str) -> List[str]:
    """スレッドのテキストを改行文字で分割する関数

    Args:
        thread_text (str): スレッドのテキスト

    Returns:
        thread_text_list (List[str]): スレッドのテキストを改行文字で分割したリスト
    """
    thread_text_list = []
    if thread_text is None:
        return thread_text_list
    thread_text_list = thread_text.split("\n")
    return thread_text_list


class PDFProcessor:
    def __init__(self, dir_path: str, pdf_name: str, pdf_info: Dict[str, str]):
        self.dir_path = dir_path
        self.pdf_name = pdf_name
        self.pdf_info = pdf_info
        self.device = self._get_device()
        self.creator = DocumentCreator()

    def _get_device(self):
        return "cuda:0" if torch.cuda.is_available() else "cpu"

    def _load_xml(self, xml_path: str):
        err_flag = self.creator.load_xml(xml_path, contain_abst=False)
        if err_flag:
            raise Exception("Error loading xml.")

    def _create_docs(self):
        docs = self.creator.create_docs()
        if len(docs) == 0:
            raise Exception("Error creating docs.")
        return docs

    def get_summary_markdown_text(self) -> Dict[str, Any]:
        try:
            self._is_valid_dir_path(self.dir_path)
            self.dir_path = run_grobid(self.dir_path)
            if self.dir_path is None:
                return self._handle_error("Error running Grobid.")
            xml_path = self.dir_path + self.pdf_name + ".tei.xml"
            self._load_xml(xml_path)
            self.creator.input_pdf_info(self.pdf_info)
            docs = self._create_docs()
            doc_info = self.creator.get_doc_info()
            markdown_text = write_markdown(
                documents=docs,
                device=self.device,
                package_name="llama_index",
                temperature=0.0,
                context_window=4096,
                max_tokens=4096,
            )
            with open(f"{self.dir_path}/tmp_markdown.md", mode="w") as f:
                f.write(markdown_text)
            return {"markdown_text": markdown_text, "doc_info": doc_info}
        except Exception as e:
            return self._handle_error(str(e))

    @staticmethod
    def _is_valid_dir_path(dir_path: str) -> None:
        if not os.path.exists(dir_path):
            raise ValueError("Directory path does not exist.")
        if not os.path.isdir(dir_path):
            raise ValueError(
                "File path is specified instead of directory path."
            )

    @staticmethod
    def _handle_error(error_message: str):
        print(f"Error: {error_message}")
        return {}


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
) -> bool:
    """
    PDFファイルの要約を作成する関数
    Args:
        thread_message (dict): スレッドのメッセージ
        user (str): ユーザーID
        thread_ts (str): スレッドのタイムスタンプ
        say (function): botの発言を行う関数
    """
    try:
        document_dir_path = _get_document_dir_path()
        entry_id = _get_entry_id(thread_message)
        paper = _get_paper(entry_id)
        pdf_info = _create_pdf_info(paper)
        dir_path, pdf_name = _download_pdf(paper, document_dir_path)
        pdf_processor = PDFProcessor(dir_path, pdf_name, pdf_info)
        summary = pdf_processor.get_summary_markdown_text()
        write_markdown_to_notion(summary["markdown_text"], summary["doc_info"])
        _say_summary_complete(user, thread_ts, say)
        _remove_pdf(dir_path)
        return False
    except Exception as e:
        _handle_error_output_slack(e, thread_ts, say)
        return True


def _get_document_dir_path() -> str:
    """
    PDFファイルを保存するディレクトリのパスを取得する関数
    """
    document_dir_path = os.getenv("DOCUMENT_DIR")
    if not document_dir_path:
        raise ValueError("DOCUMENT_DIRが設定されていません。")
    return document_dir_path


def _get_entry_id(thread_message: dict) -> str:
    """
    スレッドメッセージから論文IDを取得する関数
    """
    thread_text = thread_message["text"]
    entry_id = get_entry_id_from_thread_text(thread_text)
    if not entry_id:
        raise ValueError("論文IDを取得できませんでした。")
    return entry_id


def _get_paper(entry_id: str) -> dict:
    """
    論文情報を取得する関数
    """
    paper = get_paper_by_id(entry_id)
    if not paper:
        raise ValueError("論文情報を取得できませんでした。")
    return paper


def _create_pdf_info(paper: dict) -> dict:
    """
    PDFファイルの情報を作成する関数
    """
    pdf_info = create_paper_info(paper)
    if not pdf_info:
        raise ValueError("PDFファイルの情報を作成できませんでした。")
    return pdf_info


def _download_pdf(paper: dict, document_dir_path: str) -> Tuple[str, str]:
    """
    PDFファイルをダウンロードする関数
    """
    dir_path, _, pdf_name = download_pdf(paper, document_dir_path)
    if not dir_path or not pdf_name:
        raise ValueError("PDFファイルをダウンロードできませんでした。")
    return dir_path, pdf_name


def _say_summary_complete(user: str, thread_ts: str, say) -> None:
    """
    Slackに要約を書き込む関数
    """
    say(text=f"<@{user}> 要約が完了しました :robot_face:", thread_ts=thread_ts)
    return None


def _remove_pdf(dir_path: str) -> None:
    """
    ダウンロードしたPDFファイルを削除する関数
    """
    if isinstance(dir_path, str) and os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    return None


def _handle_error_output_slack(e: Exception, thread_ts: str, say) -> None:
    """
    エラーを処理する関数
    """
    say(f"Error: {e}", thread_ts=thread_ts)
    return None


def process_thread_message(
    message: str, thread_message: dict, user: str, thread_ts: str, say
) -> bool:
    """
    スレッドのメッセージを処理する関数

    Args:
        message (str): ユーザーからの入力
        thread_message (dict): スレッドのメッセージ
        user (str): ユーザーID
        thread_ts (str): スレッドのタイムスタンプ
        say (function): botの発言を行う関数
    """
    err_flag = True
    if "subtype" in thread_message.keys():
        # subtypeがある場合は、処理をスキップする
        return err_flag

    try:
        err_flag = _process_message(
            message, thread_message, user, thread_ts, say
        )
    except ValueError as e:
        # エラーが発生した場合は、エラーメッセージを表示してNoneを返す
        say(f"Error: {e}", thread_ts=thread_ts)
        return err_flag

    if err_flag:
        # エラーが発生した場合は、エラーメッセージを表示する
        say("指示の処理中にエラーが発生しました。", thread_ts=thread_ts)
    else:
        return False


def _process_message(
    message: str, thread_message: dict, user: str, thread_ts: str, say
) -> bool:
    """
    メッセージを処理する関数

    Args:
        message (str): ユーザーからの入力
        thread_message (dict): スレッドのメッセージ
        user (str): ユーザーID
        thread_ts (str): スレッドのタイムスタンプ
        say (function): botの発言を行う関数
    """
    if "要約" in message:
        # 要約を作成する
        return process_pdf_request(thread_message, user, thread_ts, say)
    elif "pdf" in message:
        # pdfファイルを取得する
        return process_pdf_request(thread_message, user, thread_ts, say)
    elif "ping" in message:
        # pingリクエストを処理する
        return process_ping_request(user, thread_ts, say)
    else:
        # それ以外の場合は、エラーメッセージを返す
        say("不正なメッセージが送信されました。", thread_ts=thread_ts)
        return True


@app.event("app_mention")
def process_mention_event(body, logger, say):
    """
    app_mentionイベントを処理する関数

    Args:
        body (dict): イベントの情報
        logger (Logger): ロガー
        say (function): botの発言を行う関数
    """
    err_flag = True
    logger.info(body)
    user = body["event"]["user"]
    channel_id = body["event"]["channel"]
    thread_ts = body["event"].get("thread_ts", body["event"]["ts"])
    thread_messages = get_thread_messages(channel_id, thread_ts)

    if thread_messages is None:
        # スレッドのメッセージが取得できなかった場合は、エラーメッセージを返す
        say("スレッドのメッセージを取得できませんでした。", thread_ts=thread_ts)
        return err_flag

    bot_user_id = body["authorizations"][0]["user_id"]
    message = body["event"]["text"]
    message = message.replace(f"<@{bot_user_id}>", "").strip()

    thread_message = thread_messages[0]

    err_flag = process_thread_message(
        message, thread_message, user, thread_ts, say
    )

    if err_flag:
        # エラーが発生した場合は、エラーメッセージを表示する
        logger.error("指示の処理中にエラーが発生しました。")
    else:
        logger.info("指示の処理が完了しました。")


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

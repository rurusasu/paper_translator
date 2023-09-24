import os

import arxiv
import notion_client as client
from notion_client import errors

from src.arXivUtils import get_paper_info_by_id

PROPERTIES = {
    "Name": {
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "",
                },
            }
        ]
    },
    "URL": {
        "url": "",
    },
    "Type": {
        "select": {
            "name": "paper",
        }
    },
    "Author": {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": "",
                },
            }
        ]
    },
    "Conference": {
        "select": {
            "name": "arXiv",
        }
    },
    "Published": {
        "date": {
            "start": "",
        }
    },
}


# インスタンスの作成
notion_client = client.Client(auth=os.getenv("NOTION_API_KEY"))


def check_connect_notion() -> None:
    """Notionに接続できるか確認する関数

    Returns:
        None
    """
    import pprint

    # APIキーの接続確認
    try:
        list_users_response = notion_client.users.list()
    except client.errors.APIResponseError as e:
        print(f"Error getting message: {e}")
        return None
    else:
        pprint.pprint(list_users_response["results"][0])

    # DATABASE_IDの接続確認
    try:
        response = notion_client.databases.retrieve(
            database_id=os.getenv("NOTION_DATABASE_ID")
        )
    except client.errors.APIResponseError as e:
        print(f"Error getting message: {e}")
        return None
    else:
        pprint.pprint(response)
        return None


def page_to_property(paper: arxiv.Result) -> None:
    """Notionのページにプロパティを設定する関数

    Args:
        paper (arxiv.Result): 論文情報
    """

    # ページのプロパティを設定する
    PROPERTIES["Name"]["title"][0]["text"]["content"] = paper.title
    PROPERTIES["URL"]["url"] = paper.entry_id
    PROPERTIES["Type"]["select"]["name"] = "paper"
    # PROPERTIES["Author"]["rich_text"][0]["text"]["content"] = paper.authors
    PROPERTIES["Conference"]["select"]["name"] = "arXiv"
    PROPERTIES["Published"]["date"]["start"] = paper.published.strftime(
        "%Y-%m-%d"
    )

    return None


def save_to_notion_page(markdown_text: str, entry_id: str) -> None:
    """NotionのページにMarkdownを書き込む関数

    Args:
        markdown_text (str): Markdownのテキスト
        entry_id (str): 論文のID
    """
    paper = get_paper_info_by_id(entry_id=entry_id)

    page_to_property(paper)
    payload = {"children": []}
    for sentence in markdown_text.split("\n"):
        if "#" in sentence:
            n_head = len(sentence.split(" ")[0])
            if n_head >= 4:
                payload["children"].append(
                    {
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": " ".join(
                                            sentence.split(" ")[1:]
                                        )
                                    }
                                }
                            ]
                        }
                    }
                )
            else:
                payload["children"].append(
                    {
                        f"heading_{n_head}": {
                            "text": [
                                {
                                    "text": {
                                        "content": " ".join(
                                            sentence.split(" ")[1:]
                                        )
                                    }
                                }
                            ]
                        }
                    }
                )
        else:
            payload["children"].append(
                {
                    "paragraph": {
                        "rich_text": [
                            {"text": {"content": sentence}},
                        ]
                    }
                }
            )

    # NotionのページにMarkdownを書き込む
    try:
        response = notion_client.pages.create(
            **{
                "parent": {"database_id": os.getenv("NOTION_DATABASE_ID")},
                "icon": {
                    "type": "emoji",
                    "emoji": "📄",
                },
                "properties": PROPERTIES,
                **payload,
            }
        )
    except errors.APIResponseError as e:
        print(f"Error writing message: {e}")


if __name__ == "__main__":
    entry_id = "2103.14030"
    # check_connect_notion()
    with open(
        "./data/FPTQ_Fine-grained_Post-Training_Quantization_for_Large_Language_Models/tmp_markdown.md",
        mode="r",
    ) as f:
        markdown_text = f.read()
    save_to_notion_page(
        markdown_text=markdown_text,
        entry_id=entry_id,
    )

import os
from datetime import datetime
from typing import Dict

import notion_client as client
from notion_client import errors

PROPERTIES = {
    "Title": {
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

    try:
        list_users_response = notion_client.users.list()
    except client.errors.APIResponseError as e:
        print(f"Error getting message: {e}")
        return None
    else:
        pprint.pprint(list_users_response["results"][0])

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


def set_title_property(doc_info: Dict[str, str]) -> None:
    """Notionページのタイトルプロパティを設定する関数

    Args:
        doc_info (Dict[str, str]): ページの情報
    """
    PROPERTIES["Title"]["title"][0]["text"]["content"] = doc_info["Title"]


def set_url_property(doc_info: Dict[str, str]) -> None:
    """NotionページのURLプロパティを設定する関数

    Args:
        doc_info (Dict[str, str]): ページの情報
    """
    PROPERTIES["URL"]["url"] = doc_info["Entry_id"]


def set_type_property() -> None:
    """NotionページのTypeプロパティを設定する関数"""
    PROPERTIES["Type"]["select"]["name"] = "paper"


def set_author_property(doc_info: Dict[str, str]) -> None:
    """NotionページのAuthorプロパティを設定する関数

    Args:
        doc_info (Dict[str, str]): ページの情報
    """
    PROPERTIES["Author"]["rich_text"][0]["text"]["content"] = doc_info[
        "Authors"
    ]


def set_conference_property() -> None:
    """NotionページのConferenceプロパティを設定する関数"""
    PROPERTIES["Conference"]["select"]["name"] = "arXiv"


def set_published_property(doc_info: Dict[str, str]) -> None:
    """NotionページのPublishedプロパティを設定する関数

    Args:
        doc_info (Dict[str, str]): ページの情報
    """
    if doc_info["Published"] is None:
        return
    PROPERTIES["Published"]["date"]["start"] = datetime.strptime(
        doc_info["Published"], "%d %b %Y"
    ).strftime("%Y-%m-%d")


def set_page_properties(doc_info: Dict[str, str]) -> None:
    """Notionページのプロパティを設定する関数

    Args:
        doc_info (Dict[str, str]): ページの情報
    """
    set_title_property(doc_info)
    set_url_property(doc_info)
    set_type_property()
    set_author_property(doc_info)
    set_conference_property()
    set_published_property(doc_info)


def create_notion_page(payload: Dict) -> None:
    """Notionページを作成する関数

    Args:
        payload (Dict): ページの情報
    """
    try:
        notion_client.pages.create(
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


def set_page_properties_and_create_notion_page(
    markdown_text: str, doc_info: Dict[str, str]
) -> None:
    """Notionページのプロパティを設定し、ページを作成する関数

    Args:
        markdown_text (str): Markdownのテキスト
        doc_info (Dict[str, str]): ページの情報
    """
    set_page_properties(doc_info)
    payload = {"children": []}
    for sentence in markdown_text.split("\n"):
        if "#" in sentence:
            n_head = len(sentence.split(" ")[0])
            if n_head >= 4:
                payload["children"].append(
                    {
                        "object": "block",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": " ".join(
                                            sentence.split(" ")[1:]
                                        )
                                    }
                                }
                            ],
                        },
                    }
                )
            else:
                payload["children"].append(
                    {
                        "object": "block",
                        "type": f"heading_{n_head}",
                        f"heading_{n_head}": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": " ".join(
                                            sentence.split(" ")[1:]
                                        )
                                    }
                                }
                            ]
                        },
                    }
                )
        else:
            payload["children"].append(
                {
                    "object": "block",
                    "paragraph": {
                        "rich_text": [
                            {"text": {"content": sentence}},
                        ]
                    },
                }
            )

    create_notion_page(payload)


def write_markdown_to_notion(
    markdown_text: str, doc_info: Dict[str, str]
) -> None:
    """NotionページにMarkdownを書き込む関数

    Args:
        markdown_text (str): Markdownのテキスト
        doc_info (Dict[str, str]): ページの情報
    """
    if not isinstance(markdown_text, str) or not isinstance(doc_info, dict):
        raise TypeError("Invalid input type")
    set_page_properties_and_create_notion_page(markdown_text, doc_info)


if __name__ == "__main__":
    from src.XMLUtils import DocumentCreator

    entry_id = "2103.14030"
    with open(
        "./data/documents/FPTQ_Fine-grained_Post-Training_Quantization_for_Large_Language_Models/tmp_markdown.md",
        mode="r",
    ) as f:
        markdown_text = f.read()

    creator = DocumentCreator()
    DocumentCreator.load_xml(
        creator,
        "./data/documents/FPTQ_Fine-grained_Post-Training_Quantization_for_Large_Language_Models/FPTQ_Fine-grained_Post-Training_Quantization_for_Large_Language_Models.tei.xml",
    )
    doc_info = creator.get_doc_info()
    doc_info["Entry_id"] = entry_id

    write_markdown_to_notion(
        markdown_text=markdown_text,
        doc_info=doc_info,
    )

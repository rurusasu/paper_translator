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


def set_page_properties(doc_info: Dict[str, str]) -> None:
    """Notionのページにプロパティを設定する関数

    Args:
        paper (arxiv.Result): 論文情報
    """

    PROPERTIES["Title"]["title"][0]["text"]["content"] = doc_info["Title"]
    PROPERTIES["URL"]["url"] = doc_info["Entry_id"]
    PROPERTIES["Type"]["select"]["name"] = "paper"
    PROPERTIES["Author"]["rich_text"][0]["text"]["content"] = doc_info[
        "Authors"
    ]
    PROPERTIES["Conference"]["select"]["name"] = "arXiv"
    PROPERTIES["Published"]["date"]["start"] = datetime.strptime(
        doc_info["Published"], "%d %b %Y"
    ).strftime("%Y-%m-%d")

    return None


def write_markdown_to_notion(
    markdown_text: str, doc_info: Dict[str, str]
) -> None:
    """NotionのページにMarkdownを書き込む関数

    Args:
        markdown_text (str): Markdownのテキスト
        entry_id (str): 論文のID
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

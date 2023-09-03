import os

import arxiv
import notion_client as client

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


def page_to_property(paper: arxiv.Result) -> None:
    """Notionのページにプロパティを設定する関数

    Args:
        paper (arxiv.Result): 論文情報
    """

    # ページのプロパティを設定する
    PROPERTIES["Name"]["title"][0]["text"]["content"] = paper.title
    PROPERTIES["URL"]["url"] = paper.entry_id
    PROPERTIES["Type"]["select"]["name"] = "paper"
    PROPERTIES["Author"]["rich_text"][0]["text"]["content"] = paper.author
    PROPERTIES["Conference"]["select"]["name"] = "arXiv"
    PROPERTIES["Published"]["date"]["start"] = paper.publishd.strftime(
        "%Y-%m-%d"
    )

    return None


def write_to_notion_page(markdown_text: str, paper: arxiv.Result) -> None:
    """NotionのページにMarkdownを書き込む関数

    Args:
        markdown_text (str): Markdownのテキスト
        paper (arxiv.Result): 論文情報
    """

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
    response = client.pages.create(
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


if __name__ == "__main__":
    from src.XMLUtils import get_sections, make_xml_file

    pdf_name = "ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN"
    pdf_path = "./data/ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN/ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN.pdf"
    dir_path = (
        "./data/ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN/"
    )
    root = make_xml_file(dir_path, pdf_name, pdf_path)
    sections = get_sections(root=root)

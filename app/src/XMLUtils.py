import os
import subprocess
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Literal
from xml.etree.ElementTree import Element

import bs4
from llama_index import Document

GROBID_PATH = "/usr/lib/grobid-0.7.3"


def extract_author_names(author: Element) -> str:
    """著者名を抽出する関数

    Args:
        author (Element): 著者情報を含むElementオブジェクト

    Returns:
        author_name (str): 著者名
    """
    try:
        if len(author.find("persname")) == 2:
            first_name = author.find("persname").find("forename").text
            last_name = author.find("persname").find("surname").text
            author_name = f"{first_name} {last_name}"
        elif len(author.find("persname")) == 3:
            first_name = author.find("persname").find("forename").text
            middle_name = (
                author.find("persname")
                .find("forename", {"type": "middle"})
                .text
            )
            last_name = author.find("persname").find("surname").text
            author_name = f"{first_name} {middle_name} {last_name}"
        else:
            author_name = ""
    except Exception as e:
        print(f"Error in extract_author_names: {e}")
        author_name = ""
    return author_name


def extract_author_names_from_authors(authors: bs4.ResultSet) -> List[str]:
    """著者名を抽出する関数

    Args:
        authors (ResultSet): 著者情報を含むResultSetオブジェクト

    Returns:
        authors_list (List[str]): 著者名のリスト
    """
    authors_list = []
    try:
        for author in authors:
            author_name = extract_author_names(author)
            if author_name:
                authors_list.append(author_name)
    except (AttributeError, TypeError) as e:
        print(f"Error in extract_author_names_from_authors: {e}")
    return authors_list


def extract_pdf_info(teiheader: bs4.ResultSet) -> Dict[str, str]:
    """PDFファイルの情報を抽出する関数

    Args:
        teiheader (ResultSet): TEIヘッダー情報を含むResultSetオブジェクト
    Returns:
        pdf_info (Dict[str, str]): PDFファイルの情報を格納した辞書
    """
    pdf_info = {}
    try:
        sourceDesc = teiheader.find("sourcedesc").find("biblstruct")
        pdf_title = sourceDesc.find("analytic").find("title").text
        pdf_summary = teiheader.find("profiledesc").find("abstract").text
        authors = sourceDesc.find("analytic").find_all("author")
        authors_list = extract_author_names_from_authors(authors)
        published = sourceDesc.find("monogr").find("imprint").find("date").text
        pdf_idno = sourceDesc.find("idno").text
        pdf_lang = teiheader.get("xml:lang")

        pdf_info = {
            "Title": pdf_title,
            "All_Document_Summary": pdf_summary,
            "Idno": pdf_idno,
            "Language": pdf_lang,
            "Published": published,
            "Authors": authors_list,
        }
    except (AttributeError, TypeError) as e:
        print(f"Error in extract_pdf_info: {e}")
    return pdf_info


def run_grobid(dir_path: str) -> None:
    """Grobidを実行してXMLファイルを生成する関数

    Args:
        dir_path (str): PDFファイルが保存されているディレクトリのパス
    """
    try:
        if not os.path.exists(dir_path):
            raise ValueError("Invalid directory path")
        subprocess.run(
            f"java -Xmx4G -Djava.library.path=grobid-home/lib/lin-64:grobid-home/lib/lin-64/jep -jar {GROBID_PATH}/grobid-core/build/libs/grobid-core-0.7.3-onejar.jar -gH {GROBID_PATH}/grobid-home  -dIn {dir_path} -dOut {dir_path} -exe processFullText",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error in run_grobid: {e}")
    except Exception as e:
        print(f"Error in run_grobid: {e}")


def parse_xml_file(xml_path: str) -> Any:
    """XMLファイルをパースする関数

    Args:
        xml_path (str): XMLファイルのパス
    Returns:
        Dict["soup": BeautifulSoup, "root": Element] | None: BeautifulSoupオブジェクト
    """
    try:
        if not os.path.exists(xml_path):
            raise ValueError("Invalid XML file path")
        soup = bs4.BeautifulSoup(open(xml_path), "lxml")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return {"soup": soup, "root": root}
    except FileNotFoundError as e:
        print(f"Error in parse_xml_file: {e}")
    except Exception as e:
        print(f"Error in parse_xml_file: {e}")
    return None


def extract_documents(
    div_list: bs4.ResultSet,
    root: Element,
    pdf_info: Dict[str, str],
    doc_id_type: Literal[
        "Section_No.", "Section_Title", "Serial_Number"
    ] = "Serial_Number",
) -> List[Document]:
    """XMLからセクションを抽出し、Documentオブジェクトのリストを返す関数

    Args:
        div_list (ResultSet): セクション情報を含むResultSetオブジェクト
        root (Element): XMLのルート要素
        pdf_info (Dict[str, str]): PDFファイルの情報を格納した辞書
        doc_id_type (Literal["Section_No.", "Section_Title", "Serial_Number"], optional): ドキュメントIDの種類. Defaults to "Serial_Number".

    Returns:
        documents (List[Document]): Documentオブジェクトのリスト
    """
    # ドキュメントIDを設定する
    if doc_id_type not in [
        "Section_No.",
        "Section_Title",
        "Serial_Number",
    ]:
        raise ValueError("Invalid doc_id")

    documents = []
    try:
        i = 0
        meta_data = {
            "Section No.": "",
            "Section Title": "",
        }

        # セクションごとに処理を行う
        for div in root[1][0]:
            # セクション内の要素ごとに処理を行う
            for element in div:
                # セクションタイトルを取得する
                if element.tag == "{http://www.tei-c.org/ns/1.0}head":
                    if element.attrib.keys():
                        meta_data["Section No."] = element.attrib["n"]
                        meta_data["Section Title"] = element.text

                        # PDFファイルの情報をメタデータに追加する
                        for k, v in pdf_info.items():
                            meta_data[k] = v

                        if doc_id_type == "Section_No.":
                            doc_id = f"Section No.{element.attrib['n']}"
                        elif doc_id_type == "Section_Title":
                            doc_id = element.text
                        elif doc_id_type == "Serial_Number":
                            doc_id = f"{i}"

                        # セクションのテキストを取得する
                        soup_title = list(div_list[i].children)[0]
                        if soup_title != div_list[i].text:
                            text = div_list[i].find("p").text
                        else:
                            text = ""

                        # Documentオブジェクトを作成する
                        document = Document(
                            doc_id=doc_id,
                            text=text,
                            metadata=meta_data,
                        )
                        documents.append(document)
                        i += 1
                    else:
                        pass
    except (ValueError, Exception) as e:
        print(f"Error in extract_documents: {e}")
    else:
        return documents


class DocumentReader:
    def __init__(self):
        pass

    def load_data(
        self,
        xml_path: str,
        doc_id_type: Literal[
            "Section_No.", "Section_Title", "Serial_Number"
        ] = "Serial_Number",
    ) -> List[Document]:
        """XMLファイルからDocumentオブジェクトのリストを作成するメソッド

        Args:
            xml_path (str): XMLファイルのパス
            doc_id_type (Literal["Section_No.", "Section_Title", "Serial_Number"], optional): ドキュメントIDの種類. Defaults to "Serial_Number".

        Returns:
            documents (List[Document]): Documentオブジェクトのリスト
        """
        try:
            # ドキュメントIDの種類が正しいかチェックする
            if doc_id_type not in [
                "Section_No.",
                "Section_Title",
                "Serial_Number",
            ]:
                raise ValueError("Invalid doc_id")

            # XMLファイルをパースする
            parsed_data = parse_xml_file(xml_path)
            if parsed_data is None:
                raise ValueError("Failed to parse XML file")
            soup, root = parsed_data["soup"], parsed_data["root"]

            # PDFファイルの情報を取得する
            teiheader = soup.find("tei").find("teiheader")
            pdf_info = extract_pdf_info(teiheader)

            # セクションを抽出し、Documentオブジェクトのリストを作成する
            div_list = soup.find("text").find_all("div")
            documents = extract_documents(
                div_list=div_list,
                root=root,
                pdf_info=pdf_info,
                doc_id_type=doc_id_type,
            )
        except (ValueError, Exception) as e:
            print(f"Error in DocumentReader.load_data: {e}")
            return None
        else:
            return documents


if __name__ == "__main__":
    # from llama_index import SimpleDirectoryReader

    base_path = "/home/paper_translator/data"
    document_name = (
        "Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    )
    document_path = f"{base_path}/documents/{document_name}"
    xml_path = f"{document_path}/{document_name}.tei.xml"

    # Llama Index で提供されている SimpleDirectoryReader を使用して、
    # ディレクトリ内の PDF ファイルをDocumentオブジェクトとして読み込む
    # required_exts = [".pdf"]
    # documents_1 = SimpleDirectoryReader(
    #    input_dir=document_path, required_exts=required_exts, recursive=True
    # ).load_data()
    # print(f"documents_1 metadata: \n{documents_1[0].metadata}")

    # 自作の DirectoryReader を使用して、
    # ディレクトリ内の xml ファイルをDocumentオブジェクトとして読み込む
    # run_grobid(dir_path, pdf_name)
    documents_2 = DocumentReader().load_data(xml_path)
    print(f"documents_2 metadata: \n{documents_2[0].metadata['Section Title']}")

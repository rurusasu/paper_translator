import os
import subprocess
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Literal, Optional
from xml.etree.ElementTree import Element

import bs4
from llama_index import Document

from src.Informations import DocsInfoDict

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


def extract_author_names_from_authors(
    authors: bs4.ResultSet, is_list: bool = False
) -> str | List[str]:
    """著者名を抽出する関数

    Args:
        authors (ResultSet): 著者情報を含むResultSetオブジェクト

    Returns:
        authors (str | List[str]): 著者名を連結した文字列もしくはリスト
    """
    if is_list:
        authors = []
    else:
        authors = ""
    try:
        for author in authors:
            author_name = extract_author_names(author)
            if author_name:
                if is_list:
                    authors.append(author_name)
                else:
                    authors += f"{author_name}, "
    except (AttributeError, TypeError) as e:
        print(f"Error in extract_author_names_from_authors: {e}")
    return authors


def extract_doc_info(teiheader: bs4.ResultSet) -> Dict[str, str]:
    """PDFファイルの情報を抽出する関数

    Args:
        teiheader (ResultSet): TEIヘッダー情報を含むResultSetオブジェクト
    Returns:
        doc_info (Dict[str, str]): PDFファイルの情報を格納した辞書
    """
    try:
        sourceDesc = teiheader.find("sourcedesc").find("biblstruct")
        pdf_title = sourceDesc.find("analytic").find("title").text
        pdf_summary = teiheader.find("profiledesc").find("abstract").text
        authors = sourceDesc.find("analytic").find_all("author")
        authors = extract_author_names_from_authors(authors)
        published = sourceDesc.find("monogr").find("imprint").find("date").text
        pdf_idno = sourceDesc.find("idno").text
        pdf_lang = teiheader.get("xml:lang")

        """
        doc_info = {
            "Title": pdf_title,
            "All_Document_Summary": pdf_summary,
            "Idno": pdf_idno,
            "Language": pdf_lang,
            "Published": published,
            "Authors": authors,
        }
        """
        doc_info = DocsInfoDict.copy()
        doc_info["Title"] = pdf_title
        doc_info["All_Document_Summary"] = pdf_summary
        doc_info["Idno"] = pdf_idno
        doc_info["Language"] = pdf_lang
        doc_info["Published"] = published
        doc_info["Authors"] = authors
    except (AttributeError, TypeError) as e:
        raise (f"Error in extract_doc_info: {e}")
    else:
        return doc_info


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


def _parse_xml_file(xml_path: str) -> Any:
    """XMLファイルをパースする関数

    Args:
        xml_path (str): XMLファイルのパス
    Returns:
        Dict["bs4": BeautifulSoup, "root": Element] | None: BeautifulSoupオブジェクト
    """
    try:
        if not os.path.exists(xml_path):
            raise ValueError("Invalid XML file path")
        soup = bs4.BeautifulSoup(open(xml_path), "lxml")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return {"bs4": soup, "root": root}
    except FileNotFoundError as e:
        print(f"Error in parse_xml_file: {e}")
    except Exception as e:
        print(f"Error in parse_xml_file: {e}")
    return None


def extract_documents(
    div_list: bs4.ResultSet,
    root: Element,
    doc_info: Dict[str, str],
    doc_id_type: Literal[
        "Section_No.", "Section_Title", "Serial_Number"
    ] = "Serial_Number",
) -> List[Document]:
    """XMLからセクションを抽出し、Documentオブジェクトのリストを返す関数

    Args:
        div_list (ResultSet): セクション情報を含むResultSetオブジェクト
        root (Element): XMLのルート要素
        doc_info (Dict[str, str]): PDFファイルの情報を格納した辞書
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
                        for k, v in doc_info.items():
                            if v != "":
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


class DocumentCreator:
    def __init__(self):
        self.root = None
        self.doc_info = {}
        self.pdf_info = {}
        self.documents = []
        self.div_list = None

    def load_xml(
        self,
        xml_path: str,
    ) -> None:
        # XMLファイルをパースする
        parsed_data = _parse_xml_file(xml_path)
        if parsed_data is None:
            raise ValueError("Failed to parse XML file")
        soup, self.root = parsed_data["bs4"], parsed_data["root"]

        # PDFファイルの情報を取得する
        teiheader = soup.find("tei").find("teiheader")
        self.doc_info = extract_doc_info(teiheader)

        # セクションを抽出し、Documentオブジェクトのリストを作成する
        self.div_list = soup.find("text").find_all("div")

        return None

    def input_pdf_info(self, pdf_info: Dict[str, str]) -> None:
        self.pdf_info.update(pdf_info)

    def _marge_info(self) -> None:
        if self.pdf_info:
            self.doc_info["Entry_id"] = self.pdf_info["Entry_id"]
            self.doc_info["Pdf_url"] = self.pdf_info["Pdf_url"]
            self.doc_info["Updated"] = self.pdf_info["Updated"]
            self.doc_info["Categories"] = self.pdf_info["Categories"]
            self.doc_info["Comment"] = self.pdf_info["Comment"]
        return None

    def create_docs(
        self,
        doc_id_type: Literal[
            "Section_No.", "Section_Title", "Serial_Number"
        ] = "Serial_Number",
    ) -> Optional[List[Document]]:
        """XMLファイルからDocumentオブジェクトのリストを作成するメソッド

        Args:
            xml_path (str): XMLファイルのパス
            doc_id_type (Literal["Section_No.", "Section_Title", "Serial_Number"], optional): ドキュメントIDの種類. Defaults to "Serial_Number".

        Returns:
            Optional[List[Document]]: Documentオブジェクトのリスト
        """
        try:
            if (self.root is None) or (self.doc_info is None):
                raise ValueError(
                    "Error in DocumentReader.load_data: Invalid data"
                )

            # ドキュメントIDの種類が正しいかチェックする
            if doc_id_type not in [
                "Section_No.",
                "Section_Title",
                "Serial_Number",
            ]:
                raise ValueError("Invalid doc_id")

            if self.pdf_info:
                self._marge_info()

            documents = extract_documents(
                div_list=self.div_list,
                root=self.root,
                doc_info=self.doc_info,
                doc_id_type=doc_id_type,
            )
        except (ValueError, Exception) as e:
            print(f"Error in DocumentReader.load_data: {e}")
            return None
        else:
            self.documents = documents
            return self.documents

    def get_doc_info(self) -> Dict[str, str]:
        """PDFファイルの情報を取得するメソッド

        Returns:
            Dict[str, str]: PDFファイルの情報
        """
        return self.doc_info


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
    creator = DocumentCreator().load_xml(xml_path)
    documents_2 = creator.create_docs()
    print(f"documents_2 metadata: \n{documents_2[0].metadata['Section Title']}")

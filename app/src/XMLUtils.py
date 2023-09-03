import subprocess
import xml.etree.ElementTree as ET
from typing import List
from xml.etree.ElementTree import Element

GROBID_PATH = "/usr/lib/grobid-0.7.3"


class Section:
    def __init__(self, title: str = "", body: str = "") -> None:
        """セクションのタイトルと本文を保持するクラス

        Args:
            title (str, optional): セクションのタイトル. Defaults to "".
            body (str, optional): セクションの本文. Defaults to "".
        """
        self.title = title
        self.body = body


def make_xml_file(
    dir_path: str, pdf_name: str, is_debug: bool = False
) -> Element:
    if not is_debug:
        cp = subprocess.run(
            f"java -Xmx4G -Djava.library.path=grobid-home/lib/lin-64:grobid-home/lib/lin-64/jep -jar {GROBID_PATH}/grobid-core/build/libs/grobid-core-0.7.3-onejar.jar -gH {GROBID_PATH}/grobid-home  -dIn {dir_path} -dOut {dir_path} -exe processFullText",
            shell=True,
        )

    xml_path = dir_path + "/" + pdf_name + ".tei.xml"
    tree = ET.parse(xml_path)
    root = tree.getroot()
    return root


def get_sections(root: Element) -> List[str]:
    """XMLからセクションを取得する関数

    Args:
        root (Element): XMLのルート要素
    Returns:
        sections (List[Section]): セクションのリスト
    """
    sections = []
    for div in root[1][0]:
        section = Section("", "")
        for element in div:
            if element.tag == "{http://www.tei-c.org/ns/1.0}head":
                section.title = element.text
            if element.tag == "{http://www.tei-c.org/ns/1.0}p":
                section.body += get_text(element=element)

        if section.body != "":
            sections.append(section)

    return sections


def get_text(element: Element):
    """XML要素からテキストを取得

    Args:
        element (Element): XMLの要素
    Returns:
        text: テキスト
    """
    text = ""
    for elem in element.iter():
        if elem.text:
            text += elem.text
        if elem.tail:
            text += elem.tail
    return text


if __name__ == "__main__":
    pdf_name = "ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN"
    pdf_path = "./data/ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN/ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN.pdf"
    dir_path = (
        "./data/ALGAN_Time_Series_Anomaly_Detection_with_Adjusted-LSTM_GAN/"
    )
    root = make_xml_file(dir_path, pdf_name)
    sections = get_sections(root=root)

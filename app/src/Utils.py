import torch
from typing import List
from tqdm import tqdm
from src.OpenAIUtils import get_message, SYSTEM
from src.translator.summarize_translator import summarize_translator
from src.translator.llama_cpp import create_llama_cpp_model


device = "cuda:0" if torch.cuda.is_available() else "cpu"


def create_summarizer(llm_model, prompt_temp_path):
    """要約器を作成する関数

    Args:
        llm_model: Llama-CPPモデル
        prompt_temp_path: プロンプトテンプレートのパス

    Returns:
        summarizer: 要約器
    """
    summarizer = summarize_translator(llm_model=llm_model, max_tokens=60)
    summarizer.create_prompr_from_file(prompt_temp_path)
    return summarizer


def translate_section(section, summarizer):
    """セクションを翻訳する関数

    Args:
        section: セクション
        summarizer: 要約器

    Returns:
        translated_text: 翻訳されたテキスト
    """
    # 144文字以下の場合は、全文を翻訳する
    if len(section.body.split(" ")) < 144:
        response = section.body
    # 144文字以上の場合は、要約して翻訳する
    else:
        response = get_message(text=section.body, system=SYSTEM)

    translated_text = summarizer.translate(response)
    return translated_text


def write_markdown(
    sections: List[str],
    prompt_temp_path: str | None = None,
) -> str:
    """Markdownファイルを作成する関数

    Args:
        sections (List[str]): セクションのリスト
        prompt_temp_path (str | None, optional): プロンプトテンプレートのパス. Defaults to None.

    Returns:
        markdown_text (str): Markdownのテキスト
    """
    try:
        llm_model = create_llama_cpp_model(
            package_name="langchain",
            model_path="/home/paper_translator/data/models/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf",
            temperature=0.1,
        )
        summarizer = create_summarizer(llm_model, prompt_temp_path)

        markdown_text = ""
        for section in tqdm(sections):
            translated_text = translate_section(section, summarizer)
            markdown_text += "\n" + translated_text

            if "conclusion" in section.title.lower():
                break

        return markdown_text

    except Exception as e:
        print(f"Error occurred: {e}")
        return ""


if __name__ == "__main__":
    # from src.arXivUtils import get_pdf
    from src.XMLUtils import extract_sections, parse_xml_file, run_grobid

    # dir_path, _, pdf_name = get_pdf("2103.00020")
    dir_path = "/home/paper_translator/data/documents/Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    pdf_name = (
        "Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    )
    temp_file = "/home/paper_translator/data/prompt_temp/prompt_test.txt"

    run_grobid(dir_path, pdf_name)
    xml_path = dir_path + "/" + pdf_name + ".tei.xml"
    root = parse_xml_file(xml_path)
    sections = extract_sections(root=root)
    markdown_text = write_markdown(
        sections=sections, prompt_temp_path=temp_file
    )
    print(markdown_text)

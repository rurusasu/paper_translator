from typing import List

import torch
from auto_gptq import AutoGPTQForCausalLM
from tqdm.auto import tqdm
from transformers import AutoTokenizer, pipeline

from src.OpenAIUtils import get_message
from src.translator import LlamaCppWrapper, Pipeline

SYSTEM = """
### 指示 ###
文章の内容の中で、重要なポイントを3つ箇条書きしてください。
箇条書きは、文章の内容を簡潔にまとめたものである必要があります。
箇条書きは、以下の制約に従ってください。

### 箇条書きの制約 ###
- 最大5個まで
- 箇条書き1個を50文字以内

### 対象とする論文の内容 ###
{text}

### 出力形式 ###
- 箇条書き1
- 箇条書き2
- 箇条書き3
"""


PROMPT_TEMPLATE = """
### 指示 ###
対象とする文章を翻訳してください。
翻訳は、以下の制約に従ってください。

### 対象とする文章 ###
{prompt_text}

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
"""

device = "cuda:0" if torch.cuda.is_available() else "cpu"


def write_markdown(
    sections: List[str], pdf_name: str, use_OpenAI: bool = False
) -> str:
    """Markdownファイルを作成する関数

    Args:
        sections (List[str]): セクションのリスト
        pdf_name (str): PDFファイル名
        use_OpenAI (bool, optional): OpenAI APIを使うかどうか. Defaults to False.

    Returns:
        markdown_text (str): Markdownのテキスト
    """
    """
    # トークナイザーとモデルの準備
    quantized_model_dir = "dahara1/weblab-10b-instruction-sft-GPTQ"
    model_basename = "gptq_model-4bit-128g"

    summarizer = pipeline("summarization", model="kworts/BARTxiv")
    tokenizer = AutoTokenizer.from_pretrained(
        quantized_model_dir, use_fast=True
    )

    model = AutoGPTQForCausalLM.from_quantized(
        quantized_model_dir,
        model_basename=model_basename,
        use_safetensors=True,
        device=device,
    )
    """
    llm_model = LlamaCppWrapper(
        model_path="/home/paper_translator/data/models/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf",
    )
    prompt_temp_path = "/home/paper_translator/data/prompt_temp/prompt.txt"
    index_dir_path = "/home/paper_translator/data/vector_store/"
    pipline = Pipeline(llm_model=llm_model, prompt_temp_path=prompt_temp_path)
    pipline.ReadVectorIndex(index_dir_path=index_dir_path)

    markdown_text = ""
    for section in tqdm(sections):
        # 144文字以下の場合は、全文を翻訳する
        if (len(section.body.split(" "))) < 144:
            # translated_text = translator(section.body)[0]["translation_text"]
            prompt_text = section.body
        # 144文字以上500文字以下の場合は、要約して翻訳する
        elif len(section.body.split(" ")) < 500:
            summary = summarizer(section.body)[0]["summary_text"]
            # translated_text = translator(summary)[0]["translation_text"]
            prompt_text = summary
        else:
            response = get_message(text=section.body, system=SYSTEM)
            # translated_text = translator(response)[0]["translation_text"]
            prompt_text = response
            """
            tokens = (
                tokenizer(
                    PROMPT_TEMPLATE.format(prompt_text=prompt_text),
                    return_tensors="pt",
                )
                .to(device)
                .input_ids
            )

            output = model.generate(
                input_ids=tokens,
                eos_token_id=0,
                pad_token_id=1,
                max_new_tokens=500,
                do_sample=True,
                top_k=5,
                temperature=0.1,
            )
            output_text = tokenizer.decode(output[0])
            start_index = output_text.find("### 出力 ###")
            translated_text = output_text[start_index:]
            """
        translated_text = pipline.Answer(prompt_text)

        markdown_text += "\n" + translated_text

        if "conclusion" in section.title.lower():
            break

    return markdown_text


if __name__ == "__main__":
    # from src.arXivUtils import get_pdf
    from src.XMLUtils import get_sections, make_xml_file

    # dir_path, _, pdf_name = get_pdf("2103.00020")
    dir_path = "/home/paper_translator/data/documents/Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    pdf_name = (
        "Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    )

    root = make_xml_file(dir_path=dir_path, pdf_name=pdf_name, is_debug=True)
    sections = get_sections(root=root)
    markdown_text = write_markdown(sections=sections, pdf_name=pdf_name)
    print(markdown_text)

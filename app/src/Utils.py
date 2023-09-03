from typing import List

from auto_gptq import AutoGPTQForCausalLM
from tqdm.auto import tqdm
from transformers import AutoTokenizer, pipeline

from src.OpenAIUtils import get_message

SYSTEM = """
### 指示 ###
論文の内容を理解した上で，重要なポイントを箇条書きで3点書いてください。

### 箇条書きの制約 ###
- 最大3個
- 日本語
- 箇条書き1個を100文字以内

### 対象とする論文の内容 ###
{text}

### 出力形式 ###
- 箇条書き1
- 箇条書き2
- 箇条書き3
"""

PROMPT_TEMPLATE = """
以下は、タスクを説明する指示です。要求を適切に満たす応答を書きなさい。
### 指示 ###
次の文章を翻訳してください。
{prompt_text}
### 応答: """


def write_markdown(sections: List[str], pdf_name: str) -> str:
    """Markdownファイルを作成する関数

    Args:
        sections (List[str]): セクションのリスト
        pdf_name (str): PDFファイル名

    Returns:
        markdown_text (str): Markdownのテキスト
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
        device="cuda:0",
    )

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

        tokens = (
            tokenizer(PROMPT_TEMPLATE, return_tensors="pt")
            .to("cuda:0")
            .input_ids
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        output = model.generate(
            input_ids=tokens,
            pad_token_id=tokenizer.pad_token_id,
            max_new_tokens=500,
            do_sample=True,
            temperature=0.1,
        )
        translated_text = tokenizer.decode(output[0])
        markdown_text += "\n" + translated_text

        if "conclusion" in section.title.lower():
            break

    return markdown_text


if __name__ == "__main__":
    # from src.arXivUtils import get_pdf
    from src.XMLUtils import get_sections, make_xml_file

    # dir_path, _, pdf_name = get_pdf("2103.00020")
    dir_path = "/home/paper_translator/data/Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    pdf_name = (
        "Learning_Transferable_Visual_Models_From_Natural_Language_Supervision"
    )

    root = make_xml_file(dir_path=dir_path, pdf_name=pdf_name, is_debug=True)
    sections = get_sections(root=root)
    markdown_text = write_markdown(sections=sections, pdf_name=pdf_name)
    print(markdown_text)

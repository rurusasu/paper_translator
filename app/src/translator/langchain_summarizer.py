from typing import Any

from langchain import OpenAI
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import TokenTextSplitter


class langchain_summarizer:
    def __init__(
        self, llm_model: Any | None = None, max_tokens: int = 8
    ) -> None:
        """
        SummarizeTranslatorクラスのコンストラクタ

        Args:
            llm_model (Any | None): OpenAIのLLMモデル名。デフォルトはNone。
            max_tokens (int): 1つの文章に含める最大トークン数。デフォルトは8。
        """
        if llm_model is None:
            # LLMモデルが指定されていない場合
            self.llm = OpenAI(temperature=0)
        else:
            self.llm = llm_model
        self.text_splitter = TokenTextSplitter(
            chunk_size=max_tokens, chunk_overlap=20
        )
        self.summary_chain = load_summarize_chain(
            self.llm, chain_type="map_reduce"
        )
        # prompt_templeateの作成
        self.prompt_subject = self._create_prompt()

    def _create_prompt(self) -> str:
        """
        翻訳プロンプトを生成する関数

        Returns:
            str: 翻訳プロンプト
        """
        prompt_template = PromptTemplate(
            input_variables=["prompt_text"],
            template=(
                "### 指示 ###\n"
                "対象とする文章を翻訳してください。\n"
                "翻訳は、以下の制約に従ってください。\n"
                "### 対象とする文章 ###\n"
                "{prompt_text}\n"
                "### 文章の制約 ###\n"
                "- 日本語で出力してください。\n"
                "- 箇条書きの文章ごとに翻訳してください。\n"
                "- 1つの項目ごとに100文字以内で翻訳してください。\n"
                "- 箇条書きで出力してください。\n"
            ),
        )
        return prompt_template

    def create_prompr_from_file(self, template_path: str) -> str:
        with open(template_path, "r") as f:
            template = f.read()
        self.prompt_subject = PromptTemplate(
            input_variables=["prompt_text"], template=template
        )
        return self.prompt_subject

    def translate(self, document: str) -> str:
        """文章を翻訳する関数

        Args:
            document (str): 翻訳する文章

        Returns:
            str: 翻訳した文章
        """
        documents = self.text_splitter.create_documents([document])
        chainSubject = LLMChain(llm=self.llm, prompt=self.prompt_subject)
        overall_chain_map_reduce = SimpleSequentialChain(
            chains=[self.summary_chain, chainSubject]
        )
        subject = overall_chain_map_reduce.run(documents)

        return subject

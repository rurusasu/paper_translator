from typing import List

import torch
from llama_index.llms import HuggingFaceLLM
from transformers import AutoTokenizer, pipeline

device = "cuda:0" if torch.cuda.is_available() else "cpu"


class HuggingFaceWrapper:
    def __init__(
        self, model_name_or_path: str, model_basename: str | None = None
    ):
        self.model_name_or_path = model_name_or_path
        GPTQ_Flag = (
            True if "GPTQ" in self.model_name_or_path.split("/")[-1] else False
        )
        if GPTQ_Flag:
            from auto_gptq import AutoGPTQForCausalLM

            self._model = AutoGPTQForCausalLM.from_pretrained(
                model_name_or_path=self.model_name_or_path,
                model_basename=model_basename,
                use_safetensors=True,
                device=device,
            )

        # set tokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path=self.model_name_or_path,
            use_fast=True,
        )

        # set summarizer
        self._summrizer = pipeline(
            "summarization", model=self.model_name_or_path
        )

        self._llm = HuggingFaceLLM(
            model=self._model,
            tokenizer=self._tokenizer,
            summarizer=self._summrizer,
        )

    def summarize(self, prompt: str) -> str:
        tokens = (
            self._tokenizer(prompt, return_tensors="pt").to(device).input_ids
        )

        output = self._model.generate(
            input_ids=tokens,
            max_length=512,
            eos_token_id=0,
            pad_token_id=1,
            max_new_tokens=500,
            do_sample=True,
            top_k=5,
            top_p=0.95,
            temperature=0.1,
        )

        output_text = self._tokenizer.decode(output[0])
        return output_text


if __name__ == "__main__":
    model_name_or_path = "dahara1/weblab-10b-instruction-sft-GPTQ"
    model_basename = "gptq_model-4bit-128g"
    model = HuggingFaceWrapper(model_name_or_path, model_basename)
    prompt = "The quick brown fox jumps over the lazy dog"
    output_text = model.summarize(prompt)
    print(output_text)

import os
import time
from typing import List

import openai

# OpenAIのAPIを使うための準備
openai.organization = "org-Iag9C9eT1CKuntaQKeCdZdXm"
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo-0301"  # OpenAIのモデル名
TEMPERATURE = 0.15  # OpenAIのtemperature

SYSTEM = """
### 指示 ###
論文の内容を理解した上で, 重要なポイントを箇条書きで3点書いてください。

### 箇条書きの制約 ###
- 最大3個
- 日本語
- 箇条書き1個を50文字以内

### 対象とする論文の内容 ###
{text}

### 出力形式 ###
タイトル(和名)

- 箇条書き1
- 箇条書き2
- 箇条書き3
"""


def OpenAIModelList() -> List[str]:
    """
    OpenAIのモデル一覧を取得する関数

    Returns:
        list: OpenAIのモデル一覧
    """
    api_dict = dict(openai.Model.list())
    api_list = api_dict["data"]
    model_list = []
    for value1 in api_list:
        for key2, value2 in value1.items():
            if key2 == "id":
                model_list.append(value2)
                break
    return model_list


def get_message(
    text: str, model_name: str = MODEL_NAME, system: str = SYSTEM
) -> str:
    """OpenAI APIを使って，ChatGPTに文章を生成させる関数

    Args:
        text (str): ユーザーからの入力
        model_name (str, optional): OpenAIのモデル名. Defaults to MODEL_NAME.
        system (str, optional): ChatGPTのシステムの入力. Defaults to SYSTEM.

    Returns:
        message (str): ChatGPTからの出力
    """
    cnt = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": text},
                ],
            )
            break
        # OpenAIのAPIのエラー処理
        except (
            openai.error.RateLimitError,
            openai.error.InvalidRequestError,
        ) as e:
            print(e.user_message)
            time.sleep(20)
            cnt += 1
            # 3回失敗したら終了
            if cnt == 3:
                raise e

    time.sleep(5)
    message = response.choices[0]["message"]["content"]
    return message


if __name__ == "__main__":
    # print(OpenAIModelList())

    text = "大谷翔平について教えて"
    message = get_message(text)
    print(message)

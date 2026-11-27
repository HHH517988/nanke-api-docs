"""最小可用示例：OpenAI SDK 接 Nanke API，含空流校验与降级链。

pip install openai
NK_KEY=sk-xxx python python_openai.py
"""
import os

from openai import OpenAI

BASE_URL = "https://nanke.pw/v1"
MODEL = "claude-3-haiku"  # 短名＝性价比档；anthropic/xxx 为原厂档
FALLBACK = ["claude-3-haiku", "deepseek-flash"]

client = OpenAI(base_url=BASE_URL, api_key=os.environ["NK_KEY"])


def chat(prompt: str, model: str = MODEL) -> str:
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    parts, got_content = [], False
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            got_content = True
            parts.append(chunk.choices[0].delta.content)

    # 关键：HTTP 200 + 空流 也要当失败
    if not got_content:
        raise RuntimeError(f"empty stream from {model}")
    return "".join(parts)


def chat_with_fallback(prompt: str) -> str:
    last_err = None
    for model in FALLBACK:
        try:
            return chat(prompt, model)
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[warn] {model} failed: {e}")
    raise RuntimeError(f"all models failed: {last_err}")


if __name__ == "__main__":
    print(chat_with_fallback("用一句话解释什么是 token 计费。"))

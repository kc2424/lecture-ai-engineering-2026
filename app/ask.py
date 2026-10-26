"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str, session=None) -> str:
    if session is None:
        client = genai.Client(api_key=get_api_key())
        response = client.models.generate_content(model=MODEL, contents=question)
    else:
        response = session.send_message(question)
    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", None)
    output_tokens = getattr(usage, "candidates_token_count", None)
    print(
        f"[usage] input: {input_tokens if input_tokens is not None else '不明'} tokens, "
        f"output: {output_tokens if output_tokens is not None else '不明'} tokens"
    )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--chat", action="store_true", help="会話を続ける")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    if args.chat:
        client = genai.Client(api_key=get_api_key())

        # 会話を1回だけ作り、同じものを使い続ける。
        session = client.chats.create(model=MODEL)
        print("会話モード：q で終了します。")

        try:
            while True:
                question = input("\n[you] > ").strip()

                if question.lower() == "q":
                    break

                if not question:
                    continue

                try:
                    print(ask(question, session=session))
                except errors.APIError as e:
                    print(api_error_message(e.code, e.message))

        except (EOFError, KeyboardInterrupt):
            print()
        finally:
            client.close()

        print("会話を終了しました。")
        return
    print(f"[質問] {args.question}\n")
    try:
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

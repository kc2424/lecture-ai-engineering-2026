from types import SimpleNamespace

from app import ask


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    class FakeClient:
        def __init__(self, api_key):
            self.models = SimpleNamespace(
                generate_content=lambda **kwargs: SimpleNamespace(
                    text="回答",
                    usage_metadata=SimpleNamespace(
                        prompt_token_count=12,
                        candidates_token_count=8,
                    ),
                )
            )

    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")

    assert ask.ask("質問") == "回答"
    assert "[usage] input: 12 tokens, output: 8 tokens" in capsys.readouterr().out
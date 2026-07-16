import tiktoken

def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    return len(tokens)

if __name__ == "__main__":
    test_texts = [
        "Salut!",
        "Salut, sunt DevOpescu!",
        "How do I diagnose a Docker container that will not start?",
        "",
        "Docker container logs can be inspected using docker logs."
    ]

    for text in test_texts:
        print(f"Text: {text!r}")
        print(f"Număr tokeni: {count_tokens(text)}")
        print("-" * 40)    
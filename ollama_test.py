from ollama import chat


def ask_qwen3():
    prompt = "How you doin?"
    response = chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


if __name__ == "__main__":
    print(ask_qwen3())
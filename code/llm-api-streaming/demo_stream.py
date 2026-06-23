from __future__ import annotations

from dotenv import load_dotenv

from streaming_client import LLMStreamingClient, load_default_stream_request


def main() -> None:
    """命令行演示模型流式输出。

    默认使用 mock provider，不产生模型费用。真实 provider 请先配置 .env。
    """
    load_dotenv()
    client = LLMStreamingClient()
    request = load_default_stream_request("用三句话解释为什么 LLM API 需要 streaming。")

    print(f"request_id={request.request_id}")
    print("stream output:", end="", flush=True)
    for chunk in client.stream(request):
        if chunk.delta:
            print(chunk.delta, end="", flush=True)
    print("\n")
    print(f"log_path={client.log_path}")


if __name__ == "__main__":
    main()

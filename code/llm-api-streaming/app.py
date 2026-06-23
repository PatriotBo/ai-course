from __future__ import annotations

import json

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from streaming_client import LLMStreamingClient, Message, StreamRequest, env_first


load_dotenv()

app = FastAPI(title="LLM API Streaming Demo", version="0.1.0")


class ChatStreamRequest(BaseModel):
    """浏览器/业务方提交给后端 streaming endpoint 的请求。"""

    message: str = Field(..., min_length=1, description="用户输入")
    model: str | None = Field(default=None, description="可选，覆盖默认模型")
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int = Field(default=512, ge=1, le=4096)


def sse_event(event: str, data: dict) -> str:
    """把事件名称和 JSON 数据编码成 SSE 文本帧。

    SSE 格式必须用空行分隔事件：
    event: delta
    data: {"text":"..."}

    """
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat/stream")
def chat_stream(body: ChatStreamRequest) -> StreamingResponse:
    """把模型流式响应封装成后端 SSE 接口。

    业务层只看到 /api/chat/stream，不需要知道底层是 mock、GLM、腾讯混元还是其他供应商。
    """
    client = LLMStreamingClient()
    model = body.model or env_first("LLM_MODEL", "OPENAI_MODEL", "ZAI_MODEL", "HUNYUAN_MODEL", default="mock-stream-model")

    request = StreamRequest(
        model=model or "mock-stream-model",
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        messages=[
            Message(role="system", content="你是一个严谨的 AI 工程课程助教，回答要结构化、准确、可执行。"),
            Message(role="user", content=body.message),
        ],
    )

    def event_generator():
        """FastAPI 会迭代这个 generator，并把每个字符串立即发送给客户端。"""
        yield sse_event("meta", {"request_id": request.request_id, "model": request.model})
        try:
            for chunk in client.stream(request):
                if chunk.done:
                    yield sse_event("done", {"request_id": request.request_id})
                elif chunk.delta:
                    yield sse_event("delta", {"request_id": request.request_id, "text": chunk.delta})
        except Exception as exc:
            # SSE 已经开始返回后，不能再改 HTTP status，只能用 error event 告诉前端。
            yield sse_event("error", {
                "request_id": request.request_id,
                "type": exc.__class__.__name__,
                "message": str(exc),
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

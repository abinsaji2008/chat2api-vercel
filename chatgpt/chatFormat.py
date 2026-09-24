import json
import random
import string
import time
import uuid

async def head_process_response(response):
    async for chunk in response:
        if isinstance(chunk, bytes):
            chunk = chunk.decode()
        if chunk.startswith("data: {"):
            try:
                data = json.loads(chunk[6:].strip())
            except Exception:
                continue
            message = data.get("message", {})
            if message.get("author", {}).get("role") in ("user", "system"):
                continue
            if message.get("status") == "in_progress":
                return response, True
    return response, False

async def stream_response(service, response, model, max_tokens):
    chat_id = "chatcmpl-" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(29))
    created = int(time.time())
    yield "data: " + json.dumps({
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}],
    }) + "\n\n"
    async for chunk in response:
        if isinstance(chunk, bytes):
            chunk = chunk.decode()
        if chunk.startswith("data: [DONE]"):
            yield "data: [DONE]\n\n"
            continue
        if not chunk.startswith("data: "):
            continue
        try:
            data = json.loads(chunk[6:].strip())
            message = data.get("message", {})
            parts = message.get("content", {}).get("parts", [])
            if parts:
                yield "data: " + json.dumps({
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"content": parts[-1]}, "finish_reason": None}],
                }) + "\n\n"
        except Exception:
            continue
    yield "data: [DONE]\n\n"

async def format_not_stream_response(response, prompt_tokens, max_tokens, model):
    text = []
    async for chunk in response:
        if not chunk.startswith("data: ") or chunk.startswith("data: [DONE]"):
            continue
        try:
            data = json.loads(chunk[6:].strip())
            text.append(data["choices"][0]["delta"].get("content", ""))
        except Exception:
            pass
    content = "".join(text)
    completion_tokens = len(content.split())
    return {
        "id": "chatcmpl-" + uuid.uuid4().hex[:29],
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens},
    }

async def api_messages_to_chat(service, api_messages, upload_by_url=False):
    messages = []
    for message in api_messages:
        content = message.get("content", "")
        if isinstance(content, list):
            text = "\n".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        else:
            text = str(content)
        messages.append({
            "id": str(uuid.uuid4()),
            "author": {"role": message.get("role", "user")},
            "content": {"content_type": "text", "parts": [text]},
            "metadata": {},
        })
    prompt_tokens = sum(len(str(m.get("content", "")).split()) for m in api_messages)
    return messages, prompt_tokens

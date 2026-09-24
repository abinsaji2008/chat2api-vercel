from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app import app
from chatgpt.ChatService import ChatService
import types
from starlette.background import BackgroundTask
from utils.configs import api_prefix, authorization_list


async def _send_conversation(request: Request):
    if authorization_list:
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] not in authorization_list:
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    service = ChatService("")
    try:
        await service.set_dynamic_data(data)
        await service.get_chat_requirements()
        await service.prepare_send_conversation()
        result = await service.send_conversation()

        if isinstance(result, types.AsyncGeneratorType):
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                background=BackgroundTask(service.close_client),
            )

        return JSONResponse(
            result,
            background=BackgroundTask(service.close_client),
        )
    except HTTPException:
        await service.close_client()
        raise
    except Exception as exc:
        await service.close_client()
        raise HTTPException(status_code=500, detail=str(exc))


# Always expose the standard OpenAI-compatible path.
app.add_api_route(
    "/v1/chat/completions",
    _send_conversation,
    methods=["POST"],
    name="chat_completions",
)

# If API_PREFIX is configured, expose the prefixed path as well.
# This keeps both forms working and makes Postman testing easier.
if api_prefix:
    app.add_api_route(
        f"/{api_prefix}/v1/chat/completions",
        _send_conversation,
        methods=["POST"],
        name="chat_completions_prefixed",
    )

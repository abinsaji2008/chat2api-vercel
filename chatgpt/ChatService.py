import hashlib
import random
import uuid
from fastapi import HTTPException
from chatgpt.fp import get_fp
from chatgpt.proofofWork import get_dpl
from chatgpt.chatFormat import api_messages_to_chat, stream_response, format_not_stream_response, head_process_response
from api.models import model_proxy
from utils.Client import Client
from utils.configs import chatgpt_base_url_list, chatgpt_cookie_dict, history_disabled, upload_by_url, auth_key, oai_language

class ChatService:
    def __init__(self, origin_token=None):
        self.req_token = origin_token or ""
        self.s = None
        self.ss = None

    async def set_dynamic_data(self, data):
        self.data = data
        self.fp = get_fp(self.req_token)
        self.proxy_url = self.fp.pop("proxy_url", None)
        self.impersonate = self.fp.pop("impersonate", "safari15_3")
        self.user_agent = self.fp.get("user-agent")
        self.origin_model = data.get("model", "gpt-4o")
        self.resp_model = model_proxy.get(self.origin_model, self.origin_model)
        self.req_model = self.origin_model
        self.account_id = data.get("Chatgpt-Account-Id")
        self.parent_message_id = data.get("parent_message_id") or str(uuid.uuid4())
        self.conversation_id = data.get("conversation_id")
        self.history_disabled = data.get("history_disabled", history_disabled)
        self.api_messages = data.get("messages", [])
        self.max_tokens = data.get("max_tokens", 2147483647)
        self.host_url = random.choice(chatgpt_base_url_list)
        self.s = Client(proxy=self.proxy_url, impersonate=self.impersonate, cookies=chatgpt_cookie_dict)
        self.ss = self.s
        self.base_url = self.host_url + "/backend-api"
        self.base_headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": self.host_url,
            "referer": self.host_url + "/",
            "oai-language": oai_language,
        }
        self.base_headers.update(self.fp)
        if self.account_id:
            self.base_headers["chatgpt-account-id"] = self.account_id
        if auth_key:
            self.base_headers["authkey"] = auth_key
        await get_dpl(self)

    async def get_chat_requirements(self):
        return None

    async def prepare_send_conversation(self):
        messages, self.prompt_tokens = await api_messages_to_chat(self, self.api_messages, upload_by_url)
        self.chat_headers = self.base_headers.copy()
        self.chat_headers["accept"] = "text/event-stream"
        self.chat_request = {
            "action": "next",
            "messages": messages,
            "model": self.req_model,
            "parent_message_id": self.parent_message_id,
            "conversation_mode": {"kind": "primary_assistant"},
            "timezone": "Asia/Kolkata",
            "timezone_offset_min": 330,
            "history_and_training_disabled": self.history_disabled,
            "force_use_sse": True,
            "suggestions": [],
        }
        if self.conversation_id:
            self.chat_request["conversation_id"] = self.conversation_id

    async def send_conversation(self):
        response = await self.s.post_stream(
            self.base_url + "/conversation",
            headers=self.chat_headers,
            json=self.chat_request,
            timeout=60,
            stream=True,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text[:500])
        if "text/event-stream" not in response.headers.get("Content-Type", ""):
            return await response.json()
        stream, started = await head_process_response(response.aiter_lines())
        if not started:
            raise HTTPException(status_code=403, detail="Upstream did not return a conversation stream")
        if self.data.get("stream", False):
            return stream_response(self, stream, self.resp_model, self.max_tokens)
        return await format_not_stream_response(
            stream_response(self, stream, self.resp_model, self.max_tokens),
            self.prompt_tokens,
            self.max_tokens,
            self.resp_model,
        )

    async def close_client(self):
        if self.s:
            await self.s.close()

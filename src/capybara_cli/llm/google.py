from __future__ import annotations

from typing import AsyncIterator

import httpx

from .base import BaseLLMProvider, LLMResponse, Message, Role


class GoogleProvider(BaseLLMProvider):
    def __init__(self, model: str = "gemini-1.5-pro", api_key: str | None = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.api_base = self.api_base or "https://generativelanguage.googleapis.com/v1beta"
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            timeout=self.timeout,
        )
    
    async def chat(self, messages: list[Message], **kwargs) -> LLMResponse:
        contents = []
        system_instruction = None
        
        for m in messages:
            if m.role == Role.SYSTEM:
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                role = "user" if m.role == Role.USER else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content}],
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.temperature),
                "maxOutputTokens": kwargs.get("max_tokens", self.max_tokens),
                "topP": kwargs.get("top_p", self.top_p),
            },
        }
        
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        
        if "tools" in kwargs:
            payload["tools"] = [{"functionDeclarations": kwargs["tools"]}]
        
        url = f"/models/{self.model}:generateContent?key={self.api_key}"
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        candidate = data["candidates"][0]
        content = candidate["content"]["parts"][0].get("text", "")
        
        tool_calls = []
        if "functionCall" in candidate["content"]["parts"][0]:
            fc = candidate["content"]["parts"][0]["functionCall"]
            tool_calls.append({
                "id": fc["name"],
                "type": "function",
                "function": {
                    "name": fc["name"],
                    "arguments": fc["args"],
                }
            })
        
        return LLMResponse(
            content=content,
            input_tokens=data.get("usageMetadata", {}).get("promptTokenCount", 0),
            output_tokens=data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
            model=self.model,
            finish_reason=candidate.get("finishReason", ""),
            tool_calls=tool_calls,
        )
    
    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]:
        contents = []
        system_instruction = None
        
        for m in messages:
            if m.role == Role.SYSTEM:
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                role = "user" if m.role == Role.USER else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content}],
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.temperature),
                "maxOutputTokens": kwargs.get("max_tokens", self.max_tokens),
            },
        }
        
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        
        url = f"/models/{self.model}:streamGenerateContent?key={self.api_key}"
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json
                    try:
                        chunk = json.loads(line)
                        if "candidates" in chunk:
                            content = chunk["candidates"][0]["content"]["parts"][0].get("text", "")
                            if content:
                                yield content
                    except:
                        pass
    
    def count_tokens(self, text: str) -> int:
        return len(text.split()) * 2

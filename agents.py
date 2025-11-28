from __future__ import annotations

import json
import webbrowser
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


class ChatBackend(Protocol):
    def send(self, messages: List[Dict[str, str]]) -> str: ...


@dataclass
class AgentPlan:
    agent: str
    arguments: Dict[str, Any]
    user_visible_message: Optional[str] = None


class ConversationBuffer:
    """Utility to manage rolling chat history with a system prompt."""

    def __init__(self, system_prompt: str, limit: int) -> None:
        self.limit = max(limit, 2)
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt.strip()}
        ]

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self._trim()

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def snapshot(self) -> List[Dict[str, str]]:
        return list(self.messages)

    def last_assistant(self) -> Optional[str]:
        for message in reversed(self.messages):
            if message["role"] == "assistant":
                return message["content"]
        return None

    def _trim(self) -> None:
        if len(self.messages) <= self.limit:
            return
        system_message = self.messages[0]
        self.messages = [system_message] + self.messages[-(self.limit - 1) :]


class Planner:
    def __init__(
        self,
        client: ChatBackend,
        buffer: ConversationBuffer,
        error_cls: type[Exception] = RuntimeError,
    ) -> None:
        self.client = client
        self.buffer = buffer
        self.error_cls = error_cls

    def plan(self) -> AgentPlan:
        raw_response = self.client.send(self.buffer.snapshot())
        parsed = self._extract_json(raw_response)
        if not parsed:
            raise self.error_cls("Планировщик не смог вернуть валидный JSON.")
        agent = str(parsed.get("agent", "qa")).lower().strip()
        arguments = parsed.get("arguments") or {}
        if not isinstance(arguments, dict):
            arguments = {}
        user_visible_message = parsed.get("user_visible_message")
        if user_visible_message is not None:
            user_visible_message = str(user_visible_message).strip()
        return AgentPlan(agent=agent, arguments=arguments, user_visible_message=user_visible_message)

    @staticmethod
    def _extract_json(payload: str) -> Optional[Dict[str, Any]]:
        try:
            start = payload.index("{")
            end = payload.rindex("}") + 1
        except ValueError:
            return None
        try:
            return json.loads(payload[start:end])
        except json.JSONDecodeError:
            return None


class QuestionAnswerAgent:
    """LLM-backed agent that answers user questions."""

    def __init__(self, client: ChatBackend, buffer: ConversationBuffer) -> None:
        self.client = client
        self.buffer = buffer

    def run(self) -> str:
        return self.client.send(self.buffer.snapshot())


class BrowserAgent:
    """Agent that opens websites in the default system browser."""

    def run(self, arguments: Dict[str, Any]) -> str:
        url = (arguments.get("url") or "").strip()
        if not url:
            raise ValueError("BrowserAgent требует поле 'url'.")
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        webbrowser.open(url)
        tab_label = arguments.get("label")
        if tab_label:
            tab_label = str(tab_label).strip()
        action_message = (
            f"Открываю вкладку '{tab_label}' по адресу {url}"
            if tab_label
            else f"Открываю браузер по адресу {url}"
        )
        return action_message


class AgentRegistry:
    def __init__(self, qa_agent: QuestionAnswerAgent, browser_agent: BrowserAgent) -> None:
        self.qa_agent = qa_agent
        self.browser_agent = browser_agent

    def run(self, plan: AgentPlan) -> str:
        if plan.agent == "browser":
            return self.browser_agent.run(plan.arguments)
        return self.qa_agent.run()



from __future__ import annotations

import sys
from typing import List, Dict, Any

import requests

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    TIMEOUT,
    SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    CHAT_HISTORY_LIMIT,
    PLANNER_HISTORY_LIMIT,
)
from agents import (
    AgentPlan,
    AgentRegistry,
    BrowserAgent,
    ConversationBuffer,
    Planner,
    QuestionAnswerAgent,
)


def _select_user_reply(plan: AgentPlan, agent_reply: str) -> str:
    if plan.agent == "qa":
        return agent_reply
    if plan.user_visible_message:
        return plan.user_visible_message
    return agent_reply


class DeepSeekClientError(RuntimeError):
    """Исключение верхнего уровня для ошибок клиента DeepSeek."""


class DeepSeekChatClient:
    """Минимальный клиент для эндпоинта /chat/completions."""

    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> None:
        self.api_key = api_key.strip()
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._session = requests.Session()

    def send(self, messages: List[Dict[str, str]]) -> str:
        """Отправляет список сообщений в DeepSeek и возвращает ответ ассистента."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise DeepSeekClientError(f"Ошибка сети или API: {exc}") from exc
        except ValueError as exc:
            raise DeepSeekClientError("Не удалось распарсить ответ DeepSeek") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise DeepSeekClientError(f"Неожиданный формат ответа: {data}") from exc

        return content.strip()


def main() -> None:
    print("DeepSeek Chat (введите 'exit' чтобы выйти)\n")
    client = DeepSeekChatClient(
        api_key=DEEPSEEK_API_KEY,
        api_url=DEEPSEEK_API_URL,
        model=DEEPSEEK_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT,
    )

    user_buffer = ConversationBuffer(SYSTEM_PROMPT, CHAT_HISTORY_LIMIT)
    planner_buffer = ConversationBuffer(PLANNER_SYSTEM_PROMPT, PLANNER_HISTORY_LIMIT)
    planner = Planner(client=client, buffer=planner_buffer, error_cls=DeepSeekClientError)
    qa_agent = QuestionAnswerAgent(client=client, buffer=user_buffer)
    browser_agent = BrowserAgent()
    registry = AgentRegistry(qa_agent=qa_agent, browser_agent=browser_agent)

    while True:
        try:
            user_prompt = input("Вы: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break

        if not user_prompt:
            continue

        if user_prompt.lower() in {"exit", "quit", "выход"}:
            print("Пока!")
            break

        user_buffer.add_user(user_prompt)
        planner_buffer.add_user(f"Пользователь: {user_prompt}")

        try:
            plan = planner.plan()
        except DeepSeekClientError as exc:
            print(f"[Планировщик] {exc} — переключаюсь в режим QA.")
            plan = AgentPlan(agent="qa", arguments={}, user_visible_message=None)

        try:
            agent_reply = registry.run(plan)
        except Exception as exc:  # noqa: BLE001
            error_message = f"[Ошибка агента {plan.agent}] {exc}"
            print(error_message)
            user_buffer.add_assistant(error_message)
            planner_buffer.add_assistant(error_message)
            continue

        final_reply = _select_user_reply(plan, agent_reply)
        print(f"DeepSeek: {final_reply}\n")
        user_buffer.add_assistant(final_reply)
        planner_buffer.add_assistant(
            f"Агент '{plan.agent}' завершил действие. Ответ: {final_reply}"
        )


if __name__ == "__main__":
    try:
        main()
    except DeepSeekClientError as exc:
        print(f"Не удалось инициализировать чат: {exc}", file=sys.stderr)
        sys.exit(1)



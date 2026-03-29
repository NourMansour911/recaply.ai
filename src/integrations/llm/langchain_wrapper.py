from typing import List, Optional, AsyncGenerator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    AIMessageChunk,
)
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun
from .llm_enums import OpenAIEnums
from .providers.openai_provider import OpenAIProvider


class ChatOpenAICompatible(BaseChatModel):

    def __init__(self, provider: OpenAIProvider, model: str , **kwargs):
        super().__init__(**kwargs)
        self.provider = provider
        self.model = model

    @property
    def _llm_type(self) -> str:
        return "openai_compatible"

    def _convert_messages(self, messages: List[BaseMessage]) -> List[dict]:
        chat_history = []

        for m in messages:
            if isinstance(m, HumanMessage):
                role = OpenAIEnums.USER.value
            elif isinstance(m, AIMessage):
                role = OpenAIEnums.ASSISTANT.value
            elif isinstance(m, SystemMessage):
                role = OpenAIEnums.SYSTEM.value
            else:
                continue

            chat_history.append({"role": role, "content": m.content})

        return chat_history

    def _apply_stop(self, text: str, stop: Optional[List[str]]) -> str:
        if not stop:
            return text

        for token in stop:
            if token in text:
                text = text.split(token)[0]
        return text

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:

        model_to_use = kwargs.get("model", self.model)

        output = self.provider.generate_text(
            prompt=messages[-1].content,
            chat_history=self._convert_messages(messages[:-1]),
            model=model_to_use,
            temperature=kwargs.get("temperature"),
            max_tokens=kwargs.get("max_tokens"),
        )

        output = self._apply_stop(output, stop)

        ai_message = AIMessage(content=output)

        return ChatResult(
            generations=[ChatGeneration(message=ai_message)],
            llm_output={"model": model_to_use},
        )

    async def _acall(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:

        model_to_use = kwargs.get("model", self.model)

        output = await self.provider.agenerate_text(
            prompt=messages[-1].content,
            chat_history=self._convert_messages(messages[:-1]),
            model=model_to_use,
            temperature=kwargs.get("temperature"),
            max_tokens=kwargs.get("max_tokens"),
        )

        output = self._apply_stop(output, stop)

        ai_message = AIMessage(content=output)

        return ChatResult(
            generations=[ChatGeneration(message=ai_message)],
            llm_output={"model": model_to_use},
        )

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> AsyncGenerator[ChatGeneration, None]:

        model_to_use = kwargs.get("model", self.model)

        async for token in self.provider.stream_text(
            prompt=messages[-1].content,
            chat_history=self._convert_messages(messages[:-1]),
            model=model_to_use,
        ):
            if run_manager:
                await run_manager.on_llm_new_token(token)

            yield ChatGeneration(message=AIMessageChunk(content=token))
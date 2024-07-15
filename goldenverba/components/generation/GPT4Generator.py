import os
from typing import List, AsyncGenerator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from goldenverba.components.interfaces import Generator
from goldenverba.components.generation.message_history import (
    create_runnable_with_message_history,
)

load_dotenv()


class GPT4Generator(Generator):
    """
    GPT4 Generator using LangChain with OpenAI's API.
    """

    def __init__(self):
        super().__init__()
        self.name = "GPT4-O"
        self.description = "Generator using OpenAI's gpt-4o model via LangChain"
        self.requires_library = ["langchain-openai"]
        self.requires_env = ["OPENAI_API_KEY"]
        self.streamable = True
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.context_window = 10000

        # Set up LangChain tracing
        tracer = LangChainTracer()
        callback_manager = CallbackManager([tracer])

        # Initialize ChatOpenAI
        self.client = ChatOpenAI(
            model_name=self.model_name,
            temperature=0.0,
            streaming=True,
            callbacks=[tracer],
        )

        # Set up runnable with message history
        self.runnable = create_runnable_with_message_history(self.client)

    async def generate_stream(
        self,
        queries: List[str],
        context: List[str],
        conversation: List = None,
    ) -> AsyncGenerator[dict[str, str], None]:
        """Generate a stream of response dicts based on queries, contexts, and conversation."""
        if not os.getenv("OPENAI_API_KEY"):
            yield {"message": "Missing OpenAI API Key", "finish_reason": "stop"}
            return

        messages = self.prepare_messages(queries, context, conversation or [])

        try:
            async for chunk in self.client.astream(messages):
                if chunk.content:
                    yield {
                        "message": chunk.content,
                        "finish_reason": None,
                    }
            yield {"message": "", "finish_reason": "stop"}

        except Exception as e:
            yield {"message": f"Error: {str(e)}", "finish_reason": "error"}

    def prepare_messages(
        self, queries: List[str], context: List[str], conversation: List
    ) -> List[HumanMessage | SystemMessage | AIMessage]:
        """Prepare messages for the chatbot."""
        system_message = SystemMessage(
            content="""You are Verba, The Golden RAGtriever, a chatbot for Retrieval Augmented Generation (RAG). You will receive a user query and context pieces that have a semantic similarity to that specific query. Please answer these user queries only using their provided context. If the provided documentation does not provide enough information, say so. If the user asks questions about you as a chatbot specifically, answer them naturally. If the answer requires code examples encapsulate them with ```programming-language-name ```. Don't do pseudo-code."""
        )

        messages = [system_message]

        for message in conversation:
            if message.type == "human":
                messages.append(HumanMessage(content=message.content))
            elif message.type == "ai":
                messages.append(AIMessage(content=message.content))

        query = " ".join(queries)
        user_context = " ".join(context)
        user_message = HumanMessage(
            content=f"Please answer this query: '{query}' with this provided context: {user_context}"
        )
        messages.append(user_message)

        return messages

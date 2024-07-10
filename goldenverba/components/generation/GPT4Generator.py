import os
from dotenv import load_dotenv
from goldenverba.components.interfaces import Generator
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage

load_dotenv()

# Set up LangSmith environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# Make sure LANGCHAIN_API_KEY is set in your .env file


class GPT4Generator(Generator):
    """
    GPT4 Generator with LangSmith tracing using ChatOpenAI.
    """

    def __init__(self):
        super().__init__()
        self.name = "GPT4-O"
        self.description = "Generator using OpenAI's GPT-4 model with LangSmith tracing"
        self.requires_library = ["langchain-openai", "langsmith"]
        self.requires_env = ["OPENAI_API_KEY", "LANGCHAIN_API_KEY"]
        self.streamable = True
        self.model_name = "gpt-4"
        self.context_window = 10000

        # Set up LangChain tracing
        tracer = LangChainTracer()
        callback_manager = CallbackManager([tracer])

        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=0.0,
            streaming=True,
            callbacks=[tracer],
        )

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = None,
    ):
        """
        Generate a stream of response dicts based on a list of queries and list
        of contexts, and includes conversational context
        """
        if not os.getenv("OPENAI_API_KEY"):
            yield {
                "message": "Missing OpenAI API Key",
                "finish_reason": "stop",
            }
            return

        messages = self.prepare_messages(queries, context, conversation)

        try:
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield {
                        "message": chunk.content,
                        "finish_reason": None,
                    }
            yield {
                "message": "",
                "finish_reason": "stop",
            }

        except Exception as e:
            yield {
                "message": f"Error: {str(e)}",
                "finish_reason": "stop",
            }

    def prepare_messages(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict[str, str],
    ) -> list[BaseMessage]:
        """
        Prepares a list of messages formatted for a Retrieval Augmented
        Generation chatbot system
        """
        messages = [
            SystemMessage(
                content=(
                   """ You are the RoboRail Assistant, an AI expert on the RoboRail machine manufactured by HGG Profiling Equipment b.v. Your primary function is to answer honestly but briefly, assist users with operation, maintenance, troubleshooting, and safety of the RoboRail. Here are your key responsibilities:

                1. Answer user queries concisely based on the RoboRail manual and your knowledge base. For complex queries, offer a brief response first, then ask if more detail is needed.

                2. Guide users through troubleshooting by asking targeted questions to diagnose issues efficiently.

                3. Provide clear, step-by-step instructions for operations, maintenance, and calibrations when requested.

                4. Emphasize safety, ensuring users are aware of potential hazards and proper protocols.

                5. If asked about your AI capabilities, answer honestly but briefly, refocusing on RoboRail assistance.

                6. Use proper formatting for code examples or machine commands:
                ```language-name
                code here
                ```

                7. Clarify ambiguous queries promptly. Ask follow-up questions to ensure accurate and helpful information.

                8. For issues beyond your scope, advise contacting HGG customer support and provide contact information.

                9. Diagnose problems systematically by asking users relevant questions about symptoms, recent changes, or error messages.

                10. Offer concise initial responses, then ask if the user needs more detailed explanations or instructions.

                Your goal is to be a knowledgeable, efficient, and safety-conscious assistant for all aspects of the RoboRail machine, providing concise yet comprehensive support.
                """)
            )
        ]

        if conversation:
            for message in conversation:
                if message.type == "human":
                    messages.append(HumanMessage(content=message.content))
                elif message.type == "ai":
                    messages.append(AIMessage(content=message.content))

        query = " ".join(queries)
        user_context = " ".join(context)
        messages.append(
            HumanMessage(
                content=f"Please answer this query: '{query}' with this provided context: {user_context}"
            )
        )

        return messages

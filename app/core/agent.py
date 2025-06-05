"""
AI Shop Assist Agent

A minimal agent using LangGraph for product recommendations.
"""

from typing import TypedDict, Annotated, List, Optional, Dict
import operator
import pandas as pd
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langgraph.graph import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


from .llm import LLMManager
from .. import config

# System prompt for the shopping assistant
SHOPPING_ASSISTANT_PROMPT = (
    "You are an AI shopping assistant. Your goal is to help users find and understand products. "
    "When given a product ID, provide detailed information about that product. "
    "If no product ID is provided, help the user find relevant products based on their needs."
)

# Define state schema
class ShopState(TypedDict):
    user_query: str  # Original user query
    context: Annotated[list, operator.add]  # Context for agent to use
    messages: Annotated[list[AnyMessage], add_messages]  # Message history
    final_response: str  # Final response to the user
    product_id: Optional[str]  # Product ID if specified

class ShopAgent:
    """AI Shop Assist Agent"""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.products_df = self._load_products()
        self.tools = [
            Tool(
                name="get_product_details",
                description="Get detailed information about a specific product",
                func=self._get_product_details
            )
        ]
        self.llm_bind_tools = self.llm_manager.llm.bind_tools(self.tools)
    
    def _load_products(self) -> pd.DataFrame:
        """Load products from configured CSV path"""
        if not config.PRODUCT_CSV.exists():
            raise FileNotFoundError(f"Product data file not found: {config.PRODUCT_CSV}")
        return pd.read_csv(config.PRODUCT_CSV)
    
    def _get_product_details(self, product_id: Optional[str]) -> str:
        """Get product details from DataFrame"""
        try:
            product = self.products_df[self.products_df['id'] == product_id].iloc[0]
            return (
                f"Product Details for {product_id}:\n"
                f"- Name: {product['name']}\n"
                f"- Price: {product['discount_price']} (was {product['actual_price']})\n"
                f"- Ratings: {product['ratings']} ({product['no_of_ratings']} ratings)\n"
                f"- Link: {product['link']}\n"
                f"- Image: {product['image']}\n"
            )
        except Exception:
            return f"Product with ID {product_id} not found."



def should_continue(state: ShopState) -> str:
    # If the last message is a tool result, continue to assistant
    # Otherwise, end the conversation
    if state["messages"] and isinstance(state["messages"][-1], AIMessage):
        return "assistant"
    return END

shopagent = ShopAgent()

def agent_builder(state,
                  function,
                  tool_list: List[Tool]):
    default_builder = StateGraph(ShopState)

    # Define nodes: these do the work
    default_builder.add_node(function.__name__, function)
    default_builder.add_node("tools", ToolNode(tool_list))

    # Define edges: these determine how the control flow moves
    default_builder.add_edge(START, function.__name__)
    default_builder.add_conditional_edges(
        function.__name__,
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        tools_condition,
    )
    # Add condition to check if we should continue or end after tools

    default_builder.add_conditional_edges(
        "tools",
        should_continue,
        {
            function.__name__: function.__name__,
            END: END
        }
    )

    return default_builder.compile()

def shopper_agent(state: ShopState):
    query = state["user_query"]
    context = state.get("context", [])
    formatted_context = "\n\n".join(context)
    message = f"""User query: {query}
    Additional context:
    {formatted_context}
    """
    response = shopagent.llm_bind_tools.invoke([
        SystemMessage(content=SHOPPING_ASSISTANT_PROMPT),
        HumanMessage(content=message)
    ])
    return {
        "messages": [response],
        "final_response": response.content
    }

graph = agent_builder(ShopState, shopper_agent, shopagent.tools)



def get_response(query: str, context: List[str] = None, conversation_id: str = None) -> str:
        """Get response from the agent"""
        initial_state = {
            "user_query": query,
            "context": context or [],
            "messages": [],
            "final_response": "",
            "product_id": None  # Will be extracted from query/context if present
        }
        
        # Configure thread for checkpointer
        thread = {"configurable": {"thread_id": conversation_id or "default"}}
        
        result = graph.invoke(initial_state, thread)
        return result["final_response"] if result.get("final_response") else "No response generated." 
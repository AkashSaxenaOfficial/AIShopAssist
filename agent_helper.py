from aws_lambda_powertools import Logger
import operator
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage
from langgraph.prebuilt import tools_condition
from langgraph.graph import MessagesState, add_messages
from langgraph.prebuilt import ToolNode
from kuberai.common.rag_helper import (APIManager,
                                       LLMManager,
                                       WeaviateVectorStore,
                                       extract_reasoning,
                                       post_ws_data)
from kuberai.common.system_prompt import (kuber_ai_agent_prompt,
                                          financial_planner_agent_prompt,
                                          mutual_fund_advisor_agent_prompt,
                                          insurance_advisor_agent_prompt,

                                          tax_advisor_agent_prompt,


                                          loan_advisor_agent_prompt,
                                          credit_card_advisor_agent_prompt,

                                          stock_market_advisor_agent_prompt,
                                          budgeting_advisor_agent_prompt,
                                      
                                          router_agent_prompt,
                                          fraud_prevention_agent_prompt)


import re
import boto3
import json
import time
from typing import List, Dict, Any, Annotated, TypedDict

# Setup logging
logger = Logger()

api_manager = APIManager()
llm_manager = LLMManager(api_manager)
weaviate_mng = WeaviateVectorStore(
    api_manager=api_manager,
    vector_db_class="SM_Document",
    attribute_with_vector="content")

llm_with_tools = llm_manager.claude_llm.bind_tools(llm_manager.tools)


# Define state schema
class KuberState(TypedDict):
    user_query: str  # Original user query
    user_id: str  # User ID
    required_agents: List[str]  # Agents to be consulted
    agent_responses: Dict[str, str]  # Responses from worker agents
    context: Annotated[list, operator.add]  # Context for agents to use
    final_response: str  # Final response to the user
    user_profile: str
    messages: Annotated[list[AnyMessage], add_messages]


# Node functions for the graph
def analyze_query(state: KuberState):
    """Analyze the user query and determine which agents to consult."""
    query = state["user_query"]
    # Use Kuber.AI to determine which agents to consult
    message = f"""User query: {query}"""
    response = llm_manager.claude_llm.invoke([
        SystemMessage(content=router_agent_prompt),
        HumanMessage(content=message)
    ])
    # Parse the response to get the list of required agents
    agents_text = response.content.strip().lower()
    required_agents = [agent.strip() for agent in agents_text.split(",")]

    return {
        "required_agents": required_agents,
    }


def should_continue(state: KuberState) -> str:
    # If the last message is a tool result, continue to assistant
    # Otherwise, end the conversation
    if state["messages"] and isinstance(state["messages"][-1], AIMessage):
        return "assistant"
    return END


def route_to_agents(state: KuberState):
    """Route the query to the appropriate agent based on required_agents."""
    required_agents = state.get("required_agents", [])

    # Check if any agents are required
    if not required_agents:
        return "default_advisor"
    # Prioritize tax_advisor for tax queries
    if "tax_advisor" in required_agents:
        return "tax_advisor"
    # Otherwise follow the original priority order
    elif "financial_planner" in required_agents:
        return "financial_planner"
    elif "mutual_fund_advisor" in required_agents:
        return "mutual_fund_advisor"
    elif "insurance_advisor" in required_agents:
        return "insurance_advisor"
    elif "loan_advisor" in required_agents:
        return "loan_advisor"


    elif "credit_card_advisor" in required_agents:
        return "credit_card_advisor"
    elif "budgeting_advisor" in required_agents:
        return "budgeting_advisor"
  
  
    elif "stock_market_advisor" in required_agents:
        return "stock_market_advisor"


      
    elif "fraud_prevention" in required_agents:
        return "fraud_prevention"



    else:
        # Default fallback
        return "default_advisor"


def financial_planner(state: KuberState):
    """Financial planner agent."""
    query = state["user_query"]
    context = state.get("context", [])

    # Format context
    formatted_context = "\n\n".join(context)

    # Generate response
    message = f"""User query: {query}

    Additional context:
    {formatted_context}
    """

    response = llm_with_tools.invoke([
        SystemMessage(content=financial_planner_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"financial_planner": response.content}
    }





def credit_card_advisor(state: KuberState):
    """Credit card advisor agent."""
    query = state["user_query"]
    context = state.get("context", [])

    # Format context
    formatted_context = "\n\n".join(context)

    # Generate response
    message = f"""User query: {query}

    Additional context:
    {formatted_context}

    Based on this information, provide your expert credit card advice.
    You have access to the following tools:
    1. user_financial_health - Get user's financial health data
    2. weaviate_search - Search knowledge base for relevant information
    3. brave_search - Search web for real-time information

    Use these tools as needed to gather information and provide comprehensive credit card recommendations."""

    response = llm_with_tools.invoke([
        SystemMessage(content=credit_card_advisor_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"credit_card_advisor": response.content},
        "messages": [response]
    }

  
  
  

def mutual_fund_advisor(state: KuberState):
    """Mutual fund advisor agent."""
    query = state["user_query"]
    message = f"""User query: {query}"""

    response = llm_with_tools.invoke([
        SystemMessage(content=mutual_fund_advisor_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"mutual_fund_advisor": response.content}
    }


def insurance_advisor(state: KuberState):
    """Insurance advisor agent."""
    query = state["user_query"]

    # Bind tools to LLM
    # llm_with_tools = llm_manager.bind_tools(TOOLS, parallel_tool_calls=False)

    # Generate response
    message = f"""User query: {query}"""

    response = llm_with_tools.invoke([
        SystemMessage(content=insurance_advisor_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"insurance_advisor": response.content}
    }



def loan_advisor(state: KuberState):
    """Loan advisor agent."""
    query = state["user_query"]
    context = state.get("context", [])
    
    # Format context
    formatted_context = "\n\n".join(context)
    
   
    message = f"""User query: {query}

    Additional context:
    {formatted_context}

    Based on this information, provide your expert loan advice.
    You have access to the following tools:
    1. user_financial_health - Get user's financial health data
    2. weaviate_search - Search knowledge base for relevant information
    3. brave_search - Search web for real-time information

    Use these tools as needed to gather information and provide comprehensive loan recommendations."""

    # Initialize messages if not present in state
    if "messages" not in state or not state["messages"]:
        state["messages"] = []
        
    # Add human message to messages
    human_msg = HumanMessage(content=message)
    state["messages"].append(human_msg)
    
    response = llm_with_tools.invoke([
        SystemMessage(content=loan_advisor_agent_prompt),
        HumanMessage(content=message)
    ])
    
    # Add AI response to messages
    state["messages"].append(response)
    
    # Return the response to be added to agent_responses and updated messages

    return {
        "agent_responses": {"loan_advisor": response.content},
        "messages": state["messages"]
    }


def stock_market_advisor(state: KuberState):
    """Stock Market Advisor agent."""
    query = state["user_query"]
    context = state.get("context", [])

    formatted_context = "\n\n".join(context)


    message = f"""User query: {query}

    Additional context:
    {formatted_context}

    Based on this information, provide your expert stock market advice.
    You have access to the following tools:
    1. user_financial_health - Get user's financial health data
    2. weaviate_search - Search knowledge base for relevant information
    3. brave_search - Search web for real-time information

    Use these tools as needed to gather information and provide comprehensive stock market recommendations."""

    response = llm_with_tools.invoke([
        SystemMessage(content=stock_market_advisor_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"stock_market_advisor": response.content},
        "messages": [response]
    }


def budgeting_advisor(state: KuberState):
    """Budgeting advisor agent."""
    query = state["user_query"]
    context = state.get("context", [])

    # Format context
    formatted_context = "\n\n".join(context)

    # Generate response
    message = f"""User query: {query}

    Additional context:
    {formatted_context}

    You must take into consideration the user's profile and expense categories which you have access to.
    Then analyze the user's financial profile and spending patterns across different expense categories.
    Based on this information, provide your expert budgeting advice.
    You have access to the following tools:
    1. user_financial_health - Get user's financial health data
    2. weaviate_search - Search knowledge base for relevant information
    3. brave_search - Search web for real-time information

    Use these tools as needed to gather information and provide comprehensive budgeting recommendations."""

    response = llm_with_tools.invoke([
        SystemMessage(content=budgeting_advisor_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"budgeting_advisor": response.content},
        "messages": [response]
    }


def default_advisor(state: KuberState):
    """Generate a default response when no specific agents are required."""
    query = state["user_query"]
    messages = state.get("messages", [])

    # Generate response
    response = llm_with_tools.invoke([
        SystemMessage(content=kuber_ai_agent_prompt),
        HumanMessage(content=query)
    ])

    # Update messages with the response
    messages.append(response)

    # Set both the agent response and final response
    return {
        "agent_responses": {"kuber_ai": response.content},
        "final_response": response.content,
        "messages": messages
    }


def combine_responses(state: KuberState):
    """Combine the responses from all agents."""
    query = state["user_query"]
    agent_responses = state.get("agent_responses", {})
    context = state.get("context", [])
    messages = state["messages"]
    formatted_messages = [m.content for m in messages]

    # Format the agent responses
    formatted_responses = "\n\n".join([
        f"{agent_name.replace('_', ' ').title()}:\n{response}"
        for agent_name, response in agent_responses.items()
    ])

    # Format context
    formatted_context = "\n\n".join(context)

    # Generate final response
    message = f"""User query: {query}

    Additional context:
    {formatted_context}

    Specialist responses:
    {formatted_responses}
    {formatted_messages[-1]}

    Based on these specialist responses and context, provide a comprehensive answer to the user's query. 
    Be concise but thorough. Synthesize the information from all specialists into a coherent response.
    Focus on providing actionable advice tailored to the Indian financial context."""

    response = llm_manager.claude_llm.invoke([
        SystemMessage(content=kuber_ai_agent_prompt),
        HumanMessage(content=message)
    ])

    return {"final_response": response.content}


def tax_advisor(state: KuberState):
    """Tax advisor agent."""
    query = state["user_query"]
    context = state.get("context", [])

    # Format context
    formatted_context = "\n\n".join(context)

    # Generate response
    message = f"""User query: {query}

    Additional context:
    {formatted_context}

    Based on this information, provide your expert tax planning advice.
    You have access to the following tools:
    1. user_financial_health - Get user's financial health data
    2. weaviate_search - Search knowledge base for relevant information
    3. brave_search - Search web for real-time information

    Use these tools as needed to gather information and provide comprehensive advice."""

    response = llm_with_tools.invoke([
        SystemMessage(content=tax_advisor_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response to be added to agent_responses
    return {
        "agent_responses": {"tax_advisor": response.content}
    }

def fraud_prevention(state: KuberState):
    """Fraud Prevention agent."""
    query = state["user_query"]
    # Generate response
    message = f"""User query: {query}

    Based on this information, provide your expert fraud prevention advice.
    You have access to the following tools:
    1. user_financial_health - Get user's financial health data
    2. weaviate_search - Search knowledge base for relevant information
    3. brave_search - Search web for real-time information

    Use these tools as needed to gather information and provide comprehensive advice."""

    response = llm_with_tools.invoke([
        SystemMessage(content=fraud_prevention_agent_prompt),
        HumanMessage(content=message)
    ])

    # Return the response in the correct format
    return {
        "agent_responses": {"fraud_prevention": response.content},
        "messages": [response]
    }

def assistant(state: KuberState):
    response = llm_with_tools.invoke([
        SystemMessage(content=router_agent_prompt),
        HumanMessage(content=state["user_query"])
    ])

    return {"messages": response}


def agent_builder(state,
                  function,
                  tool_list: List[Tool]):
    default_builder = StateGraph(KuberState)

    # Define nodes: these do the work
    default_builder.add_node(function.__name__, function)
    default_builder.add_node("tools", ToolNode(tool_list))

    # Define edges: these determine how the control flow moves
    default_builder.add_edge(START, function.__name__)
    default_builder.add_conditional_edges(
        function.__name__,
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
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


def agent_graph():
    # Build the graph
    builder = StateGraph(KuberState)

    default_advisor_agent = agent_builder(KuberState, default_advisor, llm_manager.tools)
    financial_planner_agent = agent_builder(KuberState, financial_planner, llm_manager.tools)
    mutual_fund_advisor_agent = agent_builder(KuberState, mutual_fund_advisor, llm_manager.tools)
    insurance_advisor_agent = agent_builder(KuberState, insurance_advisor, llm_manager.tools)
    tax_advisor_agent = agent_builder(KuberState, tax_advisor, llm_manager.tools)
    budgeting_advisor_agent = agent_builder(KuberState, budgeting_advisor, llm_manager.tools)
                                                                                                    

    stock_market_advisor_agent = agent_builder(KuberState, stock_market_advisor, llm_manager.tools)

    loan_advisor_agent = agent_builder(KuberState, loan_advisor, llm_manager.tools)
    credit_card_advisor_agent = agent_builder(KuberState, credit_card_advisor, llm_manager.tools)                                                                                           
    fraud_prevention_agent = agent_builder(KuberState, fraud_prevention, llm_manager.tools)




    # Add nodes
    builder.add_node("query_router", analyze_query)
    builder.add_node("financial_planner", financial_planner_agent)
    builder.add_node("mutual_fund_advisor", mutual_fund_advisor_agent)
    builder.add_node("insurance_advisor", insurance_advisor_agent)
    builder.add_node("tax_advisor", tax_advisor_agent)
    

    builder.add_node("loan_advisor", loan_advisor_agent)

  
    builder.add_node("credit_card_advisor", credit_card_advisor_agent)
    builder.add_node("stock_market_advisor", stock_market_advisor_agent)
    builder.add_node("budgeting_advisor", budgeting_advisor_agent)


    builder.add_node("fraud_prevention", fraud_prevention_agent)
    builder.add_node("default_advisor", default_advisor_agent)
    builder.add_node("kuber_aggregator", combine_responses)

    # Add edges
    builder.add_edge(START, "query_router")

    # Connect analyze_query to agents using conditional routing
    builder.add_conditional_edges(
        "query_router",
        route_to_agents,
        {
            "financial_planner": "financial_planner",
            "mutual_fund_advisor": "mutual_fund_advisor",
            "insurance_advisor": "insurance_advisor",
            "loan_advisor": "loan_advisor",
            "tax_advisor": "tax_advisor",
       
            "credit_card_advisor": "credit_card_advisor",
            "fraud_prevention": "fraud_prevention",
            "stock_market_advisor": "stock_market_advisor",
            "budgeting_advisor": "budgeting_advisor",


            "default_advisor": "default_advisor"
        }
    )

    # Connect agents to combine_responses
    builder.add_edge("financial_planner", "kuber_aggregator")
    builder.add_edge("mutual_fund_advisor", "kuber_aggregator")
    builder.add_edge("loan_advisor", "kuber_aggregator")
    builder.add_edge("insurance_advisor", "kuber_aggregator")
    builder.add_edge("tax_advisor", "kuber_aggregator")
    builder.add_edge("budgeting_advisor", "kuber_aggregator")


    builder.add_edge("credit_card_advisor", "kuber_aggregator")
    builder.add_edge("stock_market_advisor", "kuber_aggregator")


    builder.add_edge("fraud_prevention", "kuber_aggregator")
    builder.add_edge("default_advisor", "kuber_aggregator")
    builder.add_edge("kuber_aggregator", END)

    # Compile the graph with memory checkpointing
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph


main_graph = agent_graph()


def retrieve_agent_response(
        messages: dict,
        connection_id: str,
        conversation_id: str,
        message_id: str,
        api_gateway_client: boto3.client,
        script_process: int = 0) -> tuple[str, str]:
    initial_state = {
        "user_query": messages["current_msg"],
        "user_id": messages["user_id"],
        "required_agents": [],
        "agent_responses": {},
        "context": [],
        "user_profile": messages["user_profile"]
    }
    lang: str = "en-US"  # Default language
    bulk: int = 10
    kuber_response: str = ""
    stream_logs: list = []

    thread = {"configurable": {"thread_id": conversation_id}}
    result = main_graph.invoke(initial_state, thread)
    response = result["final_response"]

    response, reasoning = extract_reasoning(response)

    # check language is present else pass default lang
    lang_match = re.match(r"\[lang:([\w-]+)\]", response)
    logger.info("lang_match: %s", lang_match)
    if lang_match:
        lang = lang_match.group(1)
    else:
        logger.warning("No language found in response. Using default language: %s", lang)
    lang_message = json.dumps({"lang": lang})

    # Connect API Gateway: Webhook Stream
    post_ws_data(api_gateway_client, connection_id, lang_message)

    # First Set of Stream: As Starting message
    start_message = {
        "start": True,
        "conversation_id": conversation_id,
        "message_id": message_id,
    }
    start_message_json = json.dumps(start_message)
    post_ws_data(api_gateway_client, connection_id, start_message_json)

    # Start Streaming the Agent response
    tokens = re.split(r"( )", response)
    previous_token_stream = None
    sub_time = time.time()
    for i in range(0, len(tokens), bulk):
        current_token_stream = time.time()
        token = "".join(tokens[i: i + bulk])
        stream_text = json.dumps({"text": token})
        post_ws_data(api_gateway_client, connection_id, stream_text)
        kuber_response += token
        duration = (
            0 if previous_token_stream is None else current_token_stream - previous_token_stream
        )
        stream_logs.append(
            str({"token": token, "time": current_token_stream, "duration": round(duration, 4)})
        )
        previous_token_stream = current_token_stream
    logger.info("Time taken to send the response: %.6f seconds.", time.time() - sub_time)

    end_message = json.dumps({"end": True, "reasoning": reasoning})
    post_ws_data(api_gateway_client, connection_id, end_message)



    logger.info(
        "agent_response",
        extra={
            "model_name": "agent",
            "kuber_response": kuber_response,
            "stream_logs": stream_logs,
            "streaming_count": len(stream_logs),
            "reasoning": reasoning,
        },
    )
    return kuber_response, lang


def local_agent_response(
        messages: dict,
        conversation_id: str,
) -> tuple[str, str]:
    initial_state = {
        "user_query": messages["current_msg"],
        "user_id": messages["user_id"],
        "required_agents": [],
        "agent_responses": {},
        "context": [],
        "user_profile": messages["user_profile"]
    }

    thread = {"configurable": {"thread_id": conversation_id}}
    result = main_graph.invoke(initial_state, thread)
    response = result["final_response"]

    response, reasoning = extract_reasoning(response)

    return response, reasoning
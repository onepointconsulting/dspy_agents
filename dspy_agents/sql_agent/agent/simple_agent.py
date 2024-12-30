from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.base import RunnableBinding

from dspy_agents.config import cfg
from dspy_agents.sql_agent.sql_tools import sql_list_tables_wrapper, sql_info_tables_wrapper, sql_query, sql_query_checker
from dspy_agents.main.callbacks import ReActCallback


# Define the function that determines whether to continue or not
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END

# Define the function that calls the model
def create_call_model(model: RunnableBinding):
    def call_model(state: MessagesState):
        messages = state['messages']
        response = model.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}
    return call_model


def create_workflow(model: RunnableBinding, tools: list[callable]) -> CompiledStateGraph:
    workflow = StateGraph(MessagesState)

    agent_node = "agent"
    tools_node = "tools"
    workflow.add_node(agent_node, create_call_model(model))
    workflow.add_node(tools_node, ToolNode(tools))

    workflow.add_edge(START, agent_node)
    # We now add a conditional edge
    workflow.add_conditional_edges(
        # First, we define the start node. We use `agent`.
        # This means these are the edges taken after the `agent` node is called.
        agent_node,
        # Next, we pass in the function that will determine which node is called next.
        should_continue,
    )
    workflow.add_edge(tools_node, agent_node)
    checkpointer = MemorySaver()

    app = workflow.compile(checkpointer=checkpointer)
    return app


def execute_query(query: str, callbacks: list[ReActCallback] = []) -> str:
    
    tools = [sql_list_tables_wrapper(callbacks), sql_info_tables_wrapper(callbacks), sql_query, sql_query_checker]
    model = cfg.llm.bind_tools(tools)

    app = create_workflow(model, tools)
    final_state = app.invoke(
        {"messages": [
            SystemMessage(content="""You are a SQL agent designed to interact with tools which extract information from a database. When a questions is asked you retrieve information from existing tables. 
If the information cannot be found in the database, you say so."""),
            HumanMessage(content=query)
        ]},
        config={"configurable": {"thread_id": 42}}
    )
    final_response = final_state["messages"][-1].content
    return final_response
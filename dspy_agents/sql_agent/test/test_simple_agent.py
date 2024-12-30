from dspy_agents.sql_agent.agent.simple_agent import create_workflow, execute_query
from dspy_agents.main.callbacks import ReActCallback
from dspy_agents.logger import logger

def test_create_workflow():
    app = create_workflow()
    assert app is not None, "Workflow should have been returned"

def test_table_list():
    response = execute_query("Can you list me all tables in the database?")
    assert response is not None, "No table list available"
    print(response)


class LoggerReActCallback(ReActCallback):

    def on_tool(self, tool_name: str, tool_args: dict):
        logger.info("Tool: %s: tool_args: %s", tool_name, tool_args)

    def on_observe(self, observation: str):
        logger.info("Tool observation", observation)


def test_list_actors():
    response = execute_query("Can you list all actors in the database?", [LoggerReActCallback()])
    assert response is not None, "No actor list available"
    print(response)


def test_countries_with_most_cities():
    response = execute_query("Which countries have the most cities in the database?")
    assert response is not None, "No countries with cities available"
    print(response)
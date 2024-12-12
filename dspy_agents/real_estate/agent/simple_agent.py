import dspy
from dspy.predict.react import Tool
from dspy_agents.real_estate.tools.tools import (
    location_search,
    property_search,
    property_identifier,
)
from dspy_agents.real_estate.agent.CallbackReAct import CallbackReAct, ReActCallback
from dspy.utils.callback import BaseCallback
from dspy_agents.logger import logger


def create_simple_agent(callbacks: list[ReActCallback] = []):
    agent = CallbackReAct(
        signature="question -> answer",
        tools=[
            Tool(
                location_search,
                name="Location search",
                desc="Based on some location in the United Kingdom find an location identifier which can be used to get the property search.",
                args={
                    "location": "The location from a query, like e.g. 'NW2 5JE' or 'Willesden Green'[str]"
                },
            ),
            Tool(
                property_identifier,
                name="Find property identifier",
                desc="Based on a property type, like e.g 'apartment', 'new development', 'house' returns a code which can be used by the property search.",
                args={"property_type": "The expression with the property type[str]"},
            ),
            Tool(
                property_search,
                name="Property search",
                desc="Based on a location, a maximum price and a currency finds multiple real estate properties. The currency is given in a 3 leeter abbreviation, like USD, EUR or GBP",
                args={
                    "location_identifier": "The identifier of the location used by Savills. Example: 'Id_43379 Category_Postcode'[str]",
                    "max_price": "The minimum price a specific currency, like e.g: '100000'[Optional[int]]",
                    "max_price": "The maximum price a specific currency, like e.g: '500000'[int]",
                    "currency": "A currency identifier like 'GBP', 'USD', 'EUR'[str]",
                    "property_types": "The list of property types as specific codes[list[str]]",
                },
            ),
        ],
        react_callbacks=callbacks,
    )
    return agent


# 1. Define a custom callback class that extends BaseCallback class
class AgentLoggingCallback(BaseCallback):

    # 2. Implement on_module_end handler to run a custom logging code.
    def on_module_end(self, call_id, outputs, exception):
        step = "Reasoning" if self._is_reasoning_output(outputs) else "Acting"
        logger.info(f"== {step} Step ===")
        for k, v in outputs.items():
            logger.info(f"  {k}: {v}")
        logger.info("\n")

    def _is_reasoning_output(self, outputs):
        return any(k.startswith("Thought") for k in outputs.keys())


# 3. Set the callback to DSPy setting so it will be applied to program execution
dspy.configure(callbacks=[AgentLoggingCallback()])

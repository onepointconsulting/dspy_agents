from pathlib import Path
from dspy_agents.real_estate.agent.simple_agent import agent


def predict_property(question: str, file_name: str):
    prediction = agent(
        question=f"""
{question}Try to be as detailed as possible. If you mention a property, let us know about the location, the price and some details about it. Please use markdown in your response.
"""
    )
    if prediction.answer:
        examples = Path("./examples")
        if not examples.exists():
            examples.mkdir(parents=True)
        with open(examples / file_name, "w", encoding="utf-8") as f:
            f.write(prediction.answer)
    else:
        return "There is no answer. Sorry."


def test_simple_agent_willesden_green():
    predict_property(
        "Can you find a property in Willesden Green for 500000 UK pounds?",
        "willesden_500000.txt",
    )


def test_simple_agent_dollis_hill():
    predict_property(
        "Can you find a property in Dollis Hill between 100000 and 1000000 UK pounds?",
        "dollis_hill_1000000.txt",
    )


def test_simple_agent_manchester():
    predict_property(
        "Can you find an apartment in Manchester between 100000 and 1000000 UK pounds?",
        "manchester.txt",
    )


def test_simple_agent_cambridge():
    predict_property(
        "Can you find an apartment or a house in Cambridge between 100000 and 1000000 UK pounds?",
        "cambridge.txt",
    )


def test_simple_agent_nottingham():
    predict_property(
        "Can you find an apartment or a house in Nottigham between 100000 and 1000000 dollars?",
        "cambridge.txt",
    )


if __name__ == "__main__":
    test_simple_agent_willesden_green()
    # test_simple_agent_dollis_hill()
    # test_simple_agent_manchester()
    # test_simple_agent_cambridge()
    # test_simple_agent_nottingham()

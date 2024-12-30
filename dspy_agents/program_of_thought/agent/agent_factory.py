import dspy
from dspy_agents.program_of_thought.agent.CallbackProgramOfThought import (
    CallbackProgramOfThought,
    ProgramOfThoughtCallback,
)


class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers"""

    question = dspy.InputField()
    answer = dspy.OutputField(
        desc="often between 1 and 5 words", prefix="Question’s Answer:"
    )


def create_coding_agent(
    callbacks: list[ProgramOfThoughtCallback], max_iters: int = 3
) -> CallbackProgramOfThought:

    pot = CallbackProgramOfThought(
        BasicQA, callbacks, max_iters, import_white_list=["numpy"]
    )
    return pot

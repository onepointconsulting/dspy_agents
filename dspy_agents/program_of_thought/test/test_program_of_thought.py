import re
from typing import Optional
from dspy_agents.config import cfg
import logging
from datetime import datetime, timezone

from dspy_agents.program_of_thought.agent.agent_factory import create_coding_agent
from dspy_agents.program_of_thought.agent.CallbackProgramOfThought import (
    ProgramOfThoughtCallback,
)
from dspy.primitives.prediction import Prediction


class PrintCallback(ProgramOfThoughtCallback):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_code_generate(self, code_data: Prediction) -> None:
        self.logger.info("Code generated.")
        self.write_generated(code_data)

    def on_parse_code(self, code_block: str, error: Optional[str]) -> None:
        self.logger.info(f"Parsed code: {code_block}")

    def on_execute_code(self, code: str, output: str, error: Optional[str]) -> None:
        self.logger.info(f"Code generation output: {output}")
        if error:
            self.logger.error(f"Code generation error: {error}")

    def on_code_regenerate(self, code_data: Prediction) -> None:
        self.logger.info("Code regenerated.")
        self.write_generated(code_data)

    def on_generate_answer(self, answer: str) -> None:
        self.logger.info(f"Generated answer: {answer}")

    def write_generated(self, code_data: Prediction):
        now = datetime.now(timezone.utc)
        iso_timestamp = now.isoformat()
        iso_timestamp = re.sub(r"[\W]", "", re.sub(r"\..+", "", iso_timestamp))
        output_file = cfg.generation_folder / f"code_generate_{iso_timestamp}.py"
        reasoning = cfg.generation_folder / f"code_generate_{iso_timestamp}.txt"
        if "generated_code" in code_data:
            try:
                output_file.write_text(code_data["generated_code"])
            except Exception as e:
                self.logger.error(f"Failed to write: {output_file}")
                self.logger.exception(e)
        if "reasoning" in code_data:
            reasoning.write_text(code_data["reasoning"])

    def on_module_end(self, call_id: int, results: any, error: any):
        if not error:
            self.logger.info(f"Module end: {call_id} -> {results}")
        else:
            self.logger.error(f"Module end: {call_id} -> {error}")


if __name__ == "__main__":
    questions = [
        """Can you please calculate the matrix multiplication of 
[[1, 2], [5, 9]] by [[5, 4, 7], [5, 4, 7]]?
    """,
        """
Which is the sandard deviation of the following array: [1, 3, 4, 5, 4]""",
        """Can you calculate the geometric mean of [1, 3, 4, 5, 4]?""",
    ]

    agent = create_coding_agent(callbacks=[PrintCallback()], max_iters=3)
    logger = logging.getLogger("Program of thought test")
    for question in questions:
        result = agent(question=question)
        logger.info(result)
        print(result.answer)

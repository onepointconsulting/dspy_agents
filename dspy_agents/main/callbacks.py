from typing import Optional
import asyncio

from dspy_agents.real_estate.agent.CallbackReAct import ReActCallback
from dspy_agents.program_of_thought.agent.CallbackProgramOfThought import (
    ProgramOfThoughtCallback,
)
from dspy_agents.logger import logger
from dspy.primitives.prediction import Prediction


class WSCallBack(ReActCallback):

    def __init__(self, send, loop):
        super().__init__()
        self.send = send
        self.loop = loop
        self.thoughts = []

    def on_thought(self, thought: str):
        logger.info(thought)
        self.thoughts.append(thought)
        all_thoughts = "".join([f"<li>{t}</li>" for t in self.thoughts])
        future = asyncio.run_coroutine_threadsafe(self.send(all_thoughts), self.loop)
        future.result()

    def on_tool(self, tool_name: str, tool_args: dict):
        logger.info(f"{tool_name} - {tool_args}")

    def on_observe(self, observation: str):
        if observation:
            logger.info(observation)


class WSCodeCallBack(ProgramOfThoughtCallback):

    def __init__(self, send, loop):
        super().__init__()
        self.send = send
        self.loop = loop
        self.code = []

    def join_snippets(self) -> str:
        all_snippets = "".join([f"<p>Code:</p><pre>{c}</pre>" for c in self.code])
        return all_snippets

    def on_start(self):
        self.code.append("<p>Starting &#128640</p>")
        self.send_to_ui("".join(self.code))

    def send_to_ui(self, html: str):
        future = asyncio.run_coroutine_threadsafe(self.send(html), self.loop)
        future.result()

    def on_code_generate(self, code_data: Prediction) -> None:
        logger.info(code_data)
        generated_code = code_data.generated_code
        self.code.append(generated_code)
        all_snippets = self.join_snippets()
        self.send_to_ui(all_snippets)

    def on_parse_code(self, code_block: str, error: Optional[str]) -> None:
        logger.info(f"Code block: {code_block}")

    def on_execute_code(self, code: str, output: str, error: Optional[str]) -> None:
        if not error:
            logger.info(f"Code block: {code}")
            all_snippets = self.join_snippets()
            all_snippets += f"""<p>Result:</p><p>{output}</p>"""
            self.send_to_ui(all_snippets)
        else:
            logger.error(f"Error: {code}")

    def on_code_regenerate(self, code_data: Prediction) -> None:
        self.on_code_generate(code_data)

    def on_generate_answer(self, answer: str) -> None:
        logger.info(f"Answer: {answer}")

    def on_module_end(self, call_id: int, results: any, error: any) -> None:
        logger.info(f"End: {call_id}")

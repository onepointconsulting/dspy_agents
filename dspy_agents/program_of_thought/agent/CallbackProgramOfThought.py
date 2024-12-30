from typing import Optional
from dspy.predict.program_of_thought import ProgramOfThought
from dspy.primitives.prediction import Prediction

import logging


class ProgramOfThoughtCallback:
    """A base class for defining callback handlers for Program of Thought components."""

    def on_start(self) -> None:
        pass

    def on_code_generate(self, code_data: Prediction) -> None:
        pass

    def on_parse_code(self, code_block: str, error: Optional[str]) -> None:
        pass

    def on_execute_code(self, code: str, output: str, error: Optional[str]) -> None:
        pass

    def on_code_regenerate(self, code_data: Prediction) -> None:
        pass

    def on_generate_answer(self, answer: str) -> None:
        pass

    def on_module_end(self, call_id: int, results: any, error: any) -> None:
        pass


class CallbackProgramOfThought(ProgramOfThought):

    def __init__(
        self,
        signature,
        callbacks: list[ProgramOfThoughtCallback] = [],
        max_iters=3,
        import_white_list=None,
    ):
        super().__init__(signature, max_iters, import_white_list)
        self.callbacks = callbacks
        self.logger = logging.getLogger(self.__class__.__name__)

    def loop_callbacks(self, func: callable):
        for callback in self.callbacks:
            try:
                func(callback)
            except Exception as e:
                self.logger.error(f"Callback {callback.__class__.__name__} failed: {e}")

    def handle_parse_error(self, parse_error: str):
        message = f"Code parsing failed: {parse_error}"
        self.logger.error(message)

    def execute_code(self, code):
        try:
            code, output, error = super().execute_code(code)
            if output is None:
                output = exec(code)
                if output:
                    error = None
            return code, output, error
        except Exception as e:
            self.logger.error(f"Could not run code: {e}")
            output = eval(code)
            return code, output, ""

    def forward(self, **kwargs):
        input_kwargs = {
            field_name: kwargs[field_name] for field_name in self.input_fields
        }
        self.loop_callbacks(lambda callback: callback.on_start())

        code_data = self.code_generate(**input_kwargs)
        self.loop_callbacks(lambda callback: callback.on_code_generate(code_data))

        parsed_code, parse_error = self.parse_code(code_data)
        self.loop_callbacks(
            lambda callback: callback.on_parse_code(parsed_code, parse_error)
        )

        # Don't try to execute the code if it didn't parse
        if parse_error:
            self.handle_parse_error(parse_error)
            return parse_error

        code, output, error = self.execute_code(parsed_code)
        self.loop_callbacks(
            lambda callback: callback.on_execute_code(code, output, error)
        )

        hop = 0
        while hop < self.max_iters and error:
            self.logger.warning(f"Error in code execution (Attempt {hop + 1})")
            input_kwargs.update({"previous_code": code, "error": error})
            code_data = self.code_regenerate(**input_kwargs)
            self.loop_callbacks(lambda callback: callback.on_code_regenerate(code_data))

            parsed_code, error = self.parse_code(code_data)
            # Don't try to execute the code if it didn't parse
            if parse_error:
                self.handle_parse_error(parse_error)
                return parse_error
            code, output, error = self.execute_code(parsed_code)
            self.loop_callbacks(
                lambda callback: callback.on_execute_code(code, output, error)
            )

            hop += 1
            if hop == self.max_iters:
                error = "Max hops reached. Error persists."
                self.logger.error(error)
                return error
        input_kwargs.update({"final_generated_code": code, "code_output": output})
        answer_gen_result = self.generate_answer(**input_kwargs)
        self.loop_callbacks(
            lambda callback: callback.on_generate_answer(answer_gen_result)
        )

        return answer_gen_result

from typing import Callable, Any

import dspy
from dspy.predict import ReAct


class ReActCallback:
    """A base class for defining callback handlers for ReAct components."""

    def on_thought(self, thought: str):
        pass

    def on_tool(self, tool_name: str, tool_args: dict):
        pass

    def on_observe(self, observation: str):
        pass


class CallbackReAct(ReAct):
    def __init__(
        self,
        signature: str,
        tools: list[Callable],
        react_callbacks: list[ReActCallback],
        max_iters: int = 5,
    ):
        super().__init__(signature, tools, max_iters)
        self.react_callbacks = react_callbacks

    def forward(self, **input_args):
        trajectory = {}

        def format(trajectory_: dict[str, Any], last_iteration: bool):
            adapter = dspy.settings.adapter or dspy.ChatAdapter()
            signature_ = dspy.Signature(f"{', '.join(trajectory_.keys())} -> x")
            return adapter.format_fields(signature_, trajectory_, role="user")

        for idx in range(self.max_iters):
            pred = self.react(
                **input_args,
                trajectory=format(
                    trajectory, last_iteration=(idx == self.max_iters - 1)
                ),
            )

            trajectory[f"thought_{idx}"] = pred.next_thought
            trajectory[f"tool_name_{idx}"] = pred.next_tool_name
            trajectory[f"tool_args_{idx}"] = pred.next_tool_args

            for callback in self.react_callbacks:
                callback.on_thought(pred.next_thought)
                if pred.next_tool_name:
                    callback.on_tool(pred.next_thought, pred.next_tool_args)

            try:
                trajectory[f"observation_{idx}"] = self.tools[pred.next_tool_name](
                    **pred.next_tool_args
                )
                for callback in self.react_callbacks:
                    callback.on_observe(trajectory[f"observation_{idx}"])
            except Exception as e:
                trajectory[f"observation_{idx}"] = f"Failed to execute: {e}"

            if pred.next_tool_name == "finish":
                break

        extract = self.extract(
            **input_args, trajectory=format(trajectory, last_iteration=False)
        )
        return dspy.Prediction(trajectory=trajectory, **extract)

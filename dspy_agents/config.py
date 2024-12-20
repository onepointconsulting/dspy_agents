from pathlib import Path
import os

import dspy
from dspy_agents.logger import logger

from dotenv import load_dotenv

load_dotenv()


class Config:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    assert (
        openai_api_key is not None
    ), "Please specify the OPENAI_API_KEY environment variable."

    openai_api_model = os.getenv("OPENAI_API_MODEL")
    assert (
        openai_api_model is not None
    ), "Please specify the OPENAI_API_MODEL environment variable."
    logger.info(f"Using model {openai_api_model}")

    dspy.configure(lm=dspy.LM(openai_api_model))

    prompts_path = os.getenv("PROMPTS_PATH", (Path(__file__) / "prompts").as_posix())
    prompts_path = Path(prompts_path)
    assert prompts_path.exists(), f"The template path does not exist."

    generation_folder_str = os.getenv("GENERATION_FOLDER")
    assert generation_folder_str is not None, "Please specify a generation folder"
    generation_folder = Path(generation_folder_str)
    if not generation_folder.exists():
        generation_folder.mkdir(parents=True)


cfg = Config()

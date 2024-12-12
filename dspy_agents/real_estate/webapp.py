import asyncio
from dspy_agents.config import cfg

from fasthtml.common import (
    FastHTML,
    FileResponse,
    picolink,
    Div,
    P,
    A,
    Ul,
    Li,
    H1,
    H2,
    H3,
    Link,
    Blockquote,
    Script,
    MarkdownJS,
    HighlightJS,
    Form,
    Textarea,
    Img,
    NotStr,
)
from fasthtml.common import serve
from asyncer import asyncify

from dspy_agents.real_estate.agent.simple_agent import create_simple_agent
from dspy_agents.real_estate.agent.CallbackReAct import ReActCallback
from dspy_agents.logger import logger

ID_CARD = "card"
ID_HISTORY = "history"
ID_SPINNER = "spinner"

footer = Div(Div("@Copyright Onepoint Consulting"), id="footer", cls="footer container")

app = FastHTML(
    hdrs=(
        picolink,
        Link(href="/css/main.css", type="text/css", rel="stylesheet"),
        Script(src="/js/error.js"),
        Script(src="/js/main.js"),
        MarkdownJS(),
        HighlightJS(langs=["python", "javascript", "html", "css"]),
    ),
    htmlkw={"data-theme": "dark"},
    ftrs=(footer,),
    exts="ws",
)


@app.route("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    return FileResponse(f"assets/{fname}.{ext}")


@app.route("/")
def get():
    return Div(
        H1("Agents"),
        Div(
            Img(
                src="/images/agents_4c22344a-347f-4574-ba5b-8b2d587cba69.webp",
                cls="agents-image",
            ),
            Div(Blockquote(H2(A("Property Agent", href="/property")))),
            cls="grid",
        ),
        cls="main container",
    )


def createQuestionLinks(questions: list[str]) -> list[Li]:
    return [Li(A(q, href="#", cls="questionLink")) for q in questions]


@app.route("/property")
def get():
    question_links = [
        "Can you find properties in Aberdeen under 1 million pounds?",
        "Can you find properties in Cricklewood under 2 million pounds? Preferably some houses.",
        "Can you find houses in Liverpool under 1 million pounds?",
        "Can you find apartments near Barnett in London under 1 million pounds?",
        "Are there any properties in SW2 between 500000 and 1 million pounds?",
    ]
    return Div(
        H1("Property agent"),
        P("Examples"),
        Ul(*createQuestionLinks(question_links)),
        P("Please enter your real estate query and press ENTER"),
        Form(
            Textarea(cls="chat", id="question"),
            hx_trigger="keyup[key=='Enter']",
            target_id=ID_CARD,
            hx_swap="innerHTML",
            ws_send=True,
        ),
        Div(H3("Results", cls="card"), H3("Thinking", cls="card"), Div(id=ID_CARD), Div(id=ID_HISTORY), id="results"),
        cls="main container",
        hx_ext="ws",
        ws_connect="/property_agent",
    )


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


@app.ws("/property_agent")
async def ws(question: str, send):
    template = (cfg.prompts_path / "real_estate.txt").read_text()
    question = template.format(question=question)
    logger.info(question)
    await send(
        Div(
            Div(
                Img(src="/images/loading.svg", cls="loading"),
                "The agent is trying to fetch some properties. Please wait ...",
                area_busy="true",
                id=ID_SPINNER,
            ),
            id=ID_CARD,
        )
    )
    loop = asyncio.get_event_loop()

    async def send_ws(text: str):
        await send(Div(NotStr(text), id=ID_HISTORY))

    agent = create_simple_agent([WSCallBack(send_ws, loop)])
    prediction = await asyncify(agent)(question=question)
    await send(Div(NotStr(prediction.answer), id=ID_CARD))
    logger.info(f"Sent {prediction.answer}")


if __name__ == "__main__":
    serve()

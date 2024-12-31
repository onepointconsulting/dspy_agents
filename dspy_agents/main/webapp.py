import asyncio
from pathlib import Path
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
from dspy_agents.program_of_thought.agent.agent_factory import create_coding_agent
from dspy_agents.logger import logger
from dspy_agents.main.callbacks import WSCallBack, WSCodeCallBack, WSToolsCallBack
from dspy_agents.sql_agent.agent.simple_agent import execute_sql_agent_query


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
    me = Path(__file__)
    assets = me.parent.parent.parent / "assets"
    return FileResponse(f"{assets.as_posix()}/{fname}.{ext}")


@app.route("/")
def get():
    agents = [
        {"name": "Property Agent", "href": "/property"},
        {"name": "Coder Agent", "href": "/coder"},
        {"name": "SQL Query Agent", "href": "/sql"}
    ]
    agents_block = [Div(Blockquote(H2(A(a["name"], href=a["href"])))) for a in agents]
    return Div(
        H1("Agents"),
        Div(
            Img(
                src="/images/agents_4c22344a-347f-4574-ba5b-8b2d587cba69.webp",
                cls="agents-image",
            ),
            Div(*agents_block),
            cls="grid",
        ),
        cls="main container",
    )


def createQuestionLinks(questions: list[str]) -> list[Li]:
    return [Li(A(q, href="#", cls="questionLink")) for q in questions]


def generate_agent_layout(
    question_links: list[str], title: str, instruction: str, ws_connect: str
):
    return Div(
        Div(H1(title), A(NotStr("&#8962; Home"), href="/", style="font-size: 1.5em"), cls="title-header"),
        P("Examples"),
        Ul(*createQuestionLinks(question_links)),
        P(instruction),
        Form(
            Textarea(cls="chat", id="question"),
            hx_trigger="keyup[key=='Enter']",
            target_id=ID_CARD,
            hx_swap="innerHTML",
            ws_send=True,
        ),
        Div(
            H3("Results", cls="card hidden"),
            H3("Thinking", cls="card hidden"),
            Div(id=ID_CARD),
            Div(id=ID_HISTORY),
            id="results",
        ),
        cls="main container",
        hx_ext="ws",
        ws_connect=ws_connect,
    )


@app.route("/property")
def get():
    question_links = [
        "Can you find properties in Aberdeen under 1 million pounds?",
        "Can you find properties in Cricklewood under 2 million pounds? Preferably some houses.",
        "Can you find houses in Liverpool under 1 million pounds?",
        "Can you find apartments near Barnett in London under 1 million pounds?",
        "Are there any properties in SW2 between 500000 and 1 million pounds?",
    ]
    return generate_agent_layout(
        question_links,
        "Property agent",
        "Please enter your real estate query and press ENTER",
        "/property_agent",
    )


@app.route("/coder")
def get():
    question_links = [
        "Can you please calculate the matrix multiplication of [[1, 2], [5, 9]] by [[5, 4, 7], [5, 4, 7]]?",
        "Can you calculate the geometric mean of [1, 3, 4, 5, 4]?",
        "Can you calculate the inverse matrix of [[1, 2], [5, 9]]?",
        "Can you multipy these two matrices [[4, 2], [5, 9]] and [[1, 0], [0, 1]]?",
    ]
    return generate_agent_layout(
        question_links,
        "Coder",
        "Please enter your question to the coding agent",
        "/coding_agent",
    )


@app.route("/sql")
def get():
    question_links = [
        "Can you list all tables in the database?",
        "Can you list all actors in the database?",
        "Which customers have ordered the most products?",
        "Which countries have the most cities in the database?",
        "How many orders are there in the database?",
        "From which countries came most orders?",
        "Which actors were involved in the ACADEMY DINOSAUR movie?",
        "Which are the most popular movies in the database?",
        "Which are the most popular film categories by movie rental?",
        "What do you know about the actor ROCK DUKAKIS based on the current database? In which movies did he act?"
    ]
    return generate_agent_layout(
        question_links,
        "SQL Query Agent",
        "Please enter your question to the SQL query agent",
        "/sql_agent",
    )


def build_send_ws(send: callable):
    async def send_ws(text: str):
        await send(Div(NotStr(text), id=ID_HISTORY))
    return send_ws


async def send_prediction(send: callable, prediction: any):
    answer = prediction if isinstance(prediction, str) else prediction.answer
    await send(Div(NotStr(answer), id=ID_CARD))
    logger.info(f"Sent {answer}")


async def display_loading(send, message: str):
    await send(
        Div(
            Div(
                Img(src="/images/loading.svg", cls="loading"),
                message,
                area_busy="true",
                id=ID_SPINNER,
            ),
            id=ID_CARD,
        )
    )


@app.ws("/property_agent")
async def ws(question: str, send):
    template = (cfg.prompts_path / "real_estate.txt").read_text()
    question = template.format(question=question)
    logger.info(question)
    await display_loading(send, "The agent is trying to fetch some properties. Please wait ...")

    agent = create_simple_agent(
        [WSCallBack(build_send_ws(send), asyncio.get_event_loop())]
    )
    prediction = await asyncify(agent)(question=question)
    await send_prediction(send, prediction)


@app.ws("/coding_agent")
async def ws(question: str, send):

    await display_loading(send, "The agent is trying to calculate. Please wait ...")
    agent = create_coding_agent(
        [WSCodeCallBack(build_send_ws(send), asyncio.get_event_loop())]
    )
    prediction = await asyncify(agent)(question=question)
    await send_prediction(send, prediction)


@app.ws("/sql_agent")
async def ws(question: str, send):
    await display_loading(send, "The agent is trying to query the database ...")
    prediction = await asyncify(execute_sql_agent_query)(question, [WSToolsCallBack(build_send_ws(send), asyncio.get_event_loop())])
    await send_prediction(send, prediction)


if __name__ == "__main__":
    serve()

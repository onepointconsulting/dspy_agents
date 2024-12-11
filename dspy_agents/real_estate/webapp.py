from dspy_agents.config import cfg

from fasthtml.common import (
    FastHTML,
    FileResponse,
    picolink,
    Div,
    Article,
    P,
    A,
    Ul,
    Li,
    H1,
    H2,
    Link,
    Blockquote,
    Script,
    MarkdownJS,
    HighlightJS,
    Form,
    Textarea,
    Img,
    NotStr
)
from fasthtml.common import serve

from dspy_agents.real_estate.agent.simple_agent import create_simple_agent
from dspy_agents.logger import logger

ID_CARD = "card"
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


@app.route("/property")
def get():
    return Div(
        H1("Property agent"),
        P("Examples"),
        Ul(
            Li("Can you find properties in Aberdeen under 1 million pounds?"),
            Li(
                "Can you find properties in Cricklewood under 2 million pounds? Preferably some houses."
            ),
            Li("Can you find houses in Liverpool under 1 million pounds?"),
            Li(
                "Can you find apartments near Barnett in London under 1 million pounds?"
            ),
            Li("Are there any properties in SW2 between 500000 and 1 million pounds?"),
        ),
        P("Please enter your real estate query and press ENTER"),
        Form(
            Textarea(cls="chat", id="question"),
            hx_trigger="keyup[key=='Enter']",
            hx_indicator=f"#{ID_SPINNER}",
            target_id=ID_CARD,
            hx_swap="innerHTML",
            ws_send=True,
        ),
        Article(
            Img(src="/images/loading.svg", cls="loading"),
            "The agent is trying to fetch some properties. Please wait ...",
            area_busy="true",
            id=ID_SPINNER,
            cls="htmx-indicator",
        ),
        Div(id=ID_CARD, style="margin-top: -60px;"),
        cls="main container",
        hx_ext="ws",
        ws_connect="/property_agent",
    )


@app.ws("/property_agent")
async def ws(question: str, send):
    template = (cfg.prompts_path / "real_estate.txt").read_text()
    question = template.format(question=question)
    logger.info(question)
    agent = create_simple_agent()
    await send(Div(Article(
            Img(src="/images/loading.svg", cls="loading"),
            "The agent is trying to fetch some properties. Please wait ...",
            area_busy="true",
            id=ID_SPINNER,
        ), id=ID_CARD, style="margin-top: -60px;"))
    prediction = agent(question=question)
    await send(Div(NotStr(prediction.answer), id=ID_CARD, style="margin-top: -60px;"))
    logger.info(f"Sent {prediction.answer}")


if __name__ == "__main__":
    serve()

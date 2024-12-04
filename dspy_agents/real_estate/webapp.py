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
)
from fasthtml.common import serve
from markdown import markdown

from dspy_agents.real_estate.agent.simple_agent import agent

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
        P("Please enter your real estate query and press ENTER"),
        P("Examples"),
        Ul(
            Li("Can you find properties in Aberdeen under 1 million pounds?"),
            Li("Can you find properties in Cricklewood under 2 million pounds? Preferably some houses."),
            Li("Can you find houses in Liverpool under 1 million pounds?"),
            Li("Can you find apartments near Swiss Cottage in London under 1 million pounds?")
        ),
        Form(
            Textarea(cls="chat", id="question"),
            hx_post="/property_agent",
            hx_trigger="keyup[key=='Enter']",
            hx_indicator=f"#{ID_SPINNER}",
            target_id=ID_CARD,
            hx_swap="innerHTML",
        ),
        Article("The agent is trying to fetch some properties. Please wait ...", area_busy="true", id=ID_SPINNER, cls="htmx-indicator"),
        Div(id=ID_CARD, style="margin-top: 20px;"),
        cls="main container",
    )


@app.route("/property_agent")
def post(question: str):
    question = f"""
Here is the question:

{question}

Instructions: 

Try to be as detailed as possible. If you mention a property, let us know about the location, the price and some details about it. Please use plain html in your response.

If the search failed and you could not use the tools, just say that you could not find anything.

Here is the example of a valid answer:

<h2>Properties in Portsmouth Under £500,000</h2>

<div class="property">
    <h3>St James Park, Locksway Road, Southsea, PO4 8LD</h3>
    <p><strong>Price:</strong> Guide price £359,950 - £474,950</p>
    <p><strong>Size:</strong> 934 to 1,285 sq ft (86.77 to 119.38 sq m)</p>
    <p><strong>Features:</strong>
        Energy efficient newly built homes and bespoke conversion properties.
        Beautiful 2, 3, 4 & 5 bedroom newly built homes with parking and private gardens.
        Estimated A rated EPC, EV Charging, solar panels with optional battery storage & triple glazing.
        High specification kitchen including Neff appliances.
    </p>
    <p><a href="https://search.savills.com/property-detail/gbhqrscps240022" target="_blank">Property details</a></p>
</div>

<div class="property">
    <h3>Searle Drive, Gosport, Hampshire, PO12 4WE</h3>
    <p><strong>Price:</strong> Guide price £375,000</p>
    <p><strong>Features:</strong>
        Stunning and versatile Townhouses in a waterside location.
        Parking and EV option available.
        EPC rating - B.
        Private landscaped garden.
    </p>
    <p><a href="https://search.savills.com/property-detail/gbhqrscps240043" target="_blank">Property details</a></p>
</div>

"""
    print(question)
    prediction = agent(question=question)
    return prediction.answer


if __name__ == "__main__":
    serve()

from dataclasses import dataclass
from flask import Flask, url_for, request

import htmf as ht
from htmf import Safe


@dataclass
class Soup:
    name: str
    countries: list[str]
    is_chunky: bool


def SoupCard(id: int, soup: Soup) -> Safe:
    return ht.m(
        f"""
        <div class="card mb-2">
            <div class="card-body">
                <h5 class="{ ht.c("card-title", soup.is_chunky and 'text-danger') }" >
                    { ht.t(soup.name) }
                </h5>
                <p class="card-text">
                    Countries:
                    { ht.t(', '.join(soup.countries) if soup.countries else '?') }
                </p>
                <a href="{ ht.t(url_for('soup', id=id)) }" class="card-link">Go</a>
            </div>
        </div>
        """
    )


def SoupsCollection(soups: dict[int, Soup], limit: int) -> Safe:
    selected = list(soups.items())[:limit]

    return ht.m(
        f"""
        <div class="container">
            <h4>Showing first { ht.t(limit) } soups:</h4>
            { ht.t(SoupCard(*soup) for soup in selected) }
        </div>
        """
    )


def Layout(body: Safe, title: str):
    bootstrap = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    return ht.document(
        f"""
        <!doctype html>
        <html>
            <head>
                <title>{ ht.t(title) }</title>
                <link href="{ bootstrap }" rel="stylesheet">
            </head>
            <body>
                { body }
            </body>
        </html>
        """
    )


app = Flask(__name__)

# From the wiki
SOUPS = {
    1: Soup("Aguadito", ["Peru"], True),
    2: Soup("Ant egg soup", ["Laos", "Northeastern Thailand"], True),
    3: Soup("Beef noodle soup", ["East Asia"], False),
    4: Soup("Chicken soup", [], False),
    5: Soup("Tom Yum", ["Thailand"], True),
}


@app.route("/")
def index():
    limit = request.args.get("limit", type=int, default=len(SOUPS))
    return Layout(SoupsCollection(SOUPS, limit=limit), title="Soups list")


@app.route("/<int:id>")
def soup(id: int):
    found = SOUPS.get(id)
    if not found:
        return Layout(ht.t("Unknown soup id"), title="Soup 404")
    return Layout(SoupCard(id, found), title="Soups list")

from __future__ import annotations

from dash import html


def metric_card(title: str, value: str, subtitle: str) -> html.Div:
    return html.Div(
        className="metric-card",
        children=[
            html.Div(title, className="metric-card__title"),
            html.Div(value, className="metric-card__value"),
            html.Div(subtitle, className="metric-card__subtitle"),
        ],
    )

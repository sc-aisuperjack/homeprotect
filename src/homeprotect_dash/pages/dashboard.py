from __future__ import annotations

from dash import dcc, html

from homeprotect_dash.components.cards import metric_card
from homeprotect_dash.components.tables import dataframe_table
from homeprotect_dash.data.contracts import StructuredInsights
from homeprotect_dash.data.figures import (
    build_negative_themes_bar,
    build_nps_figure,
    build_nps_score_figure,
    build_outlier_table,
    build_segment_sentiment_heatmap,
    build_segment_volume_figure,
    build_sentiment_figure,
    build_theme_table,
)


def dashboard_layout(insights: StructuredInsights) -> html.Div:
    total_reviews = insights.summary.total_reviews
    avg_nps = round(sum(segment.nps.score for segment in insights.segments) / len(insights.segments))
    total_outliers = len(insights.outliers)

    positive_themes = build_theme_table(insights, "positive")
    negative_themes = build_theme_table(insights, "negative")
    outlier_table = build_outlier_table(insights)

    return html.Div(
        className="page",
        children=[
            html.Div(
                className="hero",
                children=[
                    html.Div(
                        [
                            html.H1("Homeprotect Review Intelligence"),
                            html.P(
                                "A stakeholder-ready dashboard for Claims, Pricing, and Customer Service insights."
                            ),
                        ]
                    ),
                    html.Div(
                        className="metrics-grid",
                        children=[
                            metric_card("Total reviews", f"{total_reviews}", "Processed by backend pipeline"),
                            metric_card("Average segment NPS", f"{avg_nps}", "Mean of inferred segment scores"),
                            metric_card("Outlier insights", f"{total_outliers}", "Interesting signals outside the main buckets"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="panel-grid",
                children=[
                    html.Div(
                        className="panel",
                        children=[
                            dcc.Graph(
                                figure=build_segment_volume_figure(insights),
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                    html.Div(
                        className="panel",
                        children=[
                            dcc.Graph(
                                figure=build_nps_score_figure(insights),
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                ],
            ),
            html.Div(
                className="panel-grid",
                children=[
                    html.Div(
                        className="panel panel--wide",
                        children=[
                            html.Div(
                                className="panel__header",
                                children=[
                                    html.H2("Sentiment mix"),
                                    dcc.RadioItems(
                                        id="sentiment-view-toggle",
                                        options=[
                                            {"label": "100% stacked", "value": "percentage"},
                                            {"label": "Count", "value": "count"},
                                        ],
                                        value="percentage",
                                        inline=True,
                                    ),
                                ],
                            ),
                            dcc.Graph(
                                id="sentiment-figure",
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                    html.Div(
                        className="panel panel--wide",
                        children=[
                            dcc.Graph(
                                figure=build_nps_figure(insights),
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                ],
            ),
            html.Div(
                className="panel-grid",
                children=[
                    html.Div(
                        className="panel panel--wide",
                        children=[
                            dcc.Graph(
                                figure=build_segment_sentiment_heatmap(insights),
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                    html.Div(
                        className="panel panel--wide",
                        children=[
                            dcc.Graph(
                                figure=build_negative_themes_bar(insights),
                                config={"displayModeBar": False},
                            )
                        ],
                    ),
                ],
            ),
            html.Div(
                className="panel-grid",
                children=[
                    html.Div(
                        className="panel panel--wide",
                        children=[
                            html.H2("Positive themes"),
                            dataframe_table(positive_themes, "positive-themes-table"),
                        ],
                    ),
                    html.Div(
                        className="panel panel--wide",
                        children=[
                            html.H2("Negative themes"),
                            dataframe_table(negative_themes, "negative-themes-table"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="panel",
                children=[
                    html.H2("Outlier insights"),
                    html.P(
                        "These are unusual but potentially strategic insights that do not neatly fit the three main business segments."
                    ),
                    dataframe_table(outlier_table, "outliers-table"),
                ],
            ),
        ],
    )
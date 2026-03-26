from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from homeprotect_dash.data.contracts import StructuredInsights


SEGMENT_ORDER = ["Claims", "Pricing", "Customer Service"]
SENTIMENT_ORDER = ["positive", "neutral", "negative"]
NPS_ORDER = ["promoters", "passives", "detractors"]


def segment_overview_table(insights: StructuredInsights) -> pd.DataFrame:
    rows: list[dict[str, int | str]] = []
    for segment in insights.segments:
        rows.append(
            {
                "segment": segment.segment,
                "reviews": segment.review_count,
                "positive": segment.sentiment.positive,
                "neutral": segment.sentiment.neutral,
                "negative": segment.sentiment.negative,
                "nps_score": segment.nps.score,
            }
        )
    return pd.DataFrame(rows)


def build_segment_volume_figure(insights: StructuredInsights) -> go.Figure:
    df = segment_overview_table(insights)
    fig = px.bar(
        df,
        x="segment",
        y="reviews",
        category_orders={"segment": SEGMENT_ORDER},
        title="Review volume by business area",
        text_auto=True,
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=360)
    return fig


def _sentiment_long_df(insights: StructuredInsights) -> pd.DataFrame:
    rows: list[dict[str, int | float | str]] = []
    for segment in insights.segments:
        total = segment.review_count
        for label in SENTIMENT_ORDER:
            count = getattr(segment.sentiment, label)
            percentage = (count / total * 100) if total else 0.0
            rows.append(
                {
                    "segment": segment.segment,
                    "sentiment": label.title(),
                    "count": count,
                    "percentage": round(percentage, 1),
                }
            )
    return pd.DataFrame(rows)


def build_sentiment_figure(
    insights: StructuredInsights, view_mode: str = "percentage"
) -> go.Figure:
    df = _sentiment_long_df(insights)

    if view_mode == "count":
        y_field = "count"
        chart_title = "Sentiment mix by segment (count)"
        y_axis_title = "Reviews"
        text_field = "count"
        tick_suffix = ""
    else:
        y_field = "percentage"
        chart_title = "Sentiment mix by segment (100 percent stacked)"
        y_axis_title = "Percentage of segment reviews"
        text_field = "percentage"
        tick_suffix = "%"

    fig = px.bar(
        df,
        x="segment",
        y=y_field,
        color="sentiment",
        barmode="stack",
        category_orders={
            "segment": SEGMENT_ORDER,
            "sentiment": [label.title() for label in SENTIMENT_ORDER],
        },
        title=chart_title,
        text=text_field,
        custom_data=["count", "percentage"],
    )

    fig.update_traces(
        texttemplate="%{text}" + tick_suffix,
        textposition="inside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Sentiment: %{fullData.name}<br>"
            "Count: %{customdata[0]}<br>"
            "Percentage: %{customdata[1]}%"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
        autosize=False,
        legend_title_text="",
        yaxis_title=y_axis_title,
    )

    if view_mode != "count":
        fig.update_yaxes(range=[0, 100], ticksuffix="%")

    return fig


def build_nps_figure(insights: StructuredInsights) -> go.Figure:
    rows: list[dict[str, int | str]] = []
    for segment in insights.segments:
        rows.extend(
            [
                {
                    "segment": segment.segment,
                    "bucket": "Detractors",
                    "signed_count": -segment.nps.detractors,
                    "display_count": segment.nps.detractors,
                },
                {
                    "segment": segment.segment,
                    "bucket": "Passives",
                    "signed_count": segment.nps.passives,
                    "display_count": segment.nps.passives,
                },
                {
                    "segment": segment.segment,
                    "bucket": "Promoters",
                    "signed_count": segment.nps.promoters,
                    "display_count": segment.nps.promoters,
                },
            ]
        )

    df = pd.DataFrame(rows)

    fig = px.bar(
        df,
        x="segment",
        y="signed_count",
        color="bucket",
        barmode="relative",
        category_orders={
            "segment": SEGMENT_ORDER,
            "bucket": ["Detractors", "Passives", "Promoters"],
        },
        title="Inferred NPS distribution by segment",
        text="display_count",
        custom_data=["display_count"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Bucket: %{fullData.name}<br>"
            "Count: %{customdata[0]}"
            "<extra></extra>"
        )
    )

    fig.add_hline(y=0, line_dash="dash")

    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
        legend_title_text="",
        yaxis_title="Review count",
    )

    return fig


def build_nps_score_figure(insights: StructuredInsights) -> go.Figure:
    df = pd.DataFrame(
        [{"segment": segment.segment, "nps_score": segment.nps.score} for segment in insights.segments]
    )
    fig = px.bar(
        df,
        x="segment",
        y="nps_score",
        category_orders={"segment": SEGMENT_ORDER},
        title="Net Promoter Score by segment",
        text_auto=True,
    )
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), height=360)
    return fig


def build_segment_sentiment_heatmap(insights: StructuredInsights) -> go.Figure:
    df = _sentiment_long_df(insights)
    pivot = (
        df.pivot(index="segment", columns="sentiment", values="percentage")
        .reindex(index=SEGMENT_ORDER)
        .reindex(columns=[label.title() for label in SENTIMENT_ORDER])
    )

    fig = px.imshow(
        pivot,
        text_auto=".1f",
        aspect="auto",
        title="Segment × sentiment heatmap",
        labels={"x": "Sentiment", "y": "Segment", "color": "Percentage"},
    )

    fig.update_traces(
        texttemplate="%{z:.1f}%",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Sentiment: %{x}<br>"
            "Percentage: %{z:.1f}%"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
        coloraxis_colorbar=dict(title="%"),
    )

    return fig


def build_negative_themes_bar(insights: StructuredInsights) -> go.Figure:
    rows: list[dict[str, int | str]] = []
    for segment in insights.segments:
        for item in segment.themes.negative:
            rows.append(
                {
                    "segment": segment.segment,
                    "theme": item.theme,
                    "mentions": item.count,
                    "label": f"{item.theme} ({segment.segment})",
                }
            )

    df = pd.DataFrame(rows).sort_values("mentions", ascending=True)

    fig = px.bar(
        df,
        x="mentions",
        y="label",
        color="segment",
        orientation="h",
        category_orders={"segment": SEGMENT_ORDER},
        title="Top negative themes by segment",
        text="mentions",
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
        legend_title_text="",
        yaxis_title="",
        xaxis_title="Mentions",
    )

    return fig


def build_theme_table(insights: StructuredInsights, polarity: str) -> pd.DataFrame:
    rows: list[dict[str, int | str]] = []
    for segment in insights.segments:
        theme_list = getattr(segment.themes, polarity)
        for item in theme_list:
            rows.append(
                {
                    "segment": segment.segment,
                    "theme": item.theme,
                    "mentions": item.count,
                    "example": item.example,
                }
            )
    return pd.DataFrame(rows).sort_values(by=["segment", "mentions"], ascending=[True, False])


def build_outlier_table(insights: StructuredInsights) -> pd.DataFrame:
    return pd.DataFrame([item.model_dump() for item in insights.outliers])
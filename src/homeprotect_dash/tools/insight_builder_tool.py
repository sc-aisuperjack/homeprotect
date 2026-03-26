from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import pandas as pd

from homeprotect_dash.data.contracts import (
    NPSBreakdown,
    OutlierInsight,
    SegmentInsight,
    SentimentBreakdown,
    StructuredInsights,
    Summary,
    ThemeBundle,
    ThemeInsight,
)


SegmentName = Literal["Claims", "Pricing", "Customer Service"]
SentimentLabel = Literal["positive", "neutral", "negative"]

SEGMENT_KEYWORDS: dict[SegmentName, list[str]] = {
    "Claims": [
        "claim",
        "claims",
        "settled",
        "settlement",
        "payout",
        "pay out",
        "damage",
        "damaged",
        "repair",
        "repairs",
        "flood",
        "leak",
        "storm",
        "loss adjuster",
        "subsidence",
        "incident",
    ],
    "Pricing": [
        "price",
        "pricing",
        "premium",
        "renewal",
        "renewed",
        "quote",
        "quotes",
        "cost",
        "expensive",
        "cheaper",
        "value",
        "fee",
        "fees",
        "rip off",
        "overpriced",
        "increase",
        "policy price",
    ],
    "Customer Service": [
        "service",
        "staff",
        "team",
        "support",
        "advisor",
        "adviser",
        "agent",
        "phone",
        "call",
        "contact",
        "helpful",
        "rude",
        "complaint",
        "complaints",
        "customer service",
        "email",
        "response",
        "communication",
        "callback",
        "cancel",
        "cancellation",
    ],
}

THEME_LIBRARY: dict[SegmentName, dict[SentimentLabel, dict[str, list[str]]]] = {
    "Claims": {
        "positive": {
            "Fast payout": ["quick", "quickly", "fast", "prompt", "settled", "payout"],
            "Helpful claims handlers": ["helpful", "supportive", "professional", "handler", "adviser", "advisor"],
            "Clear process": ["clear", "explained", "easy", "straightforward", "simple process"],
        },
        "negative": {
            "Slow updates": ["delay", "delayed", "waiting", "waited", "slow", "chasing", "no update"],
            "Documentation burden": ["document", "documents", "paperwork", "evidence", "proof"],
            "Claim rejection frustration": ["declined", "rejected", "refused", "not covered", "would not pay"],
        },
        "neutral": {},
    },
    "Pricing": {
        "positive": {
            "Competitive quotes": ["competitive", "cheap", "cheaper", "best price", "good quote"],
            "Good value cover": ["value", "worth", "reasonable", "affordable"],
            "Easy quote journey": ["quote", "quoted", "online", "straightforward", "easy"],
        },
        "negative": {
            "Renewal increase": ["renewal", "increased", "increase", "went up", "higher"],
            "Fee confusion": ["fee", "fees", "charge", "charges", "hidden"],
            "Expensive pricing": ["expensive", "overpriced", "rip off", "too much", "costly"],
        },
        "neutral": {},
    },
    "Customer Service": {
        "positive": {
            "Friendly staff": ["friendly", "polite", "kind", "pleasant", "lovely"],
            "Easy contact": ["answered", "responsive", "contact", "got through", "available"],
            "Helpful guidance": ["helpful", "advice", "explained", "guided", "support"],
        },
        "negative": {
            "Callback delays": ["callback", "call back", "waiting", "delay", "never called"],
            "Inconsistent answers": ["different", "conflicting", "inconsistent", "unclear", "contradictory"],
            "Poor communication": ["rude", "ignored", "no response", "unhelpful", "dismissive"],
        },
        "neutral": {},
    },
}

OUTLIER_RULES: list[tuple[str, str, str, str, str]] = [
    (
        "Praise for fraud checks",
        "Claims",
        "positive",
        "fraud verification seen as trust building rather than friction.",
        r"fraud|verification|security check",
    ),
    (
        "Bundle confusion across journeys",
        "Cross-Segment",
        "negative",
        "Several reviews blended pricing and service complaints, suggesting the journey boundaries feel unclear to customers.",
        r"renewal|quote|premium.*(?:call|service|agent)|(?:call|service).*(?:renewal|quote|premium)",
    ),
    (
        "Cancellation friction",
        "Customer Service",
        "negative",
        "A visible cluster mentioned difficulty when trying to cancel or change cover.",
        r"cancel|cancellation|leave|terminate",
    ),
]


def classify_segment(text: str, stars: int) -> SegmentName:
    lowered = text.lower()
    scores = {
        segment: sum(lowered.count(keyword) for keyword in keywords)
        for segment, keywords in SEGMENT_KEYWORDS.items()
    }
    best_segment = max(scores, key=scores.get)
    if scores[best_segment] > 0:
        return best_segment
    if stars <= 2 and any(token in lowered for token in ["call", "service", "staff", "team"]):
        return "Customer Service"
    return "Pricing"


def infer_sentiment(stars: int) -> SentimentLabel:
    if stars >= 4:
        return "positive"
    if stars == 3:
        return "neutral"
    return "negative"


def infer_nps_bucket(stars: int) -> str:
    if stars >= 5:
        return "promoters"
    if stars in (3, 4):
        return "passives"
    return "detractors"


def nps_score_from_counts(promoters: int, detractors: int, total: int) -> int:
    if total == 0:
        return 0
    return int(round(((promoters / total) - (detractors / total)) * 100))


def _match_theme(row: pd.Series, segment: SegmentName, sentiment: SentimentLabel) -> str | None:
    lowered = str(row["review_text"]).lower()
    for theme, patterns in THEME_LIBRARY[segment][sentiment].items():
        if any(pattern in lowered for pattern in patterns):
            return theme
    return None


def _example_text(row: pd.Series) -> str:
    title = str(row["Title"]).strip()
    content = str(row["Content"]).strip()
    example = title if len(title) >= 15 else f"{title} {content}".strip()
    example = re.sub(r"\s+", " ", example)
    return example[:180].strip()


def _build_theme_bundle(rows: pd.DataFrame, segment: SegmentName) -> ThemeBundle:
    bundles: dict[str, list[ThemeInsight]] = {"positive": [], "negative": []}
    for sentiment in ("positive", "negative"):
        matching = rows[rows["sentiment"] == sentiment]
        theme_rows: defaultdict[str, list[pd.Series]] = defaultdict(list)
        for _, row in matching.iterrows():
            theme = _match_theme(row, segment, sentiment)
            if theme:
                theme_rows[theme].append(row)
        sorted_themes = sorted(
            theme_rows.items(), key=lambda item: (-len(item[1]), item[0])
        )[:5]
        bundles[sentiment] = [
            ThemeInsight(theme=theme, count=len(theme_items), example=_example_text(theme_items[0]))
            for theme, theme_items in sorted_themes
        ]
    return ThemeBundle(positive=bundles["positive"], negative=bundles["negative"])


def _build_outliers(df: pd.DataFrame) -> list[OutlierInsight]:
    outliers: list[OutlierInsight] = []
    text_series = df["review_text"].astype(str).str.lower()
    for title, segment, sentiment, detail, pattern in OUTLIER_RULES:
        matches = text_series.str.contains(pattern, regex=True, na=False)
        if matches.sum() >= 5:
            outliers.append(
                OutlierInsight(title=title, segment=segment, sentiment=sentiment, detail=detail)
            )
    return outliers


def build_structured_insights(df: pd.DataFrame) -> StructuredInsights:
    working = df.copy()
    working["segment"] = working.apply(
        lambda row: classify_segment(str(row["review_text"]), int(row["Stars"])), axis=1
    )
    working["sentiment"] = working["Stars"].apply(infer_sentiment)
    working["nps_bucket"] = working["Stars"].apply(infer_nps_bucket)

    segments: list[SegmentInsight] = []
    for segment_name in ("Claims", "Pricing", "Customer Service"):
        segment_rows = working[working["segment"] == segment_name]
        review_count = int(len(segment_rows))
        sentiment = SentimentBreakdown(
            positive=int((segment_rows["sentiment"] == "positive").sum()),
            neutral=int((segment_rows["sentiment"] == "neutral").sum()),
            negative=int((segment_rows["sentiment"] == "negative").sum()),
        )
        promoters = int((segment_rows["nps_bucket"] == "promoters").sum())
        passives = int((segment_rows["nps_bucket"] == "passives").sum())
        detractors = int((segment_rows["nps_bucket"] == "detractors").sum())
        nps = NPSBreakdown(
            promoters=promoters,
            passives=passives,
            detractors=detractors,
            score=nps_score_from_counts(promoters, detractors, review_count),
        )
        themes = _build_theme_bundle(segment_rows, segment_name)
        segments.append(
            SegmentInsight(
                segment=segment_name,
                review_count=review_count,
                sentiment=sentiment,
                nps=nps,
                themes=themes,
            )
        )

    return StructuredInsights(
        summary=Summary(total_reviews=int(len(working)), generated_at=datetime.now(UTC)),
        segments=segments,
        outliers=_build_outliers(working),
    )


def write_structured_insights(insights: StructuredInsights, path: Path) -> None:
    path.write_text(json.dumps(insights.model_dump(mode="json"), indent=2), encoding="utf-8")

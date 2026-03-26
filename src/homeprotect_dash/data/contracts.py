from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


SegmentName = Literal["Claims", "Pricing", "Customer Service"]
SentimentLabel = Literal["positive", "neutral", "negative"]


class ThemeInsight(BaseModel):
    theme: str = Field(min_length=1)
    count: int = Field(ge=0)
    example: str = Field(min_length=1)


class ThemeBundle(BaseModel):
    positive: list[ThemeInsight]
    negative: list[ThemeInsight]


class SentimentBreakdown(BaseModel):
    positive: int = Field(ge=0)
    neutral: int = Field(ge=0)
    negative: int = Field(ge=0)

    def total(self) -> int:
        return self.positive + self.neutral + self.negative


class NPSBreakdown(BaseModel):
    promoters: int = Field(ge=0)
    passives: int = Field(ge=0)
    detractors: int = Field(ge=0)
    score: int = Field(ge=-100, le=100)

    def total(self) -> int:
        return self.promoters + self.passives + self.detractors


class SegmentInsight(BaseModel):
    segment: SegmentName
    review_count: int = Field(ge=0)
    sentiment: SentimentBreakdown
    nps: NPSBreakdown
    themes: ThemeBundle

    @model_validator(mode="after")
    def validate_totals(self) -> "SegmentInsight":
        if self.sentiment.total() != self.review_count:
            raise ValueError(
                f"Sentiment counts for {self.segment} do not sum to review_count."
            )
        if self.nps.total() != self.review_count:
            raise ValueError(f"NPS counts for {self.segment} do not sum to review_count.")
        return self


class OutlierInsight(BaseModel):
    title: str = Field(min_length=1)
    segment: SegmentName | Literal["Cross-Segment"]
    sentiment: SentimentLabel
    detail: str = Field(min_length=1)


class Summary(BaseModel):
    total_reviews: int = Field(ge=0)
    generated_at: datetime


class StructuredInsights(BaseModel):
    summary: Summary
    segments: list[SegmentInsight]
    outliers: list[OutlierInsight] = Field(default_factory=list)

    @field_validator("segments")
    @classmethod
    def validate_exact_segments(cls, segments: list[SegmentInsight]) -> list[SegmentInsight]:
        found = {segment.segment for segment in segments}
        expected: set[str] = {"Claims", "Pricing", "Customer Service"}
        if found != expected:
            raise ValueError(
                f"Expected exactly {sorted(expected)} but received {sorted(found)}."
            )
        return sorted(segments, key=lambda item: item.segment)

    @model_validator(mode="after")
    def validate_summary(self) -> "StructuredInsights":
        summed_reviews = sum(segment.review_count for segment in self.segments)
        if summed_reviews != self.summary.total_reviews:
            raise ValueError("Summary total_reviews does not match the sum of segment review counts.")
        return self

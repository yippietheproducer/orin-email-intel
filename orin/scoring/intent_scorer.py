"""
Intent Scorer — NLP-based prospect qualification.

Analyzes prospect signals (website, social, behavior) to produce
a 0-100 intent score. Only prospects above SCORING_THRESHOLD
proceed to sequence generation.
"""
import json
import os
from dataclasses import dataclass
from typing import Optional

import boto3

BEDROCK_MODEL = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
SCORING_THRESHOLD = float(os.getenv("SCORING_THRESHOLD", "0.7"))


@dataclass
class ProspectSignals:
    """Raw signals collected about a prospect."""
    company_name: str
    website_url: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    tech_stack: Optional[list[str]] = None
    recent_funding: Optional[float] = None
    social_activity_score: float = 0.0
    website_traffic_rank: Optional[int] = None


@dataclass
class ScoringResult:
    """Output of the intent scoring pipeline."""
    prospect_id: str
    score: float  # 0.0 - 1.0
    confidence: float
    signals_used: list[str]
    reasoning: str
    qualified: bool


class IntentScorer:
    """Score prospects using Bedrock NLP models."""

    def __init__(self):
        self.bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "eu-west-1"))
        self._call_count = 0

    def score(self, prospect_id: str, signals: ProspectSignals) -> ScoringResult:
        """Score a single prospect based on collected signals."""
        prompt = self._build_prompt(signals)
        response = self._invoke_model(prompt)
        parsed = self._parse_response(response)

        score = parsed.get("score", 0.0)
        return ScoringResult(
            prospect_id=prospect_id,
            score=score,
            confidence=parsed.get("confidence", 0.5),
            signals_used=parsed.get("signals_used", []),
            reasoning=parsed.get("reasoning", ""),
            qualified=score >= SCORING_THRESHOLD,
        )

    def _build_prompt(self, signals: ProspectSignals) -> str:
        """Build scoring prompt from prospect signals."""
        return f"""Analyze this prospect for purchase intent (e-commerce SaaS buyer):

Company: {signals.company_name}
Website: {signals.website_url or 'unknown'}
Industry: {signals.industry or 'unknown'}
Employees: {signals.employee_count or 'unknown'}
Tech stack: {', '.join(signals.tech_stack or [])}
Recent funding: ${signals.recent_funding or 0:,.0f}
Social activity: {signals.social_activity_score}/10
Traffic rank: {signals.website_traffic_rank or 'unknown'}

Score from 0.0 to 1.0 based on likelihood they need email marketing intelligence.
Return JSON: {{"score": float, "confidence": float, "signals_used": [...], "reasoning": "..."}}"""

    def _invoke_model(self, prompt: str) -> dict:
        """Call Bedrock for inference."""
        self._call_count += 1
        response = self.bedrock.invoke_model(
            modelId=BEDROCK_MODEL,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )
        return json.loads(response["body"].read())

    def _parse_response(self, response: dict) -> dict:
        """Extract structured scoring from model response."""
        try:
            content = response["content"][0]["text"]
            # Find JSON in response
            start = content.index("{")
            end = content.rindex("}") + 1
            return json.loads(content[start:end])
        except (KeyError, ValueError, json.JSONDecodeError):
            return {"score": 0.0, "confidence": 0.0, "reasoning": "parse_error"}

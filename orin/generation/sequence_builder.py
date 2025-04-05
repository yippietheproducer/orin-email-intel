"""
Sequence Builder — Generate personalized email sequences.

Each email is uniquely crafted using the prospect's context.
No templates. Every message references specific details about their business.
"""
import json
import os
from dataclasses import dataclass

import boto3

BEDROCK_MODEL = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")


@dataclass
class EmailSequence:
    """A multi-touch email sequence for one prospect."""
    prospect_id: str
    emails: list[dict]  # [{subject, body, delay_hours}]
    personalization_signals: list[str]
    estimated_reply_probability: float


class SequenceBuilder:
    """Generate personalized email sequences via Bedrock."""

    def __init__(self):
        self.bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "eu-west-1"))

    def generate(self, prospect_id: str, context: dict, num_touches: int = 3) -> EmailSequence:
        """Generate a personalized sequence for a qualified prospect."""
        prompt = self._build_generation_prompt(context, num_touches)
        response = self._invoke(prompt)
        emails = self._parse_sequence(response)

        return EmailSequence(
            prospect_id=prospect_id,
            emails=emails,
            personalization_signals=list(context.keys()),
            estimated_reply_probability=self._estimate_reply_prob(context),
        )

    def _build_generation_prompt(self, context: dict, num_touches: int) -> str:
        return f"""Write a {num_touches}-email outreach sequence for this prospect:

{json.dumps(context, indent=2)}

Requirements:
- Each email must reference SPECIFIC details about their business
- Tone: professional but warm, founder-to-founder
- First email: introduce value prop with their specific pain point
- Follow-ups: add new angles, not just "checking in"
- Keep each email under 150 words
- Subject lines: specific, no clickbait

Return JSON array: [{{"subject": "...", "body": "...", "delay_hours": N}}, ...]"""

    def _invoke(self, prompt: str) -> dict:
        response = self.bedrock.invoke_model(
            modelId=BEDROCK_MODEL,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )
        return json.loads(response["body"].read())

    def _parse_sequence(self, response: dict) -> list[dict]:
        try:
            content = response["content"][0]["text"]
            start = content.index("[")
            end = content.rindex("]") + 1
            return json.loads(content[start:end])
        except (KeyError, ValueError, json.JSONDecodeError):
            return []

    def _estimate_reply_prob(self, context: dict) -> float:
        """Heuristic reply probability based on personalization depth."""
        signals = len([v for v in context.values() if v])
        return min(0.15 + (signals * 0.02), 0.45)
